#!/bin/bash

# 🚀 Script pour copier les fichiers backend vers un repo séparé
# Ce script prépare tous les fichiers nécessaires pour le déploiement Render

set -e  # Arrêter en cas d'erreur

echo "🚀 Préparation des fichiers backend pour repo séparé"
echo "=================================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "backend" ]; then
    print_error "Le répertoire 'backend' n'existe pas. Êtes-vous dans le bon répertoire ?"
    exit 1
fi

# Créer le répertoire de destination
BACKEND_DIR="tchaller-backend"
print_status "Création du répertoire $BACKEND_DIR..."

if [ -d "$BACKEND_DIR" ]; then
    print_warning "Le répertoire $BACKEND_DIR existe déjà. Suppression..."
    rm -rf "$BACKEND_DIR"
fi

mkdir -p "$BACKEND_DIR/backend"
print_success "Répertoire créé"

# Copier les fichiers principaux du backend
print_status "Copie des fichiers principaux..."
cp backend/main.py "$BACKEND_DIR/backend/"
cp backend/config.py "$BACKEND_DIR/backend/"
cp backend/__init__.py "$BACKEND_DIR/backend/"

# Copier les sous-répertoires
print_status "Copie des sous-répertoires..."
cp -r backend/database "$BACKEND_DIR/backend/"
cp -r backend/schemas "$BACKEND_DIR/backend/"
cp -r backend/services "$BACKEND_DIR/backend/"
cp -r backend/api "$BACKEND_DIR/backend/"

# Copier les fichiers de configuration
print_status "Copie des fichiers de configuration..."
cp requirements.txt "$BACKEND_DIR/"
cp runtime.txt "$BACKEND_DIR/"
cp Procfile "$BACKEND_DIR/"

# Créer .env.example
print_status "Création de .env.example..."
cat > "$BACKEND_DIR/.env.example" << 'EOF'
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=*
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
CORS_ALLOW_CREDENTIALS=true
EOF

# Copier la base de données
print_status "Copie du schéma de base de données..."
cp database_schema.sql "$BACKEND_DIR/"

# Créer README.md pour le backend
print_status "Création du README.md..."
cat > "$BACKEND_DIR/README.md" << 'EOF'
# 🚀 Tcha-llé Backend - API Ultra Polyvalente

## 📋 Description

Backend ultra polyvalent pour la plateforme Tcha-llé, capable de gérer tous types d'activités utiles avec un moteur de recherche conversationnel intelligent.

## 🏗️ Architecture

- **FastAPI** : Framework web moderne et rapide
- **PostgreSQL + PostGIS** : Base de données spatiale
- **SQLAlchemy** : ORM pour la gestion des données
- **Pydantic** : Validation des données
- **CORS Ultra Permissif** : Accepte toutes les origines

## 🚀 Déploiement sur Render

### Prérequis
- Compte Render.com
- Base de données PostgreSQL (Neon recommandé)

### Configuration
1. Connecter le repository GitHub
2. Build Command : `pip install -r requirements.txt`
3. Start Command : `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Variables d'Environnement
```
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=*
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
CORS_ALLOW_CREDENTIALS=true
```

## 📊 Fonctionnalités

- ✅ **API REST Complète** : Authentification, activités, recherche
- ✅ **Moteur de Recherche Conversationnel** : 8 intents, 7 entités
- ✅ **Base de Données Ultra Polyvalente** : 20+ tables
- ✅ **Support Tous Types d'Activités** : Santé, éducation, services, etc.
- ✅ **CORS Ultra Permissif** : Développement et production
- ✅ **Documentation Automatique** : Swagger UI intégré

## 🧪 Test Local

```bash
# Installer Python 3.11
pyenv install 3.11.9
pyenv local 3.11.9

# Installer les dépendances
pip install -r requirements.txt

# Tester l'application
uvicorn backend.main:app --reload
```

## 📚 Documentation API

Une fois déployé, accédez à la documentation interactive :
- **Swagger UI** : `https://votre-app.onrender.com/docs`
- **ReDoc** : `https://votre-app.onrender.com/redoc`

## 🎯 Endpoints Principaux

- `GET /` : Page d'accueil
- `GET /info` : Informations de l'API
- `POST /api/auth/request-otp` : Demande OTP
- `POST /api/auth/verify-otp` : Vérification OTP
- `GET /api/activities` : Liste des activités
- `POST /api/search` : Recherche conversationnelle
- `GET /api/categories` : Catégories d'activités

## 🔧 Développement

### Structure
```
backend/
├── main.py              # Application FastAPI
├── config.py            # Configuration
├── database/            # Base de données
├── schemas/             # Schémas Pydantic
├── services/            # Services métier
└── api/                 # Routes API
```

### Tests
```bash
python test_render_config.py
```

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

**🎉 Développé avec ❤️ pour l'économie locale africaine**
EOF

# Créer un script de test
print_status "Création du script de test..."
cat > "$BACKEND_DIR/test_deployment.py" << 'EOF'
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
EOF

chmod +x "$BACKEND_DIR/test_deployment.py"

# Créer un .gitignore
print_status "Création du .gitignore..."
cat > "$BACKEND_DIR/.gitignore" << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Temporary files
*.tmp
*.temp
EOF

# Afficher le résumé
print_success "Préparation terminée !"
echo
echo "📁 Fichiers créés dans : $BACKEND_DIR/"
echo
echo "📋 Structure du repo backend :"
echo "├── backend/                 # Code source"
echo "├── requirements.txt         # Dépendances Python"
echo "├── runtime.txt             # Version Python 3.11.9"
echo "├── Procfile               # Commande de démarrage"
echo "├── .env.example           # Variables d'environnement"
echo "├── database_schema.sql    # Schéma de base de données"
echo "├── README.md              # Documentation"
echo "├── test_deployment.py     # Script de test"
echo "└── .gitignore             # Fichiers à ignorer"
echo
echo "🚀 Prochaines étapes :"
echo "1. cd $BACKEND_DIR"
echo "2. git init"
echo "3. git add ."
echo "4. git commit -m 'Initial commit: Backend ultra polyvalent'"
echo "5. Créer un repo GitHub"
echo "6. git remote add origin https://github.com/votre-username/tchaller-backend.git"
echo "7. git push -u origin main"
echo "8. Déployer sur Render"
echo
echo "📚 Guide complet disponible dans : BACKEND_REPO_GUIDE.md"
echo
print_success "🎉 Backend prêt pour le déploiement !"