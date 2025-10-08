from datetime import datetime
from typing import Annotated, TypeVar, Generic, List

from pydantic import BaseModel, Field
from pydantic.v1.generics import GenericModel


class ReviewResponse(BaseModel):
    topic: str
    score: int
    repeat: str
    next: str
    class Config: from_attributes = True


class PageParams(BaseModel):
    # PQ params for paginated API
    # Annotated: A wrapper around `int` that allows for additional constraints.
    #  ge: The value must be greater than or equal to this.
    #  le: The value must be less than or equal to this.
    page: Annotated[int, Field(strict=True, ge=1)] = 1
    size: Annotated[int, Field(strict=True, ge=1, le=100)] = 10


T = TypeVar("T")


class PagedResponseSchema(GenericModel, Generic[T]):
    # Response schema for any paged API
    total: int
    page: int
    size: int
    results: List[T]


class History(BaseModel):
    session_id: str
    topic: str
    repetitions: int
    created_date: datetime
    next_repetition: datetime
    repeat: str
    score: int
    review_date: datetime

    class Config:
        orm_mode = True
        from_attributes=True
