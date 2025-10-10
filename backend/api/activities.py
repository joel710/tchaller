"""
Routes pour les activités
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas.activities import ActivityCreate, ActivityUpdate, ActivityResponse, ActivityListResponse, ActivityFilters
from backend.schemas.common import PaginationParams, PaginationResponse
from backend.services.activity_service import ActivityService
from backend.services.auth_service import AuthService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.post("/", response_model=ActivityResponse)
async def create_activity(
    activity_data: ActivityCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Créer une nouvelle activité"""
    auth_service = AuthService(db)
    activity_service = ActivityService(db)
    
    try:
        # Obtenir l'utilisateur actuel
        user = await auth_service.get_current_user(credentials.credentials)
        
        # Créer l'activité
        activity = await activity_service.create_activity(activity_data, user.id)
        
        return ActivityResponse.from_orm(activity)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la création: {str(e)}"
        )

@router.get("/", response_model=ActivityListResponse)
async def get_activities(
    pagination: PaginationParams = Depends(),
    filters: ActivityFilters = Depends(),
    db: Session = Depends(get_db)
):
    """Obtenir la liste des activités avec filtres"""
    activity_service = ActivityService(db)
    
    try:
        # Construire la requête de base
        query = db.query(Activity).filter(Activity.is_active == True)
        
        # Appliquer les filtres
        if filters.category_id:
            query = query.filter(Activity.category_id == filters.category_id)
        if filters.activity_type_id:
            query = query.filter(Activity.activity_type_id == filters.activity_type_id)
        if filters.zone_id:
            query = query.filter(Activity.zone_id == filters.zone_id)
        if filters.price_level:
            query = query.filter(Activity.price_level == filters.price_level)
        if filters.is_verified is not None:
            query = query.filter(Activity.is_verified == filters.is_verified)
        if filters.min_rating:
            query = query.filter(Activity.rating >= filters.min_rating)
        if filters.search_query:
            query = query.filter(
                Activity.name.ilike(f"%{filters.search_query}%") |
                Activity.description.ilike(f"%{filters.search_query}%")
            )
        
        # Compter le total
        total = query.count()
        
        # Appliquer la pagination
        activities = query.offset(pagination.offset).limit(pagination.size).all()
        
        # Convertir en ActivityResponse
        activity_responses = []
        for activity in activities:
            activity_responses.append(ActivityResponse.from_orm(activity))
        
        return ActivityListResponse(
            activities=activity_responses,
            total=total,
            page=pagination.page,
            size=pagination.size,
            pages=(total + pagination.size - 1) // pagination.size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )

@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """Obtenir une activité par ID"""
    activity_service = ActivityService(db)
    
    activity = await activity_service.get_activity(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activité non trouvée"
        )
    
    return ActivityResponse.from_orm(activity)

@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Mettre à jour une activité"""
    auth_service = AuthService(db)
    activity_service = ActivityService(db)
    
    try:
        # Obtenir l'utilisateur actuel
        user = await auth_service.get_current_user(credentials.credentials)
        
        # Vérifier que l'utilisateur est propriétaire de l'activité
        activity = await activity_service.get_activity(activity_id)
        if not activity or activity.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'êtes pas autorisé à modifier cette activité"
            )
        
        # Mettre à jour l'activité
        updated_activity = await activity_service.update_activity(activity_id, activity_data)
        
        return ActivityResponse.from_orm(updated_activity)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.delete("/{activity_id}", response_model=dict)
async def delete_activity(
    activity_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Supprimer une activité"""
    auth_service = AuthService(db)
    activity_service = ActivityService(db)
    
    try:
        # Obtenir l'utilisateur actuel
        user = await auth_service.get_current_user(credentials.credentials)
        
        # Vérifier que l'utilisateur est propriétaire de l'activité
        activity = await activity_service.get_activity(activity_id)
        if not activity or activity.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'êtes pas autorisé à supprimer cette activité"
            )
        
        # Supprimer l'activité
        success = await activity_service.delete_activity(activity_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activité non trouvée"
            )
        
        return {"message": "Activité supprimée avec succès", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )

@router.get("/categories/", response_model=List[dict])
async def get_categories(db: Session = Depends(get_db)):
    """Obtenir toutes les catégories"""
    activity_service = ActivityService(db)
    
    try:
        categories = await activity_service.get_categories()
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "icon": cat.icon,
                "color": cat.color
            }
            for cat in categories
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des catégories: {str(e)}"
        )

@router.get("/activity-types/", response_model=List[dict])
async def get_activity_types(
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Obtenir les types d'activités"""
    activity_service = ActivityService(db)
    
    try:
        activity_types = await activity_service.get_activity_types(category_id)
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