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
                r'trouve.*endroit', r'cherche.*endroit', r'où.*manger', r'où.*boire',
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin'
            ],
            'find_open_now': [
                r'ouvert.*maintenant', r'ouvert.*ce soir', r'ouvert.*aujourd\'hui',
                r'qui.*ouvert', r'fermé', r'disponible'
            ],
            'find_by_dish': [
                r'manger.*porc', r'manger.*poulet', r'manger.*poisson', r'manger.*riz',
                r'plat.*porc', r'plat.*poulet', r'cuisine.*africaine', r'cuisine.*locale'
            ],
            'ask_opening_hours': [
                r'horaires', r'heures.*ouverture', r'ferme.*à', r'ouvre.*à'
            ],
            'ask_contact': [
                r'numéro', r'téléphone', r'whatsapp', r'contact', r'appeler'
            ]
        }
        
        self.entity_patterns = {
            'food_item': [
                r'porc', r'poulet', r'poisson', r'riz', r'fufu', r'attiéké', r'alloco'
            ],
            'service_type': [
                r'restaurant', r'maquis', r'bar', r'café', r'boutique', r'magasin', r'pharmacie'
            ],
            'time_constraint': [
                r'ce soir', r'aujourd\'hui', r'maintenant', r'après-midi', r'matin'
            ],
            'location': [
                r'près.*moi', r'proche', r'ici', r'quartier', r'centre.*ville'
            ],
            'price_level': [
                r'pas cher', r'bon marché', r'cher', r'coûteux', r'économique'
            ]
        }
        
        self.category_mapping = {
            'restaurant': 'Restaurant',
            'maquis': 'Restaurant',
            'bar': 'Bar',
            'café': 'Café',
            'boutique': 'Boutique',
            'magasin': 'Magasin',
            'pharmacie': 'Pharmacie'
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
        """Generate a human-like response"""
        if not merchants:
            return "Désolé, je n'ai trouvé aucun endroit correspondant à votre recherche. Essayez avec d'autres mots-clés ou élargissez votre zone de recherche."
        
        count = len(merchants)
        nearest = merchants[0]
        
        # Base response
        if count == 1:
            response = f"J'ai trouvé 1 endroit parfait pour vous !"
        else:
            response = f"J'ai trouvé {count} endroits qui correspondent à votre recherche."
        
        # Add nearest merchant info
        response += f"\n\nLe plus proche est **{nearest.name}**"
        
        if hasattr(nearest, 'distance') and nearest.distance:
            if nearest.distance < 1000:
                response += f" à {int(nearest.distance)}m"
            else:
                response += f" à {nearest.distance/1000:.1f}km"
        
        # Add status info
        if nearest.is_open:
            response += " - ✅ **OUVERT**"
        else:
            response += " - ❌ **FERMÉ**"
        
        # Add verification status
        if nearest.is_verified:
            response += " (✓ Vérifié)"
        
        # Add rating if available
        if nearest.rating > 0:
            response += f" - ⭐ {nearest.rating:.1f}/5"
        
        # Add contact info if requested
        if 'ask_contact' in intent or 'contact' in entities:
            if nearest.phone_number:
                response += f"\n\n📞 Téléphone: {nearest.phone_number}"
            if nearest.whatsapp_number:
                response += f"\n💬 WhatsApp: {nearest.whatsapp_number}"
        
        # Add opening hours if requested
        if 'ask_opening_hours' in intent or 'horaires' in entities:
            if nearest.opening_hours:
                try:
                    hours = json.loads(nearest.opening_hours)
                    response += f"\n\n🕒 Horaires: {hours.get('today', 'Non spécifié')}"
                except:
                    response += f"\n\n🕒 Horaires: {nearest.opening_hours}"
        
        # Add more options if multiple results
        if count > 1:
            response += f"\n\nVoulez-vous voir les {count-1} autres options ?"
        
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