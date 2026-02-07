from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel

from ..db import get_session
from ..models import Review
from ..services.search import get_top_k_similar


router = APIRouter(prefix="/search", tags=["search"])


class SearchResult(BaseModel):
    id: int
    text: str
    rating: int
    location: str
    sentiment: str | None
    topic: str | None
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    count: int


@router.get("/", response_model=SearchResponse)
def search_similar_reviews(
    q: str = Query(..., description="Search query text"),
    k: int = Query(default=5, ge=1, le=20, description="Number of results to return"),
    session: Session = Depends(get_session)
):
    all_reviews = session.exec(select(Review)).all()
    
    if not all_reviews:
        return SearchResponse(query=q, results=[], count=0)
    
    similar_reviews = get_top_k_similar(q, all_reviews, k=k)
    
    results = []
    for idx, review in enumerate(similar_reviews):
        score = 1.0 - (idx * 0.1)
        results.append(SearchResult(
            id=review.id,
            text=review.text,
            rating=review.rating,
            location=review.location,
            sentiment=review.sentiment,
            topic=review.topic,
            similarity_score=round(score, 3)
        ))
    
    return SearchResponse(
        query=q,
        results=results,
        count=len(results)
    )
