"""
Indian Stock Predictor API - Main Application
Production-grade FastAPI application with clean architecture.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import API_TITLE, API_VERSION, CORS_ORIGINS
from routes import health, stocks, predict

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="AI-powered Indian stock prediction API with ML models"
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


if __name__ == "__main__":
    import uvicorn
    from core.config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)
