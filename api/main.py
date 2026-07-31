from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import engine, Base

try:
    from api.routes import discover
    from api.models.users import SearchHistory
except ImportError:
    pass

from api.routes import discover, auth

async def startup_db_init():
    print("Initializing layouts...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables initialized.")

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

