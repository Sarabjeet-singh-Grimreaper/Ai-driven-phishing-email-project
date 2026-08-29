import os
import sys
import pytest

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))

from app.services.prediction_service import prediction_service

def test_empty_string_regression():
    """Verify that passing an empty string to the prediction engine does not crash the system."""
    res = prediction_service.predict("")
    assert res["prediction"] == "SAFE"
    assert res["risk_score"] == 0
    assert "Empty input" in res["reason"]

def test_whitespace_string_regression():
    """Verify that passing whitespace-only strings is handled cleanly."""
    res = prediction_service.predict("   \n   ")
    assert res["prediction"] == "SAFE"
    assert res["risk_score"] == 0
    assert "Empty input" in res["reason"]
