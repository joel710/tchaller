"""
Service de gestion des activités
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import Activity, Category, ActivityType
from backend.schemas.activities import ActivityCreate, ActivityUpdate, ActivityResponse
from geoalchemy2 import functions as gf

class ActivityService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_activity(self, activity_data: ActivityCreate, owner_id: int) -> Activity:
        """Créer une nouvelle activité"""
        # Créer le point géographique
        location = f"POINT({activity_data.longitude} {activity_data.latitude})"
        
        activity = Activity(
            name=activity_data.name,
            description=activity_data.description,
            address=activity_data.address,
            location=location,
            phone_number=activity_data.phone_number,
            whatsapp_number=activity_data.whatsapp_number,
            email=activity_data.email,
            website=activity_data.website,
            opening_hours=activity_data.opening_hours,
            price_level=activity_data.price_level,
            category_id=activity_data.category_id,
            activity_type_id=activity_data.activity_type_id,
            zone_id=activity_data.zone_id,
            owner_id=owner_id
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    async def get_activity(self, activity_id: int) -> Optional[Activity]:
        """Obtenir une activité par ID"""
        return self.db.query(Activity).filter(Activity.id == activity_id).first()
    
    async def update_activity(self, activity_id: int, activity_data: ActivityUpdate) -> Optional[Activity]:
        """Mettre à jour une activité"""
        activity = await self.get_activity(activity_id)
        if not activity:
            return None
        
        # Mettre à jour les champs fournis
        for field, value in activity_data.dict(exclude_unset=True).items():
            if field in ["latitude", "longitude"] and value is not None:
                # Mettre à jour la localisation
                if activity_data.latitude and activity_data.longitude:
                    activity.location = f"POINT({activity_data.longitude} {activity_data.latitude})"
            else:
                setattr(activity, field, value)
        
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    async def delete_activity(self, activity_id: int) -> bool:
        """Supprimer une activité (soft delete)"""
        activity = await self.get_activity(activity_id)
        if not activity:
            return False
        
        activity.is_active = False
        self.db.commit()
        
        return True
    
    async def get_activities_by_owner(self, owner_id: int, limit: int = 20, offset: int = 0) -> List[Activity]:
        """Obtenir les activités d'un propriétaire"""
        return self.db.query(Activity)\
            .filter(Activity.owner_id == owner_id)\
            .filter(Activity.is_active == True)\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    async def get_categories(self) -> List[Category]:
        """Obtenir toutes les catégories"""
        return self.db.query(Category).filter(Category.is_active == True).all()
    
    async def get_activity_types(self, category_id: Optional[int] = None) -> List[ActivityType]:
        """Obtenir les types d'activités"""
        query = self.db.query(ActivityType).filter(ActivityType.is_active == True)
        
        if category_id:
            query = query.filter(ActivityType.category_id == category_id)
        
        return query.all()