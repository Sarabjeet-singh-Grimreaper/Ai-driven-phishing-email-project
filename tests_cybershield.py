import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add backend to sys.path to resolve packages
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.services.pipeline_utils import preprocess_text, EmailFeatureExtractor
from app.services.prediction_service import prediction_service
from backend.main import app

class TestCyberShieldPipeline(unittest.TestCase):
    def test_text_preprocessing(self):
        # HTML tag stripping and stopwords removal check
        html_input = "<html>Dear PayPal User, please <p>reset your password immediately</p>!</html>"
        expected = "dear paypal user please reset password immediately"
        result = preprocess_text(html_input)
        self.assertEqual(result, expected)
        
    def test_feature_extractor_rich_indicators(self):
        extractor = EmailFeatureExtractor()
        emails = [
            "Urgent: Reset password at http://paypa1.com/secure immediately!",
            "Normal email conversation without links or urgency keywords."
        ]
        features_df = extractor.transform(emails)
        
        # Checking features shapes
        self.assertEqual(len(features_df), 2)
        
        # Verify URL details extracted
        self.assertEqual(features_df.iloc[0]["url_count"], 1.0)
        self.assertGreater(features_df.iloc[0]["domain_similarity_score"], 0.8) # paypal similarity
        self.assertEqual(features_df.iloc[1]["url_count"], 0.0)
        
        # Verify NLP details extracted
        self.assertGreater(features_df.iloc[0]["urgency_count"], 0.0)
        self.assertEqual(features_df.iloc[1]["urgency_count"], 0.0)

    def test_prediction_service_outputs(self):
        # Predict on a typical phishing email
        phish_text = "From: security@paypa1.com\nSubject: Action Required: Reset Password\nReceived-SPF: fail\nVerify your credentials immediately at http://paypa1.com"
        result = prediction_service.predict(phish_text)
        
        self.assertEqual(result["prediction"], "PHISHING")
        self.assertGreater(result["confidence"], 50.0)
        self.assertIn("Lookalike Domain Mimicry", result["indicators"])
        self.assertEqual(result["severity"], "High")
        
        # Predict on a clean email
        clean_text = "Hi Team, thanks for the monthly product updates. Let me know if you agree. Regards."
        clean_result = prediction_service.predict(clean_text)
        self.assertEqual(clean_result["prediction"], "SAFE")
        self.assertEqual(clean_result["severity"], "Low")

class TestCyberShieldAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_api_gateway_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "AI CyberShield API Gateway is online."})

    def test_analyze_email_endpoint_phishing(self):
        payload = {
            "email": "From: Microsoft Team\nSubject: Account Terminated\nVerify account password immediately at http://micr0soft.com/login"
        }
        response = self.client.post("/api/analyze-email", json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data["prediction"], "PHISHING")
        self.assertEqual(json_data["attack_type"], "Credential Theft")
        self.assertIn("reason", json_data)

    def test_analyze_email_input_validation(self):
        # Empty payload check
        response = self.client.post("/api/analyze-email", json={"email": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Email body content cannot be empty.")
        
        # Oversized payload check
        response = self.client.post("/api/analyze-email", json={"email": "a" * 160000})
        self.assertEqual(response.status_code, 400)
        self.assertTrue("exceeds the maximum size" in response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
