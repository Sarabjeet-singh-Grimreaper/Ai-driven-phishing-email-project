from pydantic import BaseModel
from typing import List, Optional

class EmailAnalysisRequest(BaseModel):
    email: str

class AnalysisResponse(BaseModel):
    prediction: str
    confidence: float
    risk_score: int
    attack_type: str
    severity: str
    indicators: List[str]
    highlighted_email: str
    model: str
    reason: Optional[str] = None
    reasons: Optional[List[str]] = []
    feature_contributions: Optional[dict] = None
