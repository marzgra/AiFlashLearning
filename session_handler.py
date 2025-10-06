from agents.extensions.memory import SQLAlchemySession
from sqlalchemy.ext.asyncio import AsyncSession

from config import app
from database import db_engine, open_session


async def get_session(session_id: str, db: AsyncSession):
    """Zwraca istniejącą sesję lub ładuje z pliku .db."""
    if session_id in app.state.sessions:
        return app.state.sessions[session_id]

    session = SQLAlchemySession(session_id=session_id, engine=db_engine, create_tables=True)
    await open_session(db, session_id)

    app.state.sessions[session_id] = session
    return session