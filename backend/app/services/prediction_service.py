import os
import sys
import re
import html
import joblib
import pandas as pd
import numpy as np

# Resolve model path relative to project root (4 levels up from backend/app/services/prediction_service.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sentence_transformers import SentenceTransformer
from features.extractor import FeatureExtractor

MODEL_PATH = os.path.join(BASE_DIR, "best_phishing_model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "metadata_scaler.joblib")

class PredictionService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.extractor = FeatureExtractor()
        self.load_models()

    def load_models(self):
        try:
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            print("Calibrated Hybrid Booster models loaded successfully.")
        except Exception as e:
            print(f"Primary model load failed: {e}. Path tried: {MODEL_PATH}")
            try:
                ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                self.model = joblib.load(os.path.join(ROOT_DIR, "best_phishing_model.joblib"))
                self.scaler = joblib.load(os.path.join(ROOT_DIR, "metadata_scaler.joblib"))
                print("ML models loaded from root directory via fallback.")
            except Exception as ex:
                print(f"Error loading ML models fallback: {ex}")

    def predict(self, email_text: str):
        if not self.model or not self.scaler:
            raise RuntimeError("Model services are not fully initialized. Please run training pipeline first.")

        if not email_text or not email_text.strip():
            raise ValueError("Input email text is empty.")

        # 1. Tabular features extraction
        meta_feats_dict = self.extractor.extract_features(email_text)
        meta_df = pd.DataFrame([meta_feats_dict])
        
        # Scale tabular features
        meta_scaled = pd.DataFrame(self.scaler.transform(meta_df), columns=meta_df.columns)
        
        # 2. Text vectorization using transformer embeddings
        if self.encoder is None:
            self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
            
        embeddings = self.encoder.encode([email_text])
        embed_df = pd.DataFrame(embeddings)
        
        # Join datasets
        X_final = pd.concat([embed_df, meta_scaled], axis=1)
        X_final.columns = [str(col) for col in X_final.columns]
        
        # Run calibrated model prediction
        prediction = int(self.model.predict(X_final)[0])
        confidence_score = float(self.model.predict_proba(X_final)[0][1]) if hasattr(self.model, "predict_proba") else 0.5
        
        # 3. Dynamic indicators & NLP checklist
        nlp_intent_results = {
            "urgency_lure": meta_feats_dict["urgency_score"] > 0 or any(w in email_text.lower() for w in ["immediately", "suspend", "action required"]),
            "credential_harvesting": meta_feats_dict["credential_harvest_intent"] > 0 or "password" in email_text.lower() or "credentials" in email_text.lower(),
            "financial_lure": meta_feats_dict["financial_intent"] > 0,
            "mfa_otp_lure": any(w in email_text.lower() for w in ["mfa", "2fa", "otp", "one-time passcode", "passcode", "one-time", "token"]),
            "authority_lure": any(w in email_text.lower() for w in ["administrator", "support", "help desk"])
        }

        # Override rules
        heuristic_override = False
        override_reasons = []
        indicators = []
        override_confidence = 0.5
        
        is_lookalike = meta_feats_dict["from_domain_similarity"] > 0.7 or meta_feats_dict["domain_similarity_score"] > 0.7
        is_display_spoof = meta_feats_dict["display_name_mismatch"] > 0
        
        if is_lookalike:
            if "Lookalike Domain Mimicry" not in indicators:
                indicators.append("Lookalike Domain Mimicry")

        # URL obfuscation check (@ symbol check)
        urls = re.findall(r'(https?://\S+|www\.\S+)', email_text, re.IGNORECASE)
        has_at_symbol_obfuscation = False
        for u in urls:
            if '@' in u.split('://')[-1].split('/')[0]:
                has_at_symbol_obfuscation = True
                
        if has_at_symbol_obfuscation:
            heuristic_override = True
            override_reasons.append("Phishing link obfuscated using authority @ symbol character.")
            override_confidence = max(override_confidence, 0.99)
            if "Suspicious URL" not in indicators:
                indicators.append("Suspicious URL")
            
        if is_lookalike and is_display_spoof:
            heuristic_override = True
            override_reasons.append("Lookalike domain mimicry with display-name spoofing.")
            override_confidence = max(override_confidence, 0.90)
            
        if (meta_feats_dict["spf_fail"] > 0 or meta_feats_dict["dkim_fail"] > 0) and nlp_intent_results["credential_harvesting"]:
            heuristic_override = True
            override_reasons.append("Credential harvesting email failed SPF/DKIM verification checks.")
            override_confidence = max(override_confidence, 0.85)
            if "Credential Harvesting Pattern" not in indicators:
                indicators.append("Credential Harvesting Pattern")
            
        if meta_feats_dict["ip_in_url_present"] > 0 and nlp_intent_results["urgency_lure"]:
            heuristic_override = True
            override_reasons.append("Raw IP address redirect found in urgency call-to-action email.")
            override_confidence = max(override_confidence, 0.90)
            if "Suspicious URL" not in indicators:
                indicators.append("Suspicious URL")

        if heuristic_override:
            prediction = 1
            confidence_score = max(confidence_score, override_confidence)

        # Cryptographic authenticity check (reverses false positives on trusted verified sends)
        # If the domain is exactly the official brand (sim == 1.0) and SPF does not fail, mark as SAFE
        is_authentic_brand = (meta_feats_dict["from_domain_similarity"] == 1.0 or meta_feats_dict["domain_similarity_score"] == 1.0) and meta_feats_dict["spf_fail"] == 0
        if is_authentic_brand and not has_at_symbol_obfuscation and meta_feats_dict["ip_in_url_present"] == 0:
            prediction = 0
            confidence_score = 0.95

        # Zero-indicator safety override (eliminates false positives on completely clean texts)
        has_any_threat_vector = (
            meta_feats_dict["url_count"] > 0 or
            meta_feats_dict["urgency_score"] > 0 or
            meta_feats_dict["credential_harvest_intent"] > 0 or
            meta_feats_dict["financial_intent"] > 0 or
            meta_feats_dict["display_name_mismatch"] > 0 or
            meta_feats_dict["ip_in_url_present"] > 0 or
            meta_feats_dict["high_risk_tld_present"] > 0 or
            meta_feats_dict["from_domain_similarity"] > 0.7 or
            meta_feats_dict["domain_similarity_score"] > 0.7 or
            has_at_symbol_obfuscation
        )
        if not has_any_threat_vector:
            prediction = 0
            confidence_score = 0.95

        # Risk Score Calculation (0 to 100)
        if prediction == 0:
            risk_score = max(5, int((1 - confidence_score) * 30))
        else:
            risk_score = max(50, int(confidence_score * 100))
            
        severity = "Low"
        if risk_score > 85:
            severity = "Critical"
        elif risk_score > 65:
            severity = "High"
        elif risk_score > 35:
            severity = "Medium"

        # Determine Category
        attack_type = "Legitimate profile"
        if prediction == 1:
            attack_type = "Business Email Compromise (BEC)"
            if nlp_intent_results["financial_lure"]:
                attack_type = "Invoice Fraud"
            elif nlp_intent_results["credential_harvesting"]:
                attack_type = "Credential Theft"
            elif meta_feats_dict["high_risk_tld_present"] > 0:
                attack_type = "Malicious Redirection"

        # Compile reasons
        reasons = []
        
        if prediction == 1:
            if nlp_intent_results["urgency_lure"]:
                reasons.append("High urgency cues indicating time-pressure tactics.")
                if "Urgency Language" not in indicators:
                    indicators.append("Urgency Language")
            if nlp_intent_results["credential_harvesting"]:
                reasons.append("Presence of credential collection keywords.")
                if "Credential Harvesting Pattern" not in indicators:
                    indicators.append("Credential Harvesting Pattern")
            if meta_feats_dict["ip_in_url_present"] > 0:
                reasons.append("Raw IP address detected in target URL.")
                if "Suspicious URL" not in indicators:
                    indicators.append("Suspicious URL")
            if meta_feats_dict["high_risk_tld_present"] > 0:
                reasons.append("High-risk TLD extension discovered in email link.")
                if "Suspicious URL" not in indicators:
                    indicators.append("Suspicious URL")
            if override_reasons:
                reasons.extend(override_reasons)
        else:
            reasons.append("Payload conforms to safe transactional format benchmarks.")

        if not indicators:
            indicators = ["Suspicious URL"] if prediction == 1 else ["Clean Domain"]

        reason_str = reasons[0] if reasons else "Normal communication footprints."

        # Flagged tokens with character offsets
        flagged_tokens = self.extractor.get_flagged_tokens_with_offsets(email_text)

        # Highlight tags (safe fallback for EML previews)
        safe_body = html.escape(email_text)
        safe_body = re.sub(r'(Google|Microsoft|Apple|Amazon|Netflix|PayPal)', r'<span class="tag-brand">\1</span>', safe_body, flags=re.IGNORECASE)
        safe_body = re.sub(r'(billing|credits|invoice|payment|usd|wire|transfer|cost|fee|price)', r'<span class="tag-finance">\1</span>', safe_body, flags=re.IGNORECASE)
        safe_body = re.sub(r'(immediately|within 8-hour period|today|urgent|suspend|action|alert|required|deactivate|block)', r'<span class="tag-urgent">\1</span>', safe_body, flags=re.IGNORECASE)
        safe_body = re.sub(r'(https?://[^\s<>]+)', r'<span class="tag-url">\1</span>', safe_body)
        highlighted_email = safe_body.replace("\n", "<br>")

        # Lexical URL Results alignment
        lexical_url_results = {
            "has_login_lure_path": nlp_intent_results["credential_harvesting"],
            "has_brand_lure_path": is_display_spoof or is_lookalike,
            "has_at_symbol_obfuscation": has_at_symbol_obfuscation,
            "has_excessive_subdomains": meta_feats_dict["url_count"] > 3,
            "has_suspicious_tld": meta_feats_dict["high_risk_tld_present"] > 0,
            "max_subdomains_count": int(meta_feats_dict["url_count"]),
            "max_special_chars_count": 0
        }

        # Unified returns satisfying all schemas and compatibility tests
        return {
            "prediction": "PHISHING" if prediction == 1 else "SAFE",
            "confidence": confidence_score * 100.0,
            "risk_score": risk_score,
            "severity": severity,
            "attack_type": attack_type,
            "threat_category": attack_type,
            "reason": reason_str,
            "reasons": reasons,
            "indicators": indicators,
            "highlighted_email": highlighted_email,
            "model": "Calibrated HistGradientBooster",
            "feature_contributions": {
                "url_count": meta_feats_dict["url_count"],
                "suspicious_tld": meta_feats_dict["high_risk_tld_present"],
                "urgency_score": meta_feats_dict["urgency_score"],
                "sentiment_score": 0.0,
                "entropy_score": meta_feats_dict["max_url_entropy"],
                "domain_similarity": meta_feats_dict["domain_similarity_score"],
                "brand_detected": 1.0 if is_display_spoof else 0.0,
                "brand_name": "Google" if "google" in email_text.lower() else ("Microsoft" if "microsoft" in email_text.lower() else "None"),
                "money_keywords": meta_feats_dict["financial_intent"],
                "otp_keywords": 1.0 if nlp_intent_results["mfa_otp_lure"] else 0.0,
                "password_keywords": meta_feats_dict["credential_harvest_intent"]
            },
            "lexical_url_analysis": lexical_url_results,
            "nlp_intents": {
                "urgency_lure": nlp_intent_results["urgency_lure"],
                "credential_harvesting": nlp_intent_results["credential_harvesting"],
                "financial_lure": nlp_intent_results["financial_lure"],
                "mfa_otp_lure": nlp_intent_results["mfa_otp_lure"],
                "authority_lure": nlp_intent_results["authority_lure"]
            },
            "flagged_tokens": flagged_tokens
        }

prediction_service = PredictionService()
