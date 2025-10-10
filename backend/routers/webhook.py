from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db, Merchant, MerchantStatusHistory
from ..schemas import WebhookRequest
import re
from datetime import datetime

router = APIRouter(prefix="/webhook", tags=["webhook"])

@router.post("/status")
async def handle_status_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle status updates from WhatsApp/SMS"""
    try:
        # Parse the webhook data
        form_data = await request.form()
        
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "").strip().upper()
        message_sid = form_data.get("MessageSid", "")
        
        # Extract phone number (remove country code if present)
        phone_number = re.sub(r'^\+?(\d+)', r'\1', from_number)
        
        # Find merchant by phone number
        merchant = db.query(Merchant).filter(
            (Merchant.phone_number == phone_number) | 
            (Merchant.whatsapp_number == phone_number)
        ).first()
        
        if not merchant:
            return {"message": "Merchant not found"}
        
        # Parse status from message
        status = None
        if "OUVERT" in message_body or "OPEN" in message_body:
            status = "OPEN"
        elif "FERMÉ" in message_body or "FERME" in message_body or "CLOSED" in message_body:
            status = "CLOSED"
        else:
            return {"message": "Status not recognized"}
        
        # Update merchant status
        merchant.is_open = (status == "OPEN")
        merchant.updated_at = datetime.utcnow()
        
        # Log status change
        status_history = MerchantStatusHistory(
            merchant_id=merchant.id,
            status=status
        )
        
        db.add(status_history)
        db.commit()
        
        return {
            "message": "Status updated successfully",
            "merchant_id": merchant.id,
            "status": status,
            "is_open": merchant.is_open
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@router.post("/test-status")
async def test_status_update(
    merchant_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Test endpoint to update merchant status"""
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    # Update status
    merchant.is_open = (status.upper() == "OPEN")
    merchant.updated_at = datetime.utcnow()
    
    # Log status change
    status_history = MerchantStatusHistory(
        merchant_id=merchant.id,
        status=status.upper()
    )
    
    db.add(status_history)
    db.commit()
    
    return {
        "message": "Status updated successfully",
        "merchant_id": merchant.id,
        "status": status.upper(),
        "is_open": merchant.is_open
    }