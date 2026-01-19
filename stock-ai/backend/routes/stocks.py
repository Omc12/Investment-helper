"""
Stock-related routes (list, search, details, candles).
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.stock_service import StockService
from services.yahoo_service import YahooFinanceService
from core.config import STOCKS_JSON_PATH, CACHE_STOCK_DETAILS, CACHE_CANDLES_DAILY, CACHE_CANDLES_INTRADAY
from core.cache import stock_details_cache, candles_cache, cached

router = APIRouter()
stock_service = StockService(STOCKS_JSON_PATH)


@router.get("/stocks")
def get_all_stocks():
    """Get list of all available stocks."""
    stocks = stock_service.load_stocks()
    return {
        "count": len(stocks),
        "stocks": stocks
    }


@router.get("/stocks/search")
def search_stocks(q: Optional[str] = Query(None, description="Search query")):
    """Search for stocks by ticker or name."""
    if not q or q.strip() == "":
        # Return top 10 popular stocks
        stocks = stock_service.load_stocks()
        return {"results": stocks[:10]}
    
    results = stock_service.search_stocks(q, limit=10)
    return {"results": results}


@router.get("/stocks/details")
@cached(stock_details_cache, key_func=lambda ticker: f"details_{ticker}")
def get_stock_details(ticker: Optional[str] = Query(None, description="Stock ticker")):
    """
    Get detailed stock information.
    Cached for 5 minutes.
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    ticker = ticker.strip().upper()
    
    try:
        details = YahooFinanceService.get_stock_details(ticker)
        
        if details.get("error"):
            raise HTTPException(status_code=404, detail=details["error"])
        
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching details: {str(e)}")


@router.get("/stocks/candles")
def get_stock_candles(
    ticker: Optional[str] = Query(None, description="Stock ticker"),
    interval: str = Query("1d", description="Interval: 1d, 5m, 15m"),
    period: str = Query("6mo", description="Period: 1d, 5d, 1mo, 6mo, 1y, 2y")
):
    """
    Get OHLCV candles for a stock.
    Cached based on interval (30 min for daily, 30 sec for intraday).
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    ticker = ticker.strip().upper()
    
    # Validate interval
    valid_intervals = ["1d", "5m", "15m", "1h"]
    if interval not in valid_intervals:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval. Must be one of: {', '.join(valid_intervals)}"
        )
    
    # Create cache key
    cache_key = f"candles_{ticker}_{interval}_{period}"
    
    # Check cache
    if cache_key in candles_cache:
        return candles_cache[cache_key]
    
    try:
        candles = YahooFinanceService.get_candles(ticker, period, interval)
        
        if not candles:
            raise HTTPException(status_code=404, detail="No data found for this ticker")
        
        result = {
            "ticker": ticker,
            "interval": interval,
            "period": period,
            "count": len(candles),
            "candles": candles
        }
        
        # Cache result
        candles_cache[cache_key] = result
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candles: {str(e)}")
