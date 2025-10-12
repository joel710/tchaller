"""
Moteur de recherche conversationnel simplifié sans scikit-learn
Compatible avec le déploiement Render
"""

import re
import random
from typing import List, Dict, Any, Optional
from backend.database.models import Activity, Category, ActivityType
from backend.schemas.search import SearchRequest
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import math

class SimpleConversationalSearchEngine:
    """Moteur de recherche conversationnel simplifié"""
    
    def __init__(self):
        # Patterns d'intent simplifiés
        self.intent_patterns = {
            'search_place': [
                r'cherche|trouve|où|localiser|près|proche',
                r'restaurant|hôpital|pharmacie|garage|école|banque',
                r'disponible|ouvert|fermé'
            ],
            'ask_directions': [
                r'comment.*aller|itinéraire|direction|chemin',
                r'où.*se.*trouve|localisation|adresse'
            ],
            'emergency': [
                r'urgence|urgent|sos|aide|secours',
                r'hôpital.*urgence|pompiers|police'
            ],
            'find_by_service': [
                r'service|besoin|requis|nécessaire',
                r'peux.*faire|peut.*faire|capable'
            ],
            'compare_places': [
                r'comparer|différence|mieux|meilleur',
                r'vs|versus|ou.*ou'
            ],
            'ask_hours': [
                r'heures|horaire|ouvert|fermé',
                r'quand.*ouvre|quand.*ferme'
            ],
            'ask_contact': [
                r'contact|téléphone|appeler|numéro',
                r'email|mail|écrire'
            ],
            'ask_rating': [
                r'note|évaluation|avis|rating',
                r'qualité|bon|mauvais|recommandé'
            ]
        }
        
        # Patterns d'entités simplifiés
        self.entity_patterns = {
            'service_type': [
                r'restaurant|maquis|bar|café|hôtel',
                r'hôpital|clinique|pharmacie|laboratoire',
                r'garage|station.*service|mécanicien',
                r'école|université|collège|lycée',
                r'banque|assurance|microfinance',
                r'église|mosquée|temple|chapelle',
                r'mairie|préfecture|tribunal|administration',
                r'cinéma|théâtre|centre.*jeux|loisir'
            ],
            'location': [
                r'proche|près|à.*côté|voisinage',
                r'centre.*ville|centre|downtown',
                r'quartier|zone|secteur'
            ],
            'time_constraint': [
                r'maintenant|immédiatement|urgent',
                r'aujourd\'hui|ce.*soir|demain',
                r'ouvert|fermé|disponible'
            ],
            'price_level': [
                r'cher|coûteux|luxe|premium',
                r'pas.*cher|économique|bon.*marché',
                r'gratuit|gratis|libre'
            ]
        }
        
        # Templates de réponses variés
        self.response_templates = {
            'greeting': [
                "Salut ! Je suis là pour vous aider à trouver ce que vous cherchez. Que puis-je faire pour vous ?",
                "Bonjour ! Comment puis-je vous assister dans votre recherche ?",
                "Hey ! Je suis votre assistant pour découvrir les meilleures activités. Que cherchez-vous ?"
            ],
            'search_results': [
                "Parfait ! J'ai trouvé {count} {activity_type} qui pourraient vous intéresser :",
                "Excellent ! Voici {count} {activity_type} dans votre zone :",
                "Super ! J'ai localisé {count} {activity_type} pour vous :"
            ],
            'no_results': [
                "Désolé, je n'ai pas trouvé d'{activity_type} dans cette zone. Voulez-vous essayer une recherche plus large ?",
                "Aucun {activity_type} trouvé pour le moment. Essayons autre chose ?",
                "Pas de {activity_type} disponible ici. Cherchons autre chose ?"
            ],
            'single_result': [
                "J'ai trouvé un {activity_type} parfait pour vous :",
                "Voici exactement ce que vous cherchez :",
                "Parfait ! Un {activity_type} idéal :"
            ],
            'multiple_results': [
                "Voici plusieurs {activity_type} qui correspondent à votre recherche :",
                "J'ai trouvé plusieurs options intéressantes :",
                "Plusieurs {activity_type} disponibles :"
            ],
            'distance': [
                "à seulement {distance:.1f} km",
                "à {distance:.1f} km de vous",
                "situé à {distance:.1f} km"
            ],
            'rating': [
                "avec une note de {rating}/5",
                "évalué {rating}/5",
                "noté {rating}/5"
            ],
            'contact': [
                "Contact : {phone}",
                "Téléphone : {phone}",
                "Appelez au {phone}"
            ],
            'hours': [
                "Ouvert {hours}",
                "Horaires : {hours}",
                "Disponible {hours}"
            ],
            'suggestions': [
                "Voulez-vous que je vous suggère autre chose ?",
                "Besoin d'autres recommandations ?",
                "Cherchons autre chose ?"
            ]
        }
    
    def classify_intent(self, query: str) -> str:
        """Classifie l'intent de la requête"""
        query_lower = query.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return 'search_place'  # Intent par défaut
    
    def extract_entities(self, query: str) -> Dict[str, str]:
        """Extrait les entités de la requête"""
        entities = {}
        query_lower = query.lower()
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query_lower)
                if match:
                    entities[entity_type] = match.group(0)
                    break
        
        return entities
    
    def generate_sql_query(self, entities: Dict[str, str], user_lat: float = None, user_lon: float = None) -> str:
        """Génère une requête SQL basée sur les entités extraites"""
        base_query = """
        SELECT a.*, c.name as category_name, at.name as activity_type_name,
               ST_X(a.location) as latitude, ST_Y(a.location) as longitude
        FROM activities a
        LEFT JOIN categories c ON a.category_id = c.id
        LEFT JOIN activity_types at ON a.activity_type_id = at.id
        WHERE a.is_active = true
        """
        
        conditions = []
        params = {}
        
        # Filtre par type de service
        if 'service_type' in entities:
            service_type = entities['service_type']
            conditions.append("""
                (LOWER(a.name) LIKE :service_type 
                 OR LOWER(a.description) LIKE :service_type
                 OR LOWER(c.name) LIKE :service_type
                 OR LOWER(at.name) LIKE :service_type)
            """)
            params['service_type'] = f'%{service_type}%'
        
        # Filtre par contrainte de temps
        if 'time_constraint' in entities:
            time_constraint = entities['time_constraint']
            if 'ouvert' in time_constraint or 'disponible' in time_constraint:
                conditions.append("a.is_open = true")
        
        # Ajouter les conditions
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # Tri par distance si coordonnées utilisateur disponibles
        if user_lat and user_lon:
            base_query += f"""
            ORDER BY ST_Distance(a.location, ST_SetSRID(ST_MakePoint({user_lon}, {user_lat}), 4326))
            """
        else:
            base_query += " ORDER BY a.rating DESC, a.created_at DESC"
        
        base_query += " LIMIT 10"
        
        return base_query, params
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcule la distance entre deux points (formule de Haversine)"""
        R = 6371  # Rayon de la Terre en km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def generate_response(self, query: str, results: List[Activity], entities: Dict[str, str]) -> str:
        """Génère une réponse conversationnelle"""
        intent = self.classify_intent(query)
        response = ""
        
        # Déterminer le type d'activité
        activity_type = entities.get('service_type', 'activité')
        
        if not results:
            # Aucun résultat
            no_results_template = random.choice(self.response_templates['no_results'])
            response = no_results_template.format(activity_type=activity_type)
        else:
            # Résultats trouvés
            count = len(results)
            
            if count == 1:
                template = random.choice(self.response_templates['single_result'])
            else:
                template = random.choice(self.response_templates['multiple_results'])
            
            response = template.format(activity_type=activity_type)
            response += "\n\n"
            
            # Ajouter les résultats
            for i, activity in enumerate(results[:5], 1):
                response += f"{i}. **{activity.name}**\n"
                
                if activity.description:
                    response += f"   {activity.description[:100]}...\n"
                
                if activity.rating:
                    rating_template = random.choice(self.response_templates['rating'])
                    response += f"   {rating_template.format(rating=activity.rating)}\n"
                
                if activity.phone:
                    contact_template = random.choice(self.response_templates['contact'])
                    response += f"   {contact_template.format(phone=activity.phone)}\n"
                
                if activity.business_hours:
                    hours_template = random.choice(self.response_templates['hours'])
                    response += f"   {hours_template.format(hours=activity.business_hours)}\n"
                
                response += "\n"
        
        # Ajouter des suggestions
        suggestions_template = random.choice(self.response_templates['suggestions'])
        response += f"\n{suggestions_template}"
        
        return response
    
    def search(self, request: SearchRequest, db: Session) -> Dict[str, Any]:
        """Effectue une recherche conversationnelle"""
        try:
            # Classifier l'intent et extraire les entités
            intent = self.classify_intent(request.query)
            entities = self.extract_entities(request.query)
            
            # Générer la requête SQL
            sql_query, params = self.generate_sql_query(
                entities, 
                request.user_latitude, 
                request.user_longitude
            )
            
            # Exécuter la requête
            result = db.execute(text(sql_query), params)
            activities = []
            
            for row in result:
                activity = Activity(
                    id=row.id,
                    name=row.name,
                    description=row.description,
                    location=f"POINT({row.longitude} {row.latitude})",
                    phone=row.phone,
                    email=row.email,
                    website=row.website,
                    rating=row.rating,
                    business_hours=row.business_hours,
                    is_active=row.is_active,
                    category_id=row.category_id,
                    activity_type_id=row.activity_type_id
                )
                activities.append(activity)
            
            # Générer la réponse conversationnelle
            response = self.generate_response(request.query, activities, entities)
            
            return {
                "query": request.query,
                "intent": intent,
                "entities": entities,
                "results": activities,
                "response": response,
                "count": len(activities)
            }
            
        except Exception as e:
            return {
                "query": request.query,
                "intent": "error",
                "entities": {},
                "results": [],
                "response": f"Désolé, une erreur s'est produite lors de la recherche : {str(e)}",
                "count": 0,
                "error": str(e)
            }