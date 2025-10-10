#!/usr/bin/env python3
"""
Script de test pour l'API Tcha-llé
"""
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_health():
    """Test du endpoint de santé"""
    print("🔍 Test du endpoint de santé...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
            return True
        else:
            print(f"❌ Health check: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check: {e}")
        return False

def test_categories():
    """Test du endpoint des catégories"""
    print("🔍 Test des catégories...")
    try:
        response = requests.get(f"{API_BASE}/categories/")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Catégories: {len(categories)} trouvées")
            for cat in categories[:3]:
                print(f"   - {cat['name']}")
            return True
        else:
            print(f"❌ Catégories: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Catégories: {e}")
        return False

def test_merchants():
    """Test du endpoint des commerces"""
    print("🔍 Test des commerces...")
    try:
        response = requests.get(f"{API_BASE}/merchants/")
        if response.status_code == 200:
            merchants = response.json()
            print(f"✅ Commerces: {len(merchants)} trouvés")
            for merchant in merchants[:3]:
                print(f"   - {merchant['name']} ({'OUVERT' if merchant['is_open'] else 'FERMÉ'})")
            return True
        else:
            print(f"❌ Commerces: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Commerces: {e}")
        return False

def test_search():
    """Test du moteur de recherche"""
    print("🔍 Test de la recherche conversationnelle...")
    try:
        search_data = {
            "query": "Trouve-moi un endroit où je peux manger du porc ce soir près de moi",
            "latitude": 6.1723,
            "longitude": 1.2312
        }
        
        response = requests.post(
            f"{API_BASE}/merchants/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Recherche: {result['total_count']} résultats en {result['search_time_ms']:.1f}ms")
            print(f"   Query traitée: {result['query_processed']}")
            return True
        else:
            print(f"❌ Recherche: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Recherche: {e}")
        return False

def test_auth():
    """Test de l'authentification"""
    print("🔍 Test de l'authentification...")
    try:
        # Test request OTP
        otp_data = {"phone_number": "+225123456789"}
        response = requests.post(
            f"{API_BASE}/auth/request-otp",
            json=otp_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Demande OTP: OK")
            # Note: On ne peut pas tester la vérification OTP sans le code réel
            return True
        else:
            print(f"❌ Demande OTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentification: {e}")
        return False

def main():
    print("🧪 Test de l'API Tcha-llé")
    print("=" * 40)
    
    tests = [
        test_health,
        test_categories,
        test_merchants,
        test_search,
        test_auth
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! L'API fonctionne correctement.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les logs ci-dessus.")

if __name__ == "__main__":
    main()