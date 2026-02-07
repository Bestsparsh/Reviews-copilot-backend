from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from ..db import get_session
from ..models import Review

router = APIRouter(prefix="/analytics", tags=["analytics"])


def group_count(session: Session, column):
    results = session.exec(
        select(column, func.count())
        .group_by(column)
    ).all()

    return {key or "Unknown": count for key, count in results}


@router.get("/")
def get_analytics(session: Session = Depends(get_session)):
    try:
        sentiment_counts = group_count(session, Review.sentiment)
        topic_counts = group_count(session, Review.topic)

        total_reviews = session.exec(
            select(func.count(Review.id))
        ).one()

        avg_rating = session.exec(
            select(func.avg(Review.rating))
        ).one()

        return {
            "sentiment": sentiment_counts,
            "topics": topic_counts,
            "total_reviews": total_reviews or 0,
            "avg_rating": round(avg_rating or 0, 2)
        }
    except Exception as e:
        return {
            "sentiment": {"Positive": 0, "Neutral": 0, "Negative": 0},
            "topics": {},
            "total_reviews": 0,
            "avg_rating": 0
        }
