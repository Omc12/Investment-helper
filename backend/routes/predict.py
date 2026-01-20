"""
Prediction routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.model_service import ModelService

router = APIRouter()


@router.get("/predict")
def predict_stock(ticker: Optional[str] = Query(None, description="Stock ticker like RELIANCE.NS")):
    """
    Predict next-day direction for a stock.
    Uses walk-forward validation and caching.
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    ticker = ticker.strip().upper()
    
    try:
        prediction = ModelService.train_and_predict(ticker)
        return prediction
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
