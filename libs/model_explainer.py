"""
Model Explainability with SHAP

Provides interpretable explanations for model predictions using SHAP values.
Supports XGBoost (TreeExplainer) and basic framework for deep learning models.

Author: Trading System ML Team
Created: 2026-01-07
"""

import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Dict, List, Tuple
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelExplainer:
    """
    SHAP-based model explainer for interpretable predictions.
    
    Supports:
    - TreeExplainer for XGBoost, Random Forest
    - Feature importance analysis
    - Individual prediction explanations
    - Global feature importance
    
    Example:
        >>> explainer = ModelExplainer(xgb_model, model_type='tree')
        >>> shap_values = explainer.explain_prediction(X_test)
        >>> explainer.plot_waterfall(X_test[0], feature_names)
    """
    
    def __init__(self, 
                 model: object,
                 model_type: str = 'tree',
                 background_data: Optional[np.ndarray] = None):
        """
        Initialize model explainer.
        
        Args:
            model: Trained model to explain
            model_type: Type of model ('tree' for XGBoost/RF, 'deep' for neural nets)
            background_data: Background dataset for DeepExplainer (optional)
        """
        self.model = model
        self.model_type = model_type
        
        # Create appropriate explainer
        if model_type == 'tree':
            self.explainer = shap.TreeExplainer(model)
            logger.info("Initialized TreeExplainer for tree-based model")
        elif model_type == 'deep':
            if background_data is None:
                raise ValueError("background_data required for DeepExplainer")
            self.explainer = shap.DeepExplainer(model, background_data)
            logger.info("Initialized DeepExplainer for deep learning model")
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")
    
    def explain_prediction(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate SHAP values for predictions.
        
        Args:
            X: Input features (n_samples, n_features)
        
        Returns:
            SHAP values array
            - For binary: (n_samples, n_features)
            - For multiclass: (n_classes, n_samples, n_features)
        """
        shap_values = self.explainer.shap_values(X)
        
        logger.info(f"Calculated SHAP values for {len(X)} samples")
        
        return shap_values
    
    def get_feature_importance(self, 
                               X: np.ndarray,
                               feature_names: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Get SHAP-based feature importance.
        
        Args:
            X: Input features
            feature_names: Names of features (optional)
        
        Returns:
            DataFrame with feature importance scores
        """
        shap_values = self.explain_prediction(X)
        
        # Handle different SHAP value formats
        if isinstance(shap_values, list):
            # Some models return list of arrays: [class0_shap, class1_shap, ...]
            # Each is shape (n_samples, n_features)
            importance = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
        elif shap_values.ndim == 3:
            # XGBoost multiclass returns (n_samples, n_features, n_classes)
            # Average across samples and classes
            importance = np.abs(shap_values).mean(axis=(0, 2))
        else:
            # Binary or regression: (n_samples, n_features)
            importance = np.abs(shap_values).mean(axis=0)
        
        # Ensure importance is 1D
        importance = np.asarray(importance).flatten()
        
        # Create DataFrame
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(importance))]
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def plot_waterfall(self,
                      X_sample: np.ndarray,
                      feature_names: Optional[List[str]] = None,
                      class_idx: int = 0,
                      max_display: int = 20,
                      save_path: Optional[str] = None) -> plt.Figure:
        """
        Create waterfall plot for a single prediction.
        
        Shows how each feature contributes to pushing the prediction
        from the base value to the final prediction.
        
        Args:
            X_sample: Single sample features (n_features,)
            feature_names: Names of features
            class_idx: Class index for multiclass (default: 0)
            max_display: Maximum features to display
            save_path: Path to save plot (optional)
        
        Returns:
            Matplotlib figure
        """
        # Ensure X_sample is 2D
        if X_sample.ndim == 1:
            X_sample = X_sample.reshape(1, -1)
        
        # Get SHAP values
        shap_values = self.explain_prediction(X_sample)
        
        # Handle multiclass
        if isinstance(shap_values, list):
            shap_vals = shap_values[class_idx][0]
        else:
            shap_vals = shap_values[0]
        
        # Create explanation object
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(shap_vals))]
        
        explanation = shap.Explanation(
            values=shap_vals,
            base_values=self.explainer.expected_value if not isinstance(self.explainer.expected_value, list) 
                        else self.explainer.expected_value[class_idx],
            data=X_sample[0],
            feature_names=feature_names
        )
        
        # Create plot
        fig = plt.figure(figsize=(10, 6))
        shap.waterfall_plot(explanation, max_display=max_display, show=False)
        plt.tight_layout()
        
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Saved waterfall plot to {save_path}")
        
        return fig
    
    def plot_summary(self,
                    X: np.ndarray,
                    feature_names: Optional[List[str]] = None,
                    max_display: int = 20,
                    save_path: Optional[str] = None) -> plt.Figure:
        """
        Create summary plot showing global feature importance.
        
        Args:
            X: Input features (n_samples, n_features)
            feature_names: Names of features
            max_display: Maximum features to display
            save_path: Path to save plot (optional)
        
        Returns:
            Matplotlib figure
        """
        shap_values = self.explain_prediction(X)
        
        # Create plot
        fig = plt.figure(figsize=(10, 8))
        
        # Handle multiclass
        if isinstance(shap_values, list):
            # For multiclass, show average across classes
            shap_values_avg = np.mean(np.abs(shap_values), axis=0)
            shap.summary_plot(
                shap_values_avg, 
                X, 
                feature_names=feature_names,
                max_display=max_display,
                show=False
            )
        else:
            shap.summary_plot(
                shap_values, 
                X, 
                feature_names=feature_names,
                max_display=max_display,
                show=False
            )
        
        plt.tight_layout()
        
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Saved summary plot to {save_path}")
        
        return fig
    
    def plot_force(self,
                  X_sample: np.ndarray,
                  feature_names: Optional[List[str]] = None,
                  class_idx: int = 0) -> shap.plots._force.AdditiveForceVisualizer:
        """
        Create force plot for a single prediction.
        
        Shows how features push the prediction higher or lower.
        
        Args:
            X_sample: Single sample features
            feature_names: Names of features
            class_idx: Class index for multiclass
        
        Returns:
            SHAP force plot visualizer
        """
        # Ensure X_sample is 2D
        if X_sample.ndim == 1:
            X_sample = X_sample.reshape(1, -1)
        
        # Get SHAP values
        shap_values = self.explain_prediction(X_sample)
        
        # Handle multiclass
        if isinstance(shap_values, list):
            shap_vals = shap_values[class_idx][0]
            base_value = self.explainer.expected_value[class_idx]
        else:
            shap_vals = shap_values[0]
            base_value = self.explainer.expected_value
        
        # Create force plot
        force_plot = shap.force_plot(
            base_value,
            shap_vals,
            X_sample[0],
            feature_names=feature_names
        )
        
        return force_plot
    
    def get_top_features(self,
                        X_sample: np.ndarray,
                        feature_names: Optional[List[str]] = None,
                        class_idx: int = 0,
                        top_n: int = 10) -> pd.DataFrame:
        """
        Get top N features contributing to a prediction.
        
        Args:
            X_sample: Single sample features
            feature_names: Names of features
            class_idx: Class index for multiclass
            top_n: Number of top features to return
        
        Returns:
            DataFrame with top features and their SHAP values
        """
        # Ensure X_sample is 2D
        if X_sample.ndim == 1:
            X_sample = X_sample.reshape(1, -1)
        
        # Get SHAP values
        shap_values = self.explain_prediction(X_sample)
        
        # Handle multiclass
        if isinstance(shap_values, list):
            shap_vals = shap_values[class_idx][0]
        else:
            shap_vals = shap_values[0]
        
        # Create feature names if not provided
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(shap_vals))]
        
        # Get top features by absolute SHAP value
        abs_shap = np.abs(shap_vals)
        top_indices = np.argsort(abs_shap)[-top_n:][::-1]
        
        top_features = pd.DataFrame({
            'feature': [feature_names[i] for i in top_indices],
            'shap_value': shap_vals[top_indices],
            'feature_value': X_sample[0, top_indices],
            'abs_shap_value': abs_shap[top_indices]
        })
        
        return top_features


def explain_xgboost_prediction(model: object,
                               X_sample: np.ndarray,
                               feature_names: List[str],
                               class_names: Optional[List[str]] = None) -> Dict:
    """
    Comprehensive explanation for a single XGBoost prediction.
    
    Args:
        model: Trained XGBoost model
        X_sample: Single sample to explain
        feature_names: Names of features
        class_names: Names of classes (optional)
    
    Returns:
        Dictionary with explanation details
    """
    explainer = ModelExplainer(model, model_type='tree')
    
    # Get prediction
    if hasattr(model, 'predict_proba'):
        prediction_proba = model.predict_proba(X_sample.reshape(1, -1))[0]
        prediction_class = np.argmax(prediction_proba)
    else:
        prediction_class = model.predict(X_sample.reshape(1, -1))[0]
        prediction_proba = None
    
    # Get SHAP values
    shap_values = explainer.explain_prediction(X_sample.reshape(1, -1))
    
    # Get top features
    top_features = explainer.get_top_features(
        X_sample, 
        feature_names, 
        class_idx=prediction_class if isinstance(shap_values, list) else 0,
        top_n=10
    )
    
    # Build explanation
    explanation = {
        'prediction_class': int(prediction_class),
        'prediction_proba': prediction_proba.tolist() if prediction_proba is not None else None,
        'class_name': class_names[prediction_class] if class_names else f'Class {prediction_class}',
        'top_features': top_features.to_dict('records'),
        'shap_values': shap_values
    }
    
    return explanation
