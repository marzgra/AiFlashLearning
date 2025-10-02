from fastapi.middleware.cors import CORSMiddleware

import endpoints
from config import app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)

print(app.routes)
