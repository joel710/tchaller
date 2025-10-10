"""
Routes pour les utilisateurs
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.users import UserResponse, UserUpdate, UserProfile, UserStats
from backend.services.auth_service import AuthService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtenir les informations de l'utilisateur connecté"""
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Mettre à jour les informations de l'utilisateur connecté"""
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        
        # Mettre à jour les champs fournis
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtenir le profil détaillé de l'utilisateur"""
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        
        # Construire le profil
        profile = UserProfile(
            id=user.id,
            phone_number=user.phone_number,
            full_name=user.full_name,
            email=user.email,
            is_verified=user.is_verified,
            language=user.language,
            timezone=user.timezone,
            roles=[],  # À implémenter avec les rôles
            stats={},  # À implémenter avec les statistiques
            created_at=user.created_at
        )
        
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du profil: {str(e)}"
        )

@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques de l'utilisateur"""
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        
        # Calculer les statistiques
        stats = UserStats(
            total_activities=0,  # À implémenter
            verified_activities=0,  # À implémenter
            total_reviews=0,  # À implémenter
            total_searches=0,  # À implémenter
            last_login=None  # À implémenter
        )
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )