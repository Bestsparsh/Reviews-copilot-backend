from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    text: str
    rating: int
    location: str
    date: str

    sentiment: Optional[str] = None
    topic: Optional[str] = None

    reply: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
