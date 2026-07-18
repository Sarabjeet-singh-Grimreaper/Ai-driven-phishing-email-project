import os
import re
import pandas as pd
import numpy as np
import streamlit as st
import joblib

# 1. PAGE SETUP WITH MODERN SAAS CONFIGURATION
st.set_page_config(
    page_title="AI Phishing Portal",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. DESIGN OVERHAUL: ULTRA-DARK GLASSMORPHIC STYLING
st.markdown("""
<style>
    /* Global Font and Core Background Override */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #030712 !important; /* Deep space dark */
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f3f4f6 !important;
    }
    
    /* Sleek Modern Gradient for Titles */
    .hero-title {
        font-weight: 700;
        font-size: 2.8rem;
        letter-spacing: -0.05rem;
        background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 5px;
    }
    
    .hero-subtitle {
        color: #9ca3af;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 300;
    }

    /* Premium Input Container */
    div[data-testid="stForm"], .stTextArea textarea {
        background-color: #0b0f19 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        color: #f3f4f6 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 1px #6366f1, 0 0 20px rgba(99, 102, 241, 0.15) !important;
    }

    /* Modern SaaS Interactive Primary Action Button */
    .stButton button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        padding: 10px 24px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: -0.01rem !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
        background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%) !important;
    }

    /* Styled Status Cards */
    .threat-card-malicious {
        background: linear-gradient(180deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.02) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 4px solid #ef4444;
        padding: 24px;
        border-radius: 12px;
        margin-top: 20px;
    }
    
    .threat-card-safe {
        background: linear-gradient(180deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.02) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 4px solid #10b981;
        padding: 24px;
        border-radius: 12px;
        margin-top: 20px;
    }

    /* Clean Code Workspace for Explanations */
    .code-workspace {
        background-color: #070a13;
        border: 1px solid #111827;
        border-radius: 8px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #e5e7eb;
    }

    /* Tab styling */
    div[data-testid="stTabBar"] {
        background-color: #0b0f19;
        border-radius: 12px;
        padding: 4px;
        border: 1px solid #1f2937;
        margin-bottom: 2rem;
    }
    button[data-baseweb="tab"] {
        color: #9ca3af !important;
        border-bottom: none !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #6366f1 !important;
    }

    /* Metrics styling override */
    div[data-testid="stMetric"] {
        background-color: #0b0f19 !important;
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        padding: 14px 10px !important;
        text-align: center !important;
    }
    div[data-testid="stMetricValue"] {
        color: #f3f4f6 !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. BACKGROUND ML ENGINE INITIALIZATION
@st.cache_resource
def load_security_weights():
    try:
        model = joblib.load("best_phishing_model.joblib")
        vectorizer = joblib.load("tfidf_vectorizer.joblib")
        scaler = joblib.load("metadata_scaler.joblib")
        return model, vectorizer, scaler, True
    except:
        return None, None, None, False

model, vectorizer, scaler, assets_ready = load_security_weights()

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

def preprocess_payload(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    tokens = text.split()
    return " ".join([word for word in tokens if word not in STOPWORDS])

# 4. FRONTEND HEADER ARCHITECTURE
st.markdown('<div class="hero-title">🛡️ AI Phishing Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">A minimal, intelligence-powered scanner for detecting email threats</div>', unsafe_allow_html=True)

if not assets_ready:
    st.error("🚨 Missing System Artifacts: Please run the training pipeline first (`train_pipeline.py`) to generate matching joblib configurations.")
else:
    # 5. USER WORKSPACE LAYOUT
    tabs = st.tabs(["✨ Threat Predictor", "📊 System Performance"])
    
    with tabs[0]:
        email_payload = st.text_area(
            "Email Payload Data Ingestion",
            placeholder="Paste raw, unstructured email body strings or network text capture records here...",
            height=200,
            label_visibility="collapsed"
        )
        
        scan_triggered = st.button("Analyze Ingested Payload")
        
        if scan_triggered:
            if not email_payload.strip():
                st.info("💡 Notification: Paste text patterns inside the main ingestion workspace above before initializing analysis filters.")
            else:
                with st.spinner("Processing local text tokens and vector structures..."):
                    # Feature Mining & Vector Conversion Routine
                    cleaned_body = preprocess_payload(email_payload)
                    
                    url_pattern = re.compile(
                        r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+|<a\s+href=|href\s*=\s*[\'"][^\'"]*[\'"]|bit\.ly|tinyurl\.com|t\.co|ow\.ly|is\.gd|buff\.ly|rebrand\.ly',
                        re.IGNORECASE
                    )
                    url_count = len(url_pattern.findall(email_payload))
                    
                    tld_pattern = re.compile(r'\.(zip|mov|ru|xyz|top|support|info|cc|tk|gq|cf|ml)\b', re.IGNORECASE)
                    has_suspicious_tld = 1 if tld_pattern.search(email_payload) else 0

                    mfa_keywords = ['mfa', '2fa', 'otp', 'authenticator', 'verification code', 'one-time', 'passcode']
                    has_mfa_lure = 1 if any(word in email_payload.lower() for word in mfa_keywords) else 0

                    urgency_keywords = [
                        'urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 
                        'restricted', 'security', 'update', 'password', 'confirm', 'attention', 'required', 'login',
                        'unusual', 'activity', 'invoice', 'overdue', 'billing', 'delivery', 'fedex', 'ups', 'paypal', 
                        'crypto', 'wallet', 'authorize', 'deactivate', 'block'
                    ]
                    urgency_count = sum(1 for word in urgency_keywords if word in email_payload.lower())
                    email_length = len(email_payload)
                    exclamation_count = email_payload.count('!')
                    money_char_count = email_payload.count('$') + email_payload.count('€') + email_payload.count('£') + email_payload.lower().count('usd') + email_payload.lower().count('transfer')
                    
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
                    
                    tfidf_feat = vectorizer.transform([cleaned_body]).toarray()
                    tfidf_df = pd.DataFrame(tfidf_feat, columns=vectorizer.get_feature_names_out())
                    X_final = pd.concat([tfidf_df, meta_df], axis=1)
                    
                    prediction = model.predict(X_final)[0]
                    confidence = model.predict_proba(X_final)[0][1] if hasattr(model, "predict_proba") else 0.5
                
                # Dynamic Response Cards Rendering
                if prediction == 1:
                    st.markdown(f"""
                    <div class="threat-card-malicious">
                        <h4 style="color: #f87171; margin-top:0;">🚨 MALICIOUS Footprint Identified</h4>
                        <p style="color: #fca5a5; margin-bottom:0; font-size:0.95rem;">
                            Structural analytics confirm signature threat metrics. Neural index evaluates phishing variant likelihood at <strong>{confidence*100:.2f}%</strong> confirmation certainty.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="threat-card-safe">
                        <h4 style="color: #34d399; margin-top:0;">✅ LEGITIMATE Communication Structural Pattern</h4>
                        <p style="color: #6ee7b7; margin-bottom:0; font-size:0.95rem;">
                            Ingested sequence matches standard communication parameters. Phishing anomaly threat probability drops below <strong>{(1-confidence)*100:.2f}%</strong> validation variance thresholds.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Interactive Semantic Highlighting Display (Explainable UX UI Feature)
                st.markdown("<br><h4 style='color: #a5b4fc; font-size: 1.1rem;'>🗺️ Highlighted Key Risk Anomaly Identifiers</h4>", unsafe_allow_html=True)
                highlighted_output = email_payload
                
                # Escape HTML characters first
                highlighted_output = highlighted_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                for term in urgency_keywords + mfa_keywords:
                    highlighted_output = re.sub(
                        f"\\b({term})\\b", 
                        r"<mark style='background-color: rgba(245, 158, 11, 0.25); color: #fbbf24; padding: 2px 6px; border-radius: 4px; font-weight:500;'>\1</mark>", 
                        highlighted_output, 
                        flags=re.IGNORECASE
                    )
                # Convert newlines to breaks for HTML workspace
                highlighted_output = highlighted_output.replace("\n", "<br>")
                st.markdown(f'<div class="code-workspace">{highlighted_output}</div>', unsafe_allow_html=True)
                
                # Metrics Grid Architecture Injections
                st.markdown("<br>", unsafe_allow_html=True)
                g1, g2, g3, g4 = st.columns(4)
                g1.metric("Anomalous Risk Index", f"{confidence*100:.1f}%")
                g2.metric("Urgency Matches", f"{urgency_count}")
                g3.metric("Link Count / Threat TLDs", f"{url_count} / {'Yes' if has_suspicious_tld else 'No'}")
                g4.metric("Structural Length", f"{email_length} chars")

    with tabs[1]:
        st.markdown("<h4 style='color: #a5b4fc; font-size: 1.2rem;'>📈 System Validation Curves & Validation Matrices</h4>", unsafe_allow_html=True)
        st.write("Review localized cross-validation reports tracking historical validation tests across continuous evaluation loops:")
        
        c1, c2 = st.columns(2)
        with c1:
            if os.path.exists("confusion_matrix.png"):
                st.image("confusion_matrix.png", caption="Evaluation Loop Confusion Matrix Chart", use_container_width=True)
            else:
                st.info("System Notification: Confusion matrix image logs currently missing from active workspace paths.")
        with c2:
            if os.path.exists("roc_curve_comparison.png"):
                st.image("roc_curve_comparison.png", caption="Model ROC Curve Comparison Blueprint", use_container_width=True)
            else:
                st.info("System Notification: ROC performance log charts missing from operational directory layers.")
