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
    url_pattern = re.compile(r'https?://\S+|www\.\S+|<a\s+href=')
    has_url = 1 if url_pattern.search(raw_email) else 0
    
    urgency_keywords = ['urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 'restricted', 'security']
    urgency_count = sum(1 for word in urgency_keywords if word in raw_email.lower())
    email_length = len(raw_email)
    exclamation_count = raw_email.count('!')
    money_char_count = raw_email.count('$')
    
    # 3. Create metadata frame and scale
    meta_df = pd.DataFrame([{
        'has_url': has_url,
        'urgency_count': urgency_count,
        'email_length': email_length,
        'exclamation_count': exclamation_count,
        'money_char_count': money_char_count
    }])
    
    # Scale non-binary metadata columns using loaded scaler
    scale_cols = ['urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
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

# Define test samples
test_cases = [
    {
        "desc": "Suspicious Phishing Email (Urgency lure & link)",
        "text": "URGENT SECURITY ALERT! Your account has been compromised by an unauthorized login attempt from IP 192.168.1.100. Please click on http://update-secure-banking.net immediately to verify your profile details and restore access. Failure to comply in 12 hours will lead to account suspension."
    },
    {
        "desc": "Legitimate Corporate Sync Email",
        "text": "Hi team, quick reminder that our progress review meeting is scheduled for tomorrow at 2:00 PM in Conference Room B. We'll go over the Q3 planning slides and milestones. See you all there, John."
    }
]

print("=== Running Phishing Detection Predictor Tests ===\n")
for idx, case in enumerate(test_cases, start=1):
    label, prob = predict_email(case["text"])
    status = "PHISHING" if label == 1 else "SAFE"
    confidence_str = f" (Confidence: {prob*100:.2f}%)" if prob is not None else ""
    print(f"Test Case {idx}: {case['desc']}")
    print(f"Prediction: {status}{confidence_str}")
    print(f"Email Content: '{case['text'][:120]}...'")
    print("-" * 60)
