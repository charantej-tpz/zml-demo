"""
Health check endpoints.

Provides liveness and readiness probes for container orchestration
and monitoring systems.
"""

import logging

from fastapi import APIRouter, status

from app.api.deps import SettingsDep
from app.db.firebase_admin import get_firebase_app
from app.db.firestore import check_firestore_connection
from app.db.realtime_db import check_realtime_db_connection
from app.schemas.common import HealthStatus

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Basic liveness probe. Returns 200 if the service is running.",
)
async def health_check(settings: SettingsDep) -> HealthStatus:
    """
    Basic health check endpoint.

    Returns application status, version, and environment.
    Used as a liveness probe for container orchestration.
    """
    return HealthStatus(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment.value,
    )


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Readiness probe checking Firestore and Realtime Database.",
)
async def readiness_check(settings: SettingsDep):
    """
    Readiness check endpoint.

    Verifies that the application is ready to receive traffic by checking:
    - Firestore connectivity
    - Realtime Database connectivity (if configured)
    - Firebase project details

    Returns detailed status of each dependency.
    """
    checks = {}

    # Check Firestore connection
    firestore_healthy = await check_firestore_connection()
    checks["firestore"] = "healthy" if firestore_healthy else "unhealthy"

    # Check Realtime Database connection (only if configured)
    if settings.realtime_database_url:
        rtdb_healthy = await check_realtime_db_connection()
        checks["realtime_db"] = "healthy" if rtdb_healthy else "unhealthy"

    # Get Firebase project details
    firebase_info = {}
    try:
        firebase_app = get_firebase_app()
        firebase_info["project_id"] = firebase_app.project_id
        firebase_info["name"] = firebase_app.name
        firebase_info["status"] = "connected"
    except Exception as e:
        firebase_info["status"] = "error"
        firebase_info["error"] = str(e)

    # Determine overall status
    all_healthy = all(status == "healthy" for status in checks.values())
    overall_status = "ready" if all_healthy else "not_ready"

    if not all_healthy:
        logger.warning(f"Readiness check failed: {checks}")

    return {
        "status": overall_status,
        "checks": checks,
        "firebase": firebase_info,
    }
