# 🧭 Tcha-llé — Backend & Moteur de Recherche Conversationnel

## 📖 Description du projet

**Tcha-llé** est une application mobile et web visant à **rendre visible l’économie informelle locale**.  
Elle permet aux utilisateurs de **trouver facilement les commerces, services et lieux populaires autour d’eux**, grâce à un **moteur de recherche conversationnel** qui comprend le langage naturel.

Exemple :  
> Utilisateur : *« Trouve-moi un endroit où je peux manger du porc ce soir près de moi. »*  
> Réponse : *« D’accord — j’ai trouvé 3 endroits où tu peux manger du porc ce soir près de toi. Le plus proche est “Maquis Doho” à 420m, il ferme à 23h. Tu veux l’itinéraire ou le numéro WhatsApp ? »*

---

## 🎯 Objectif du backend

Le backend doit permettre :
1. Une **API REST/GraphQL** robuste et extensible.
2. Un **moteur de recherche intelligent** capable de comprendre les requêtes naturelles.
3. Un **système de mise à jour en temps réel** des statuts (OUVERT / FERMÉ) via SMS ou WhatsApp.
4. Un **outil d’enrôlement rapide** des commerces via un portail ambassadeur.
5. Une architecture **sécurisée, scalable et monitorée**, prête pour l’évolution vers un système IA complet.

---

## ⚙️ Stack technique recommandée

| Composant | Choix recommandé |
|------------|------------------|
| Langage | **Node.js (NestJS)** |
| Base de données | **PostgreSQL** + **PostGIS** |
| Cache / Queue | **Redis** / **RabbitMQ** |
| Stockage média | S3-compatible (Wasabi, Backblaze, MinIO) |
| Authentification | JWT, OAuth2 (futur) |
| Monitoring | Prometheus + Grafana |
| Déploiement | Docker / Kubernetes |
| Communication | Twilio (WhatsApp/SMS) |

---

## 🧩 Structure du backend

### 1️⃣ Base de données (PostgreSQL)
Tables principales :
- **users**
- **ambassadors**
- **merchants**
- **merchant_photos**
- **merchant_status_history**
- **categories**
- **search_logs**
- **conversations**
- **messages**
- **subscriptions**
- **audits**

Chaque table doit inclure :
- clés primaires/étrangères
- indexations géospatiales (GIST)
- contraintes d’intégrité
- timestamps normalisés (`created_at`, `updated_at`)

---

### 2️⃣ Endpoints API (OpenAPI Spec)

| Endpoint | Description |
|-----------|--------------|
| `POST /auth/login` | Authentification via OTP |
| `POST /auth/verify-otp` | Vérification de code |
| `POST /auth/register-ambassador` | Inscription ambassadeur |
| `GET /merchants` | Liste filtrée de commerces |
| `GET /merchants/{id}` | Détails d’un commerce |
| `POST /merchants` | Création (ambassadeur) |
| `PUT /merchants/{id}` | Modification |
| `POST /merchants/{id}/photos` | Upload d’images |
| `GET /merchants/{id}/status` | Statut actuel |
| `POST /webhook/status` | Réception des messages WhatsApp/SMS |
| `POST /search/converse` | Recherche conversationnelle |
| `GET /admin/metrics` | KPIs administratifs |

---

### 3️⃣ Moteur de recherche conversationnel

**Pipeline du moteur :**

1. **Pré-traitement** : nettoyage, détection de langue, tokenisation.  
2. **Classification d’intent** :
   - `search_place`
   - `find_open_now`
   - `find_by_dish`
   - `ask_opening_hours`
   - `ask_contact`
3. **Extraction d’entités** :
   - `food_item`, `service_type`, `time_constraint`, `location`, `price_level`
4. **Génération de requête SQL** (PostGIS + filtres dynamiques).
5. **Classement (ranking)** :
   - Pondération par proximité, badge vérifié, statut ouvert, popularité.
6. **Génération de réponse humanisée** :
   - Templates variés et naturels.
7. **Conservation du contexte** :
   - Session utilisateur stockée dans Redis.

---

### 4️⃣ Statuts en temps réel (WhatsApp / SMS)

**Principe de fonctionnement :**
1. Le commerçant envoie “OUVERT” ou “FERMÉ” par message.  
2. Twilio → webhook `/webhook/status`.  
3. Le backend identifie le commerçant via son numéro.  
4. Le statut est mis à jour dans la base.  
5. Une notification temps réel est émise aux utilisateurs.

**Anti-abus & sécurité :**
- Vérification de signature Twilio.  
- Limitation du nombre de messages.  
- Captcha pour validations ambiguës.  
- Logs et suivi via tableau admin.

---

### 5️⃣ Portail ambassadeur

PWA mobile-friendly permettant :
- Enrôlement de nouveaux commerces (formulaire rapide).
- Upload de 1 à 3 photos.
- Détection GPS automatique.
- Génération automatique de QR code du commerce.

---

### 6️⃣ Architecture et déploiement

**MVP (Docker Compose)** :
- app (python)
- postgres
- redis
- worker (Twilio ingestion)
- nginx

**Production (Kubernetes)** :
- déploiements + services
- ingress nginx
- autoscaling horizontal
- stockage persistant pour DB et médias
- monitoring Prometheus/Grafana

---

### 7️⃣ Observabilité & sécurité

| Aspect | Outils / Bonnes pratiques |
|--------|----------------------------|
| **Logs** | JSON → ELK/Loki |
| **Metrics** | Prometheus (latence, erreurs, file d’attente) |
| **Dashboards** | Grafana |
| **Alertes** | seuils automatiques |
| **Sécurité** | HTTPS, JWT, rate limiting, chiffrement PII |
| **Backups** | Quotidiens + rétention 30 jours |
| **Conformité** | Inspiré RGPD : consentement, anonymisation, opt-out |

---

### 8️⃣ Tests & qualité

| Type de test | Cible |
|---------------|--------|
| Unitaires | modules NLP, ranking, API |
| Intégration | recherche → DB |
| E2E | flux WhatsApp → statut marchand |
| Charge (k6) | 1000 req/s |
| Validation MVP | <1s pour une requête non-cachée |

---

### 9️⃣ Roadmap technique

#### 🧱 Phase 1 — MVP (0–3 mois)
- API, DB, webhook Twilio, moteur NLP rule-based, PWA ambassadeur.

#### ⚙️ Phase 2 — Scale (3–12 mois)
- Optimisation NLP, cache Redis, monitoring complet, verified badges.

#### 💰 Phase 3 — Monétisation (12–36 mois)
- Pipeline de data anonymisée, API B2B, abonnements, expansion multi-villes.

---

### 🔬 Exemple de requête / réponse

**Entrée :**
```json
{
  "query": "Trouve moi un endroit où je peux manger du porc ce soir près de moi",
  "location": { "lat": 6.1723, "lon": 1.2312 }
}
