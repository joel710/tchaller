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
