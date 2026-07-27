import os
import re
import joblib
import pandas as pd
import numpy as np
from app.services.pipeline_utils import EmailFeatureExtractor, preprocess_text, BRANDS

# Resolve model path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "best_phishing_model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "metadata_scaler.joblib")


class PredictionService:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.extractor = EmailFeatureExtractor()
        self.load_models()

    def load_models(self):
        try:
            self.model = joblib.load(MODEL_PATH)
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            print("ML models loaded successfully.")
        except Exception as e:
            print(f"Primary model load failed: {e}. Path tried: {MODEL_PATH}")
            # Fallback path if loaded inside backend/
            try:
                # Correct root dir lookup: services is 3 levels down from root (app/services/prediction_service.py)
                ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                fallback_model_path = os.path.join(ROOT_DIR, "best_phishing_model.joblib")
                self.model = joblib.load(fallback_model_path)
                self.vectorizer = joblib.load(os.path.join(ROOT_DIR, "tfidf_vectorizer.joblib"))
                self.scaler = joblib.load(os.path.join(ROOT_DIR, "metadata_scaler.joblib"))
                print("ML models loaded from root directory via fallback.")
            except Exception as ex:
                print(f"Error loading ML models fallback: {ex}. Path tried: {fallback_model_path if 'fallback_model_path' in locals() else 'None'}")


    def predict(self, email_text: str):
        if not self.model or not self.vectorizer or not self.scaler:
            raise RuntimeError("Model services are not fully initialized. Please run training pipeline first.")

        # Input Validation
        if not email_text or not email_text.strip():
            raise ValueError("Input email text is empty.")
            
        cleaned_body = preprocess_text(email_text)
        
        # Extract features using shared utility
        features_df = self.extractor.transform([email_text])
        features = features_df.iloc[0].to_dict()
        
        # Transform for scikit-learn model
        meta_df = features_df.copy()
        
        # Scale features using the fitted scaler
        meta_scaled = pd.DataFrame(self.scaler.transform(meta_df), columns=meta_df.columns)
        
        tfidf_feat = self.vectorizer.transform([cleaned_body]).toarray()
        tfidf_df = pd.DataFrame(tfidf_feat, columns=self.vectorizer.get_feature_names_out())
        X_final = pd.concat([tfidf_df, meta_scaled], axis=1)
        
        prediction = int(self.model.predict(X_final)[0])
        confidence = float(self.model.predict_proba(X_final)[0][1]) if hasattr(self.model, "predict_proba") else 0.5
        
        # Risk Score Calculation (0 to 100 scale)
        if prediction == 0:
            risk_score = max(5, int((1 - confidence) * 30))
        else:
            risk_score = max(50, int(confidence * 100))
            
        severity = "Low"
        if risk_score > 85:
            severity = "Critical"
        elif risk_score > 65:
            severity = "High"
        elif risk_score > 35:
            severity = "Medium"

        # Threat Categorization (Phase 3)
        attack_type = "Legitimate communication"
        if prediction == 1:
            attack_type = "Business Email Compromise (BEC)"
            if "invoice" in email_text.lower() or "billing" in email_text.lower() or "overdue" in email_text.lower() or "payment" in email_text.lower():
                attack_type = "Invoice Fraud"
            elif "password" in email_text.lower() or "login" in email_text.lower() or "credentials" in email_text.lower() or "credential" in email_text.lower():
                attack_type = "Credential Theft"
            elif "delivery" in email_text.lower() or "fedex" in email_text.lower() or "dhl" in email_text.lower() or "ups" in email_text.lower() or "shipping" in email_text.lower():
                attack_type = "Delivery Scam"
            elif "crypto" in email_text.lower() or "wallet" in email_text.lower() or "bitcoin" in email_text.lower() or "ethereum" in email_text.lower():
                attack_type = "Crypto Scam"
            elif "bank" in email_text.lower() or "transfer" in email_text.lower() or "wire" in email_text.lower() or "account" in email_text.lower():
                attack_type = "Bank Scam"
            elif "tax" in email_text.lower() or "irs" in email_text.lower() or "refund" in email_text.lower():
                attack_type = "Tax Scam"
            elif "hr" in email_text.lower() or "salary" in email_text.lower() or "payroll" in email_text.lower() or "benefits" in email_text.lower() or "leave" in email_text.lower():
                attack_type = "HR Scam"
            elif features["sender_spoofing"] > 0 or features["domain_similarity_score"] > 0.8:
                attack_type = "Brand Mimicry / Spoofing"

        # Indicators & Explainable Reasons (Phase 2 & Phase 11)
        indicators = []
        reasons = []
        
        if prediction == 1:
            if features["sender_spoofing"] > 0:
                indicators.append("Sender Spoofing Detected")
                reasons.append("Sender spoofing display name matches brand but email domain differs")
            if features["domain_similarity_score"] > 0.8:
                indicators.append("Lookalike Domain (Brand Mimicry)")
                reasons.append("URL domain highly similar to reputable brand (homograph/mimicry)")
            if features["reply_to_mismatch"] > 0:
                indicators.append("Reply-To Domain Mismatch")
                reasons.append("Reply-To header domain mismatches the From header domain")
            if features["url_entropy"] > 4.5:
                indicators.append("High URL Entropy")
                reasons.append("URLs contain unusually complex/random strings (indicates obfuscation)")
            if features["url_redirects_count"] > 0:
                indicators.append("Multi-Redirect URL")
                reasons.append("URLs redirect via multiple hops to obscure final landing page")
            if features["ip_url_count"] > 0:
                indicators.append("IP-based URL Destination")
                reasons.append("Email links direct to raw IP addresses instead of registered domain names")
            if features["punycode_count"] > 0:
                indicators.append("Punycode Domain Obfuscation")
                reasons.append("Links contain Cyrillic or non-standard characters (Punycode)")
            if features["shortened_url_count"] > 0:
                indicators.append("URL Shortener Redirect")
                reasons.append("Contains shortened URLs (e.g. bit.ly) to mask final landing page")
            if features["has_suspicious_tld"] > 0:
                indicators.append("Suspicious TLD Extension")
                reasons.append("Contains link or reference to high-risk top-level domain (.zip, .ru, .xyz)")
            if features["urgency_count"] > 1:
                indicators.append("Urgency Lure Detection")
                reasons.append("High count of psychological urgency keywords (e.g. immediately, suspend)")
            if features["has_mfa_lure"] > 0:
                indicators.append("MFA Bypass / OTP Request")
                reasons.append("Requests verification code, passcode or one-time authenticator keys")
            if features["money_char_count"] > 1:
                indicators.append("Financial Lure Signature")
                reasons.append("Heavy references to money transactions, invoices, or wire transfers")
            if features["imperative_ratio"] > 0.05:
                indicators.append("Call to Action Commands")
                reasons.append("High proportion of imperative verb commands (click, log, check, pay)")
            
            # Default fallback reason
            if not reasons:
                reasons.append("High structural and lexical similarity to historical phishing templates")
                indicators.append("Unstructured Semantic Signature")
        else:
            reasons.append("Matches clean email characteristics; headers and link safety score are positive.")
            indicators.append("Clean Security Footprints")

        # Phase 5: Defender-style Color Highlighting
        # 🔴 URLs, 🟠 Password, 🟢 Company, 🔵 OTP, 🟣 Money
        highlighted_email = email_text
        highlighted_email = highlighted_email.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # 1. Company/Brand: Green (Microsoft, Amazon, Google, PayPal, Apple, Facebook, Netflix, DHL, FedEx, LinkedIn)
        for brand in BRANDS:
            highlighted_email = re.sub(
                f"\\b({brand})\\b", 
                r"<mark style='background-color: rgba(34, 197, 94, 0.2); color: #22c55e; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
            
        # 2. Password: Orange (password, credential, credentials, login, user, verify, verification, account, update, authenticating, signin, reset)
        password_terms = ['password', 'credential', 'credentials', 'login', 'verify', 'verification', 'reset', 'signin', 'auth']
        for term in password_terms:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(249, 115, 22, 0.2); color: #f97316; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
            
        # 3. OTP: Blue (mfa, 2fa, otp, authenticator, passcode, one-time, code, token)
        otp_terms = ['mfa', '2fa', 'otp', 'authenticator', 'passcode', 'one-time', 'token']
        for term in otp_terms:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(59, 130, 246, 0.2); color: #3b82f6; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
            
        # 4. Money: Purple ($, €, £, usd, transfer, wire, payment, invoice, salary, payroll, refund, billing, cost, fee)
        money_terms = ['usd', 'transfer', 'wire', 'payment', 'invoice', 'salary', 'payroll', 'refund', 'billing', 'cost', 'fee', 'price']
        for term in money_terms:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(168, 85, 247, 0.2); color: #a855f7; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
        # Regex for currency symbols specifically
        highlighted_email = re.sub(
            r'([\$€£¥])',
            r"<mark style='background-color: rgba(168, 85, 247, 0.2); color: #a855f7; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>",
            highlighted_email
        )
            
        # 5. URLs: Red (https?://\S+|www\.\S+)
        # Ensure we don't highlight the links inside previous marks
        highlighted_email = re.sub(
            r'(?<!color:\s)(https?://\S+|www\.\S+)',
            r"<mark style='background-color: rgba(239, 68, 68, 0.2); color: #ef4444; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>",
            highlighted_email,
            flags=re.IGNORECASE
        )
        
        highlighted_email = highlighted_email.replace("\n", "<br>")

        # Primary reason string
        reason_str = reasons[0] if reasons else "Indeterminate scan fingerprint"

        return {
            "prediction": "PHISHING" if prediction == 1 else "SAFE",
            "confidence": round(confidence * 100, 2) if prediction == 1 else round((1 - confidence) * 100, 2),
            "risk_score": risk_score,
            "attack_type": attack_type,
            "severity": severity,
            "indicators": indicators,
            "highlighted_email": highlighted_email,
            "model": "Random Forest (Tuned)",
            "reason": reason_str,
            "reasons": reasons
        }

prediction_service = PredictionService()
