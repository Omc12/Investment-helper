"""
Finnhub data provider.
"""
import asyncio
import aiohttp
from typing import List, Dict, Optional
from .base_provider import StockDataProvider
import os
import logging

logger = logging.getLogger(__name__)


class FinnhubProvider(StockDataProvider):
    """Finnhub data provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Finnhub", priority=15)
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY', 'demo')
        self.base_url = "https://finnhub.io/api/v1"
        self.requests_per_minute = 60  # Free tier limit
        self.request_delay = 1  # 1 second between requests
    
    async def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """Fetch stock data from Finnhub."""
        stocks = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            for i, symbol in enumerate(symbols[:30]):  # Reasonable limit
                try:
                    stock_data = await self._fetch_single_stock(session, symbol)
                    if stock_data:
                        stocks.append(stock_data)
                    
                    # Rate limiting
                    if i < len(symbols) - 1:
                        await asyncio.sleep(self.request_delay)
                        
                except Exception as e:
                    logger.debug(f"Failed to fetch {symbol} from Finnhub: {e}")
                    continue
        
        if stocks:
            self.on_success()
        else:
            self.on_error(Exception("No stocks fetched"))
        
        return stocks
    
    async def _fetch_single_stock(self, session: aiohttp.ClientSession, symbol: str) -> Optional[Dict]:
        """Fetch data for a single stock symbol."""
        # Convert NSE symbol format for Finnhub
        clean_symbol = symbol.replace('.NS', '')
        
        try:
            # Get quote data
            quote_url = f"{self.base_url}/quote"
            quote_params = {'symbol': clean_symbol, 'token': self.api_key}
            
            async with session.get(quote_url, params=quote_params) as response:
                if response.status == 200:
                    quote_data = await response.json()
                    
                    # Get company profile for additional info
                    profile_url = f"{self.base_url}/stock/profile2"
                    profile_params = {'symbol': clean_symbol, 'token': self.api_key}
                    
                    async with session.get(profile_url, params=profile_params) as profile_response:
                        profile_data = {}
                        if profile_response.status == 200:
                            profile_data = await profile_response.json()
                    
                    return self._parse_finnhub_data(symbol, quote_data, profile_data)
        except Exception as e:
            logger.debug(f"Finnhub request failed for {symbol}: {e}")
        
        return None
    
    def _parse_finnhub_data(self, symbol: str, quote_data: Dict, profile_data: Dict) -> Optional[Dict]:
        """Parse Finnhub response data."""
        try:
            current_price = quote_data.get('c', 0)  # Current price
            
            if current_price <= 0:
                return None
            
            return {
                'ticker': symbol,
                'name': profile_data.get('name', symbol.replace('.NS', '')),
                'sector': self._map_sector(profile_data.get('finnhubIndustry', 'Unknown')),
                'market_cap': profile_data.get('marketCapitalization', 0) * 1000000,  # Convert to actual value
                'last_price': current_price
            }
        except Exception as e:
            logger.debug(f"Failed to parse Finnhub data for {symbol}: {e}")
            return None
    
    def _map_sector(self, finnhub_industry: str) -> str:
        """Map Finnhub industries to our standard sectors."""
        sector_mapping = {
            'Technology': 'Technology',
            'Health Care': 'Healthcare',
            'Financials': 'Financials',
            'Energy': 'Energy',
            'Consumer Discretionary': 'Consumer Goods',
            'Consumer Staples': 'Consumer Goods',
            'Materials': 'Materials',
            'Real Estate': 'Real Estate',
            'Communication Services': 'Communication',
            'Utilities': 'Utilities',
            'Industrials': 'Industrials'
        }
        return sector_mapping.get(finnhub_industry, 'Other')
    
    def get_supported_markets(self) -> List[str]:
        return ['NSE', 'BSE', 'NASDAQ', 'NYSE', 'LSE']
    
    def requires_api_key(self) -> bool:
        return True