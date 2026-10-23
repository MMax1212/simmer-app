from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import admin, auth, recipes, users
from app.core.config import settings

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
app.include_router(recipes.router)
app.include_router(admin.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Simmer Backend", "version": "1.0.0"}
