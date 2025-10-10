"""
Schémas pour les utilisateurs
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """Base pour les utilisateurs"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')

class UserCreate(UserBase):
    """Création d'utilisateur"""
    pass

class UserUpdate(BaseModel):
    """Mise à jour d'utilisateur"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    language: Optional[str] = Field(None, pattern=r'^[a-z]{2}$')
    timezone: Optional[str] = None

class User(UserBase):
    """Modèle utilisateur complet"""
    id: int
    is_verified: bool = False
    is_active: bool = True
    language: str = "fr"
    timezone: str = "Africa/Abidjan"
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserResponse(User):
    """Réponse utilisateur avec relations"""
    roles: List[str] = []
    activities_count: int = 0
    reviews_count: int = 0

class UserProfile(BaseModel):
    """Profil utilisateur détaillé"""
    id: int
    phone_number: str
    full_name: str
    email: Optional[str] = None
    is_verified: bool
    language: str
    timezone: str
    roles: List[str]
    stats: dict = {}
    created_at: datetime

class UserStats(BaseModel):
    """Statistiques utilisateur"""
    total_activities: int = 0
    verified_activities: int = 0
    total_reviews: int = 0
    total_searches: int = 0
    last_login: Optional[datetime] = None