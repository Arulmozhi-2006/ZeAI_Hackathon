import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Import routers
from app.api.v1 import auth, firewall, logs, analytics, models

# Create main router
api_router = APIRouter(prefix="/api/v1")

logger.info("Registering API v1 routes...")

# Include routers WITHOUT additional prefix (they have their own)
api_router.include_router(auth.router)
api_router.include_router(firewall.router)
api_router.include_router(logs.router)
api_router.include_router(analytics.router)
api_router.include_router(models.router)

logger.info("✓ All v1 routers registered successfully")