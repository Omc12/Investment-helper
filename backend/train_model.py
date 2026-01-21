#!/usr/bin/env python3
"""
Model Training Module - Separate from Prediction System
This handles ONLY the training of the model, not prediction
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from datetime import datetime
import joblib
import os
from pathlib import Path

# Import data services
from services.trading_signals import SignalDataService, FeatureEngine

# Model storage configuration
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODEL_FILE = os.path.join(MODELS_DIR, 'pretrained_trading_model.pkl')
Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)

class ModelTrainer:
    """
    Dedicated class for training the trading model
    This should be run ONCE to create the persistent model
    """
    
    def __init__(self):
        self.model = HistGradientBoostingClassifier(
            learning_rate=0.05, 
            max_iter=300, 
            max_depth=5, 
            random_state=42
        )
        self.features = ['rsi', 'macd', 'macd_hist', 'dist_sma50', 
                         'rel_str_20', 'vix_level', 'atr']

    def create_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """Triple Barrier Labeling for training data"""
        # Trading parameters
        TP_PCT = 0.035  # 3.5% target profit
        SL_PCT = 0.015  # 1.5% stop loss
        HORIZON = 10    # 10-day horizon
        COST = 0.003    # 0.3% transaction cost
        
        df = df.copy()
        
        # Forward returns
        fwd_ret = df['Close'].pct_change(HORIZON).shift(-HORIZON)
        
        # Triple barrier conditions
        target_reached = (fwd_ret >= TP_PCT)
        stop_reached = (fwd_ret <= -SL_PCT)
        
        # Labels: 1 = BUY signal, 0 = WAIT
        df['target'] = np.where(target_reached, 1, 0)
        
        # Remove rows with NaN targets
        df = df.dropna(subset=['target'])
        
        print(f"[TRAINING] Label distribution: {dict(df['target'].value_counts().sort_index())}")
        
        return df

    def train_model(self, save_path: str = MODEL_FILE):
        """
        Train the comprehensive model on CSV data and save it
        """
        print("🚀 STARTING MODEL TRAINING 🚀")
        print("="*60)
        
        try:
            # Step 1: Load comprehensive training data
            print("[STEP 1] Loading CSV training data...")
            market_data = SignalDataService.load_from_csv()
            print(f"         Loaded {len(market_data)} rows of market data")
            
            # Step 2: Engineer features
            print("[STEP 2] Engineering features...")
            market_features = FeatureEngine.process(market_data)
            print(f"         Created features for {len(market_features)} samples")
            
            # Step 3: Create labels
            print("[STEP 3] Creating training labels...")
            market_labeled = self.create_labels(market_features)
            print(f"         Generated {len(market_labeled)} labeled samples")
            
            if len(market_labeled) < 1000:
                raise ValueError(f"Insufficient training data: {len(market_labeled)} samples")
            
            # Step 4: Prepare features and labels
            print("[STEP 4] Preparing training data...")
            X_market = market_labeled[self.features].fillna(0)
            y_market = market_labeled['target']
            
            print(f"         Features: {', '.join(self.features)}")
            print(f"         Training samples: {len(X_market)}")
            print(f"         Feature ranges:")
            for feature in self.features:
                values = X_market[feature]
                print(f"           {feature}: [{values.min():.3f}, {values.max():.3f}]")
            
            # Step 5: Train the model
            print("[STEP 5] Training the model...")
            self.model.fit(X_market, y_market)
            print("         ✅ Model training completed")
            
            # Step 6: Calculate training metrics
            print("[STEP 6] Calculating training metrics...")
            y_pred_proba = self.model.predict_proba(X_market)[:, 1]
            training_auc = roc_auc_score(y_market, y_pred_proba) if len(y_market.unique()) >= 2 else 0.5
            print(f"         Training AUC: {training_auc:.4f}")
            
            # Step 7: Save the model
            print("[STEP 7] Saving trained model...")
            model_data = {
                'model': self.model,
                'features': self.features,
                'metadata': {
                    'training_date': datetime.now().isoformat(),
                    'training_samples': len(X_market),
                    'training_auc': training_auc,
                    'feature_columns': self.features,
                    'data_source': 'CSV_comprehensive',
                    'data_range': f'{market_data.index[0].date()} to {market_data.index[-1].date()}',
                    'model_version': '2.0',
                    'algorithm': 'HistGradientBoostingClassifier'
                }
            }
            
            # Save to disk
            joblib.dump(model_data, save_path)
            file_size_kb = os.path.getsize(save_path) / 1024
            
            print(f"         ✅ Model saved to: {save_path}")
            print(f"         📁 File size: {file_size_kb:.1f} KB")
            
            # Summary
            print("\n🎉 TRAINING COMPLETED SUCCESSFULLY! 🎉")
            print("="*60)
            print(f"📊 Training Samples: {len(X_market):,}")
            print(f"🎯 Training AUC: {training_auc:.4f}")
            print(f"📅 Data Range: {market_data.index[0].date()} to {market_data.index[-1].date()}")
            print(f"💾 Model Size: {file_size_kb:.1f} KB")
            print("🚀 Ready for instant predictions!")
            
            return True
            
        except Exception as e:
            print(f"❌ TRAINING FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main training function"""
    trainer = ModelTrainer()
    success = trainer.train_model()
    
    if success:
        print("\n✅ Training script completed successfully!")
        print("🎯 The model is now ready for production use!")
    else:
        print("\n❌ Training failed. Please check the errors above.")

if __name__ == "__main__":
    main()