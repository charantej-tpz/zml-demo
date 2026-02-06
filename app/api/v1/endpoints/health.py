"""
Health check endpoints.

Provides liveness and readiness probes for container orchestration
and monitoring systems.
"""

import logging

from fastapi import APIRouter, status

from app.api.deps import SettingsDep
from app.db.firestore import check_firestore_connection
from app.db.realtime_db import check_realtime_db_connection
from app.schemas.common import HealthStatus, ReadinessStatus

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
    response_model=ReadinessStatus,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Readiness probe that checks all dependencies including Firestore and Realtime Database.",
)
async def readiness_check(settings: SettingsDep) -> ReadinessStatus:
    """
    Readiness check endpoint.

    Verifies that the application is ready to receive traffic by checking:
    - Firestore connectivity
    - Realtime Database connectivity (if configured)

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

    # Determine overall status
    all_healthy = all(status == "healthy" for status in checks.values())
    overall_status = "ready" if all_healthy else "not_ready"

    if not all_healthy:
        logger.warning(f"Readiness check failed: {checks}")

    return ReadinessStatus(
        status=overall_status,
        checks=checks,
    )

