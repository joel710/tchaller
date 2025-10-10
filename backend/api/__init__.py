"""
API routes pour Tcha-llé
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .activities import router as activities_router
from .search import router as search_router
from .users import router as users_router
from .categories import router as categories_router
from .webhooks import router as webhooks_router

# Router principal
api_router = APIRouter(prefix="/api/v1")

# Inclusion des sous-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(activities_router, prefix="/activities", tags=["Activities"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(categories_router, prefix="/categories", tags=["Categories"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

__all__ = ["api_router"]