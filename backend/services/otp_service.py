"""
Service OTP (One-Time Password)
"""
import random
import asyncio
from typing import Dict

class OTPService:
    def __init__(self):
        self.otp_storage: Dict[str, Dict] = {}
    
    async def generate_otp(self, phone_number: str) -> str:
        """Générer un code OTP"""
        otp_code = str(random.randint(100000, 999999))
        
        # Stocker l'OTP (en production, utiliser Redis ou base de données)
        self.otp_storage[phone_number] = {
            "code": otp_code,
            "attempts": 0,
            "created_at": asyncio.get_event_loop().time()
        }
        
        return otp_code
    
    async def send_otp(self, phone_number: str, otp_code: str) -> bool:
        """Envoyer l'OTP (simulation)"""
        # En production, intégrer avec Twilio ou autre service SMS
        print(f"📱 OTP envoyé à {phone_number}: {otp_code}")
        return True
    
    async def verify_otp(self, phone_number: str, otp_code: str) -> bool:
        """Vérifier l'OTP"""
        if phone_number not in self.otp_storage:
            return False
        
        stored_data = self.otp_storage[phone_number]
        
        # Vérifier les tentatives
        if stored_data["attempts"] >= 3:
            return False
        
        # Vérifier l'expiration (5 minutes)
        if asyncio.get_event_loop().time() - stored_data["created_at"] > 300:
            del self.otp_storage[phone_number]
            return False
        
        # Vérifier le code
        if stored_data["code"] == otp_code:
            del self.otp_storage[phone_number]
            return True
        else:
            stored_data["attempts"] += 1
            return False