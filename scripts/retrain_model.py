import argparse
import sys
from pathlib import Path
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from libs.ml_pipeline import train_model_for_symbol
from libs.mlflow_utils import MLflowManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retrainer")

def retrain_symbol(symbol: str, timeframe: str = '1d', classification: str = '3class'):
    """
    Retrain model for a symbol and log to MLflow.
    """
    logger.info(f"Starting automated retraining for {symbol} {timeframe}")
    
    try:
        # Initialize MLflow
        mlflow_manager = MLflowManager()
        run_name = f"auto_retrain_{symbol}_{pd.Timestamp.now().strftime('%Y%m%d')}"
        
        # Train model (logging is handled inside train_model if use_mlflow=True)
        # But train_model convenience function might need update or we call pipeline directly?
        # train_model_for_symbol calls pipeline methods.
        # We need to ensure MLflow usage.
        
        # Let's inspect train_model_for_symbol in libs/ml_pipeline.py
        # It calls pipeline.train_model(..., model_type=model_type)
        # We updated pipeline.train_model to accept use_mlflow=True by default.
        
        pipeline, metrics = train_model_for_symbol(
            symbol=symbol,
            timeframe=timeframe,
            classification=classification,
            model_type='xgboost'
        )
        
        logger.info(f"Retraining successful for {symbol}. Accuracy: {metrics['accuracy']:.2%}")
        
    except Exception as e:
        logger.error(f"Retraining failed for {symbol}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Model Retrainer")
    parser.add_argument("symbol", type=str, help="Stock symbol to retrain (e.g., TCS)")
    parser.add_argument("--timeframe", type=str, default="1d", help="Timeframe (default: 1d)")
    
    args = parser.parse_args()
    
    import pandas as pd
    retrain_symbol(args.symbol, args.timeframe)
