import os
from datetime import datetime, timedelta
from typing import Type

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, select, func, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.sql.expression import desc

from schemas import PageParams, PagedResponseSchema, T

DB_URL = "postgresql+asyncpg://user:password@localhost:5432/ai-flash-learning-db"

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DB_URL
)

db_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)
Base = declarative_base()


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    session_id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)

class Message(Base):
    __tablename__ = "agent_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("agent_sessions.session_id", ondelete="CASCADE"))
    message_data = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

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
    has_opened_session = Column(Boolean, nullable=False)

class Repetition(Base):
    __tablename__ = "session_repetition"
    id = Column(Integer, primary_key=True, index=True)
    topic_id: Mapped[Integer] = mapped_column(ForeignKey("session_topic.id"))
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
    
    
async def get_session(db: AsyncSession, session_id: str):
    result = await db.execute(select(AgentSession).where(AgentSession.session_id == session_id))
    session = result.scalars().first()
    if not session:
        raise ValueError(f"Session {session_id} not found")
    return session


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
        ease_factor = 1,
        has_opened_session = True
    )
    db.add(topic)
    await db.flush()  # add to the session but don't commit
    await db.refresh(topic)  # Ensure all attributes are loaded
    return topic


def get_history_query():
    latest_repetition_subq = select(
        Repetition.topic_id,
        func.max(Repetition.review_date).label('max_review_date')
    ).group_by(
        Repetition.topic_id
    ).subquery()

    latest_repetition = select(
        Repetition.topic_id,
        Repetition.repeat,
        Repetition.score,
        Repetition.review_date
    ).join(
        latest_repetition_subq,
        (Repetition.topic_id == latest_repetition_subq.c.topic_id) &
        (Repetition.review_date == latest_repetition_subq.c.max_review_date)
    ).subquery()

    query = select(
        Topic.session_id,
        Topic.topic,
        Topic.repetitions,
        Topic.created_date,
        Topic.next_repetition,
        latest_repetition.c.repeat,
        latest_repetition.c.score,
        latest_repetition.c.review_date
    ).outerjoin(
        latest_repetition,
        Topic.id == latest_repetition.c.topic_id
    )

    return query


def today_review():
    return get_history_query().where(
        func.date(Topic.next_repetition) <= datetime.now().date()
    )


async def paginate(page_params: PageParams, query, db: AsyncSession, response_schema: Type[BaseModel]) -> PagedResponseSchema[T]:
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    paginated_query = query.offset((page_params.page - 1) * page_params.size).limit(page_params.size)
    result = await db.execute(paginated_query)
    items = result.all()

    return PagedResponseSchema(
        total=total,
        page=page_params.page,
        size=page_params.size,
        results=[response_schema.model_validate(item) for item in items],
    )

async def update_stats(db: AsyncSession):
    yesterday = datetime.now().date() - timedelta(days=1)

    result = await db.execute(
        select(Streak)
        .where(func.date(Streak.last_session_date) == func.date(yesterday))
    )
    streak = result.scalars().first()

    # If not found, get the streak with the latest last_session_date
    if not streak:
        result = await (db.execute(get_stats_query()))
        streak = result.scalars().first()

    if not streak:
        streak = Streak(current_streak=0, longest_streak=0, last_session_date=datetime.now())
        db.add(streak)
        await db.flush()

    streak.current_streak += 1
    streak.last_session_date = datetime.now()
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)


async def get_stats(db: AsyncSession):
    result = await (db.execute(get_stats_query()))
    return result.scalars().first()


def get_stats_query():
    return (select(Streak)
            .order_by(desc(Streak.last_session_date))
            .limit(1))


async def open_session(db: AsyncSession, session_id: str):
    topic = await get_topic(db, session_id)
    topic.has_opened_session = True
    await db.commit()


async def get_db():
    AsyncSessionLocal = sessionmaker(
        db_engine,
        class_= AsyncSession,
        expire_on_commit=False  # This prevents lazy-loading issues
    )
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()  # Ensure changes are committed
