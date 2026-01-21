"""
Prediction routes.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.trading_signals import analyze_stock_signals

router = APIRouter()


@router.get("/predict")
def predict_stock(ticker: Optional[str] = Query(None, description="Stock ticker like RELIANCE.NS")):
    """
    Predict next-day direction for a stock.
    Uses pre-trained model for fast predictions.
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    ticker = ticker.strip().upper()
    
    try:
        prediction = analyze_stock_signals(ticker)
        return prediction
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
