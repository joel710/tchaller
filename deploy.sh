#!/bin/bash

echo "🚀 Déploiement de Tcha-llé sur Render"
echo "======================================"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "backend/main.py" ]; then
    echo "❌ Erreur: Le fichier backend/main.py n'existe pas"
    echo "Assurez-vous d'être dans le répertoire racine du projet"
    exit 1
fi

# Vérifier que Git est configuré
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  Configuration Git manquante"
    echo "Configuration de Git..."
    git config --global user.name "Tcha-llé Deploy"
    git config --global user.email "deploy@tchaller.com"
fi

# Ajouter tous les fichiers
echo "📁 Ajout des fichiers..."
git add .

# Commit des changements
echo "💾 Commit des changements..."
git commit -m "Deploy Tcha-llé MVP v1.0.0

✨ Fonctionnalités:
- Moteur de recherche conversationnel intelligent
- Interface utilisateur moderne et responsive
- API REST complète avec documentation
- Portail ambassadeur PWA
- Authentification sécurisée par OTP
- Gestion des commerces et géolocalisation
- Prêt pour le déploiement sur Render"

# Push vers le repository
echo "📤 Push vers le repository..."
git push origin main

echo ""
echo "✅ Déploiement terminé !"
echo ""
echo "🌐 Votre application sera disponible sur:"
echo "   https://tchaller-api.onrender.com"
echo ""
echo "📚 Documentation API:"
echo "   https://tchaller-api.onrender.com/docs"
echo ""
echo "🎨 Interface utilisateur:"
echo "   https://tchaller-api.onrender.com/static/index.html"
echo ""
echo "👥 Portail ambassadeur:"
echo "   https://tchaller-api.onrender.com/static/ambassador.html"
echo ""
echo "🔧 Pour configurer le déploiement automatique sur Render:"
echo "   1. Connectez votre repository GitHub à Render"
echo "   2. Utilisez les paramètres suivants:"
echo "      - Build Command: pip install -r backend/requirements.txt"
echo "      - Start Command: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
echo "      - Environment: Python 3"
echo "   3. Ajoutez les variables d'environnement dans Render"
echo ""
echo "🎉 Tcha-llé MVP est prêt pour la production !"