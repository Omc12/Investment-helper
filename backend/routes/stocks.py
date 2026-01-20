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
def get_all_stocks(
    limit: Optional[int] = Query(None, description="Limit number of stocks returned"),
    search: Optional[str] = Query(None, description="Search query for stocks")
):
    """Get stocks - only returns results when search query is provided."""
    
    # Only search when query is provided - no default stocks
    if search and search.strip():
        stocks = stock_service.search_stocks(search.strip(), limit=limit or 50)
    else:
        stocks = []  # Return empty when no search query
    
    return {
        "count": len(stocks),
        "stocks": stocks,
        "search_query": search.strip() if search else None
    }


@router.get("/stocks/search")
def search_stocks(q: Optional[str] = Query(None, description="Search query")):
    """Search for stocks with on-demand API fetching."""
    if not q or q.strip() == "":
        # Return empty results when no query provided
        return {"results": [], "query": "", "total_found": 0}
    
    print(f"[SEARCH] API search request for: '{q}'")
    
    # Use the on-demand search that fetches from APIs
    results = stock_service.search_stocks(q.strip(), limit=20)
    
    print(f"[OK] Returning {len(results)} results")
    
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
    Real-time stock lookup by ticker.
    Uses on-demand API fetching to find stocks.
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    ticker = ticker.strip().upper()
    search_query = f"{ticker}{exchange}" if exchange else ticker
    
    print(f"[SEARCH] Looking up ticker: '{search_query}'")
    
    # Use the on-demand search which queries APIs
    results = stock_service.search_stocks(search_query, limit=5)
    
    if results:
        print(f"[OK] Found {len(results)} match(es)")
        return {
            "stock": results[0],  # Return first match
            "all_matches": results,
            "found": True,
            "total_matches": len(results)
        }
    
    print(f"[ERROR] No results found for '{search_query}'")
    raise HTTPException(
        status_code=404, 
        detail=f"Stock with ticker '{ticker}' not found"
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
def get_stock_details(ticker: Optional[str] = Query(None, description="Stock ticker")):
    """
    Get detailed stock information - fetches fresh data on-demand.
    No caching to ensure latest data is always shown.
    """
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")
    
    ticker = ticker.strip().upper()
    
    print(f"[FETCH] Fetching fresh details for {ticker}...")
    
    try:
        details = YahooFinanceService.get_stock_details(ticker)
        
        if details.get("error"):
            print(f"[ERROR] Error fetching {ticker}: {details['error']}")
            raise HTTPException(status_code=404, detail=details["error"])
        
        print(f"[OK] Successfully fetched details for {ticker}")
        return details
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Exception fetching {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching details: {str(e)}")


@router.get("/stocks/candles")
def get_stock_candles(
    ticker: Optional[str] = Query(None, description="Stock ticker"),
    interval: str = Query("1d", description="Interval: 1d, 5m, 15m"),
    period: str = Query("6mo", description="Period: 1d, 5d, 1mo, 6mo, 1y, 2y")
):
    """
    Get OHLCV candles for a stock - fetches fresh historical data on-demand.
    Required for charts and prediction model.
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
    
    print(f"[FETCH] Fetching {period} of {interval} candles for {ticker}...")
    
    try:
        candles = YahooFinanceService.get_candles(ticker, period, interval)
        
        if not candles:
            print(f"[ERROR] No candle data found for {ticker}")
            raise HTTPException(status_code=404, detail="No historical data found for this ticker")
        
        print(f"[OK] Fetched {len(candles)} candles for {ticker}")
        
        result = {
            "ticker": ticker,
            "interval": interval,
            "period": period,
            "count": len(candles),
            "candles": candles
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candles: {str(e)}")
