import random
from sqlmodel import Session

from ..db import engine
from ..models import Review
from sqlmodel import select



SAMPLE_REVIEWS = [
    ("Amazing service, staff were very polite and helpful", 5, "Positive", "Service"),
    ("Room was dirty and smelled bad", 1, "Negative", "Cleanliness"),
    ("Food was decent but overpriced", 3, "Neutral", "Price"),
    ("Loved the ambience and quick support", 5, "Positive", "Service"),
    ("Waited 40 minutes, terrible experience", 2, "Negative", "Service"),
    ("Good value for money", 4, "Positive", "Price"),
    ("Bathroom not clean at all", 2, "Negative", "Cleanliness"),
    ("Friendly reception staff", 5, "Positive", "Service"),
    ("Average stay, nothing special", 3, "Neutral", "Service"),
    ("Great quality but slightly expensive", 4, "Neutral", "Price"),
]


def seed():
    with Session(engine) as session:
        existing = len(session.exec(select(Review)).all())

        if existing > 0:
            print("Database already seeded ✅")
            return

        for text, rating, sentiment, topic in SAMPLE_REVIEWS:
            review = Review(
                text=text,
                rating=rating,
                sentiment=sentiment,
                topic=topic,
            )
            session.add(review)

        session.commit()
        print("Seeded reviews 🌱")


if __name__ == "__main__":
    seed()
