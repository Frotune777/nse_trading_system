from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from api.schemas import PredictionRequest, PredictionResponse, BatchPredictionRequest, ModelInfo
from libs.ml_pipeline import MLPipeline
from libs.historical_data_manager import HistoricalDataManager
from libs.feature_engineering import FeatureEngineer
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(
    title="NSE Trading System API",
    description="ML-powered stock prediction API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Cache for Models
models_cache = {}

def get_pipeline(symbol: str, timeframe: str):
    """Load or retrieve cached pipeline."""
    key = f"{symbol}_{timeframe}"
    if key in models_cache:
        return models_cache[key]
    
    try:
        pipeline = MLPipeline(symbol, timeframe)
        # Check if model exists
        model_path = pipeline.model_dir / f"{symbol}_{timeframe}_v1.joblib"
        if not model_path.exists():
            return None
            
        pipeline.load_model(version='v1')
        models_cache[key] = pipeline
        return pipeline
    except Exception as e:
        logger.error(f"Error loading model for {key}: {e}")
        return None

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/models", response_model=list[ModelInfo])
async def list_models():
    """List all available trained models."""
    models_dir = Path("models")
    if not models_dir.exists():
        return []
        
    model_files = list(models_dir.glob("*_v1.joblib"))
    results = []
    
    for f in model_files:
        try:
            parts = f.stem.split('_')
            symbol = parts[0]
            timeframe = parts[1]
            
            # Simple metadata extraction logic could go here
            results.append(ModelInfo(
                symbol=symbol,
                timeframe=timeframe,
                model_type="Unknown", # Requires metadata load to be accurate
                version="v1" 
            ))
        except:
            continue
            
    return results

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Generate prediction for a specific symbol."""
    symbol = request.symbol.upper()
    timeframe = request.timeframe
    
    pipeline = get_pipeline(symbol, timeframe)
    if not pipeline:
        raise HTTPException(status_code=404, detail=f"Model not found for {symbol} {timeframe}")
    
    try:
        # Load latest data
        manager = HistoricalDataManager()
        df = manager.get_symbol_data(symbol, timeframe)
        
        if df.empty:
            raise HTTPException(status_code=500, detail="No historical data available")
            
        # Engineer features
        engineer = FeatureEngineer(df)
        features = engineer.build_all()
        
        if features.empty:
            raise HTTPException(status_code=500, detail="Feature engineering failed")
            
        # Get latest row
        latest_features = features.iloc[[-1]] 
        
        # Predict
        preds, probs = pipeline.predict(latest_features)
        
        # Format response
        class_idx = preds[0]
        prob_dist = probs[0]
        
        confidence = prob_dist[class_idx]
        
        labels = {0: "Down", 1: "Neutral", 2: "Up"} # Assuming 3-class
        if pipeline.classification_type == '2class':
             labels = {0: "Down", 1: "Up"}
        
        prediction_label = labels.get(class_idx, "Unknown")
        
        prob_dict = {labels.get(i, str(i)): float(p) for i, p in enumerate(prob_dist)}
        
        return PredictionResponse(
            symbol=symbol,
            prediction=prediction_label,
            confidence=float(confidence),
            probabilities=prob_dict,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
