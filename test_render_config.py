#!/usr/bin/env python3
"""
Test de la configuration optimisée pour Render
"""

import sys
import subprocess
import importlib.util

def test_python_version():
    """Teste la version de Python"""
    print("🐍 Test de la version Python...")
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 11:
        print("✅ Python 3.11 détecté - Compatible avec Render")
        return True
    elif version.major == 3 and version.minor >= 11:
        print("⚠️  Python 3.11+ détecté - Peut fonctionner")
        return True
    else:
        print("❌ Version Python incompatible - Utilisez Python 3.11")
        return False

def test_requirements():
    """Teste l'installation des requirements"""
    print("\n📦 Test des requirements...")
    
    try:
        # Lire requirements.txt
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        missing_packages = []
        installed_packages = []
        
        for req in requirements:
            if req.strip() and not req.startswith('#'):
                package = req.split('==')[0].split('[')[0]
                try:
                    __import__(package.replace('-', '_'))
                    installed_packages.append(package)
                except ImportError:
                    missing_packages.append(package)
        
        print(f"✅ Packages installés: {len(installed_packages)}")
        if missing_packages:
            print(f"❌ Packages manquants: {missing_packages}")
            return False
        else:
            print("✅ Tous les packages sont installés")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test des requirements: {e}")
        return False

def test_imports():
    """Teste les imports critiques"""
    print("\n🔍 Test des imports critiques...")
    
    critical_imports = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'pydantic',
        'geoalchemy2',
        'shapely'
    ]
    
    failed_imports = []
    
    for module in critical_imports:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} imports ont échoué")
        return False
    else:
        print("\n✅ Tous les imports critiques fonctionnent")
        return True

def test_scikit_learn():
    """Teste spécifiquement scikit-learn"""
    print("\n🤖 Test de scikit-learn...")
    
    try:
        import sklearn
        print(f"✅ scikit-learn version: {sklearn.__version__}")
        
        # Test d'import des modules critiques
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        print("✅ Modules scikit-learn fonctionnels")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur scikit-learn: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Avertissement scikit-learn: {e}")
        return True

def test_backend_imports():
    """Teste les imports du backend"""
    print("\n🏗️  Test des imports backend...")
    
    try:
        # Test des imports principaux
        from backend.config import settings
        from backend.database.connection import create_tables, get_db
        from backend.database.models import Activity, User, Category
        from backend.schemas.activities import ActivityResponse
        from backend.services.simple_search_engine import SimpleConversationalSearchEngine
        from backend.main import app
        
        print("✅ Tous les imports backend fonctionnent")
        return True
        
    except Exception as e:
        print(f"❌ Erreur imports backend: {e}")
        return False

def test_cors_config():
    """Teste la configuration CORS"""
    print("\n🌐 Test de la configuration CORS...")
    
    try:
        from backend.config import settings
        
        assert settings.cors_origins == ["*"], f"CORS origins incorrect: {settings.cors_origins}"
        assert settings.cors_allow_methods == ["*"], f"CORS methods incorrect: {settings.cors_allow_methods}"
        assert settings.cors_allow_headers == ["*"], f"CORS headers incorrect: {settings.cors_allow_headers}"
        assert settings.cors_allow_credentials == True, f"CORS credentials incorrect: {settings.cors_allow_credentials}"
        
        print("✅ Configuration CORS correcte")
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration CORS: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de Configuration Render Optimisée")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_requirements,
        test_imports,
        test_scikit_learn,
        test_backend_imports,
        test_cors_config
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
        print("🎉 Configuration optimisée prête pour Render !")
        print("\n📋 Prochaines étapes:")
        print("1. Créer un repo backend séparé")
        print("2. Copier tous les fichiers backend")
        print("3. Ajouter runtime.txt et requirements.txt")
        print("4. Déployer sur Render")
        return True
    else:
        print("❌ Certains tests ont échoué. Vérifiez la configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)