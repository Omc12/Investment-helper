"""
YFinance direct provider for individual stock lookups.
"""
import yfinance as yf
from typing import List, Dict, Optional
from .base_provider import StockDataProvider
import logging

logger = logging.getLogger(__name__)


class YFinanceDirectProvider(StockDataProvider):
    """Direct yfinance provider for individual stock lookups."""
    
    def __init__(self):
        super().__init__("YFinance Direct", priority=5)  # High priority for direct lookups
    
    async def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """Fetch individual stocks using yfinance directly."""
        stocks = []
        errors = 0
        
        for symbol in symbols[:10]:  # Limit to 10 symbols for speed
            try:
                stock_info = self._fetch_single_stock_yfinance(symbol)
                if stock_info:
                    stocks.append(stock_info)
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                error_msg = str(e).lower()
                # Check for rate limiting indicators
                if any(indicator in error_msg for indicator in ['rate limit', '429', 'too many requests', 'quota']):
                    logger.warning(f"Rate limit detected for {symbol}: {e}")
                    print(f"⚠️  YFinance rate limit detected - triggering fallback to other providers")
                    self.on_error(e)  # Mark as error to potentially disable provider
                    break  # Stop trying more symbols if rate limited
                logger.debug(f"Failed to fetch {symbol} via yfinance: {e}")
                continue
        
        # If most requests failed, it might be rate limiting
        if errors > len(symbols) * 0.7 and errors > 2:
            logger.warning(f"YFinance: High failure rate ({errors}/{len(symbols)}) - possible rate limiting")
            print(f"⚠️  YFinance high failure rate - may be rate limited")
        
        if stocks:
            self.on_success()
        return stocks
    
    def _fetch_single_stock_yfinance(self, symbol: str) -> Optional[Dict]:
        """Fetch single stock using yfinance."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid data
            if not info or 'symbol' not in info:
                return None
            
            # Get current price
            hist = ticker.history(period="1d")
            current_price = 0.0
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
            
            return {
                'ticker': symbol,
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': self._map_sector(info.get('sector', 'Unknown')),
                'market_cap': info.get('marketCap', 0),
                'last_price': current_price or info.get('currentPrice', 0.0)
            }
            
        except Exception as e:
            logger.debug(f"YFinance error for {symbol}: {e}")
            return None
    
    def _map_sector(self, sector: str) -> str:
        """Map YFinance sectors to our standard sectors."""
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
        return sector_mapping.get(sector, 'Other')
    
    def get_supported_markets(self) -> List[str]:
        return ['NSE', 'BSE', 'NASDAQ', 'NYSE', 'LSE', 'TSX']
    
    def requires_api_key(self) -> bool:
        return False