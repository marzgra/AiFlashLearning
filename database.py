from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, select
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./app.db"
db_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
Base = declarative_base()


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    session_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class Topic(Base):
    __tablename__ = "session_topic"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    session_id = Column(String, ForeignKey("agent_sessions.session_id", ondelete="CASCADE"))
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
    repeat = Column(String, nullable=True)
    next = Column(String, nullable=True)

class Streak(Base):
    __tablename__ = "learning_streak"
    id = Column(Integer, primary_key=True, index=True)
    current_streak = Column(Integer, nullable=False)
    longest_streak = Column(Integer, nullable=False)
    last_session_date = Column(DateTime, nullable=False)


async def get_topic(db: AsyncSession, session_id: str):
    result = await db.execute(select(Topic).where(Topic.session_id == session_id))
    topic = result.scalars().first()
    if topic:
        # Ensure attributes are loaded before returning
        await db.refresh(topic)
        return topic
    topic = Topic(
        topic = "temp",
        session_id = session_id,
        repetitions = 0,
        created_date = datetime.now(),
        next_repetition = datetime.now(),
        interval_days = 0,
        ease_factor = 1
    )
    db.add(topic)
    await db.flush()  # add to the session but don't commit
    await db.refresh(topic)  # Ensure all attributes are loaded
    return topic


async def get_db():
    AsyncSessionLocal = sessionmaker(
        db_engine,
        class_= AsyncSession,
        expire_on_commit=False  # This prevents lazy-loading issues
    )
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()  # Ensure changes are committed
