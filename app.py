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

# Custom Styling (Rich dark/cybersecurity design without deprecated classes)
st.markdown("""
<style>
    /* Base theme override */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
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
    /* Metrics custom container */
    div[data-testid="stMetric"] {
        background-color: #1b1e26;
        border: 1px solid #2d3139;
        border-radius: 8px;
        padding: 10px;
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

        # Main Threat Prediction block using new UX strategies
        if st.button("🚀 Run Comprehensive Security Scan"):
            if not email_input.strip():
                st.warning("⚠️ Action Required: Please paste an email body to analyze.")
            else:
                # Create a clean native loader experience
                with st.spinner("Analyzing linguistic structures and inspecting heuristic footprints..."):
                    # 1. Preprocessing and feature engineering executions
                    cleaned_text = preprocess_text(email_input)
                    
                    # Enhanced Heuristics mapping realistic phishing email features
                    url_pattern = re.compile(
                        r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+|<a\s+href=|href\s*=\s*[\'"][^\'"]*[\'"]|bit\.ly|tinyurl\.com|t\.co|ow\.ly|is\.gd|buff\.ly|rebrand\.ly',
                        re.IGNORECASE
                    )
                    has_url = 1 if url_pattern.search(email_input) else 0
                    
                    urgency_keywords = ['urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 'restricted', 'security', 'update', 'password', 'confirm', 'attention', 'required', 'login']
                    urgency_count = sum(1 for word in urgency_keywords if word in email_input.lower())
                    email_length = len(email_input)
                    exclamation_count = email_input.count('!')
                    money_char_count = email_input.count('$') + email_input.count('€') + email_input.count('£') + email_input.lower().count('usd') + email_input.lower().count('transfer')
                    
                    # 2. Scale and Predict
                    meta_df = pd.DataFrame([{
                        'has_url': has_url,
                        'urgency_count': urgency_count,
                        'email_length': email_length,
                        'exclamation_count': exclamation_count,
                        'money_char_count': money_char_count
                    }])
                    scale_cols = ['urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
                    meta_df[scale_cols] = scaler.transform(meta_df[scale_cols])
                    
                    tfidf_feat = vectorizer.transform([cleaned_text]).toarray()
                    tfidf_df = pd.DataFrame(tfidf_feat, columns=vectorizer.get_feature_names_out())
                    X_pred = pd.concat([tfidf_df, meta_df], axis=1)
                    
                    prediction = model.predict(X_pred)[0]
                    prob = model.predict_proba(X_pred)[0][1] if hasattr(model, "predict_proba") else 0.5

                # 3. Clean Visual Card Layout Output
                st.subheader("🔍 Threat Assessment Analysis")
                
                if prediction == 1:
                    st.error(f"🚨 **Malicious Activity Flagged:** Phishing Variant Detected with {prob*100:.1f}% certainty.")
                else:
                    st.success(f"✅ **Verified Clean:** Email exhibits legitimate safe behavior pattern ({100 - (prob*100):.1f}% confidence score).")
                    
                # 4. Highlight Explanatory Triggers (UX Feature)
                st.markdown("### 🗺️ Visual Explanatory Blueprint")
                st.write("This interactive blueprint highlights urgent terminology and calls to action dynamically detected inside your text:")
                
                highlighted_text = email_input
                # Escape html characters to avoid rendering raw HTML injected by the user but let us wrap the marked highlights
                highlighted_text = highlighted_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                # Replace marked keywords safely using HTML mark tag (excluding mark tag brackets itself)
                for word in urgency_keywords:
                    pattern = re.compile(rf"\b({word})\b", re.IGNORECASE)
                    highlighted_text = pattern.sub(
                        r"<mark style='background-color: rgba(255, 165, 0, 0.35); color: #ff9900; padding: 2px 4px; border-radius: 4px; font-weight: bold;'>\1</mark>",
                        highlighted_text
                    )
                
                # Format line breaks for markdown rendering in the custom container
                highlighted_text_html = highlighted_text.replace("\n", "<br>")
                
                st.markdown(f"<div style='background-color: #1b1e26; padding: 20px; border-radius: 8px; border-left: 5px solid #00f2fe; color: #ffffff; font-family: monospace; font-size: 14px; line-height: 1.6;'>{highlighted_text_html}</div>", unsafe_allow_html=True)
                
                # 5. High-Impact Metrics Grid
                st.markdown("---")
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Linguistic Threat Level", f"{prob*100:.1f}%")
                m_col2.metric("Urgency Triggers", f"{urgency_count} matches")
                m_col3.metric("Financial Lures Found", "Yes" if money_char_count > 0 else "None")
                m_col4.metric("Total Structural Density", f"{email_length} chars")

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

