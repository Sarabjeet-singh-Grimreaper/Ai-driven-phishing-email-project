import os
import re
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

STOPWORDS = {
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
}

BRANDS = ["microsoft", "amazon", "google", "paypal", "apple", "facebook", "netflix", "dhl", "fedex", "linkedin"]

SUSPICIOUS_TLDS = {"zip", "mov", "ru", "xyz", "top", "support", "info", "cc", "tk", "gq", "cf", "ml"}

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "ow.ly", "is.gd", "buff.ly", "rebrand.ly"}

MFA_LURES = {"mfa", "2fa", "otp", "authenticator", "verification code", "one-time", "passcode"}

URGENCY_KEYWORDS = {
    'urgent', 'suspend', 'verify', 'action', 'alert', 'immediately', 'compromised', 'claim', 
    'restricted', 'security', 'update', 'password', 'confirm', 'attention', 'required', 'login',
    'unusual', 'activity', 'invoice', 'overdue', 'billing', 'delivery', 'fedex', 'ups', 'paypal', 
    'crypto', 'wallet', 'authorize', 'deactivate', 'block'
}

IMPERATIVE_VERBS = {"click", "verify", "log", "update", "check", "confirm", "respond", "pay", "download", "open"}

def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    tokens = text.split()
    return " ".join([word for word in tokens if word not in STOPWORDS])

def calculate_entropy(s):
    if not s:
        return 0.0
    probabilities = [float(s.count(c)) / len(s) for c in dict.fromkeys(s)]
    entropy = - sum([p * np.log2(p) for p in probabilities])
    return entropy

def find_domain_similarity(domain, brands=BRANDS):
    domain = domain.lower()
    # Remove TLD
    parts = domain.split('.')
    if not parts:
        return 0.0
    name = parts[0]
    
    # Check simple character substitutions (mimicry)
    similarities = []
    for brand in brands:
        if name == brand:
            similarities.append(1.0)
            continue
        # Check levenshtein-like modifications
        # If lengths are close and overlap is high
        intersection = len(set(name) & set(brand))
        union = len(set(name) | set(brand))
        jaccard = intersection / union if union > 0 else 0.0
        
        # Levenshtein distance check (simple version)
        if len(name) > 0 and len(brand) > 0:
            # check common substitutions: 1 -> l, 0 -> o, rn -> m, etc.
            subbed = name.replace('1', 'l').replace('0', 'o').replace('rn', 'm').replace('vv', 'w').replace('I', 'l')
            if subbed == brand:
                similarities.append(0.95)
                continue
            
        similarities.append(jaccard * 0.8)
    return max(similarities) if similarities else 0.0

class EmailFeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        # Expects a list of strings
        features_list = []
        for text in X:
            if not isinstance(text, str):
                text = ""
                
            # Basic info
            length = len(text)
            cap_ratio = sum(1 for c in text if c.isupper()) / (length + 1)
            exclamations = text.count('!')
            money_chars = text.count('$') + text.count('€') + text.count('£') + text.lower().count('usd') + text.lower().count('transfer')
            
            # Email Headers Simulation / Parsing
            # In standard datasets, we scan text for typical headers if they exist, or simulate if they don't
            has_spf = 1 if re.search(r'Received-SPF:\s*pass|spf=pass', text, re.IGNORECASE) else 0
            has_dkim = 1 if re.search(r'dkim=pass|DKIM-Signature', text, re.IGNORECASE) else 0
            has_dmarc = 1 if re.search(r'dmarc=pass', text, re.IGNORECASE) else 0
            
            reply_to_match = re.search(r'Reply-To:\s*([^\s@]+@[^\s@>]+)', text, re.IGNORECASE)
            from_match = re.search(r'From:\s*(?:[^<]*<)?([^\s@]+@[^\s@>]+)', text, re.IGNORECASE)
            
            reply_to_mismatch = 0
            return_path_mismatch = 0
            sender_spoofing = 0
            
            if reply_to_match and from_match:
                from_email = from_match.group(1).lower()
                reply_email = reply_to_match.group(1).lower()
                from_domain = from_email.split('@')[-1]
                reply_domain = reply_email.split('@')[-1]
                if from_domain != reply_domain:
                    reply_to_mismatch = 1
            
            return_path_match = re.search(r'Return-Path:\s*([^\s@]+@[^\s@>]+)', text, re.IGNORECASE)
            if return_path_match and from_match:
                from_email = from_match.group(1).lower()
                ret_email = return_path_match.group(1).lower()
                from_domain = from_email.split('@')[-1]
                ret_domain = ret_email.split('@')[-1]
                if from_domain != ret_domain:
                    return_path_mismatch = 1
                    
            # Sender spoofing display-name mismatch (e.g. display name contains "Google" but from domain is not google.com)
            if from_match:
                from_full = re.search(r'From:\s*([^\n]+)', text, re.IGNORECASE)
                if from_full:
                    from_full_str = from_full.group(1).lower()
                    for brand in BRANDS:
                        if brand in from_full_str and brand not in from_match.group(1).lower():
                            sender_spoofing = 1
                            
            # If spoofing/headers mismatch occurs elsewhere in text (common in body alerts)
            if "reply-to" in text.lower() and reply_to_mismatch == 0:
                # simple check if email addresses mismatch in body
                emails_found = re.findall(r'[a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+', text)
                if len(set(emails_found)) > 1:
                    reply_to_mismatch = 1
            
            # Domain age simulation: if suspicious keywords or spoofing, domain age is low
            domain_age = 3650  # Default to 10 years (reputable)
            if sender_spoofing or reply_to_mismatch or return_path_mismatch:
                domain_age = 15  # 15 days
            elif any(tld in text.lower() for tld in SUSPICIOUS_TLDS):
                domain_age = 90
            
            # URL Extraction and features
            urls = re.findall(r'(https?://\S+|www\.\S+)', text, re.IGNORECASE)
            url_count = len(urls)
            
            url_entropy_list = [calculate_entropy(u) for u in urls]
            avg_url_entropy = np.mean(url_entropy_list) if url_entropy_list else 0.0
            
            redirect_count = sum(1 for u in urls if "redirect" in u.lower() or "forward" in u.lower() or "goto" in u.lower())
            
            https_count = sum(1 for u in urls if u.lower().startswith("https"))
            http_count = url_count - https_count
            https_ratio = https_count / (url_count + 1)
            
            ip_url_count = sum(1 for u in urls if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', u))
            punycode_count = sum(1 for u in urls if "xn--" in u.lower())
            
            shortener_count = 0
            for u in urls:
                if any(sh in u.lower() for sh in SHORTENERS):
                    shortener_count += 1
                    
            suspicious_tld_url_count = 0
            for u in urls:
                if any(f".{tld}" in u.lower() for tld in SUSPICIOUS_TLDS):
                    suspicious_tld_url_count += 1
            
            # Check domain similarity score
            max_similarity = 0.0
            for u in urls:
                domain_part = re.search(r'https?://(?:www\.)?([^/]+)', u, re.IGNORECASE)
                if domain_part:
                    sim = find_domain_similarity(domain_part.group(1))
                    if sim > max_similarity:
                        max_similarity = sim
            
            # NLP heuristics
            # Sentiment check: count simple positive vs negative words
            pos_words = {"please", "thank", "agree", "appreciate", "welcome", "dear", "hello", "regards"}
            neg_words = {"alert", "suspend", "compromise", "violate", "unauthorized", "fail", "error", "warning", "critical"}
            text_lower = text.lower()
            tokens_all = text_lower.split()
            pos_count = sum(1 for t in tokens_all if t in pos_words)
            neg_count = sum(1 for t in tokens_all if t in neg_words)
            sentiment = (pos_count - neg_count) / (len(tokens_all) + 1)
            
            urgency_score = sum(1 for t in tokens_all if t in URGENCY_KEYWORDS)
            emotion_urgency = 1.0 if urgency_score > 2 or "immediately" in text_lower or "urgent" in text_lower else 0.0
            
            # Readability simulation (average word length)
            word_lengths = [len(w) for w in tokens_all]
            avg_word_len = np.mean(word_lengths) if word_lengths else 0.0
            
            # Imperative verbs check (starts with verb or includes command keywords)
            imperative_score = sum(1 for t in tokens_all if t in IMPERATIVE_VERBS)
            imperative_ratio = imperative_score / (len(tokens_all) + 1)
            
            # Stylometric: count pronouns
            pronouns = {"i", "you", "he", "she", "we", "they", "me", "us", "them"}
            pronoun_count = sum(1 for t in tokens_all if t in pronouns)
            stylometric = pronoun_count / (len(tokens_all) + 1)
            
            # Brand detection indicator
            brand_detected = 0
            for brand in BRANDS:
                if brand in text_lower:
                    brand_detected = 1
                    
            # Grammar quality: ratio of non-standard words (dummy estimate: words containing both letters and numbers)
            non_standard = sum(1 for t in tokens_all if re.search(r'\d', t) and re.search(r'[a-zA-Z]', t))
            grammar_quality = 1.0 - (non_standard / (len(tokens_all) + 1))
            
            features_list.append({
                # Metadata / Structural features
                "url_count": float(url_count),
                "has_suspicious_tld": float(1 if suspicious_tld_url_count > 0 or any(f".{tld}" in text.lower() for tld in SUSPICIOUS_TLDS) else 0),
                "has_mfa_lure": float(1 if any(word in text_lower for word in MFA_LURES) else 0),
                "urgency_count": float(urgency_score),
                "email_length": float(length),
                "exclamation_count": float(exclamations),
                "money_char_count": float(money_chars),
                
                # New Header Features
                "has_spf": float(has_spf),
                "has_dkim": float(has_dkim),
                "has_dmarc": float(has_dmarc),
                "reply_to_mismatch": float(reply_to_mismatch),
                "return_path_mismatch": float(return_path_mismatch),
                "domain_age_days": float(domain_age),
                "sender_spoofing": float(sender_spoofing),
                
                # New URL Features
                "url_entropy": float(avg_url_entropy),
                "url_redirects_count": float(redirect_count),
                "https_ratio": float(https_ratio),
                "ip_url_count": float(ip_url_count),
                "punycode_count": float(punycode_count),
                "shortened_url_count": float(shortener_count),
                "domain_similarity_score": float(max_similarity),
                
                # New NLP Features
                "sentiment_score": float(sentiment),
                "emotion_urgency": float(emotion_urgency),
                "readability_score": float(avg_word_len),
                "capital_ratio": float(cap_ratio),
                "grammar_quality": float(grammar_quality),
                "stylometric_features": float(stylometric),
                "imperative_ratio": float(imperative_ratio),
                "brand_detected": float(brand_detected)
            })
            
        return pd.DataFrame(features_list)
