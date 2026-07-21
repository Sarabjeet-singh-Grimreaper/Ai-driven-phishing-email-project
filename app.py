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

# 2. DESIGN OVERHAUL: "THE CATALYST" ACID-DARK SYSTEM
st.markdown("""
<style>
    /* Global Font and Core Background Override */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #090d16 !important; /* Deep slate-space */
        font-family: 'Inter', sans-serif !important;
        color: #f3f4f6 !important;
        letter-spacing: -0.02em !important;
    }
    
    /* Clean up default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header typography */
    .hero-title {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700;
        font-size: 2.6rem;
        letter-spacing: -0.04em;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 5px;
        text-transform: uppercase;
    }
    
    .hero-subtitle {
        color: #9ca3af;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 40px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Machined Silver Card System */
    .machined-card {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid #374151 !important;
        border-radius: 0px !important;
        padding: 24px;
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* Premium Input Container */
    div[data-testid="stForm"], .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid #374151 !important;
        border-radius: 0px !important;
        color: #f3f4f6 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease-in-out;
    }
    
    .stTextArea textarea:focus {
        border-color: #d4ff00 !important;
        box-shadow: 0 0 0 1px #d4ff00 !important;
    }

    /* Modern SaaS Interactive Primary Action Button (Catalyst mechanical layout) */
    .stButton button {
        background-color: #d4ff00 !important;
        color: #090d16 !important;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: 4px 4px 0px #000000 !important;
        transition: all 0.15s ease-in-out !important;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 6px 6px 0px #000000 !important;
        background-color: #ccff00 !important;
        color: #090d16 !important;
    }
    
    .stButton button:active {
        transform: translate(2px, 2px) !important;
        box-shadow: 2px 2px 0px #000000 !important;
    }

    /* Styled Status Cards with Deep Warning Aura */
    .threat-card-malicious {
        background: linear-gradient(180deg, rgba(239, 68, 68, 0.1) 0%, rgba(239, 68, 68, 0.02) 100%) !important;
        border: 1px solid #ef4444 !important;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
        padding: 24px;
        border-radius: 0px !important;
        margin-top: 20px;
    }
    
    .threat-card-safe {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%) !important;
        border: 1px solid #374151 !important;
        border-left: 4px solid #d4ff00 !important;
        padding: 24px;
        border-radius: 0px !important;
        margin-top: 20px;
    }

    /* Clean Code Workspace for Explanations */
    .code-workspace {
        background-color: #05070c;
        border: 1px solid #374151;
        border-radius: 0px;
        padding: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #e5e7eb;
    }

    /* Tab styling */
    div[data-testid="stTabBar"] {
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 0px;
        padding: 4px;
        border: 1px solid #374151;
        margin-bottom: 2rem;
    }
    button[data-baseweb="tab"] {
        color: #9ca3af !important;
        border-bottom: none !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        border-radius: 0px !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.05em !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #d4ff00 !important;
    }

    /* Metrics override */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid #374151 !important;
        border-radius: 0px !important;
        padding: 14px 10px !important;
        text-align: center !important;
    }
    div[data-testid="stMetricValue"] {
        color: #d4ff00 !important; /* Acid Yellow metrics values */
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #9ca3af !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 600 !important;
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
    text = re.sub(r'\s+', ' ', text)  # normalize whitespace
    tokens = text.split()
    return " ".join([word for word in tokens if word not in STOPWORDS])

def extract_text_from_image(uploaded_file):
    try:
        from PIL import Image
        import numpy as np
        
        # Read file as PIL Image
        img = Image.open(uploaded_file)
        # Convert to RGB to remove alpha channel transparency/grayscale mode issues
        img = img.convert("RGB")
        img_np = np.array(img)
        
        extracted_text = ""
        ocr_errors = []
        
        # 1. Try RapidOCR first
        try:
            from rapidocr_onnxruntime import RapidOCR
            engine = RapidOCR()
            result, elapse = engine(img_np)
            if result:
                texts = [line[1] for line in result]
                extracted_text = "\n".join(texts)
        except Exception as e_rapid:
            ocr_errors.append(f"RapidOCR error: {str(e_rapid)}")
            
        # 2. Try pytesseract as fallback if RapidOCR did not find text
        if not extracted_text.strip():
            try:
                import pytesseract
                # Attempt to extract text via pytesseract
                tess_text = pytesseract.image_to_string(img)
                if tess_text.strip():
                    extracted_text = tess_text
            except Exception as e_tess:
                ocr_errors.append(f"Pytesseract error: {str(e_tess)}")
                
        if extracted_text.strip():
            return extracted_text, None
        else:
            err_msg = "No text detected in the image. Please ensure the image contains clear, readable email text."
            if ocr_errors:
                err_msg += f" (Diagnostics: {'; '.join(ocr_errors)})"
            return "", err_msg
            
    except Exception as e:
        return "", f"Error reading image: {str(e)}"

# 4. FRONTEND HEADER ARCHITECTURE
st.markdown('<div class="hero-title">🛡️ AI Phishing Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">A minimal, intelligence-powered scanner for detecting email threats</div>', unsafe_allow_html=True)

if not assets_ready:
    st.error("🚨 Missing System Artifacts: Please run the training pipeline first (`train_pipeline.py`) to generate matching joblib configurations.")
else:
    # 5. USER WORKSPACE LAYOUT
    tabs = st.tabs(["✨ Threat Predictor", "📊 System Performance", "💡 Security Checklist"])
    
    with tabs[0]:
        st.markdown("<h4 style='color: #ffffff; font-size: 1.0rem; text-transform: uppercase; font-weight:600; letter-spacing: 0.05em; margin-bottom: 8px;'>📥 Choose Ingestion Method</h4>", unsafe_allow_html=True)
        input_method = st.radio(
            "Choose Ingestion Method",
            ["Type / Paste Text", "Upload Screenshot / Image"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        email_payload = ""
        
        if input_method == "Type / Paste Text":
            email_payload = st.text_area(
                "Email Payload Data Ingestion",
                placeholder="Paste raw, unstructured email body strings or network text capture records here...",
                height=200,
                label_visibility="collapsed"
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload Email Screenshot or Image", 
                type=["png", "jpg", "jpeg"], 
                label_visibility="collapsed"
            )
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Email Image", use_container_width=True)
                with st.spinner("Extracting text from image via OCR engine..."):
                    extracted_text, err = extract_text_from_image(uploaded_file)
                    if err:
                        st.error(err)
                        email_payload = ""
                    else:
                        email_payload = extracted_text
                        st.success("📝 Text successfully extracted from image!")
                        with st.expander("🔎 View Extracted Text Payload"):
                            st.text_area("Extracted Text", value=email_payload, height=150, disabled=True)
            else:
                st.info("💡 Upload a screenshot or image of an email to scan it.")
        
        scan_triggered = st.button("Analyze Ingested Payload")
        
        if scan_triggered:
            if not email_payload.strip():
                st.info("💡 Notification: Please paste text patterns or upload an image before initializing analysis filters.")
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
                        <h4 style="color: #ef4444; margin-top:0; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">🚨 MALICIOUS FOOTPRINT IDENTIFIED</h4>
                        <p style="color: #fca5a5; margin-bottom:0; font-size:0.95rem;">
                            Structural analytics confirm signature threat metrics. Neural index evaluates phishing variant likelihood at <strong style="color: #d4ff00;">{confidence*100:.2f}%</strong> confirmation certainty.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="threat-card-safe">
                        <h4 style="color: #d4ff00; margin-top:0; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">✅ LEGITIMATE PATTERN CONFIRMED</h4>
                        <p style="color: #f3f4f6; margin-bottom:0; font-size:0.95rem;">
                            Ingested sequence matches standard communication parameters. Legitimate pattern validation certainty is evaluated at <strong style="color: #d4ff00;">{(1-confidence)*100:.2f}%</strong>.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Interactive Semantic Highlighting Display (Explainable UX UI Feature)
                st.markdown("<br><h4 style='color: #ffffff; font-size: 1.1rem; text-transform: uppercase; font-weight:600; letter-spacing: 0.05em;'>🗺️ Highlighted Key Risk Anomaly Identifiers</h4>", unsafe_allow_html=True)
                highlighted_output = email_payload
                
                # Escape HTML characters first
                highlighted_output = highlighted_output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                for term in urgency_keywords + mfa_keywords:
                    highlighted_output = re.sub(
                        f"\\b({term})\\b", 
                        r"<mark style='background-color: rgba(212, 255, 0, 0.15); color: #d4ff00; padding: 2px 6px; border-radius: 0px; font-weight:600;'>\1</mark>", 
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
        st.markdown("<h4 style='color: #ffffff; font-size: 1.2rem; text-transform: uppercase; font-weight: 600;'>📈 System Validation Curves & Validation Matrices</h4>", unsafe_allow_html=True)
        st.write("Review localized cross-validation reports tracking historical validation tests across continuous evaluation loops:")
        st.write("")
        
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

    with tabs[2]:
        st.markdown("<h4 style='color: #ffffff; font-size: 1.2rem; text-transform: uppercase; font-weight: 600;'>🛡️ Beyond AI: The Human Firewall Checklist</h4>", unsafe_allow_html=True)
        st.write("No AI model is 100% foolproof against highly targeted attacks (like spear-phishing or zero-days). Use this checklist to verify indicators outside the raw text:")
        st.write("")
        
        st.checkbox("✉️ **Verify the Sender's Actual Domain**: Attackers use display name spoofing (e.g., displaying 'Netflix Security' but sending from `admin@netflix-security-update.xyz`). Check the address suffix carefully.")
        st.checkbox("🔗 **Inspect Hyperlinks (Hover, Don't Click)**: Hover over any links to check where they actually lead. Look for typos or character substitutions (e.g., `micros0ft.com` or `paypa1.com`).")
        st.checkbox("🔒 **Watch out for High-Risk Actions**: Be extremely skeptical of requests for credential entry, passwords, bank transfers, or MFA codes via email.")
        st.checkbox("📞 **Use Out-of-Band Verification**: If an email claims to be from a colleague or your bank requesting urgent changes, verify it independently by calling them or messaging them on a known channel.")
        
        st.info("💡 **Pro-Tip**: Safe emails never demand that you verify MFA/2FA codes via unencrypted email forms or click direct links to authorize high-security transactions.")
