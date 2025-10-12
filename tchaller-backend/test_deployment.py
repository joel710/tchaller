#!/usr/bin/env python3
"""
Test de déploiement pour le backend Tcha-llé
"""

import sys
import os

def test_imports():
    """Teste les imports critiques"""
    try:
        from backend.config import settings
        from backend.database.connection import create_tables
        from backend.database.models import Activity, User, Category
        from backend.schemas.activities import ActivityResponse
        from backend.services.simple_search_engine import SimpleConversationalSearchEngine
        from backend.main import app
        print("✅ Tous les imports fonctionnent")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_config():
    """Teste la configuration"""
    try:
        from backend.config import settings
        print(f"✅ Configuration chargée: {settings.app_name}")
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

def main():
    print("🧪 Test de déploiement backend...")
    
    tests = [test_imports, test_config]
    passed = sum(1 for test in tests if test())
    
    print(f"\n📊 Résultats: {passed}/{len(tests)} tests passés")
    
    if passed == len(tests):
        print("🎉 Backend prêt pour le déploiement !")
        return True
    else:
        print("❌ Certains tests ont échoué")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
