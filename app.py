"""
AI-Driven Phishing Email Detector - Streamlit App
------------------------------------------------
This dashboard loads the serialized ML components to offer an interactive email
threat classification workspace. It extracts linguistic & structural features,
evaluates risk levels, and displays explainable classification insights.
"""

import os
import re
import pandas as pd
import numpy as np
import streamlit as st
import joblib

# Page configuration
st.set_page_config(
    page_title="AI Phishing Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Rich dark/cybersecurity design)
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .reportview-container {
        background: #0e1117;
    }
    h1, h2, h3 {
        color: #00f2fe !important;
        font-family: 'Outfit', sans-serif;
    }
    .stTextArea textarea {
        background-color: #1b1e26;
        color: #ffffff;
        border: 1px solid #00f2fe;
    }
    .risk-high {
        background-color: rgba(255, 75, 75, 0.1);
        border: 2px solid #ff4b4b;
        padding: 20px;
        border-radius: 10px;
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-safe {
        background-color: rgba(9, 171, 59, 0.1);
        border: 2px solid #09ab3b;
        padding: 20px;
        border-radius: 10px;
        color: #09ab3b;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load persistent ML components
@st.cache_resource
def load_assets():
    model = joblib.load("best_phishing_model.joblib")
    vectorizer = joblib.load("tfidf_vectorizer.joblib")
    scaler = joblib.load("metadata_scaler.joblib")
    return model, vectorizer, scaler

try:
    model, vectorizer, scaler = load_assets()
    assets_loaded = True
except Exception as e:
    assets_loaded = False

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

# Sidebar layout
st.sidebar.title("🛡️ NLP Security Portal")
st.sidebar.markdown("---")
st.sidebar.info("This system uses Natural Language Processing (TF-IDF) combined with structural heuristics to identify malicious email patterns.")

# Navigation tabs
app_mode = st.sidebar.radio("Navigation", ["Threat Predictor", "Model Benchmarks"])

if not assets_loaded:
    st.error("⚠️ Persistent model assets not found! Please run the training pipeline `train_pipeline.py` first to generate models.")
else:
    if app_mode == "Threat Predictor":
        st.title("🛡️ AI-Driven Phishing Email Detector")
        st.write("Paste an email below to analyze linguistic indicators, structural urgency, and classification confidence.")

        email_input = st.text_area("Email Content:", placeholder="Paste raw email body here...", height=220)

        if st.button("Run Security Scan"):
            if not email_input.strip():
                st.warning("Please enter some text to scan.")
            else:
                # 1. Preprocessing
                cleaned_text = preprocess_text(email_input)
                
                # 2. Structural Heuristics
                url_pattern = re.compile(r'https?://\S+|www\.\S+|<a\s+href=')
                has_url = 1 if url_pattern.search(email_input) else 0
                
                urgency_keywords = ['urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 'restricted', 'security']
                urgency_count = sum(1 for word in urgency_keywords if word in email_input.lower())
                email_length = len(email_input)
                exclamation_count = email_input.count('!')
                money_char_count = email_input.count('$')
                
                # 3. Scale Features
                meta_df = pd.DataFrame([{
                    'has_url': has_url,
                    'urgency_count': urgency_count,
                    'email_length': email_length,
                    'exclamation_count': exclamation_count,
                    'money_char_count': money_char_count
                }])
                scale_cols = ['urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
                meta_df[scale_cols] = scaler.transform(meta_df[scale_cols])
                
                # 4. Vectorize text
                tfidf_feat = vectorizer.transform([cleaned_text]).toarray()
                tfidf_df = pd.DataFrame(tfidf_feat, columns=vectorizer.get_feature_names_out())
                
                # 5. Combined Input
                X_pred = pd.concat([tfidf_df, meta_df], axis=1)
                
                # 6. Predict
                prediction = model.predict(X_pred)[0]
                prob = model.predict_proba(X_pred)[0][1] if hasattr(model, "predict_proba") else None
                
                st.markdown("### 🔍 Scan Results")
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if prediction == 1:
                        st.markdown(f"""
                        <div class="risk-high">
                            <h3>🚨 PHISHING DETECTED</h3>
                            <p>This email has been flagged as suspicious. Confidence: {prob*100:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="risk-safe">
                            <h3>✅ LEGITIMATE EMAIL</h3>
                            <p>This email exhibits safe characteristics. Phishing Probability: {prob*100:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                with col2:
                    st.metric("Linguistic Risk Score", f"{prob*100:.1f}%")
                    st.metric("Character Count", f"{email_length}")
                
                st.markdown("### 📊 Engineered Threat Heuristics")
                h_col1, h_col2, h_col3, h_col4 = st.columns(4)
                h_col1.metric("Embedded Links (URLs)", "Yes" if has_url == 1 else "None")
                h_col2.metric("Urgency Word Matches", f"{urgency_count}")
                h_col3.metric("Exclamation Mark Count", f"{exclamation_count}")
                h_col4.metric("Financial Symbols ($)", f"{money_char_count}")

    elif app_mode == "Model Benchmarks":
        st.title("📊 Model Performance & Validation Benchmarks")
        st.write("Below are the comparative evaluation charts generated during model training and validation.")
        
        bench_col1, bench_col2 = st.columns(2)
        
        with bench_col1:
            st.subheader("Confusion Matrix")
            if os.path.exists("confusion_matrix.png"):
                st.image("confusion_matrix.png", use_container_width=True)
            else:
                st.info("Confusion matrix graph not found in workspace.")
                
        with bench_col2:
            st.subheader("ROC-AUC Curve Performance")
            if os.path.exists("roc_curve_comparison.png"):
                st.image("roc_curve_comparison.png", use_container_width=True)
            else:
                st.info("ROC comparison graph not found in workspace.")
