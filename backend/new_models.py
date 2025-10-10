"""
Nouveaux modèles SQLAlchemy pour la structure ultra polyvalente
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float, Index, JSON, ARRAY, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# =====================================================
# MODÈLES DE BASE
# =====================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True)
    full_name = Column(String(255))
    avatar_url = Column(Text)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_location = Column(Geometry(geometry_type='POINT', srid=4326))
    preferred_language = Column(String(5), default='fr')
    timezone = Column(String(50), default='Africa/Abidjan')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now())

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, default={})
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)

# =====================================================
# GÉOLOCALISATION
# =====================================================

class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(3), unique=True, nullable=False)
    currency = Column(String(3))
    timezone = Column(String(50))
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Region(Base):
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"))
    name = Column(String(100), nullable=False)
    code = Column(String(10))
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("regions.id"))
    name = Column(String(100), nullable=False)
    population = Column(Integer)
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
    center_point = Column(Geometry(geometry_type='POINT', srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Zone(Base):
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"))
    name = Column(String(100), nullable=False)
    type = Column(String(50), default='neighborhood')
    geometry = Column(Geometry(geometry_type='MULTIPOLYGON', srid=4326))
    center_point = Column(Geometry(geometry_type='POINT', srid=4326))
    population = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# =====================================================
# CATÉGORIES ET TYPES D'ACTIVITÉS
# =====================================================

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    color = Column(String(7))  # Hex color
    parent_id = Column(Integer, ForeignKey("categories.id"))
    level = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ActivityType(Base):
    __tablename__ = "activity_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    requires_verification = Column(Boolean, default=False)
    allows_online_booking = Column(Boolean, default=False)
    allows_delivery = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# =====================================================
# ACTIVITÉS (REMPLACE MERCHANTS)
# =====================================================

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Classification
    activity_type_id = Column(Integer, ForeignKey("activity_types.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Localisation
    address = Column(Text)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    
    # Contact
    phone_number = Column(String(20))
    whatsapp_number = Column(String(20))
    email = Column(String(255))
    website = Column(String(500))
    
    # Statut et vérification
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_open = Column(Boolean, default=True)
    verification_level = Column(Integer, default=0)
    
    # Propriétaire/Gestionnaire
    owner_id = Column(Integer, ForeignKey("users.id"))
    manager_id = Column(Integer, ForeignKey("users.id"))
    ambassador_id = Column(Integer, ForeignKey("users.id"))
    
    # Informations commerciales
    price_level = Column(Integer, default=1)
    accepts_cash = Column(Boolean, default=True)
    accepts_card = Column(Boolean, default=False)
    accepts_mobile_money = Column(Boolean, default=False)
    
    # Horaires
    opening_hours = Column(JSON, default={})
    special_hours = Column(JSON, default={})
    
    # Évaluation et popularité
    rating = Column(DECIMAL(3,2), default=0.0)
    review_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    search_count = Column(Integer, default=0)
    
    # Médias
    cover_image_url = Column(Text)
    logo_url = Column(Text)
    
    # Métadonnées
    tags = Column(ARRAY(Text))
    keywords = Column(ARRAY(Text))
    languages = Column(ARRAY(String(10)))
    
    # Données personnalisées
    custom_data = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified_at = Column(DateTime(timezone=True))
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Index spatial
    __table_args__ = (
        Index('idx_activity_location', 'location', postgresql_using='gist'),
    )

# =====================================================
# MÉDIAS
# =====================================================

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Informations du fichier
    file_url = Column(Text, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100))
    file_size = Column(Integer)
    
    # Métadonnées
    title = Column(String(255))
    description = Column(Text)
    alt_text = Column(String(255))
    
    # Dimensions
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(Integer)  # Pour vidéos/audio
    
    # Classification
    category = Column(String(50), default='general')
    is_primary = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Modération
    is_approved = Column(Boolean, default=True)
    moderation_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# =====================================================
# ÉVALUATIONS
# =====================================================

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Évaluation
    rating = Column(Integer, nullable=False)
    title = Column(String(255))
    comment = Column(Text)
    
    # Catégories d'évaluation
    category_ratings = Column(JSON, default={})
    
    # Photos
    photos = Column(ARRAY(Text))
    
    # Utilité
    helpful_count = Column(Integer, default=0)
    is_verified_purchase = Column(Boolean, default=False)
    
    # Modération
    is_approved = Column(Boolean, default=True)
    is_flagged = Column(Boolean, default=False)
    moderation_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# =====================================================
# RECHERCHES ET ANALYTICS
# =====================================================

class SearchLog(Base):
    __tablename__ = "search_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(100))
    
    # Requête
    query = Column(Text, nullable=False)
    processed_query = Column(Text)
    language = Column(String(5), default='fr')
    
    # Localisation
    user_location = Column(Geometry(geometry_type='POINT', srid=4326))
    search_radius = Column(Integer, default=5000)
    
    # Filtres
    filters = Column(JSON, default={})
    
    # Résultats
    results_count = Column(Integer, default=0)
    results_ids = Column(ARRAY(Integer))
    
    # Classification IA
    intent = Column(String(50))
    entities = Column(JSON, default={})
    confidence_score = Column(DECIMAL(3,2))
    
    # Performance
    search_time_ms = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))
    interaction_type = Column(String(50), nullable=False)
    session_id = Column(String(100))
    
    # Contexte
    referrer = Column(String(500))
    user_agent = Column(Text)
    ip_address = Column(String(45))  # IPv6 compatible
    
    # Données additionnelles
    interaction_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# =====================================================
# AMBASSADEURS
# =====================================================

class Ambassador(Base):
    __tablename__ = "ambassadors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Informations personnelles
    full_name = Column(String(255), nullable=False)
    id_document_type = Column(String(50))
    id_document_number = Column(String(100))
    id_document_image_url = Column(Text)
    
    # Statut
    status = Column(String(20), default='pending')
    level = Column(Integer, default=1)
    points = Column(Integer, default=0)
    
    # Zone de responsabilité
    assigned_zones = Column(ARRAY(Integer))
    max_activities = Column(Integer, default=10)
    
    # Performance
    activities_created = Column(Integer, default=0)
    activities_verified = Column(Integer, default=0)
    verification_accuracy = Column(DECIMAL(3,2), default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True))

# =====================================================
# INSIGHTS ET IA
# =====================================================

class DataModel(Base):
    __tablename__ = "data_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    model_type = Column(String(50), nullable=False)
    
    # Configuration
    parameters = Column(JSON, default={})
    training_data = Column(JSON, default={})
    
    # Performance
    accuracy = Column(DECIMAL(5,4))
    precision_score = Column(DECIMAL(5,4))
    recall_score = Column(DECIMAL(5,4))
    f1_score = Column(DECIMAL(5,4))
    
    # Statut
    status = Column(String(20), default='draft')
    version = Column(String(20), default='1.0.0')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    trained_at = Column(DateTime(timezone=True))

class Insight(Base):
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    insight_type = Column(String(50), nullable=False)
    
    # Données
    data = Column(JSON, nullable=False)
    visualization_config = Column(JSON, default={})
    
    # Métadonnées
    source_tables = Column(ARRAY(Text))
    filters_applied = Column(JSON, default={})
    confidence_level = Column(DECIMAL(3,2))
    
    # Ciblage
    target_audience = Column(String(50), default='all')
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))

# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================

def create_db_and_tables():
    """Crée toutes les tables dans la base de données"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Obtient une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# RELATIONS
# =====================================================

# Relations User
User.roles = relationship("UserRole", back_populates="user")
User.owned_activities = relationship("Activity", foreign_keys="Activity.owner_id", back_populates="owner")
User.managed_activities = relationship("Activity", foreign_keys="Activity.manager_id", back_populates="manager")
User.ambassador_activities = relationship("Activity", foreign_keys="Activity.ambassador_id", back_populates="ambassador")
User.reviews = relationship("Review", back_populates="user")
User.interactions = relationship("UserInteraction", back_populates="user")
User.media = relationship("Media", back_populates="user")
User.ambassador = relationship("Ambassador", back_populates="user", uselist=False)

# Relations Activity
Activity.activity_type = relationship("ActivityType", back_populates="activities")
Activity.category = relationship("Category", back_populates="activities")
Activity.zone = relationship("Zone", back_populates="activities")
Activity.owner = relationship("User", foreign_keys="Activity.owner_id", back_populates="owned_activities")
Activity.manager = relationship("User", foreign_keys="Activity.manager_id", back_populates="managed_activities")
Activity.ambassador = relationship("User", foreign_keys="Activity.ambassador_id", back_populates="ambassador_activities")
Activity.media = relationship("Media", back_populates="activity")
Activity.reviews = relationship("Review", back_populates="activity")
Activity.interactions = relationship("UserInteraction", back_populates="activity")

# Relations Category
Category.activities = relationship("Activity", back_populates="category")
Category.children = relationship("Category", back_populates="parent")
Category.parent = relationship("Category", back_populates="children", remote_side="Category.id")

# Relations ActivityType
ActivityType.activities = relationship("Activity", back_populates="activity_type")
ActivityType.category = relationship("Category", back_populates="activity_types")

# Relations Ambassador
Ambassador.user = relationship("User", back_populates="ambassador")

# Relations Review
Review.user = relationship("User", back_populates="reviews")
Review.activity = relationship("Activity", back_populates="reviews")

# Relations Media
Media.user = relationship("User", back_populates="media")
Media.activity = relationship("Activity", back_populates="media")

# Relations UserInteraction
UserInteraction.user = relationship("User", back_populates="interactions")
UserInteraction.activity = relationship("Activity", back_populates="interactions")

# Relations UserRole
UserRole.user = relationship("User", back_populates="roles")
UserRole.role = relationship("Role", back_populates="user_roles")

# Relations Role
Role.user_roles = relationship("UserRole", back_populates="role")

# Relations Zone
Zone.activities = relationship("Activity", back_populates="zone")
Zone.city = relationship("City", back_populates="zones")

# Relations City
City.zones = relationship("Zone", back_populates="city")
City.region = relationship("Region", back_populates="cities")

# Relations Region
Region.cities = relationship("City", back_populates="region")
Region.country = relationship("Country", back_populates="regions")

# Relations Country
Country.regions = relationship("Region", back_populates="country")
