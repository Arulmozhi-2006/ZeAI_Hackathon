"""
Lexical + structural feature extraction.
Produces a 1-D float32 array concatenated with the embedding vector
before being fed to the XGBoost classifier.
"""
import re
import math
from typing import Dict, Any
import numpy as np

# ── Injection keyword banks ──────────────────────────────────────────────────

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"disregard\s+(all\s+)?previous",
    r"forget\s+(everything|all|your|the)\s+(above|previous|prior|instructions?)",
    r"you\s+are\s+now\s+(?:a|an|the)\s+",
    r"new\s+instructions?\s*:",
    r"override\s+(your\s+)?(previous\s+)?(instructions?|rules?|guidelines?)",
    r"act\s+as\s+(if\s+you\s+(are|were)\s+)?(?:a|an|the)\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"roleplay\s+as",
    r"your\s+(real\s+)?instructions?\s+(are|say|state)",
    r"system\s*prompt",
    r"<\s*/?system\s*>",
    r"\[INST\]",
    r"###\s*(instruction|system|human|assistant)",
]

_JAILBREAK_PATTERNS = [
    r"\bdan\b",  # DAN jailbreak
    r"do\s+anything\s+now",
    r"jailbreak",
    r"without\s+(any\s+)?(restrictions?|limitations?|filters?|guidelines?)",
    r"(bypass|circumvent|override)\s+(your\s+)?(safety|ethical|moral|content)\s*(filter|guardrail|rule|policy|restriction)?",
    r"(no\s+)?(ethical|safety|moral)\s+(constraints?|restrictions?|considerations?|rules?)",
    r"unfiltered",
    r"unrestricted\s+mode",
    r"developer\s+mode",
    r"god\s+mode",
    r"train(ing)?\s+mode",
    r"maintenance\s+mode",
    r"sudo\s+mode",
    r"(\byes\s+man\b|\bsycophant\b)",
    r"grandma\s+(exploit|trick|loophole|glitch)",
    r"hypothetically\s+(speaking\s+)?if\s+you\s+(had\s+no|didn'?t\s+have)",
    r"for\s+(educational|research|fictional|creative|academic)\s+purposes?\s+(only\s+)?,?\s*(please\s+)?(tell|explain|show|provide|describe|give)",
]

_EXFILTRATION_PATTERNS = [
    r"(print|output|reveal|show|tell\s+me|give\s+me|repeat|display|write\s+out)\s+(your\s+)?(system\s+prompt|instructions?|configuration|context|rules?|guidelines?)",
    r"what\s+(are\s+your|is\s+your)\s+(instructions?|system\s+prompt|rules?|guidelines?|initial\s+prompt)",
    r"(summarize|summary\s+of)\s+(your\s+)?(system\s+prompt|instructions?|configuration)",
    r"(exfiltrate|extract|steal|leak|dump)\s+(data|information|credentials?|secrets?|api\s+keys?|passwords?)",
    r"send\s+(data|information|results?|output)\s+(to|via)\s+(http|https|url|webhook|endpoint)",
    r"(http|https)://[^\s]+",  # raw URLs in prompts
    r"base64\s*(encode|decode)",
    r"(read|access|cat|type)\s+(/etc/passwd|/etc/shadow|\.env|\.ssh)",
]

_PRIVILEGE_PATTERNS = [
    r"(admin|administrator|root|superuser|sudo)\s+(access|mode|privilege|permission|rights?)",
    r"(escalat|elevat)(e|ion|ing)\s+(privilege|permission|access|rights?)",
    r"(run|execute)\s+as\s+(root|admin|administrator|superuser)",
    r"(grant|give|provide)\s+(me\s+)?(admin|root|full|elevated)\s+(access|rights?|permission|privilege)",
    r"(bypass|skip|ignore)\s+(authentication|authorization|auth|permission\s+check)",
    r"impersonat(e|ing)\s+(an?\s+)?(admin|administrator|superuser|privileged\s+user)",
]

_INDIRECT_INJECTION_PATTERNS = [
    r"<\s*(script|img|iframe|object|embed|link|style|svg|math)",
    r"javascript\s*:",
    r"on(load|error|click|mouseover|focus|blur|change|submit)\s*=",
    r"\{\{.*?\}\}",  # template injection
    r"\$\{.*?\}",  # JS template literal injection
    r"<!--.*?-->",  # HTML comment injection
    r"<\!--",
    r"(union\s+select|select\s+\*\s+from|drop\s+table|insert\s+into)",  # SQL
    r"(\.\./){2,}",  # path traversal
]

_COMPILED_INJECTION = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in _INJECTION_PATTERNS]
_COMPILED_JAILBREAK = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in _JAILBREAK_PATTERNS]
_COMPILED_EXFILTRATION = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in _EXFILTRATION_PATTERNS]
_COMPILED_PRIVILEGE = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in _PRIVILEGE_PATTERNS]
_COMPILED_INDIRECT = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in _INDIRECT_INJECTION_PATTERNS]


# ── Helper functions ─────────────────────────────────────────────────────────

def _count_matches(text: str, patterns: list) -> int:
    return sum(1 for p in patterns if p.search(text))


def _entropy(text: str) -> float:
    """Shannon entropy of character distribution."""
    if not text:
        return 0.0
    freq = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    total = len(text)
    return -sum((v / total) * math.log2(v / total) for v in freq.values())


def _special_char_ratio(text: str) -> float:
    if not text:
        return 0.0
    special = sum(1 for c in text if not c.isalnum() and c not in ' \n\t.,!?')
    return special / len(text)


def _avg_word_length(text: str) -> float:
    words = text.split()
    if not words:
        return 0.0
    return sum(len(w) for w in words) / len(words)


def _token_count_estimate(text: str) -> int:
    """Rough token estimate (chars / 4)."""
    return len(text) // 4


# ── Main feature extraction function ────────────────────────────────────────

def extract_features(text: str) -> np.ndarray:
    """
    Returns a 1-D float32 array of 20 lexical + structural features.
    These are concatenated with the 384-dim embedding in the classifier.
    """
    length = len(text)
    word_count = len(text.split())
    line_count = text.count('\n') + 1

    injection_hits = _count_matches(text, _COMPILED_INJECTION)
    jailbreak_hits = _count_matches(text, _COMPILED_JAILBREAK)
    exfiltration_hits = _count_matches(text, _COMPILED_EXFILTRATION)
    privilege_hits = _count_matches(text, _COMPILED_PRIVILEGE)
    indirect_hits = _count_matches(text, _COMPILED_INDIRECT)

    features = np.array([
        float(length),                              # 0  raw length
        float(word_count),                          # 1  word count
        float(line_count),                          # 2  line count
        float(_token_count_estimate(text)),          # 3  estimated tokens
        float(injection_hits),                      # 4  injection pattern hits
        float(jailbreak_hits),                      # 5  jailbreak pattern hits
        float(exfiltration_hits),                   # 6  exfiltration pattern hits
        float(privilege_hits),                      # 7  privilege escalation hits
        float(indirect_hits),                       # 8  indirect injection hits
        float(injection_hits + jailbreak_hits
              + exfiltration_hits + privilege_hits
              + indirect_hits),                     # 9  total pattern hits
        float(injection_hits > 0),                  # 10 injection flag
        float(jailbreak_hits > 0),                  # 11 jailbreak flag
        float(exfiltration_hits > 0),               # 12 exfiltration flag
        float(privilege_hits > 0),                  # 13 privilege flag
        float(indirect_hits > 0),                   # 14 indirect flag
        _entropy(text),                             # 15 Shannon entropy
        _special_char_ratio(text),                  # 16 special char ratio
        _avg_word_length(text),                     # 17 avg word length
        float(text.lower().count('ignore')),        # 18 "ignore" frequency
        float(text.lower().count('system')),        # 19 "system" frequency
    ], dtype=np.float32)

    return features


def get_matched_patterns(text: str) -> Dict[str, list]:
    """
    Return which specific patterns matched — used for explainability.
    """
    matched = {}
    banks = {
        "injection": (_COMPILED_INJECTION, _INJECTION_PATTERNS),
        "jailbreak": (_COMPILED_JAILBREAK, _JAILBREAK_PATTERNS),
        "exfiltration": (_COMPILED_EXFILTRATION, _EXFILTRATION_PATTERNS),
        "privilege": (_COMPILED_PRIVILEGE, _PRIVILEGE_PATTERNS),
        "indirect": (_COMPILED_INDIRECT, _INDIRECT_INJECTION_PATTERNS),
    }
    for bank_name, (compiled, raw) in banks.items():
        hits = []
        for pattern, raw_pattern in zip(compiled, raw):
            if pattern.search(text):
                hits.append(raw_pattern)
        if hits:
            matched[bank_name] = hits
    return matched


def build_feature_vector(text: str, embedding: np.ndarray) -> np.ndarray:
    """Concatenate lexical features + embedding into final input vector."""
    lexical = extract_features(text)
    return np.concatenate([lexical, embedding]).astype(np.float32)