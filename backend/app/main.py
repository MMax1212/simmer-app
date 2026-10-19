from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.api import admin, auth, recipes, users
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Creates missing tables on startup. Fine for Sprint 1; switch to Alembic
    # migrations before the schema starts changing under teammates' feet.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Simmer API",
    description="Backend REST API for Simmer Cooking Social Network",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow CORS during local development between frontend (5173) and backend (8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(recipes.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend connectivity."""
    return {"status": "ok", "app": "Simmer Backend", "version": "1.0.0"}
