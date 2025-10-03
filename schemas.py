from pydantic import BaseModel

class ReviewResponse(BaseModel):
    topic: str
    score: int
    hints: str
    class Config: from_attributes = True
