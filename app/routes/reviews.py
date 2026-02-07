from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, col
from typing import List

from ..db import get_session
from ..models import Review
from ..services.search import get_top_k_similar
from ..services.llm import generate_reply
from ..services.guardrails import redact, is_safe
from ..schemas import ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewRead)
def create_review(payload: ReviewCreate, session: Session = Depends(get_session)):
    review = Review(**payload.model_dump())
    session.add(review)
    session.commit()
    session.refresh(review)
    return review

@router.post("/{review_id}/suggest-reply")
def suggest_reply(review_id: int, session: Session = Depends(get_session)):
    try:
        review = session.get(Review, review_id)

        if not review:
            raise HTTPException(404, "Review not found")

        all_reviews = session.exec(select(Review)).all()
        
        if not all_reviews:
            raise HTTPException(400, "No reviews in database to generate context")

        similar = get_top_k_similar(review.text, all_reviews)
        reply = generate_reply(review.text, similar)
        reply = redact(reply)

        if not is_safe(reply):
            reply = "Thank you for your feedback. Our team will look into this immediately."

        return {
            "reply": reply,
            "similar_reviews": [r.text for r in similar]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating reply: {str(e)}")
        return {
            "reply": "Thank you for your feedback. We appreciate you taking the time to share your experience with us.",
            "similar_reviews": []
        }

@router.get("/", response_model=dict)
def list_reviews(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    location: str | None = Query(default=None, description="Filter by location"),
    sentiment: str | None = Query(default=None, description="Filter by sentiment"),
    q: str | None = Query(default=None, description="Search query for text"),
    session: Session = Depends(get_session)
):
    query = select(Review)
    
    if location:
        query = query.where(Review.location == location)
    
    if sentiment:
        query = query.where(Review.sentiment == sentiment)
    
    if q:
        query = query.where(col(Review.text).ilike(f"%{q}%"))
    
    total_query = select(Review)
    if location:
        total_query = total_query.where(Review.location == location)
    if sentiment:
        total_query = total_query.where(Review.sentiment == sentiment)
    if q:
        total_query = total_query.where(col(Review.text).ilike(f"%{q}%"))
    
    total = len(session.exec(total_query).all())
    
    query = query.offset(skip).limit(limit)
    reviews = session.exec(query).all()
    
    total_pages = (total + limit - 1) // limit
    current_page = (skip // limit) + 1
    
    return {
        "reviews": [ReviewRead.model_validate(r) for r in reviews],
        "pagination": {
            "total": total,
            "page": current_page,
            "page_size": limit,
            "total_pages": total_pages,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    }

@router.get("/{review_id}", response_model=ReviewRead)
def get_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Not found")
    return review

@router.patch("/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: int,
    payload: ReviewUpdate,
    session: Session = Depends(get_session),
):
    try:
        review = session.get(Review, review_id)
        if not review:
            raise HTTPException(404, "Review not found")

        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(review, k, v)

        session.commit()
        session.refresh(review)
        return review
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(500, f"Failed to update review: {str(e)}")

@router.delete("/{review_id}")
def delete_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)
    if review:
        session.delete(review)
        session.commit()

    return {"ok": True}
