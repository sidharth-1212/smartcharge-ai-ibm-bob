"""
SmartCharge AI Backend - FastAPI Application
Main entry point for the backend API server
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import sys
from datetime import datetime

from app.config import settings, get_cors_origins
from app.database import init_db, check_db_connection, check_redis_connection
from app.routers import telemetry, bob, charging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_file_path) if settings.log_file_path else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("=" * 60)
    
    # Check database connection
    logger.info("Checking database connection...")
    if check_db_connection():
        logger.info("✓ Database connection successful")
        
        # Initialize database tables (in production, use Alembic migrations)
        if settings.environment == "development":
            logger.info("Initializing database tables...")
            try:
                init_db()
                logger.info("✓ Database tables initialized")
            except Exception as e:
                logger.error(f"✗ Failed to initialize database: {str(e)}")
    else:
        logger.error("✗ Database connection failed")
    
    # Check Redis connection
    logger.info("Checking Redis connection...")
    if check_redis_connection():
        logger.info("✓ Redis connection successful")
    else:
        logger.warning("✗ Redis connection failed (caching will be disabled)")
    
    logger.info("=" * 60)
    logger.info(f"Server ready at http://0.0.0.0:8000")
    logger.info(f"API docs available at http://0.0.0.0:8000/docs")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("Shutting down SmartCharge AI Backend...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered EV charging optimizer using IBM watsonx.ai Bob",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    
    Returns system status and connectivity checks
    """
    db_status = check_db_connection()
    redis_status = check_redis_connection()
    
    return {
        "status": "healthy" if db_status else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.environment,
        "services": {
            "database": "connected" if db_status else "disconnected",
            "redis": "connected" if redis_status else "disconnected",
            "bob_api": "configured"
        }
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI-powered EV charging optimizer using IBM watsonx.ai Bob",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "telemetry": "/api/telemetry",
            "bob": "/api/bob",
            "charging": "/api/charging"
        }
    }


# Include routers
app.include_router(telemetry.router)
app.include_router(bob.router)
app.include_router(charging.router)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    # Log response
    logger.info(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] {duration:.3f}s"
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

# Made with Bob