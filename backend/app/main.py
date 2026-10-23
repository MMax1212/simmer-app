from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Simmer API",
    description="Backend REST API for Simmer Cooking Social Network",
    version="1.0.0"
)

# Allow CORS during local development between frontend (5173) and backend (8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    """Health check endpoint to verify backend connectivity."""
    return {"status": "ok", "app": "Simmer Backend", "version": "1.0.0"}

@app.get("/api/recipes/placeholder")
def sample_recipes():
    """Placeholder endpoint for initial testing."""
    return [
        {
            "id": 1,
            "title": "Grandma's Rustic Tomato Pasta",
            "author": "Chef Maximo",
            "cook_time_mins": 25,
            "likes": 12
        },
        {
            "id": 2,
            "title": "Crispy Avocado Toast",
            "author": "Chef Bryan",
            "cook_time_mins": 10,
            "likes": 8
        }
    ]
