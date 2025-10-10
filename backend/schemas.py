from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from geoalchemy2.shape import to_shape

class UserBase(BaseModel):
    phone_number: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserCreateResponse(UserBase):
    id: int
    is_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AmbassadorBase(BaseModel):
    full_name: str

class AmbassadorCreate(AmbassadorBase):
    user_id: int

class Ambassador(AmbassadorBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MerchantPhotoBase(BaseModel):
    image_url: str

class MerchantPhotoCreate(MerchantPhotoBase):
    merchant_id: int

class MerchantPhoto(MerchantPhotoBase):
    id: int
    merchant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MerchantBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    opening_hours: Optional[str] = None
    price_level: int = Field(default=1, ge=1, le=3)

class MerchantCreate(MerchantBase):
    category_id: int
    latitude: float
    longitude: float
    ambassador_id: Optional[int] = None

class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    opening_hours: Optional[str] = None
    price_level: Optional[int] = Field(None, ge=1, le=3)
    is_open: Optional[bool] = None

class Merchant(MerchantBase):
    id: int
    category_id: int
    is_verified: bool
    is_open: bool
    rating: float
    review_count: int
    ambassador_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[Category] = None
    photos: List[MerchantPhoto] = []
    distance: Optional[float] = None  # Calculated distance in meters

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius: Optional[float] = Field(default=5000, description="Search radius in meters")
    category_id: Optional[int] = None
    price_level: Optional[int] = Field(None, ge=1, le=3)
    is_open_now: Optional[bool] = None
    limit: Optional[int] = Field(default=10, description="Maximum number of results")
    user_id: Optional[int] = None

class SearchResponse(BaseModel):
    merchants: List[Merchant]
    total_count: int
    query_processed: str
    search_time_ms: float

class ConversationBase(BaseModel):
    user_id: int

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    messages: List['Message'] = []

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    sender: str

class MessageCreate(MessageBase):
    conversation_id: int

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class OTPRequest(BaseModel):
    phone_number: str

class OTPVerify(BaseModel):
    phone_number: str
    otp_code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    phone_number: Optional[str] = None

class StatusUpdate(BaseModel):
    merchant_id: int
    status: str  # 'OPEN' or 'CLOSED'
    timestamp: Optional[datetime] = None

class WebhookRequest(BaseModel):
    From: str
    Body: str
    MessageSid: str