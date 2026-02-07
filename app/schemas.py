from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field as PydanticField


class ReviewCreate(BaseModel):
    text: str
    rating: int = PydanticField(ge=1, le=5)
    location: str
    date: str
    sentiment: Optional[str] = None
    topic: Optional[str] = None


class ReviewUpdate(BaseModel):
    reply: Optional[str] = None


class ReviewRead(BaseModel):
    id: int
    text: str
    rating: int
    location: str
    date: str
    sentiment: Optional[str]
    topic: Optional[str]
    reply: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
