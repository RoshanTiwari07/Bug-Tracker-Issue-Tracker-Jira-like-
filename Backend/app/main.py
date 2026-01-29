from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine
from sqlmodel import SQLModel

# Import all models to ensure they're registered with the metadata
# This MUST be done before create_all() is called
import app.models  # This will import all models in the correct order

# Setup logging
setup_logging()
logger = get_logger(__name__)


# Lifespan event for async startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    async with engine.begin() as conn:
        # Create tables from both Base (SQLAlchemy) and SQLModel metadata
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("[OK] Database tables created")
    yield
    # Shutdown
    await engine.dispose()
    logger.info("[OK] Database connection closed")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(api_router)


# Setup Scalar UI for API testing
@app.get("/scalar", include_in_schema=False)
async def scalar_docs():
    """Scalar UI - Modern API documentation and testing interface"""
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FastAPI Template",
        "version": settings.app_version,
        "docs": "/docs",
        "scalar": "/scalar"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


