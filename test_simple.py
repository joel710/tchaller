#!/usr/bin/env python3
"""
Test simple de l'API Tcha-llé
"""
import sys
import os
sys.path.append('/workspace')

def test_imports():
    """Test des imports"""
    try:
        print("🔍 Test des imports...")
        
        # Test import des modules de base
        from backend.database import create_db_and_tables, Base, engine
        print("✅ Database module: OK")
        
        from backend.schemas import User, Merchant, SearchRequest
        print("✅ Schemas module: OK")
        
        from backend.auth import generate_otp, verify_otp
        print("✅ Auth module: OK")
        
        from backend.search_engine import ConversationalSearchEngine
        print("✅ Search engine module: OK")
        
        from backend.routers import auth, merchants, webhook, categories
        print("✅ Routers modules: OK")
        
        from backend.main import app
        print("✅ Main app: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_database_connection():
    """Test de connexion à la base de données"""
    try:
        print("\n🔍 Test de connexion à la base de données...")
        
        from backend.database import engine
        from sqlalchemy import text
        
        # Test de connexion simple
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion à la base de données: OK")
            return True
            
    except Exception as e:
        print(f"❌ Erreur de connexion DB: {e}")
        return False

def test_create_tables():
    """Test de création des tables"""
    try:
        print("\n🔍 Test de création des tables...")
        
        from backend.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Tables créées: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de création des tables: {e}")
        return False

def test_seed_data():
    """Test d'ajout des données de test"""
    try:
        print("\n🔍 Test d'ajout des données de test...")
        
        from backend.seed_data import create_sample_data
        create_sample_data()
        print("✅ Données de test ajoutées: OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'ajout des données: {e}")
        return False

def test_search_engine():
    """Test du moteur de recherche"""
    try:
        print("\n🔍 Test du moteur de recherche...")
        
        from backend.search_engine import ConversationalSearchEngine
        from backend.schemas import SearchRequest
        
        engine = ConversationalSearchEngine()
        
        # Test de classification d'intent
        intent = engine.classify_intent("Trouve-moi un endroit où je peux manger du porc ce soir près de moi")
        print(f"✅ Classification d'intent: {intent}")
        
        # Test d'extraction d'entités
        entities = engine.extract_entities("Trouve-moi un endroit où je peux manger du porc ce soir près de moi")
        print(f"✅ Extraction d'entités: {entities}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur du moteur de recherche: {e}")
        return False

def main():
    print("🧪 Test de l'API Tcha-llé")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database_connection,
        test_create_tables,
        test_seed_data,
        test_search_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'API est prête.")
        print("\n🚀 Pour démarrer le serveur:")
        print("   python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        print("\n🌐 Accès:")
        print("   - API: http://localhost:8000")
        print("   - Docs: http://localhost:8000/docs")
        print("   - Frontend: http://localhost:8000/static/index.html")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les logs ci-dessus.")

if __name__ == "__main__":
    main()