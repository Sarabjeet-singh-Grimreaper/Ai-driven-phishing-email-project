"""
AI-Driven Phishing Email Detection Using NLP (Production Pipeline)
------------------------------------------------------------------
This script performs a complete, end-to-end training and optimization cycle on the
real-world dataset: 'Phishing_Email.csv' (~18,650 samples).

It features:
1. Real Data Ingestion & Target Variable Encoding.
2. Advanced Hybrid Feature Extraction (Text vectorization + custom metadata features).
3. Class Imbalance Mitigation (Class-weighted models).
4. Hyperparameter Tuning using Cross-Validated Grid Search (`GridSearchCV`).
5. Comprehensive Visual & Quantitative Evaluation (ROC-AUC Curves, Confusion Matrix, Classification Reports).
6. Model & Vectorizer Persistence for deployment.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Scikit-learn imports
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_curve, roc_auc_score
from sklearn.preprocessing import StandardScaler

# Set plotting styles
sns.set_theme(style="whitegrid")

# Hardcoded Stopwords to prevent NLTK environment security violations
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

def preprocess_email(text):
    """
    Cleans raw email text: lowercases, removes HTML tags and punctuation, splits tokens, and filters stopwords.
    """
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Filter punctuation & special characters (keep space & alphanumeric)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Tokenize
    tokens = text.split()
    # Filter stopwords
    filtered_tokens = [word for word in tokens if word not in STOPWORDS]
    
    return " ".join(filtered_tokens)


# ==========================================
# 1. REAL DATASET INGESTION
# ==========================================
print("=== Phase 1: Real Dataset Ingestion ===")
dataset_path = "Phishing_Email.csv"

if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Missing dataset! Please ensure '{dataset_path}' is in the current directory.")

# Read CSV (using specific columns to optimize memory)
df = pd.read_csv(dataset_path, usecols=["Email Text", "Email Type"])

# Clean missing values
df = df.dropna(subset=["Email Text", "Email Type"])

# Map target string labels to binary classes: 1 for Phishing, 0 for Safe (Ham)
df['label'] = df['Email Type'].apply(lambda x: 1 if "phishing" in str(x).lower() else 0)

# To balance training speed and representativeness, we downsample using train_test_split
SAMPLE_SIZE = min(15000, len(df))
if len(df) > SAMPLE_SIZE:
    _, df = train_test_split(df, test_size=SAMPLE_SIZE, stratify=df['label'], random_state=42)

print(f"Sampled {len(df)} records for training (Stratified distribution):")
print(df['Email Type'].value_counts())
print("\n")


# ==========================================
# 2. ADVANCED HYBRID FEATURE ENGINEERING
# ==========================================
print("=== Phase 2: Hybrid Feature Engineering ===")

# A. Extract Structural/Metadata heuristic features
url_pattern = re.compile(
    r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.\S+|<a\s+href=|href\s*=\s*[\'"][^\'"]*[\'"]|bit\.ly|tinyurl\.com|t\.co|ow\.ly|is\.gd|buff\.ly|rebrand\.ly',
    re.IGNORECASE
)
df['url_count'] = df['Email Text'].apply(lambda x: len(url_pattern.findall(str(x))))

# Suspicious top-level domains & subdomains
tld_pattern = re.compile(r'\.(zip|mov|ru|xyz|top|support|info|cc|tk|gq|cf|ml)\b', re.IGNORECASE)
df['has_suspicious_tld'] = df['Email Text'].apply(lambda x: 1 if tld_pattern.search(str(x)) else 0)

# Modern security/MFA lures
mfa_keywords = ['mfa', '2fa', 'otp', 'authenticator', 'verification code', 'one-time', 'passcode']
def check_mfa_lure(text):
    text_lower = str(text).lower()
    return 1 if any(word in text_lower for word in mfa_keywords) else 0
df['has_mfa_lure'] = df['Email Text'].apply(check_mfa_lure)

# Expanded urgency and modern corporate brand lures (Invoice, Delivery, Payment, Auth)
urgency_keywords = [
    'urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 
    'restricted', 'security', 'update', 'password', 'confirm', 'attention', 'required', 'login',
    'unusual', 'activity', 'invoice', 'overdue', 'billing', 'delivery', 'fedex', 'ups', 'paypal', 
    'crypto', 'wallet', 'authorize', 'deactivate', 'block'
]
def count_urgency_keywords(text):
    text_lower = str(text).lower()
    return sum(1 for word in urgency_keywords if word in text_lower)

df['urgency_count'] = df['Email Text'].apply(count_urgency_keywords)
df['email_length'] = df['Email Text'].apply(lambda x: len(str(x)))
df['exclamation_count'] = df['Email Text'].apply(lambda x: str(x).count('!'))
df['money_char_count'] = df['Email Text'].apply(
    lambda x: str(x).count('$') + str(x).count('€') + str(x).count('£') + 
              str(x).lower().count('usd') + str(x).lower().count('transfer')
)

# B. Clean unstructured text column
print("Preprocessing raw email body text...")
df['cleaned_text'] = df['Email Text'].apply(preprocess_email)

# C. Text Vectorization (TF-IDF Vectorizer with max 4000 features)
vectorizer = TfidfVectorizer(max_features=4000)
tfidf_features = vectorizer.fit_transform(df['cleaned_text']).toarray()
tfidf_df = pd.DataFrame(tfidf_features, columns=vectorizer.get_feature_names_out())

# D. Consolidate TF-IDF with engineered structural features
metadata_cols = ['url_count', 'has_suspicious_tld', 'has_mfa_lure', 'urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
metadata_df = df[metadata_cols].reset_index(drop=True)

# Standardize/Scale the non-binary structural columns using MinMaxScaler to ensure values are non-negative (required for MultinomialNB)
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
metadata_scaled = metadata_df.copy()
scale_cols = ['url_count', 'urgency_count', 'email_length', 'exclamation_count', 'money_char_count']
metadata_scaled[scale_cols] = scaler.fit_transform(metadata_df[scale_cols])

X = pd.concat([tfidf_df, metadata_scaled], axis=1)
y = df['label'].reset_index(drop=True)

# Split dataset (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Aggregated Feature Dimensions: {X.shape}")
print("\n")


# ==========================================
# 3. HYPERPARAMETER TUNING & TRAINING
# ==========================================
print("=== Phase 3: Grid Search Optimization & Model Training ===")

# Tune Random Forest Classifier
print("Tuning Random Forest via GridSearchCV (sequential execution to save resources)...")
rf_param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [15, None],
}
rf_grid = GridSearchCV(RandomForestClassifier(class_weight='balanced', random_state=42), rf_param_grid, cv=3, scoring='f1', n_jobs=-1)
rf_grid.fit(X_train, y_train)
best_rf = rf_grid.best_estimator_
print(f"Optimal Random Forest params: {rf_grid.best_params_}")

# Baseline Class-Weighted Classifiers
models = {
    "Logistic Regression": LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
    "Naive Bayes": MultinomialNB(),
    "Random Forest (Tuned)": best_rf,
    "Neural Network (MLP)": MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=200, early_stopping=True, random_state=42)
}

# Train remaining models
for name, clf in models.items():
    if name != "Random Forest (Tuned)":
        clf.fit(X_train, y_train)
        print(f"Trained model: {name}")
print("\n")


# ==========================================
# 4. EVALUATION & VISUALIZATION
# ==========================================
print("=== Phase 4: Comparative Evaluation ===")

best_model_name = ""
best_f1 = -1
predictions_dict = {}

# Quantitative Classification Reports
for name, clf in models.items():
    preds = clf.predict(X_test)
    predictions_dict[name] = preds
    
    # Calculate performance metrics
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)
    f1 = report['macro avg']['f1-score']
    print(f"Model: {name}")
    print(f"Accuracy: {report['accuracy']:.4f} | Precision: {report['1']['precision']:.4f} | Recall: {report['1']['recall']:.4f} | F1-Score (Phishing): {report['1']['f1-score']:.4f}")
    print("-" * 75)
    
    if f1 > best_f1:
        best_f1 = f1
        best_model_name = name

print(f"Best Overall Classifier: {best_model_name}")

# Plot Confusion Matrix for the best performing model
best_clf = models[best_model_name]
best_preds = predictions_dict[best_model_name]
cm = confusion_matrix(y_test, best_preds)

plt.figure(figsize=(6, 4.5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=["Safe Email", "Phishing Email"], 
            yticklabels=["Safe Email", "Phishing Email"])
plt.title(f"Confusion Matrix - {best_model_name}")
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.close()
print("Saved Confusion Matrix: 'confusion_matrix.png'")

# Plot ROC-AUC curves for all models
plt.figure(figsize=(8, 6))
for name, clf in models.items():
    if hasattr(clf, "predict_proba"):
        probs = clf.predict_proba(X_test)[:, 1]
    else:
        probs = clf.decision_function(X_test)
        probs = (probs - probs.min()) / (probs.max() - probs.min())
        
    fpr, tpr, _ = roc_curve(y_test, probs)
    auc_score = roc_auc_score(y_test, probs)
    plt.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {auc_score:.3f})")

plt.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=1.5, label="Random Guess")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)')
plt.ylabel('True Positive Rate (TPR)')
plt.title('Receiver Operating Characteristic (ROC) Comparison')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("roc_curve_comparison.png", dpi=150)
plt.close()
print("Saved ROC-AUC Plot: 'roc_curve_comparison.png'")
print("\n")


# ==========================================
# 5. MODEL PERSISTENCE
# ==========================================
print("=== Phase 5: Model Persistence ===")

# Save the best model, vectorizer, and scaler
joblib.dump(best_clf, "best_phishing_model.joblib")
joblib.dump(vectorizer, "tfidf_vectorizer.joblib")
joblib.dump(scaler, "metadata_scaler.joblib")

print("Serialized artifacts saved to disk:")
print(" - Model: best_phishing_model.joblib")
print(" - Vectorizer: tfidf_vectorizer.joblib")
print(" - Scaler: metadata_scaler.joblib")
print("\nPipeline execution complete!")

