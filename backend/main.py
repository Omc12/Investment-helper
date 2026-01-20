"""
Indian Stock Predictor API - Main Application
Production-grade FastAPI application with clean architecture and multi-provider support.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import API_TITLE, API_VERSION, CORS_ORIGINS
from routes import health, stocks, predict, providers
from services.price_updater import PriceUpdater

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AI-powered Indian stock prediction API with multi-provider data system"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(stocks.router, tags=["stocks"])
app.include_router(predict.router, tags=["prediction"])
app.include_router(providers.router, prefix="/api", tags=["providers"])


@app.on_event("startup")
async def startup_event():
    """Load cached prices on startup."""
    PriceUpdater.load_prices()
    print("Loaded cached prices on startup")


@app.get("/prices/update")
def update_prices():
    """Manually trigger a price update from Yahoo Finance."""
    try:
        updated = PriceUpdater.fetch_and_update_all()
        return {
            "success": True,
            "updated_count": updated,
            "message": f"Updated {updated} stock prices from market"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/prices/status")
def price_status():
    """Get status of cached prices."""
    prices = PriceUpdater._cached_prices
    return {
        "cached_tickers": len(prices),
        "last_update": PriceUpdater._last_update.isoformat() if PriceUpdater._last_update else None,
        "tickers": list(prices.keys())
    }


if __name__ == "__main__":
    import uvicorn
    from core.config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)
