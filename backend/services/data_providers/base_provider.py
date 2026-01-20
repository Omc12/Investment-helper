"""
Base provider interface for stock data sources.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class StockDataProvider(ABC):
    """Abstract base class for stock data providers."""
    
    def __init__(self, name: str, priority: int = 100):
        self.name = name
        self.priority = priority  # Lower number = higher priority
        self.is_available = True
        self.error_count = 0
        self.max_errors = 5  # Disable provider after 5 consecutive errors
    
    @abstractmethod
    async def fetch_stock_data(self, symbols: List[str]) -> List[Dict]:
        """Fetch stock data for given symbols."""
        pass
    
    @abstractmethod
    def get_supported_markets(self) -> List[str]:
        """Return list of supported markets (e.g., ['NSE', 'BSE'])."""
        pass
    
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Return True if provider requires API key."""
        pass
    
    def on_success(self):
        """Called when provider successfully fetches data."""
        self.error_count = 0
        self.is_available = True
        logger.info(f"Provider {self.name} successfully fetched data")
    
    def on_error(self, error: Exception):
        """Called when provider encounters an error."""
        self.error_count += 1
        logger.warning(f"Provider {self.name} error ({self.error_count}/{self.max_errors}): {error}")
        
        if self.error_count >= self.max_errors:
            self.is_available = False
            logger.error(f"Provider {self.name} disabled after {self.max_errors} errors")
    
    def reset_errors(self):
        """Reset error count and re-enable provider."""
        self.error_count = 0
        self.is_available = True
        logger.info(f"Provider {self.name} reset and re-enabled")