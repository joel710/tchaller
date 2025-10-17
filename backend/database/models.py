"""
Modèles de base de données ultra polyvalents pour Tcha-llé
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from .connection import Base
import enum

# Enums
class UserRoleEnum(str, enum.Enum):
    ADMIN = "admin"
    AMBASSADOR = "ambassador"
    USER = "user"
    MODERATOR = "moderator"

class ActivityStatusEnum(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"

class VerificationStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class InteractionTypeEnum(str, enum.Enum):
    SEARCH = "search"
    VIEW = "view"
    CLICK = "click"
    CALL = "call"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEBSITE = "website"
    DIRECTION = "direction"

# Modèles de base
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_location = Column(Geometry('POINT', srid=4326))
    language = Column(String(5), default="fr") # Reverted
    timezone = Column(String(50), default="Africa/Abidjan") # Reverted
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    roles = relationship("UserRole", back_populates="user")
    activities = relationship("Activity", back_populates="owner")
    reviews = relationship("Review", back_populates="user")
    interactions = relationship("UserInteraction", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    ambassador = relationship("Ambassador", back_populates="user", uselist=False)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    users = relationship("UserRole", back_populates="role")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

# Géolocalisation
class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(3), unique=True, nullable=False)
    phone_code = Column(String(5))
    
    # Relations
    regions = relationship("Region", back_populates="country")

class Region(Base):
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    
    # Relations
    country = relationship("Country", back_populates="regions")
    cities = relationship("City", back_populates="region")

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    
    # Relations
    region = relationship("Region", back_populates="cities")
    zones = relationship("Zone", back_populates="city")

class Zone(Base):
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    boundary = Column(Geometry('POLYGON', srid=4326))
    
    # Relations
    city = relationship("City", back_populates="zones")
    service_zones = relationship("ServiceZone", back_populates="zone")
    activities = relationship("Activity", back_populates="zone")

class ServiceZone(Base):
    __tablename__ = "service_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"), nullable=False)
    is_available = Column(Boolean, default=True)
    
    # Relations
    zone = relationship("Zone", back_populates="service_zones")
    activity_type = relationship("ActivityType", back_populates="service_zones")

# Catégorisation
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True) # Added slug column
    description = Column(Text)
    icon = Column(String(50))
    color = Column(String(7))  # Hex color
    parent_id = Column(Integer, ForeignKey("categories.id"))
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    parent = relationship("Category", remote_side=[id])
    children = relationship("Category", back_populates="parent")
    activities = relationship("Activity", back_populates="category")

class ActivityType(Base):
    __tablename__ = "activity_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    icon = Column(String(50))
    color = Column(String(7))
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    category = relationship("Category")
    activities = relationship("Activity", back_populates="activity_type")
    service_zones = relationship("ServiceZone", back_populates="activity_type")

# Activités (remplace les merchants)
class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    address = Column(Text, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False, index=True)
    
    # Contact
    phone_number = Column(String(20))
    whatsapp_number = Column(String(20))
    email = Column(String(255))
    website = Column(String(500))
    
    # Informations commerciales
    opening_hours = Column(JSON)
    price_level = Column(Integer, default=2)  # 1-3
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Statut
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    status = Column(SQLEnum(ActivityStatusEnum), default=ActivityStatusEnum.ACTIVE)
    
    # Relations
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    category = relationship("Category", back_populates="activities")
    activity_type = relationship("ActivityType", back_populates="activities")
    zone = relationship("Zone", back_populates="activities")
    owner = relationship("User", back_populates="activities")
    media = relationship("Media", back_populates="activity")
    reviews = relationship("Review", back_populates="activity")

# Médias
class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer)
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    activity = relationship("Activity", back_populates="media")

# Avis
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    activity = relationship("Activity", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

# Logs et analytics
class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    processed_query = Column(Text)
    intent = Column(String(50))
    entities = Column(JSON)
    results_count = Column(Integer, default=0)
    response_time = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User")

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))
    interaction_type = Column(SQLEnum(InteractionTypeEnum), nullable=False)
    session_id = Column(String(100))
    
    # Contexte
    referrer = Column(String(500))
    user_agent = Column(Text)
    ip_address = Column(String(45))  # IPv6 compatible
    
    # Données additionnelles
    interaction_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User", back_populates="interactions")
    activity = relationship("Activity")

# Conversations IA
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), nullable=False)
    context = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relations
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    sender_type = Column(String(20), nullable=False)  # 'user' ou 'bot'
    intent = Column(String(50))
    entities = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    conversation = relationship("Conversation", back_populates="messages")

# Ambassadeurs
class Ambassador(Base):
    __tablename__ = "ambassadors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id")) # Reverted
    commission_rate = Column(Float, default=0.0) # Reverted
    total_activities = Column(Integer, default=0) # Reverted
    verified_activities = Column(Integer, default=0) # Reverted
    is_active = Column(Boolean, default=True) # Reverted
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User", back_populates="ambassador")
    zone = relationship("Zone") # Reverted

# Vérifications
class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    ambassador_id = Column(Integer, ForeignKey("ambassadors.id"))
    status = Column(SQLEnum(VerificationStatusEnum), default=VerificationStatusEnum.PENDING)
    notes = Column(Text)
    verified_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    activity = relationship("Activity")
    ambassador = relationship("Ambassador")

# Webhooks
class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    event_type = Column(String(50), nullable=False)
    secret = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    logs = relationship("WebhookLog", back_populates="webhook")

class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, ForeignKey("webhooks.id"), nullable=False)
    payload = Column(JSON)
    response_status = Column(Integer)
    response_body = Column(Text)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    webhook = relationship("Webhook", back_populates="logs")

# IA et Analytics
class DataModel(Base):
    __tablename__ = "data_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    insights = relationship("Insight", back_populates="data_model")

class Insight(Base):
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    data_model_id = Column(Integer, ForeignKey("data_models.id"), nullable=False)
    insight_type = Column(String(50), nullable=False)
    data = Column(JSON)
    confidence = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    data_model = relationship("DataModel", back_populates="insights")

# Abonnements
class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="XOF")
    features = Column(JSON)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    subscriptions = relationship("Subscription", back_populates="plan")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(String(20), default="active")
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    
    # Relations
    user = relationship("User")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

# Notifications
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)
    data = Column(JSON)
    is_read = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User")

# Audit
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = Column(JSON)
    new_values = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    user = relationship("User")