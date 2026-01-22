"""
Stock data routes for frontend compatibility.
Uses Finnhub as primary data source with yfinance as fallback.
"""
from fastapi import APIRouter, Query, HTTPException
import yfinance as yf
import pandas as pd
import json
import os
import requests
import time
from typing import Optional
from functools import lru_cache
from datetime import datetime, timedelta

router = APIRouter()

# Finnhub API configuration
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

# Simple in-memory cache with TTL
_stock_details_cache = {}
_stock_candles_cache = {}
CACHE_TTL_SECONDS = 300  # 5 minutes cache


def get_cached_stock_details(ticker: str):
    """Get cached stock details if not expired"""
    if ticker in _stock_details_cache:
        data, timestamp = _stock_details_cache[ticker]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return data
    return None


def set_cached_stock_details(ticker: str, data: dict):
    """Cache stock details with timestamp"""
    _stock_details_cache[ticker] = (data, time.time())


def get_cached_candles(cache_key: str):
    """Get cached candles if not expired"""
    if cache_key in _stock_candles_cache:
        data, timestamp = _stock_candles_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL_SECONDS:
            return data
    return None


def set_cached_candles(cache_key: str, data: dict):
    """Cache candles with timestamp"""
    _stock_candles_cache[cache_key] = (data, time.time())


# ============ FINNHUB API FUNCTIONS ============

def finnhub_get_quote(symbol: str) -> Optional[dict]:
    """Get real-time quote from Finnhub"""
    if not FINNHUB_API_KEY:
        return None
    try:
        url = f"{FINNHUB_BASE_URL}/quote"
        params = {"symbol": symbol, "token": FINNHUB_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        # Check if we got valid data (c=0 means no data)
        if data.get("c", 0) > 0:
            return data
        return None
    except Exception as e:
        print(f"Finnhub quote error: {e}")
        return None


def finnhub_get_company_profile(symbol: str) -> Optional[dict]:
    """Get company profile from Finnhub"""
    if not FINNHUB_API_KEY:
        return None
    try:
        url = f"{FINNHUB_BASE_URL}/stock/profile2"
        params = {"symbol": symbol, "token": FINNHUB_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("name"):
            return data
        return None
    except Exception as e:
        print(f"Finnhub profile error: {e}")
        return None


def finnhub_get_candles(symbol: str, resolution: str, from_ts: int, to_ts: int) -> Optional[dict]:
    """Get stock candles from Finnhub
    resolution: 1, 5, 15, 30, 60, D, W, M
    """
    if not FINNHUB_API_KEY:
        return None
    try:
        url = f"{FINNHUB_BASE_URL}/stock/candle"
        params = {
            "symbol": symbol,
            "resolution": resolution,
            "from": from_ts,
            "to": to_ts,
            "token": FINNHUB_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Check if we got valid data
        if data.get("s") == "ok" and data.get("c"):
            return data
        return None
    except Exception as e:
        print(f"Finnhub candles error: {e}")
        return None


def finnhub_get_basic_financials(symbol: str) -> Optional[dict]:
    """Get basic financials/metrics from Finnhub"""
    if not FINNHUB_API_KEY:
        return None
    try:
        url = f"{FINNHUB_BASE_URL}/stock/metric"
        params = {"symbol": symbol, "metric": "all", "token": FINNHUB_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("metric"):
            return data.get("metric")
        return None
    except Exception as e:
        print(f"Finnhub financials error: {e}")
        return None


def convert_ticker_for_finnhub(ticker: str) -> str:
    """Convert NSE ticker to Finnhub format (e.g., TATASTEEL.NS -> TATASTEEL.NS)"""
    # Finnhub uses the same format for Indian stocks
    return ticker


def period_to_timestamps(period: str) -> tuple:
    """Convert period string to from/to timestamps"""
    now = datetime.now()
    to_ts = int(now.timestamp())
    
    period_map = {
        "1d": timedelta(days=1),
        "5d": timedelta(days=5),
        "1mo": timedelta(days=30),
        "3mo": timedelta(days=90),
        "6mo": timedelta(days=180),
        "1y": timedelta(days=365),
        "2y": timedelta(days=730),
        "5y": timedelta(days=1825),
        "10y": timedelta(days=3650),
        "ytd": timedelta(days=(now - datetime(now.year, 1, 1)).days),
        "max": timedelta(days=7300),
    }
    
    delta = period_map.get(period, timedelta(days=30))
    from_ts = int((now - delta).timestamp())
    
    return from_ts, to_ts


def interval_to_finnhub_resolution(interval: str) -> str:
    """Convert yfinance interval to Finnhub resolution"""
    interval_map = {
        "1m": "1",
        "5m": "5",
        "15m": "15",
        "30m": "30",
        "60m": "60",
        "1h": "60",
        "1d": "D",
        "1wk": "W",
        "1mo": "M",
    }
    return interval_map.get(interval, "D")


# Load fallback stock database
def load_stock_database():
    """Load all NSE stocks from JSON file as fallback"""
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "stocks_nse.json")
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Cache the stock database for fallback
STOCK_DATABASE = load_stock_database()


def search_stocks_api(query: str, limit: int = 8):
    """
    Real-time API search using Yahoo Finance API.
    Searches through ALL Indian stocks dynamically.
    """
    if not query:
        # Return top popular stocks when no query
        return STOCK_DATABASE[:limit]
    
    try:
        # Yahoo Finance search endpoint
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            "q": query,
            "quotesCount": limit,
            "newsCount": 0,
            "listsCount": 0,
            "quotesQueryId": "tss_match_phrase_query"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        stocks = []
        quotes = data.get("quotes", [])
        
        for quote in quotes:
            symbol = quote.get("symbol", "")
            
            # Filter for Indian stocks (NSE/BSE)
            if ".NS" in symbol or ".BO" in symbol:
                exchange = "NSE" if ".NS" in symbol else "BSE"
                
                stocks.append({
                    "symbol": symbol,
                    "name": quote.get("longname") or quote.get("shortname") or symbol,
                    "sector": quote.get("sector", quote.get("industry", "Unknown")),
                    "exchange": exchange,
                    "quoteType": quote.get("quoteType", "EQUITY")
                })
        
        # If API returns results, use them
        if stocks:
            return stocks[:limit]
        
        # Fallback to local database search if API returns no results
        return search_stocks_local(query, limit)
        
    except Exception as e:
        print(f"Yahoo Finance API search failed: {e}, falling back to local search")
        # Fallback to local database search
        return search_stocks_local(query, limit)


def search_stocks_local(query: str, limit: int = 8):
    """
    Fallback local search with word-by-word matching.
    """
    if not query:
        return STOCK_DATABASE[:limit]
    
    query_lower = query.lower().strip()
    search_words = query_lower.split()
    
    scored_stocks = []
    
    for stock in STOCK_DATABASE:
        name_lower = stock["name"].lower()
        symbol_lower = stock["symbol"].lower().replace(".ns", "").replace(".bo", "")
        sector_lower = stock.get("sector", "").lower()
        
        score = 0
        matched_words = 0
        
        # Check each search word
        for word in search_words:
            # Exact symbol match (highest priority)
            if word == symbol_lower:
                score += 100
                matched_words += 1
            # Symbol starts with word
            elif symbol_lower.startswith(word):
                score += 80
                matched_words += 1
            # Symbol contains word
            elif word in symbol_lower:
                score += 50
                matched_words += 1
            # Name starts with word (high priority)
            elif name_lower.startswith(word):
                score += 70
                matched_words += 1
            # Any word in name starts with search word
            elif any(name_word.startswith(word) for name_word in name_lower.split()):
                score += 60
                matched_words += 1
            # Name contains word
            elif word in name_lower:
                score += 40
                matched_words += 1
            # Sector match
            elif word in sector_lower:
                score += 20
                matched_words += 1
        
        # Only include stocks that match at least one search word
        if matched_words > 0:
            # Boost score if all words match
            if matched_words == len(search_words):
                score += 30
            
            scored_stocks.append({
                "stock": stock,
                "score": score,
                "matched_words": matched_words
            })
    
    # Sort by score (descending), then by matched words (descending)
    scored_stocks.sort(key=lambda x: (x["score"], x["matched_words"]), reverse=True)
    
    # Return top results
    return [item["stock"] for item in scored_stocks[:limit]]


@router.get("/stocks")
def get_stocks(search: Optional[str] = Query(None), limit: int = Query(8)):
    """Get stock list with real-time API search"""
    
    if search:
        # Use real-time API search
        stocks = search_stocks_api(search, limit)
    else:
        # Return popular/top stocks when no search
        stocks = STOCK_DATABASE[:limit]
    
    return {
        "stocks": stocks,
        "total": len(stocks)
    }


@router.get("/stocks/details")
def get_stock_details(ticker: str = Query(...)):
    """Get comprehensive real-time stock details using Finnhub (primary) or yfinance (fallback)"""
    try:
        # Clean ticker
        if not ticker.endswith('.NS'):
            ticker = f"{ticker}.NS"
        
        # Check cache first
        cached = get_cached_stock_details(ticker)
        if cached:
            print(f"Returning cached details for {ticker}")
            return cached
        
        response = None
        data_source = None
        
        # ========== TRY FINNHUB FIRST ==========
        if FINNHUB_API_KEY:
            print(f"Trying Finnhub for {ticker}")
            finnhub_symbol = convert_ticker_for_finnhub(ticker)
            
            quote = finnhub_get_quote(finnhub_symbol)
            profile = finnhub_get_company_profile(finnhub_symbol)
            metrics = finnhub_get_basic_financials(finnhub_symbol)
            
            if quote and quote.get("c", 0) > 0:
                data_source = "finnhub"
                
                # Build response from Finnhub data
                current_price = quote.get("c", 0)
                prev_close = quote.get("pc", current_price)
                
                response = {
                    # Basic Info
                    "ticker": ticker,
                    "symbol": ticker,
                    "longName": profile.get("name", ticker.replace(".NS", "")) if profile else ticker.replace(".NS", ""),
                    "shortName": profile.get("name", ticker.replace(".NS", "")) if profile else ticker.replace(".NS", ""),
                    "name": profile.get("name", ticker.replace(".NS", "")) if profile else ticker.replace(".NS", ""),
                    "lastUpdateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "marketState": "REGULAR",
                    "dataSource": "finnhub",
                    
                    # Real-time Price Data
                    "currentPrice": float(current_price),
                    "previousClose": float(prev_close),
                    "regularMarketPrice": float(current_price),
                    "regularMarketPreviousClose": float(prev_close),
                    "open": float(quote.get("o", current_price)),
                    "regularMarketOpen": float(quote.get("o", current_price)),
                    "dayHigh": float(quote.get("h", current_price)),
                    "dayLow": float(quote.get("l", current_price)),
                    "regularMarketDayHigh": float(quote.get("h", current_price)),
                    "regularMarketDayLow": float(quote.get("l", current_price)),
                    "high": float(quote.get("h", current_price)),
                    "low": float(quote.get("l", current_price)),
                    
                    # Intraday Changes
                    "regularMarketChange": float(quote.get("d", 0)) if quote.get("d") else float(current_price - prev_close),
                    "regularMarketChangePercent": float(quote.get("dp", 0)) if quote.get("dp") else (float((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0),
                    
                    # Business Info from profile
                    "sector": profile.get("finnhubIndustry", "Unknown") if profile else "Unknown",
                    "industry": profile.get("finnhubIndustry", "Unknown") if profile else "Unknown",
                    "country": profile.get("country", "India") if profile else "India",
                    "exchange": profile.get("exchange", "NSE") if profile else "NSE",
                    "currency": profile.get("currency", "INR") if profile else "INR",
                    "website": profile.get("weburl", "") if profile else "",
                    "logo": profile.get("logo", "") if profile else "",
                    "marketCap": profile.get("marketCapitalization", 0) * 1000000 if profile and profile.get("marketCapitalization") else None,
                    "sharesOutstanding": profile.get("shareOutstanding", 0) * 1000000 if profile and profile.get("shareOutstanding") else None,
                    
                    # Metrics from basic financials
                    "fiftyTwoWeekHigh": metrics.get("52WeekHigh") if metrics else None,
                    "fiftyTwoWeekLow": metrics.get("52WeekLow") if metrics else None,
                    "beta": metrics.get("beta") if metrics else None,
                    "trailingPE": metrics.get("peBasicExclExtraTTM") if metrics else None,
                    "priceToBook": metrics.get("pbAnnual") if metrics else None,
                    "dividendYield": metrics.get("dividendYieldIndicatedAnnual") if metrics else None,
                    "returnOnEquity": metrics.get("roeTTM") if metrics else None,
                    "returnOnAssets": metrics.get("roaTTM") if metrics else None,
                    "grossMargins": metrics.get("grossMarginTTM") if metrics else None,
                    "operatingMargins": metrics.get("operatingMarginTTM") if metrics else None,
                    "profitMargins": metrics.get("netProfitMarginTTM") if metrics else None,
                    "revenueGrowth": metrics.get("revenueGrowthTTMYoy") if metrics else None,
                    "trailingEps": metrics.get("epsBasicExclExtraItemsTTM") if metrics else None,
                    "bookValue": metrics.get("bookValuePerShareAnnual") if metrics else None,
                    "currentRatio": metrics.get("currentRatioAnnual") if metrics else None,
                    "debtToEquity": metrics.get("totalDebt/totalEquityAnnual") if metrics else None,
                    "fiftyDayAverage": metrics.get("10DayAverageTradingVolume") if metrics else None,
                    
                    # Placeholders for compatibility
                    "quoteType": "EQUITY",
                    "financialCurrency": "INR",
                    "volume": None,
                    "regularMarketVolume": None,
                }
                
                print(f"Successfully got data from Finnhub for {ticker}")
        
        # ========== FALLBACK TO YFINANCE ==========
        if response is None:
            print(f"Falling back to yfinance for {ticker}")
            data_source = "yfinance"
            
            # Add small delay to help with rate limiting
            time.sleep(0.5)
        
            # Get data from yfinance
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check if we got valid data (rate limit returns empty or error)
            if not info or len(info) < 5:
                raise ValueError("Rate limited or invalid ticker")
            
            # Get latest intraday data (1-minute intervals for real-time price)
            hist_intraday = stock.history(period="1d", interval="1m")
            # Get recent daily data for previous close
            hist_daily = stock.history(period="5d", interval="1d")
            
            # Determine latest price source (prefer intraday if market is open, else use info)
            if not hist_intraday.empty and len(hist_intraday) > 0:
                latest = hist_intraday.iloc[-1]
                latest_price = float(latest["Close"])
                latest_open = float(latest["Open"]) if not pd.isna(latest["Open"]) else info.get("regularMarketOpen", latest_price)
                latest_high = float(hist_intraday["High"].max())
                latest_low = float(hist_intraday["Low"].min())
                latest_volume = int(hist_intraday["Volume"].sum())
                latest_time = hist_intraday.index[-1].strftime("%Y-%m-%d %H:%M:%S")
            elif not hist_daily.empty:
                latest = hist_daily.iloc[-1]
                latest_price = float(latest["Close"])
                latest_open = float(latest["Open"])
                latest_high = float(latest["High"])
                latest_low = float(latest["Low"])
                latest_volume = int(latest["Volume"])
                latest_time = hist_daily.index[-1].strftime("%Y-%m-%d")
            else:
                # Fallback to info values
                latest_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
                latest_open = info.get("regularMarketOpen", latest_price)
                latest_high = info.get("regularMarketDayHigh", latest_price)
                latest_low = info.get("regularMarketDayLow", latest_price)
                latest_volume = info.get("regularMarketVolume", 0)
                latest_time = "N/A"
            
            # Get previous close
            if not hist_daily.empty and len(hist_daily) > 1:
                prev_close = float(hist_daily.iloc[-2]["Close"])
            else:
                prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose", latest_price)
            
            # Build comprehensive response with real-time data
            response = {
                # Basic Info
                "ticker": ticker,
                "symbol": ticker,
                "longName": info.get("longName", ticker.replace(".NS", "")),
                "shortName": info.get("shortName", ticker.replace(".NS", "")),
                "name": info.get("longName", ticker.replace(".NS", "")),
                "lastUpdateTime": latest_time,
                "marketState": info.get("marketState", "CLOSED"),
                "dataSource": "yfinance",
                
                # Real-time Price Data
                "currentPrice": float(latest_price),
                "previousClose": float(prev_close),
                "regularMarketPrice": float(latest_price),
                "regularMarketPreviousClose": float(prev_close),
                "open": float(latest_open),
                "regularMarketOpen": float(latest_open),
                "dayHigh": float(latest_high),
                "dayLow": float(latest_low),
                "regularMarketDayHigh": float(latest_high),
                "regularMarketDayLow": float(latest_low),
                "high": float(latest_high),
                "low": float(latest_low),
                
                # Intraday Changes
                "regularMarketChange": float(latest_price - prev_close),
                "regularMarketChangePercent": float((latest_price - prev_close) / prev_close * 100) if prev_close > 0 else 0,
                
                # 52 Week Range
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
                "fiftyTwoWeekChange": info.get("52WeekChange"),
                "fiftyTwoWeekChangePercent": info.get("fiftyTwoWeekChangePercent"),
                "fiftyTwoWeekHighChange": info.get("fiftyTwoWeekHighChange"),
                "fiftyTwoWeekHighChangePercent": info.get("fiftyTwoWeekHighChangePercent"),
                "fiftyTwoWeekLowChange": info.get("fiftyTwoWeekLowChange"),
                "fiftyTwoWeekLowChangePercent": info.get("fiftyTwoWeekLowChangePercent"),
                "fiftyTwoWeekRange": info.get("fiftyTwoWeekRange"),
                
                # Volume
                "volume": int(latest_volume),
                "regularMarketVolume": int(latest_volume),
                "averageVolume": info.get("averageVolume"),
                "averageVolume10days": info.get("averageVolume10days"),
                "averageDailyVolume10Day": info.get("averageDailyVolume10Day"),
                "averageDailyVolume3Month": info.get("averageDailyVolume3Month"),
                
                # Moving Averages
                "fiftyDayAverage": info.get("fiftyDayAverage"),
                "fiftyDayAverageChange": info.get("fiftyDayAverageChange"),
                "fiftyDayAverageChangePercent": info.get("fiftyDayAverageChangePercent"),
                "twoHundredDayAverage": info.get("twoHundredDayAverage"),
                "twoHundredDayAverageChange": info.get("twoHundredDayAverageChange"),
                "twoHundredDayAverageChangePercent": info.get("twoHundredDayAverageChangePercent"),
                
                # Market Cap & Valuation
                "marketCap": info.get("marketCap"),
                "enterpriseValue": info.get("enterpriseValue"),
                "enterpriseToRevenue": info.get("enterpriseToRevenue"),
                "enterpriseToEbitda": info.get("enterpriseToEbitda"),
                
                # Ratios
                "trailingPE": info.get("trailingPE"),
                "forwardPE": info.get("forwardPE"),
                "priceToBook": info.get("priceToBook"),
                "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),
                "pegRatio": info.get("trailingPegRatio"),
                "beta": info.get("beta"),
                
                # Earnings & Dividends
                "trailingEps": info.get("trailingEps") or info.get("epsTrailingTwelveMonths"),
                "forwardEps": info.get("forwardEps") or info.get("epsForward"),
                "epsCurrentYear": info.get("epsCurrentYear"),
                "dividendRate": info.get("dividendRate") or info.get("trailingAnnualDividendRate"),
                "dividendYield": info.get("dividendYield") or info.get("trailingAnnualDividendYield"),
                "exDividendDate": info.get("exDividendDate"),
                "payoutRatio": info.get("payoutRatio"),
                "fiveYearAvgDividendYield": info.get("fiveYearAvgDividendYield"),
                
                # Profitability
                "profitMargins": info.get("profitMargins"),
                "operatingMargins": info.get("operatingMargins"),
                "grossMargins": info.get("grossMargins"),
                "ebitdaMargins": info.get("ebitdaMargins"),
                "revenueGrowth": info.get("revenueGrowth"),
                "earningsGrowth": info.get("earningsGrowth"),
                "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),
                
                # Financial Health
                "totalRevenue": info.get("totalRevenue"),
                "revenuePerShare": info.get("revenuePerShare"),
                "totalCash": info.get("totalCash"),
                "totalCashPerShare": info.get("totalCashPerShare"),
                "totalDebt": info.get("totalDebt"),
                "debtToEquity": info.get("debtToEquity"),
                "currentRatio": info.get("currentRatio"),
                "quickRatio": info.get("quickRatio"),
                "returnOnAssets": info.get("returnOnAssets"),
                "returnOnEquity": info.get("returnOnEquity"),
                "freeCashflow": info.get("freeCashflow"),
                "operatingCashflow": info.get("operatingCashflow"),
                "ebitda": info.get("ebitda"),
                "grossProfits": info.get("grossProfits"),
                "netIncomeToCommon": info.get("netIncomeToCommon"),
                
                # Business Info
                "sector": info.get("sector", "Unknown"),
                "sectorKey": info.get("sectorKey"),
                "industry": info.get("industry", "Unknown"),
                "industryKey": info.get("industryKey"),
                "fullTimeEmployees": info.get("fullTimeEmployees"),
                "website": info.get("website"),
                "irWebsite": info.get("irWebsite"),
                "country": info.get("country"),
                "city": info.get("city"),
                "address1": info.get("address1"),
                "address2": info.get("address2"),
                "zip": info.get("zip"),
                "phone": info.get("phone"),
                "fax": info.get("fax"),
                
                # Description
                "longBusinessSummary": info.get("longBusinessSummary"),
                "businessSummary": info.get("businessSummary"),
                
                # Trading Info
                "exchange": info.get("exchange", "NSE"),
                "fullExchangeName": info.get("fullExchangeName"),
                "quoteType": info.get("quoteType", "EQUITY"),
                "currency": info.get("currency", "INR"),
                "financialCurrency": info.get("financialCurrency", "INR"),
                "exchangeTimezoneName": info.get("exchangeTimezoneName"),
                "exchangeTimezoneShortName": info.get("exchangeTimezoneShortName"),
                
                # Analyst Recommendations
                "targetHighPrice": info.get("targetHighPrice"),
                "targetLowPrice": info.get("targetLowPrice"),
                "targetMeanPrice": info.get("targetMeanPrice"),
                "targetMedianPrice": info.get("targetMedianPrice"),
                "recommendationKey": info.get("recommendationKey"),
                "recommendationMean": info.get("recommendationMean"),
                "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
                "averageAnalystRating": info.get("averageAnalystRating"),
                
                # Additional Metrics
                "sharesOutstanding": info.get("sharesOutstanding"),
                "impliedSharesOutstanding": info.get("impliedSharesOutstanding"),
                "floatShares": info.get("floatShares"),
                "heldPercentInsiders": info.get("heldPercentInsiders"),
                "heldPercentInstitutions": info.get("heldPercentInstitutions"),
                "bookValue": info.get("bookValue"),
                "lastDividendValue": info.get("lastDividendValue"),
                "lastDividendDate": info.get("lastDividendDate"),
                "lastSplitDate": info.get("lastSplitDate"),
                "lastSplitFactor": info.get("lastSplitFactor"),
                
                # Risk Metrics
                "auditRisk": info.get("auditRisk"),
                "boardRisk": info.get("boardRisk"),
                "compensationRisk": info.get("compensationRisk"),
                "shareHolderRightsRisk": info.get("shareHolderRightsRisk"),
                "overallRisk": info.get("overallRisk"),
                
                # Historical Highs/Lows
                "allTimeHigh": info.get("allTimeHigh"),
                "allTimeLow": info.get("allTimeLow"),
                
                # Bid/Ask
                "bid": info.get("bid"),
                "ask": info.get("ask"),
                "bidSize": info.get("bidSize"),
                "askSize": info.get("askSize"),
            }
        
        # Cache the response before returning
        set_cached_stock_details(ticker, response)
        
        return response
        
    except Exception as e:
        # If rate limited, return a more helpful message with retry-after hint
        error_msg = str(e)
        if "Rate" in error_msg or "Too Many" in error_msg or "limited" in error_msg.lower():
            raise HTTPException(
                status_code=429, 
                detail="Yahoo Finance rate limit reached. Please try again in a few minutes."
            )
        raise HTTPException(status_code=400, detail=f"Failed to fetch stock details: {error_msg}")


@router.get("/stocks/candles") 
def get_stock_candles(
    ticker: str = Query(...),
    period: str = Query("1mo", description="1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max"),
    interval: str = Query("1d", description="1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo")
):
    """Get stock price history/candles using Finnhub (primary) or yfinance (fallback)"""
    try:
        # Clean ticker
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            ticker = f"{ticker}.NS"
        
        # Check cache first
        cache_key = f"{ticker}_{period}_{interval}"
        cached = get_cached_candles(cache_key)
        if cached:
            print(f"Returning cached candles for {cache_key}")
            return cached
        
        response = None
        intraday_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']
        
        # ========== TRY FINNHUB FIRST ==========
        if FINNHUB_API_KEY:
            print(f"Trying Finnhub candles for {ticker}")
            finnhub_symbol = convert_ticker_for_finnhub(ticker)
            from_ts, to_ts = period_to_timestamps(period)
            resolution = interval_to_finnhub_resolution(interval)
            
            finnhub_data = finnhub_get_candles(finnhub_symbol, resolution, from_ts, to_ts)
            
            if finnhub_data and finnhub_data.get("c"):
                candles = []
                for i in range(len(finnhub_data["c"])):
                    ts = finnhub_data["t"][i]
                    if interval in intraday_intervals:
                        time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
                    else:
                        time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                    
                    candles.append({
                        "time": time_str,
                        "date": time_str,
                        "open": float(finnhub_data["o"][i]),
                        "high": float(finnhub_data["h"][i]),
                        "low": float(finnhub_data["l"][i]),
                        "close": float(finnhub_data["c"][i]),
                        "volume": int(finnhub_data["v"][i]) if finnhub_data.get("v") else 0
                    })
                
                response = {
                    "candles": candles,
                    "ticker": ticker,
                    "interval": interval,
                    "count": len(candles),
                    "dataSource": "finnhub"
                }
                print(f"Successfully got candles from Finnhub for {ticker}")
        
        # ========== FALLBACK TO YFINANCE ==========
        if response is None:
            print(f"Falling back to yfinance candles for {ticker}")
            
            # Add small delay to help with rate limiting
            time.sleep(0.3)
                
            stock = yf.Ticker(ticker)
            
            if interval in intraday_intervals:
                # Try fetching intraday data first
                hist = stock.history(period=period, interval=interval)
                
                # If no intraday data (market closed), fall back to daily data
                if hist.empty or len(hist) < 2:
                    print(f"No intraday data for {ticker}, falling back to daily data")
                    # Use more days for daily fallback
                    fallback_period = "5d" if period == "1d" else period
                    hist = stock.history(period=fallback_period, interval="1d")
                    interval = "1d"  # Update interval for response
            else:
                hist = stock.history(period=period, interval=interval)
            
            # If still empty, try with a longer period
            if hist.empty:
                print(f"No data for {ticker} with period {period}, trying 1mo")
                hist = stock.history(period="1mo", interval="1d")
            
            if hist.empty:
                raise ValueError(f"No data available for {ticker}. The stock may be delisted or the ticker is invalid.")
            
            # Convert to candles format
            candles = []
            for index, row in hist.iterrows():
                # Handle both date and datetime indexes
                if hasattr(index, 'strftime'):
                    if interval in intraday_intervals:
                        time_str = index.strftime("%Y-%m-%d %H:%M")
                    else:
                        time_str = index.strftime("%Y-%m-%d")
                else:
                    time_str = str(index)
                    
                candles.append({
                    "time": time_str,
                    "date": time_str,
                    "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                    "high": float(row["High"]) if pd.notna(row["High"]) else None, 
                    "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                    "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                    "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0
                })
            
            # Filter out any candles with None values
            candles = [c for c in candles if c["close"] is not None]
            
            response = {
                "candles": candles,
                "ticker": ticker,
                "interval": interval,
                "count": len(candles),
                "dataSource": "yfinance"
            }
        
        # Cache the response
        set_cached_candles(cache_key, response)
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        if "Rate" in error_msg or "Too Many" in error_msg or "limited" in error_msg.lower():
            raise HTTPException(
                status_code=429, 
                detail="Rate limit reached. Please try again in a few minutes."
            )
        raise HTTPException(status_code=400, detail=f"Failed to fetch candles: {error_msg}")
