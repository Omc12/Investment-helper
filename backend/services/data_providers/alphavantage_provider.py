"""
Alpha Vantage data provider.
"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from .base_provider import StockDataProvider
import os
import logging

logger = logging.getLogger(__name__)


class AlphaVantageProvider(StockDataProvider):
    """Alpha Vantage data provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Alpha Vantage", priority=10)  # Higher priority than Yahoo
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
        self.requests_per_minute = 5  # Free tier limit
        self.request_delay = 12  # 60/5 = 12 seconds between requests
    
    async def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """Fetch stock data from Alpha Vantage."""
        stocks = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            for i, symbol in enumerate(symbols[:20]):  # Limit for free tier
                try:
                    stock_data = await self._fetch_single_stock(session, symbol)
                    if stock_data:
                        stocks.append(stock_data)
                    
                    # Rate limiting for free tier
                    if i < len(symbols) - 1:
                        await asyncio.sleep(self.request_delay)
                        
                except Exception as e:
                    logger.debug(f"Failed to fetch {symbol} from Alpha Vantage: {e}")
                    continue
        
        if stocks:
            self.on_success()
        else:
            self.on_error(Exception("No stocks fetched"))
        
        return stocks
    
    async def _fetch_single_stock(self, session: aiohttp.ClientSession, symbol: str) -> Optional[Dict]:
        """Fetch data for a single stock symbol."""
        # Convert NSE symbol format
        clean_symbol = symbol.replace('.NS', '')
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': clean_symbol,
            'apikey': self.api_key
        }
        
        try:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_alphavantage_data(symbol, data)
        except Exception as e:
            logger.debug(f"Alpha Vantage request failed for {symbol}: {e}")
        
        return None
    
    def _parse_alphavantage_data(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Parse Alpha Vantage response data."""
        try:
            quote = data.get('Global Quote', {})
            
            if not quote:
                return None
            
            return {
                'ticker': symbol,
                'name': quote.get('01. symbol', symbol.replace('.NS', '')),
                'sector': 'Unknown',  # Alpha Vantage doesn't provide sector in quote
                'market_cap': 0,  # Not available in basic quote
                'last_price': float(quote.get('05. price', 0))
            }
        except Exception as e:
            logger.debug(f"Failed to parse Alpha Vantage data for {symbol}: {e}")
            return None
    
    def get_supported_markets(self) -> List[str]:
        return ['NSE', 'BSE', 'NASDAQ', 'NYSE', 'LSE', 'TSX']
    
    def requires_api_key(self) -> bool:
        return True