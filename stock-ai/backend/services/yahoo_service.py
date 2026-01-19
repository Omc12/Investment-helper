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
        Fetch historical price data from Yahoo Finance with fast timeout.
        """
        # If Yahoo Finance is down, skip the call
        if YahooFinanceService._yahoo_finance_down:
            return None
            
        try:
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Yahoo Finance historical data timed out")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 second timeout for historical data
            
            try:
                df = yf.download(
                    ticker,
                    period=period,
                    interval=interval,
                    progress=False,
                    auto_adjust=True
                )
                signal.alarm(0)  # Cancel alarm
                
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
                
            except TimeoutError:
                signal.alarm(0)
                return None
            
        except Exception as e:
            signal.alarm(0)  # Make sure to cancel alarm
            return None
    
    @staticmethod
    def get_stock_details(ticker: str) -> Dict:
        """
        Get detailed stock information with immediate fallback for speed.
        """
        # Use fallback data immediately for speed - no API delays
        return FallbackDataService.get_stock_details(ticker)
    
    @staticmethod
    def get_candles(
        ticker: str,
        period: str = "6mo",
        interval: str = "1d"
    ) -> List[Dict]:
        """
        Get OHLCV candles with immediate fallback for speed.
        """
        # Use fallback data immediately for instant response
        return FallbackDataService.get_candles(ticker, period, interval)
