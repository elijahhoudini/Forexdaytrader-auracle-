"""
ML-based Signal Optimization
============================

Machine learning framework for dynamic signal tuning and optimization.
Uses scikit-learn to learn optimal thresholds based on recent trade outcomes.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from typing import Dict, List, Tuple, Optional
import joblib
import os
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class MLSignalOptimizer:
    """
    Machine learning-based signal optimization system.
    
    Features:
    - Learns optimal signal thresholds from historical performance
    - Dynamic parameter adjustment based on market conditions
    - Multiple ML models for signal classification
    - Feature engineering for technical indicators
    - Model persistence and versioning
    """
    
    def __init__(self, config: Dict):
        """
        Initialize ML signal optimizer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.model_dir = config.get('model_dir', 'data/models')
        self.min_samples = config.get('min_samples', 50)
        self.retrain_frequency = config.get('retrain_frequency', 24)  # hours
        
        # Model configuration
        self.models_config = {
            'random_forest': {
                'class': RandomForestClassifier,
                'params': {
                    'n_estimators': 100,
                    'max_depth': 10,
                    'min_samples_split': 5,
                    'random_state': 42
                }
            },
            'logistic_regression': {
                'class': LogisticRegression,
                'params': {
                    'C': 1.0,
                    'max_iter': 1000,
                    'random_state': 42
                }
            }
        }
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load existing models
        self._load_models()
    
    def prepare_features(self, trade_data: List[Dict], market_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML training.
        
        Args:
            trade_data: Historical trade data
            market_data: Market price data with technical indicators
            
        Returns:
            DataFrame with features and target
        """
        features = []
        
        for trade in trade_data:
            # Get market data at trade entry time
            entry_time = pd.to_datetime(trade['entry_time'])
            
            # Find closest market data point
            market_idx = market_data.index[market_data.index <= entry_time]
            if len(market_idx) == 0:
                continue
            
            market_row = market_data.loc[market_idx[-1]]
            
            # Extract features
            feature_dict = {
                # Signal characteristics
                'signal_confidence': trade.get('confidence', 0.5),
                'signal_type': 1 if trade['direction'] == 'BUY' else 0,
                
                # Technical indicators
                'rsi': market_row.get('rsi', 50),
                'macd': market_row.get('macd', 0),
                'macd_signal': market_row.get('macd_signal', 0),
                'bb_position': market_row.get('bb_position', 0.5),  # Position within Bollinger Bands
                'atr': market_row.get('atr', 0),
                
                # Price action
                'price_change_1h': market_row.get('price_change_1h', 0),
                'price_change_4h': market_row.get('price_change_4h', 0),
                'volatility': market_row.get('volatility', 0),
                
                # Market conditions
                'volume': market_row.get('volume', 0),
                'spread': trade.get('spread', 0.0001),
                'time_of_day': entry_time.hour,
                'day_of_week': entry_time.weekday(),
                
                # Risk metrics
                'position_size': trade.get('size', 0.1),
                'stop_loss_distance': abs(trade.get('entry_price', 0) - trade.get('stop_loss', 0)),
                'risk_reward_ratio': trade.get('risk_reward_ratio', 2.0),
                
                # Target variable (1 for profitable trade, 0 for loss)
                'target': 1 if trade.get('pnl', 0) > 0 else 0
            }
            
            features.append(feature_dict)
        
        if not features:
            return pd.DataFrame()
        
        df = pd.DataFrame(features)
        
        # Store feature names
        self.feature_names = [col for col in df.columns if col != 'target']
        
        return df
    
    def train_models(self, features_df: pd.DataFrame) -> Dict[str, float]:
        """
        Train ML models on prepared features.
        
        Args:
            features_df: Features DataFrame with target column
            
        Returns:
            Dictionary of model scores
        """
        if len(features_df) < self.min_samples:
            print(f"Insufficient data for training. Need {self.min_samples}, have {len(features_df)}")
            return {}
        
        print(f"Training ML models on {len(features_df)} samples...")
        
        # Prepare data
        X = features_df[self.feature_names]
        y = features_df['target']
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        model_scores = {}
        
        for model_name, model_config in self.models_config.items():
            try:
                print(f"Training {model_name}...")
                
                # Initialize model
                model = model_config['class'](**model_config['params'])
                
                # Scale features for models that need it
                if model_name == 'logistic_regression':
                    scaler = StandardScaler()
                    X_scaled = scaler.fit_transform(X)
                    self.scalers[model_name] = scaler
                else:
                    X_scaled = X
                
                # Train model
                model.fit(X_scaled, y)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='accuracy')
                mean_score = cv_scores.mean()
                
                # Store model
                self.models[model_name] = model
                model_scores[model_name] = mean_score
                
                print(f"{model_name} trained - CV Accuracy: {mean_score:.3f} (+/- {cv_scores.std() * 2:.3f})")
                
                # Feature importance (for tree-based models)
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    feature_importance = list(zip(self.feature_names, importances))
                    feature_importance.sort(key=lambda x: x[1], reverse=True)
                    
                    print(f"Top 5 features for {model_name}:")
                    for feature, importance in feature_importance[:5]:
                        print(f"  {feature}: {importance:.3f}")
                
            except Exception as e:
                print(f"Error training {model_name}: {e}")
                continue
        
        # Save models
        self._save_models()
        
        return model_scores
    
    def optimize_signal(self, signal: Dict, market_data: pd.DataFrame) -> Dict:
        """
        Optimize a trading signal using ML models.
        
        Args:
            signal: Original trading signal
            market_data: Current market data with indicators
            
        Returns:
            Optimized signal with adjusted parameters
        """
        if not self.models:
            return signal
        
        try:
            # Prepare features for current signal
            current_time = pd.to_datetime(signal['timestamp'])
            market_row = market_data.iloc[-1]  # Latest market data
            
            features = {
                'signal_confidence': signal.get('confidence', 0.5),
                'signal_type': 1 if signal['signal'] == 'BUY' else 0,
                'rsi': market_row.get('rsi', 50),
                'macd': market_row.get('macd', 0),
                'macd_signal': market_row.get('macd_signal', 0),
                'bb_position': market_row.get('bb_position', 0.5),
                'atr': market_row.get('atr', 0),
                'price_change_1h': market_row.get('price_change_1h', 0),
                'price_change_4h': market_row.get('price_change_4h', 0),
                'volatility': market_row.get('volatility', 0),
                'volume': market_row.get('volume', 0),
                'spread': 0.0001,  # Default spread
                'time_of_day': current_time.hour,
                'day_of_week': current_time.weekday(),
                'position_size': 0.1,  # Default position size
                'stop_loss_distance': abs(signal.get('entry_price', 0) - signal.get('stop_loss', 0)),
                'risk_reward_ratio': signal.get('risk_reward_ratio', 2.0)
            }
            
            # Create DataFrame
            X = pd.DataFrame([features])[self.feature_names]
            X = X.fillna(X.mean())
            
            # Get predictions from all models
            predictions = {}
            probabilities = {}
            
            for model_name, model in self.models.items():
                try:
                    # Scale features if needed
                    if model_name in self.scalers:
                        X_scaled = self.scalers[model_name].transform(X)
                    else:
                        X_scaled = X
                    
                    # Get prediction
                    pred = model.predict(X_scaled)[0]
                    predictions[model_name] = pred
                    
                    # Get probability if available
                    if hasattr(model, 'predict_proba'):
                        prob = model.predict_proba(X_scaled)[0]
                        probabilities[model_name] = prob[1]  # Probability of positive class
                
                except Exception as e:
                    print(f"Error getting prediction from {model_name}: {e}")
                    continue
            
            if not predictions:
                return signal
            
            # Ensemble prediction (majority vote)
            positive_votes = sum(predictions.values())
            total_votes = len(predictions)
            ensemble_confidence = positive_votes / total_votes
            
            # Average probability
            if probabilities:
                avg_probability = sum(probabilities.values()) / len(probabilities)
            else:
                avg_probability = ensemble_confidence
            
            # Optimize signal based on ML predictions
            optimized_signal = signal.copy()
            
            # Adjust confidence based on ML prediction
            ml_confidence_boost = avg_probability - 0.5  # Boost if > 0.5, reduce if < 0.5
            original_confidence = signal.get('confidence', 0.5)
            new_confidence = max(0.1, min(1.0, original_confidence + ml_confidence_boost * 0.3))
            optimized_signal['confidence'] = new_confidence
            
            # Adjust stop loss and take profit based on volatility and prediction confidence
            if avg_probability > 0.7:  # High confidence prediction
                # Widen take profit for high confidence signals
                current_tp = signal.get('take_profit', 0)
                if current_tp > 0:
                    tp_adjustment = 1.2  # 20% wider
                    optimized_signal['take_profit'] = current_tp * tp_adjustment
            
            elif avg_probability < 0.3:  # Low confidence prediction
                # Tighten stop loss for low confidence signals
                current_sl = signal.get('stop_loss', 0)
                if current_sl > 0:
                    sl_adjustment = 0.8  # 20% tighter
                    entry_price = signal['entry_price']
                    
                    if signal['signal'] == 'BUY':
                        optimized_signal['stop_loss'] = entry_price - (entry_price - current_sl) * sl_adjustment
                    else:
                        optimized_signal['stop_loss'] = entry_price + (current_sl - entry_price) * sl_adjustment
            
            # Add ML metadata
            optimized_signal['ml_optimization'] = {
                'ensemble_confidence': ensemble_confidence,
                'avg_probability': avg_probability,
                'predictions': predictions,
                'probabilities': probabilities,
                'optimization_applied': True
            }
            
            return optimized_signal
            
        except Exception as e:
            print(f"Error optimizing signal: {e}")
            return signal
    
    def should_retrain(self) -> bool:
        """Check if models should be retrained."""
        last_training_file = os.path.join(self.model_dir, 'last_training.json')
        
        if not os.path.exists(last_training_file):
            return True
        
        try:
            with open(last_training_file, 'r') as f:
                last_training = json.load(f)
            
            last_time = datetime.fromisoformat(last_training['timestamp'])
            hours_since = (datetime.now() - last_time).total_seconds() / 3600
            
            return hours_since >= self.retrain_frequency
        except:
            return True
    
    def evaluate_models(self, test_data: pd.DataFrame) -> Dict:
        """
        Evaluate trained models on test data.
        
        Args:
            test_data: Test dataset with features and targets
            
        Returns:
            Evaluation results
        """
        if not self.models or test_data.empty:
            return {}
        
        X_test = test_data[self.feature_names]
        y_test = test_data['target']
        X_test = X_test.fillna(X_test.mean())
        
        evaluation_results = {}
        
        for model_name, model in self.models.items():
            try:
                # Scale features if needed
                if model_name in self.scalers:
                    X_test_scaled = self.scalers[model_name].transform(X_test)
                else:
                    X_test_scaled = X_test
                
                # Predictions
                predictions = model.predict(X_test_scaled)
                
                # Accuracy
                accuracy = (predictions == y_test).mean()
                
                # Classification report
                report = classification_report(y_test, predictions, output_dict=True)
                
                evaluation_results[model_name] = {
                    'accuracy': accuracy,
                    'precision': report['weighted avg']['precision'],
                    'recall': report['weighted avg']['recall'],
                    'f1_score': report['weighted avg']['f1-score']
                }
                
                print(f"{model_name} - Test Accuracy: {accuracy:.3f}")
                
            except Exception as e:
                print(f"Error evaluating {model_name}: {e}")
                continue
        
        return evaluation_results
    
    def _save_models(self):
        """Save trained models to disk."""
        try:
            for model_name, model in self.models.items():
                model_path = os.path.join(self.model_dir, f'{model_name}.joblib')
                joblib.dump(model, model_path)
            
            # Save scalers
            for scaler_name, scaler in self.scalers.items():
                scaler_path = os.path.join(self.model_dir, f'{scaler_name}_scaler.joblib')
                joblib.dump(scaler, scaler_path)
            
            # Save feature names
            features_path = os.path.join(self.model_dir, 'feature_names.json')
            with open(features_path, 'w') as f:
                json.dump(self.feature_names, f)
            
            # Save training timestamp
            timestamp_path = os.path.join(self.model_dir, 'last_training.json')
            with open(timestamp_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'num_models': len(self.models)
                }, f)
            
            print(f"Models saved to {self.model_dir}")
            
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def _load_models(self):
        """Load trained models from disk."""
        try:
            # Load feature names
            features_path = os.path.join(self.model_dir, 'feature_names.json')
            if os.path.exists(features_path):
                with open(features_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            # Load models
            for model_name in self.models_config.keys():
                model_path = os.path.join(self.model_dir, f'{model_name}.joblib')
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    print(f"Loaded {model_name} model")
                
                # Load scalers
                scaler_path = os.path.join(self.model_dir, f'{model_name}_scaler.joblib')
                if os.path.exists(scaler_path):
                    self.scalers[model_name] = joblib.load(scaler_path)
                    print(f"Loaded {model_name} scaler")
            
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models."""
        info = {
            'loaded_models': list(self.models.keys()),
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'model_directory': self.model_dir
        }
        
        # Add last training info
        timestamp_path = os.path.join(self.model_dir, 'last_training.json')
        if os.path.exists(timestamp_path):
            with open(timestamp_path, 'r') as f:
                last_training = json.load(f)
                info['last_training'] = last_training
        
        return info


def create_ml_optimizer(config: Dict = None) -> MLSignalOptimizer:
    """
    Create ML signal optimizer instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        MLSignalOptimizer instance
    """
    default_config = {
        'model_dir': 'data/models',
        'min_samples': 50,
        'retrain_frequency': 24  # hours
    }
    
    if config:
        default_config.update(config)
    
    return MLSignalOptimizer(default_config)