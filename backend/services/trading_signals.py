"""
Trading Signals Module - PURE PREDICTION ONLY
No training, no labeling, no CSV loading - just prediction with pre-trained models
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime
import os
import joblib
from pathlib import Path

# Model storage path
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
MODEL_FILE = os.path.join(MODELS_DIR, 'pretrained_trading_model.pkl')

# Configuration
CONF = {
    "PROB_THRESH": 0.6,   # Probability threshold for signals
    "VIX_MIN": 12,        # VIX safe zone minimum
    "VIX_MAX": 25         # VIX safe zone maximum
}

# ==============================================================================
# TECHNICAL INDICATORS (Manual Implementation)
# ==============================================================================
class TechnicalIndicators:
    """Manual implementation of technical indicators"""
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def sma(series: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return series.rolling(window=period).mean()
    
    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return series.ewm(span=period).mean()
    
    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Moving Average Convergence Divergence"""
        exp1 = series.ewm(span=fast).mean()
        exp2 = series.ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line, 
            'histogram': histogram
        }
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(period).mean()

# ==============================================================================
# DATA SERVICES - LIVE DATA ONLY
# ==============================================================================
class SignalDataService:
    """Data fetching services for live predictions"""
    
    @staticmethod
    def fetch_data(ticker: str) -> pd.DataFrame:
        """Fetch live stock + market data for prediction"""
        print(f"[SIGNALS] Fetching {ticker}.NS + NIFTY + INDIAVIX...")
        
        try:
            # Fetch stock data
            print(f"[SIGNALS] Downloading {ticker}.NS...")
            stock = yf.Ticker(f"{ticker}.NS")
            stock_data = stock.history(period="5y")
            print(f"[SIGNALS] Got {len(stock_data)} rows for {ticker}.NS")
            
            if len(stock_data) < 200:
                raise ValueError(f"Insufficient stock data: {len(stock_data)} rows")
            
            # Fetch NIFTY data
            print("[SIGNALS] Downloading NIFTY...")
            nifty = yf.Ticker("^NSEI")
            nifty_data = nifty.history(period="5y")
            print(f"[SIGNALS] Got {len(nifty_data)} rows for NIFTY")
            
            # Fetch VIX data
            print("[SIGNALS] Downloading VIX...")
            vix = yf.Ticker("^INDIAVIX")
            vix_data = vix.history(period="5y")
            print(f"[SIGNALS] Got {len(vix_data)} rows for VIX")
            
            # Merge datasets
            merged = stock_data.copy()
            merged['Nifty'] = nifty_data['Close']
            merged['VIX'] = vix_data['Close'].fillna(15)  # Default VIX if missing
            
            # Clean data
            merged = merged.dropna().round(2)
            
            print(f"[SIGNALS] Successfully fetched {len(merged)} days of merged data")
            return merged
            
        except Exception as e:
            print(f"[SIGNALS] Error fetching {ticker}: {e}")
            raise e

# ==============================================================================
# FEATURE ENGINEERING
# ==============================================================================
class FeatureEngine:
    """Feature engineering for trading signals"""
    
    @staticmethod
    def process(df: pd.DataFrame) -> pd.DataFrame:
        """Create technical features for model input"""
        print("[SIGNALS] Engineering features...")
        
        df = df.copy()
        
        # Technical Indicators
        df['rsi'] = TechnicalIndicators.rsi(df['Close'])
        
        macd_dict = TechnicalIndicators.macd(df['Close'])
        df['macd'] = macd_dict['macd']
        df['macd_hist'] = macd_dict['histogram']
        
        # Moving averages and distances
        df['sma_50'] = TechnicalIndicators.sma(df['Close'], 50)
        df['dist_sma50'] = (df['Close'] - df['sma_50']) / df['sma_50']
        
        # Relative strength vs NIFTY
        stock_ret = df['Close'].pct_change(20)
        nifty_ret = df['Nifty'].pct_change(20) 
        df['rel_str_20'] = (stock_ret - nifty_ret).fillna(0)
        
        # VIX features
        df['vix_level'] = df['VIX']
        df['vix_ma_20'] = TechnicalIndicators.sma(df['VIX'], 20)
        
        # ATR
        df['atr'] = TechnicalIndicators.atr(df['High'], df['Low'], df['Close'])
        
        # Remove rows with NaN values
        df = df.dropna()
        
        print(f"[SIGNALS] Features created: {len(df)} rows remaining")
        return df

# ==============================================================================
# TRADING SIGNAL SYSTEM - PURE PREDICTION ONLY
# ==============================================================================
class TradingSignalSystem:
    """Trading Signal System - PURE PREDICTION ONLY
    
    This class ONLY:
    1. Loads pre-trained models from disk
    2. Makes predictions on live data
    3. No training, no labeling, no CSV loading
    
    For training, use: python train_model.py
    """
    
    def __init__(self):
        self.model = None
        self.features = ['rsi', 'macd', 'macd_hist', 'dist_sma50', 
                         'rel_str_20', 'vix_level', 'atr']
        self.is_trained = False

    def load_model(self, filepath: str = MODEL_FILE):
        """Load pre-trained model from disk"""
        try:
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"No trained model found at {filepath}")
            
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.features = model_data.get('features', self.features)
            self.is_trained = True
            
            metadata = model_data['metadata']
            print(f"[MODEL] ✅ Loaded pre-trained model from disk")
            print(f"[MODEL] 📊 Trained on: {metadata['training_samples']} samples")
            print(f"[MODEL] 🎯 Training AUC: {metadata['training_auc']:.4f}")
            print(f"[MODEL] 📅 Trained on: {metadata['training_date'][:10]}")
            
            return model_data
            
        except Exception as e:
            print(f"[MODEL] ❌ Failed to load model: {e}")
            raise e

    def predict(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Make predictions using pre-trained model - NO LABELING NEEDED
        
        Args:
            df: Live stock data with features
        
        Returns:
            tuple: (predictions_df, prediction_stats)
        """
        # Ensure model is loaded
        if not self.is_trained or self.model is None:
            print("[PREDICTION] Loading pre-trained model...")
            self.load_model()
        
        try:
            if len(df) < 50:
                raise ValueError(f"Insufficient stock data: {len(df)} samples")
            
            # Prepare features (no labels needed for prediction)
            X = df[self.features].fillna(0)
            
            # Generate predictions using the loaded model
            df_pred = df.copy()
            df_pred['prob'] = self.model.predict_proba(X)[:, 1]
            
            # Apply VIX regime filter and generate signals
            mask_vix_ok = (df_pred['vix_level'] >= CONF['VIX_MIN']) & (df_pred['vix_level'] <= CONF['VIX_MAX'])
            df_pred['signal'] = np.where((df_pred['prob'] > CONF["PROB_THRESH"]) & mask_vix_ok, 1, 0)
            
            # Generate prediction statistics
            signals = df_pred[df_pred['signal'] == 1]
            
            prediction_stats = {
                "total_signals": int(len(signals)),
                "avg_probability": float(df_pred['prob'].mean()),
                "max_probability": float(df_pred['prob'].max()),
                "signals_in_last_30_days": int(len(signals.tail(30))),
                "model_loaded_from_disk": True,
                "prediction_only": True,
                "no_training_in_prediction": True
            }
            
            print(f"[PREDICTION] ✅ Prediction completed")
            print(f"[PREDICTION] Signals: {prediction_stats['total_signals']}, Avg Prob: {prediction_stats['avg_probability']:.3f}")
            
            return df_pred, prediction_stats
            
        except Exception as e:
            print(f"[PREDICTION] ❌ Prediction failed: {e}")
            raise e

# ==============================================================================
# MAIN ANALYSIS FUNCTION  
# ==============================================================================
def analyze_stock_signals(ticker: str, use_pretrain: bool = True) -> Dict:
    """
    Main function to analyze a stock and generate trading signals
    PURE PREDICTION - no training or labeling
    
    Args:
        ticker: Stock ticker symbol
        use_pretrain: Legacy parameter (always uses pre-trained model)
    
    Returns:
        Dict with signal, probability, VIX status, and prediction metrics
    """
    try:
        # Step 1: Fetch Live Data
        raw_data = SignalDataService.fetch_data(ticker)
        
        # Step 2: Engineer Features
        processed_data = FeatureEngine.process(raw_data)
        
        # Step 3: Make Prediction using Pre-trained Model (NO LABELS)
        system = TradingSignalSystem()
        result_df, prediction_stats = system.predict(processed_data)
        
        # Step 4: Extract Latest Signal
        last_row = result_df.iloc[-1]
        
        vix_value = float(last_row['vix_level'])
        vix_status = "SAFE" if (CONF['VIX_MIN'] <= vix_value <= CONF['VIX_MAX']) else "DANGER"
        
        return {
            "success": True,
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "current_price": float(last_row['Close']),
            "signal": "BUY" if last_row['signal'] == 1 else "WAIT",
            "probability": float(last_row['prob']),
            "confidence": "HIGH" if last_row['prob'] > 0.70 else "MEDIUM" if last_row['prob'] > 0.60 else "LOW",
            "vix": {
                "current": vix_value,
                "ma_20": float(last_row['vix_ma_20']),
                "status": vix_status,
                "safe_range": f"{CONF['VIX_MIN']}-{CONF['VIX_MAX']}"
            },
            "model": {
                "algorithm": "Pre-trained HistGradientBoostingClassifier",
                "validation": "No validation needed in prediction",
                "pre_trained": True,
                "model_loaded": prediction_stats.get("model_loaded_from_disk", False),
                "prediction_only": prediction_stats.get("prediction_only", True),
                "no_labeling": True,
                "training_method": "Separate train_model.py (not in this file)"
            },
            "prediction": prediction_stats,
            "technicals": {
                "rsi": float(last_row['rsi']),
                "macd": float(last_row['macd']),
                "dist_from_sma50": f"{float(last_row['dist_sma50'])*100:.2f}%",
                "relative_strength_20d": float(last_row['rel_str_20'])
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Signal analysis failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "ticker": ticker
        }