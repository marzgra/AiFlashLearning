from pydantic import BaseModel

class ReviewResponse(BaseModel):
    topic: str
    score: int
    focus: str
    class Config: from_attributes = True
