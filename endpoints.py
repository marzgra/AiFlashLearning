import uuid

from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession
from fastapi import Body, Request, APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ai_client import run_agent, summary
from database import db_engine, get_topic, get_db
from main import app
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
               user_input: str = Body(..., embed=True)):
    session = get_session(session_id)
    return StreamingResponse(event_generator(user_input, session, request), media_type="text/event-stream")


@router.get("/session/{session_id}/close")
async def end_session(session_id: str, db: AsyncSession = Depends(get_db)):
    session = get_session(session_id)
    ai_summary = await summary(session)
    topic = await get_topic(db, session_id)
    topic = await update_topic_with_sm2(db, topic, ai_summary)
    return {
        "topic": topic.topic,
        "score": ai_summary.score,
        "focus": ai_summary.focus
    }


@router.get("/history")
def list_conversations():
    return []


async def event_generator(prompt: str,
                          session: SQLAlchemySession,
                          request: Request):
    async for chunk in run_agent(prompt, session):
        if await request.is_disconnected():
            print("Połączenie przerwane przez klienta")
            break
        yield f"data: {chunk}\n\n"