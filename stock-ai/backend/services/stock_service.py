"""
Stock data service for loading and searching stock lists.
"""
import json
import os
from typing import List, Dict, Optional
from core.cache import stock_list_cache, cached


class StockService:
    """Service for managing stock lists."""
    
    def __init__(self, stocks_json_path: str):
        self.stocks_json_path = stocks_json_path
        self._stocks_cache = None
    
    @cached(stock_list_cache, key_func=lambda self: "all_stocks")
    def load_stocks(self) -> List[Dict]:
        """Load stocks from JSON file with caching."""
        if not os.path.exists(self.stocks_json_path):
            return []
        
        try:
            with open(self.stocks_json_path, 'r', encoding='utf-8') as f:
                stocks = json.load(f)
            return stocks
        except Exception as e:
            print(f"Error loading stocks: {e}")
            return []
    
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
    
    def get_stock_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Get stock info by ticker."""
        stocks = self.load_stocks()
        ticker_upper = ticker.upper()
        
        for stock in stocks:
            if stock.get("ticker", "").upper() == ticker_upper:
                return stock
        
        return None
