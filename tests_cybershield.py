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

    def test_async_scanning_endpoint(self):
        payload = {"email": "Please update your credentials immediately at http://secure-update-login.com"}
        response = self.client.post("/api/analyze-email/async", json=payload)
        self.assertEqual(response.status_code, 202)
        json_data = response.json()
        self.assertIn("task_id", json_data)
        self.assertEqual(json_data["status"], "pending")

        # Poll status
        task_id = json_data["task_id"]
        status_resp = self.client.get(f"/api/analyze-email/tasks/{task_id}")
        self.assertEqual(status_resp.status_code, 200)
        status_data = status_resp.json()
        self.assertEqual(status_data["task_id"], task_id)
        self.assertIn(status_data["status"], ["pending", "processing", "completed"])

    def test_batch_processing_endpoint(self):
        payload = {
            "items": [
                {"id": "file1", "email": "Legitimate check-in details for the upcoming meeting."},
                {"id": "file2", "email": "Urgent wire transfer required for invoice #4852."}
            ]
        }
        response = self.client.post("/api/analyze-email/batch", json=payload)
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("batch_id", json_data)
        self.assertEqual(json_data["total_processed"], 2)
        self.assertEqual(len(json_data["results"]), 2)
        self.assertEqual(json_data["results"][0]["id"], "file1")
        self.assertEqual(json_data["results"][1]["id"], "file2")

    def test_historical_analytics_endpoint(self):
        response = self.client.get("/api/analytics/history")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIn("total_scanned", json_data)
        self.assertIn("daily_trends", json_data)
        self.assertIn("top_target_brands", json_data)
        self.assertIn("severity_breakdown", json_data)

class TestCyberShieldHeuristics(unittest.TestCase):
    def test_spf_dkim_verification_parsing(self):
        # Fail SPF/DKIM
        fail_email = "Authentication-Results: mx.google.com; spf=fail dkim=fail\nSubject: Update password"
        features_df = EmailFeatureExtractor().transform([fail_email])
        self.assertEqual(features_df.iloc[0]["has_spf"], 0.0)
        self.assertEqual(features_df.iloc[0]["has_dkim"], 0.0)

        # Pass SPF/DKIM
        pass_email = "Received-SPF: pass\nDKIM-Signature: v=1; ...\nSubject: Normal update"
        features_df_pass = EmailFeatureExtractor().transform([pass_email])
        self.assertEqual(features_df_pass.iloc[0]["has_spf"], 1.0)
        self.assertEqual(features_df_pass.iloc[0]["has_dkim"], 1.0)

    def test_lexical_url_heuristics(self):
        # Obfuscation via @ symbol
        at_email = "Click here: http://paypal.com@attacker-site.com/login"
        res = prediction_service.predict(at_email)
        self.assertEqual(res["prediction"], "PHISHING")
        self.assertTrue(res["lexical_url_analysis"]["has_at_symbol_obfuscation"])
        self.assertTrue(res["lexical_url_analysis"]["has_login_lure_path"])

    def test_nlp_intent_scanning(self):
        # Action Urgency & MFA bypass lure
        intent_email = "Enter your password and one-time passcode immediately or we will suspend your account."
        res = prediction_service.predict(intent_email)
        self.assertTrue(res["nlp_intents"]["urgency_lure"])
        self.assertTrue(res["nlp_intents"]["mfa_otp_lure"])
        self.assertTrue(res["nlp_intents"]["credential_harvesting"])

if __name__ == "__main__":
    unittest.main()
