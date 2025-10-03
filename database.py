from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.ext.asyncio import create_async_engine

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"
db_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base = declarative_base()

class Topic(Base):
    __tablename__ = "session_topic"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    session_id = Column(Integer, ForeignKey("agents_sessions.id", ondelete="CASCADE"))
    repetitions = Column(Integer, nullable=False)
    created_date = Column(DateTime, nullable=False)
    next_repetition = Column(DateTime, nullable=False)
    interval_days = Column(Integer, nullable=False)
    ease_factor = Column(Integer, nullable=False)

class Repetition(Base):
    __tablename__ = "session_repetition"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("session_topic.id", ondelete="CASCADE"))
    review_date = Column(DateTime, nullable=False)
    score = Column(Integer, nullable=False)
    focus = Column(String, nullable=True)

class Streak(Base):
    __tablename__ = "learning_streak"
    id = Column(Integer, primary_key=True, index=True)
    current_streak = Column(Integer, nullable=False)
    longest_streak = Column(Integer, nullable=False)
    last_session_date = Column(DateTime, nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
