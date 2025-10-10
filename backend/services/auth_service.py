"""
Service d'authentification
"""
from typing import Optional
from sqlalchemy.orm import Session
from backend.database.models import User, UserRole, Role
from backend.schemas.users import UserCreate
from backend.config import settings
import jwt
from datetime import datetime, timedelta

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_or_create_user(self, phone_number: str, full_name: str = "Utilisateur") -> User:
        """Obtenir ou créer un utilisateur"""
        user = self.db.query(User).filter(User.phone_number == phone_number).first()
        
        if not user:
            user = User(
                phone_number=phone_number,
                full_name=full_name,
                is_verified=True
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    async def create_user(self, phone_number: str, full_name: str, email: Optional[str] = None) -> User:
        """Créer un nouvel utilisateur"""
        user = User(
            phone_number=phone_number,
            full_name=full_name,
            email=email,
            is_verified=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def create_access_token(self, user_id: int, phone_number: str) -> str:
        """Créer un token d'accès JWT"""
        data = {
            "user_id": user_id,
            "phone_number": phone_number,
            "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        }
        return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)
    
    async def get_current_user(self, token: str) -> User:
        """Obtenir l'utilisateur actuel à partir du token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("user_id")
            if user_id is None:
                raise Exception("Token invalide")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if user is None:
                raise Exception("Utilisateur non trouvé")
            
            return user
        except jwt.ExpiredSignatureError:
            raise Exception("Token expiré")
        except jwt.JWTError:
            raise Exception("Token invalide")