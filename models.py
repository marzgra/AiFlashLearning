from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

# class Topic(Base):
#     __tablename__ = "topics"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False, unique=True)
#     created_at = Column(DateTime, nullable=False, default=datetime.today())
#
#     reviews = relationship("Review", back_populates="topic", uselist=True, cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    # topic_id = Column(Integer, ForeignKey("topics.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.today())
    interval_days = Column(Integer, nullable=False, default=1)
    ease_factor = Column(Float, default=2.5)
    # repetitions = Column(Integer, nullable=False, default=0)
    score = Column(Float, nullable=False, default=0.0)

    # topic = relationship("Topic", back_populates="reviews")