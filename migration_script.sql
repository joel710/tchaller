
-- =====================================================
-- MIGRATION VERS LA NOUVELLE STRUCTURE ULTRA POLYVALENTE
-- =====================================================

-- 1. Créer la nouvelle structure
\i database_schema.sql

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
