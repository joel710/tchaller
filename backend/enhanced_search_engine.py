import re
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from geoalchemy2 import functions as gf
from .new_models import Activity, Category, ActivityType, Zone, User, Review, Media
from .schemas import SearchRequest
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
        
        # Mapping des types d'activités vers les catégories
        self.activity_type_mapping = {
            'restaurant': 'Restaurant',
            'maquis': 'Restaurant',
            'bar': 'Bar',
            'café': 'Café',
            'boutique': 'Boutique',
            'magasin': 'Magasin',
            'pharmacie': 'Pharmacie',
            'hôpital': 'Hôpital',
            'clinique': 'Clinique',
            'école': 'École',
            'université': 'Université',
            'banque': 'Banque',
            'garage': 'Garage',
            'coiffure': 'Coiffure',
            'centre.*jeux': 'Centre de jeux',
            'cinéma': 'Cinéma',
            'théâtre': 'Théâtre',
            'église': 'Église',
            'mosquée': 'Mosquée',
            'station.*service': 'Station-service',
            'laboratoire': 'Laboratoire',
            'centre.*formation': 'Centre de formation',
            'tribunal': 'Tribunal',
            'mairie': 'Mairie',
            'préfecture': 'Préfecture',
            'ong': 'ONG',
            'association': 'Association'
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
        # Remove extra spaces
        query = re.sub(r'\s+', ' ', query)
        return query

    def classify_intent(self, query: str) -> str:
        """Classify the user's intent"""
        query = self.preprocess_query(query)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return intent
        
        return 'search_place'  # Default intent

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

    def generate_sql_query(self, db: Session, search_request: SearchRequest, intent: str, entities: Dict[str, Any]) -> str:
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
        
        # Filter by activity type if specified
        if 'service_type' in entities:
            service_type = entities['service_type']
            for activity_type, category_name in self.activity_type_mapping.items():
                if re.search(activity_type, service_type):
                    conditions.append("(c.name ILIKE :category_name OR at.name ILIKE :activity_type)")
                    params['category_name'] = f"%{category_name}%"
                    params['activity_type'] = f"%{service_type}%"
                    break
        
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
        
        # Filter by time constraint
        if 'time_constraint' in entities:
            time_constraint = entities['time_constraint']
            if 'maintenant' in time_constraint or 'ce soir' in time_constraint or 'aujourd\'hui' in time_constraint:
                conditions.append("a.is_active = true")  # Only active activities
        
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

    def rank_results(self, activities: List[Activity], intent: str, entities: Dict[str, Any]) -> List[Activity]:
        """Rank search results by relevance"""
        if not activities:
            return activities
        
        for activity in activities:
            score = 0.0
            
            # Base score from rating
            if hasattr(activity, 'rating') and activity.rating:
                score += activity.rating * 0.3
            
            # Distance score (closer is better)
            if hasattr(activity, 'distance') and activity.distance:
                distance_km = activity.distance / 1000
                if distance_km < 1:
                    score += 0.4
                elif distance_km < 5:
                    score += 0.3
                elif distance_km < 10:
                    score += 0.2
                else:
                    score += 0.1
            
            # Verification bonus
            if hasattr(activity, 'is_verified') and activity.is_verified:
                score += 0.2
            
            # Review count bonus
            if hasattr(activity, 'review_count') and activity.review_count:
                if activity.review_count > 100:
                    score += 0.1
                elif activity.review_count > 50:
                    score += 0.05
            
            # Intent-specific scoring
            if intent == 'emergency':
                # Prioritize verified and highly rated activities
                if hasattr(activity, 'is_verified') and activity.is_verified:
                    score += 0.3
                if hasattr(activity, 'rating') and activity.rating and activity.rating >= 4.0:
                    score += 0.2
            
            # Entity matching bonus
            if 'service_type' in entities:
                service_type = entities['service_type']
                if hasattr(activity, 'category_name') and activity.category_name:
                    if service_type.lower() in activity.category_name.lower():
                        score += 0.2
                if hasattr(activity, 'activity_type_name') and activity.activity_type_name:
                    if service_type.lower() in activity.activity_type_name.lower():
                        score += 0.2
            
            # Set relevance score
            activity.relevance_score = score
        
        # Sort by relevance score
        return sorted(activities, key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)

    def generate_response(self, activities: List[Activity], intent: str, entities: Dict[str, Any]) -> str:
        """Generate a human-like, conversational response"""
        import random
        
        if not activities:
            return random.choice(self.response_templates['no_results'])
        
        count = len(activities)
        nearest = activities[0]
        
        # Déterminer le type d'activité pour personnaliser la réponse
        activity_type = "endroit"
        if hasattr(nearest, 'category_name') and nearest.category_name:
            activity_type = nearest.category_name.lower()
        elif hasattr(nearest, 'activity_type_name') and nearest.activity_type_name:
            activity_type = nearest.activity_type_name.lower()
        elif 'service_type' in entities:
            activity_type = entities['service_type']
        
        # Gestion des urgences
        if intent == 'emergency':
            response = random.choice(self.response_templates['emergency'])
        else:
            # Réponse de base variée
            if count == 1:
                response = random.choice(self.response_templates['single_result'])
            else:
                template = random.choice(self.response_templates['multiple_results'])
                response = template.format(count=count, type_activity=activity_type)
        
        # Informations sur l'activité la plus proche
        response += f"\n\n**{nearest.name}**"
        
        # Distance avec variété
        if hasattr(nearest, 'distance') and nearest.distance:
            if nearest.distance < 1000:
                distance_text = f"{int(nearest.distance)}m"
            else:
                distance_text = f"{nearest.distance/1000:.1f}km"
            
            distance_template = random.choice(self.response_templates['distance_info'])
            response += f" {distance_template.format(distance=distance_text)}"
        
        # Type d'activité si pertinent
        if hasattr(nearest, 'category_name') and nearest.category_name and nearest.category_name.lower() != activity_type:
            response += f" ({nearest.category_name})"
        elif hasattr(nearest, 'activity_type_name') and nearest.activity_type_name and nearest.activity_type_name.lower() != activity_type:
            response += f" ({nearest.activity_type_name})"
        
        # Statut avec variété
        if hasattr(nearest, 'is_active') and nearest.is_active:
            status_template = random.choice(self.response_templates['status_open'])
            response += f" - {status_template}"
        else:
            status_template = random.choice(self.response_templates['status_closed'])
            response += f" - {status_template}"
        
        # Vérification avec variété
        if hasattr(nearest, 'is_verified') and nearest.is_verified:
            verified_template = random.choice(self.response_templates['verified'])
            response += f" ({verified_template})"
        
        # Évaluation avec variété
        if hasattr(nearest, 'rating') and nearest.rating and nearest.rating > 0:
            rating_template = random.choice(self.response_templates['rating'])
            rating_value = f"{nearest.rating:.1f}"
            response += f" - {rating_template.format(rating=rating_value)}"
            if hasattr(nearest, 'review_count') and nearest.review_count and nearest.review_count > 0:
                response += f" ({nearest.review_count} avis)"
        
        # Niveau de prix si pertinent
        if hasattr(nearest, 'price_level') and nearest.price_level:
            price_icons = "€" * nearest.price_level
            response += f" - {price_icons}"
        
        # Informations de contact si demandées
        if 'ask_contact' in intent or 'contact' in entities:
            contact_parts = []
            if hasattr(nearest, 'phone_number') and nearest.phone_number:
                contact_parts.append(f"📞 {nearest.phone_number}")
            if hasattr(nearest, 'whatsapp_number') and nearest.whatsapp_number:
                contact_parts.append(f"💬 {nearest.whatsapp_number}")
            if hasattr(nearest, 'email') and nearest.email:
                contact_parts.append(f"📧 {nearest.email}")
            if hasattr(nearest, 'website') and nearest.website:
                contact_parts.append(f"🌐 {nearest.website}")
            
            if contact_parts:
                response += f"\n\n{', '.join(contact_parts)}"
        
        # Horaires si demandés
        if 'ask_hours' in intent or 'horaires' in entities:
            if hasattr(nearest, 'opening_hours') and nearest.opening_hours:
                try:
                    hours = json.loads(nearest.opening_hours) if isinstance(nearest.opening_hours, str) else nearest.opening_hours
                    hours_text = hours.get('today', 'Non spécifié')
                except:
                    hours_text = nearest.opening_hours
                
                hours_template = random.choice(self.response_templates['hours_info'])
                response += f"\n\n{hours_template.format(hours=hours_text)}"
        
        # Directions si demandées
        if 'ask_directions' in intent or 'itinéraire' in entities:
            directions_template = random.choice(self.response_templates['directions'])
            response += f"\n\n{directions_template.format(name=nearest.name)}"
        
        # Plus d'options si plusieurs résultats
        if count > 1:
            more_options_template = random.choice(self.response_templates['more_options'])
            if '{type_activity}' in more_options_template:
                more_options_template = more_options_template.format(type_activity=activity_type)
            if '{count-1}' in more_options_template:
                more_options_template = more_options_template.replace('{count-1}', str(count-1))
            response += f"\n\n{more_options_template}"
        
        # Suggestions contextuelles
        if count > 0 and random.random() < 0.3:  # 30% de chance d'ajouter des suggestions
            suggestions_template = random.choice(self.response_templates['suggestions'])
            response += f"\n\n{suggestions_template}"
        
        return response

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
        
        # Rank results
        ranked_activities = self.rank_results(activities, intent, entities)
        
        # Generate response
        response = self.generate_response(ranked_activities, intent, entities)
        
        # Log search
        try:
            search_log = SearchLog(
                query=search_request.query,
                processed_query=processed_query,
                intent=intent,
                entities=json.dumps(entities),
                results_count=len(ranked_activities),
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
            "intent": intent,
            "entities": entities,
            "activities": ranked_activities[:search_request.limit or 10],
            "response": response,
            "total_results": len(ranked_activities),
            "response_time": time.time() - start_time
        }