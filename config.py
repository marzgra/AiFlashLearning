from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import db_engine, Base

@asynccontextmanager
async def lifespan(app):
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="AI Chat Manager", lifespan=lifespan)

app.state.sessions = {}
