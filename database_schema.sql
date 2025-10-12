DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- =====================================================
-- TCHA-LLÉ - STRUCTURE DE BASE DE DONNÉES ULTRA POLYVALENTE
-- =====================================================
-- Version: 2.0.0
-- Description: Structure évolutive pour toutes activités locales
-- Auteur: Tcha-llé Team
-- Date: 2025
-- =====================================================

DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Extension PostGIS pour la géolocalisation
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- =====================================================
-- 1. GESTION DES UTILISATEURS ET RÔLES
-- =====================================================

-- Table des utilisateurs
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    avatar_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_location GEOMETRY(POINT, 4326),
    preferred_language VARCHAR(5) DEFAULT 'fr',
    timezone VARCHAR(50) DEFAULT 'Africa/Abidjan',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des rôles et permissions
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table de liaison utilisateurs-rôles
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, role_id)
);

-- =====================================================
-- 2. GESTION DES ZONES ET GÉOLOCALISATION
-- =====================================================

-- Table des pays
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(3) UNIQUE NOT NULL,
    currency VARCHAR(3),
    timezone VARCHAR(50),
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des régions/provinces
CREATE TABLE regions (
    id SERIAL PRIMARY KEY,
    country_id INTEGER REFERENCES countries(id),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10),
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des villes
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    region_id INTEGER REFERENCES regions(id),
    name VARCHAR(100) NOT NULL,
    population INTEGER,
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des quartiers/zones
CREATE TABLE zones (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) DEFAULT 'neighborhood', -- neighborhood, district, sector, etc.
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    population INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des zones de service (zones d'influence des activités)
CREATE TABLE service_zones (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER, -- Référence générique vers n'importe quelle activité
    activity_type VARCHAR(50), -- Type d'activité (merchant, service, etc.)
    zone_id INTEGER REFERENCES zones(id),
    radius_meters INTEGER DEFAULT 5000,
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 3. GESTION DES CATÉGORIES ET TYPES D'ACTIVITÉS
-- =====================================================

-- Table des catégories principales
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    color VARCHAR(7), -- Hex color
    parent_id INTEGER REFERENCES categories(id),
    level INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des types d'activités
CREATE TABLE activity_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES categories(id),
    requires_verification BOOLEAN DEFAULT FALSE,
    allows_online_booking BOOLEAN DEFAULT FALSE,
    allows_delivery BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 4. GESTION DES ACTIVITÉS (POLYVALENTE)
-- =====================================================

-- Table principale des activités (remplace merchants)
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    
    -- Classification
    activity_type_id INTEGER REFERENCES activity_types(id),
    category_id INTEGER REFERENCES categories(id),
    
    -- Localisation
    address TEXT,
    location GEOMETRY(POINT, 4326) NOT NULL,
    zone_id INTEGER REFERENCES zones(id),
    
    -- Contact
    phone_number VARCHAR(20),
    whatsapp_number VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(500),
    
    -- Statut et vérification
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    is_open BOOLEAN DEFAULT TRUE,
    verification_level INTEGER DEFAULT 0, -- 0=non vérifié, 1=basique, 2=complet, 3=premium
    
    -- Propriétaire/Gestionnaire
    owner_id INTEGER REFERENCES users(id),
    manager_id INTEGER REFERENCES users(id),
    
    -- Ambassadeur qui a enregistré
    ambassador_id INTEGER REFERENCES users(id),
    
    -- Informations commerciales
    price_level INTEGER DEFAULT 1, -- 1-5 échelle de prix
    accepts_cash BOOLEAN DEFAULT TRUE,
    accepts_card BOOLEAN DEFAULT FALSE,
    accepts_mobile_money BOOLEAN DEFAULT FALSE,
    
    -- Horaires (JSON flexible)
    opening_hours JSONB DEFAULT '{}',
    special_hours JSONB DEFAULT '{}', -- Jours fériés, événements spéciaux
    
    -- Évaluation et popularité
    rating DECIMAL(3,2) DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    search_count INTEGER DEFAULT 0,
    
    -- Médias
    cover_image_url TEXT,
    logo_url TEXT,
    
    -- Métadonnées
    tags TEXT[], -- Tags libres
    keywords TEXT[], -- Mots-clés pour la recherche
    languages VARCHAR(10)[], -- Langues parlées
    
    -- Données personnalisées (JSON flexible)
    custom_data JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index spatial pour les performances
CREATE INDEX idx_activities_location ON activities USING GIST (location);
CREATE INDEX idx_activities_zone ON activities (zone_id);
CREATE INDEX idx_activities_type ON activities (activity_type_id);
CREATE INDEX idx_activities_category ON activities (category_id);
CREATE INDEX idx_activities_owner ON activities (owner_id);
CREATE INDEX idx_activities_ambassador ON activities (ambassador_id);
CREATE INDEX idx_activities_active ON activities (is_active, is_open);
CREATE INDEX idx_activities_verified ON activities (is_verified, verification_level);

-- =====================================================
-- 5. GESTION DES MÉDIAS ET PHOTOS
-- =====================================================

-- Table des médias
CREATE TABLE media (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    
    -- Informations du fichier
    file_url TEXT NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- image, video, audio, document
    mime_type VARCHAR(100),
    file_size INTEGER,
    
    -- Métadonnées
    title VARCHAR(255),
    description TEXT,
    alt_text VARCHAR(255),
    
    -- Dimensions (pour images/vidéos)
    width INTEGER,
    height INTEGER,
    duration INTEGER, -- Pour vidéos/audio (en secondes)
    
    -- Classification
    category VARCHAR(50) DEFAULT 'general', -- cover, logo, gallery, menu, etc.
    is_primary BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- Modération
    is_approved BOOLEAN DEFAULT TRUE,
    moderation_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 6. GESTION DES ÉVALUATIONS ET COMMENTAIRES
-- =====================================================

-- Table des évaluations
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    
    -- Évaluation
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    
    -- Catégories d'évaluation (JSON flexible)
    category_ratings JSONB DEFAULT '{}', -- Ex: {"service": 5, "quality": 4, "price": 3}
    
    -- Photos de l'évaluation
    photos TEXT[],
    
    -- Utilité
    helpful_count INTEGER DEFAULT 0,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    
    -- Modération
    is_approved BOOLEAN DEFAULT TRUE,
    is_flagged BOOLEAN DEFAULT FALSE,
    moderation_notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 7. GESTION DES RECHERCHES ET ANALYTICS
-- =====================================================

-- Table des logs de recherche
CREATE TABLE search_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100),
    
    -- Requête
    query TEXT NOT NULL,
    processed_query TEXT,
    language VARCHAR(5) DEFAULT 'fr',
    
    -- Localisation
    user_location GEOMETRY(POINT, 4326),
    search_radius INTEGER DEFAULT 5000,
    
    -- Filtres appliqués
    filters JSONB DEFAULT '{}',
    
    -- Résultats
    results_count INTEGER DEFAULT 0,
    results_ids INTEGER[],
    
    -- Classification IA
    intent VARCHAR(50),
    entities JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),
    
    -- Performance
    search_time_ms INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des interactions utilisateur
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    activity_id INTEGER REFERENCES activities(id),
    interaction_type VARCHAR(50) NOT NULL, -- view, click, call, direction, save, share
    session_id VARCHAR(100),
    
    -- Contexte
    referrer VARCHAR(500),
    user_agent TEXT,
    ip_address INET,
    
    -- Données additionnelles
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 8. GESTION DES CONVERSATIONS ET IA
-- =====================================================

-- Table des conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100),
    
    -- Contexte
    context JSONB DEFAULT '{}',
    user_location GEOMETRY(POINT, 4326),
    
    -- État
    status VARCHAR(20) DEFAULT 'active', -- active, closed, archived
    language VARCHAR(5) DEFAULT 'fr',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    
    -- Contenu
    sender VARCHAR(20) NOT NULL, -- user, bot, system
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text', -- text, image, location, quick_reply
    
    -- IA et traitement
    intent VARCHAR(50),
    entities JSONB DEFAULT '{}',
    confidence_score DECIMAL(3,2),
    processing_time_ms INTEGER,
    
    -- Références
    referenced_activities INTEGER[],
    referenced_categories INTEGER[],
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 9. GESTION DES AMBASSADEURS ET VÉRIFICATIONS
-- =====================================================

-- Table des ambassadeurs
CREATE TABLE ambassadors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) UNIQUE,
    
    -- Informations personnelles
    full_name VARCHAR(255) NOT NULL,
    id_document_type VARCHAR(50),
    id_document_number VARCHAR(100),
    id_document_image_url TEXT,
    
    -- Statut
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, suspended, rejected
    level INTEGER DEFAULT 1, -- 1-5 niveau d'ambassadeur
    points INTEGER DEFAULT 0,
    
    -- Zone de responsabilité
    assigned_zones INTEGER[],
    max_activities INTEGER DEFAULT 10,
    
    -- Performance
    activities_created INTEGER DEFAULT 0,
    activities_verified INTEGER DEFAULT 0,
    verification_accuracy DECIMAL(3,2) DEFAULT 0.0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE
);

-- Table des vérifications
CREATE TABLE verifications (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES activities(id),
    ambassador_id INTEGER REFERENCES ambassadors(id),
    
    -- Type de vérification
    verification_type VARCHAR(50) NOT NULL, -- phone, visit, document, photo
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    
    -- Données de vérification
    verification_data JSONB DEFAULT '{}',
    notes TEXT,
    
    -- Photos de vérification
    photos TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- 10. GESTION DES WEBHOOKS ET INTÉGRATIONS
-- =====================================================

-- Table des webhooks
CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    secret_key VARCHAR(255),
    
    -- Configuration
    events TEXT[] NOT NULL, -- Types d'événements à écouter
    is_active BOOLEAN DEFAULT TRUE,
    retry_count INTEGER DEFAULT 3,
    
    -- Statistiques
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des logs de webhook
CREATE TABLE webhook_logs (
    id SERIAL PRIMARY KEY,
    webhook_id INTEGER REFERENCES webhooks(id),
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    
    -- Statut
    status VARCHAR(20) NOT NULL, -- success, failed, pending
    response_code INTEGER,
    response_body TEXT,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- 11. GESTION DES DONNÉES ET INSIGHTS
-- =====================================================

-- Table des modèles de données
CREATE TABLE data_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    model_type VARCHAR(50) NOT NULL, -- classification, regression, clustering, nlp
    
    -- Configuration
    parameters JSONB DEFAULT '{}',
    training_data JSONB DEFAULT '{}',
    
    -- Performance
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    
    -- Statut
    status VARCHAR(20) DEFAULT 'draft', -- draft, training, active, deprecated
    version VARCHAR(20) DEFAULT '1.0.0',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    trained_at TIMESTAMP WITH TIME ZONE
);

-- Table des insights générés
CREATE TABLE insights (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    insight_type VARCHAR(50) NOT NULL, -- trend, pattern, recommendation, alert
    
    -- Données
    data JSONB NOT NULL,
    visualization_config JSONB DEFAULT '{}',
    
    -- Métadonnées
    source_tables TEXT[],
    filters_applied JSONB DEFAULT '{}',
    confidence_level DECIMAL(3,2),
    
    -- Ciblage
    target_audience VARCHAR(50) DEFAULT 'all', -- all, ambassadors, admins, specific_users
    is_public BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- 12. GESTION DES ABONNEMENTS ET MONÉTISATION
-- =====================================================

-- Table des plans d'abonnement
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Configuration
    price_monthly DECIMAL(10,2),
    price_yearly DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'XOF',
    
    -- Limites
    max_activities INTEGER,
    max_photos_per_activity INTEGER,
    max_ambassadors INTEGER,
    features JSONB DEFAULT '{}',
    
    -- Statut
    is_active BOOLEAN DEFAULT TRUE,
    is_popular BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des abonnements
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    plan_id INTEGER REFERENCES subscription_plans(id),
    
    -- Statut
    status VARCHAR(20) DEFAULT 'active', -- active, cancelled, expired, suspended
    payment_status VARCHAR(20) DEFAULT 'pending', -- pending, paid, failed, refunded
    
    -- Dates
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    
    -- Paiement
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 13. GESTION DES NOTIFICATIONS
-- =====================================================

-- Table des notifications
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    
    -- Contenu
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL, -- info, warning, success, error
    
    -- Ciblage
    target_activity_id INTEGER REFERENCES activities(id),
    target_zone_id INTEGER REFERENCES zones(id),
    
    -- Configuration
    is_read BOOLEAN DEFAULT FALSE,
    is_push_sent BOOLEAN DEFAULT FALSE,
    is_sms_sent BOOLEAN DEFAULT FALSE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    
    -- Données additionnelles
    data JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- =====================================================
-- 14. GESTION DES AUDITS ET LOGS
-- =====================================================

-- Table des audits
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    
    -- Action
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    
    -- Données
    old_values JSONB,
    new_values JSONB,
    
    -- Contexte
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- 15. VUES ET FONCTIONS UTILES
-- =====================================================

-- Vue des activités avec informations complètes
CREATE VIEW activities_full AS
SELECT 
    a.*,
    at.name as activity_type_name,
    at.slug as activity_type_slug,
    c.name as category_name,
    c.slug as category_slug,
    z.name as zone_name,
    z.type as zone_type,
    ci.name as city_name,
    r.name as region_name,
    co.name as country_name,
    u.full_name as owner_name,
    amb.full_name as ambassador_name,
    ST_X(a.location) as longitude,
    ST_Y(a.location) as latitude
FROM activities a
LEFT JOIN activity_types at ON a.activity_type_id = at.id
LEFT JOIN categories c ON a.category_id = c.id
LEFT JOIN zones z ON a.zone_id = z.id
LEFT JOIN cities ci ON z.city_id = ci.id
LEFT JOIN regions r ON ci.region_id = r.id
LEFT JOIN countries co ON r.country_id = co.id
LEFT JOIN users u ON a.owner_id = u.id
LEFT JOIN ambassadors amb ON a.ambassador_id = amb.user_id;

-- Fonction pour calculer la distance entre deux points
CREATE OR REPLACE FUNCTION calculate_distance(
    lat1 DECIMAL, lon1 DECIMAL, 
    lat2 DECIMAL, lon2 DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    RETURN ST_Distance(
        ST_SetSRID(ST_MakePoint(lon1, lat1), 4326),
        ST_SetSRID(ST_MakePoint(lon2, lat2), 4326)
    );
END;
$$ LANGUAGE plpgsql;

-- Fonction pour trouver les activités dans un rayon
CREATE OR REPLACE FUNCTION find_activities_in_radius(
    user_lat DECIMAL,
    user_lon DECIMAL,
    radius_meters INTEGER DEFAULT 5000,
    activity_type_filter VARCHAR DEFAULT NULL,
    category_filter INTEGER DEFAULT NULL
) RETURNS TABLE (
    activity_id INTEGER,
    name VARCHAR,
    distance_meters DECIMAL,
    activity_type VARCHAR,
    category_name VARCHAR,
    rating DECIMAL,
    is_open BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.name,
        ST_Distance(
            a.location,
            ST_SetSRID(ST_MakePoint(user_lon, user_lat), 4326)
        ) as distance,
        at.name as activity_type,
        c.name as category,
        a.rating,
        a.is_open
    FROM activities a
    LEFT JOIN activity_types at ON a.activity_type_id = at.id
    LEFT JOIN categories c ON a.category_id = c.id
    WHERE 
        a.is_active = TRUE
        AND ST_DWithin(
            a.location,
            ST_SetSRID(ST_MakePoint(user_lon, user_lat), 4326),
            radius_meters
        )
        AND (activity_type_filter IS NULL OR at.slug = activity_type_filter)
        AND (category_filter IS NULL OR a.category_id = category_filter)
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 16. DONNÉES INITIALES
-- =====================================================

-- Insertion des rôles de base
INSERT INTO roles (name, description, permissions, is_system) VALUES
('admin', 'Administrateur système', '{"all": true}', true),
('ambassador', 'Ambassadeur', '{"create_activities": true, "verify_activities": true, "manage_own_activities": true}', true),
('moderator', 'Modérateur', '{"moderate_content": true, "verify_activities": true}', true),
('user', 'Utilisateur standard', '{"view_activities": true, "create_reviews": true}', true),
('analyst', 'Analyste de données', '{"view_analytics": true, "export_data": true}', true);

-- Insertion des catégories principales
INSERT INTO categories (name, slug, description, icon, color, level) VALUES
('Commerce & Services', 'commerce-services', 'Tous types de commerces et services', 'store', '#3B82F6', 0),
('Santé & Bien-être', 'sante-bien-etre', 'Services de santé et bien-être', 'heart', '#EF4444', 0),
('Éducation & Formation', 'education-formation', 'Établissements éducatifs et formation', 'graduation-cap', '#10B981', 0),
('Transport & Mobilité', 'transport-mobilite', 'Services de transport et mobilité', 'car', '#F59E0B', 0),
('Loisirs & Culture', 'loisirs-culture', 'Divertissements et activités culturelles', 'music', '#8B5CF6', 0),
('Alimentation & Restauration', 'alimentation-restauration', 'Restaurants, bars, et alimentation', 'utensils', '#F97316', 0),
('Immobilier & Construction', 'immobilier-construction', 'Services immobiliers et construction', 'home', '#06B6D4', 0),
('Technologie & Communication', 'technologie-communication', 'Services technologiques et communication', 'laptop', '#6366F1', 0),
('Finance & Assurance', 'finance-assurance', 'Services financiers et assurance', 'credit-card', '#84CC16', 0),
('Gouvernement & Administration', 'gouvernement-administration', 'Services publics et administration', 'building', '#6B7280', 0);

-- Insertion des types d'activités
INSERT INTO activity_types (name, slug, description, category_id, requires_verification, allows_online_booking) VALUES
-- Commerce & Services
('Boutique', 'boutique', 'Magasin de vêtements et accessoires', 1, false, false),
('Épicerie', 'epicerie', 'Magasin d''alimentation générale', 1, false, false),
('Pharmacie', 'pharmacie', 'Pharmacie et produits de santé', 1, true, true),
('Coiffure', 'coiffure', 'Salon de coiffure et esthétique', 1, false, true),
('Réparation', 'reparation', 'Service de réparation divers', 1, false, false),

-- Santé & Bien-être
('Hôpital', 'hopital', 'Établissement hospitalier', 2, true, true),
('Clinique', 'clinique', 'Clinique médicale', 2, true, true),
('Cabinet médical', 'cabinet-medical', 'Cabinet de médecin', 2, true, true),
('Laboratoire', 'laboratoire', 'Laboratoire d''analyses', 2, true, true),

-- Éducation & Formation
('École', 'ecole', 'Établissement scolaire', 3, true, false),
('Université', 'universite', 'Établissement universitaire', 3, true, false),
('Centre de formation', 'centre-formation', 'Centre de formation professionnelle', 3, false, true),

-- Transport & Mobilité
('Station-service', 'station-service', 'Station-service et carburant', 4, false, false),
('Garage', 'garage', 'Garage automobile', 4, false, true),
('Transport public', 'transport-public', 'Service de transport public', 4, true, false),

-- Loisirs & Culture
('Cinéma', 'cinema', 'Salle de cinéma', 5, false, true),
('Théâtre', 'theatre', 'Salle de théâtre', 5, false, true),
('Centre de jeux', 'centre-jeux', 'Centre de jeux et divertissement', 5, false, false),
('Bibliothèque', 'bibliotheque', 'Bibliothèque publique', 5, true, false),

-- Alimentation & Restauration
('Restaurant', 'restaurant', 'Restaurant et gastronomie', 6, false, true),
('Maquis', 'maquis', 'Maquis et restauration locale', 6, false, false),
('Bar', 'bar', 'Bar et boissons', 6, false, false),
('Café', 'cafe', 'Café et pâtisserie', 6, false, false),

-- Gouvernement & Administration
('Mairie', 'mairie', 'Mairie et administration locale', 10, true, false),
('Préfecture', 'prefecture', 'Préfecture et administration', 10, true, false),
('Tribunal', 'tribunal', 'Tribunal et justice', 10, true, false),
('Banque', 'banque', 'Établissement bancaire', 10, true, true);

-- Insertion des plans d'abonnement
INSERT INTO subscription_plans (name, description, price_monthly, price_yearly, max_activities, features) VALUES
('Gratuit', 'Plan gratuit pour débuter', 0, 0, 5, '{"basic_search": true, "limited_photos": true}'),
('Pro', 'Plan professionnel', 5000, 50000, 50, '{"advanced_search": true, "unlimited_photos": true, "analytics": true, "priority_support": true}'),
('Business', 'Plan entreprise', 15000, 150000, 200, '{"all_features": true, "custom_branding": true, "api_access": true, "dedicated_support": true}'),
('Enterprise', 'Plan entreprise avancé', 50000, 500000, -1, '{"unlimited": true, "white_label": true, "custom_development": true, "24_7_support": true}');

-- =====================================================
-- 17. INDEX ET OPTIMISATIONS
-- =====================================================

-- Index pour les performances de recherche
-- CREATE INDEX idx_activities_search ON activities USING GIN (to_tsvector('french', name || ' ' || COALESCE(description, '') || ' ' || array_to_string(tags, ' ')));
CREATE INDEX idx_activities_rating ON activities (rating DESC, review_count DESC);
CREATE INDEX idx_activities_created ON activities (created_at DESC);
CREATE INDEX idx_activities_updated ON activities (updated_at DESC);

-- Index pour les analytics
CREATE INDEX idx_search_logs_created ON search_logs (created_at DESC);
CREATE INDEX idx_user_interactions_created ON user_interactions (created_at DESC);
CREATE INDEX idx_user_interactions_type ON user_interactions (interaction_type, created_at DESC);

-- Index pour les notifications
CREATE INDEX idx_notifications_user_unread ON notifications (user_id, is_read, created_at DESC);
CREATE INDEX idx_notifications_type ON notifications (notification_type, created_at DESC);

-- =====================================================
-- 18. TRIGGERS ET FONCTIONS AUTOMATIQUES
-- =====================================================

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Application du trigger sur les tables principales
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_activities_updated_at BEFORE UPDATE ON activities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ambassadors_updated_at BEFORE UPDATE ON ambassadors FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Fonction pour calculer automatiquement les statistiques
CREATE OR REPLACE FUNCTION update_activity_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        -- Mettre à jour les statistiques de l'activité
        UPDATE activities 
        SET 
            rating = (
                SELECT COALESCE(AVG(rating), 0) 
                FROM reviews 
                WHERE activity_id = NEW.activity_id AND is_approved = TRUE
            ),
            review_count = (
                SELECT COUNT(*) 
                FROM reviews 
                WHERE activity_id = NEW.activity_id AND is_approved = TRUE
            )
        WHERE id = NEW.activity_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger pour les évaluations
CREATE TRIGGER update_activity_stats_trigger
    AFTER INSERT OR UPDATE OR DELETE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_activity_stats();

-- =====================================================
-- 19. COMMENTAIRES ET DOCUMENTATION
-- =====================================================

COMMENT ON TABLE activities IS 'Table principale des activités - remplace merchants pour plus de polyvalence';
COMMENT ON TABLE activity_types IS 'Types d''activités possibles (restaurant, pharmacie, école, etc.)';
COMMENT ON TABLE zones IS 'Zones géographiques pour la localisation et le ciblage';
COMMENT ON TABLE search_logs IS 'Logs des recherches pour l''amélioration de l''IA';
COMMENT ON TABLE insights IS 'Insights générés par l''IA à partir des données collectées';
COMMENT ON TABLE data_models IS 'Modèles de machine learning entraînés sur les données';

-- =====================================================
-- FIN DE LA STRUCTURE
-- =====================================================

-- Vérification de l'installation
DO $$
BEGIN
    RAISE NOTICE 'Structure de base de données Tcha-llé créée avec succès !';
    RAISE NOTICE 'Tables créées: %', (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public');
    RAISE NOTICE 'Extensions PostGIS installées: %', (SELECT COUNT(*) FROM pg_extension WHERE extname LIKE 'postgis%');
END $$;