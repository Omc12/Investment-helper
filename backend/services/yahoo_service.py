"""
Yahoo Finance data fetching service with fallback support.
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime
from .fallback_service import FallbackDataService


class YahooFinanceService:
    """Service for fetching data from Yahoo Finance."""
    
    # Track Yahoo Finance availability to avoid slow repeated calls
    _yahoo_finance_down = False
    _last_check_time = 0
    
    @staticmethod
    def get_ticker_info(ticker: str) -> Optional[Dict]:
        """
        Safely fetch ticker info from Yahoo Finance with fast timeout.
        Returns None if ticker is invalid or data unavailable.
        """
        import time
        current_time = time.time()
        
        # If Yahoo Finance was down recently, skip the call for 60 seconds
        if YahooFinanceService._yahoo_finance_down and (current_time - YahooFinanceService._last_check_time) < 60:
            return None
            
        try:
            # Set a short timeout for faster failure
            import yfinance as yf
            yf_ticker = yf.Ticker(ticker)
            
            # Use a timeout mechanism
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Yahoo Finance call timed out")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(3)  # 3 second timeout
            
            try:
                info = yf_ticker.info
                signal.alarm(0)  # Cancel alarm
                
                # Check if info is valid (has basic data)
                if not info or len(info) < 5:
                    YahooFinanceService._yahoo_finance_down = True
                    YahooFinanceService._last_check_time = current_time
                    return None
                
                # Check for error in the info response
                if 'error' in info or info.get('longName') is None and info.get('shortName') is None:
                    return None
                
                # Reset the down flag if successful
                YahooFinanceService._yahoo_finance_down = False
                return info
                
            except TimeoutError:
                signal.alarm(0)
                YahooFinanceService._yahoo_finance_down = True
                YahooFinanceService._last_check_time = current_time
                return None
                
        except Exception as e:
            signal.alarm(0)  # Make sure to cancel alarm
            YahooFinanceService._yahoo_finance_down = True
            YahooFinanceService._last_check_time = current_time
            return None
    
    @staticmethod
    def get_historical_data(
        ticker: str,
        period: str = "2y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data from Yahoo Finance using Ticker object.
        """
        # If Yahoo Finance is down, skip the call
        if YahooFinanceService._yahoo_finance_down:
            return None
            
        try:
            # Use Ticker object which is more reliable than download()
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval, auto_adjust=True)
            
            if df is None or df.empty or len(df) < 2:
                print(f"[DEBUG] No historical data for {ticker}")
                return None

            # Ensure required columns exist
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                print(f"[DEBUG] Missing required columns for {ticker}. Got: {df.columns.tolist()}")
                return None

            print(f"[DEBUG] Successfully fetched {len(df)} rows for {ticker}")
            return df
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch historical data for {ticker}: {str(e)}")
            return None
    
    @staticmethod
    def get_stock_details(ticker: str) -> Dict:
        """
        Get detailed stock information from Yahoo Finance with real-time data.
        Falls back to cached data only if API fails.
        """
        try:
            # Try to get real-time data from Yahoo Finance first
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Validate that we got real data
            if not info or 'regularMarketPrice' not in info:
                print(f"[WARNING] Yahoo Finance returned incomplete data for {ticker}, using fallback")
                return FallbackDataService.get_stock_details(ticker)
            
            # Extract relevant fields with proper fallbacks
            result = {
                "ticker": ticker,
                "longName": info.get("longName", info.get("shortName", ticker)),
                "shortName": info.get("shortName", ticker),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                
                # Current price data
                "currentPrice": info.get("regularMarketPrice", info.get("currentPrice", 0)),
                "previousClose": info.get("regularMarketPreviousClose", info.get("previousClose", 0)),
                
                # Day trading range
                "dayHigh": info.get("regularMarketDayHigh", info.get("dayHigh", 0)),
                "dayLow": info.get("regularMarketDayLow", info.get("dayLow", 0)),
                "open": info.get("regularMarketOpen", info.get("open", 0)),
                
                # 52-week range
                "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
                "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
                
                # Volume and market cap
                "volume": info.get("regularMarketVolume", info.get("volume", 0)),
                "averageVolume": info.get("averageVolume", 0),
                "marketCap": info.get("marketCap", 0),
                
                # Valuation metrics
                "trailingPE": info.get("trailingPE", 0),
                "forwardPE": info.get("forwardPE", 0),
                "dividendYield": info.get("dividendYield", 0),
                "bookValue": info.get("bookValue", 0),
                
                # Additional info
                "currency": info.get("currency", "INR"),
                "exchange": info.get("exchange", "NSI"),
                "quoteType": info.get("quoteType", "EQUITY"),
                
                # Timestamp
                "lastUpdated": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch details for {ticker}: {str(e)}")
            # Fallback to cached/mock data
            return FallbackDataService.get_stock_details(ticker)
    
    @staticmethod
    def get_candles(
        ticker: str,
        period: str = "6mo",
        interval: str = "1d"
    ) -> List[Dict]:
        """
        Get OHLCV candles from Yahoo Finance with real-time data.
        Falls back to cached data only if API fails.
        """
        try:
            # Try to get real historical data
            df = YahooFinanceService.get_historical_data(ticker, period, interval)
            
            if df is None or df.empty:
                print(f"[WARNING] Yahoo Finance returned no data for {ticker}, using fallback")
                return FallbackDataService.get_candles(ticker, period, interval)
            
            # Convert DataFrame to list of candle dictionaries
            candles = []
            for date, row in df.iterrows():
                candles.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "timestamp": int(date.timestamp()),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
                })
            
            return candles
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch candles for {ticker}: {str(e)}")
            # Fallback to cached/mock data
            return FallbackDataService.get_candles(ticker, period, interval)
