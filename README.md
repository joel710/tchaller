# 🧭 Tcha-llé - MVP Ultra Bluffant

**Tcha-llé** est une application révolutionnaire qui rend visible l'économie informelle locale grâce à un moteur de recherche conversationnel intelligent.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- PostgreSQL (base de données configurée)

### Installation et Lancement

1. **Cloner et naviguer dans le projet**
```bash
cd /workspace
```

2. **Lancer le MVP**
```bash
python run.py
```

3. **Accéder à l'application**
- 🌐 **Interface utilisateur**: http://localhost:8000/static/recherche_ai.html
- 📚 **Documentation API**: http://localhost:8000/docs
- 🔧 **API Health**: http://localhost:8000/health

## ✨ Fonctionnalités du MVP

### 🔍 Moteur de Recherche Conversationnel
- Comprend le langage naturel français
- Recherche géolocalisée intelligente
- Classification automatique des intentions
- Extraction d'entités (plats, services, contraintes temporelles)

### 📱 Interface Utilisateur Moderne
- Design responsive et élégant
- Recherche en temps réel
- Géolocalisation automatique
- Filtres avancés (catégorie, prix, statut)

### 🏪 Gestion des Commerces
- Création et modification par les ambassadeurs
- Statuts en temps réel (OUVERT/FERMÉ)
- Photos et informations détaillées
- Système de vérification

### 🔐 Authentification Sécurisée
- Authentification par OTP (SMS/WhatsApp)
- Gestion des rôles (utilisateur/ambassadeur)
- Tokens JWT sécurisés

### 📊 Base de Données Optimisée
- PostgreSQL avec PostGIS pour la géolocalisation
- Indexation spatiale pour des recherches rapides
- Relations optimisées entre entités

## 🏗️ Architecture

```
backend/
├── main.py              # Point d'entrée FastAPI
├── database.py          # Modèles SQLAlchemy
├── schemas.py           # Schémas Pydantic
├── auth.py              # Authentification JWT/OTP
├── search_engine.py     # Moteur de recherche conversationnel
├── seed_data.py         # Données de test
└── routers/
    ├── auth.py          # Endpoints d'authentification
    ├── merchants.py     # Gestion des commerces
    ├── webhook.py       # Webhooks WhatsApp/SMS
    └── categories.py    # Gestion des catégories

frontend/
└── index.html           # Interface utilisateur moderne
```

## 🔧 Configuration

### Variables d'Environnement
Le fichier `.env` contient la configuration de la base de données PostgreSQL :

```env
DATABASE_URL=postgresql://neondb_owner:npg_cxutU4TLm1qp@ep-wispy-darkness-agjihedd-pooler.c-2.eu-central-1.aws.neon.tech/tchaller?sslmode=require&channel_binding=require
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📡 API Endpoints

### Authentification
- `POST /auth/request-otp` - Demander un code OTP
- `POST /auth/verify-otp` - Vérifier le code OTP
- `POST /auth/register-ambassador` - S'inscrire comme ambassadeur

### Commerces
- `GET /merchants/` - Lister les commerces avec filtres
- `GET /merchants/{id}` - Détails d'un commerce
- `POST /merchants/` - Créer un commerce (ambassadeur)
- `PUT /merchants/{id}` - Modifier un commerce
- `POST /merchants/search` - Recherche conversationnelle

### Webhooks
- `POST /webhook/status` - Mise à jour de statut WhatsApp/SMS

## 🎯 Exemples d'Utilisation

### Recherche Conversationnelle
```json
POST /merchants/search
{
  "query": "Trouve-moi un endroit où je peux manger du porc ce soir près de moi",
  "latitude": 6.1723,
  "longitude": 1.2312
}
```

### Réponse Intelligente
```json
{
  "merchants": [...],
  "total_count": 3,
  "query_processed": "trouve endroit manger porc ce soir près moi",
  "search_time_ms": 45.2,
  "response": "J'ai trouvé 3 endroits qui correspondent à votre recherche. Le plus proche est **Maquis Doho** à 420m - ✅ **OUVERT** (✓ Vérifié) - ⭐ 4.5/5"
}
```

## 🚀 Déploiement sur Render

1. **Créer un nouveau service Web sur Render**
2. **Configurer les variables d'environnement**
3. **Déployer depuis le repository Git**
4. **L'application sera accessible via l'URL Render**

## 🔮 Roadmap

### Phase 1 - MVP (Actuel)
- ✅ API REST complète
- ✅ Moteur de recherche conversationnel
- ✅ Interface utilisateur moderne
- ✅ Authentification OTP
- ✅ Gestion des commerces

### Phase 2 - Scale (3-6 mois)
- 🔄 Intégration Twilio pour SMS/WhatsApp
- 🔄 Cache Redis pour les performances
- 🔄 Monitoring et alertes
- 🔄 Badges de vérification

### Phase 3 - Monétisation (6-12 mois)
- 🔄 Pipeline de données anonymisées
- 🔄 API B2B
- 🔄 Système d'abonnements
- 🔄 Expansion multi-villes

## 🤝 Contribution

Ce MVP est conçu pour être déployé rapidement et évoluer progressivement. La structure modulaire permet d'ajouter facilement de nouvelles fonctionnalités.

## 📞 Support

Pour toute question ou problème, consultez la documentation API à `/docs` ou contactez l'équipe de développement.

---

**Tcha-llé** - Rendre visible l'économie informelle locale 🚀
