"""
Price Updater Service - Fetches and stores real market prices
Updates a JSON file with the last known good prices from Yahoo Finance
"""
import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, Optional

# Path to store the latest prices
PRICES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'latest_prices.json')


class PriceUpdater:
    """Updates and stores the latest market prices."""
    
    # Default prices in case file doesn't exist (Jan 2026 estimates)
    DEFAULT_PRICES = {
        "^NSEI": {
            "name": "NIFTY 50",
            "currentPrice": 24856.70,
            "previousClose": 24723.45,
            "dayHigh": 24912.30,
            "dayLow": 24685.20,
            "sector": "Index",
            "industry": "Market Index"
        },
        "^NSEBANK": {
            "name": "BANK NIFTY", 
            "currentPrice": 52345.85,
            "previousClose": 52087.60,
            "dayHigh": 52498.90,
            "dayLow": 51965.40,
            "sector": "Index",
            "industry": "Banking Index"
        },
        "RELIANCE.NS": {
            "name": "Reliance Industries Limited",
            "currentPrice": 2876.45,
            "previousClose": 2862.30,
            "dayHigh": 2891.80,
            "dayLow": 2854.15,
            "sector": "Oil & Gas",
            "industry": "Oil & Gas Refining & Marketing"
        },
        "TCS.NS": {
            "name": "Tata Consultancy Services Limited",
            "currentPrice": 4285.60,
            "previousClose": 4267.85,
            "dayHigh": 4302.40,
            "dayLow": 4251.70,
            "sector": "Information Technology",
            "industry": "IT Services"
        },
        "HDFCBANK.NS": {
            "name": "HDFC Bank Limited",
            "currentPrice": 1756.35,
            "previousClose": 1748.20,
            "dayHigh": 1768.90,
            "dayLow": 1741.55,
            "sector": "Financial Services",
            "industry": "Private Sector Bank"
        },
        "INFY.NS": {
            "name": "Infosys Limited",
            "currentPrice": 1892.70,
            "previousClose": 1878.45,
            "dayHigh": 1905.30,
            "dayLow": 1871.85,
            "sector": "Information Technology",
            "industry": "IT Services"
        },
        "ICICIBANK.NS": {
            "name": "ICICI Bank Limited",
            "currentPrice": 1298.45,
            "previousClose": 1289.30,
            "dayHigh": 1308.70,
            "dayLow": 1282.95,
            "sector": "Financial Services",
            "industry": "Private Sector Bank"
        },
        "BHARTIARTL.NS": {
            "name": "Bharti Airtel Limited",
            "currentPrice": 1654.80,
            "previousClose": 1642.55,
            "dayHigh": 1665.40,
            "dayLow": 1638.20,
            "sector": "Telecommunication",
            "industry": "Telecom Services"
        },
        "SBIN.NS": {
            "name": "State Bank of India",
            "currentPrice": 876.25,
            "previousClose": 869.80,
            "dayHigh": 882.60,
            "dayLow": 865.45,
            "sector": "Financial Services",
            "industry": "Public Sector Bank"
        },
        "LT.NS": {
            "name": "Larsen & Toubro Limited",
            "currentPrice": 3742.90,
            "previousClose": 3725.45,
            "dayHigh": 3768.35,
            "dayLow": 3712.80,
            "sector": "Construction",
            "industry": "Construction & Engineering"
        },
        "ITC.NS": {
            "name": "ITC Limited",
            "currentPrice": 492.35,
            "previousClose": 489.70,
            "dayHigh": 496.80,
            "dayLow": 487.25,
            "sector": "FMCG",
            "industry": "Tobacco & Cigarettes"
        },
        "HINDUNILVR.NS": {
            "name": "Hindustan Unilever Limited",
            "currentPrice": 2578.40,
            "previousClose": 2564.85,
            "dayHigh": 2592.70,
            "dayLow": 2556.30,
            "sector": "FMCG",
            "industry": "Personal Care"
        },
        "BAJFINANCE.NS": {
            "name": "Bajaj Finance Limited",
            "currentPrice": 7234.65,
            "previousClose": 7198.40,
            "dayHigh": 7278.90,
            "dayLow": 7165.25,
            "sector": "Financial Services",
            "industry": "NBFC"
        }
    }
    
    _cached_prices: Dict = {}
    _last_update: Optional[datetime] = None
    _update_lock = threading.Lock()
    
    @classmethod
    def load_prices(cls) -> Dict:
        """Load prices from file or use defaults."""
        try:
            if os.path.exists(PRICES_FILE):
                with open(PRICES_FILE, 'r') as f:
                    data = json.load(f)
                    cls._cached_prices = data.get('prices', cls.DEFAULT_PRICES)
                    cls._last_update = datetime.fromisoformat(data.get('last_update', ''))
                    return cls._cached_prices
        except Exception as e:
            print(f"Error loading prices: {e}")
        
        cls._cached_prices = cls.DEFAULT_PRICES.copy()
        return cls._cached_prices
    
    @classmethod
    def save_prices(cls, prices: Dict) -> None:
        """Save prices to file."""
        try:
            os.makedirs(os.path.dirname(PRICES_FILE), exist_ok=True)
            with open(PRICES_FILE, 'w') as f:
                json.dump({
                    'prices': prices,
                    'last_update': datetime.now().isoformat()
                }, f, indent=2)
            print(f"Saved {len(prices)} prices to {PRICES_FILE}")
        except Exception as e:
            print(f"Error saving prices: {e}")
    
    @classmethod
    def get_price(cls, ticker: str) -> Optional[Dict]:
        """Get cached price for a ticker."""
        if not cls._cached_prices:
            cls.load_prices()
        return cls._cached_prices.get(ticker)
    
    @classmethod
    def update_price(cls, ticker: str, price_data: Dict) -> None:
        """Update price for a single ticker."""
        with cls._update_lock:
            if not cls._cached_prices:
                cls.load_prices()
            cls._cached_prices[ticker] = price_data
    
    @classmethod
    def fetch_and_update_all(cls) -> int:
        """Fetch real prices from Yahoo Finance and update cache."""
        import yfinance as yf
        
        tickers = list(cls.DEFAULT_PRICES.keys())
        updated = 0
        
        print(f"Fetching real prices for {len(tickers)} tickers...")
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if info and (info.get('currentPrice') or info.get('regularMarketPrice')):
                    price_data = {
                        "name": info.get('longName') or info.get('shortName') or cls.DEFAULT_PRICES.get(ticker, {}).get('name', ticker),
                        "currentPrice": info.get('currentPrice') or info.get('regularMarketPrice'),
                        "previousClose": info.get('previousClose') or info.get('regularMarketPreviousClose'),
                        "dayHigh": info.get('dayHigh') or info.get('regularMarketDayHigh'),
                        "dayLow": info.get('dayLow') or info.get('regularMarketDayLow'),
                        "sector": info.get('sector') or cls.DEFAULT_PRICES.get(ticker, {}).get('sector', 'N/A'),
                        "industry": info.get('industry') or cls.DEFAULT_PRICES.get(ticker, {}).get('industry', 'N/A'),
                        "marketCap": info.get('marketCap'),
                        "volume": info.get('volume'),
                        "fiftyTwoWeekHigh": info.get('fiftyTwoWeekHigh'),
                        "fiftyTwoWeekLow": info.get('fiftyTwoWeekLow'),
                    }
                    cls.update_price(ticker, price_data)
                    updated += 1
                    print(f"Updated {ticker}: ₹{price_data['currentPrice']}")
                    
            except Exception as e:
                print(f"Failed to fetch {ticker}: {e}")
                continue
        
        # Save updated prices
        if updated > 0:
            cls.save_prices(cls._cached_prices)
            cls._last_update = datetime.now()
        
        print(f"Updated {updated}/{len(tickers)} prices")
        return updated


# Background thread to update prices periodically
def start_price_updater(interval_minutes: int = 15):
    """Start background thread to update prices periodically."""
    def update_loop():
        while True:
            try:
                PriceUpdater.fetch_and_update_all()
            except Exception as e:
                print(f"Price update error: {e}")
            time.sleep(interval_minutes * 60)
    
    thread = threading.Thread(target=update_loop, daemon=True)
    thread.start()
    print(f"Price updater started (updates every {interval_minutes} minutes)")


# Load prices on module import
PriceUpdater.load_prices()
