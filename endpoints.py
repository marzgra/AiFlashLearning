import uuid

from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession
from fastapi import Body, Request, APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ai_client import run_agent, get_ai_summary
from database import db_engine, get_topic, get_db, get_history_query, paginate, today_review, get_stats, update_stats
from main import app
from schemas import PageParams, History
from session_handler import get_session
from sm2 import update_topic_with_sm2

router = APIRouter()

@router.post("/session")
async def create_session():
    session_id = uuid.uuid4()
    session = SQLAlchemySession(session_id=session_id.__str__(), engine=db_engine, create_tables=True)
    app.state.sessions[session_id] = session
    return {"id": session_id}


@router.post("/session/{session_id}")
async def chat(session_id: str,
               request: Request,
               user_input: str = Body(..., embed=True),
               db: AsyncSession = Depends(get_db)):
    session = await get_session(session_id, db)
    return StreamingResponse(event_generator(user_input, session, request), media_type="text/event-stream")
    #  for debug
    # return await event_generator(user_input, session, request)


@router.get("/session/{session_id}/close")
async def end_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = await get_session(session_id, db)
    topic = await get_topic(db, session_id)
    # if topic.has_opened_session:
    ai_summary = await get_ai_summary(session)
    topic = await update_topic_with_sm2(db, topic, ai_summary)
    await update_stats(db)
    return {
        "topic": topic.topic,
        "score": ai_summary.score,
        "repeat": ai_summary.repeat,
        "next": ai_summary.next
    }
    # return { "error": "Session already closed" }


@router.get("/history")
async def history(page_params: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await paginate(page_params, get_history_query(), db, History)


@router.get("/today")
async def today(page_params: PageParams = Depends(), db: AsyncSession = Depends(get_db)):
    return await paginate(page_params, today_review(), db, History)


@router.get("/stats")
async def stats(db: AsyncSession = Depends(get_db)):
    return await get_stats(db)

async def event_generator(prompt: str,
                          session: SQLAlchemySession,
                          request: Request):
    async for chunk in run_agent(prompt, session):
        if await request.is_disconnected():
            print("Połączenie przerwane przez klienta")
            break
        yield f"data: {chunk}\n\n"
    #  for debug
    # return await run_agent(prompt, session)