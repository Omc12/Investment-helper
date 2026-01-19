"""
Yahoo Finance data fetching service.
"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime


class YahooFinanceService:
    """Service for fetching data from Yahoo Finance."""
    
    @staticmethod
    def get_ticker_info(ticker: str) -> Optional[Dict]:
        """
        Safely fetch ticker info from Yahoo Finance.
        Returns None if ticker is invalid or data unavailable.
        """
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            
            # Check if info is valid (has basic data)
            if not info or len(info) < 5:
                return None
            
            return info
        except Exception as e:
            print(f"Error fetching info for {ticker}: {e}")
            return None
    
    @staticmethod
    def get_historical_data(
        ticker: str,
        period: str = "2y",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data from Yahoo Finance.
        
        Args:
            ticker: Stock ticker (e.g., "RELIANCE.NS")
            period: Time period (e.g., "1d", "5d", "1mo", "6mo", "2y")
            interval: Data interval (e.g., "1d", "5m", "15m", "1h")
        
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
            
            if df.empty or len(df) < 2:
                return None
            
            # Handle MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Ensure required columns exist
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_cols):
                return None
            
            return df
            
        except Exception as e:
            print(f"Error fetching historical data for {ticker}: {e}")
            return None
    
    @staticmethod
    def get_stock_details(ticker: str) -> Dict:
        """
        Get detailed stock information safely.
        Returns dict with all available fields, None for missing ones.
        """
        info = YahooFinanceService.get_ticker_info(ticker)
        
        if not info:
            return {
                "ticker": ticker,
                "name": None,
                "sector": None,
                "marketCap": None,
                "currentPrice": None,
                "previousClose": None,
                "dayHigh": None,
                "dayLow": None,
                "fiftyTwoWeekHigh": None,
                "fiftyTwoWeekLow": None,
                "error": "Unable to fetch stock details"
            }
        
        return {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "marketCap": info.get("marketCap"),
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
            "previousClose": info.get("previousClose") or info.get("regularMarketPreviousClose"),
            "dayHigh": info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "dayLow": info.get("dayLow") or info.get("regularMarketDayLow"),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
            "volume": info.get("volume"),
            "averageVolume": info.get("averageVolume")
        }
    
    @staticmethod
    def get_candles(
        ticker: str,
        period: str = "6mo",
        interval: str = "1d"
    ) -> List[Dict]:
        """
        Get OHLCV candles as list of dicts.
        """
        df = YahooFinanceService.get_historical_data(ticker, period, interval)
        
        if df is None or df.empty:
            return []
        
        candles = []
        for idx, row in df.iterrows():
            try:
                candle = {
                    "time": idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                }
                candles.append(candle)
            except (ValueError, TypeError, KeyError):
                continue
        
        return candles
