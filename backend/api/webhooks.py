"""
Routes pour les webhooks
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Webhook, WebhookLog
from schemas.common import MessageResponse
import json

router = APIRouter()

@router.post("/status", response_model=MessageResponse)
async def webhook_status(request: Request, db: Session = Depends(get_db)):
    """Webhook pour les mises à jour de statut (WhatsApp/SMS)"""
    try:
        # Récupérer les données du webhook
        data = await request.json()
        
        # Log du webhook
        webhook_log = WebhookLog(
            webhook_id=1,  # ID du webhook de statut
            payload=data,
            response_status=200,
            response_body="OK"
        )
        db.add(webhook_log)
        db.commit()
        
        # Traiter le webhook (logique métier)
        # Ici, on pourrait mettre à jour le statut d'une activité
        # basé sur le message reçu
        
        return MessageResponse(
            message="Webhook traité avec succès",
            success=True
        )
        
    except Exception as e:
        # Log de l'erreur
        webhook_log = WebhookLog(
            webhook_id=1,
            payload={},
            response_status=500,
            error_message=str(e)
        )
        db.add(webhook_log)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement du webhook: {str(e)}"
        )

@router.post("/test-status", response_model=MessageResponse)
async def test_webhook_status(request: Request, db: Session = Depends(get_db)):
    """Test du webhook de statut"""
    try:
        data = await request.json()
        
        # Simuler une mise à jour de statut
        print(f"📱 Webhook de test reçu: {data}")
        
        return MessageResponse(
            message="Webhook de test traité avec succès",
            success=True
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors du test: {str(e)}"
        )