#!/bin/bash

# 🚀 Script de Déploiement Tcha-llé Backend sur Render
# Ce script automatise le processus de déploiement

set -e  # Arrêter en cas d'erreur

echo "🚀 Déploiement Tcha-llé Backend sur Render"
echo "=========================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
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
if [ ! -f "backend/main.py" ]; then
    print_error "Le fichier backend/main.py n'existe pas. Êtes-vous dans le bon répertoire ?"
    exit 1
fi

print_status "Vérification de la structure du projet..."

# Vérifier les fichiers essentiels
required_files=(
    "backend/main.py"
    "backend/config.py"
    "backend/database/connection.py"
    "backend/database/models.py"
    "requirements.txt"
    "Procfile"
    "render.yaml"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Fichier manquant: $file"
        exit 1
    fi
done

print_success "Structure du projet validée"

# Vérifier que Git est configuré
print_status "Vérification de la configuration Git..."

if ! git status > /dev/null 2>&1; then
    print_error "Git n'est pas initialisé dans ce répertoire"
    exit 1
fi

# Vérifier que nous sommes sur la bonne branche
current_branch=$(git branch --show-current)
if [ "$current_branch" != "feature/ultra-polyvalent-architecture" ]; then
    print_warning "Vous n'êtes pas sur la branche feature/ultra-polyvalent-architecture"
    print_warning "Branche actuelle: $current_branch"
    read -p "Voulez-vous continuer quand même ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Déploiement annulé"
        exit 1
    fi
fi

print_success "Configuration Git validée"

# Vérifier que tous les changements sont commités
if ! git diff --quiet || ! git diff --cached --quiet; then
    print_warning "Il y a des changements non commités"
    print_status "Ajout et commit des changements..."
    
    git add .
    git commit -m "feat: Prepare for Render deployment

- Updated requirements.txt with all dependencies
- Fixed render.yaml configuration for new architecture
- Added deployment guide and test scripts
- Ready for production deployment"
    
    print_success "Changements commités"
fi

# Pousser vers GitHub
print_status "Poussée vers GitHub..."

if ! git push origin "$current_branch"; then
    print_error "Échec de la poussée vers GitHub"
    exit 1
fi

print_success "Code poussé vers GitHub"

# Afficher les instructions pour Render
echo
echo "🎯 Étapes suivantes sur Render.com:"
echo "=================================="
echo
echo "1. 🌐 Allez sur https://render.com"
echo "2. 🔐 Connectez votre compte GitHub"
echo "3. ➕ Cliquez sur 'New +' puis 'Web Service'"
echo "4. 🔗 Connectez le repository 'tchaller'"
echo "5. 🌿 Sélectionnez la branche: $current_branch"
echo
echo "6. ⚙️  Configuration du service:"
echo "   - Name: tchaller-api"
echo "   - Environment: Python 3"
echo "   - Region: Oregon (US West)"
echo "   - Root Directory: (laisser vide)"
echo
echo "7. 🔧 Build & Deploy:"
echo "   - Build Command: pip install -r requirements.txt && python -c \"from backend.database.connection import create_tables; create_tables()\" && python -c \"from backend.seed_data import create_sample_data; create_sample_data()\""
echo "   - Start Command: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
echo
echo "8. 🔑 Variables d'environnement:"
echo "   - DATABASE_URL = postgresql://neondb_owner:npg_cxutU4TLm1qp@ep-wispy-darkness-agjihedd-pooler.c-2.eu-central-1.aws.neon.tech/tchaller?sslmode=require&channel_binding=require"
echo "   - SECRET_KEY = tchaller-ultra-polyvalent-secret-key-2024-render-deploy"
echo "   - ALGORITHM = HS256"
echo "   - ACCESS_TOKEN_EXPIRE_MINUTES = 30"
echo "   - CORS_ORIGINS = *"
echo "   - CORS_ALLOW_METHODS = *"
echo "   - CORS_ALLOW_HEADERS = *"
echo "   - CORS_ALLOW_CREDENTIALS = true"
echo
echo "9. 🚀 Cliquez sur 'Create Web Service'"
echo
echo "10. ⏳ Attendez que le build se termine (5-10 minutes)"
echo
echo "11. ✅ Testez votre API:"
echo "    - https://tchaller-api.onrender.com/"
echo "    - https://tchaller-api.onrender.com/docs"
echo "    - https://tchaller-api.onrender.com/api/activities"
echo

# Vérifier la base de données
print_status "Vérification de la base de données..."

echo "📋 N'oubliez pas d'exécuter le script SQL sur votre base de données Neon:"
echo "   - Allez sur https://console.neon.tech"
echo "   - Ouvrez votre base de données 'tchaller'"
echo "   - Exécutez le contenu de 'database_schema.sql'"
echo "   - Vérifiez que PostGIS est activé"
echo

print_success "Script de déploiement terminé !"
print_status "Suivez les instructions ci-dessus pour finaliser le déploiement sur Render."

echo
echo "📚 Documentation complète disponible dans:"
echo "   - DEPLOYMENT_GUIDE.md"
echo "   - PULL_REQUEST_DESCRIPTION.md"
echo
echo "🎉 Bon déploiement !"