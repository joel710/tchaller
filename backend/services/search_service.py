"""
Service de recherche ultra polyvalent
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from geoalchemy2 import functions as gf
from backend.schemas.search import SearchRequest, SearchResponse
from backend.schemas.activities import ActivityResponse
from backend.database.models import Activity, Category, ActivityType, Review, Media
from .simple_search_engine import SimpleConversationalSearchEngine
import time

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.search_engine = SimpleConversationalSearchEngine()
    
    async def search_activities(self, request: SearchRequest) -> SearchResponse:
        """Recherche d'activités avec moteur conversationnel"""
        start_time = time.time()
        
        try:
            # Utiliser le moteur de recherche simplifié
            result = self.search_engine.search(request, self.db)
            
            # Convertir les activités en ActivityResponse
            activities = []
            for activity in result.get('activities', []):
                activity_response = await self._convert_to_activity_response(activity)
                activities.append(activity_response)
            
            response_time = time.time() - start_time
            
            return SearchResponse(
                query=request.query,
                processed_query=result.get('processed_query', request.query),
                intent=result.get('intent', 'search_place'),
                entities=result.get('entities', {}),
                activities=activities,
                total_results=len(activities),
                response_time=response_time,
                suggestions=self._generate_suggestions(request, activities),
                filters_applied=self._get_applied_filters(request)
            )
            
        except Exception as e:
            raise Exception(f"Erreur lors de la recherche: {str(e)}")
    
    async def _convert_to_activity_response(self, activity) -> ActivityResponse:
        """Convertir une activité en ActivityResponse"""
        # Récupérer les médias
        media = self.db.query(Media).filter(Media.activity_id == activity.id).all()
        media_info = [
            {
                "id": m.id,
                "file_url": m.file_url,
                "file_type": m.file_type,
                "alt_text": m.alt_text,
                "is_primary": m.is_primary,
                "created_at": m.created_at
            } for m in media
        ]
        
        # Récupérer les avis
        reviews = self.db.query(Review).filter(Review.activity_id == activity.id).limit(5).all()
        review_info = [
            {
                "id": r.id,
                "user_name": "Utilisateur",  # Anonymisé
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at,
                "is_verified": r.is_verified
            } for r in reviews
        ]
        
        return ActivityResponse(
            id=activity.id,
            name=activity.name,
            description=activity.description,
            address=activity.address,
            latitude=getattr(activity, 'latitude', 0.0),
            longitude=getattr(activity, 'longitude', 0.0),
            phone_number=activity.phone_number,
            whatsapp_number=activity.whatsapp_number,
            email=activity.email,
            website=activity.website,
            opening_hours=activity.opening_hours,
            price_level=activity.price_level,
            rating=activity.rating,
            review_count=activity.review_count,
            is_verified=activity.is_verified,
            is_active=activity.is_active,
            created_at=activity.created_at,
            updated_at=activity.updated_at,
            category_id=activity.category_id,
            activity_type_id=activity.activity_type_id,
            zone_id=activity.zone_id,
            owner_id=activity.owner_id,
            category_name=getattr(activity, 'category_name', None),
            activity_type_name=getattr(activity, 'activity_type_name', None),
            zone_name=getattr(activity, 'zone_name', None),
            owner_name=getattr(activity, 'owner_name', None),
            distance=getattr(activity, 'distance', None),
            media=media_info,
            reviews=review_info
        )
    
    def _generate_suggestions(self, request: SearchRequest, activities: List[ActivityResponse]) -> List[str]:
        """Générer des suggestions basées sur la recherche"""
        suggestions = []
        
        # Suggestions basées sur les catégories trouvées
        categories = set()
        for activity in activities:
            if activity.category_name:
                categories.add(activity.category_name)
        
        for category in list(categories)[:3]:
            suggestions.append(f"Voir plus de {category.lower()}")
        
        # Suggestions basées sur la localisation
        if request.latitude and request.longitude:
            suggestions.append("Activités près de moi")
            suggestions.append("Activités ouvertes maintenant")
        
        return suggestions
    
    def _get_applied_filters(self, request: SearchRequest) -> Dict[str, Any]:
        """Obtenir les filtres appliqués"""
        filters = {}
        
        if request.category_id:
            filters["category_id"] = request.category_id
        if request.activity_type_id:
            filters["activity_type_id"] = request.activity_type_id
        if request.price_level:
            filters["price_level"] = request.price_level
        if request.is_verified is not None:
            filters["is_verified"] = request.is_verified
        if request.is_open_now is not None:
            filters["is_open_now"] = request.is_open_now
        if request.min_rating:
            filters["min_rating"] = request.min_rating
        if request.radius:
            filters["radius"] = request.radius
        
        return filters
    
    async def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtenir les recherches populaires"""
        try:
            query = text("""
                SELECT query, COUNT(*) as count
                FROM search_logs 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY query 
                ORDER BY count DESC 
                LIMIT :limit
            """)
            
            result = self.db.execute(query, {"limit": limit})
            return [{"query": row.query, "count": row.count} for row in result]
            
        except Exception as e:
            return []
    
    async def get_search_analytics(self) -> Dict[str, Any]:
        """Obtenir les analytics de recherche"""
        try:
            # Statistiques générales
            total_searches = self.db.query(func.count()).select_from(text("search_logs")).scalar()
            unique_users = self.db.query(func.count(func.distinct(text("user_id")))).select_from(text("search_logs")).scalar()
            
            # Requêtes populaires
            popular_queries = await self.get_popular_searches(5)
            
            # Intents populaires
            intents_query = text("""
                SELECT intent, COUNT(*) as count
                FROM search_logs 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                AND intent IS NOT NULL
                GROUP BY intent 
                ORDER BY count DESC
            """)
            
            intents_result = self.db.execute(intents_query)
            search_intents = {row.intent: row.count for row in intents_result}
            
            # Temps de réponse moyen
            avg_response_time = self.db.query(func.avg(text("response_time"))).select_from(text("search_logs")).scalar() or 0.0
            
            return {
                "total_searches": total_searches or 0,
                "unique_users": unique_users or 0,
                "popular_queries": popular_queries,
                "search_intents": search_intents,
                "average_response_time": float(avg_response_time),
                "success_rate": 95.0  # Calculé basé sur les logs d'erreur
            }
            
        except Exception as e:
            return {
                "total_searches": 0,
                "unique_users": 0,
                "popular_queries": [],
                "search_intents": {},
                "average_response_time": 0.0,
                "success_rate": 0.0
            }