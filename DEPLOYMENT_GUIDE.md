# 🚀 Guide de Déploiement Tcha-llé Backend sur Render

## 📋 Prérequis

- ✅ Compte Render.com
- ✅ Base de données PostgreSQL (Neon fournie)
- ✅ Repository GitHub avec le code
- ✅ Variables d'environnement configurées

## 🔧 Configuration Actuelle

### **Fichiers de Configuration**

#### `requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
geoalchemy2==0.14.2
shapely==2.0.2
nltk==3.8.1
scikit-learn==1.3.2
numpy==1.24.4
pandas==2.1.4
requests==2.31.0
httpx==0.25.2
jinja2==3.1.2
aiofiles==23.2.1
```

#### `Procfile`
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### `render.yaml`
```yaml
services:
  - type: web
    name: tchaller-api
    env: python
    plan: free
    buildCommand: |
      pip install -r requirements.txt
      python -c "from backend.database.connection import create_tables; create_tables()"
      python -c "from backend.seed_data import create_sample_data; create_sample_data()"
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        value: postgresql://neondb_owner:npg_cxutU4TLm1qp@ep-wispy-darkness-agjihedd-pooler.c-2.eu-central-1.aws.neon.tech/tchaller?sslmode=require&channel_binding=require
      - key: SECRET_KEY
        value: tchaller-ultra-polyvalent-secret-key-2024-render-deploy
      - key: ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "30"
      - key: CORS_ORIGINS
        value: "*"
      - key: CORS_ALLOW_METHODS
        value: "*"
      - key: CORS_ALLOW_HEADERS
        value: "*"
      - key: CORS_ALLOW_CREDENTIALS
        value: "true"
```

## 🚀 Étapes de Déploiement

### **1. Préparation de la Base de Données**

#### A. Exécuter le Script SQL
```sql
-- Exécuter database_schema.sql sur votre base de données Neon
-- Ce script crée toutes les tables ultra polyvalentes
```

#### B. Vérifier les Extensions PostGIS
```sql
-- Vérifier que PostGIS est activé
SELECT PostGIS_version();
```

### **2. Déploiement sur Render**

#### A. Connexion GitHub
1. Allez sur [render.com](https://render.com)
2. Connectez votre compte GitHub
3. Autorisez l'accès au repository `tchaller`

#### B. Création du Service
1. Cliquez sur **"New +"**
2. Sélectionnez **"Web Service"**
3. Connectez le repository `tchaller`
4. Choisissez la branche `feature/ultra-polyvalent-architecture`

#### C. Configuration du Service
```
Name: tchaller-api
Environment: Python 3
Region: Oregon (US West)
Branch: feature/ultra-polyvalent-architecture
Root Directory: (laisser vide)
```

#### D. Build & Deploy
```
Build Command: pip install -r requirements.txt && python -c "from backend.database.connection import create_tables; create_tables()" && python -c "from backend.seed_data import create_sample_data; create_sample_data()"

Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### E. Variables d'Environnement
```
DATABASE_URL = postgresql://neondb_owner:npg_cxutU4TLm1qp@ep-wispy-darkness-agjihedd-pooler.c-2.eu-central-1.aws.neon.tech/tchaller?sslmode=require&channel_binding=require
SECRET_KEY = tchaller-ultra-polyvalent-secret-key-2024-render-deploy
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
CORS_ORIGINS = *
CORS_ALLOW_METHODS = *
CORS_ALLOW_HEADERS = *
CORS_ALLOW_CREDENTIALS = true
```

### **3. Vérification du Déploiement**

#### A. Tests des Endpoints
```bash
# Test de l'endpoint principal
curl https://tchaller-api.onrender.com/

# Test de l'API
curl https://tchaller-api.onrender.com/api/activities

# Test de la recherche
curl -X POST https://tchaller-api.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Je cherche un restaurant"}'
```

#### B. Documentation API
```
https://tchaller-api.onrender.com/docs
```

## 🔧 Dépannage

### **Problèmes Courants**

#### 1. Erreur de Build
```bash
# Vérifier les logs de build sur Render
# Problème probable: dépendances manquantes
```

#### 2. Erreur de Base de Données
```bash
# Vérifier la connexion à Neon
# Vérifier que PostGIS est activé
```

#### 3. Erreur CORS
```bash
# Vérifier les variables d'environnement CORS
# Tester avec différents navigateurs
```

### **Logs de Debug**
```bash
# Sur Render, aller dans "Logs" pour voir les erreurs
# Vérifier les logs de build et de runtime
```

## 📊 Monitoring

### **Métriques à Surveiller**
- ✅ **Uptime** : Disponibilité du service
- ✅ **Response Time** : Temps de réponse des API
- ✅ **Memory Usage** : Utilisation mémoire
- ✅ **Database Connections** : Connexions à la base

### **Alertes Recommandées**
- Uptime < 99%
- Response time > 5s
- Memory usage > 80%
- Error rate > 5%

## 🎯 URLs de Production

### **API Endpoints**
```
Base URL: https://tchaller-api.onrender.com

Endpoints principaux:
- GET  /                    # Page d'accueil
- GET  /info               # Informations de l'API
- GET  /docs               # Documentation Swagger
- POST /api/auth/request-otp    # Demande OTP
- POST /api/auth/verify-otp     # Vérification OTP
- GET  /api/activities          # Liste des activités
- POST /api/search             # Recherche conversationnelle
- GET  /api/categories         # Catégories d'activités
```

### **Frontend PWA**
```
URL: https://tchaller-api.onrender.com/ambassador_enhanced.html
```

## ✅ Checklist de Déploiement

- [ ] Base de données PostgreSQL configurée
- [ ] Script `database_schema.sql` exécuté
- [ ] Extensions PostGIS activées
- [ ] Repository GitHub connecté
- [ ] Service Render créé
- [ ] Variables d'environnement configurées
- [ ] Build réussi
- [ ] Service démarré
- [ ] Tests des endpoints
- [ ] Documentation accessible
- [ ] CORS fonctionnel
- [ ] Monitoring configuré

## 🎉 Résultat Attendu

Après le déploiement, vous devriez avoir :

1. **API Ultra Polyvalente** accessible sur Render
2. **CORS Ultra Permissif** pour tous les frontends
3. **Base de Données** avec toutes les tables créées
4. **Moteur de Recherche** conversationnel fonctionnel
5. **Documentation** automatique avec Swagger
6. **PWA Frontend** pour les ambassadeurs

**🚀 Votre backend Tcha-llé est maintenant prêt pour la production !**