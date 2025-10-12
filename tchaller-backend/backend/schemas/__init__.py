"""
Schémas Pydantic pour l'API Tcha-llé
"""
from .auth import *
from .activities import *
from .users import *
from .search import *
from .common import *

__all__ = [
    # Auth
    "OTPRequest",
    "OTPVerify", 
    "Token",
    "TokenData",
    "UserLogin",
    "UserRegister",
    
    # Users
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "User",
    "UserResponse",
    
    # Activities
    "ActivityBase",
    "ActivityCreate",
    "ActivityUpdate", 
    "Activity",
    "ActivityResponse",
    "ActivityListResponse",
    
    # Search
    "SearchRequest",
    "SearchResponse",
    "SearchFilters",
    
    # Common
    "MessageResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginationResponse"
]