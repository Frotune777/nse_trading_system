"""
Prediction Tracker Module

Tracks ML predictions over time and compares with actual outcomes.
Enables accuracy tracking, performance analysis, and prediction history.

Author: Trading System ML Team
Created: 2026-01-07
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionTracker:
    """
    Track and analyze ML predictions over time.
    
    Features:
    - Save predictions to database
    - Compare predictions with actual outcomes
    - Calculate accuracy metrics
    - Generate performance reports
    - Track prediction confidence
    
    Example:
        >>> tracker = PredictionTracker()
        >>> tracker.save_prediction('TCS', '1d', 2, [0.1, 0.3, 0.6], '2026-01-07')
        >>> accuracy = tracker.calculate_accuracy('TCS', '1d', days=30)
    """
    
    def __init__(self, db_path: str = 'data/trading.db'):
        """
        Initialize prediction tracker.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._create_tables()
        logger.info(f"Initialized PredictionTracker with database: {db_path}")
    
    def _create_tables(self):
        """Create prediction tracking tables if they don't exist."""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Predictions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    prediction_date TEXT NOT NULL,
                    predicted_class INTEGER NOT NULL,
                    confidence_down REAL,
                    confidence_neutral REAL,
                    confidence_up REAL,
                    actual_class INTEGER,
                    actual_return REAL,
                    is_correct INTEGER,
                    model_version TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timeframe, prediction_date)
                )
            """)
            
            # Model performance table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ml_model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    accuracy REAL,
                    precision_down REAL,
                    precision_neutral REAL,
                    precision_up REAL,
                    total_predictions INTEGER,
                    correct_predictions INTEGER,
                    evaluation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timeframe, model_version, evaluation_date)
                )
            """)
            
            conn.commit()
            logger.info("Prediction tracking tables created/verified")
    
    def save_prediction(self, symbol: str, timeframe: str, 
                       predicted_class: int, probabilities: List[float],
                       prediction_date: str, model_version: str = 'v1') -> bool:
        """
        Save a prediction to the database.
        
        Args:
            symbol: Stock symbol
            timeframe: Data timeframe
            predicted_class: Predicted class (0=Down, 1=Neutral, 2=Up)
            probabilities: List of probabilities [down, neutral, up]
            prediction_date: Date of prediction (YYYY-MM-DD)
            model_version: Model version
        
        Returns:
            True if saved successfully
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO ml_predictions 
                    (symbol, timeframe, prediction_date, predicted_class,
                     confidence_down, confidence_neutral, confidence_up, model_version)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, prediction_date, predicted_class,
                      probabilities[0], probabilities[1], probabilities[2], model_version))
                
                conn.commit()
                logger.info(f"Saved prediction for {symbol} {timeframe} on {prediction_date}")
                return True
        
        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return False
    
    def update_actual_outcome(self, symbol: str, timeframe: str,
                             prediction_date: str, actual_class: int,
                             actual_return: float) -> bool:
        """
        Update prediction with actual outcome.
        
        Args:
            symbol: Stock symbol
            timeframe: Data timeframe
            prediction_date: Date of prediction
            actual_class: Actual class (0=Down, 1=Neutral, 2=Up)
            actual_return: Actual return percentage
        
        Returns:
            True if updated successfully
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Get predicted class
                cursor = conn.execute("""
                    SELECT predicted_class FROM ml_predictions
                    WHERE symbol=? AND timeframe=? AND prediction_date=?
                """, (symbol, timeframe, prediction_date))
                
                result = cursor.fetchone()
                if not result:
                    logger.warning(f"No prediction found for {symbol} {timeframe} on {prediction_date}")
                    return False
                
                predicted_class = result[0]
                is_correct = 1 if predicted_class == actual_class else 0
                
                # Update with actual outcome
                conn.execute("""
                    UPDATE ml_predictions
                    SET actual_class=?, actual_return=?, is_correct=?
                    WHERE symbol=? AND timeframe=? AND prediction_date=?
                """, (actual_class, actual_return, is_correct,
                      symbol, timeframe, prediction_date))
                
                conn.commit()
                logger.info(f"Updated actual outcome for {symbol} {timeframe} on {prediction_date}")
                return True
        
        except Exception as e:
            logger.error(f"Error updating actual outcome: {e}")
            return False
    
    def get_prediction_history(self, symbol: str, timeframe: str,
                              days: Optional[int] = None) -> pd.DataFrame:
        """
        Get prediction history for a symbol.
        
        Args:
            symbol: Stock symbol
            timeframe: Data timeframe
            days: Number of days to look back (None = all)
        
        Returns:
            DataFrame with prediction history
        """
        query = """
            SELECT prediction_date, predicted_class, 
                   confidence_down, confidence_neutral, confidence_up,
                   actual_class, actual_return, is_correct, model_version
            FROM ml_predictions
            WHERE symbol=? AND timeframe=?
        """
        
        params = [symbol, timeframe]
        
        if days:
            query += " AND prediction_date >= date('now', '-' || ? || ' days')"
            params.append(days)
        
        query += " ORDER BY prediction_date DESC"
        
        with sqlite3.connect(str(self.db_path)) as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        return df
    
    def calculate_accuracy(self, symbol: str, timeframe: str,
                          days: Optional[int] = 30) -> Dict:
        """
        Calculate accuracy metrics for predictions.
        
        Args:
            symbol: Stock symbol
            timeframe: Data timeframe
            days: Number of days to analyze
        
        Returns:
            Dictionary with accuracy metrics
        """
        df = self.get_prediction_history(symbol, timeframe, days)
        
        # Filter only predictions with actual outcomes
        df_with_outcomes = df[df['actual_class'].notna()]
        
        if len(df_with_outcomes) == 0:
            return {
                'total_predictions': 0,
                'predictions_with_outcomes': 0,
                'accuracy': 0.0,
                'precision_by_class': {},
                'recall_by_class': {}
            }
        
        total = len(df_with_outcomes)
        correct = df_with_outcomes['is_correct'].sum()
        accuracy = correct / total if total > 0 else 0.0
        
        # Calculate precision and recall by class
        precision_by_class = {}
        recall_by_class = {}
        
        for class_id in [0, 1, 2]:
            # Precision: of all predictions for this class, how many were correct?
            predicted_as_class = df_with_outcomes[df_with_outcomes['predicted_class'] == class_id]
            if len(predicted_as_class) > 0:
                precision = predicted_as_class['is_correct'].sum() / len(predicted_as_class)
                precision_by_class[class_id] = precision
            else:
                precision_by_class[class_id] = 0.0
            
            # Recall: of all actual occurrences of this class, how many did we predict?
            actual_class = df_with_outcomes[df_with_outcomes['actual_class'] == class_id]
            if len(actual_class) > 0:
                recall = actual_class['is_correct'].sum() / len(actual_class)
                recall_by_class[class_id] = recall
            else:
                recall_by_class[class_id] = 0.0
        
        return {
            'total_predictions': len(df),
            'predictions_with_outcomes': total,
            'correct_predictions': int(correct),
            'accuracy': accuracy,
            'precision_by_class': precision_by_class,
            'recall_by_class': recall_by_class
        }
    
    def get_recent_predictions(self, limit: int = 10) -> pd.DataFrame:
        """
        Get most recent predictions across all symbols.
        
        Args:
            limit: Number of predictions to return
        
        Returns:
            DataFrame with recent predictions
        """
        query = """
            SELECT symbol, timeframe, prediction_date, predicted_class,
                   confidence_down, confidence_neutral, confidence_up,
                   actual_class, is_correct
            FROM ml_predictions
            ORDER BY created_at DESC
            LIMIT ?
        """
        
        with sqlite3.connect(str(self.db_path)) as conn:
            df = pd.read_sql_query(query, conn, params=[limit])
        
        return df
    
    def save_model_performance(self, symbol: str, timeframe: str,
                              model_version: str, metrics: Dict) -> bool:
        """
        Save model performance metrics.
        
        Args:
            symbol: Stock symbol
            timeframe: Data timeframe
            model_version: Model version
            metrics: Dictionary with performance metrics
        
        Returns:
            True if saved successfully
        """
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute("""
                    INSERT INTO ml_model_performance
                    (symbol, timeframe, model_version, accuracy,
                     precision_down, precision_neutral, precision_up,
                     total_predictions, correct_predictions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (symbol, timeframe, model_version, metrics.get('accuracy', 0),
                      metrics.get('precision_by_class', {}).get(0, 0),
                      metrics.get('precision_by_class', {}).get(1, 0),
                      metrics.get('precision_by_class', {}).get(2, 0),
                      metrics.get('total_predictions', 0),
                      metrics.get('correct_predictions', 0)))
                
                conn.commit()
                logger.info(f"Saved performance metrics for {symbol} {timeframe} {model_version}")
                return True
        
        except Exception as e:
            logger.error(f"Error saving model performance: {e}")
            return False
