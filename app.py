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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Minimalist, modern, and high-end security interface)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        background-color: #0B0F17;
        color: #F8FAFC;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Clean up default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Header styling */
    .header-container {
        text-align: center;
        padding: 2.5rem 0 1.5rem 0;
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* Tab styling */
    div[data-testid="stTabBar"] {
        background-color: #111827;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #1F2937;
        margin-bottom: 2rem;
    }
    button[data-baseweb="tab"] {
        color: #94A3B8 !important;
        border-bottom: none !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1F2937 !important;
        color: #38BDF8 !important;
    }

    /* Textarea styling */
    div[data-testid="stTextArea"] textarea {
        background-color: #111827 !important;
        color: #F8FAFC !important;
        border: 1px solid #1F2937 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #38BDF8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15) !important;
    }

    /* Button styling */
    div[data-testid="stButton"] button {
        background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15) !important;
    }
    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.25) !important;
        color: #ffffff !important;
    }

    /* Card Layouts */
    .result-card {
        background: #111827;
        border-radius: 16px;
        border: 1px solid #1F2937;
        padding: 24px;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .threat-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1.25rem;
    }
    .threat-badge.malicious {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    .threat-badge.clean {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    /* Metrics override */
    div[data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 12px !important;
        padding: 14px 10px !important;
        text-align: center !important;
    }
    div[data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
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

# Header Section
st.markdown("""
<div class="header-container">
    <div class="header-title">🛡️ AI Phishing Detector</div>
    <div class="header-subtitle">A minimal, intelligence-powered scanner for detecting email threats</div>
</div>
""", unsafe_allow_html=True)

# Clean Navigation Tabs
tab1, tab2 = st.tabs(["🛡️ Threat Predictor", "📊 Model Benchmarks"])

if not assets_loaded:
    st.error("⚠️ Persistent model assets not found! Please run the training pipeline `train_pipeline.py` first to generate models.")
else:
    with tab1:
        st.write("")
        email_input = st.text_area(
            "Analyze Email Content:",
            placeholder="Paste raw email body here...",
            height=200,
            label_visibility="collapsed"
        )
        
        col_btn, _ = st.columns([1, 1])
        with col_btn:
            scan_clicked = st.button("Scan Message")
            
        if scan_clicked:
            if not email_input.strip():
                st.warning("⚠️ Action Required: Please paste an email body to analyze.")
            else:
                with st.spinner("Analyzing linguistic structures..."):
                    # 1. Preprocessing and feature engineering executions
                    cleaned_text = preprocess_text(email_input)
                    
                    # Enhanced Heuristics mapping realistic phishing email features
                    url_pattern = re.compile(
                        r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+|<a\s+href=|href\s*=\s*[\'"][^\'"]*[\'"]|bit\.ly|tinyurl\.com|t\.co|ow\.ly|is\.gd|buff\.ly|rebrand\.ly',
                        re.IGNORECASE
                    )
                    url_count = len(url_pattern.findall(email_input))
                    
                    tld_pattern = re.compile(r'\.(zip|mov|ru|xyz|top|support|info|cc|tk|gq|cf|ml)\b', re.IGNORECASE)
                    has_suspicious_tld = 1 if tld_pattern.search(email_input) else 0

                    mfa_keywords = ['mfa', '2fa', 'otp', 'authenticator', 'verification code', 'one-time', 'passcode']
                    has_mfa_lure = 1 if any(word in email_input.lower() for word in mfa_keywords) else 0

                    urgency_keywords = [
                        'urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 
                        'restricted', 'security', 'update', 'password', 'confirm', 'attention', 'required', 'login',
                        'unusual', 'activity', 'invoice', 'overdue', 'billing', 'delivery', 'fedex', 'ups', 'paypal', 
                        'crypto', 'wallet', 'authorize', 'deactivate', 'block'
                    ]
                    urgency_count = sum(1 for word in urgency_keywords if word in email_input.lower())
                    email_length = len(email_input)
                    exclamation_count = email_input.count('!')
                    money_char_count = email_input.count('$') + email_input.count('€') + email_input.count('£') + email_input.lower().count('usd') + email_input.lower().count('transfer')
                    
                    # 2. Scale and Predict
                    meta_df = pd.DataFrame([{
                        'url_count': url_count,
                        'has_suspicious_tld': has_suspicious_tld,
                        'has_mfa_lure': has_mfa_lure,
                        'urgency_count': urgency_count,
                        'email_length': email_length,
                        'exclamation_count': exclamation_count,
                        'money_char_count': money_char_count
                    }])
                    scale_cols = ['url_count', 'urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
                    meta_df[scale_cols] = scaler.transform(meta_df[scale_cols])
                    
                    tfidf_feat = vectorizer.transform([cleaned_text]).toarray()
                    tfidf_df = pd.DataFrame(tfidf_feat, columns=vectorizer.get_feature_names_out())
                    X_pred = pd.concat([tfidf_df, meta_df], axis=1)
                    
                    prediction = model.predict(X_pred)[0]
                    prob = model.predict_proba(X_pred)[0][1] if hasattr(model, "predict_proba") else 0.5

                # 3. Clean Visual Card Layout Output
                if prediction == 1:
                    st.markdown(f"""
                    <div class="result-card" style="border-left: 4px solid #EF4444;">
                        <span class="threat-badge malicious">🚨 MALICIOUS THREAT DETECTED</span>
                        <h3 style="margin: 0; color: #F87171; font-size: 1.35rem; font-weight: 700;">Linguistic Threat level flagged at {prob*100:.1f}%</h3>
                        <p style="color: #94A3B8; margin-top: 10px; margin-bottom: 0; font-size: 0.95rem; line-height: 1.5;">This email contains high-risk phrasing patterns, urgency signals, or structural anomalies consistent with targeted phishing behavior.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card" style="border-left: 4px solid #10B981;">
                        <span class="threat-badge clean">✅ VERIFIED CLEAN</span>
                        <h3 style="margin: 0; color: #34D399; font-size: 1.35rem; font-weight: 700;">Legitimate safe pattern confirmed ({100 - (prob*100):.1f}% confidence score)</h3>
                        <p style="color: #94A3B8; margin-top: 10px; margin-bottom: 0; font-size: 0.95rem; line-height: 1.5;">No high-risk structures or phishing language matches detected. Standard security practices still advised.</p>
                    </div>
                    """, unsafe_allow_html=True)

                # 4. Highlight Explanatory Triggers (UX Feature)
                st.markdown("### 🗺️ Visual Explanatory Blueprint")
                st.write("Highlighted terms below indicate urgency triggers, call-to-actions, or security keywords detected:")
                
                highlighted_text = email_input
                # Escape html characters to avoid rendering raw HTML injected by the user but let us wrap the marked highlights
                highlighted_text = highlighted_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                # Replace marked keywords safely using HTML mark tag (excluding mark tag brackets itself)
                for word in urgency_keywords + mfa_keywords:
                    pattern = re.compile(rf"\b({word})\b", re.IGNORECASE)
                    highlighted_text = pattern.sub(
                        r"<mark style='background-color: rgba(245, 158, 11, 0.2); color: #F59E0B; padding: 2px 6px; border-radius: 4px; font-weight: 600;'>\1</mark>",
                        highlighted_text
                    )
                
                # Format line breaks for markdown rendering in the custom container
                highlighted_text_html = highlighted_text.replace("\n", "<br>")
                
                st.markdown(f"<div style='background-color: #111827; padding: 20px; border-radius: 12px; border: 1px solid #1F2937; color: #F8FAFC; font-family: monospace; font-size: 14px; line-height: 1.7;'>{highlighted_text_html}</div>", unsafe_allow_html=True)
                st.write("")

                # 5. High-Impact Metrics Grid
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("Linguistic Threat Level", f"{prob*100:.1f}%")
                m_col2.metric("Urgency Triggers", f"{urgency_count} matches")
                m_col3.metric("Financial Lures", "Yes" if money_char_count > 0 else "None")
                m_col4.metric("Link Count / Threat TLDs", f"{url_count} / {'Yes' if has_suspicious_tld else 'No'}")

    with tab2:
        st.write("")
        st.markdown("### 📊 Model Performance & Validation Benchmarks")
        st.write("Below are the comparative evaluation charts generated during training.")
        st.write("")
        
        bench_col1, bench_col2 = st.columns(2)
        
        with bench_col1:
            st.markdown("#### Confusion Matrix")
            if os.path.exists("confusion_matrix.png"):
                st.image("confusion_matrix.png", use_container_width=True)
            else:
                st.info("Confusion matrix graph not found in workspace.")
                
        with bench_col2:
            st.markdown("#### ROC-AUC Curve Performance")
            if os.path.exists("roc_curve_comparison.png"):
                st.image("roc_curve_comparison.png", use_container_width=True)
            else:
                st.info("ROC comparison graph not found in workspace.")

