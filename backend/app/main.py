import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import configure_logging

# Configure logging first
configure_logging(debug=settings.APP_DEBUG)
logger = logging.getLogger(__name__)

# Import routers AFTER setting up logging
from app.api.v1.router import api_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Adversarial Prompt Firewall for Enterprise LLMs",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Allowed origins: {settings.allowed_origins_list}")

# Include routers
logger.info("Registering API routes...")
app.include_router(api_router)
logger.info("✓ API routes registered")

# Root endpoints
@app.get("/", tags=["system"])
def root():
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "env": settings.APP_ENV,
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("AI Prompt Firewall Backend Starting")
    logger.info("=" * 50)
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"API Base: http://localhost:8000/api/v1")
    logger.info(f"Docs: http://localhost:8000/docs")
    logger.info("=" * 50)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AI Prompt Firewall Backend Shutting Down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)