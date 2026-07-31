from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import discover, auth
from api.database import engine, Base

async def startup_db_init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="American History Investigative Helper Engine",
    on_startup=[startup_db_init] 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(discover.router)
app.include_router(auth.router)
