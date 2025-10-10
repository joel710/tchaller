"""
Configuration de la connexion à la base de données
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.config import settings

# Configuration de l'engine avec optimisations
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug,
    connect_args={
        "options": "-c timezone=utc"
    } if "postgresql" in settings.database_url else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

def get_db():
    """
    Dependency pour obtenir une session de base de données
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Créer toutes les tables dans la base de données
    """
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Supprimer toutes les tables (ATTENTION: supprime toutes les données)
    """
    Base.metadata.drop_all(bind=engine)