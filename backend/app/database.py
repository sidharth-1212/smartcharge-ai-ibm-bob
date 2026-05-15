"""
Database connection and session management
Provides SQLAlchemy engine, session factory, and dependency injection
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine with SQLite-specific settings
if settings.database_url.startswith("sqlite"):
    # SQLite doesn't support connection pooling the same way
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},  # Allow multi-threading
        echo=settings.debug,  # Log SQL queries in debug mode
    )
else:
    # PostgreSQL/MySQL with connection pooling
    engine = create_engine(
        settings.database_url,
        poolclass=QueuePool,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,  # Verify connections before using
        echo=settings.debug,  # Log SQL queries in debug mode
    )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions
    
    Usage in FastAPI endpoints:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models.py
    
    Note: In production, use Alembic migrations instead
    """
    from .models import Base
    
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_db_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False


# Redis connection (for caching) - Optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis library not available, caching disabled")

from typing import Optional
from .config import is_redis_enabled

_redis_client: Optional[any] = None


def get_redis() -> Optional[any]:
    """
    Get Redis client instance (singleton)
    Returns None if Redis is disabled or unavailable
    
    Returns:
        Redis client or None
    """
    global _redis_client
    
    if not REDIS_AVAILABLE or not is_redis_enabled():
        return None
    
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            logger.info("Redis client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis: {e}")
            return None
    
    return _redis_client


def check_redis_connection() -> bool:
    """
    Check if Redis connection is working
    
    Returns:
        True if connection successful, False otherwise
    """
    if not REDIS_AVAILABLE or not is_redis_enabled():
        logger.info("Redis is disabled")
        return False
    
    try:
        redis_client = get_redis()
        if redis_client:
            redis_client.ping()
            logger.info("Redis connection successful")
            return True
        return False
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
        return False


# Cache helper functions (no-op if Redis disabled)
def cache_set(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """
    Set a value in Redis cache (no-op if Redis disabled)
    
    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds (default from settings)
    
    Returns:
        True if successful, False otherwise
    """
    if not is_redis_enabled():
        return False
    
    try:
        redis_client = get_redis()
        if not redis_client:
            return False
        ttl = ttl or settings.redis_cache_ttl
        redis_client.setex(key, ttl, value)
        return True
    except Exception as e:
        logger.error(f"Failed to set cache key {key}: {str(e)}")
        return False


def cache_get(key: str) -> Optional[str]:
    """
    Get a value from Redis cache (returns None if Redis disabled)
    
    Args:
        key: Cache key
    
    Returns:
        Cached value or None if not found
    """
    if not is_redis_enabled():
        return None
    
    try:
        redis_client = get_redis()
        if not redis_client:
            return None
        return redis_client.get(key)
    except Exception as e:
        logger.error(f"Failed to get cache key {key}: {str(e)}")
        return None


def cache_delete(key: str) -> bool:
    """
    Delete a value from Redis cache (no-op if Redis disabled)
    
    Args:
        key: Cache key
    
    Returns:
        True if successful, False otherwise
    """
    if not is_redis_enabled():
        return False
    
    try:
        redis_client = get_redis()
        if not redis_client:
            return False
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to delete cache key {key}: {str(e)}")
        return False


def cache_exists(key: str) -> bool:
    """
    Check if a key exists in Redis cache (returns False if Redis disabled)
    
    Args:
        key: Cache key
    
    Returns:
        True if key exists, False otherwise
    """
    if not is_redis_enabled():
        return False
    
    try:
        redis_client = get_redis()
        if not redis_client:
            return False
        return redis_client.exists(key) > 0
    except Exception as e:
        logger.error(f"Failed to check cache key {key}: {str(e)}")
        return False

# Made with Bob