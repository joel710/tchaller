#!/bin/bash

# Script de build pour Render
echo "🔧 Installation des dépendances..."

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances système nécessaires
apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
pip install -r requirements.txt

# Télécharger les données NLTK
python -c "
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
print('✅ NLTK data downloaded')
"

echo "✅ Build terminé avec succès"