from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class PredictionRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., TCS)")
    timeframe: str = Field("1d", description="Data timeframe")
    
class PredictionResponse(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    predicted_price_change: Optional[str] = None
    timestamp: str

class BatchPredictionRequest(BaseModel):
    symbols: List[str]
    timeframe: str = "1d"

class ModelInfo(BaseModel):
    symbol: str
    timeframe: str
    model_type: str
    version: str
    accuracy: Optional[float] = None
