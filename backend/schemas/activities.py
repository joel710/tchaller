"""
Schémas pour les activités
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from .common import LocationData, ContactInfo, BusinessHours, MediaInfo, ReviewInfo

class ActivityBase(BaseModel):
    """Base pour les activités"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    address: str = Field(..., min_length=5)
    category_id: int
    activity_type_id: int
    zone_id: Optional[int] = None
    price_level: int = Field(1, ge=1, le=3)
    opening_hours: Optional[dict] = None

class ActivityCreate(ActivityBase, LocationData, ContactInfo):
    """Création d'une activité"""
    pass

class ActivityUpdate(BaseModel):
    """Mise à jour d'une activité"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = Field(None, min_length=5)
    category_id: Optional[int] = None
    activity_type_id: Optional[int] = None
    zone_id: Optional[int] = None
    price_level: Optional[int] = Field(None, ge=1, le=3)
    opening_hours: Optional[dict] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class Activity(ActivityBase):
    """Modèle d'activité complet"""
    id: int
    latitude: float
    longitude: float
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    rating: float = 0.0
    review_count: int = 0
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    # Relations
    category_name: Optional[str] = None
    activity_type_name: Optional[str] = None
    zone_name: Optional[str] = None
    owner_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class ActivityResponse(Activity):
    """Réponse d'activité avec relations"""
    media: List[MediaInfo] = []
    reviews: List[ReviewInfo] = []
    distance: Optional[float] = None  # Distance en mètres si calculée

class ActivityListResponse(BaseModel):
    """Réponse de liste d'activités"""
    activities: List[ActivityResponse]
    total: int
    page: int
    size: int
    pages: int

class ActivityFilters(BaseModel):
    """Filtres pour les activités"""
    category_id: Optional[int] = None
    activity_type_id: Optional[int] = None
    zone_id: Optional[int] = None
    price_level: Optional[int] = Field(None, ge=1, le=3)
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    search_query: Optional[str] = None

class ActivityStats(BaseModel):
    """Statistiques d'une activité"""
    total_views: int = 0
    total_clicks: int = 0
    total_calls: int = 0
    total_whatsapp: int = 0
    total_emails: int = 0
    total_website_visits: int = 0
    total_directions: int = 0
    last_30_days_views: int = 0
    last_30_days_clicks: int = 0