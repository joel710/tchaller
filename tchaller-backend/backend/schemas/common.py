"""
Schémas communs pour l'API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

class MessageResponse(BaseModel):
    """Réponse de message simple"""
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    """Réponse d'erreur"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

class PaginationParams(BaseModel):
    """Paramètres de pagination"""
    page: int = Field(1, ge=1, description="Numéro de page")
    size: int = Field(20, ge=1, le=100, description="Taille de la page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

class PaginationResponse(BaseModel):
    """Réponse paginée"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    
    @classmethod
    def create(cls, items: List[Any], total: int, page: int, size: int):
        pages = (total + size - 1) // size
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

class LocationData(BaseModel):
    """Données de localisation"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    zone_id: Optional[int] = None

class ContactInfo(BaseModel):
    """Informations de contact"""
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class BusinessHours(BaseModel):
    """Horaires d'ouverture"""
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None

class MediaInfo(BaseModel):
    """Informations sur les médias"""
    id: int
    file_url: str
    file_type: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    created_at: datetime

class ReviewInfo(BaseModel):
    """Informations sur les avis"""
    id: int
    user_name: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime
    is_verified: bool = False

class StatsInfo(BaseModel):
    """Informations statistiques"""
    total_activities: int = 0
    verified_activities: int = 0
    pending_activities: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    total_views: int = 0