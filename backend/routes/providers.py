"""
Provider status and health check endpoints.
"""
from fastapi import APIRouter, Depends
from services.stock_service import StockService
from core.config import STOCKS_JSON_PATH
import asyncio

router = APIRouter()

def get_stock_service() -> StockService:
    return StockService(STOCKS_JSON_PATH)

@router.get("/providers/status")
async def get_provider_status(stock_service: StockService = Depends(get_stock_service)):
    """Get status of all data providers."""
    try:
        status = stock_service.multi_fetcher.get_provider_status()
        return {
            "providers": status,
            "total_providers": len(status),
            "available_providers": len([p for p in status.values() if p['available']])
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/providers/health")
async def check_provider_health(stock_service: StockService = Depends(get_stock_service)):
    """Check health of all providers."""
    try:
        health = await stock_service.multi_fetcher.health_check()
        return {
            "health": health,
            "healthy_providers": len([h for h in health.values() if h]),
            "total_providers": len(health)
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/providers/{provider_name}/reset")
async def reset_provider_errors(provider_name: str, stock_service: StockService = Depends(get_stock_service)):
    """Reset errors for a specific provider."""
    try:
        stock_service.multi_fetcher.reset_provider_errors(provider_name)
        return {"message": f"Reset errors for provider: {provider_name}"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/providers/reset-all")
async def reset_all_provider_errors(stock_service: StockService = Depends(get_stock_service)):
    """Reset errors for all providers."""
    try:
        stock_service.multi_fetcher.reset_provider_errors()
        return {"message": "Reset errors for all providers"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/refresh")
async def force_refresh_stocks(stock_service: StockService = Depends(get_stock_service)):
    """Force refresh stock data from providers."""
    try:
        # Clear cache to force refresh
        from core.cache import stock_list_cache
        stock_list_cache.clear()
        
        # Load fresh data
        stocks = stock_service.load_stocks()
        
        return {
            "message": "Successfully refreshed stock data",
            "total_stocks": len(stocks),
            "timestamp": stock_service._last_fetch.isoformat() if stock_service._last_fetch else None
        }
    except Exception as e:
        return {"error": str(e)}