"""
ML Pipeline Module

Complete machine learning pipeline from data loading to prediction.
Handles target creation, train-test split, model training, and evaluation.

Author: Trading System ML Team
Created: 2026-01-07
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import joblib
from typing import Dict, Tuple, Optional, List
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLPipeline:
    """
    Complete ML pipeline for stock prediction.
    
    Features:
    - Target variable creation (2-class, 3-class, 5-class)
    - Time-series aware train-test split
    - Feature scaling
    - Model training (XGBoost, Random Forest)
    - Model persistence
    - Prediction with confidence scores
    
    Example:
        >>> pipeline = MLPipeline('TCS', '1d')
        >>> target = pipeline.create_target(df, classification='3class')
        >>> X_train, X_test, y_train, y_test = pipeline.prepare_data(features, target)
        >>> pipeline.train_model(X_train, y_train, model_type='xgboost')
        >>> metrics = pipeline.evaluate(X_test, y_test)
    """
    
    def __init__(self, symbol: str, timeframe: str = '1d', model_dir: str = 'models'):
        """
        Initialize ML pipeline.
        
        Args:
            symbol: Stock symbol (e.g., 'TCS')
            timeframe: Data timeframe (e.g., '1d')
            model_dir: Directory to save models
        """
        self.symbol = symbol.upper()
        self.timeframe = timeframe
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = None
        self.target_name = None
        self.classification_type = None
        
        logger.info(f"Initialized MLPipeline for {self.symbol} {self.timeframe}")
    
    def create_target(self, df: pd.DataFrame, horizon: int = 1, 
                     classification: str = '3class') -> pd.Series:
        """
        Create target variable for prediction.
        
        Args:
            df: DataFrame with Close prices
            horizon: Days ahead to predict (default: 1 = next day)
            classification: '2class', '3class', or '5class'
        
        Returns:
            Target series with labels
            
        Classification schemes:
        - 2class: Up (1) or Down (0)
        - 3class: Up (2), Neutral (1), Down (0)
        - 5class: Strong Up (4), Up (3), Neutral (2), Down (1), Strong Down (0)
        """
        logger.info(f"Creating {classification} target with horizon={horizon}")
        
        # Calculate future returns
        future_return = df['Close'].pct_change(horizon).shift(-horizon)
        
        if classification == '2class':
            # Binary: Up (1) or Down (0)
            target = (future_return > 0).astype(int)
            self.target_name = 'direction_2class'
            
        elif classification == '3class':
            # 3-class: Up (2), Neutral (1), Down (0)
            # Neutral: -1% to +1%
            target = pd.cut(
                future_return,
                bins=[-np.inf, -0.01, 0.01, np.inf],
                labels=[0, 1, 2]
            )
            # Convert to int, handling NaN by filling with neutral class (1)
            target = pd.to_numeric(target, errors='coerce').fillna(1).astype(int)
            self.target_name = 'direction_3class'
            
        elif classification == '5class':
            # 5-class: Strong Down (0), Down (1), Neutral (2), Up (3), Strong Up (4)
            # Strong: >2%, Normal: 0.5-2%, Neutral: -0.5% to 0.5%
            target = pd.cut(
                future_return,
                bins=[-np.inf, -0.02, -0.005, 0.005, 0.02, np.inf],
                labels=[0, 1, 2, 3, 4]
            )
            # Convert to int, handling NaN by filling with neutral class (2)
            target = pd.to_numeric(target, errors='coerce').fillna(2).astype(int)
            self.target_name = 'direction_5class'
        
        else:
            raise ValueError(f"Unknown classification type: {classification}")
        
        self.classification_type = classification
        
        # Log class distribution
        class_counts = target.value_counts().sort_index()
        logger.info(f"Target distribution:\n{class_counts}")
        
        return target
    
    def prepare_data(self, features: pd.DataFrame, target: pd.Series,
                    test_size: float = 0.2, validation_size: float = 0.1) -> Tuple:
        """
        Split data into train/validation/test sets (time-series aware).
        
        IMPORTANT: No random shuffle! Time-series data must maintain temporal order.
        
        Args:
            features: Feature DataFrame
            target: Target series
            test_size: Proportion for test set (default: 0.2 = 20%)
            validation_size: Proportion for validation set (default: 0.1 = 10%)
        
        Returns:
            Tuple of (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        logger.info(f"Preparing data with test_size={test_size}, validation_size={validation_size}")
        
        # Remove NaN values
        valid_idx = ~(features.isnull().any(axis=1) | target.isnull())
        features_clean = features[valid_idx]
        target_clean = target[valid_idx]
        
        logger.info(f"After removing NaN: {len(features_clean)} samples")
        
        # Time-series split (no shuffle!)
        total_size = len(features_clean)
        test_idx = int(total_size * (1 - test_size))
        val_idx = int(test_idx * (1 - validation_size))
        
        # Split indices
        train_end = val_idx
        val_end = test_idx
        
        X_train = features_clean.iloc[:train_end]
        X_val = features_clean.iloc[train_end:val_end]
        X_test = features_clean.iloc[val_end:]
        
        y_train = target_clean.iloc[:train_end]
        y_val = target_clean.iloc[train_end:val_end]
        y_test = target_clean.iloc[val_end:]
        
        logger.info(f"Split sizes - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        # Scale features
        logger.info("Scaling features with StandardScaler...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to DataFrame for feature names
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
        X_val_scaled = pd.DataFrame(X_val_scaled, columns=X_val.columns, index=X_val.index)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
        
        self.feature_names = list(features_clean.columns)
        
        return X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test
    
    
    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series,
                   X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None,
                   model_type: str = 'xgboost', use_mlflow: bool = True, **kwargs) -> None:
        """
        Train ML model.
        
        Args:
            X_train: Training features
            y_train: Training target
            X_val: Validation features (optional, for early stopping)
            y_val: Validation target (optional, for early stopping)
            model_type: 'xgboost' or 'random_forest'
            use_mlflow: Whether to log run to MLflow
            **kwargs: Additional model parameters
        """
        logger.info(f"Training {model_type} model...")
        
        # Initialize MLflow if requested
        mlflow_manager = None
        if use_mlflow:
            try:
                from libs.mlflow_utils import MLflowManager
                mlflow_manager = MLflowManager()
                run_name = f"{self.symbol}_{self.timeframe}_{model_type}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}"
                mlflow_manager.start_run(run_name=run_name)
                mlflow_manager.log_params({"symbol": self.symbol, "timeframe": self.timeframe, "model_type": model_type})
                mlflow_manager.log_params(kwargs)
            except Exception as e:
                logger.warning(f"Failed to specific MLflow run: {e}")
                mlflow_manager = None
        
        if model_type == 'xgboost':
            # XGBoost with sensible defaults
            default_params = {
                'n_estimators': 200,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'eval_metric': 'mlogloss',
                'early_stopping_rounds': 20,
                'verbosity': 0
            }
            default_params.update(kwargs)
            
            if mlflow_manager:
                mlflow_manager.log_params(default_params)
            
            self.model = XGBClassifier(**default_params)
            
            # Train with validation set if provided
            if X_val is not None and y_val is not None:
                self.model.fit(
                    X_train, y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:
                self.model.fit(X_train, y_train)
                
        elif model_type == 'random_forest':
            # Random Forest with sensible defaults
            default_params = {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 20,
                'min_samples_leaf': 10,
                'random_state': 42,
                'n_jobs': -1
            }
            default_params.update(kwargs)
            
            if mlflow_manager:
                mlflow_manager.log_params(default_params)
            
            self.model = RandomForestClassifier(**default_params)
            self.model.fit(X_train, y_train)
        
        else:
            if mlflow_manager:
                mlflow_manager.end_run()
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Log model to MLflow
        if mlflow_manager:
            try:
                mlflow_manager.log_model(self.model, "model", model_type=model_type)
            except Exception as e:
                logger.warning(f"Failed to log model to MLflow: {e}")
                
        logger.info(f"✅ {model_type} training complete")
        
        # We keep the MLflow run open to log evaluation metrics later in evaluate()
        # But since evaluate() is a separate method, we need to handle state.
        # For simplicity, we'll end the run here and evaluate() can start a nested run or we pass the manager?
        # Better design: Pass metrics back here or evaluate immediately.
        # Given the existing pipeline structure, we'll store the manager in self for evaluate() to use.
        self._mlflow_manager = mlflow_manager
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Evaluate model performance.
        
        Args:
            X_test: Test features
            y_test: Test target
        
        Returns:
            Dictionary with metrics
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score, 
            classification_report, confusion_matrix, roc_auc_score
        )
        
        logger.info("Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'classification_report': classification_report(y_test, y_pred, zero_division=0)
        }
        
        # ROC-AUC for multi-class (one-vs-rest)
        try:
            if len(np.unique(y_test)) > 2:
                metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
            else:
                metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba[:, 1])
        except Exception as e:
            logger.warning(f"Could not calculate ROC-AUC: {e}")
            metrics['roc_auc'] = None
        
        
        # Feature importance (if available)
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            metrics['feature_importance'] = feature_importance
        
        logger.info(f"✅ Evaluation complete - Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_score']:.4f}")
        
        # Log metrics to MLflow if manager exists
        if hasattr(self, '_mlflow_manager') and self._mlflow_manager:
            try:
                # Filter out non-scalar metrics (like confusion matrix)
                loggable_metrics = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
                self._mlflow_manager.log_metrics(loggable_metrics)
                self._mlflow_manager.end_run()
                self._mlflow_manager = None # Clear it
            except Exception as e:
                logger.warning(f"Failed to log metrics to MLflow: {e}")
        
        return metrics
    
    def predict(self, features: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions with confidence scores.
        
        Args:
            features: Feature DataFrame
        
        Returns:
            Tuple of (predictions, probabilities)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        predictions = self.model.predict(features_scaled)
        probabilities = self.model.predict_proba(features_scaled)
        
        return predictions, probabilities
    
    def save_model(self, version: str = 'v1') -> None:
        """
        Save trained model and scaler.
        
        Args:
            version: Model version string
        """
        model_path = self.model_dir / f"{self.symbol}_{self.timeframe}_{version}.joblib"
        scaler_path = self.model_dir / f"{self.symbol}_{self.timeframe}_{version}_scaler.joblib"
        metadata_path = self.model_dir / f"{self.symbol}_{self.timeframe}_{version}_metadata.joblib"
        
        # Save model and scaler
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        # Save metadata
        metadata = {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'feature_names': self.feature_names,
            'target_name': self.target_name,
            'classification_type': self.classification_type,
            'model_type': type(self.model).__name__
        }
        joblib.dump(metadata, metadata_path)
        
        logger.info(f"✅ Model saved to {model_path}")
    
    def load_model(self, version: str = 'v1') -> None:
        """
        Load trained model and scaler.
        
        Args:
            version: Model version string
        """
        model_path = self.model_dir / f"{self.symbol}_{self.timeframe}_{version}.joblib"
        scaler_path = self.model_dir / f"{self.symbol}_{self.timeframe}_{version}_scaler.joblib"
        metadata_path = self.model_dir / f"{self.symbol}_{self.timeframe}_{version}_metadata.joblib"
        
        # Load model and scaler
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        # Load metadata
        metadata = joblib.load(metadata_path)
        self.feature_names = metadata['feature_names']
        self.target_name = metadata['target_name']
        self.classification_type = metadata['classification_type']
        
        logger.info(f"✅ Model loaded from {model_path}")
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get top N most important features.
        
        Args:
            top_n: Number of top features to return
        
        Returns:
            DataFrame with feature importance
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("Model does not support feature importance")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False).head(top_n)
        
        return importance_df


def train_model_for_symbol(symbol: str, timeframe: str = '1d', 
                          classification: str = '3class',
                          model_type: str = 'xgboost') -> Tuple[MLPipeline, Dict]:
    """
    Convenience function to train a model for a symbol.
    
    Args:
        symbol: Stock symbol
        timeframe: Data timeframe
        classification: Classification type ('2class', '3class', '5class')
        model_type: Model type ('xgboost', 'random_forest')
    
    Returns:
        Tuple of (trained pipeline, evaluation metrics)
    
    Example:
        >>> pipeline, metrics = train_model_for_symbol('TCS', '1d', '3class', 'xgboost')
        >>> print(f"Accuracy: {metrics['accuracy']:.2%}")
    """
    from libs.historical_data_manager import HistoricalDataManager
    from libs.feature_engineering import FeatureEngineer
    
    logger.info(f"Training {model_type} for {symbol} {timeframe} ({classification})")
    
    # Load data
    manager = HistoricalDataManager()
    df = manager.get_symbol_data(symbol, timeframe)
    
    if df.empty:
        raise ValueError(f"No data found for {symbol} {timeframe}")
    
    # Engineer features
    engineer = FeatureEngineer(df)
    features = engineer.build_all()
    
    # Create pipeline
    pipeline = MLPipeline(symbol, timeframe)
    
    # Create target
    target = pipeline.create_target(df, horizon=1, classification=classification)
    
    # Prepare data
    X_train, X_val, X_test, y_train, y_val, y_test = pipeline.prepare_data(features, target)
    
    # Train model
    pipeline.train_model(X_train, y_train, X_val, y_val, model_type=model_type)
    
    # Evaluate
    metrics = pipeline.evaluate(X_test, y_test)
    
    # Save model
    pipeline.save_model(version='v1')
    
    logger.info(f"✅ Training complete for {symbol}")
    
    return pipeline, metrics
