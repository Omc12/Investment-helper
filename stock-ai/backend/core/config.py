"""
Configuration settings for the stock prediction API.
"""

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
API_TITLE = "Indian Stock Predictor API"
API_VERSION = "2.0"

# CORS Settings
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

# Cache Settings (in seconds)
CACHE_STOCK_DETAILS = 300  # 5 minutes
CACHE_CANDLES_DAILY = 1800  # 30 minutes
CACHE_CANDLES_INTRADAY = 30  # 30 seconds
CACHE_MODEL = 600  # 10 minutes
CACHE_STOCK_LIST = 3600  # 1 hour

# Data Settings
STOCKS_JSON_PATH = "data/stocks_nse.json"

# Model Settings
MODEL_LOOKBACK_YEARS = 2
MODEL_FEATURES = [
    "Return1", "Return5", "Return10", "Return20", "LogReturn1",
    "Volatility10", "Volatility20",
    "SMA10", "SMA20", "SMA50",
    "EMA10", "EMA20",
    "RSI14",
    "MACD", "MACD_Signal",
    "Stochastic_K", "Stochastic_D",
    "BB_Upper", "BB_Lower", "BB_Width",
    "ATR14",
    "HL_Range",
    "Gap",
    "Volume_Change",
    "Volume_SMA20",
    "Volume_Ratio"
]

# Confidence thresholds
CONFIDENCE_HIGH = 0.65
CONFIDENCE_MEDIUM = 0.55

# Default chart settings
DEFAULT_CHART_PERIOD = "6mo"
DEFAULT_CHART_INTERVAL = "1d"
