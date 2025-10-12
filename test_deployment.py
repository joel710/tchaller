#!/usr/bin/env python3
"""
Script de test pour vérifier que l'application est prête pour le déploiement
"""

import sys
import os
import subprocess
import requests
import time
from pathlib import Path

def test_imports():
    """Teste que tous les imports fonctionnent"""
    print("🔍 Test des imports...")
    
    try:
        # Test des imports principaux
        from backend.config import settings
        from backend.database.connection import create_tables, get_db
        from backend.database.models import Activity, User, Category
        from backend.schemas.activities import ActivityResponse
        from backend.services.enhanced_search_engine import EnhancedConversationalSearchEngine
        from backend.main import app
        
        print("✅ Tous les imports fonctionnent correctement")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_database_connection():
    """Teste la connexion à la base de données"""
    print("🔍 Test de la connexion à la base de données...")
    
    try:
        from backend.database.connection import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion à la base de données réussie")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def test_cors_configuration():
    """Teste la configuration CORS"""
    print("🔍 Test de la configuration CORS...")
    
    try:
        from backend.config import settings
        
        assert settings.cors_origins == ["*"], f"CORS origins incorrect: {settings.cors_origins}"
        assert settings.cors_allow_methods == ["*"], f"CORS methods incorrect: {settings.cors_allow_methods}"
        assert settings.cors_allow_headers == ["*"], f"CORS headers incorrect: {settings.cors_allow_headers}"
        assert settings.cors_allow_credentials == True, f"CORS credentials incorrect: {settings.cors_allow_credentials}"
        
        print("✅ Configuration CORS correcte")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration CORS: {e}")
        return False

def test_search_engine():
    """Teste le moteur de recherche"""
    print("🔍 Test du moteur de recherche...")
    
    try:
        from backend.services.enhanced_search_engine import EnhancedConversationalSearchEngine
        
        engine = EnhancedConversationalSearchEngine()
        
        # Test de classification d'intent
        test_queries = [
            "Je cherche un restaurant",
            "Où est l'hôpital le plus proche ?",
            "J'ai besoin d'un garage",
            "Y a-t-il une pharmacie ouverte ?"
        ]
        
        for query in test_queries:
            intent = engine.classify_intent(query)
            entities = engine.extract_entities(query)
            print(f"  Query: '{query}' -> Intent: {intent}, Entities: {entities}")
        
        print("✅ Moteur de recherche fonctionnel")
        return True
    except Exception as e:
        print(f"❌ Erreur du moteur de recherche: {e}")
        return False

def test_requirements():
    """Teste que tous les requirements sont installés"""
    print("🔍 Test des requirements...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        missing_packages = []
        for req in requirements:
            package = req.split('==')[0]
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Packages manquants: {missing_packages}")
            return False
        else:
            print("✅ Tous les requirements sont installés")
            return True
    except Exception as e:
        print(f"❌ Erreur lors du test des requirements: {e}")
        return False

def test_file_structure():
    """Teste que la structure des fichiers est correcte"""
    print("🔍 Test de la structure des fichiers...")
    
    required_files = [
        'backend/main.py',
        'backend/config.py',
        'backend/database/connection.py',
        'backend/database/models.py',
        'backend/schemas/__init__.py',
        'backend/services/__init__.py',
        'backend/api/__init__.py',
        'requirements.txt',
        'Procfile',
        'render.yaml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        return False
    else:
        print("✅ Structure des fichiers correcte")
        return True

def main():
    """Fonction principale de test"""
    print("🚀 Test de déploiement Tcha-llé Backend")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_requirements,
        test_imports,
        test_database_connection,
        test_cors_configuration,
        test_search_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Résultats: {passed}/{total} tests passés")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le backend est prêt pour le déploiement.")
        return True
    else:
        print("❌ Certains tests ont échoué. Veuillez corriger les erreurs avant le déploiement.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)