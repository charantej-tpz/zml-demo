"""
API v1 router aggregator.

Combines all v1 endpoint routers into a single router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import authentication, health, vitals

# Create the main v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(health.router)
router.include_router(authentication.router)
router.include_router(vitals.router)
