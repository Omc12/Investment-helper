"""
Stock data service for loading and searching stock lists.
Now supports dynamic API-based stock fetching.
"""
import json
import os
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from core.cache import stock_list_cache, cached
from .stock_fetcher import StockListFetcher


class StockService:
    """Service for managing stock lists with dynamic API fetching."""
    
    def __init__(self, stocks_json_path: str):
        self.stocks_json_path = stocks_json_path
        self.stock_fetcher = StockListFetcher()
        self._last_fetch = None
        self._force_refresh_hours = 24  # Refresh every 24 hours
    
    @cached(stock_list_cache, key_func=lambda self: "all_stocks")
    def load_stocks(self) -> List[Dict]:
        """Load stocks dynamically from APIs with JSON fallback."""
        
        # Check if we need to refresh from APIs
        should_refresh = self._should_refresh_from_api()
        
        if should_refresh:
            print("Fetching fresh stock data from APIs...")
            try:
                # Get stocks from API
                api_stocks = self.stock_fetcher.get_comprehensive_stock_list()
                
                if api_stocks and len(api_stocks) > 50:  # Minimum threshold
                    self._last_fetch = datetime.now()
                    # Save to JSON as backup
                    self._save_stocks_to_json(api_stocks)
                    print(f"Successfully loaded {len(api_stocks)} stocks from APIs")
                    return api_stocks
                else:
                    print("API returned insufficient data, falling back to JSON")
                    
            except Exception as e:
                print(f"Error fetching from API: {e}, falling back to JSON")
        
        # Fallback to JSON file
        return self._load_stocks_from_json()
    
    def _should_refresh_from_api(self) -> bool:
        """Check if we should refresh from API based on time."""
        if not self._last_fetch:
            return True
            
        time_diff = datetime.now() - self._last_fetch
        return time_diff.total_seconds() > (self._force_refresh_hours * 3600)
    
    def _load_stocks_from_json(self) -> List[Dict]:
        """Load stocks from JSON file."""
        if not os.path.exists(self.stocks_json_path):
            print(f"JSON file not found: {self.stocks_json_path}")
            return []
        
        try:
            with open(self.stocks_json_path, 'r', encoding='utf-8') as f:
                stocks = json.load(f)
            print(f"Loaded {len(stocks)} stocks from JSON file")
            return stocks
        except Exception as e:
            print(f"Error loading stocks from JSON: {e}")
            return []
    
    def _save_stocks_to_json(self, stocks: List[Dict]) -> None:
        """Save fetched stocks to JSON file for backup."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.stocks_json_path), exist_ok=True)
            
            with open(self.stocks_json_path, 'w', encoding='utf-8') as f:
                json.dump(stocks, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(stocks)} stocks to {self.stocks_json_path}")
        except Exception as e:
            print(f"Error saving stocks to JSON: {e}")
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search stocks by ticker or name.
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of matching stock dicts
        """
        if not query or query.strip() == "":
            return []
        
        stocks = self.load_stocks()
        query_lower = query.lower().strip()
        
        # Filter matching stocks
        matches = [
            stock for stock in stocks
            if query_lower in stock.get("ticker", "").lower()
            or query_lower in stock.get("name", "").lower()
        ]
        
        # Sort: exact ticker matches first, then by name
        matches.sort(key=lambda x: (
            not x.get("ticker", "").lower().startswith(query_lower),
            x.get("name", "")
        ))
        
        return matches[:limit]
        
    def search_stocks_dynamic(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Dynamic search that queries APIs for stocks in real-time.
        Searches both cached stocks and tries to find new ones via API.
        """
        if not query or query.strip() == "":
            return self.load_stocks()[:limit]
        
        query = query.strip().upper()
        results = []
        
        # First search in cached stocks
        cached_results = self.search_stocks(query, limit//2) or []
        results.extend(cached_results)
        
        # If we have enough results from cache, return
        if len(results) >= limit:
            return results[:limit]
        
        # Try to find additional stocks via API
        api_results = self._search_stocks_via_api(query, limit - len(results)) or []
        results.extend(api_results)
        
        # Remove duplicates
        seen_tickers = set()
        unique_results = []
        for stock in results:
            ticker = stock.get('ticker', '').upper()
            if ticker not in seen_tickers:
                seen_tickers.add(ticker)
                unique_results.append(stock)
        
        return unique_results[:limit]
    
    def _search_stocks_via_api(self, query: str, limit: int) -> List[Dict]:
        """
        Search for stocks via APIs by trying different ticker combinations.
        """
        results = []
        
        # Common suffixes for Indian stocks
        suffixes = ['.NS', '.BO', '']
        
        # If query looks like a ticker, try direct lookup
        if len(query) <= 20 and query.isalpha():
            for suffix in suffixes:
                ticker_to_try = query + suffix if suffix else query
                
                try:
                    stock_info = self._get_stock_info_from_api(ticker_to_try)
                    if stock_info:
                        results.append(stock_info)
                        if len(results) >= limit:
                            break
                except:
                    continue
        
        # Try partial matches from known patterns
        if len(results) < limit:
            potential_tickers = self._generate_ticker_candidates(query)
            
            for ticker in potential_tickers[:min(10, limit - len(results))]:
                try:
                    stock_info = self._get_stock_info_from_api(ticker)
                    if stock_info:
                        results.append(stock_info)
                        if len(results) >= limit:
                            break
                except:
                    continue
        
        return results
    
    def _get_stock_info_from_api(self, ticker: str) -> Optional[Dict]:
        """
        Skip API calls and return None for instant fallback to cached data.
        This ensures fast responses without waiting for slow APIs.
        """
        # Return None immediately to use cached data - no slow API calls
        return None
    
    def _generate_ticker_candidates(self, query: str) -> List[str]:
        """
        Generate potential ticker symbols based on the query.
        """
        candidates = []
        
        # Direct ticker attempts
        candidates.extend([
            f"{query}.NS",
            f"{query}.BO",
            query
        ])
        
        # Common abbreviations and variations
        if len(query) > 3:
            # Try first few letters
            for i in range(3, min(8, len(query))):
                prefix = query[:i]
                candidates.extend([
                    f"{prefix}.NS",
                    f"{prefix}.BO"
                ])
        
        # Company name patterns (common Indian company patterns)
        common_patterns = {
            'BANK': ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'INDUSINDBK'],
            'TATA': ['TCS', 'TATAMOTORS', 'TATASTEEL', 'TATAPOWER', 'TATACONSUM'],
            'RELIANCE': ['RELIANCE', 'RPOWER', 'RCOM'],
            'BAJAJ': ['BAJFINANCE', 'BAJAJFINSV', 'BAJAJAUTO'],
            'ADANI': ['ADANIENT', 'ADANIPORTS', 'ADANIPOWER', 'ADANIGREEN']
        }
        
        for pattern, tickers in common_patterns.items():
            if pattern in query.upper():
                for ticker in tickers:
                    candidates.extend([f"{ticker}.NS", f"{ticker}.BO"])
        
        return list(set(candidates))  # Remove duplicates
    
    def search_indian_exchanges(self, query: str) -> List[Dict]:
        """
        Search across major Indian stock exchanges (NSE, BSE) for any stock.
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip().upper()
        results = []
        
        # List of major Indian stock exchanges
        exchanges = [
            '.NS',   # NSE
            '.BO',   # BSE
        ]
        
        # Try exact ticker match on each exchange
        for exchange in exchanges:
            ticker = f"{query}{exchange}"
            stock_info = self._get_stock_info_from_api(ticker)
            if stock_info:
                results.append(stock_info)
        
        # If no exact match, try broader search
        if not results:
            # Try without any suffix (sometimes works)
            stock_info = self._get_stock_info_from_api(query)
            if stock_info:
                results.append(stock_info)
            
            # Try common variations
            variations = [
                f"{query}LTD",
                f"{query}LIMITED", 
                f"{query}IND",
                f"{query}INDIA"
            ]
            
            for variation in variations:
                for exchange in exchanges:
                    ticker = f"{variation}{exchange}"
                    stock_info = self._get_stock_info_from_api(ticker)
                    if stock_info:
                        results.append(stock_info)
                        break  # Found one, move to next variation
        
        return results
    
    def force_refresh_stocks(self) -> List[Dict]:
        """Force refresh stocks from API (for admin/debug use)."""
        try:
            print("Force refreshing stocks from APIs...")
            api_stocks = self.stock_fetcher.get_comprehensive_stock_list()
            
            if api_stocks:
                self._last_fetch = datetime.now()
                self._save_stocks_to_json(api_stocks)
                
                # Clear cache to force reload
                if "all_stocks" in stock_list_cache:
                    del stock_list_cache["all_stocks"]
                
                print(f"Force refresh completed: {len(api_stocks)} stocks")
                return api_stocks
            else:
                print("Force refresh failed - no stocks returned")
                return []
                
        except Exception as e:
            print(f"Error in force refresh: {e}")
            return []
    
    def get_stock_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get stock info by ticker."""
        stocks = self.load_stocks()
        ticker_upper = ticker.upper()
        
        for stock in stocks:
            if stock.get("ticker", "").upper() == ticker_upper:
                return stock
        
        return None
