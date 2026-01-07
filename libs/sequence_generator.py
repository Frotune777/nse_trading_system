"""
Sequence Generator for Deep Learning Models

Prepares time-series sequences for LSTM, GRU, and other recurrent models.
Uses sliding window approach to create sequences from flat feature data.

Author: Trading System ML Team
Created: 2026-01-07
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SequenceGenerator:
    """
    Generate sequences for time-series deep learning models.
    
    Features:
    - Sliding window sequence creation
    - Preserves temporal order
    - Handles train/val/test splits
    - Configurable lookback period
    
    Example:
        >>> generator = SequenceGenerator(lookback=20)
        >>> X_seq, y_seq = generator.create_sequences(features, targets)
        >>> print(X_seq.shape)  # (samples, 20, 47)
    """
    
    def __init__(self, lookback: int = 20):
        """
        Initialize sequence generator.
        
        Args:
            lookback: Number of timesteps to look back (default: 20 days)
        """
        self.lookback = lookback
        logger.info(f"Initialized SequenceGenerator with lookback={lookback}")
    
    def create_sequences(self, features: pd.DataFrame, 
                        targets: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences from features and targets.
        
        Args:
            features: DataFrame with shape (n_samples, n_features)
            targets: Series with shape (n_samples,)
        
        Returns:
            X_seq: Array with shape (n_samples - lookback, lookback, n_features)
            y_seq: Array with shape (n_samples - lookback,)
        
        Example:
            If features has 1000 rows and lookback=20:
            - X_seq will have shape (980, 20, 47)
            - y_seq will have shape (980,)
        """
        # Validate inputs
        if len(features) != len(targets):
            raise ValueError(f"Features ({len(features)}) and targets ({len(targets)}) must have same length")
        
        if len(features) < self.lookback:
            raise ValueError(f"Not enough data: {len(features)} samples < lookback {self.lookback}")
        
        # Convert to numpy arrays
        X = features.values
        y = targets.values
        
        # Create sequences
        X_seq = []
        y_seq = []
        
        for i in range(self.lookback, len(X)):
            # Get sequence of past 'lookback' timesteps
            X_seq.append(X[i - self.lookback:i])
            # Get target for current timestep
            y_seq.append(y[i])
        
        X_seq = np.array(X_seq)
        y_seq = np.array(y_seq)
        
        logger.info(f"Created sequences: X_seq shape {X_seq.shape}, y_seq shape {y_seq.shape}")
        
        return X_seq, y_seq
    
    def create_train_test_sequences(self, 
                                   X_train: pd.DataFrame, 
                                   y_train: pd.Series,
                                   X_val: Optional[pd.DataFrame] = None,
                                   y_val: Optional[pd.Series] = None,
                                   X_test: Optional[pd.DataFrame] = None,
                                   y_test: Optional[pd.Series] = None) -> dict:
        """
        Create sequences while preserving train/val/test splits.
        
        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features (optional)
            y_val: Validation targets (optional)
            X_test: Test features (optional)
            y_test: Test targets (optional)
        
        Returns:
            Dictionary with keys:
                - 'X_train_seq', 'y_train_seq'
                - 'X_val_seq', 'y_val_seq' (if provided)
                - 'X_test_seq', 'y_test_seq' (if provided)
        """
        result = {}
        
        # Create training sequences
        X_train_seq, y_train_seq = self.create_sequences(X_train, y_train)
        result['X_train_seq'] = X_train_seq
        result['y_train_seq'] = y_train_seq
        
        logger.info(f"Training sequences: {X_train_seq.shape}")
        
        # Create validation sequences if provided
        if X_val is not None and y_val is not None:
            X_val_seq, y_val_seq = self.create_sequences(X_val, y_val)
            result['X_val_seq'] = X_val_seq
            result['y_val_seq'] = y_val_seq
            logger.info(f"Validation sequences: {X_val_seq.shape}")
        
        # Create test sequences if provided
        if X_test is not None and y_test is not None:
            X_test_seq, y_test_seq = self.create_sequences(X_test, y_test)
            result['X_test_seq'] = X_test_seq
            result['y_test_seq'] = y_test_seq
            logger.info(f"Test sequences: {X_test_seq.shape}")
        
        return result
    
    def create_single_sequence(self, features: pd.DataFrame) -> np.ndarray:
        """
        Create a single sequence for prediction (most recent data).
        
        Args:
            features: DataFrame with at least 'lookback' rows
        
        Returns:
            Sequence with shape (1, lookback, n_features)
        
        Example:
            >>> latest_seq = generator.create_single_sequence(recent_features)
            >>> prediction = model.predict(latest_seq)
        """
        if len(features) < self.lookback:
            raise ValueError(f"Need at least {self.lookback} rows, got {len(features)}")
        
        # Get last 'lookback' rows
        X = features.tail(self.lookback).values
        
        # Reshape to (1, lookback, n_features)
        X_seq = X.reshape(1, self.lookback, -1)
        
        return X_seq
    
    def get_sequence_info(self, original_length: int) -> dict:
        """
        Get information about sequences that would be created.
        
        Args:
            original_length: Length of original dataset
        
        Returns:
            Dictionary with sequence information
        """
        if original_length < self.lookback:
            return {
                'valid': False,
                'message': f'Not enough data: {original_length} < {self.lookback}',
                'n_sequences': 0,
                'lookback': self.lookback
            }
        
        n_sequences = original_length - self.lookback
        
        return {
            'valid': True,
            'message': 'Valid',
            'n_sequences': n_sequences,
            'lookback': self.lookback,
            'original_length': original_length,
            'data_loss': self.lookback,
            'data_loss_pct': (self.lookback / original_length) * 100
        }


class PyTorchSequenceDataset:
    """
    PyTorch Dataset wrapper for sequences.
    
    Enables batch processing and DataLoader integration.
    """
    
    def __init__(self, X_seq: np.ndarray, y_seq: np.ndarray):
        """
        Initialize dataset.
        
        Args:
            X_seq: Sequences with shape (n_samples, lookback, n_features)
            y_seq: Targets with shape (n_samples,)
        """
        import torch
        
        self.X = torch.FloatTensor(X_seq)
        self.y = torch.LongTensor(y_seq)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def create_dataloaders(X_train_seq: np.ndarray, 
                      y_train_seq: np.ndarray,
                      X_val_seq: Optional[np.ndarray] = None,
                      y_val_seq: Optional[np.ndarray] = None,
                      batch_size: int = 32,
                      shuffle: bool = True) -> dict:
    """
    Create PyTorch DataLoaders for training.
    
    Args:
        X_train_seq: Training sequences
        y_train_seq: Training targets
        X_val_seq: Validation sequences (optional)
        y_val_seq: Validation targets (optional)
        batch_size: Batch size for training
        shuffle: Whether to shuffle training data
    
    Returns:
        Dictionary with 'train_loader' and optionally 'val_loader'
    """
    from torch.utils.data import DataLoader
    
    # Create training dataset and loader
    train_dataset = PyTorchSequenceDataset(X_train_seq, y_train_seq)
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0  # Set to 0 to avoid multiprocessing issues
    )
    
    result = {'train_loader': train_loader}
    
    # Create validation loader if data provided
    if X_val_seq is not None and y_val_seq is not None:
        val_dataset = PyTorchSequenceDataset(X_val_seq, y_val_seq)
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )
        result['val_loader'] = val_loader
    
    logger.info(f"Created DataLoaders: batch_size={batch_size}, shuffle={shuffle}")
    
    return result


# Utility functions

def normalize_sequences(X_seq: np.ndarray, 
                       scaler=None,
                       fit: bool = True) -> Tuple[np.ndarray, object]:
    """
    Normalize sequences using StandardScaler.
    
    Args:
        X_seq: Sequences with shape (n_samples, lookback, n_features)
        scaler: Existing scaler (optional)
        fit: Whether to fit the scaler
    
    Returns:
        Normalized sequences and fitted scaler
    """
    from sklearn.preprocessing import StandardScaler
    
    # Reshape to 2D for scaling
    n_samples, lookback, n_features = X_seq.shape
    X_2d = X_seq.reshape(-1, n_features)
    
    # Fit or use existing scaler
    if scaler is None:
        scaler = StandardScaler()
    
    if fit:
        X_scaled = scaler.fit_transform(X_2d)
    else:
        X_scaled = scaler.transform(X_2d)
    
    # Reshape back to 3D
    X_seq_scaled = X_scaled.reshape(n_samples, lookback, n_features)
    
    return X_seq_scaled, scaler


def get_class_distribution(y_seq: np.ndarray) -> dict:
    """
    Get class distribution in sequences.
    
    Args:
        y_seq: Target array
    
    Returns:
        Dictionary with class counts and percentages
    """
    unique, counts = np.unique(y_seq, return_counts=True)
    total = len(y_seq)
    
    distribution = {}
    for class_id, count in zip(unique, counts):
        distribution[int(class_id)] = {
            'count': int(count),
            'percentage': (count / total) * 100
        }
    
    return distribution
