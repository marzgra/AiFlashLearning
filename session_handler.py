from agents.extensions.memory import SQLAlchemySession

from config import app
from database import db_engine


def get_session(session_id: str):
    """Zwraca istniejącą sesję lub ładuje z pliku .db."""
    if session_id in app.state.sessions:
        return app.state.sessions[session_id]

    session = SQLAlchemySession(session_id=session_id, engine=db_engine, create_tables=True)

    app.state.sessions[session_id] = session
    return session