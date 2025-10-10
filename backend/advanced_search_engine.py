"""
Moteur de recherche avancé pour la structure ultra polyvalente
"""
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from geoalchemy2 import functions as gf
from .new_models import Activity, ActivityType, Category, Zone, SearchLog, UserInteraction
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime, timedelta

class AdvancedSearchEngine:
    def __init__(self):
        self.intent_patterns = {
            'search_activity': [
                r'trouve.*endroit', r'cherche.*endroit', r'où.*aller', r'où.*trouver',
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin',
                r'pharmacie', r'hôpital', r'école', r'université', r'banque', r'garage',
                r'coiffure', r'centre.*jeux', r'cinéma', r'théâtre', r'église', r'mosquée'
            ],
            'find_open_now': [
                r'ouvert.*maintenant', r'ouvert.*ce soir', r'ouvert.*aujourd'hui',
                r'qui.*ouvert', r'fermé', r'disponible', r'accessible'
            ],
            'find_by_service': [
                r'manger.*porc', r'manger.*poulet', r'manger.*poisson', r'manger.*riz',
                r'plat.*porc', r'plat.*poulet', r'cuisine.*africaine', r'cuisine.*locale',
                r'réparer.*voiture', r'coiffer', r'acheter.*médicament', r'étudier',
                r'prier', r'jouer', r'divertir'
            ],
            'ask_hours': [
                r'horaires', r'heures.*ouverture', r'ferme.*à', r'ouvre.*à',
                r'disponible.*quand', r'accessible.*quand'
            ],
            'ask_contact': [
                r'numéro', r'téléphone', r'whatsapp', r'contact', r'appeler',
                r'email', r'site.*web', r'adresse'
            ],
            'ask_directions': [
                r'itinéraire', r'comment.*aller', r'où.*se.*trouve', r'direction',
                r'carte', r'localisation'
            ],
            'compare_activities': [
                r'meilleur', r'comparer', r'différence', r'quel.*choisir',
                r'recommandation', r'suggestion'
            ]
        }
        
        self.entity_patterns = {
            'activity_type': [
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin',
                r'pharmacie', r'hôpital', r'école', r'université', r'banque', r'garage',
                r'coiffure', r'centre.*jeux', r'cinéma', r'théâtre', r'église', r'mosquée',
                r'station.*service', r'clinique', r'laboratoire', r'centre.*formation',
                r'tribunal', r'mairie', r'préfecture'
            ],
            'service_item': [
                r'porc', r'poulet', r'poisson', r'riz', r'fufu', r'attiéké', r'alloco',
                r'pizza', r'burger', r'sandwich', r'jus', r'bière', r'cocktail',
                r'médicament', r'consultation', r'analyse', r'vaccin',
                r'coiffure', r'manucure', r'pédicure', r'massage',
                r'essence', r'gasoil', r'vidange', r'réparation',
                r'cours', r'formation', r'diplôme', r'certificat'
            ],
            'time_constraint': [
                r'ce soir', r'aujourd'hui', r'maintenant', r'après-midi', r'matin',
                r'weekend', r'samedi', r'dimanche', r'urgence', r'immédiatement'
            ],
            'location': [
                r'près.*moi', r'proche', r'ici', r'quartier', r'centre.*ville',
                r'cocody', r'plateau', r'yopougon', r'adjamé', r'treichville',
                r'zone.*4', r'zone.*3', r'zone.*2', r'zone.*1'
            ],
            'price_level': [
                r'pas cher', r'bon marché', r'cher', r'coûteux', r'économique',
                r'gratuit', r'payant', r'abordable', r'luxueux'
            ],
            'quality_level': [
                r'excellent', r'bon', r'moyen', r'mauvais', r'terrible',
                r'recommandé', r'populaire', r'connu', r'réputé'
            ]
        }
        
        self.activity_type_mapping = {
            'restaurant': 'Restaurant',
            'maquis': 'Maquis',
            'bar': 'Bar',
            'café': 'Café',
            'boutique': 'Boutique',
            'magasin': 'Magasin',
            'pharmacie': 'Pharmacie',
            'hôpital': 'Hôpital',
            'école': 'École',
            'université': 'Université',
            'banque': 'Banque',
            'garage': 'Garage',
            'coiffure': 'Coiffure',
            'centre.*jeux': 'Centre de jeux',
            'cinéma': 'Cinéma',
            'théâtre': 'Théâtre',
            'église': 'Église',
            'mosquée': 'Mosquée'
        }

    def preprocess_query(self, query: str) -> str:
        """Nettoie et normalise la requête"""
        query = query.lower().strip()
        query = re.sub(r'\s+', ' ', query)
        return query

    def classify_intent(self, query: str) -> str:
        """Classifie l'intention de la requête"""
        query = self.preprocess_query(query)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        return 'search_activity'

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extrait les entités de la requête"""
        query = self.preprocess_query(query)
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    entities[entity_type] = match.group(0)
                    break
        
        return entities

    def generate_advanced_sql_query(self, search_request: Dict[str, Any], entities: Dict[str, Any]) -> Tuple[str, Dict]:
        """Génère une requête SQL avancée basée sur la nouvelle structure"""
        
        base_query = """
        SELECT 
            a.*,
            at.name as activity_type_name,
            at.slug as activity_type_slug,
            c.name as category_name,
            c.slug as category_slug,
            z.name as zone_name,
            ci.name as city_name,
            r.name as region_name,
            co.name as country_name,
            u.full_name as owner_name,
            amb.full_name as ambassador_name,
            ST_X(a.location) as longitude,
            ST_Y(a.location) as latitude,
            ST_Distance(
                a.location, 
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)
            ) as distance
        FROM activities a
        LEFT JOIN activity_types at ON a.activity_type_id = at.id
        LEFT JOIN categories c ON a.category_id = c.id
        LEFT JOIN zones z ON a.zone_id = z.id
        LEFT JOIN cities ci ON z.city_id = ci.id
        LEFT JOIN regions r ON ci.region_id = r.id
        LEFT JOIN countries co ON r.country_id = co.id
        LEFT JOIN users u ON a.owner_id = u.id
        LEFT JOIN ambassadors amb ON a.ambassador_id = amb.user_id
        WHERE a.is_active = TRUE
        """
        
        params = {
            'latitude': search_request.get('latitude', 0),
            'longitude': search_request.get('longitude', 0)
        }
        
        # Filtre par rayon
        if search_request.get('radius'):
            base_query += """
            AND ST_DWithin(
                a.location, 
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), 
                :radius
            )
            """
            params['radius'] = search_request['radius']
        
        # Filtre par type d'activité
        if search_request.get('activity_type_id'):
            base_query += " AND a.activity_type_id = :activity_type_id"
            params['activity_type_id'] = search_request['activity_type_id']
        elif 'activity_type' in entities:
            activity_type_name = self.activity_type_mapping.get(entities['activity_type'], 'Restaurant')
            base_query += " AND at.name ILIKE :activity_type_name"
            params['activity_type_name'] = f"%{activity_type_name}%"
        
        # Filtre par catégorie
        if search_request.get('category_id'):
            base_query += " AND a.category_id = :category_id"
            params['category_id'] = search_request['category_id']
        
        # Filtre par niveau de prix
        if search_request.get('price_level'):
            base_query += " AND a.price_level = :price_level"
            params['price_level'] = search_request['price_level']
        elif 'price_level' in entities:
            if 'pas cher' in entities['price_level'] or 'bon marché' in entities['price_level']:
                params['price_level'] = 1
            elif 'cher' in entities['price_level'] or 'coûteux' in entities['price_level']:
                params['price_level'] = 3
            else:
                params['price_level'] = 2
            base_query += " AND a.price_level = :price_level"
        
        # Filtre par statut ouvert
        if search_request.get('is_open_now'):
            base_query += " AND a.is_open = TRUE"
        elif 'time_constraint' in entities:
            if any(word in entities['time_constraint'] for word in ['ce soir', 'maintenant', 'aujourd'hui']):
                base_query += " AND a.is_open = TRUE"
        
        # Filtre par niveau de vérification
        if search_request.get('verification_level'):
            base_query += " AND a.verification_level >= :verification_level"
            params['verification_level'] = search_request['verification_level']
        
        # Recherche textuelle avancée
        if search_request.get('query'):
            base_query += """
            AND (
                a.name ILIKE :query 
                OR a.description ILIKE :query 
                OR a.short_description ILIKE :query
                OR EXISTS (
                    SELECT 1 FROM unnest(a.tags) tag 
                    WHERE tag ILIKE :query
                )
                OR EXISTS (
                    SELECT 1 FROM unnest(a.keywords) keyword 
                    WHERE keyword ILIKE :query
                )
            )
            """
            params['query'] = f"%{search_request['query']}%"
        
        # Filtre par zone
        if search_request.get('zone_id'):
            base_query += " AND a.zone_id = :zone_id"
            params['zone_id'] = search_request['zone_id']
        
        # Filtre par langue
        if search_request.get('language'):
            base_query += " AND :language = ANY(a.languages)"
            params['language'] = search_request['language']
        
        # Tri intelligent
        base_query += """
        ORDER BY 
            CASE WHEN a.is_open = TRUE THEN 0 ELSE 1 END,
            a.verification_level DESC,
            a.rating DESC,
            distance ASC,
            a.review_count DESC,
            a.created_at DESC
        LIMIT :limit
        """
        params['limit'] = search_request.get('limit', 20)
        
        return base_query, params

    def rank_results(self, activities: List[Activity], entities: Dict[str, Any], user_context: Dict[str, Any] = None) -> List[Activity]:
        """Classe les résultats selon la pertinence"""
        if not activities:
            return activities
        
        for activity in activities:
            score = 0
            
            # Score de distance (plus proche = mieux)
            if hasattr(activity, 'distance') and activity.distance:
                if activity.distance < 500:
                    score += 100
                elif activity.distance < 1000:
                    score += 80
                elif activity.distance < 2000:
                    score += 60
                else:
                    score += 40
            
            # Score de vérification
            if activity.is_verified:
                score += 50
                score += activity.verification_level * 10
            
            # Score de statut ouvert
            if activity.is_open:
                score += 30
            
            # Score d'évaluation
            score += float(activity.rating) * 10
            
            # Score de popularité
            score += min(activity.review_count, 100) * 0.5
            score += min(activity.view_count, 1000) * 0.1
            score += min(activity.search_count, 500) * 0.2
            
            # Bonus pour les activités récentes
            days_old = (datetime.now() - activity.created_at).days
            if days_old < 30:
                score += 10
            elif days_old < 90:
                score += 5
            
            # Bonus pour les activités avec photos
            if activity.cover_image_url:
                score += 5
            
            # Bonus pour les activités avec informations complètes
            if activity.description and len(activity.description) > 50:
                score += 5
            if activity.opening_hours:
                score += 5
            if activity.phone_number or activity.whatsapp_number:
                score += 5
            
            # Stocker le score pour le tri
            activity.relevance_score = score
        
        # Trier par score de pertinence
        return sorted(activities, key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)

    def generate_advanced_response(self, activities: List[Activity], intent: str, entities: Dict[str, Any], user_context: Dict[str, Any] = None) -> str:
        """Génère une réponse avancée et contextuelle"""
        if not activities:
            return "Désolé, je n'ai trouvé aucune activité correspondant à votre recherche. Essayez avec d'autres mots-clés ou élargissez votre zone de recherche."
        
        count = len(activities)
        nearest = activities[0]
        
        # Réponse de base
        if count == 1:
            response = f"J'ai trouvé 1 activité parfaite pour vous !"
        else:
            response = f"J'ai trouvé {count} activités qui correspondent à votre recherche."
        
        # Informations sur l'activité la plus proche
        response += f"\n\nLe plus proche est **{nearest.name}**"
        
        if hasattr(nearest, 'distance') and nearest.distance:
            if nearest.distance < 1000:
                response += f" à {int(nearest.distance)}m"
            else:
                response += f" à {nearest.distance/1000:.1f}km"
        
        # Informations sur le type d'activité
        if hasattr(nearest, 'activity_type_name') and nearest.activity_type_name:
            response += f" ({nearest.activity_type_name})"
        
        # Statut
        if nearest.is_open:
            response += " - ✅ **OUVERT**"
        else:
            response += " - ❌ **FERMÉ**"
        
        # Niveau de vérification
        if nearest.is_verified:
            if nearest.verification_level >= 3:
                response += " (✓ Vérifié Premium)"
            elif nearest.verification_level >= 2:
                response += " (✓ Vérifié Complet)"
            else:
                response += " (✓ Vérifié Basique)"
        
        # Évaluation
        if nearest.rating > 0:
            response += f" - ⭐ {nearest.rating:.1f}/5"
            if nearest.review_count > 0:
                response += f" ({nearest.review_count} avis)"
        
        # Niveau de prix
        if nearest.price_level:
            price_icons = "€" * nearest.price_level
            response += f" - {price_icons}"
        
        # Informations de contact si demandées
        if 'ask_contact' in intent or 'contact' in entities:
            if nearest.phone_number:
                response += f"\n\n📞 Téléphone: {nearest.phone_number}"
            if nearest.whatsapp_number:
                response += f"\n💬 WhatsApp: {nearest.whatsapp_number}"
            if nearest.email:
                response += f"\n📧 Email: {nearest.email}"
            if nearest.website:
                response += f"\n🌐 Site web: {nearest.website}"
        
        # Horaires si demandés
        if 'ask_hours' in intent or 'horaires' in entities:
            if nearest.opening_hours:
                try:
                    hours = json.loads(nearest.opening_hours) if isinstance(nearest.opening_hours, str) else nearest.opening_hours
                    response += f"\n\n🕒 Horaires: {hours.get('today', 'Non spécifié')}"
                except:
                    response += f"\n\n🕒 Horaires: {nearest.opening_hours}"
        
        # Directions si demandées
        if 'ask_directions' in intent or 'itinéraire' in entities:
            response += f"\n\n🗺️ Voulez-vous l'itinéraire vers {nearest.name} ?"
        
        # Plus d'options si plusieurs résultats
        if count > 1:
            response += f"\n\nVoulez-vous voir les {count-1} autres options ?"
        
        # Suggestions contextuelles
        if user_context and user_context.get('previous_searches'):
            response += "\n\n💡 Basé sur vos recherches précédentes, je peux aussi vous suggérer des activités similaires."
        
        return response

    def search(self, db: Session, search_request: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Méthode de recherche principale"""
        import time
        start_time = time.time()
        
        # Préprocessing
        processed_query = self.preprocess_query(search_request.get('query', ''))
        
        # Classification et extraction d'entités
        intent = self.classify_intent(processed_query)
        entities = self.extract_entities(processed_query)
        
        # Génération de la requête SQL
        sql_query, params = self.generate_advanced_sql_query(search_request, entities)
        
        # Exécution de la requête
        result = db.execute(text(sql_query), params)
        activities = []
        
        for row in result:
            activity_dict = dict(row._mapping)
            activity = Activity(**{k: v for k, v in activity_dict.items() if k in Activity.__table__.columns})
            
            # Ajouter les attributs calculés
            for key, value in activity_dict.items():
                if key not in Activity.__table__.columns:
                    setattr(activity, key, value)
            
            activities.append(activity)
        
        # Classement des résultats
        activities = self.rank_results(activities, entities, user_context)
        
        # Génération de la réponse
        response = self.generate_advanced_response(activities, intent, entities, user_context)
        
        # Log de la recherche
        search_log = SearchLog(
            query=search_request.get('query', ''),
            processed_query=processed_query,
            user_location=search_request.get('user_location'),
            search_radius=search_request.get('radius', 5000),
            results_count=len(activities),
            intent=intent,
            entities=entities,
            search_time_ms=int((time.time() - start_time) * 1000)
        )
        
        if search_request.get('user_id'):
            search_log.user_id = search_request['user_id']
        
        db.add(search_log)
        db.commit()
        
        search_time = (time.time() - start_time) * 1000
        
        return {
            "activities": activities,
            "total_count": len(activities),
            "query_processed": processed_query,
            "search_time_ms": search_time,
            "response": response,
            "intent": intent,
            "entities": entities,
            "search_id": search_log.id
        }
