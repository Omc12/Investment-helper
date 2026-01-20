"""
Local JSON database provider (fallback).
"""
import json
import os
from typing import List, Dict
from .base_provider import StockDataProvider
import logging

logger = logging.getLogger(__name__)


class LocalDatabaseProvider(StockDataProvider):
    """Local JSON database provider as primary fast source."""
    
    def __init__(self, json_path: str):
        super().__init__("Local Database", priority=1)  # HIGHEST priority (lowest number)
        self.json_path = json_path
        self.is_available = True  # Always available
    
    async def fetch_stock_data(self, symbols: List[str] = None) -> List[Dict]:
        """Load stock data from local JSON file."""
        try:
            if not os.path.exists(self.json_path):
                raise FileNotFoundError(f"JSON file not found: {self.json_path}")
            
            with open(self.json_path, 'r', encoding='utf-8') as f:
                stocks = json.load(f)
            
            logger.info(f"Loaded {len(stocks)} stocks from local database")
            self.on_success()
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to load local database: {e}")
            self.on_error(e)
            return []
    
    def get_supported_markets(self) -> List[str]:
        return ['NSE', 'BSE']  # Based on our Indian stock database
    
    def requires_api_key(self) -> bool:
        return False
    
    def on_error(self, error: Exception):
        """Local database errors are critical - don't disable."""
        logger.error(f"Local database error: {error}")
        # Don't increment error count or disable - we need this fallback!