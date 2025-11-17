"""Simplified database initialization (SQLite only, no SQLAlchemy for MVP)."""

from .storage import SimpleStorage
from ..core.logger import get_logger

logger = get_logger(__name__)

# Global storage instance
_storage: SimpleStorage = None


def init_database(database_url: str = None) -> None:
    """
    Initialize simplified database storage.
    
    Args:
        database_url: Database connection URL (defaults to SQLite)
                     Format: sqlite:///path/to/db.db
    """
    global _storage
    
    if database_url is None:
        db_path = "./data/adco.db"
    elif database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
    else:
        db_path = database_url
    
    _storage = SimpleStorage(db_path=db_path)
    logger.info("Database initialized (simplified SQLite)", db_path=db_path)


def get_storage() -> SimpleStorage:
    """
    Get storage instance.
    
    Returns:
        SimpleStorage instance
    """
    if _storage is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _storage


# Legacy compatibility functions (for existing code)
def get_db():
    """Legacy compatibility - returns storage instance."""
    return get_storage()


def get_db_session():
    """Legacy compatibility - returns storage instance."""
    return get_storage()

