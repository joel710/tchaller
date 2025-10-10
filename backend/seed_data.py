from sqlalchemy.orm import Session
from .database import SessionLocal, Category, Merchant, Ambassador, User
from geoalchemy2 import functions as gf
import json

def create_sample_data():
    db = SessionLocal()
    
    try:
        # Create categories
        categories_data = [
            {"name": "Restaurant"},
            {"name": "Maquis"},
            {"name": "Bar"},
            {"name": "Café"},
            {"name": "Boutique"},
            {"name": "Magasin"},
            {"name": "Pharmacie"},
            {"name": "Coiffure"},
            {"name": "Réparation"},
        ]
        
        for cat_data in categories_data:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                category = Category(name=cat_data["name"])
                db.add(category)
        
        db.commit()
        
        # Get category IDs
        restaurant_cat = db.query(Category).filter(Category.name == "Restaurant").first()
        maquis_cat = db.query(Category).filter(Category.name == "Maquis").first()
        bar_cat = db.query(Category).filter(Category.name == "Bar").first()
        boutique_cat = db.query(Category).filter(Category.name == "Boutique").first()
        
        # Create sample ambassador
        ambassador_user = User(phone_number="+225123456789", is_verified=True)
        db.add(ambassador_user)
        db.commit()
        db.refresh(ambassador_user)
        
        ambassador = Ambassador(
            user_id=ambassador_user.id,
            full_name="Jean Kouassi"
        )
        db.add(ambassador)
        db.commit()
        db.refresh(ambassador)
        
        # Create sample merchants with diverse activities
        merchants_data = [
            # RESTAURANTS
            {
                "name": "Maquis Doho",
                "description": "Le meilleur maquis du quartier avec spécialités ivoiriennes",
                "category_id": maquis_cat.id,
                "latitude": 6.1723,
                "longitude": 1.2312,
                "address": "Rue des Jardins, Cocody",
                "phone_number": "+225123456789",
                "whatsapp_number": "+225123456789",
                "opening_hours": json.dumps({
                    "monday": "06:00-23:00",
                    "tuesday": "06:00-23:00",
                    "wednesday": "06:00-23:00",
                    "thursday": "06:00-23:00",
                    "friday": "06:00-24:00",
                    "saturday": "06:00-24:00",
                    "sunday": "08:00-22:00"
                }),
                "price_level": 1,
                "rating": 4.5,
                "review_count": 127,
                "is_verified": True,
                "is_open": True
            },
            {
                "name": "Restaurant Le Gourmet",
                "description": "Cuisine française et africaine dans un cadre élégant",
                "category_id": restaurant_cat.id,
                "latitude": 6.1750,
                "longitude": 1.2350,
                "address": "Boulevard de la République, Plateau",
                "phone_number": "+225987654321",
                "whatsapp_number": "+225987654321",
                "opening_hours": json.dumps({
                    "monday": "12:00-15:00,19:00-23:00",
                    "tuesday": "12:00-15:00,19:00-23:00",
                    "wednesday": "12:00-15:00,19:00-23:00",
                    "thursday": "12:00-15:00,19:00-23:00",
                    "friday": "12:00-15:00,19:00-23:00",
                    "saturday": "19:00-24:00",
                    "sunday": "19:00-22:00"
                }),
                "price_level": 3,
                "rating": 4.8,
                "review_count": 89,
                "is_verified": True,
                "is_open": True
            },
            {
                "name": "Bar Le Soleil",
                "description": "Bar convivial avec terrasse et vue sur la lagune",
                "category_id": bar_cat.id,
                "latitude": 6.1700,
                "longitude": 1.2280,
                "address": "Avenue Franchet d'Esperey, Cocody",
                "phone_number": "+225555666777",
                "whatsapp_number": "+225555666777",
                "opening_hours": json.dumps({
                    "monday": "18:00-02:00",
                    "tuesday": "18:00-02:00",
                    "wednesday": "18:00-02:00",
                    "thursday": "18:00-02:00",
                    "friday": "18:00-03:00",
                    "saturday": "18:00-03:00",
                    "sunday": "18:00-01:00"
                }),
                "price_level": 2,
                "rating": 4.2,
                "review_count": 156,
                "is_verified": False,
                "is_open": True
            },
            {
                "name": "Boutique Mode Africaine",
                "description": "Vêtements traditionnels et modernes africains",
                "category_id": boutique_cat.id,
                "latitude": 6.1800,
                "longitude": 1.2400,
                "address": "Marché de Treichville",
                "phone_number": "+225444555666",
                "whatsapp_number": "+225444555666",
                "opening_hours": json.dumps({
                    "monday": "08:00-18:00",
                    "tuesday": "08:00-18:00",
                    "wednesday": "08:00-18:00",
                    "thursday": "08:00-18:00",
                    "friday": "08:00-18:00",
                    "saturday": "08:00-16:00",
                    "sunday": "Fermé"
                }),
                "price_level": 2,
                "rating": 4.0,
                "review_count": 43,
                "is_verified": False,
                "is_open": False
            },
            {
                "name": "Maquis Chez Fatou",
                "description": "Spécialités sénégalaises et ivoiriennes",
                "category_id": maquis_cat.id,
                "latitude": 6.1650,
                "longitude": 1.2200,
                "address": "Yopougon, Secteur 15",
                "phone_number": "+225777888999",
                "whatsapp_number": "+225777888999",
                "opening_hours": json.dumps({
                    "monday": "06:00-22:00",
                    "tuesday": "06:00-22:00",
                    "wednesday": "06:00-22:00",
                    "thursday": "06:00-22:00",
                    "friday": "06:00-23:00",
                    "saturday": "06:00-23:00",
                    "sunday": "08:00-21:00"
                }),
                "price_level": 1,
                "rating": 4.6,
                "review_count": 203,
                "is_verified": True,
                "is_open": True
            },
            
            # SANTÉ
            {
                "name": "Hôpital Général d'Abidjan",
                "description": "Hôpital public principal d'Abidjan avec services d'urgence 24h/24",
                "category_id": restaurant_cat.id,  # Temporaire, sera remplacé par hôpital
                "latitude": 6.1800,
                "longitude": 1.2400,
                "address": "Boulevard de la République, Plateau",
                "phone_number": "+22520212223",
                "whatsapp_number": "+22520212223",
                "opening_hours": json.dumps({
                    "monday": "00:00-24:00",
                    "tuesday": "00:00-24:00",
                    "wednesday": "00:00-24:00",
                    "thursday": "00:00-24:00",
                    "friday": "00:00-24:00",
                    "saturday": "00:00-24:00",
                    "sunday": "00:00-24:00"
                }),
                "price_level": 1,
                "rating": 4.2,
                "review_count": 89,
                "is_verified": True,
                "is_open": True
            },
            {
                "name": "Pharmacie du Plateau",
                "description": "Pharmacie de garde avec livraison à domicile",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1780,
                "longitude": 1.2380,
                "address": "Avenue Franchet d'Esperey, Plateau",
                "phone_number": "+22520212224",
                "whatsapp_number": "+22520212224",
                "opening_hours": json.dumps({
                    "monday": "08:00-20:00",
                    "tuesday": "08:00-20:00",
                    "wednesday": "08:00-20:00",
                    "thursday": "08:00-20:00",
                    "friday": "08:00-20:00",
                    "saturday": "08:00-18:00",
                    "sunday": "09:00-17:00"
                }),
                "price_level": 2,
                "rating": 4.4,
                "review_count": 156,
                "is_verified": True,
                "is_open": True
            },
            
            # ÉDUCATION
            {
                "name": "Université Félix Houphouët-Boigny",
                "description": "Université publique principale d'Abidjan",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1900,
                "longitude": 1.2500,
                "address": "Cocody, Université",
                "phone_number": "+22520212225",
                "whatsapp_number": "+22520212225",
                "opening_hours": json.dumps({
                    "monday": "08:00-17:00",
                    "tuesday": "08:00-17:00",
                    "wednesday": "08:00-17:00",
                    "thursday": "08:00-17:00",
                    "friday": "08:00-17:00",
                    "saturday": "08:00-12:00",
                    "sunday": "Fermé"
                }),
                "price_level": 1,
                "rating": 4.1,
                "review_count": 234,
                "is_verified": True,
                "is_open": False
            },
            
            # SERVICES
            {
                "name": "Garage Auto Express",
                "description": "Réparation automobile rapide et fiable",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1600,
                "longitude": 1.2100,
                "address": "Yopougon, Route de Dabou",
                "phone_number": "+22520212226",
                "whatsapp_number": "+22520212226",
                "opening_hours": json.dumps({
                    "monday": "07:00-18:00",
                    "tuesday": "07:00-18:00",
                    "wednesday": "07:00-18:00",
                    "thursday": "07:00-18:00",
                    "friday": "07:00-18:00",
                    "saturday": "08:00-16:00",
                    "sunday": "Fermé"
                }),
                "price_level": 2,
                "rating": 4.3,
                "review_count": 78,
                "is_verified": True,
                "is_open": True
            },
            {
                "name": "Salon de Coiffure Élégance",
                "description": "Coiffure et esthétique pour hommes et femmes",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1700,
                "longitude": 1.2300,
                "address": "Cocody, Angré 8ème Tranche",
                "phone_number": "+22520212227",
                "whatsapp_number": "+22520212227",
                "opening_hours": json.dumps({
                    "monday": "09:00-19:00",
                    "tuesday": "09:00-19:00",
                    "wednesday": "09:00-19:00",
                    "thursday": "09:00-19:00",
                    "friday": "09:00-19:00",
                    "saturday": "09:00-18:00",
                    "sunday": "10:00-16:00"
                }),
                "price_level": 2,
                "rating": 4.7,
                "review_count": 145,
                "is_verified": True,
                "is_open": True
            },
            
            # FINANCE
            {
                "name": "Banque Atlantique",
                "description": "Banque commerciale avec services complets",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1750,
                "longitude": 1.2350,
                "address": "Plateau, Avenue Delafosse",
                "phone_number": "+22520212228",
                "whatsapp_number": "+22520212228",
                "opening_hours": json.dumps({
                    "monday": "08:00-16:00",
                    "tuesday": "08:00-16:00",
                    "wednesday": "08:00-16:00",
                    "thursday": "08:00-16:00",
                    "friday": "08:00-16:00",
                    "saturday": "08:00-12:00",
                    "sunday": "Fermé"
                }),
                "price_level": 3,
                "rating": 4.0,
                "review_count": 67,
                "is_verified": True,
                "is_open": True
            },
            
            # LOISIRS
            {
                "name": "Cinéma Cinecocody",
                "description": "Cinéma moderne avec films internationaux",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1850,
                "longitude": 1.2450,
                "address": "Cocody, Riviera 2",
                "phone_number": "+22520212229",
                "whatsapp_number": "+22520212229",
                "opening_hours": json.dumps({
                    "monday": "14:00-23:00",
                    "tuesday": "14:00-23:00",
                    "wednesday": "14:00-23:00",
                    "thursday": "14:00-23:00",
                    "friday": "14:00-24:00",
                    "saturday": "14:00-24:00",
                    "sunday": "14:00-22:00"
                }),
                "price_level": 2,
                "rating": 4.5,
                "review_count": 189,
                "is_verified": True,
                "is_open": True
            },
            
            # RELIGION
            {
                "name": "Cathédrale Saint-Paul",
                "description": "Cathédrale catholique principale d'Abidjan",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1700,
                "longitude": 1.2400,
                "address": "Plateau, Boulevard de la République",
                "phone_number": "+22520212230",
                "whatsapp_number": "+22520212230",
                "opening_hours": json.dumps({
                    "monday": "06:00-19:00",
                    "tuesday": "06:00-19:00",
                    "wednesday": "06:00-19:00",
                    "thursday": "06:00-19:00",
                    "friday": "06:00-19:00",
                    "saturday": "06:00-19:00",
                    "sunday": "06:00-19:00"
                }),
                "price_level": 1,
                "rating": 4.6,
                "review_count": 312,
                "is_verified": True,
                "is_open": True
            },
            
            # GOUVERNEMENT
            {
                "name": "Mairie de Cocody",
                "description": "Administration municipale de Cocody",
                "category_id": restaurant_cat.id,  # Temporaire
                "latitude": 6.1800,
                "longitude": 1.2300,
                "address": "Cocody, Mairie",
                "phone_number": "+22520212231",
                "whatsapp_number": "+22520212231",
                "opening_hours": json.dumps({
                    "monday": "08:00-16:00",
                    "tuesday": "08:00-16:00",
                    "wednesday": "08:00-16:00",
                    "thursday": "08:00-16:00",
                    "friday": "08:00-16:00",
                    "saturday": "08:00-12:00",
                    "sunday": "Fermé"
                }),
                "price_level": 1,
                "rating": 3.8,
                "review_count": 45,
                "is_verified": True,
                "is_open": True
            }
        ]
        
        for merchant_data in merchants_data:
            existing = db.query(Merchant).filter(Merchant.name == merchant_data["name"]).first()
            if not existing:
                merchant = Merchant(
                    name=merchant_data["name"],
                    description=merchant_data["description"],
                    category_id=merchant_data["category_id"],
                    address=merchant_data["address"],
                    phone_number=merchant_data["phone_number"],
                    whatsapp_number=merchant_data["whatsapp_number"],
                    opening_hours=merchant_data["opening_hours"],
                    price_level=merchant_data["price_level"],
                    rating=merchant_data["rating"],
                    review_count=merchant_data["review_count"],
                    is_verified=merchant_data["is_verified"],
                    is_open=merchant_data["is_open"],
                    ambassador_id=ambassador.id,
                    location=gf.ST_SetSRID(
                        gf.ST_MakePoint(merchant_data["longitude"], merchant_data["latitude"]), 
                        4326
                    )
                )
                db.add(merchant)
        
        db.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()