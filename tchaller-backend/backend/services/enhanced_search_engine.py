"""
Moteur de recherche conversationnel ultra polyvalent
"""
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from geoalchemy2 import functions as gf
from backend.database.models import Activity, Category, ActivityType, SearchLog
from backend.schemas.search import SearchRequest
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class EnhancedConversationalSearchEngine:
    def __init__(self):
        self.intent_patterns = {
            'search_place': [
                r'trouve.*endroit', r'cherche.*endroit', r'où.*aller', r'où.*trouver',
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin',
                r'pharmacie', r'hôpital', r'école', r'université', r'banque', r'garage',
                r'coiffure', r'centre.*jeux', r'cinéma', r'théâtre', r'église', r'mosquée',
                r'station.*service', r'clinique', r'laboratoire', r'centre.*formation',
                r'tribunal', r'mairie', r'préfecture', r'ong', r'association'
            ],
            'find_open_now': [
                r'ouvert.*maintenant', r'ouvert.*ce soir', r'ouvert.*aujourd\'hui',
                r'qui.*ouvert', r'fermé', r'disponible', r'accessible.*maintenant'
            ],
            'find_by_service': [
                r'manger.*porc', r'manger.*poulet', r'manger.*poisson', r'manger.*riz',
                r'plat.*porc', r'plat.*poulet', r'cuisine.*africaine', r'cuisine.*locale',
                r'réparer.*voiture', r'coiffer', r'acheter.*médicament', r'étudier',
                r'prier', r'jouer', r'divertir', r'consulter.*médecin', r'faire.*analyse',
                r'prendre.*cours', r'se.*former', r'faire.*papiers', r'retirer.*argent'
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
            'compare_places': [
                r'meilleur', r'comparer', r'différence', r'quel.*choisir',
                r'recommandation', r'suggestion', r'alternative'
            ],
            'emergency': [
                r'urgence', r'urgent', r'immédiatement', r'rapidement',
                r'problème', r'aide', r'sos'
            ]
        }
        
        self.entity_patterns = {
            'food_item': [
                r'porc', r'poulet', r'poisson', r'riz', r'fufu', r'attiéké', r'alloco',
                r'pizza', r'burger', r'sandwich', r'jus', r'bière', r'cocktail'
            ],
            'service_type': [
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin', r'pharmacie',
                r'hôpital', r'clinique', r'école', r'université', r'banque', r'garage',
                r'coiffure', r'centre.*jeux', r'cinéma', r'théâtre', r'église', r'mosquée',
                r'station.*service', r'laboratoire', r'centre.*formation', r'tribunal',
                r'mairie', r'préfecture', r'ong', r'association'
            ],
            'service_item': [
                r'médicament', r'consultation', r'analyse', r'vaccin', r'coiffure',
                r'manucure', r'pédicure', r'massage', r'essence', r'gasoil', r'vidange',
                r'réparation', r'cours', r'formation', r'diplôme', r'certificat',
                r'papiers', r'carte.*identité', r'passeport', r'permis', r'argent'
            ],
            'time_constraint': [
                r'ce soir', r'aujourd\'hui', r'maintenant', r'après-midi', r'matin',
                r'weekend', r'samedi', r'dimanche', r'urgence', r'immédiatement'
            ],
            'location': [
                r'près.*moi', r'proche', r'ici', r'quartier', r'centre.*ville',
                r'cocody', r'plateau', r'yopougon', r'adjamé', r'treichville'
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
        
        # Templates de réponses variés et humains
        self.response_templates = {
            'greeting': [
                "Salut ! Je suis là pour t'aider à trouver ce que tu cherches 😊",
                "Bonjour ! Dis-moi ce que tu recherches et je vais te trouver les meilleures options !",
                "Hey ! Je suis ton assistant local, que puis-je faire pour toi aujourd'hui ?",
                "Coucou ! Prêt à découvrir les meilleures activités autour de toi ?"
            ],
            'search_results': [
                "Parfait ! J'ai trouvé {count} {type_activity} qui correspondent à ta recherche :",
                "Excellent ! Voici {count} {type_activity} que je te recommande :",
                "Super ! J'ai déniché {count} {type_activity} parfait(e)s pour toi :",
                "Génial ! Voici {count} {type_activity} qui vont te plaire :"
            ],
            'no_results': [
                "Hmm, je n'ai pas trouvé d'activité correspondant à ta recherche dans cette zone. Essaie d'élargir ta recherche ou de changer de mots-clés !",
                "Désolé, aucune activité ne correspond à tes critères pour le moment. Veux-tu que je te suggère des alternatives ?",
                "Oups ! Rien ne correspond exactement à ta demande. Peux-tu reformuler ou élargir ta zone de recherche ?",
                "Je n'ai rien trouvé qui colle parfaitement. Dis-moi ce que tu cherches exactement et je vais mieux t'aider !"
            ],
            'single_result': [
                "J'ai trouvé le lieu parfait pour toi !",
                "Parfait ! J'ai déniché exactement ce qu'il te faut !",
                "Excellent ! Voici le lieu idéal pour ta demande :",
                "Super ! J'ai trouvé la perle rare !"
            ],
            'multiple_results': [
                "J'ai trouvé plusieurs options intéressantes pour toi :",
                "Parfait ! Voici plusieurs {type_activity} qui pourraient t'intéresser :",
                "Super ! J'ai déniché {count} {type_activity} de qualité :",
                "Excellent ! Voici mes meilleures trouvailles :"
            ],
            'distance_info': [
                "à seulement {distance}",
                "à {distance} de toi",
                "situé(e) à {distance}",
                "à {distance} de ta position"
            ],
            'status_open': [
                "✅ **OUVERT** - Parfait pour y aller maintenant !",
                "✅ **OUVERT** - Tu peux y aller tout de suite !",
                "✅ **OUVERT** - Idéal pour une visite immédiate !",
                "✅ **OUVERT** - Prêt à t'accueillir !"
            ],
            'status_closed': [
                "❌ **FERMÉ** - Mais ça vaut le détour !",
                "❌ **FERMÉ** - À retenir pour plus tard !",
                "❌ **FERMÉ** - Mais excellent quand c'est ouvert !",
                "❌ **FERMÉ** - À programmer pour une prochaine fois !"
            ],
            'verified': [
                "✓ Vérifié - Tu peux y aller les yeux fermés !",
                "✓ Vérifié - Qualité garantie !",
                "✓ Vérifié - Recommandé par la communauté !",
                "✓ Vérifié - Fiable et de confiance !"
            ],
            'rating': [
                "⭐ {rating}/5 - Excellent choix !",
                "⭐ {rating}/5 - Très bien noté !",
                "⭐ {rating}/5 - Qualité reconnue !",
                "⭐ {rating}/5 - Apprécié par la communauté !"
            ],
            'contact_info': [
                "📞 Téléphone: {phone}",
                "💬 WhatsApp: {whatsapp}",
                "📧 Email: {email}",
                "🌐 Site web: {website}"
            ],
            'hours_info': [
                "🕒 Horaires: {hours}",
                "🕒 Ouvert: {hours}",
                "🕒 Disponible: {hours}",
                "🕒 Fonctionne: {hours}"
            ],
            'directions': [
                "🗺️ Veux-tu que je te donne l'itinéraire ?",
                "🗺️ Je peux te guider jusqu'à {name} !",
                "🗺️ Besoin d'aide pour y aller ?",
                "🗺️ Je t'accompagne jusqu'à {name} !"
            ],
            'more_options': [
                "Veux-tu voir les autres options ?",
                "Intéressé(e) par les autres {type_activity} ?",
                "Je peux te montrer les {count-1} autres !",
                "D'autres {type_activity} t'intéressent ?"
            ],
            'suggestions': [
                "💡 Basé sur tes recherches, je peux aussi te suggérer des activités similaires !",
                "💡 Je connais d'autres endroits qui pourraient te plaire !",
                "💡 Veux-tu que je te propose des alternatives ?",
                "💡 J'ai d'autres idées qui pourraient t'intéresser !"
            ],
            'emergency': [
                "🚨 URGENCE détectée ! Voici les services d'urgence les plus proches :",
                "🚨 Je comprends que c'est urgent ! Voici les options immédiates :",
                "🚨 Situation d'urgence ! Je te trouve les services les plus rapides :",
                "🚨 Urgent ! Voici les lieux qui peuvent t'aider tout de suite :"
            ]
        }

    def preprocess_query(self, query: str) -> str:
        """Clean and normalize the query"""
        query = query.lower().strip()
        query = re.sub(r'\s+', ' ', query)
        return query

    def classify_intent(self, query: str) -> str:
        """Classify the user's intent"""
        query = self.preprocess_query(query)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return intent
        
        return 'search_place'

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query"""
        query = self.preprocess_query(query)
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    entities[entity_type] = match.group(0)
                    break
        
        return entities

    def generate_sql_query(self, db: Session, search_request: SearchRequest, intent: str, entities: Dict[str, Any]) -> Tuple[str, Dict]:
        """Generate SQL query based on intent and entities"""
        base_query = """
        SELECT 
            a.id,
            a.name,
            a.description,
            a.address,
            a.phone_number,
            a.whatsapp_number,
            a.email,
            a.website,
            a.opening_hours,
            a.price_level,
            a.rating,
            a.review_count,
            a.is_verified,
            a.is_active,
            ST_X(a.location) as latitude,
            ST_Y(a.location) as longitude,
            c.name as category_name,
            at.name as activity_type_name,
            ST_Distance(
                ST_GeogFromText('POINT(' || :longitude || ' ' || :latitude || ')'),
                a.location
            ) as distance
        FROM activities a
        LEFT JOIN categories c ON a.category_id = c.id
        LEFT JOIN activity_types at ON a.activity_type_id = at.id
        WHERE a.is_active = true
        """
        
        params = {
            'latitude': search_request.latitude,
            'longitude': search_request.longitude
        }
        
        conditions = []
        
        # Filter by service type if specified
        if 'service_type' in entities:
            service_type = entities['service_type']
            conditions.append("(c.name ILIKE :service_type OR at.name ILIKE :service_type)")
            params['service_type'] = f"%{service_type}%"
        
        # Filter by service item if specified
        if 'service_item' in entities:
            service_item = entities['service_item']
            conditions.append("(a.description ILIKE :service_item OR a.name ILIKE :service_item)")
            params['service_item'] = f"%{service_item}%"
        
        # Filter by food item if specified
        if 'food_item' in entities:
            food_item = entities['food_item']
            conditions.append("(a.description ILIKE :food_item OR a.name ILIKE :food_item)")
            params['food_item'] = f"%{food_item}%"
        
        # Filter by price level if specified
        if 'price_level' in entities:
            price_level = entities['price_level']
            if 'pas cher' in price_level or 'bon marché' in price_level or 'économique' in price_level:
                conditions.append("a.price_level <= 2")
            elif 'cher' in price_level or 'coûteux' in price_level or 'luxueux' in price_level:
                conditions.append("a.price_level >= 3")
        
        # Filter by quality level if specified
        if 'quality_level' in entities:
            quality_level = entities['quality_level']
            if 'excellent' in quality_level or 'bon' in quality_level or 'recommandé' in quality_level:
                conditions.append("a.rating >= 4.0")
            elif 'mauvais' in quality_level or 'terrible' in quality_level:
                conditions.append("a.rating < 3.0")
        
        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # Add distance filter
        if search_request.radius:
            base_query += " AND ST_DWithin(a.location, ST_GeogFromText('POINT(' || :longitude || ' ' || :latitude || ')'), :radius)"
            params['radius'] = search_request.radius
        
        # Add ordering
        if intent == 'emergency':
            base_query += " ORDER BY a.rating DESC, distance ASC"
        else:
            base_query += " ORDER BY distance ASC, a.rating DESC"
        
        # Add limit
        base_query += " LIMIT :limit"
        params['limit'] = search_request.limit or 10
        
        return base_query, params

    def search(self, db: Session, search_request: SearchRequest) -> Dict[str, Any]:
        """Main search method using the new database structure"""
        import time
        start_time = time.time()
        
        # Preprocess query
        processed_query = self.preprocess_query(search_request.query)
        
        # Classify intent and extract entities
        intent = self.classify_intent(processed_query)
        entities = self.extract_entities(processed_query)
        
        # Generate SQL query
        sql_query, params = self.generate_sql_query(db, search_request, intent, entities)
        
        # Execute query
        try:
            result = db.execute(text(sql_query), params)
            activities = []
            
            for row in result:
                activity = Activity()
                activity.id = row.id
                activity.name = row.name
                activity.description = row.description
                activity.address = row.address
                activity.phone_number = row.phone_number
                activity.whatsapp_number = row.whatsapp_number
                activity.email = row.email
                activity.website = row.website
                activity.opening_hours = row.opening_hours
                activity.price_level = row.price_level
                activity.rating = row.rating
                activity.review_count = row.review_count
                activity.is_verified = row.is_verified
                activity.is_active = row.is_active
                activity.latitude = row.latitude
                activity.longitude = row.longitude
                activity.category_name = row.category_name
                activity.activity_type_name = row.activity_type_name
                activity.distance = row.distance
                activities.append(activity)
            
        except Exception as e:
            print(f"Error executing query: {e}")
            activities = []
        
        # Log search
        try:
            search_log = SearchLog(
                query=search_request.query,
                processed_query=processed_query,
                intent=intent,
                entities=json.dumps(entities),
                results_count=len(activities),
                response_time=time.time() - start_time,
                user_id=search_request.user_id,
                latitude=search_request.latitude,
                longitude=search_request.longitude
            )
            db.add(search_log)
            db.commit()
        except Exception as e:
            print(f"Error logging search: {e}")
        
        return {
            "query": search_request.query,
            "processed_query": processed_query,
            "intent": intent,
            "entities": entities,
            "activities": activities,
            "total_results": len(activities),
            "response_time": time.time() - start_time
        }