"""
Routes d'authentification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.auth import OTPRequest, OTPVerify, Token, UserLogin, UserRegister
from backend.schemas.users import UserResponse
from backend.services.auth_service import AuthService
from backend.services.otp_service import OTPService
from backend.config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/request-otp", response_model=dict)
async def request_otp(request: OTPRequest, db: Session = Depends(get_db)):
    """Demander un code OTP"""
    otp_service = OTPService()
    
    try:
        otp_code = await otp_service.generate_otp(request.phone_number)
        await otp_service.send_otp(request.phone_number, otp_code)
        
        return {
            "message": "Code OTP envoyé avec succès",
            "success": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'envoi de l'OTP: {str(e)}"
        )

@router.post("/verify-otp", response_model=Token)
async def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    """Vérifier un code OTP et créer un token"""
    auth_service = AuthService(db)
    otp_service = OTPService()
    
    try:
        # Vérifier l'OTP
        is_valid = await otp_service.verify_otp(request.phone_number, request.otp_code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code OTP invalide ou expiré"
            )
        
        # Créer ou récupérer l'utilisateur
        user = await auth_service.get_or_create_user(
            phone_number=request.phone_number,
            full_name="Utilisateur"  # Sera mis à jour lors de l'inscription
        )
        
        # Créer le token
        token = auth_service.create_access_token(user.id, user.phone_number)
        
        return Token(
            access_token=token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la vérification: {str(e)}"
        )

@router.post("/register", response_model=UserResponse)
async def register(request: UserRegister, db: Session = Depends(get_db)):
    """Inscription d'un nouvel utilisateur"""
    auth_service = AuthService(db)
    otp_service = OTPService()
    
    try:
        # Vérifier l'OTP
        is_valid = await otp_service.verify_otp(request.phone_number, request.otp_code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code OTP invalide ou expiré"
            )
        
        # Créer l'utilisateur
        user = await auth_service.create_user(
            phone_number=request.phone_number,
            full_name=request.full_name,
            email=request.email
        )
        
        return UserResponse.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'inscription: {str(e)}"
        )

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

@router.post("/logout", response_model=dict)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Déconnexion (invalider le token)"""
    # Dans une implémentation complète, on ajouterait le token à une liste noire
    return {
        "message": "Déconnexion réussie",
        "success": True
    }