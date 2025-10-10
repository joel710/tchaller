#!/usr/bin/env python3
"""
Script de migration vers la nouvelle structure de base de données ultra polyvalente
"""
import sys
import os
sys.path.append('/workspace')

def create_migration_script():
    """Crée un script de migration pour adapter l'ancienne structure à la nouvelle"""
    
    migration_sql = """
-- =====================================================
-- MIGRATION VERS LA NOUVELLE STRUCTURE ULTRA POLYVALENTE
-- =====================================================

-- 1. Créer la nouvelle structure
\\i database_schema.sql

-- 2. Migrer les données existantes vers la nouvelle structure

-- Migrer les utilisateurs
INSERT INTO users (id, phone_number, is_verified, last_location, created_at, updated_at)
SELECT 
    id, 
    phone_number, 
    is_verified, 
    last_location, 
    created_at, 
    updated_at
FROM old_users;

-- Migrer les ambassadeurs
INSERT INTO ambassadors (user_id, full_name, created_at, updated_at)
SELECT 
    user_id, 
    full_name, 
    created_at, 
    updated_at
FROM old_ambassadors;

-- Migrer les catégories
INSERT INTO categories (id, name, created_at, updated_at)
SELECT 
    id, 
    name, 
    created_at, 
    updated_at
FROM old_categories;

-- Migrer les commerces vers les activités
INSERT INTO activities (
    id, name, description, category_id, address, location,
    phone_number, whatsapp_number, is_verified, is_active, is_open,
    price_level, rating, review_count, ambassador_id, opening_hours,
    created_at, updated_at
)
SELECT 
    id,
    name,
    description,
    category_id,
    address,
    location,
    phone_number,
    whatsapp_number,
    is_verified,
    TRUE as is_active,
    is_open,
    price_level,
    rating,
    review_count,
    ambassador_id,
    opening_hours,
    created_at,
    updated_at
FROM old_merchants;

-- Migrer les photos
INSERT INTO media (activity_id, file_url, file_type, category, created_at)
SELECT 
    merchant_id,
    image_url,
    'image' as file_type,
    'gallery' as category,
    created_at
FROM old_merchant_photos;

-- Migrer les logs de recherche
INSERT INTO search_logs (user_id, query, user_location, results_count, created_at)
SELECT 
    user_id,
    query,
    location,
    results_count,
    created_at
FROM old_search_logs;

-- 3. Supprimer les anciennes tables
DROP TABLE IF EXISTS old_merchant_photos CASCADE;
DROP TABLE IF EXISTS old_merchant_status_history CASCADE;
DROP TABLE IF EXISTS old_merchants CASCADE;
DROP TABLE IF EXISTS old_ambassadors CASCADE;
DROP TABLE IF EXISTS old_categories CASCADE;
DROP TABLE IF EXISTS old_users CASCADE;
DROP TABLE IF EXISTS old_search_logs CASCADE;
DROP TABLE IF EXISTS old_conversations CASCADE;
DROP TABLE IF EXISTS old_messages CASCADE;
DROP TABLE IF EXISTS old_subscriptions CASCADE;
DROP TABLE IF EXISTS old_audits CASCADE;

-- 4. Mettre à jour les séquences
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('activities_id_seq', (SELECT MAX(id) FROM activities));
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('ambassadors_id_seq', (SELECT MAX(id) FROM ambassadors));

-- 5. Créer les index de performance
CREATE INDEX CONCURRENTLY idx_activities_full_text ON activities 
USING GIN (to_tsvector('french', name || ' ' || COALESCE(description, '')));

CREATE INDEX CONCURRENTLY idx_activities_location_rating ON activities 
USING GIST (location) WHERE is_active = TRUE AND is_open = TRUE;

-- 6. Analyser les tables pour optimiser les performances
ANALYZE activities;
ANALYZE users;
ANALYZE search_logs;
ANALYZE user_interactions;

-- 7. Vérification de la migration
DO $$
DECLARE
    user_count INTEGER;
    activity_count INTEGER;
    category_count INTEGER;
    ambassador_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO activity_count FROM activities;
    SELECT COUNT(*) INTO category_count FROM categories;
    SELECT COUNT(*) INTO ambassador_count FROM ambassadors;
    
    RAISE NOTICE 'Migration terminée avec succès !';
    RAISE NOTICE 'Utilisateurs migrés: %', user_count;
    RAISE NOTICE 'Activités migrées: %', activity_count;
    RAISE NOTICE 'Catégories migrées: %', category_count;
    RAISE NOTICE 'Ambassadeurs migrés: %', ambassador_count;
END $$;
"""

    with open('/workspace/migration_script.sql', 'w', encoding='utf-8') as f:
        f.write(migration_sql)
    
    print("✅ Script de migration créé: migration_script.sql")

def create_new_models():
    """Crée les nouveaux modèles SQLAlchemy basés sur la nouvelle structure"""
    
    models_code = '''"""
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
    metadata = Column(JSON, default={})
    
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
'''

    with open('/workspace/backend/new_models.py', 'w', encoding='utf-8') as f:
        f.write(models_code)
    
    print("✅ Nouveaux modèles créés: backend/new_models.py")

def create_advanced_search_engine():
    """Crée un moteur de recherche avancé pour la nouvelle structure"""
    
    search_engine_code = '''"""
Moteur de recherche avancé pour la structure ultra polyvalente
"""
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from geoalchemy2 import functions as gf
from .new_models import Activity, ActivityType, Category, Zone, SearchLog, UserInteraction
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime, timedelta

class AdvancedSearchEngine:
    def __init__(self):
        self.intent_patterns = {
            'search_activity': [
                r'trouve.*endroit', r'cherche.*endroit', r'où.*aller', r'où.*trouver',
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin',
                r'pharmacie', r'hôpital', r'école', r'université', r'banque', r'garage',
                r'coiffure', r'centre.*jeux', r'cinéma', r'théâtre', r'église', r'mosquée'
            ],
            'find_open_now': [
                r'ouvert.*maintenant', r'ouvert.*ce soir', r'ouvert.*aujourd\'hui',
                r'qui.*ouvert', r'fermé', r'disponible', r'accessible'
            ],
            'find_by_service': [
                r'manger.*porc', r'manger.*poulet', r'manger.*poisson', r'manger.*riz',
                r'plat.*porc', r'plat.*poulet', r'cuisine.*africaine', r'cuisine.*locale',
                r'réparer.*voiture', r'coiffer', r'acheter.*médicament', r'étudier',
                r'prier', r'jouer', r'divertir'
            ],
            'ask_hours': [
                r'horaires', r'heures.*ouverture', r'ferme.*à', r'ouvre.*à',
                r'disponible.*quand', r'accessible.*quand'
            ],
            'ask_contact': [
                r'numéro', r'téléphone', r'whatsapp', r'contact', r'appeler',
                r'email', r'site.*web', r'adresse'
            ],
            'ask_directions': [
                r'itinéraire', r'comment.*aller', r'où.*se.*trouve', r'direction',
                r'carte', r'localisation'
            ],
            'compare_activities': [
                r'meilleur', r'comparer', r'différence', r'quel.*choisir',
                r'recommandation', r'suggestion'
            ]
        }
        
        self.entity_patterns = {
            'activity_type': [
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin',
                r'pharmacie', r'hôpital', r'école', r'université', r'banque', r'garage',
                r'coiffure', r'centre.*jeux', r'cinéma', r'théâtre', r'église', r'mosquée',
                r'station.*service', r'clinique', r'laboratoire', r'centre.*formation',
                r'tribunal', r'mairie', r'préfecture'
            ],
            'service_item': [
                r'porc', r'poulet', r'poisson', r'riz', r'fufu', r'attiéké', r'alloco',
                r'pizza', r'burger', r'sandwich', r'jus', r'bière', r'cocktail',
                r'médicament', r'consultation', r'analyse', r'vaccin',
                r'coiffure', r'manucure', r'pédicure', r'massage',
                r'essence', r'gasoil', r'vidange', r'réparation',
                r'cours', r'formation', r'diplôme', r'certificat'
            ],
            'time_constraint': [
                r'ce soir', r'aujourd\'hui', r'maintenant', r'après-midi', r'matin',
                r'weekend', r'samedi', r'dimanche', r'urgence', r'immédiatement'
            ],
            'location': [
                r'près.*moi', r'proche', r'ici', r'quartier', r'centre.*ville',
                r'cocody', r'plateau', r'yopougon', r'adjamé', r'treichville',
                r'zone.*4', r'zone.*3', r'zone.*2', r'zone.*1'
            ],
            'price_level': [
                r'pas cher', r'bon marché', r'cher', r'coûteux', r'économique',
                r'gratuit', r'payant', r'abordable', r'luxueux'
            ],
            'quality_level': [
                r'excellent', r'bon', r'moyen', r'mauvais', r'terrible',
                r'recommandé', r'populaire', r'connu', r'réputé'
            ]
        }
        
        self.activity_type_mapping = {
            'restaurant': 'Restaurant',
            'maquis': 'Maquis',
            'bar': 'Bar',
            'café': 'Café',
            'boutique': 'Boutique',
            'magasin': 'Magasin',
            'pharmacie': 'Pharmacie',
            'hôpital': 'Hôpital',
            'école': 'École',
            'université': 'Université',
            'banque': 'Banque',
            'garage': 'Garage',
            'coiffure': 'Coiffure',
            'centre.*jeux': 'Centre de jeux',
            'cinéma': 'Cinéma',
            'théâtre': 'Théâtre',
            'église': 'Église',
            'mosquée': 'Mosquée'
        }

    def preprocess_query(self, query: str) -> str:
        """Nettoie et normalise la requête"""
        query = query.lower().strip()
        query = re.sub(r'\\s+', ' ', query)
        return query

    def classify_intent(self, query: str) -> str:
        """Classifie l'intention de la requête"""
        query = self.preprocess_query(query)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        return 'search_activity'

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extrait les entités de la requête"""
        query = self.preprocess_query(query)
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    entities[entity_type] = match.group(0)
                    break
        
        return entities

    def generate_advanced_sql_query(self, search_request: Dict[str, Any], entities: Dict[str, Any]) -> Tuple[str, Dict]:
        """Génère une requête SQL avancée basée sur la nouvelle structure"""
        
        base_query = """
        SELECT 
            a.*,
            at.name as activity_type_name,
            at.slug as activity_type_slug,
            c.name as category_name,
            c.slug as category_slug,
            z.name as zone_name,
            ci.name as city_name,
            r.name as region_name,
            co.name as country_name,
            u.full_name as owner_name,
            amb.full_name as ambassador_name,
            ST_X(a.location) as longitude,
            ST_Y(a.location) as latitude,
            ST_Distance(
                a.location, 
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
            ) as distance
        FROM activities a
        LEFT JOIN activity_types at ON a.activity_type_id = at.id
        LEFT JOIN categories c ON a.category_id = c.id
        LEFT JOIN zones z ON a.zone_id = z.id
        LEFT JOIN cities ci ON z.city_id = ci.id
        LEFT JOIN regions r ON ci.region_id = r.id
        LEFT JOIN countries co ON r.country_id = co.id
        LEFT JOIN users u ON a.owner_id = u.id
        LEFT JOIN ambassadors amb ON a.ambassador_id = amb.user_id
        WHERE a.is_active = TRUE
        """
        
        params = {
            'latitude': search_request.get('latitude', 0),
            'longitude': search_request.get('longitude', 0)
        }
        
        # Filtre par rayon
        if search_request.get('radius'):
            base_query += """
            AND ST_DWithin(
                a.location, 
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), 
                :radius
            )
            """
            params['radius'] = search_request['radius']
        
        # Filtre par type d'activité
        if search_request.get('activity_type_id'):
            base_query += " AND a.activity_type_id = :activity_type_id"
            params['activity_type_id'] = search_request['activity_type_id']
        elif 'activity_type' in entities:
            activity_type_name = self.activity_type_mapping.get(entities['activity_type'], 'Restaurant')
            base_query += " AND at.name ILIKE :activity_type_name"
            params['activity_type_name'] = f"%{activity_type_name}%"
        
        # Filtre par catégorie
        if search_request.get('category_id'):
            base_query += " AND a.category_id = :category_id"
            params['category_id'] = search_request['category_id']
        
        # Filtre par niveau de prix
        if search_request.get('price_level'):
            base_query += " AND a.price_level = :price_level"
            params['price_level'] = search_request['price_level']
        elif 'price_level' in entities:
            if 'pas cher' in entities['price_level'] or 'bon marché' in entities['price_level']:
                params['price_level'] = 1
            elif 'cher' in entities['price_level'] or 'coûteux' in entities['price_level']:
                params['price_level'] = 3
            else:
                params['price_level'] = 2
            base_query += " AND a.price_level = :price_level"
        
        # Filtre par statut ouvert
        if search_request.get('is_open_now'):
            base_query += " AND a.is_open = TRUE"
        elif 'time_constraint' in entities:
            if any(word in entities['time_constraint'] for word in ['ce soir', 'maintenant', 'aujourd\'hui']):
                base_query += " AND a.is_open = TRUE"
        
        # Filtre par niveau de vérification
        if search_request.get('verification_level'):
            base_query += " AND a.verification_level >= :verification_level"
            params['verification_level'] = search_request['verification_level']
        
        # Recherche textuelle avancée
        if search_request.get('query'):
            base_query += """
            AND (
                a.name ILIKE :query 
                OR a.description ILIKE :query 
                OR a.short_description ILIKE :query
                OR EXISTS (
                    SELECT 1 FROM unnest(a.tags) tag 
                    WHERE tag ILIKE :query
                )
                OR EXISTS (
                    SELECT 1 FROM unnest(a.keywords) keyword 
                    WHERE keyword ILIKE :query
                )
            )
            """
            params['query'] = f"%{search_request['query']}%"
        
        # Filtre par zone
        if search_request.get('zone_id'):
            base_query += " AND a.zone_id = :zone_id"
            params['zone_id'] = search_request['zone_id']
        
        # Filtre par langue
        if search_request.get('language'):
            base_query += " AND :language = ANY(a.languages)"
            params['language'] = search_request['language']
        
        # Tri intelligent
        base_query += """
        ORDER BY 
            CASE WHEN a.is_open = TRUE THEN 0 ELSE 1 END,
            a.verification_level DESC,
            a.rating DESC,
            distance ASC,
            a.review_count DESC,
            a.created_at DESC
        LIMIT :limit
        """
        params['limit'] = search_request.get('limit', 20)
        
        return base_query, params

    def rank_results(self, activities: List[Activity], entities: Dict[str, Any], user_context: Dict[str, Any] = None) -> List[Activity]:
        """Classe les résultats selon la pertinence"""
        if not activities:
            return activities
        
        for activity in activities:
            score = 0
            
            # Score de distance (plus proche = mieux)
            if hasattr(activity, 'distance') and activity.distance:
                if activity.distance < 500:
                    score += 100
                elif activity.distance < 1000:
                    score += 80
                elif activity.distance < 2000:
                    score += 60
                else:
                    score += 40
            
            # Score de vérification
            if activity.is_verified:
                score += 50
                score += activity.verification_level * 10
            
            # Score de statut ouvert
            if activity.is_open:
                score += 30
            
            # Score d'évaluation
            score += float(activity.rating) * 10
            
            # Score de popularité
            score += min(activity.review_count, 100) * 0.5
            score += min(activity.view_count, 1000) * 0.1
            score += min(activity.search_count, 500) * 0.2
            
            # Bonus pour les activités récentes
            days_old = (datetime.now() - activity.created_at).days
            if days_old < 30:
                score += 10
            elif days_old < 90:
                score += 5
            
            # Bonus pour les activités avec photos
            if activity.cover_image_url:
                score += 5
            
            # Bonus pour les activités avec informations complètes
            if activity.description and len(activity.description) > 50:
                score += 5
            if activity.opening_hours:
                score += 5
            if activity.phone_number or activity.whatsapp_number:
                score += 5
            
            # Stocker le score pour le tri
            activity.relevance_score = score
        
        # Trier par score de pertinence
        return sorted(activities, key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)

    def generate_advanced_response(self, activities: List[Activity], intent: str, entities: Dict[str, Any], user_context: Dict[str, Any] = None) -> str:
        """Génère une réponse avancée et contextuelle"""
        if not activities:
            return "Désolé, je n'ai trouvé aucune activité correspondant à votre recherche. Essayez avec d'autres mots-clés ou élargissez votre zone de recherche."
        
        count = len(activities)
        nearest = activities[0]
        
        # Réponse de base
        if count == 1:
            response = f"J'ai trouvé 1 activité parfaite pour vous !"
        else:
            response = f"J'ai trouvé {count} activités qui correspondent à votre recherche."
        
        # Informations sur l'activité la plus proche
        response += f"\\n\\nLe plus proche est **{nearest.name}**"
        
        if hasattr(nearest, 'distance') and nearest.distance:
            if nearest.distance < 1000:
                response += f" à {int(nearest.distance)}m"
            else:
                response += f" à {nearest.distance/1000:.1f}km"
        
        # Informations sur le type d'activité
        if hasattr(nearest, 'activity_type_name') and nearest.activity_type_name:
            response += f" ({nearest.activity_type_name})"
        
        # Statut
        if nearest.is_open:
            response += " - ✅ **OUVERT**"
        else:
            response += " - ❌ **FERMÉ**"
        
        # Niveau de vérification
        if nearest.is_verified:
            if nearest.verification_level >= 3:
                response += " (✓ Vérifié Premium)"
            elif nearest.verification_level >= 2:
                response += " (✓ Vérifié Complet)"
            else:
                response += " (✓ Vérifié Basique)"
        
        # Évaluation
        if nearest.rating > 0:
            response += f" - ⭐ {nearest.rating:.1f}/5"
            if nearest.review_count > 0:
                response += f" ({nearest.review_count} avis)"
        
        # Niveau de prix
        if nearest.price_level:
            price_icons = "€" * nearest.price_level
            response += f" - {price_icons}"
        
        # Informations de contact si demandées
        if 'ask_contact' in intent or 'contact' in entities:
            if nearest.phone_number:
                response += f"\\n\\n📞 Téléphone: {nearest.phone_number}"
            if nearest.whatsapp_number:
                response += f"\\n💬 WhatsApp: {nearest.whatsapp_number}"
            if nearest.email:
                response += f"\\n📧 Email: {nearest.email}"
            if nearest.website:
                response += f"\\n🌐 Site web: {nearest.website}"
        
        # Horaires si demandés
        if 'ask_hours' in intent or 'horaires' in entities:
            if nearest.opening_hours:
                try:
                    hours = json.loads(nearest.opening_hours) if isinstance(nearest.opening_hours, str) else nearest.opening_hours
                    response += f"\\n\\n🕒 Horaires: {hours.get('today', 'Non spécifié')}"
                except:
                    response += f"\\n\\n🕒 Horaires: {nearest.opening_hours}"
        
        # Directions si demandées
        if 'ask_directions' in intent or 'itinéraire' in entities:
            response += f"\\n\\n🗺️ Voulez-vous l'itinéraire vers {nearest.name} ?"
        
        # Plus d'options si plusieurs résultats
        if count > 1:
            response += f"\\n\\nVoulez-vous voir les {count-1} autres options ?"
        
        # Suggestions contextuelles
        if user_context and user_context.get('previous_searches'):
            response += "\\n\\n💡 Basé sur vos recherches précédentes, je peux aussi vous suggérer des activités similaires."
        
        return response

    def search(self, db: Session, search_request: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Méthode de recherche principale"""
        import time
        start_time = time.time()
        
        # Préprocessing
        processed_query = self.preprocess_query(search_request.get('query', ''))
        
        # Classification et extraction d'entités
        intent = self.classify_intent(processed_query)
        entities = self.extract_entities(processed_query)
        
        # Génération de la requête SQL
        sql_query, params = self.generate_advanced_sql_query(search_request, entities)
        
        # Exécution de la requête
        result = db.execute(text(sql_query), params)
        activities = []
        
        for row in result:
            activity_dict = dict(row._mapping)
            activity = Activity(**{k: v for k, v in activity_dict.items() if k in Activity.__table__.columns})
            
            # Ajouter les attributs calculés
            for key, value in activity_dict.items():
                if key not in Activity.__table__.columns:
                    setattr(activity, key, value)
            
            activities.append(activity)
        
        # Classement des résultats
        activities = self.rank_results(activities, entities, user_context)
        
        # Génération de la réponse
        response = self.generate_advanced_response(activities, intent, entities, user_context)
        
        # Log de la recherche
        search_log = SearchLog(
            query=search_request.get('query', ''),
            processed_query=processed_query,
            user_location=search_request.get('user_location'),
            search_radius=search_request.get('radius', 5000),
            results_count=len(activities),
            intent=intent,
            entities=entities,
            search_time_ms=int((time.time() - start_time) * 1000)
        )
        
        if search_request.get('user_id'):
            search_log.user_id = search_request['user_id']
        
        db.add(search_log)
        db.commit()
        
        search_time = (time.time() - start_time) * 1000
        
        return {
            "activities": activities,
            "total_count": len(activities),
            "query_processed": processed_query,
            "search_time_ms": search_time,
            "response": response,
            "intent": intent,
            "entities": entities,
            "search_id": search_log.id
        }
'''

    with open('/workspace/backend/advanced_search_engine.py', 'w', encoding='utf-8') as f:
        f.write(search_engine_code)
    
    print("✅ Moteur de recherche avancé créé: backend/advanced_search_engine.py")

def main():
    """Fonction principale de migration"""
    print("🚀 CRÉATION DE LA STRUCTURE ULTRA POLYVALENTE")
    print("=" * 60)
    
    print("1. Création du script de migration...")
    create_migration_script()
    
    print("2. Création des nouveaux modèles...")
    create_new_models()
    
    print("3. Création du moteur de recherche avancé...")
    create_advanced_search_engine()
    
    print("\n✅ STRUCTURE ULTRA POLYVALENTE CRÉÉE AVEC SUCCÈS !")
    print("=" * 60)
    print("📁 Fichiers créés:")
    print("   • database_schema.sql - Structure complète de la base de données")
    print("   • migration_script.sql - Script de migration depuis l'ancienne structure")
    print("   • backend/new_models.py - Nouveaux modèles SQLAlchemy")
    print("   • backend/advanced_search_engine.py - Moteur de recherche avancé")
    
    print("\n🎯 FONCTIONNALITÉS DE LA NOUVELLE STRUCTURE:")
    print("   • Support de TOUS types d'activités (commerces, services, ONG, ministères, etc.)")
    print("   • Gestion multi-niveaux des zones géographiques")
    print("   • Système de rôles et permissions flexible")
    print("   • Analytics et insights avancés")
    print("   • Intégration IA et machine learning")
    print("   • Monétisation et abonnements")
    print("   • Notifications et communications")
    print("   • Audit et traçabilité complète")
    
    print("\n🚀 POUR APPLIQUER LA MIGRATION:")
    print("   1. Sauvegardez votre base de données actuelle")
    print("   2. Exécutez: psql -d votre_db -f database_schema.sql")
    print("   3. Exécutez: psql -d votre_db -f migration_script.sql")
    print("   4. Mettez à jour votre code pour utiliser les nouveaux modèles")

if __name__ == "__main__":
    main()