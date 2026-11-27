from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api import admin, auth, discovery, feed, grocery, posts, recipes, users
from app.core.config import settings
from app.core.database import check_database_connection, get_db

app = FastAPI(title="Simmer API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError):
    # Never echo request bodies, passwords, or exception contexts into responses.
    details = [{"loc": error["loc"], "msg": error["msg"], "type": error["type"]} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": details})


app.include_router(auth.router)
app.include_router(users.router)
# Named discovery paths must precede the recipe router's /{recipe_id} route.
app.include_router(discovery.router)
app.include_router(recipes.router)
app.include_router(admin.router)
app.include_router(posts.router)
app.include_router(posts.comments_router)
app.include_router(feed.router)
app.include_router(grocery.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Simmer Backend", "version": "1.0.0"}


@app.get("/api/health/db")
def database_health_check(db: Session = Depends(get_db)):
    """
    Database Health & Liveness Diagnostic Endpoint (INF-4.0.2).
    Executes a minimal ping query (SELECT 1) over the active database connection pool.
    Returns HTTP 200 with connection latency and dialect metadata, or HTTP 503 if unreachable.
    """
    try:
        diag = check_database_connection(db)
        return diag
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(exc),
            },
        )
