"""
Feature engineering functions for stock prediction.
"""
import pandas as pd
import numpy as np
from typing import List


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI (Relative Strength Index)."""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / (avg_loss + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def compute_ema(series: pd.Series, period: int) -> pd.Series:
    """Compute Exponential Moving Average."""
    return series.ewm(span=period, adjust=False).mean()


def compute_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Compute MACD and Signal line."""
    ema_fast = compute_ema(close, fast)
    ema_slow = compute_ema(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)
    return macd_line, signal_line


def compute_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """Compute Stochastic Oscillator %K and %D."""
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()
    
    stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-9)
    stoch_d = stoch_k.rolling(window=3).mean()
    
    return stoch_k, stoch_d


def compute_bollinger_bands(close: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Compute Bollinger Bands."""
    sma = close.rolling(window=period).mean()
    rolling_std = close.rolling(window=period).std()
    upper_band = sma + (std_dev * rolling_std)
    lower_band = sma - (std_dev * rolling_std)
    bb_width = (upper_band - lower_band) / (sma + 1e-9)
    return upper_band, lower_band, bb_width


def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Compute Average True Range."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = abs(high - prev_close)
    tr3 = abs(low - prev_close)
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer all features for the model.
    
    Args:
        df: DataFrame with OHLCV columns
    
    Returns:
        DataFrame with all engineered features
    """
    data = df.copy()
    
    # Price returns
    data['Return1'] = data['Close'].pct_change()
    data['Return5'] = data['Close'].pct_change(5)
    data['Return10'] = data['Close'].pct_change(10)
    data['Return20'] = data['Close'].pct_change(20)
    data['LogReturn1'] = np.log(data['Close'] / data['Close'].shift(1))
    
    # Volatility
    data['Volatility10'] = data['Return1'].rolling(10).std()
    data['Volatility20'] = data['Return1'].rolling(20).std()
    
    # Simple Moving Averages
    data['SMA10'] = data['Close'].rolling(10).mean()
    data['SMA20'] = data['Close'].rolling(20).mean()
    data['SMA50'] = data['Close'].rolling(50).mean()
    
    # Exponential Moving Averages
    data['EMA10'] = compute_ema(data['Close'], 10)
    data['EMA20'] = compute_ema(data['Close'], 20)
    
    # RSI
    data['RSI14'] = compute_rsi(data['Close'], period=14)
    
    # MACD
    data['MACD'], data['MACD_Signal'] = compute_macd(data['Close'], 12, 26, 9)
    
    # Stochastic
    data['Stochastic_K'], data['Stochastic_D'] = compute_stochastic(
        data['High'], data['Low'], data['Close'], 14
    )
    
    # Bollinger Bands
    data['BB_Upper'], data['BB_Lower'], data['BB_Width'] = compute_bollinger_bands(data['Close'], 20)
    
    # ATR
    data['ATR14'] = compute_atr(data['High'], data['Low'], data['Close'], 14)
    
    # High-Low Range
    data['HL_Range'] = (data['High'] - data['Low']) / (data['Close'] + 1e-9)
    
    # Gap
    data['Gap'] = (data['Open'] - data['Close'].shift(1)) / (data['Close'].shift(1) + 1e-9)
    
    # Volume features
    data['Volume_Change'] = data['Volume'].pct_change()
    data['Volume_SMA20'] = data['Volume'].rolling(20).mean()
    data['Volume_Ratio'] = data['Volume'] / (data['Volume_SMA20'] + 1e-9)
    
    # Target: next day direction
    data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)
    
    return data


def get_feature_columns() -> List[str]:
    """Get list of feature column names."""
    return [
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
