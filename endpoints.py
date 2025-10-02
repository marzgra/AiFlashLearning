import os
import uuid
from datetime import datetime

from fastapi import Body, Request, APIRouter
from fastapi.responses import StreamingResponse
from agents.extensions.memory.sqlalchemy_session import SQLAlchemySession

from ai_client import run_agent, summary
from config import SESSIONS_DIR
from database import db_engine
from schemas import Review
from session_handler import get_session
from config import app
from sm2 import update_sm2

router = APIRouter()

@router.post("/session")
def create_session():
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
async def end_session(session_id: str):
    session = get_session(session_id)
    ai_summary = await summary(session)
    review = Review(session_id = session_id,
                    topic = ai_summary.topic,
                    last_review = datetime.now(),
                    score = ai_summary.score)
    update_sm2(review, ai_summary.score)


@router.get("/history")
def list_conversations():
    return [f.replace(".db", "") for f in os.listdir(SESSIONS_DIR) if f.endswith(".db")]


async def event_generator(prompt: str,
                          session: SQLAlchemySession,
                          request: Request):
    async for chunk in run_agent(prompt, session):
        if await request.is_disconnected():
            print("Połączenie przerwane przez klienta")
            break
        yield f"data: {chunk}\n\n"