from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base, create_db_and_tables, User
from .routers import auth, merchants, webhook, categories
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title="Tcha-llé API",
    description="API pour l'économie informelle locale avec moteur de recherche conversationnel",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(merchants.router)
app.include_router(webhook.router)
app.include_router(categories.router)

# Mount static files
app.mount("/static", StaticFiles(directory="/workspace/frontend"), name="static")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
async def read_root():
    return {
        "message": "Bienvenue sur l'API Tcha-llé",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}