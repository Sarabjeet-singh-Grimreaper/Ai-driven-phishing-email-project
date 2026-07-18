"""
Phishing Email Predictor - Test Utility
---------------------------------------
This script loads the trained model, vectorizer, and metadata scaler from the disk
and runs predictions on new email text samples to test the overall system.
"""

import os
import re
import pandas as pd
import numpy as np
import joblib

# Load persistent assets
model_path = "best_phishing_model.joblib"
vectorizer_path = "tfidf_vectorizer.joblib"
scaler_path = "metadata_scaler.joblib"

if not (os.path.exists(model_path) and os.path.exists(vectorizer_path) and os.path.exists(scaler_path)):
    raise FileNotFoundError("Missing saved model assets! Please run 'train_pipeline.py' first to serialize models.")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)
scaler = joblib.load(scaler_path)

STOPWORDS = set([
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
])

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word not in STOPWORDS]
    return " ".join(filtered_tokens)

def predict_email(raw_email):
    # 1. Preprocess raw text
    cleaned_text = preprocess_text(raw_email)
    
    # 2. Extract structural features
    url_pattern = re.compile(
        r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+|<a\s+href=|href\s*=\s*[\'"][^\'"]*[\'"]|bit\.ly|tinyurl\.com|t\.co|ow\.ly|is\.gd|buff\.ly|rebrand\.ly',
        re.IGNORECASE
    )
    url_count = len(url_pattern.findall(raw_email))
    
    tld_pattern = re.compile(r'\.(zip|mov|ru|xyz|top|support|info|cc|tk|gq|cf|ml)\b', re.IGNORECASE)
    has_suspicious_tld = 1 if tld_pattern.search(raw_email) else 0

    mfa_keywords = ['mfa', '2fa', 'otp', 'authenticator', 'verification code', 'one-time', 'passcode']
    has_mfa_lure = 1 if any(word in raw_email.lower() for word in mfa_keywords) else 0

    urgency_keywords = [
        'urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 
        'restricted', 'security', 'update', 'password', 'confirm', 'attention', 'required', 'login',
        'unusual', 'activity', 'invoice', 'overdue', 'billing', 'delivery', 'fedex', 'ups', 'paypal', 
        'crypto', 'wallet', 'authorize', 'deactivate', 'block'
    ]
    urgency_count = sum(1 for word in urgency_keywords if word in raw_email.lower())
    email_length = len(raw_email)
    exclamation_count = raw_email.count('!')
    money_char_count = raw_email.count('$') + raw_email.count('€') + raw_email.count('£') + raw_email.lower().count('usd') + raw_email.lower().count('transfer')
    
    # 3. Create metadata frame and scale
    meta_df = pd.DataFrame([{
        'url_count': url_count,
        'has_suspicious_tld': has_suspicious_tld,
        'has_mfa_lure': has_mfa_lure,
        'urgency_count': urgency_count,
        'email_length': email_length,
        'exclamation_count': exclamation_count,
        'money_char_count': money_char_count
    }])
    
    # Scale non-binary metadata columns using loaded scaler
    scale_cols = ['url_count', 'urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
    meta_df[scale_cols] = scaler.transform(meta_df[scale_cols])
    
    # 4. Vectorize text features
    tfidf_feat = vectorizer.transform([cleaned_text]).toarray()
    tfidf_df = pd.DataFrame(tfidf_feat, columns=vectorizer.get_feature_names_out())
    
    # 5. Combine features
    X_pred = pd.concat([tfidf_df, meta_df], axis=1)
    
    # 6. Model Inference
    pred_label = model.predict(X_pred)[0]
    pred_prob = model.predict_proba(X_pred)[0][1] if hasattr(model, "predict_proba") else None
    
    return pred_label, pred_prob

# Define test samples with modern cyber threats
test_cases = [
    {
        "desc": "Simulated Urgent Security MFA Bypass Attack",
        "text": "Microsoft Security Alert: Unusual login activity has been detected on your Office365 account from a foreign IP address. To prevent permanent deactivation, you must verify your profile details immediately. Click here to confirm your 2FA Authentication Code: http://verification-mfa-security.support/auth-login"
    },
    {
        "desc": "Simulated Urgent Invoice Billing Scam",
        "text": "Dear customer, your payment of $1,450.00 for the outstanding invoice #94022 is past due. To avoid late service interruption fees, verify details and settle your balance immediately by visiting our secure transfer portal: http://bit.ly/payment-invoice-process"
    },
    {
        "desc": "Legitimate Personal Check-in",
        "text": "Hey there! Long time no see. Let me know if you are free to grab lunch sometime next week. I wanted to catch up and show you the new project I've been working on. Talk soon."
    }
]

print("=== Running Phishing Detection Predictor Tests ===\n")
for idx, case in enumerate(test_cases, start=1):
    label, prob = predict_email(case["text"])
    status = "PHISHING DETECTED" if label == 1 else "SAFE/LEGITIMATE"
    confidence_str = f" (Threat confidence: {prob*100:.2f}%)" if prob is not None else ""
    print(f"Test Case {idx}: {case['desc']}")
    print(f"Prediction: {status}{confidence_str}")
    print(f"Email Content: '{case['text']}'")
    print("-" * 60)
