"""
Automated Pytest Edge Case Verification Suite
---------------------------------------------
Validates the upgraded phishing detection model and feature extractor against:
1. Punycode URLs (Internationalized Domain Names lookalikes).
2. Multi-part MIME payload parsing.
3. HTML-based keyword obfuscations (HTML entities, hidden tags).
"""

import os
import sys
import pytest
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.services.prediction_service import prediction_service
from features.extractor import FeatureExtractor

@pytest.fixture
def extractor():
    return FeatureExtractor()

def test_punycode_url_reputation(extractor):
    """Verify that Punycode lookalike domains trigger similarity and entropy flags."""
    # xn--pypal-4qa.com translates to paypál.com
    email_text = "From: support@paypal.com\nSubject: Account Verification\n\nPlease login immediately at http://xn--pypal-4qa.com/login to verify your credentials."
    
    # Feature level verification
    features = extractor.extract_features(email_text)
    assert features["url_count"] > 0
    
    # Verify prediction service flags
    result = prediction_service.predict(email_text)
    assert result["prediction"] == "PHISHING"
    assert "Lookalike Domain Mimicry" in result["indicators"]

def test_multipart_mime_payload_extraction(extractor):
    """Verify that multi-part MIME formatted emails parse text and link heuristics correctly."""
    # Construct raw MIME message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "MIME multipart test alert"
    msg['From'] = "admin@micr0soft-portal.com"
    
    part1 = MIMEText("Action Required: Reset your credential password.", 'plain')
    part2 = MIMEText("<html><body>Please visit <a href='http://micr0soft-portal.com/login'>Secure Portal</a> immediately.</body></html>", 'html')
    
    msg.attach(part1)
    msg.attach(part2)
    
    raw_mime_string = msg.as_string()
    
    # Heuristics parsing
    features = extractor.extract_features(raw_mime_string)
    assert features["url_count"] >= 1.0
    assert features["urgency_score"] > 0.0
    assert features["credential_harvest_intent"] > 0.0
    
    # Prediction output check
    result = prediction_service.predict(raw_mime_string)
    assert result["prediction"] == "PHISHING"

def test_obfuscated_html_tags(extractor):
    """Verify that HTML entities and tag manipulation do not bypass intent keyword scoring."""
    # HTML entity obfuscation: "p&#97;ssword" -> "password"
    obfuscated_email = "From: service@paypal.com\nSubject: Security update\n\nEnter your user account details and p&#97;ssword immediately to prevent lockouts."
    
    # Preprocess text decode check inside extractor
    features = extractor.extract_features(obfuscated_email)
    
    # Predict on the email
    result = prediction_service.predict(obfuscated_email)
    
    # Obfuscation should trigger credential harvest intent and block
    assert result["prediction"] == "PHISHING"
    assert result["nlp_intents"]["credential_harvesting"] is True
    assert result["nlp_intents"]["urgency_lure"] is True
