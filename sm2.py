from datetime import date, timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database import Topic, Repetition
from schemas import ReviewResponse

async def update_topic_with_sm2(db: AsyncSession, topic: Topic, ai_summary: ReviewResponse):
    # score: 0..5 (float albo int)
    score = float(ai_summary.score)
    if score < 3:
        topic.repetitions = 0
        topic.interval_days = 1
        topic.ease_factor = max(1.3, topic.ease_factor - 0.2)
    else:
        topic.repetitions += 1
        if topic.repetitions == 1:
            topic.interval_days = 1
        elif topic.repetitions == 2:
            topic.interval_days = 6
        else:
            topic.interval_days = int(round(topic.interval_days * topic.ease_factor))
        # standardowa aktualizacja EF:
        topic.ease_factor += (0.1 - (5 - score) * (0.08 + (5 - score) * 0.02))
        if topic.ease_factor < 1.3:
            topic.ease_factor = 1.3

    topic = await update_topic(db, ai_summary, topic)
    await create_repetition(db, ai_summary, score, topic)

    return topic


async def update_topic(db: AsyncSession, ai_summary: ReviewResponse, topic: Topic):
    if topic.created_date is None:
        topic.created_date = datetime.today()
    topic.next_repetition = datetime.today() + timedelta(days=topic.interval_days)
    topic.has_opened_session = False
    if topic.topic == "temp":
        topic.topic = ai_summary.topic

    topic = await db.merge(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


async def create_repetition(db: AsyncSession, ai_summary: ReviewResponse, score: float, topic: Topic):
    repetition = Repetition(
        topic_id=topic.id,
        review_date=datetime.today(),
        score=score,
        repeat=ai_summary.repeat,
        next=ai_summary.next
    )

    db.add(repetition)
    await db.commit()
    await db.refresh(repetition)
