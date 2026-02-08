from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints import router as api_router
from services import init_db

app = FastAPI(title="Recipe Manager API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok"}
