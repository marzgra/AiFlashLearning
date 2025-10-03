from pydantic import BaseModel

class ReviewResponse(BaseModel):
    topic: str
    score: int
    repeat: str
    next: str
    class Config: from_attributes = True
