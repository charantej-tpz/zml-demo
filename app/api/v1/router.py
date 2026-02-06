"""
API v1 router aggregator.

Combines all v1 endpoint routers into a single router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health

# Create the main v1 router
router = APIRouter()

# Include all endpoint routers
router.include_router(health.router)

# Add more routers here as you create them:
# router.include_router(users.router, prefix="/users", tags=["Users"])
# router.include_router(items.router, prefix="/items", tags=["Items"])
