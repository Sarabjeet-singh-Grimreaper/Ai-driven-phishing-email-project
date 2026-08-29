from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any

class FlaggedTokenSchema(BaseModel):
    start: int
    end: int
    token: str
    type: str

class TextScanRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=150000, description="Raw text of the email or message to inspect")

class UrlScanRequest(BaseModel):
    url: str = Field(..., min_length=4, max_length=2048, description="Target URL string to evaluate reputation for")

class EmailAnalysisRequest(BaseModel):
    email: str

class AnalysisResponse(BaseModel):
    id: Optional[str] = None
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
    lexical_url_analysis: Optional[dict] = None
    nlp_intents: Optional[dict] = None
    flagged_tokens: Optional[List[FlaggedTokenSchema]] = []

class AsyncTaskAcceptedResponse(BaseModel):
    task_id: str
    status: str
    detail: str

class AsyncTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    result: Optional[AnalysisResponse] = None

class BatchEmailRequest(BaseModel):
    id: str
    email: str

class BatchScanRequest(BaseModel):
    items: List[BatchEmailRequest]

class BatchScanItemResponse(BaseModel):
    id: str
    status: str
    result: Optional[AnalysisResponse] = None
    error: Optional[str] = None

class BatchScanResponse(BaseModel):
    batch_id: str
    total_processed: int
    results: List[BatchScanItemResponse]

class DailyTrendItem(BaseModel):
    date: str
    total_count: int
    phishing_count: int
    safe_count: int

class BrandTrendItem(BaseModel):
    brand: str
    count: int

class SeverityBreakdown(BaseModel):
    critical: int
    high: int
    medium: int
    low: int

class HistoricalAnalyticsResponse(BaseModel):
    total_scanned: int
    phishing_detected: int
    safe_detected: int
    average_risk_score: float
    daily_trends: List[DailyTrendItem]
    top_target_brands: List[BrandTrendItem]
    severity_breakdown: SeverityBreakdown
    average_latency_ms: float
