from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import discover, auth

app = FastAPI(title="American History Investigative Helper Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(discover.router)
app.include_router(auth.router)


