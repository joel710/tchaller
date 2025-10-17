"""
Routes pour les catégories
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from database.models import Category, ActivityType

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_categories(db: Session = Depends(get_db)):
    """Obtenir toutes les catégories"""
    try:
        categories = db.query(Category).filter(Category.is_active == True).all()
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "icon": cat.icon,
                "color": cat.color,
                "parent_id": cat.parent_id
            }
            for cat in categories
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des catégories: {str(e)}"
        )

@router.get("/{category_id}/activity-types", response_model=List[dict])
async def get_activity_types_by_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir les types d'activités d'une catégorie"""
    try:
        activity_types = db.query(ActivityType)\
            .filter(ActivityType.category_id == category_id)\
            .filter(ActivityType.is_active == True)\
            .all()
        
        return [
            {
                "id": at.id,
                "name": at.name,
                "description": at.description,
                "category_id": at.category_id,
                "icon": at.icon,
                "color": at.color
            }
            for at in activity_types
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des types d'activités: {str(e)}"
        )