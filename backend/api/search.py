"""
Routes de recherche
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from schemas.search import SearchRequest, SearchResponse, SearchAnalytics
from services.search_service import SearchService

router = APIRouter()

@router.post("/", response_model=SearchResponse)
async def search_activities(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Recherche d'activités avec moteur conversationnel"""
    search_service = SearchService(db)
    
    try:
        result = await search_service.search_activities(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche: {str(e)}"
        )

@router.get("/popular", response_model=List[dict])
async def get_popular_searches(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Obtenir les recherches populaires"""
    search_service = SearchService(db)
    
    try:
        popular_searches = await search_service.get_popular_searches(limit)
        return popular_searches
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.get("/analytics", response_model=SearchAnalytics)
async def get_search_analytics(db: Session = Depends(get_db)):
    """Obtenir les analytics de recherche"""
    search_service = SearchService(db)
    
    try:
        analytics = await search_service.get_search_analytics()
        return SearchAnalytics(**analytics)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des analytics: {str(e)}"
        )