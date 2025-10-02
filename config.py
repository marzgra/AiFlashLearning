import os
from fastapi import FastAPI

SESSIONS_DIR = "sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

app = FastAPI(title="AI Chat Manager")
app.state.sessions = {}
