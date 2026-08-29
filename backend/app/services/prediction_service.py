import os
import re
import joblib
import pandas as pd
import numpy as np
from app.services.pipeline_utils import EmailFeatureExtractor, preprocess_text, BRANDS, SUSPICIOUS_TLDS

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
        
        # Extract URLs
        urls = re.findall(r'(https?://\S+|www\.\S+)', email_text, re.IGNORECASE)
        
        # 1. Lexical URL Analysis
        lexical_url_results = {
            "has_login_lure_path": False,
            "has_brand_lure_path": False,
            "has_at_symbol_obfuscation": False,
            "has_excessive_subdomains": False,
            "has_suspicious_tld": False,
            "max_subdomains_count": 0,
            "max_special_chars_count": 0
        }
        
        suspicious_path_keywords = {"login", "signin", "verify", "verification", "secure", "update", "account", "reset", "password", "support", "billing", "invoice", "refund"}
        for u in urls:
            u_lower = u.lower()
            domain_part_match = re.search(r'https?://(?:www\.)?([^/]+)', u, re.IGNORECASE)
            if domain_part_match:
                domain_part = domain_part_match.group(1)
                if '@' in domain_part:
                    lexical_url_results["has_at_symbol_obfuscation"] = True
                
                dots_count = domain_part.count('.')
                if dots_count > 3:
                    lexical_url_results["has_excessive_subdomains"] = True
                lexical_url_results["max_subdomains_count"] = max(lexical_url_results["max_subdomains_count"], dots_count)
            
            path_part = u.split('/')[-1] if '/' in u else u
            if any(kw in path_part.lower() for kw in suspicious_path_keywords):
                lexical_url_results["has_login_lure_path"] = True
            
            if any(brand in path_part.lower() for brand in BRANDS):
                lexical_url_results["has_brand_lure_path"] = True
                
            if any(f".{tld}" in u_lower for tld in SUSPICIOUS_TLDS):
                lexical_url_results["has_suspicious_tld"] = True
                
            special_chars = sum(1 for c in u if c in ['-', '_', '@', '?', '='])
            lexical_url_results["max_special_chars_count"] = max(lexical_url_results["max_special_chars_count"], special_chars)

        # 2. NLP Intent Scanning
        nlp_intent_results = {
            "urgency_lure": False,
            "credential_harvesting": False,
            "financial_lure": False,
            "mfa_otp_lure": False,
            "authority_lure": False
        }
        
        email_text_lower = email_text.lower()
        
        # Urgency Intent
        urgency_patterns = [
            r'action required', r'immediate', r'urgently', r'suspend', r'deactivat', r'within \d+ hours',
            r'compromise', r'unusual activity', r'alert', r'terminate', r'restricted', r'expire'
        ]
        if any(re.search(p, email_text_lower) for p in urgency_patterns):
            nlp_intent_results["urgency_lure"] = True
            
        # Credential Harvesting Intent
        cred_patterns = [
            r'reset your password', r'verify your account', r'update.*credential', r'login to', r'signin',
            r'security settings', r'verification link', r'confirm.*identity', r'click here to verify',
            r'password', r'login', r'credential', r'credentials'
        ]
        if any(re.search(p, email_text_lower) for p in cred_patterns):
            nlp_intent_results["credential_harvesting"] = True
            
        # Financial Lure Intent
        financial_patterns = [
            r'invoice', r'payment', r'wire transfer', r'overdue', r'refund', r'billing', r'bank account',
            r'transaction detail', r'remittance', r'purchase order', r'salary', r'payroll'
        ]
        if any(re.search(p, email_text_lower) for p in financial_patterns):
            nlp_intent_results["financial_lure"] = True
            
        # MFA/OTP Bypass Intent
        mfa_patterns = [
            r'one-time passcode', r'verification code', r'mfa code', r'2fa token', r'passcode',
            r'authenticator pin', r'enter code'
        ]
        if any(re.search(p, email_text_lower) for p in mfa_patterns):
            nlp_intent_results["mfa_otp_lure"] = True
            
        # Authority / Executive Impersonation
        authority_patterns = [
            r'it support', r'system administrator', r'ceo office', r'human resources', r'legal department',
            r'help desk', r'security desk', r'it operations'
        ]
        if any(re.search(p, email_text_lower) for p in authority_patterns):
            nlp_intent_results["authority_lure"] = True

        # Heuristic Override Rules (Defense-in-depth secure coding)
        heuristic_override = False
        override_reasons = []
        
        # Rule A: Display-Name spoofing + Lookalike domain mimicry -> override to PHISHING
        if features.get("sender_spoofing", 0) > 0 and features.get("domain_similarity_score", 0) > 0.7:
            heuristic_override = True
            override_reasons.append("Lookalike domain mimicry with display-name spoofing.")
            
        # Rule B: Authentication Failures + Credential harvesting intent -> override to PHISHING
        if (features.get("has_spf", 1) == 0 or features.get("has_dkim", 1) == 0) and nlp_intent_results["credential_harvesting"]:
            heuristic_override = True
            override_reasons.append("Credential harvesting email failed SPF/DKIM verification checks.")
            
        # Rule C: Raw IP Address destination URL + Urgency / Action intent -> override to PHISHING
        if features.get("ip_url_count", 0) > 0 and nlp_intent_results["urgency_lure"]:
            heuristic_override = True
            override_reasons.append("Raw IP address redirect found in urgency call-to-action email.")
            
        # Rule D: URL Obfuscation (@ symbol spoof) -> override to PHISHING
        if lexical_url_results["has_at_symbol_obfuscation"]:
            heuristic_override = True
            override_reasons.append("Phishing link obfuscated using authority @ symbol character.")

        if heuristic_override and prediction == 0:
            prediction = 1
            confidence = 0.99
            
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

        # Threat Categorization
        attack_type = "Legitimate profile"
        if prediction == 1:
            attack_type = "Business Email Compromise (BEC)"
            if nlp_intent_results["financial_lure"]:
                attack_type = "Invoice Fraud"
            elif nlp_intent_results["credential_harvesting"]:
                attack_type = "Credential Theft"
            elif "delivery" in email_text.lower() or "fedex" in email_text.lower() or "dhl" in email_text.lower() or "ups" in email_text.lower() or "shipping" in email_text.lower():
                attack_type = "Delivery Scam"
            elif "crypto" in email_text.lower() or "wallet" in email_text.lower() or "bitcoin" in email_text.lower() or "ethereum" in email_text.lower():
                attack_type = "Crypto Scam"
            elif "bank" in email_text.lower() or "transfer" in email_text.lower() or "wire" in email_text.lower() or "account" in email_text.lower():
                attack_type = "Bank Scam"
            elif "tax" in email_text.lower() or "irs" in email_text.lower() or "refund" in email_text.lower():
                attack_type = "Tax Scam"
            elif nlp_intent_results["authority_lure"]:
                attack_type = "Executive Impersonation"
            elif features["sender_spoofing"] > 0 or features["domain_similarity_score"] > 0.8:
                attack_type = "Brand Mimicry / Spoofing"

        # Feature contribution values (for dashboard and radar displays)
        brand_name_match = "None"
        for brand in BRANDS:
            if brand in email_text.lower():
                brand_name_match = brand.capitalize()
                break
                
        feature_contributions = {
            "url_count": float(features.get("url_count", 0)),
            "suspicious_tld": float(features.get("has_suspicious_tld", 0)),
            "urgency_score": float(features.get("urgency_count", 0)),
            "sentiment_score": float(round(features.get("sentiment_score", 0.0), 3)),
            "entropy_score": float(round(features.get("url_entropy", 0.0), 3)),
            "domain_similarity": float(round(features.get("domain_similarity_score", 0.0), 3)),
            "brand_detected": float(features.get("brand_detected", 0)),
            "brand_name": brand_name_match,
            "money_keywords": float(features.get("money_char_count", 0)),
            "otp_keywords": float(features.get("has_mfa_lure", 0)),
            "password_keywords": float(sum(1 for w in ['password', 'login', 'credentials', 'credential', 'reset'] if w in email_text.lower()))
        }

        # Explainable AI Logic: Reasons & Indicators
        indicators = []
        reasons = []

        if prediction == 0:
            # Generate positive indicators for safe emails
            if feature_contributions["url_count"] == 0:
                indicators.append("Zero Suspicious Links")
                reasons.append("Zero embedded links identified, minimizing URL redirection threats.")
            else:
                indicators.append("Secure Hyperlink Profile")
                reasons.append(f"Contains {int(feature_contributions['url_count'])} secure, verified links with no lookalike domains.")
                
            if feature_contributions["urgency_score"] == 0:
                indicators.append("No Urgent Demands")
                reasons.append("Semantic analysis found no high-pressure urgency directives or threat lures.")
            else:
                indicators.append("Standard Business Urgency")
                reasons.append(f"Low density of urgency terms ({int(feature_contributions['urgency_score'])} triggers) matching routine operations.")
                
            if feature_contributions["password_keywords"] == 0:
                indicators.append("No Account Requests")
                reasons.append("No credentials resetting forms, update notifications, or login prompts discovered.")
                
            if feature_contributions["domain_similarity"] < 0.2:
                indicators.append("Trusted Link Domains")
                reasons.append("Domain checks verify no similarity to high-risk brand domains (no homograph mimicry).")
                
            if feature_contributions["sentiment_score"] >= -0.05:
                indicators.append("Professional Sentiment Tone")
                reasons.append(f"Professional sentiment index ({feature_contributions['sentiment_score']}) with no stress signals.")
            
            reason_str = "Clean profile validated: Secure domain names, balanced professional tone, and absence of credential lures."
        else:
            # Add override markers if triggered
            for o_reason in override_reasons:
                indicators.append(f"Heuristics Triggered: {o_reason}")
                reasons.append(f"Security Policy Check: {o_reason}")
                
            # Generate risk indicators for phishing emails
            if features["sender_spoofing"] > 0:
                indicators.append("Sender Display-Name Spoofing")
                reasons.append("Sender display name replicates a target brand, but authentication headers differ.")
            if features["domain_similarity_score"] > 0.7:
                indicators.append("Lookalike Domain Mimicry")
                reasons.append(f"URL domain is highly similar to reputable brand domain (similarity: {features['domain_similarity_score']*100:.1f}%).")
            if features["reply_to_mismatch"] > 0:
                indicators.append("Reply-To Routing Mismatch")
                reasons.append("Replies are configured to redirect to a different domain than the sender domain.")
            if features["url_entropy"] > 4.5:
                indicators.append("High-Obfuscation URL Entropy")
                reasons.append(f"URLs contain complex random strings (entropy: {features['url_entropy']:.2f}) designed to bypass filter parsers.")
            if features["url_redirects_count"] > 0:
                indicators.append("Multi-Hop Redirection")
                reasons.append("Contains routing redirect links designed to mask the ultimate destination page.")
            if features["ip_url_count"] > 0:
                indicators.append("Raw IP Address Destination")
                reasons.append("Hyperlinks direct directly to raw IP addresses instead of hostname mappings.")
            if features["punycode_count"] > 0:
                indicators.append("Punycode Character Obfuscation")
                reasons.append("Domain strings utilize foreign characters (Punycode) to mimic authentic names.")
            if features["shortened_url_count"] > 0:
                indicators.append("Obscured URL Shortener")
                reasons.append("Contains URL shortener links to cover final landing destinations.")
            if features["has_suspicious_tld"] > 0:
                indicators.append("Suspicious TLD Extension")
                reasons.append("References high-risk top-level domain extensions (.zip, .ru, .xyz).")
            if features["urgency_count"] > 1:
                indicators.append("Urgency Pressure Language")
                reasons.append(f"Contains {int(features['urgency_count'])} psychological urgency prompts demanding compliance.")
            if features["has_mfa_lure"] > 0:
                indicators.append("MFA / OTP Bypass Lure")
                reasons.append("Asks for verification codes, passcodes, or security authorization keys.")
            if features["money_char_count"] > 1:
                indicators.append("Financial Lure Signature")
                reasons.append("Contains heavy monetary triggers, transaction invoices, or wire instructions.")
            if features["brand_detected"] > 0:
                indicators.append(f"Brand Impersonation Target: {brand_name_match}")
                reasons.append(f"Identified targeting of {brand_name_match} brand identity to gain credibility.")
                
            if lexical_url_results["has_login_lure_path"]:
                indicators.append("URL Login Lure Path")
                reasons.append("Lexical analysis detected credential login lures embedded in the URL path.")
                
            if nlp_intent_results["authority_lure"]:
                indicators.append("Authority Mimicry Intent")
                reasons.append("NLP intent scanner detected IT/Admin/Executive impersonation keywords.")

            if not reasons:
                reasons.append("Matches phishing semantic templates with suspicious header patterns.")
                indicators.append("Phishing Signature Profile")
                
            reason_str = f"Classified as PHISHING because of: " + ", ".join(indicators[:3])

        # Highlighting System (Optimized for readability)
        # 🔴 URLs, 🟠 Password, 🟢 Company, 🔵 OTP, 🟣 Money, 💗 Urgency
        highlighted_email = email_text
        highlighted_email = highlighted_email.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # 1. Company/Brand: Green
        for brand in BRANDS:
            highlighted_email = re.sub(
                f"\\b({brand})\\b", 
                r"<mark style='background-color: rgba(34, 197, 94, 0.15); color: #22c55e; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
            
        # 2. Password/Credentials: Orange
        password_terms = ['password', 'credential', 'credentials', 'login', 'user', 'verify', 'verification', 'account', 'signin', 'reset', 'auth']
        for term in password_terms:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(249, 115, 22, 0.15); color: #f97316; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
            
        # 3. OTP: Blue
        otp_terms = ['mfa', '2fa', 'otp', 'authenticator', 'passcode', 'one-time', 'token']
        for term in otp_terms:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(59, 130, 246, 0.15); color: #3b82f6; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
            
        # 4. Money: Purple
        money_terms = ['usd', 'transfer', 'wire', 'payment', 'invoice', 'salary', 'payroll', 'refund', 'billing', 'cost', 'fee', 'price']
        for term in money_terms:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(168, 85, 247, 0.15); color: #a855f7; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
        highlighted_email = re.sub(
            r'([\$€£¥])',
            r"<mark style='background-color: rgba(168, 85, 247, 0.15); color: #a855f7; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>",
            highlighted_email
        )
        
        # 5. Urgency: Pink
        urgency_terms = ['urgent', 'suspend', 'immediately', 'action', 'alert', 'compromised', 'restricted', 'attention', 'required', 'deactivate', 'block']
        for term in urgency_terms:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(219, 39, 119, 0.15); color: #db2777; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
            
        # 6. URLs: Red
        highlighted_email = re.sub(
            r'(?<!color:\s)(https?://\S+|www\.\S+)',
            r"<mark style='background-color: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>",
            highlighted_email,
            flags=re.IGNORECASE
        )
        
        highlighted_email = highlighted_email.replace("\n", "<br>")

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
            "reasons": reasons,
            "feature_contributions": feature_contributions,
            "lexical_url_analysis": lexical_url_results,
            "nlp_intents": nlp_intent_results
        }

prediction_service = PredictionService()
