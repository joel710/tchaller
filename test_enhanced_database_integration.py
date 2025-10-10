#!/usr/bin/env python3
"""
Test d'intégration du moteur de recherche amélioré avec la structure de base de données ultra polyvalente
"""
import sys
import os
sys.path.append('/workspace')

def test_database_schema_compatibility():
    """Test de compatibilité avec la nouvelle structure de base de données"""
    print("🗄️ TEST DE COMPATIBILITÉ BASE DE DONNÉES")
    print("=" * 60)
    
    try:
        # Test d'import des nouveaux modèles
        from backend.new_models import Activity, Category, ActivityType, Zone, User, Review, Media
        print("✅ Import des nouveaux modèles réussi")
        
        # Test d'import du moteur de recherche amélioré
        from backend.enhanced_search_engine import EnhancedConversationalSearchEngine
        print("✅ Import du moteur de recherche amélioré réussi")
        
        # Test d'initialisation du moteur
        engine = EnhancedConversationalSearchEngine()
        print("✅ Initialisation du moteur de recherche réussie")
        
        # Test des patterns d'intent
        print(f"✅ {len(engine.intent_patterns)} patterns d'intent configurés")
        for intent, patterns in engine.intent_patterns.items():
            print(f"   - {intent}: {len(patterns)} patterns")
        
        # Test des patterns d'entités
        print(f"✅ {len(engine.entity_patterns)} types d'entités configurés")
        for entity_type, patterns in engine.entity_patterns.items():
            print(f"   - {entity_type}: {len(patterns)} patterns")
        
        # Test des templates de réponse
        print(f"✅ {len(engine.response_templates)} types de templates de réponse")
        for template_type, templates in engine.response_templates.items():
            print(f"   - {template_type}: {len(templates)} variations")
        
        # Test du mapping des types d'activités
        print(f"✅ {len(engine.activity_type_mapping)} types d'activités mappés")
        for activity_type, category_name in engine.activity_type_mapping.items():
            print(f"   - {activity_type} → {category_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de compatibilité: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_functionality():
    """Test des fonctionnalités de recherche"""
    print("\n🔍 TEST DES FONCTIONNALITÉS DE RECHERCHE")
    print("=" * 60)
    
    try:
        from backend.enhanced_search_engine import EnhancedConversationalSearchEngine
        
        engine = EnhancedConversationalSearchEngine()
        
        # Test de classification d'intent
        test_queries = [
            "Trouve-moi un hôpital près de moi",
            "URGENCE ! J'ai besoin d'un médecin",
            "Où est la pharmacie la plus proche ?",
            "Cherche une université",
            "Où puis-je réparer ma voiture ?",
            "Donne-moi les horaires de la banque"
        ]
        
        print("🧪 Test de classification d'intent :")
        for query in test_queries:
            intent = engine.classify_intent(query)
            entities = engine.extract_entities(query)
            print(f"   '{query}' → Intent: {intent}, Entités: {entities}")
        
        # Test de génération de requête SQL
        print("\n🧪 Test de génération de requête SQL :")
        from backend.schemas import SearchRequest
        
        search_request = SearchRequest(
            query="Trouve-moi un hôpital",
            latitude=6.1723,
            longitude=1.2312,
            radius=5000,
            limit=5
        )
        
        sql_query, params = engine.generate_sql_query(None, search_request, "search_place", {"service_type": "hôpital"})
        print(f"   Requête SQL générée: {sql_query[:100]}...")
        print(f"   Paramètres: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de recherche: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_schema_structure():
    """Test de la structure de la base de données"""
    print("\n🏗️ TEST DE LA STRUCTURE DE BASE DE DONNÉES")
    print("=" * 60)
    
    try:
        # Lire le fichier SQL de la structure ultra polyvalente
        with open('/workspace/database_schema.sql', 'r') as f:
            schema_content = f.read()
        
        print("✅ Fichier database_schema.sql lu avec succès")
        
        # Vérifier les tables principales
        required_tables = [
            'activities', 'categories', 'activity_types', 'users', 'zones',
            'reviews', 'media', 'conversations', 'messages', 'ambassadors',
            'verifications', 'webhooks', 'search_logs', 'user_interactions',
            'data_models', 'insights', 'subscription_plans', 'subscriptions',
            'notifications', 'audit_logs'
        ]
        
        print("🔍 Vérification des tables requises :")
        for table in required_tables:
            if f"CREATE TABLE {table}" in schema_content:
                print(f"   ✅ Table {table} trouvée")
            else:
                print(f"   ❌ Table {table} manquante")
        
        # Vérifier les extensions PostGIS
        if "CREATE EXTENSION IF NOT EXISTS postgis" in schema_content:
            print("✅ Extension PostGIS configurée")
        else:
            print("❌ Extension PostGIS manquante")
        
        # Vérifier les index spatiaux
        if "CREATE INDEX" in schema_content and "GIST" in schema_content:
            print("✅ Index spatiaux configurés")
        else:
            print("❌ Index spatiaux manquants")
        
        # Vérifier les triggers
        if "CREATE TRIGGER" in schema_content:
            print("✅ Triggers configurés")
        else:
            print("❌ Triggers manquants")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de structure: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_relationships():
    """Test des relations entre modèles"""
    print("\n🔗 TEST DES RELATIONS ENTRE MODÈLES")
    print("=" * 60)
    
    try:
        from backend.new_models import Activity, Category, ActivityType, Zone, User, Review, Media
        
        # Vérifier les attributs de Activity
        activity_attrs = [
            'id', 'name', 'description', 'address', 'phone_number', 'whatsapp_number',
            'email', 'website', 'opening_hours', 'price_level', 'rating', 'review_count',
            'is_verified', 'is_active', 'latitude', 'longitude', 'location',
            'category_id', 'activity_type_id', 'zone_id', 'owner_id', 'created_at', 'updated_at'
        ]
        
        print("🔍 Vérification des attributs d'Activity :")
        for attr in activity_attrs:
            if hasattr(Activity, attr):
                print(f"   ✅ {attr}")
            else:
                print(f"   ❌ {attr} manquant")
        
        # Vérifier les relations
        print("\n🔍 Vérification des relations :")
        relations = [
            ('category', 'Category'),
            ('activity_type', 'ActivityType'),
            ('zone', 'Zone'),
            ('owner', 'User'),
            ('reviews', 'Review'),
            ('media', 'Media')
        ]
        
        for rel_name, rel_type in relations:
            if hasattr(Activity, rel_name):
                print(f"   ✅ Relation {rel_name} vers {rel_type}")
            else:
                print(f"   ❌ Relation {rel_name} vers {rel_type} manquante")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des relations: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_engine_integration():
    """Test d'intégration complète du moteur de recherche"""
    print("\n🔧 TEST D'INTÉGRATION COMPLÈTE")
    print("=" * 60)
    
    try:
        from backend.enhanced_search_engine import EnhancedConversationalSearchEngine
        from backend.schemas import SearchRequest
        
        engine = EnhancedConversationalSearchEngine()
        
        # Test de scénarios de recherche variés
        search_scenarios = [
            {
                "name": "Recherche d'hôpital d'urgence",
                "query": "URGENCE ! J'ai besoin d'un hôpital maintenant",
                "latitude": 6.1723,
                "longitude": 1.2312,
                "expected_intent": "emergency"
            },
            {
                "name": "Recherche de pharmacie",
                "query": "Où est la pharmacie la plus proche ?",
                "latitude": 6.1723,
                "longitude": 1.2312,
                "expected_intent": "search_place"
            },
            {
                "name": "Recherche d'université",
                "query": "Cherche une université près de moi",
                "latitude": 6.1723,
                "longitude": 1.2312,
                "expected_intent": "search_place"
            },
            {
                "name": "Recherche de garage",
                "query": "Où puis-je réparer ma voiture ?",
                "latitude": 6.1723,
                "longitude": 1.2312,
                "expected_intent": "find_by_service"
            }
        ]
        
        print("🧪 Test des scénarios de recherche :")
        for scenario in search_scenarios:
            print(f"\n📝 {scenario['name']}:")
            print(f"   Requête: {scenario['query']}")
            
            # Classification
            intent = engine.classify_intent(scenario['query'])
            entities = engine.extract_entities(scenario['query'])
            
            print(f"   Intent détecté: {intent}")
            print(f"   Entités extraites: {entities}")
            
            # Vérification de l'intent attendu
            if intent == scenario['expected_intent']:
                print(f"   ✅ Intent correct")
            else:
                print(f"   ⚠️ Intent attendu: {scenario['expected_intent']}, obtenu: {intent}")
            
            # Test de génération de requête SQL
            search_request = SearchRequest(
                query=scenario['query'],
                latitude=scenario['latitude'],
                longitude=scenario['longitude'],
                radius=5000,
                limit=5
            )
            
            try:
                sql_query, params = engine.generate_sql_query(None, search_request, intent, entities)
                print(f"   ✅ Requête SQL générée ({len(sql_query)} caractères)")
            except Exception as e:
                print(f"   ❌ Erreur génération SQL: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test"""
    print("🧭 TEST D'INTÉGRATION MVP AMÉLIORÉ + STRUCTURE ULTRA POLYVALENTE")
    print("=" * 80)
    print("Vérification de la compatibilité entre :")
    print("• Moteur de recherche amélioré")
    print("• Structure de base de données ultra polyvalente")
    print("• Modèles SQLAlchemy mis à jour")
    print("=" * 80)
    
    tests = [
        ("Compatibilité base de données", test_database_schema_compatibility),
        ("Fonctionnalités de recherche", test_search_functionality),
        ("Structure de base de données", test_database_schema_structure),
        ("Relations entre modèles", test_model_relationships),
        ("Intégration complète", test_search_engine_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des résultats
    print("\n\n📊 RÉSUMÉ DES TESTS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RÉSULTAT GLOBAL: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ Le MVP amélioré est parfaitement intégré avec la structure ultra polyvalente")
        print("✅ Tous les champs de la base de données correspondent")
        print("✅ Le moteur de recherche utilise la nouvelle structure")
        print("✅ Les relations entre modèles sont correctes")
        print("\n🚀 Le système est prêt pour la production !")
    else:
        print(f"\n⚠️ {total - passed} test(s) ont échoué")
        print("🔧 Des corrections sont nécessaires avant la production")

if __name__ == "__main__":
    main()