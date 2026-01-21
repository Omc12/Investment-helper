"""
Indian Stock Predictor API - Main Application
Production-grade FastAPI application with clean architecture and multi-provider support.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import API_TITLE, API_VERSION, CORS_ORIGINS
from routes import health, stocks, predict, providers

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
    """Startup event - ready for real-time data fetching."""
    print("✓ Server ready - using real-time Yahoo Finance data (no cache)")


if __name__ == "__main__":
    import uvicorn
    from core.config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)
