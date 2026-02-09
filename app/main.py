"""
FastAPI Application Entry Point.

This module creates and configures the FastAPI application instance.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.db.firestore import close_firestore_client, get_firestore_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize logging, connect to Firestore
    - Shutdown: Close Firestore connection
    """
    # Startup
    settings = get_settings()
    setup_logging()

    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} "
        f"in {settings.environment.value} mode"
    )

    # Initialize Firestore client (validates connection)
    try:
        get_firestore_client()
        logger.info("Firestore client initialized successfully")
    except Exception as e:
        logger.warning(f"Firestore client initialization warning: {e}")
        # Don't fail startup - allow health checks to report status

    yield

    # Shutdown
    logger.info("Shutting down application...")
    close_firestore_client()
    logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    """
    Application factory function.

    Creates and configures the FastAPI application with:
    - CORS middleware
    - Exception handlers
    - API routers

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="ZML API - Production-grade FastAPI with Firestore",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request context middleware for logging
    from app.middleware.request_context import RequestContextMiddleware

    app.add_middleware(RequestContextMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Include API routers
    app.include_router(v1_router, prefix=settings.api_prefix)

    # Root endpoint (outside versioned API)
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint returning API info."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment.value,
            "docs": "/docs" if settings.debug else "Disabled in production",
        }

    return app


# Create the application instance
app = create_application()
