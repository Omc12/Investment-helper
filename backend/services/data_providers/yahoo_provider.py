"""
Yahoo Finance data provider with improved error handling.
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Optional
from .base_provider import StockDataProvider
import logging

logger = logging.getLogger(__name__)


class YahooFinanceProvider(StockDataProvider):
    """Yahoo Finance data provider with multiple endpoints."""
    
    def __init__(self):
        super().__init__("Yahoo Finance", priority=20)
        self.base_urls = [
            "https://query1.finance.yahoo.com/v8/finance/chart",
            "https://query2.finance.yahoo.com/v8/finance/chart",
            "https://finance.yahoo.com/quote"  # Alternative endpoint
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """Fetch stock data from Yahoo Finance."""
        stocks = []
        
        async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout(total=30)) as session:
            for symbol in symbols[:50]:  # Limit batch size
                try:
                    stock_data = await self._fetch_single_stock(session, symbol)
                    if stock_data:
                        stocks.append(stock_data)
                except Exception as e:
                    logger.debug(f"Failed to fetch {symbol} from Yahoo: {e}")
                    continue
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
        
        if stocks:
            self.on_success()
        else:
            self.on_error(Exception("No stocks fetched"))
        
        return stocks
    
    async def _fetch_single_stock(self, session: aiohttp.ClientSession, symbol: str) -> Optional[Dict]:
        """Fetch data for a single stock symbol."""
        for base_url in self.base_urls:
            try:
                url = f"{base_url}/{symbol}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_yahoo_data(symbol, data)
            except Exception as e:
                logger.debug(f"Yahoo endpoint {base_url} failed for {symbol}: {e}")
                continue
        
        return None
    
    def _parse_yahoo_data(self, symbol: str, data: Dict) -> Optional[Dict]:
        """Parse Yahoo Finance response data."""
        try:
            chart = data.get('chart', {})
            result = chart.get('result', [{}])[0]
            meta = result.get('meta', {})
            
            return {
                'ticker': symbol,
                'name': meta.get('longName', symbol.replace('.NS', '')),
                'sector': self._map_sector(meta.get('sector', 'Unknown')),
                'market_cap': meta.get('marketCap', 0),
                'last_price': meta.get('regularMarketPrice', 0.0)
            }
        except Exception as e:
            logger.debug(f"Failed to parse Yahoo data for {symbol}: {e}")
            return None
    
    def _map_sector(self, yahoo_sector: str) -> str:
        """Map Yahoo Finance sectors to our standard sectors."""
        sector_mapping = {
            'Technology': 'Technology',
            'Healthcare': 'Healthcare',
            'Financial Services': 'Financials',
            'Energy': 'Energy',
            'Consumer Cyclical': 'Consumer Goods',
            'Consumer Defensive': 'Consumer Goods',
            'Basic Materials': 'Materials',
            'Real Estate': 'Real Estate',
            'Communication Services': 'Communication',
            'Utilities': 'Utilities',
            'Industrials': 'Industrials'
        }
        return sector_mapping.get(yahoo_sector, 'Other')
    
    def get_supported_markets(self) -> List[str]:
        return ['NSE', 'BSE', 'NASDAQ', 'NYSE']
    
    def requires_api_key(self) -> bool:
        return False