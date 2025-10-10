import re
import json
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from geoalchemy2 import functions as gf
from .database import Merchant, Category, SearchLog
from .schemas import SearchRequest, Merchant as MerchantSchema
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

class ConversationalSearchEngine:
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
        
        self.category_mapping = {
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
        """Classify the intent of the query"""
        query = self.preprocess_query(query)
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        return 'search_place'  # Default intent

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from the query"""
        query = self.preprocess_query(query)
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    entities[entity_type] = match.group(0)
                    break
        
        return entities

    def generate_sql_query(self, search_request: SearchRequest, entities: Dict[str, Any]) -> Tuple[str, Dict]:
        """Generate SQL query based on search request and entities"""
        base_query = """
        SELECT m.*, c.name as category_name,
        ST_Distance(m.location, ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)) as distance
        FROM merchants m
        LEFT JOIN categories c ON m.category_id = c.id
        WHERE 1=1
        """
        
        params = {
            'latitude': search_request.latitude,
            'longitude': search_request.longitude
        }
        
        # Add radius filter
        if search_request.radius:
            base_query += """
            AND ST_DWithin(m.location, ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), :radius)
            """
            params['radius'] = search_request.radius
        
        # Add category filter
        if search_request.category_id:
            base_query += " AND m.category_id = :category_id"
            params['category_id'] = search_request.category_id
        elif 'service_type' in entities:
            category_name = self.category_mapping.get(entities['service_type'], 'Restaurant')
            base_query += " AND c.name ILIKE :category_name"
            params['category_name'] = f"%{category_name}%"
        
        # Add price level filter
        if search_request.price_level:
            base_query += " AND m.price_level = :price_level"
            params['price_level'] = search_request.price_level
        elif 'price_level' in entities:
            if 'pas cher' in entities['price_level'] or 'bon marché' in entities['price_level']:
                params['price_level'] = 1
            elif 'cher' in entities['price_level'] or 'coûteux' in entities['price_level']:
                params['price_level'] = 3
            else:
                params['price_level'] = 2
            base_query += " AND m.price_level = :price_level"
        
        # Add open now filter
        if search_request.is_open_now:
            base_query += " AND m.is_open = true"
        elif 'time_constraint' in entities:
            if any(word in entities['time_constraint'] for word in ['ce soir', 'maintenant', 'aujourd\'hui']):
                base_query += " AND m.is_open = true"
        
        # Add text search
        if search_request.query:
            base_query += """
            AND (m.name ILIKE :query OR m.description ILIKE :query)
            """
            params['query'] = f"%{search_request.query}%"
        
        # Order by distance and rating
        base_query += """
        ORDER BY 
            CASE WHEN m.is_open = true THEN 0 ELSE 1 END,
            m.is_verified DESC,
            distance ASC,
            m.rating DESC
        LIMIT 20
        """
        
        return base_query, params

    def rank_results(self, merchants: List[Merchant], entities: Dict[str, Any]) -> List[Merchant]:
        """Rank merchants based on relevance"""
        if not merchants:
            return merchants
        
        # Calculate relevance scores
        for merchant in merchants:
            score = 0
            
            # Distance score (closer is better)
            if hasattr(merchant, 'distance') and merchant.distance:
                if merchant.distance < 500:
                    score += 100
                elif merchant.distance < 1000:
                    score += 80
                elif merchant.distance < 2000:
                    score += 60
                else:
                    score += 40
            
            # Verification bonus
            if merchant.is_verified:
                score += 50
            
            # Open status bonus
            if merchant.is_open:
                score += 30
            
            # Rating bonus
            score += merchant.rating * 10
            
            # Review count bonus
            score += min(merchant.review_count, 100) * 0.5
            
            # Store the score for sorting
            merchant.relevance_score = score
        
        # Sort by relevance score
        return sorted(merchants, key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)

    def generate_response(self, merchants: List[Merchant], intent: str, entities: Dict[str, Any]) -> str:
        """Generate a human-like, conversational response"""
        import random
        
        if not merchants:
            return random.choice(self.response_templates['no_results'])
        
        count = len(merchants)
        nearest = merchants[0]
        
        # Déterminer le type d'activité pour personnaliser la réponse
        activity_type = "endroit"
        if hasattr(nearest, 'category_name') and nearest.category_name:
            activity_type = nearest.category_name.lower()
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
        
        # Statut avec variété
        if nearest.is_open:
            status_template = random.choice(self.response_templates['status_open'])
            response += f" - {status_template}"
        else:
            status_template = random.choice(self.response_templates['status_closed'])
            response += f" - {status_template}"
        
        # Vérification avec variété
        if nearest.is_verified:
            verified_template = random.choice(self.response_templates['verified'])
            response += f" ({verified_template})"
        
        # Évaluation avec variété
        if nearest.rating > 0:
            rating_template = random.choice(self.response_templates['rating'])
            rating_value = f"{nearest.rating:.1f}"
            response += f" - {rating_template.format(rating=rating_value)}"
            if nearest.review_count > 0:
                response += f" ({nearest.review_count} avis)"
        
        # Niveau de prix si pertinent
        if hasattr(nearest, 'price_level') and nearest.price_level:
            price_icons = "€" * nearest.price_level
            response += f" - {price_icons}"
        
        # Informations de contact si demandées
        if 'ask_contact' in intent or 'contact' in entities:
            contact_parts = []
            if nearest.phone_number:
                contact_parts.append(f"📞 {nearest.phone_number}")
            if nearest.whatsapp_number:
                contact_parts.append(f"💬 {nearest.whatsapp_number}")
            if hasattr(nearest, 'email') and nearest.email:
                contact_parts.append(f"📧 {nearest.email}")
            if hasattr(nearest, 'website') and nearest.website:
                contact_parts.append(f"🌐 {nearest.website}")
            
            if contact_parts:
                response += f"\n\n{', '.join(contact_parts)}"
        
        # Horaires si demandés
        if 'ask_hours' in intent or 'horaires' in entities:
            if nearest.opening_hours:
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
        """Main search method"""
        import time
        start_time = time.time()
        
        # Preprocess query
        processed_query = self.preprocess_query(search_request.query)
        
        # Classify intent and extract entities
        intent = self.classify_intent(processed_query)
        entities = self.extract_entities(processed_query)
        
        # Generate SQL query
        sql_query, params = self.generate_sql_query(search_request, entities)
        
        # Execute query
        result = db.execute(text(sql_query), params)
        merchants = []
        
        for row in result:
            merchant_dict = dict(row._mapping)
            merchant = Merchant(**{k: v for k, v in merchant_dict.items() if k in Merchant.__table__.columns})
            merchant.distance = merchant_dict.get('distance')
            merchant.category_name = merchant_dict.get('category_name')
            merchants.append(merchant)
        
        # Rank results
        merchants = self.rank_results(merchants, entities)
        
        # Generate response
        response = self.generate_response(merchants, intent, entities)
        
        # Log search
        search_log = SearchLog(
            query=search_request.query,
            results_count=len(merchants)
        )
        if search_request.latitude and search_request.longitude:
            search_log.location = f"POINT({search_request.longitude} {search_request.latitude})"
        
        db.add(search_log)
        db.commit()
        
        search_time = (time.time() - start_time) * 1000
        
        return {
            "merchants": merchants,
            "total_count": len(merchants),
            "query_processed": processed_query,
            "search_time_ms": search_time,
            "response": response,
            "intent": intent,
            "entities": entities
        }