from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"
db_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base = declarative_base()

class SessionReview(Base):
    __tablename__ = "session_reviews"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    last_review = Column(DateTime, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

