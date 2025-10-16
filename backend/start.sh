#!/bin/bash

# Script de démarrage pour Render
echo "🚀 Démarrage de Tcha-llé Ultra Polyvalent..."

# Installer les dépendances NLTK nécessaires
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

# Démarrer l'application
echo "✅ Démarrage de l'application..."
gunicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout 120