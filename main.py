from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from endpoints import router

app = FastAPI(title="AI Chat Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
