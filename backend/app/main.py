from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.settings import settings, Base
from .config.database import engine
# Routers
from .routers.auth import router as auth_router
from .routers.users import router as users_router
from .routers.games import router as games_router

app = FastAPI(title=settings.PROJECT_NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup (dev only)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Include routers
app.include_router(auth_router, prefix="", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(games_router, prefix="/games", tags=["games"])