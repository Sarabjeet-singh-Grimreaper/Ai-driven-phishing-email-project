import os
import re
import joblib
import pandas as pd
import numpy as np

# Resolve model path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "best_phishing_model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "tfidf_vectorizer.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "metadata_scaler.joblib")

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", 
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", 
    "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", 
    "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", 
    "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", 
    "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", 
    "with", "about", "against", "between", "into", "through", "during", "before", "after", 
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", 
    "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", 
    "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", 
    "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", 
    "should", "now"
}

class PredictionService:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.load_models()

    def load_models(self):
        try:
            self.model = joblib.load(MODEL_PATH)
            self.vectorizer = joblib.load(VECTORIZER_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            print("ML models loaded successfully.")
        except Exception as e:
            print(f"Error loading ML models: {e}")

    def preprocess_payload(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        tokens = text.split()
        return " ".join([word for word in tokens if word not in STOPWORDS])

    def parse_heuristics(self, email_text: str):
        # Heuristics Calculations
        url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+|<a\s+href=|href\s*=\s*[\'"][^\'"]*[\'"]|bit\.ly|tinyurl\.com|t\.co|ow\.ly|is\.gd|buff\.ly|rebrand\.ly',
            re.IGNORECASE
        )
        url_count = len(url_pattern.findall(email_text))
        
        tld_pattern = re.compile(r'\.(zip|mov|ru|xyz|top|support|info|cc|tk|gq|cf|ml)\b', re.IGNORECASE)
        has_suspicious_tld = 1 if tld_pattern.search(email_text) else 0

        mfa_keywords = ['mfa', '2fa', 'otp', 'authenticator', 'verification code', 'one-time', 'passcode']
        has_mfa_lure = 1 if any(word in email_text.lower() for word in mfa_keywords) else 0

        urgency_keywords = [
            'urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 
            'restricted', 'security', 'update', 'password', 'confirm', 'attention', 'required', 'login',
            'unusual', 'activity', 'invoice', 'overdue', 'billing', 'delivery', 'fedex', 'ups', 'paypal', 
            'crypto', 'wallet', 'authorize', 'deactivate', 'block'
        ]
        urgency_count = sum(1 for word in urgency_keywords if word in email_text.lower())
        email_length = len(email_text)
        exclamation_count = email_text.count('!')
        money_char_count = email_text.count('$') + email_text.count('€') + email_text.count('£') + email_text.lower().count('usd') + email_text.lower().count('transfer')
        
        return {
            "url_count": url_count,
            "has_suspicious_tld": has_suspicious_tld,
            "has_mfa_lure": has_mfa_lure,
            "urgency_count": urgency_count,
            "email_length": email_length,
            "exclamation_count": exclamation_count,
            "money_char_count": money_char_count
        }

    def predict(self, email_text: str):
        if not self.model or not self.vectorizer or not self.scaler:
            raise RuntimeError("Model services are not initialized.")

        cleaned_body = self.preprocess_payload(email_text)
        features = self.parse_heuristics(email_text)
        
        meta_df = pd.DataFrame([{
            'url_count': features['url_count'],
            'has_suspicious_tld': features['has_suspicious_tld'],
            'has_mfa_lure': features['has_mfa_lure'],
            'urgency_count': features['urgency_count'], 
            'email_length': features['email_length'],
            'exclamation_count': features['exclamation_count'], 
            'money_char_count': features['money_char_count']
        }])
        
        scale_cols = ['url_count', 'urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
        meta_df[scale_cols] = self.scaler.transform(meta_df[scale_cols])
        
        tfidf_feat = self.vectorizer.transform([cleaned_body]).toarray()
        tfidf_df = pd.DataFrame(tfidf_feat, columns=self.vectorizer.get_feature_names_out())
        X_final = pd.concat([tfidf_df, meta_df], axis=1)
        
        prediction = int(self.model.predict(X_final)[0])
        confidence = float(self.model.predict_proba(X_final)[0][1]) if hasattr(self.model, "predict_proba") else 0.5
        
        # Risk Score Calculation (0 to 100 scale)
        if prediction == 0:
            risk_score = max(5, int((1 - confidence) * 30))
        else:
            risk_score = max(55, int(confidence * 100))
            
        severity = "Low"
        if risk_score > 85:
            severity = "Critical"
        elif risk_score > 60:
            severity = "High"
        elif risk_score > 30:
            severity = "Medium"

        # Indicators
        indicators = []
        if features['url_count'] > 0:
            indicators.append("Suspicious URL")
        if features['urgency_count'] > 1:
            indicators.append("Urgency Language")
        if "password" in email_text.lower() or "login" in email_text.lower():
            indicators.append("Password Request")
        if features['has_suspicious_tld']:
            indicators.append("Suspicious TLD Extension")
        if features['has_mfa_lure']:
            indicators.append("MFA Bypass Attempt")
        if features['money_char_count'] > 0:
            indicators.append("Financial Lure")

        # Highlighted Email Source
        highlighted_email = email_text
        highlighted_email = highlighted_email.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Urgency
        for term in ['urgent', 'suspend', 'verify', 'immediately', 'action', 'alert', 'compromised', 'restricted', 'password', 'login']:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(255, 0, 127, 0.2); color: #ff007f; padding: 2px 4px; border-radius: 4px;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
        # URLs
        highlighted_email = re.sub(
            r'(https?://\S+|www\.\S+)',
            r"<mark style='background-color: rgba(0, 242, 254, 0.2); color: #00f2fe; padding: 2px 4px; border-radius: 4px;'>\1</mark>",
            highlighted_email,
            flags=re.IGNORECASE
        )
        # Financial
        for term in ['\\$', '€', '£', 'usd', 'transfer', 'wire', 'payment', 'invoice']:
            highlighted_email = re.sub(
                f"\\b({term})\\b", 
                r"<mark style='background-color: rgba(249, 115, 22, 0.2); color: #f97316; padding: 2px 4px; border-radius: 4px;'>\1</mark>", 
                highlighted_email, 
                flags=re.IGNORECASE
            )
        
        highlighted_email = highlighted_email.replace("\n", "<br>")

        attack_type = "Credential Harvesting" if "Password Request" in indicators else "Brand Mimicry"
        if "Financial Lure" in indicators:
            attack_type = "Business Email Compromise (BEC)"

        return {
            "prediction": "Phishing" if prediction == 1 else "Safe",
            "confidence": round(confidence * 100, 2) if prediction == 1 else round((1 - confidence) * 100, 2),
            "risk_score": risk_score,
            "attack_type": attack_type if prediction == 1 else "Legitimate Profile",
            "severity": severity,
            "indicators": indicators if prediction == 1 else ["Clean Email Body Signature"],
            "highlighted_email": highlighted_email,
            "model": "Random Forest (Tuned)"
        }

prediction_service = PredictionService()
