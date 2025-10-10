"""
Schémas pour la recherche
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .activities import ActivityResponse

class SearchRequest(BaseModel):
    """Requête de recherche"""
    query: str = Field(..., min_length=1, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius: Optional[float] = Field(5000, ge=100, le=50000, description="Rayon en mètres")
    category_id: Optional[int] = None
    activity_type_id: Optional[int] = None
    price_level: Optional[int] = Field(None, ge=1, le=3)
    is_open_now: Optional[bool] = None
    is_verified: Optional[bool] = None
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    limit: Optional[int] = Field(10, ge=1, le=50)
    user_id: Optional[int] = None

class SearchResponse(BaseModel):
    """Réponse de recherche"""
    query: str
    processed_query: str
    intent: str
    entities: Dict[str, Any]
    activities: List[ActivityResponse]
    total_results: int
    response_time: float
    suggestions: List[str] = []
    filters_applied: Dict[str, Any] = {}

class SearchFilters(BaseModel):
    """Filtres de recherche avancés"""
    categories: List[int] = []
    activity_types: List[int] = []
    price_levels: List[int] = []
    zones: List[int] = []
    is_verified: Optional[bool] = None
    is_open_now: Optional[bool] = None
    min_rating: Optional[float] = None
    max_distance: Optional[float] = None

class SearchSuggestion(BaseModel):
    """Suggestion de recherche"""
    text: str
    type: str  # 'category', 'activity_type', 'location', 'popular'
    count: Optional[int] = None

class SearchAnalytics(BaseModel):
    """Analytics de recherche"""
    total_searches: int
    unique_users: int
    popular_queries: List[Dict[str, Any]]
    search_intents: Dict[str, int]
    average_response_time: float
    success_rate: float