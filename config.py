from fastapi import FastAPI

app = FastAPI(title="AI Chat Manager")
app.state.sessions = {}
