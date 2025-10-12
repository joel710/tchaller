"""
Schémas d'authentification
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class OTPRequest(BaseModel):
    """Demande d'OTP"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    purpose: str = Field("login", description="Purpose: login, register, reset")

class OTPVerify(BaseModel):
    """Vérification d'OTP"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp_code: str = Field(..., min_length=4, max_length=6)
    purpose: str = Field("login")

class Token(BaseModel):
    """Token d'accès"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Données du token"""
    user_id: Optional[int] = None
    phone_number: Optional[str] = None
    roles: list = []

class UserLogin(BaseModel):
    """Connexion utilisateur"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp_code: str = Field(..., min_length=4, max_length=6)

class UserRegister(BaseModel):
    """Inscription utilisateur"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    full_name: str = Field(..., min_length=2, max_length=255)
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    otp_code: str = Field(..., min_length=4, max_length=6)

class PasswordReset(BaseModel):
    """Réinitialisation de mot de passe"""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    otp_code: str = Field(..., min_length=4, max_length=6)
    new_password: str = Field(..., min_length=8)

class RefreshToken(BaseModel):
    """Rafraîchissement de token"""
    refresh_token: str