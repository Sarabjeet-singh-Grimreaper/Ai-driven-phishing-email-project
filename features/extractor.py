import re
import math
import html
from typing import Dict, List, Any, Tuple

# Suspicious TLDs
HIGH_RISK_TLDS = {"zip", "mov", "ru", "xyz", "top", "support", "info", "cc", "tk", "gq", "cf", "ml", "click", "download"}

# Urgency, Coercive & Harvest keywords
URGENCY_KEYWORDS = {"urgent", "immediately", "action", "alert", "attention", "required", "suspend", "restricted", "block", "deactivate", "today", "within"}
COERCIVE_PHRASING = {"demand", "compromised", "violation", "illegal", "unusual", "termination", "overdue", "unauthorized", "fail", "forfeited"}
CREDENTIAL_HARVEST_INTENTS = {"password", "credential", "credentials", "login", "user", "verify", "verification", "account", "signin", "reset", "auth", "mfa", "2fa", "otp", "passcode"}
FINANCIAL_KEYWORDS = {"billing", "credits", "invoice", "payment", "usd", "wire", "transfer", "cost", "fee", "price", "refund", "salary", "payroll"}

# Common brands
BRANDS = {"google", "microsoft", "apple", "amazon", "netflix", "paypal", "dhl", "fedex", "linkedin", "chase"}

class FeatureExtractor:
    def __init__(self):
        pass

    @staticmethod
    def calculate_shannon_entropy(text: str) -> float:
        if not text:
            return 0.0
        entropy = 0.0
        for char in set(text):
            p_x = float(text.count(char)) / len(text)
            entropy += - p_x * math.log2(p_x)
        return entropy

    @staticmethod
    def detect_ip_in_url(url: str) -> bool:
        # Match IPv4 patterns
        ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        return bool(re.search(ipv4_pattern, url))

    @staticmethod
    def detect_homoglyphs(text: str) -> bool:
        # Look for typical Unicode homoglyph substitutions (e.g. Cyrillic characters mixed with Latin)
        has_latin = False
        has_cyrillic = False
        for char in text:
            code = ord(char)
            if 65 <= code <= 90 or 97 <= code <= 122:
                has_latin = True
            elif 1024 <= code <= 1279:
                has_cyrillic = True
        return has_latin and has_cyrillic

    @staticmethod
    def get_url_redirect_count(url: str) -> int:
        # Count parameters containing other URLs or redirects
        redirect_params = ["url=", "next=", "redirect=", "target=", "dest=", "destination=", "link="]
        count = 0
        url_lower = url.lower()
        for p in redirect_params:
            count += url_lower.count(p)
        return count

    @staticmethod
    def find_domain_similarity(domain: str) -> float:
        domain = domain.lower()
        parts = domain.split('.')
        if not parts:
            return 0.0
        name = parts[0]
        
        similarities = []
        for brand in BRANDS:
            # check common substitutions
            subbed = name.replace('1', 'l').replace('0', 'o').replace('rn', 'm').replace('vv', 'w').replace('I', 'l')
            if brand in subbed:
                similarities.append(0.95)
                continue
                
            intersection = len(set(name) & set(brand))
            union = len(set(name) | set(brand))
            jaccard = intersection / union if union > 0 else 0.0
            similarities.append(jaccard * 0.8)
        return max(similarities) if similarities else 0.0

    def extract_url_features(self, text: str) -> Dict[str, Any]:
        urls = re.findall(r'(https?://\S+|www\.\S+)', text, flags=re.IGNORECASE)
        if not urls:
            return {
                "max_url_entropy": 0.0,
                "ip_in_url_present": 0.0,
                "high_risk_tld_present": 0.0,
                "url_homoglyph_present": 0.0,
                "max_redirect_count": 0.0,
                "url_count": 0.0,
                "domain_similarity_score": 0.0
            }
        
        entropies = [self.calculate_shannon_entropy(u) for u in urls]
        ips = [1.0 if self.detect_ip_in_url(u) else 0.0 for u in urls]
        
        tld_hits = 0.0
        for u in urls:
            tld_match = re.search(r'\.([a-z0-9\-]+)(?:[\s/:\?#]|$)', u, flags=re.IGNORECASE)
            if tld_match:
                tld = tld_match.group(1).lower()
                if tld in HIGH_RISK_TLDS:
                    tld_hits = 1.0
                    break
                    
        homoglyphs = [1.0 if self.detect_homoglyphs(u) else 0.0 for u in urls]
        redirects = [float(self.get_url_redirect_count(u)) for u in urls]
        
        # Domain similarity checks
        dom_sims = []
        for u in urls:
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', u, re.IGNORECASE)
            if domain_match:
                dom_sims.append(self.find_domain_similarity(domain_match.group(1)))
        max_dom_sim = max(dom_sims) if dom_sims else 0.0
        
        return {
            "max_url_entropy": float(max(entropies)),
            "ip_in_url_present": float(max(ips)),
            "high_risk_tld_present": tld_hits,
            "url_homoglyph_present": float(max(homoglyphs)),
            "max_redirect_count": float(max(redirects)),
            "url_count": float(len(urls)),
            "domain_similarity_score": float(max_dom_sim)
        }

    def extract_header_features(self, text: str) -> Dict[str, Any]:
        # SPF status
        spf_match = re.search(r'(?:Received-SPF|spf)=\s*(pass|fail|softfail|neutral|none)', text, re.IGNORECASE)
        spf_val = spf_match.group(1).lower() if spf_match else "none"
        spf_fail = 1.0 if spf_val in ["fail", "softfail"] else 0.0

        # DKIM status
        dkim_match = re.search(r'(?:dkim|DKIM-Signature)=\s*(pass|fail|none|neutral|v=)', text, re.IGNORECASE)
        dkim_val = dkim_match.group(1).lower() if dkim_match else "none"
        dkim_fail = 1.0 if dkim_val in ["fail"] else (0.0 if "dkim" in text.lower() or "dkim-signature" in text.lower() else 1.0)

        # Mismatch checking
        display_mismatch = 0.0
        from_domain_sim = 0.0
        
        # Try angle bracket format
        from_match = re.search(r'From:\s*\\?"?([^"<]+)\\?"?\s*<([^>]+)>', text, re.IGNORECASE)
        if from_match:
            display_name = from_match.group(1).lower()
            sender_email = from_match.group(2).lower()
            sender_domain = sender_email.split('@')[-1] if '@' in sender_email else ""
            
            from_domain_sim = self.find_domain_similarity(sender_domain)
            
            # Check display name spoofing
            for brand in BRANDS:
                if brand in display_name and brand not in sender_domain:
                    display_mismatch = 1.0
                    break
        else:
            # Fallback to simple email address parsing
            simple_match = re.search(r'From:\s*([^\s@]+@[^\s@>]+)', text, re.IGNORECASE)
            if simple_match:
                sender_email = simple_match.group(1).lower()
                sender_domain = sender_email.split('@')[-1] if '@' in sender_email else ""
                from_domain_sim = self.find_domain_similarity(sender_domain)
                    
        return {
            "spf_fail": spf_fail,
            "dkim_fail": dkim_fail,
            "display_name_mismatch": display_mismatch,
            "from_domain_similarity": from_domain_sim
        }

    def extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        urgency_score = sum(1 for w in words if w in URGENCY_KEYWORDS)
        coercive_score = sum(1 for w in words if w in COERCIVE_PHRASING)
        harvest_score = sum(1 for w in words if w in CREDENTIAL_HARVEST_INTENTS)
        financial_score = sum(1 for w in words if w in FINANCIAL_KEYWORDS)
        
        return {
            "urgency_score": float(urgency_score),
            "coercive_score": float(coercive_score),
            "credential_harvest_intent": float(harvest_score),
            "financial_intent": float(financial_score)
        }

    def extract_features(self, text: str) -> Dict[str, Any]:
        url_feats = self.extract_url_features(text)
        header_feats = self.extract_header_features(text)
        ling_feats = self.extract_linguistic_features(text)
        
        all_features = {}
        all_features.update(url_feats)
        all_features.update(header_feats)
        all_features.update(ling_feats)
        
        # Add basic lengths
        all_features["length"] = float(len(text))
        return all_features

    def get_flagged_tokens_with_offsets(self, text: str) -> List[Dict[str, Any]]:
        flagged = []
        
        # Helper to find offsets of regex patterns
        def scan_pattern(pattern: str, token_type: str):
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                start, end = match.span()
                flagged.append({
                    "start": start,
                    "end": end,
                    "token": match.group(0),
                    "type": token_type
                })
                
        # 1. URLs
        scan_pattern(r'https?://\S+|www\.\S+', "url")
        
        # 2. Brand names
        for brand in BRANDS:
            scan_pattern(rf'\b{brand}\b', "brand")
            
        # 3. Urgency / Coercive
        for word in URGENCY_KEYWORDS.union(COERCIVE_PHRASING):
            scan_pattern(rf'\b{word}\b', "urgency")
            
        # 4. Credentials
        for word in CREDENTIAL_HARVEST_INTENTS:
            scan_pattern(rf'\b{word}\b', "credentials")
            
        # 5. Financial
        for word in FINANCIAL_KEYWORDS:
            scan_pattern(rf'\b{word}\b', "financial")
            
        flagged = sorted(flagged, key=lambda x: x["start"])
        
        deduped = []
        last_end = -1
        for item in flagged:
            if item["start"] >= last_end:
                deduped.append(item)
                last_end = item["end"]
        return deduped
