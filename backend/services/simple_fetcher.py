"""
Simplified stock fetcher using only YFinance Direct.
Replaces the complex multi-provider system since we only need Yahoo Finance.
"""
import asyncio
from typing import List, Dict, Optional
import logging
from .data_providers.base_provider import StockDataProvider
from .data_providers.yfinance_provider import YFinanceDirectProvider

logger = logging.getLogger(__name__)


class SimpleStockFetcher:
    """Simplified stock fetcher using only Yahoo Finance."""
    
    def __init__(self, stocks_json_path: str):
        """Initialize with single YFinance provider."""
        self.stocks_json_path = stocks_json_path
        self.provider = YFinanceDirectProvider()
        self.provider.priority = 1  # Highest priority
        
    async def fetch_stocks(self, symbols: List[str], limit: int = 50) -> List[Dict]:
        """Fetch stock data using Yahoo Finance."""
        try:
            # Get stocks from provider
            stocks = await self.provider.get_stocks(symbols, limit)
            return stocks if stocks else []
            
        except Exception as e:
            logger.error(f"Error fetching stocks: {e}")
            return []
    
    async def search_stocks(self, query: str, limit: int = 20) -> List[Dict]:
        """Search stocks using Yahoo Finance."""
        try:
            # Use provider search if available
            if hasattr(self.provider, 'search_stocks'):
                results = await self.provider.search_stocks(query, limit)
                return results if results else []
            
            # Fallback: fetch default symbols and filter
            symbols = self._get_default_symbols()
            filtered = [s for s in symbols if query.upper() in s][:limit]
            return await self.fetch_stocks(filtered, limit)
            
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []
    
    def get_provider_status(self) -> List[Dict]:
        """Get status of the single provider."""
        return [{
            "name": "YFinanceDirectProvider",
            "priority": 1,
            "active": True,
            "error_count": 0,
            "last_error": None
        }]
    
    async def health_check(self) -> List[Dict]:
        """Basic health check."""
        try:
            # Test with a common symbol
            result = await self.provider.get_stocks(['RELIANCE.NS'], 1)
            healthy = result is not None and len(result) > 0
        except Exception:
            healthy = False
            
        return [{
            "provider": "YFinanceDirectProvider",
            "healthy": healthy,
            "status": "OK" if healthy else "ERROR"
        }]
    
    def reset_provider_errors(self, provider_name: str = None):
        """Reset provider errors (no-op for simplified version)."""
        pass
    
    def reset_all_provider_errors(self):
        """Reset all provider errors (no-op for simplified version).""" 
        pass
    
    def _get_default_symbols(self) -> List[str]:
        """Get default NSE symbols."""
        return [
            # Major NSE stocks
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HDFC.NS',
            'ICICIBANK.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS', 'ITC.NS', 'LT.NS',
            'SBIN.NS', 'WIPRO.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'HCLTECH.NS',
            'AXISBANK.NS', 'ONGC.NS', 'ULTRACEMCO.NS', 'TITAN.NS', 'SUNPHARMA.NS',
            'NESTLEIND.NS', 'POWERGRID.NS', 'NTPC.NS', 'TECHM.NS', 'M&M.NS',
            'BAJFINANCE.NS', 'HDFCLIFE.NS', 'COALINDIA.NS', 'DRREDDY.NS', 'GRASIM.NS',
        ]