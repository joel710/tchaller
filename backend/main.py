"""
Application principale Tcha-llé Ultra Polyvalent
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from backend.config import settings
from backend.database.connection import create_tables
from backend.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    print("🚀 Démarrage de Tcha-llé Ultra Polyvalent...")
    create_tables()
    print("✅ Base de données initialisée")
    print("✅ Application prête !")
    
    yield
    
    # Shutdown
    print("🛑 Arrêt de l'application...")

# Création de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS ultra permissive
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Inclusion des routes API
app.include_router(api_router)

# Montage des fichiers statiques
if os.path.exists("/workspace/frontend"):
    app.mount("/static", StaticFiles(directory="/workspace/frontend"), name="static")

# Routes principales
@app.get("/", response_class=HTMLResponse)
async def root():
    """Page d'accueil"""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tcha-llé Ultra Polyvalent</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        </style>
    </head>
    <body class="bg-gray-50">
        <div class="min-h-screen flex items-center justify-center">
            <div class="max-w-4xl mx-auto text-center px-4">
                <div class="gradient-bg text-white rounded-2xl p-12 shadow-2xl">
                    <i class="fas fa-globe-africa text-6xl mb-6"></i>
                    <h1 class="text-4xl font-bold mb-4">Tcha-llé Ultra Polyvalent</h1>
                    <p class="text-xl mb-8">Découvrez toutes les activités utiles autour de vous</p>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div class="bg-white bg-opacity-20 rounded-lg p-6">
                            <i class="fas fa-hospital text-3xl mb-3"></i>
                            <h3 class="font-semibold">Santé</h3>
                            <p class="text-sm">Hôpitaux, Pharmacies, Cliniques</p>
                        </div>
                        <div class="bg-white bg-opacity-20 rounded-lg p-6">
                            <i class="fas fa-graduation-cap text-3xl mb-3"></i>
                            <h3 class="font-semibold">Éducation</h3>
                            <p class="text-sm">Écoles, Universités, Formation</p>
                        </div>
                        <div class="bg-white bg-opacity-20 rounded-lg p-6">
                            <i class="fas fa-tools text-3xl mb-3"></i>
                            <h3 class="font-semibold">Services</h3>
                            <p class="text-sm">Garages, Coiffures, Banques</p>
                        </div>
                    </div>
                    
                    <div class="space-y-4">
                        <a href="/docs" class="inline-block bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition mr-4">
                            <i class="fas fa-book mr-2"></i>Documentation API
                        </a>
                        <a href="/static/index.html" class="inline-block bg-white bg-opacity-20 text-white px-8 py-3 rounded-lg font-semibold hover:bg-opacity-30 transition">
                            <i class="fas fa-search mr-2"></i>Rechercher
                        </a>
                    </div>
                </div>
                
                <div class="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div class="bg-white rounded-lg p-6 shadow-lg">
                        <h3 class="text-xl font-bold mb-4">🎯 Ultra Polyvalent</h3>
                        <ul class="text-gray-600 space-y-2">
                            <li>• Tous types d'activités utiles</li>
                            <li>• Santé, Éducation, Services</li>
                            <li>• Loisirs, Religion, Administration</li>
                            <li>• Recherche conversationnelle</li>
                        </ul>
                    </div>
                    
                    <div class="bg-white rounded-lg p-6 shadow-lg">
                        <h3 class="text-xl font-bold mb-4">🤖 IA Avancée</h3>
                        <ul class="text-gray-600 space-y-2">
                            <li>• Compréhension du langage naturel</li>
                            <li>• Détection d'urgence automatique</li>
                            <li>• Réponses variées et humaines</li>
                            <li>• Suggestions intelligentes</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Vérification de santé de l'application"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "message": "Tcha-llé Ultra Polyvalent est opérationnel !"
    }

@app.get("/info")
async def app_info():
    """Informations sur l'application"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "features": [
            "Recherche ultra polyvalente",
            "Moteur conversationnel IA",
            "Support de tous types d'activités",
            "Géolocalisation avancée",
            "API REST complète",
            "Interface PWA"
        ],
        "supported_activities": [
            "Santé (Hôpitaux, Pharmacies, Cliniques)",
            "Éducation (Écoles, Universités, Formation)",
            "Services (Garages, Coiffures, Banques)",
            "Alimentation (Restaurants, Maquis, Bars)",
            "Loisirs (Cinémas, Théâtres, Centres de jeux)",
            "Religion (Églises, Mosquées, Temples)",
            "Administration (Mairies, Préfectures, Tribunaux)",
            "Finance (Banques, Assurances, Microfinance)",
            "Transport (Stations-service, Taxis, Gares)",
            "Autres (ONG, Associations, Conseils)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )