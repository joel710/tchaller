from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db, User
from .schemas import TokenData
import random
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# In-memory OTP storage (in production, use Redis)
otp_storage = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        token_data = TokenData(phone_number=phone_number)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    token_data = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.phone_number == token_data.phone_number).first()
    if user is None:
        raise credentials_exception
    return user

def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp(phone_number: str) -> str:
    """Send OTP to phone number and store it"""
    otp = generate_otp()
    otp_storage[phone_number] = {
        "otp": otp,
        "created_at": datetime.utcnow(),
        "attempts": 0
    }
    
    # In production, integrate with Twilio here
    print(f"OTP for {phone_number}: {otp}")
    return otp

def verify_otp(phone_number: str, otp: str) -> bool:
    """Verify OTP and clean up storage"""
    if phone_number not in otp_storage:
        return False
    
    stored_data = otp_storage[phone_number]
    
    # Check if OTP is expired (5 minutes)
    if datetime.utcnow() - stored_data["created_at"] > timedelta(minutes=5):
        del otp_storage[phone_number]
        return False
    
    # Check attempts limit
    if stored_data["attempts"] >= 3:
        del otp_storage[phone_number]
        return False
    
    # Verify OTP
    if stored_data["otp"] == otp:
        del otp_storage[phone_number]
        return True
    else:
        stored_data["attempts"] += 1
        return False