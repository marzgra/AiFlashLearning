from pydantic import BaseModel
from datetime import date

class Review(BaseModel):
    session_id: str
    topic: str
    last_review: date
    interval_days: int = 1
    ease_factor: float = 2.5
    score: float
    class Config: from_attributes = True

class ReviewResponse(BaseModel):
    topic: str
    score: int
    hints: str
    class Config: from_attributes = True
