"""
Health check routes.
"""
from fastapi import APIRouter
from core.cache import get_cache_info

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Indian Stock Predictor API",
        "version": "2.0"
    }


@router.get("/health/cache")
def cache_health():
    """Get cache statistics."""
    return {
        "status": "ok",
        "cache_info": get_cache_info()
    }
