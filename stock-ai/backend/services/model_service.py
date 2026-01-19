"""
Machine learning model service with walk-forward validation.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from typing import Dict, Tuple
from services.yahoo_service import YahooFinanceService
from services.features import engineer_features, get_feature_columns
from core.cache import model_cache, cached
from core.config import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM


class ModelService:
    """Service for training and making predictions with ML models."""
    
    @staticmethod
    def get_confidence_label(probability: float) -> str:
        """Get confidence label based on probability."""
        if probability >= CONFIDENCE_HIGH or probability <= (1 - CONFIDENCE_HIGH):
            return "HIGH"
        elif probability >= CONFIDENCE_MEDIUM and probability <= (1 - CONFIDENCE_MEDIUM):
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def walk_forward_validation(X: np.ndarray, y: np.ndarray) -> Tuple[float, int]:
        """
        Perform walk-forward validation with 3 splits.
        
        Returns:
            (average_accuracy, total_samples_tested)
        """
        n_samples = len(X)
        accuracies = []
        total_test_samples = 0
        
        # 3 validation splits
        splits = [
            (0.6, 0.8),  # Train on 60%, test on next 20%
            (0.7, 0.9),  # Train on 70%, test on next 20%
            (0.8, 1.0),  # Train on 80%, test on remaining 20%
        ]
        
        for train_end_pct, test_end_pct in splits:
            train_end_idx = int(n_samples * train_end_pct)
            test_end_idx = int(n_samples * test_end_pct)
            
            if test_end_idx - train_end_idx < 10:  # Need at least 10 test samples
                continue
            
            X_train = X[:train_end_idx]
            y_train = y[:train_end_idx]
            X_test = X[train_end_idx:test_end_idx]
            y_test = y[train_end_idx:test_end_idx]
            
            # Train model
            model = HistGradientBoostingClassifier(
                max_iter=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            model.fit(X_train, y_train)
            
            # Evaluate
            accuracy = model.score(X_test, y_test)
            accuracies.append(accuracy)
            total_test_samples += len(y_test)
        
        if not accuracies:
            return 0.5, 0
        
        return np.mean(accuracies), total_test_samples
    
    @staticmethod
    @cached(model_cache, key_func=lambda ticker: f"model_{ticker}")
    def train_and_predict(ticker: str) -> Dict:
        """
        Train model and make prediction for a ticker.
        Uses caching to avoid retraining frequently.
        
        Returns:
            Dict with prediction results
        """
        # Fetch historical data
        df = YahooFinanceService.get_historical_data(ticker, period="2y", interval="1d")
        
        if df is None or len(df) < 200:
            raise ValueError(f"Insufficient data for {ticker}")
        
        # Engineer features
        data = engineer_features(df)
        
        # Get feature columns
        features = get_feature_columns()
        
        # Drop NaN rows
        model_data = data.dropna(subset=features + ['Target']).copy()
        
        if len(model_data) < 100:
            raise ValueError(f"Not enough valid data after feature engineering for {ticker}")
        
        X = model_data[features].values
        y = model_data['Target'].values
        
        # Walk-forward validation
        avg_accuracy, samples_used = ModelService.walk_forward_validation(X, y)
        
        # Calculate baseline (percentage of UP days in full dataset)
        baseline_accuracy = float(np.mean(y))
        
        # Train final model on 90% of data
        split_idx = int(len(X) * 0.9)
        X_train = X[:split_idx]
        y_train = y[:split_idx]
        
        final_model = HistGradientBoostingClassifier(
            max_iter=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        final_model.fit(X_train, y_train)
        
        # Predict next day using last row
        last_X = X[-1:, :]
        probability_up = float(final_model.predict_proba(last_X)[0][1])
        predicted_direction = "UP" if probability_up >= 0.5 else "DOWN"
        confidence = ModelService.get_confidence_label(probability_up)
        
        # Get latest data info
        latest_close = float(model_data['Close'].iloc[-1])
        last_date = str(model_data.index[-1].date())
        
        # Get last 100 candles for chart
        candles = YahooFinanceService.get_candles(ticker, period="6mo", interval="1d")
        
        return {
            "ticker": ticker,
            "last_date": last_date,
            "latest_close": round(latest_close, 2),
            "predicted_direction": predicted_direction,
            "probability_up": round(probability_up, 4),
            "confidence": confidence,
            "test_accuracy_avg": round(avg_accuracy, 4),
            "baseline_accuracy": round(baseline_accuracy, 4),
            "samples_used": samples_used,
            "candles": candles[-100:] if len(candles) > 100 else candles
        }
