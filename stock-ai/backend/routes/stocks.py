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
def get_all_stocks(limit: Optional[int] = Query(None, description="Limit number of stocks returned")):
    """Get list of all available stocks with optional limit."""
    stocks = stock_service.load_stocks()
    
    if limit:
        stocks = stocks[:limit]
    
    return {
        "count": len(stocks),
        "total_available": len(stock_service.load_stocks()),
        "stocks": stocks,
        "last_updated": stock_service._last_fetch.isoformat() if stock_service._last_fetch else None
    }


@router.get("/stocks/search")
def search_stocks(q: Optional[str] = Query(None, description="Search query")):
    """Search for stocks dynamically across NSE and BSE."""
    if not q or q.strip() == "":
        # Return top 20 popular stocks (by market cap)
        stocks = stock_service.load_stocks()
        return {"results": stocks[:20]}
    
    # Use dynamic search that queries APIs in real-time
    results = stock_service.search_stocks_dynamic(q, limit=20)
    
    # If no results from dynamic search, try direct API search across exchanges
    if not results:
        results = stock_service.search_indian_exchanges(q)
    
    return {
        "results": results,
        "query": q.strip(),
        "total_found": len(results),
        "is_dynamic_search": True
    }


@router.get("/stocks/lookup")
def lookup_stock(
    ticker: Optional[str] = Query(None, description="Stock ticker symbol"),
    exchange: Optional[str] = Query(None, description="Exchange suffix (.NS, .BO)")
):
    """
    Real-time stock lookup across Indian exchanges.
    Tries to find any stock by ticker, even if not in cached database.
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    ticker = ticker.strip().upper()
    
    # If exchange is specified, try that first
    if exchange:
        full_ticker = f"{ticker}{exchange}"
        stock_info = stock_service._get_stock_info_from_api(full_ticker)
        if stock_info:
            return {"stock": stock_info, "found": True}
    
    # Try all Indian exchanges
    results = stock_service.search_indian_exchanges(ticker)
    
    if results:
        return {
            "stock": results[0],  # Return first match
            "all_matches": results,
            "found": True,
            "total_matches": len(results)
        }
    
    raise HTTPException(
        status_code=404, 
        detail=f"Stock with ticker '{ticker}' not found on NSE or BSE"
    )


@router.post("/stocks/refresh")
def force_refresh_stocks():
    """Admin endpoint to force refresh stock list from APIs."""
    try:
        refreshed_stocks = stock_service.force_refresh_stocks()
        return {
            "success": True,
            "message": f"Successfully refreshed {len(refreshed_stocks)} stocks",
            "count": len(refreshed_stocks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing stocks: {str(e)}")


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
