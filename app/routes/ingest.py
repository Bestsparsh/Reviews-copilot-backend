from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel

from ..db import get_session
from ..models import Review
from ..schemas import ReviewCreate, ReviewRead
from ..services.classifier import classify_review


router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestRequest(BaseModel):
    reviews: List[ReviewCreate]


class IngestResponse(BaseModel):
    success: bool
    count: int
    message: str


@router.post("/", response_model=IngestResponse)
def ingest_reviews(payload: IngestRequest, session: Session = Depends(get_session)):
    try:
        created_count = 0
        
        for review_data in payload.reviews:
            if not review_data.sentiment or not review_data.topic:
                sentiment, topic = classify_review(review_data.text, review_data.rating)
                if not review_data.sentiment:
                    review_data.sentiment = sentiment
                if not review_data.topic:
                    review_data.topic = topic
            
            review = Review(**review_data.model_dump())
            session.add(review)
            created_count += 1
        
        session.commit()
        
        return IngestResponse(
            success=True,
            count=created_count,
            message=f"Successfully ingested {created_count} reviews"
        )
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Ingest failed: {str(e)}")
