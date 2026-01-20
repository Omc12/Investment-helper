"""
Multi-provider stock fetcher with automatic fallback.
"""
import asyncio
from typing import List, Dict, Optional
import logging
from .data_providers.base_provider import StockDataProvider
from .data_providers.yfinance_provider import YFinanceDirectProvider
from .data_providers.local_provider import LocalDatabaseProvider
# Optional providers (may have import issues)
try:
    from .data_providers.yahoo_provider import YahooFinanceProvider
    HAS_YAHOO = True
except ImportError:
    HAS_YAHOO = False
    
try:
    from .data_providers.alphavantage_provider import AlphaVantageProvider  
    HAS_ALPHAVANTAGE = True
except ImportError:
    HAS_ALPHAVANTAGE = False
    
try:
    from .data_providers.finnhub_provider import FinnhubProvider
    HAS_FINNHUB = True
except ImportError:
    HAS_FINNHUB = False

logger = logging.getLogger(__name__)

class MultiProviderStockFetcher:
    """Manages multiple stock data providers with automatic fallback."""
    
    def __init__(self, local_db_path: str):
        self.providers: List[StockDataProvider] = []
        self.local_db_path = local_db_path
        self._setup_providers()
    
    def _setup_providers(self):
        """Initialize all available providers in priority order (LOCAL + DIRECT API)."""
        # Core providers that should always work
        self.providers.extend([
            LocalDatabaseProvider(self.local_db_path),  # Priority 1 (FASTEST)
            YFinanceDirectProvider(),                   # Priority 5 (RELIABLE)
        ])
        
        # Optional providers
        if HAS_ALPHAVANTAGE:
            self.providers.append(AlphaVantageProvider())  # Priority 10
        if HAS_FINNHUB:
            self.providers.append(FinnhubProvider())       # Priority 15
        if HAS_YAHOO:
            self.providers.append(YahooFinanceProvider())  # Priority 20
        
        # Sort by priority (lower number = higher priority)
        self.providers.sort(key=lambda p: p.priority)
        
        logger.info(f"Initialized {len(self.providers)} data providers")
        for provider in self.providers:
            api_key_status = " (needs API key)" if provider.requires_api_key() else ""
            logger.info(f"  - {provider.name} (priority {provider.priority}){api_key_status}")
    
    async def fetch_comprehensive_stocks(self, search_terms: Optional[List[str]] = None) -> List[Dict]:
        """Fetch stock data using the best available provider - handles both tickers and company names."""
        
        # Get available providers
        available_providers = [p for p in self.providers if p.is_available]
        
        if not available_providers:
            logger.error("No providers available!")
            return []
        
        logger.info(f"Trying {len(available_providers)} available providers...")
        
        # Separate ticker symbols from company names
        ticker_symbols = []
        company_names = []
        
        if search_terms:
            for term in search_terms:
                # If it has spaces or is too long, likely a company name
                if ' ' in term or (len(term) > 10 and not term.endswith(('.NS', '.BO'))):
                    company_names.append(term)
                else:
                    ticker_symbols.append(term)
        
        all_results = []
        providers_tried = 0
        providers_failed = 0
        
        for provider in available_providers:
            try:
                providers_tried += 1
                print(f"[Provider {providers_tried}/{len(available_providers)}] Trying {provider.name}...")
                logger.info(f"Attempting to fetch data using {provider.name}...")
                
                if isinstance(provider, LocalDatabaseProvider) and search_terms:
                    # Skip local database for specific searches (already searched in main method)
                    print(f"  Skipping {provider.name} (already searched locally)")
                    logger.info("Skipping local database for API search")
                    continue
                elif isinstance(provider, LocalDatabaseProvider):
                    # Local database without specific search terms - return all
                    stocks = await provider.fetch_stock_data()
                else:
                    # API providers - search with both tickers and company names
                    stocks = []
                    
                    # Try ticker symbols first (more reliable)
                    if ticker_symbols:
                        try:
                            print(f"  {provider.name}: Searching for tickers {ticker_symbols[:3]}...")
                            ticker_results = await provider.fetch_stock_data(ticker_symbols)
                            if ticker_results:
                                stocks.extend(ticker_results)
                                print(f"  ✓ {provider.name} found {len(ticker_results)} results via ticker search")
                                logger.info(f"{provider.name} found {len(ticker_results)} results via ticker search")
                        except Exception as e:
                            print(f"  ✗ {provider.name} ticker search failed: {str(e)[:100]}")
                            logger.warning(f"{provider.name} ticker search failed: {e}")
                    
                    # Try company name search if supported and no ticker results
                    if company_names and len(stocks) < 3:
                        try:
                            # Some providers may support name-based search
                            for name in company_names[:3]:  # Limit to prevent too many API calls
                                print(f"  {provider.name}: Searching for name '{name}'...")
                                name_results = await provider.fetch_stock_data([name])
                                if name_results:
                                    stocks.extend(name_results)
                                    print(f"  ✓ {provider.name} found {len(name_results)} results for '{name}'")
                                    logger.info(f"{provider.name} found {len(name_results)} results for '{name}'")
                        except Exception as e:
                            print(f"  ✗ {provider.name} name search failed: {str(e)[:100]}")
                            logger.warning(f"{provider.name} name search failed: {e}")
                    
                    # Fallback to default symbols if nothing found
                    if not stocks and not search_terms:
                        stocks = await provider.fetch_stock_data(self._get_default_symbols())
                
                if stocks and len(stocks) > 0:
                    print(f"  ✓ Successfully got {len(stocks)} stocks from {provider.name}")
                    logger.info(f"Successfully fetched {len(stocks)} stocks from {provider.name}")
                    all_results.extend(stocks)
                    
                    # For API searches, continue trying more providers for better coverage
                    if search_terms and len(all_results) >= 5:  # Got enough results
                        print(f"  Collected {len(all_results)} total results, stopping early")
                        break
                else:
                    providers_failed += 1
                    print(f"  ✗ {provider.name} returned no data")
                    logger.warning(f"{provider.name} returned no data")
                    
            except Exception as e:
                providers_failed += 1
                print(f"  ✗ Provider {provider.name} failed with error: {str(e)[:100]}")
                logger.error(f"Provider {provider.name} failed: {e}")
                provider.on_error(e)
                continue
        
        print(f"Provider Summary: {providers_tried} tried, {providers_failed} failed, {len(all_results)} results")

        
        if all_results:
            # Remove duplicates based on ticker
            seen_tickers = set()
            unique_results = []
            for stock in all_results:
                ticker = stock.get('ticker', '')
                if ticker and ticker not in seen_tickers:
                    unique_results.append(stock)
                    seen_tickers.add(ticker)
            
            logger.info(f"Returning {len(unique_results)} unique results from {len(all_results)} total")
            return unique_results
        
        logger.error("All providers failed to fetch data")
        return []
    
    def _get_default_symbols(self) -> List[str]:
        """Get default NSE symbols for API providers."""
        return [
            # NIFTY 50 major stocks
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'BHARTIARTL.NS', 'ICICIBANK.NS',
            'SBIN.NS', 'INFY.NS', 'LT.NS', 'ITC.NS', 'HINDUNILVR.NS',
            'KOTAKBANK.NS', 'HDFC.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'MARUTI.NS',
            'ASIANPAINT.NS', 'HCLTECH.NS', 'WIPRO.NS', 'ULTRACEMCO.NS', 'DMART.NS',
            'TITAN.NS', 'NESTLEIND.NS', 'TECHM.NS', 'POWERGRID.NS', 'M&M.NS',
            'ONGC.NS', 'TATAMOTORS.NS', 'NTPC.NS', 'JSWSTEEL.NS', 'INDUSINDBK.NS',
            'BAJAJFINSV.NS', 'HDFCLIFE.NS', 'GRASIM.NS', 'COALINDIA.NS', 'BRITANNIA.NS',
            'SBILIFE.NS', 'EICHERMOT.NS', 'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS',
            'DIVISLAB.NS', 'ADANIENT.NS', 'TATASTEEL.NS', 'APOLLOHOSP.NS', 'BAJAJ-AUTO.NS',
            'HEROMOTOCO.NS', 'UPL.NS', 'TRENT.NS', 'ADANIPORTS.NS', 'BPCL.NS',
            
            # Recent IPOs
            'ZOMATO.NS', 'NYKAA.NS', 'PAYTM.NS', 'IRCTC.NS', 'POLICYBZR.NS',
            'LATENTVIEW.NS', 'CAMS.NS', 'ROUTE.NS', 'HAPPSTMNDS.NS', 'INDIGO.NS'
        ]
    
    def get_provider_status(self) -> Dict[str, Dict]:
        """Get status of all providers."""
        status = {}
        for provider in self.providers:
            status[provider.name] = {
                'available': provider.is_available,
                'priority': provider.priority,
                'error_count': provider.error_count,
                'requires_api_key': provider.requires_api_key(),
                'supported_markets': provider.get_supported_markets()
            }
        return status
    
    def reset_provider_errors(self, provider_name: Optional[str] = None):
        """Reset errors for a specific provider or all providers."""
        if provider_name:
            for provider in self.providers:
                if provider.name == provider_name:
                    provider.reset_errors()
                    break
        else:
            for provider in self.providers:
                provider.reset_errors()
        
        logger.info(f"Reset errors for {provider_name or 'all providers'}")
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers."""
        health = {}
        
        for provider in self.providers:
            try:
                if isinstance(provider, LocalDatabaseProvider):
                    # Quick check for local database
                    result = await provider.fetch_stock_data()
                    health[provider.name] = len(result) > 0
                else:
                    # Quick test for API providers
                    result = await provider.fetch_stock_data(['RELIANCE.NS'])
                    health[provider.name] = len(result) > 0
            except Exception as e:
                logger.debug(f"Health check failed for {provider.name}: {e}")
                health[provider.name] = False
        
        return health