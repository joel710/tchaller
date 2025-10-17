"""
Service de notifications
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import Notification, User

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_notification(
        self, 
        user_id: int, 
        title: str, 
        message: str, 
        notification_type: str,
        data: Optional[dict] = None
    ) -> Notification:
        """Créer une notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data or {}
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    async def get_user_notifications(
        self, 
        user_id: int, 
        limit: int = 20, 
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """Obtenir les notifications d'un utilisateur"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc())\
                   .offset(offset)\
                   .limit(limit)\
                   .all()
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Marquer une notification comme lue"""
        notification = self.db.query(Notification)\
            .filter(Notification.id == notification_id)\
            .filter(Notification.user_id == user_id)\
            .first()
        
        if not notification:
            return False
        
        notification.is_read = True
        self.db.commit()
        
        return True
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """Marquer toutes les notifications comme lues"""
        count = self.db.query(Notification)\
            .filter(Notification.user_id == user_id)\
            .filter(Notification.is_read == False)\
            .update({"is_read": True})
        
        self.db.commit()
        return count