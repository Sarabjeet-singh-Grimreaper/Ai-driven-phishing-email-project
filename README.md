# AI-Driven Phishing Email Detection Using NLP

An end-to-end, production-ready machine learning framework designed for B.Tech portfolio verification. It implements a **hybrid analysis approach** combining semantic Natural Language Processing (NLP) features with engineered structural heuristics to identify and classify phishing email threats.

---

## 📁 Project Structure

```text
├── Phishing_Email.csv          # Real-world training dataset (~18.6k samples)
├── train_pipeline.py           # Preprocessing, feature extraction, grid search, and training script
├── test_predict.py             # Command-line prediction and inference testing utility
├── app.py                      # Interactive Streamlit frontend dashboard
├── project_description_report.md# Academic report detailing guidelines, methodology, and lifecycle
├── confusion_matrix.png        # Best classifier's performance validation chart
├── roc_curve_comparison.png    # ROC curves comparing performance metrics across all models
├── best_phishing_model.joblib  # Serialized Multi-Layer Perceptron (MLP) Neural Network checkpoint
├── tfidf_vectorizer.joblib     # Serialized TF-IDF text feature extractor
└── metadata_scaler.joblib      # Serialized MinMaxScaler metadata scaler
```

---

## 🚀 Installation & Setup

### 1. Prerequisite Installations
Ensure Python 3.8+ is installed on your system. Install the required libraries via pip:
```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib streamlit
```

### 2. running the Training Pipeline
To retrain the models, run grid search optimization, and re-plot visual performance metrics:
```bash
python train_pipeline.py
```
*Note: This script will scale structural inputs using `MinMaxScaler`, apply a stratified 5,000-sample split, tune Random Forest parameters, train four models, and save the best performing configuration to disk.*

### 3. Running Command-Line Tests
To run quick prediction tests on sample email text inputs using the serialized MLP Neural Network:
```bash
python test_predict.py
```

### 4. Launching the Streamlit Web Application
To run the interactive portal locally:
```bash
python -m streamlit run app.py
```
Once launched, navigate to `http://localhost:8501` to test the visual scanner interface and review performance benchmarks.

---

## 🧠 Technical Highlights

### Preprocessing & Engineering
*   **Text Preprocessing:** Regular-expression based HTML tag stripping, non-alphanumeric punctuation removal, tokenization, and stopword filtering (utilizing a self-contained stopwords corpus to prevent environment-specific path issues).
*   **Linguistic Features:** High-frequency vectorization using Scikit-Learn's `TfidfVectorizer` (configured to isolate the top 3,000 features).
*   **Structural Heuristics:** Unified feature concatenation including:
    *   `has_url`: Scans for embedded hyperlinks and redirection wrappers.
    *   `urgency_count`: Registers density of threat alerts (e.g., *urgent, suspend, verify*).
    *   `email_length`: Tracks total character count.
    *   `exclamation_count` & `money_char_count`: Detects aggressive visual indicators (`!`) and financial lures (`$`).
*   **Feature Scaling:** Applied `MinMaxScaler` globally to preserve non-negative boundaries required by Naive Bayes classifiers.

---

## 📈 Performance Summary

Training metrics evaluated across **5,000 stratified samples** from the *Phishing_Email.csv* corpus:

| Model | Accuracy | Phishing Precision | Phishing Recall | F1-Score |
| :--- | :--- | :--- | :--- | :--- |
| **Neural Network (MLP)** | **95.00%** | **92.96%** | **94.39%** | **93.67%** |
| **Logistic Regression** | 94.80% | 91.06% | 96.17% | 93.55% |
| **Random Forest (Tuned)** | 93.30% | 89.93% | 93.37% | 91.61% |
| **Naive Bayes** | 93.00% | 90.66% | 91.58% | 91.12% |

*The Confusion Matrix (`confusion_matrix.png`) and the Receiver Operating Characteristic curves (`roc_curve_comparison.png`) are saved directly inside the workspace directory for verification.*
