"""
AI-Driven Phishing Email Detection Using NLP (Production Hybrid Pipeline)
------------------------------------------------------------------
This script performs a complete, end-to-end training and optimization cycle on the
real-world dataset: 'Phishing_Email.csv' using a hybrid model:
1. SentenceTransformer embeddings (all-MiniLM-L6-v2) for deep semantic text representation.
2. Custom tabular heuristics via features/extractor.py.
3. A calibrated HistGradientBoostingClassifier as the core prediction engine.
"""

import os
import re
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Scikit-learn & SentenceTransformers imports
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_curve, roc_auc_score
from sklearn.preprocessing import MinMaxScaler
from sentence_transformers import SentenceTransformer

# Load modular feature extractor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features.extractor import FeatureExtractor

# Set plotting styles
sns.set_theme(style="whitegrid")

# ==========================================
# 1. REAL DATASET INGESTION
# ==========================================
print("=== Phase 1: Real Dataset Ingestion ===")
dataset_path = "Phishing_Email.csv"

if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"Missing dataset! Please ensure '{dataset_path}' is in the current directory.")

# Read CSV
df = pd.read_csv(dataset_path, usecols=["Email Text", "Email Type"])
df = df.dropna(subset=["Email Text", "Email Type"])

# Map target string labels
df['label'] = df['Email Type'].apply(lambda x: 1 if "phishing" in str(x).lower() else 0)

# Stratified downsample for fast local CPU training with sentence-transformers
SAMPLE_SIZE = min(1500, len(df))
_, df = train_test_split(df, test_size=SAMPLE_SIZE, stratify=df['label'], random_state=42)
df = df.reset_index(drop=True)

print(f"Sampled {len(df)} records for training (Stratified distribution):")
print(df['Email Type'].value_counts())
print("\n")


# ==========================================
# 2. HYBRID FEATURE ENGINEERING
# ==========================================
print("=== Phase 2: Hybrid Feature Engineering ===")

# Tabular features extraction
extractor = FeatureExtractor()
print("Extracting rich cyber heuristics & tabular patterns...")
meta_features = []
for text in df['Email Text'].tolist():
    meta_features.append(extractor.extract_features(text))
meta_df = pd.DataFrame(meta_features)

# Text Vectorization using SentenceTransformer
print("Loading sentence-transformers/all-MiniLM-L6-v2 encoder...")
encoder = SentenceTransformer("all-MiniLM-L6-v2")
print("Computing transformer text embeddings...")
embeddings = encoder.encode(df['Email Text'].tolist(), show_progress_bar=True)
embed_df = pd.DataFrame(embeddings)

# Scale all numeric heuristic features using MinMaxScaler
scaler = MinMaxScaler()
meta_scaled = pd.DataFrame(scaler.fit_transform(meta_df), columns=meta_df.columns)

# Join semantic and heuristic datasets
X = pd.concat([embed_df, meta_scaled], axis=1)
# Ensure column names are all strings (or scikit-learn compatible)
X.columns = [str(col) for col in X.columns]
y = df['label'].reset_index(drop=True)

# Split dataset (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Aggregated Feature Dimensions: {X.shape}")
print("\n")


# ==========================================
# 3. GRADIENT BOOSTER TRAINING & CALIBRATION
# ==========================================
print("=== Phase 3: Calibrated Gradient Booster Training ===")

# Calibrate HistGradientBoostingClassifier
print("Training Calibrated HistGradientBoostingClassifier...")
base_hgb = HistGradientBoostingClassifier(random_state=42)
calibrated_hgb = CalibratedClassifierCV(estimator=base_hgb, method='sigmoid', cv=3)
calibrated_hgb.fit(X_train, y_train)


# ==========================================
# 4. EVALUATION & VISUALIZATION
# ==========================================
print("=== Phase 4: Comparative Evaluation ===")

preds = calibrated_hgb.predict(X_test)
report = classification_report(y_test, preds, output_dict=True, zero_division=0)

print(f"Calibrated HistGradientBooster Metrics:")
print(f"Accuracy: {report['accuracy']:.4f} | Precision: {report['1']['precision']:.4f} | Recall: {report['1']['recall']:.4f} | F1-Score (Phishing): {report['1']['f1-score']:.4f}")
print("-" * 75)

# Save evaluation plot components
cm = confusion_matrix(y_test, preds)
plt.figure(figsize=(6, 4.5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=["Safe Email", "Phishing Email"], 
            yticklabels=["Safe Email", "Phishing Email"])
plt.title("Confusion Matrix - Calibrated HistGradientBooster")
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.close()

# ROC Curve
plt.figure(figsize=(8, 6))
probs = calibrated_hgb.predict_proba(X_test)[:, 1]
fpr, tpr, _ = roc_curve(y_test, probs)
auc_score = roc_auc_score(y_test, probs)
plt.plot(fpr, tpr, lw=2, color='darkorange', label=f"Calibrated HGB (AUC = {auc_score:.3f})")
plt.plot([0, 1], [0, 1], color='gray', linestyle='--', lw=1.5, label="Random Guess")
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)')
plt.ylabel('True Positive Rate (TPR)')
plt.title('ROC Curve')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig("roc_curve_comparison.png", dpi=150)
plt.close()


# ==========================================
# 5. MODEL PERSISTENCE
# ==========================================
print("=== Phase 5: Model Persistence ===")

# Save models
joblib.dump(calibrated_hgb, "best_phishing_model.joblib")
# Save encoder reference (we can initialize/load dynamically)
joblib.dump("all-MiniLM-L6-v2", "tfidf_vectorizer.joblib") # Mock tfidf_vectorizer path to keep standard loader happy
joblib.dump(scaler, "metadata_scaler.joblib")

# Save versioned production model
model_version = "v2.0"
joblib.dump(calibrated_hgb, f"best_phishing_model_{model_version}.joblib")
joblib.dump(scaler, f"metadata_scaler_{model_version}.joblib")

print("Serialized artifacts saved to disk.")
print("Pipeline execution complete!")
