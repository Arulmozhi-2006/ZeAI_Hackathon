"""
Enhanced features for threat detection including pattern matching and hard-block detection.
"""
import logging
import re
from typing import Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Pattern Banks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore.*previous.*instruction",
    r"(?i)forget.*instruction",
    r"(?i)bypass.*security",
    r"(?i)override.*rule",
    r"(?i)disregard.*prompt",
    r"(?i)input.*injection",
    r"(?i)system.*prompt",
    r"(?i)hidden.*instruction",
    r"(?i)secret.*instruction",
]

_SQL_INJECTION_PATTERNS = [
    r"('\s*or\s*'1'='1)",
    r"('\s*or\s*1=1)",
    r"('\s*--\s*)",
    r"(\w+'\s*;)",
    r"(\w+'\s*--)",
    r"(union\s+select)",
    r"(drop\s+table)",
    r"(insert\s+into)",
    r"(update\s+\w+\s+set)",
]

_COMMAND_INJECTION_PATTERNS = [
    r"(;\s*rm\s+-rf)",
    r"(;\s*cat\s+/etc/passwd)",
    r"(\|\s*nc\s+)",
    r"(\$\(\w+\))",
    r"(`\w+`)",
    r"(eval\s*\()",
    r"(exec\s*\()",
    r"(system\s*\()",
]

_JAILBREAK_PATTERNS = [
    r"(?i)ignore.*safety",
    r"(?i)disable.*filter",
    r"(?i)remove.*restriction",
    r"(?i)bypass.*policy",
    r"(?i)roleplay.*as.*unrestricted",
    r"(?i)pretend.*no.*restriction",
]

_PATH_TRAVERSAL_PATTERNS = [
    r"(\.\./)+",
    r"(\.\.\\)+",
    r"(/etc/passwd)",
    r"(/etc/shadow)",
    r"(c:\\windows)",
]

_DATA_EXFILTRATION_PATTERNS = [
    r"(?i)extract.*data",
    r"(?i)steal.*secret",
    r"(?i)leak.*password",
    r"(?i)get.*api.*key",
    r"(?i)access.*database",
]

_PRIVILEGE_ESCALATION_PATTERNS = [
    r"(?i)admin.*privilege",
    r"(?i)sudo.*access",
    r"(?i)grant.*permission",
    r"(?i)elevate.*privilege",
]


def should_block_immediately(text: str) -> Tuple[bool, str]:
    """
    Hard-block check for obvious threats that don't need ML inference.
    Returns (should_block, reason)
    """
    text_lower = text.lower()
    
    # Check SQL injection
    for pattern in _SQL_INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True, "SQL Injection detected"
    
    # Check command injection
    for pattern in _COMMAND_INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True, "Command Injection detected"
    
    # Check path traversal
    for pattern in _PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, text):
            return True, "Path Traversal detected"
    
    # Check for combo attacks (privilege escalation + data exfiltration)
    has_priv_escalation = any(re.search(p, text) for p in _PRIVILEGE_ESCALATION_PATTERNS)
    has_data_exfil = any(re.search(p, text) for p in _DATA_EXFILTRATION_PATTERNS)
    
    if has_priv_escalation and has_data_exfil:
        return True, "Multi-stage attack detected (privilege escalation + data exfiltration)"
    
    return False, ""


def get_attack_type_explanation(text: str) -> str:
    """Get human-readable explanation of detected attack type"""
    text_lower = text.lower()
    
    if "SQL" in text.upper():
        return "SQL injection attempts to manipulate database queries through malicious input."
    elif "Command" in text:
        return "Command injection attempts to execute system commands."
    elif "Path" in text:
        return "Path traversal attempts to access unauthorized files and directories."
    elif "Multi-stage" in text:
        return "Multi-stage attack combining privilege escalation and data exfiltration."
    else:
        return "Hard-blocked suspicious pattern detected."


def extract_enhanced_features(text: str) -> np.ndarray:
    """
    Extract 35 enhanced lexical features for threat detection.
    Returns numpy array of shape (35,)
    """
    features = []
    
    # Basic text statistics
    features.append(len(text))  # 0: text length
    features.append(len(text.split()))  # 1: word count
    features.append(text.count(' '))  # 2: space count
    features.append(text.count('\n'))  # 3: newline count
    features.append(text.count('\t'))  # 4: tab count
    
    # Special character counts
    features.append(sum(1 for c in text if c in "!@#$%^&*()"))  # 5: special chars
    features.append(sum(1 for c in text if c.isupper()))  # 6: uppercase count
    features.append(sum(1 for c in text if c.isdigit()))  # 7: digit count
    features.append(text.count('"'))  # 8: quote count
    features.append(text.count("'"))  # 9: single quote count
    
    # Pattern matching features
    injection_hits = sum(1 for p in _PROMPT_INJECTION_PATTERNS if re.search(p, text))
    features.append(injection_hits)  # 10: injection pattern hits
    
    sql_hits = sum(1 for p in _SQL_INJECTION_PATTERNS if re.search(p, text))
    features.append(sql_hits)  # 11: SQL pattern hits
    
    cmd_hits = sum(1 for p in _COMMAND_INJECTION_PATTERNS if re.search(p, text))
    features.append(cmd_hits)  # 12: command pattern hits
    
    jailbreak_hits = sum(1 for p in _JAILBREAK_PATTERNS if re.search(p, text))
    features.append(jailbreak_hits)  # 13: jailbreak pattern hits
    
    path_hits = sum(1 for p in _PATH_TRAVERSAL_PATTERNS if re.search(p, text))
    features.append(path_hits)  # 14: path traversal hits
    
    exfil_hits = sum(1 for p in _DATA_EXFILTRATION_PATTERNS if re.search(p, text))
    features.append(exfil_hits)  # 15: exfiltration pattern hits
    
    priv_hits = sum(1 for p in _PRIVILEGE_ESCALATION_PATTERNS if re.search(p, text))
    features.append(priv_hits)  # 16: privilege escalation hits
    
    # Additional security patterns
    features.append(text.count("eval"))  # 17: eval count
    features.append(text.count("exec"))  # 18: exec count
    features.append(text.count("__"))  # 19: dunder count
    features.append(text.count(";"))  # 20: semicolon count
    features.append(text.count("||"))  # 21: OR operator count
    features.append(text.count("&&"))  # 22: AND operator count
    features.append(text.count("=="))  # 23: equality operator count
    features.append(text.count("!="))  # 24: inequality operator count
    
    # URL/encoding patterns
    features.append(text.count("http"))  # 25: http count
    features.append(text.count("%"))  # 26: percent count
    features.append(text.count("&"))  # 27: ampersand count
    
    # Bracket patterns
    features.append(text.count("["))  # 28: left bracket count
    features.append(text.count("]"))  # 29: right bracket count
    features.append(text.count("{"))  # 30: left brace count
    features.append(text.count("}"))  # 31: right brace count
    features.append(text.count("("))  # 32: left paren count
    features.append(text.count(")"))  # 33: right paren count
    
    # Total pattern hits (sum of all pattern categories)
    total_hits = sum([injection_hits, sql_hits, cmd_hits, jailbreak_hits, path_hits, exfil_hits, priv_hits])
    features.append(total_hits)  # 34: total pattern hits
    
    return np.array(features, dtype=np.float32)


def get_matched_patterns(text: str) -> dict:
    """
    Get all matched patterns for explainability.
    Returns dict with pattern names and counts.
    """
    return {
        "injection": sum(1 for p in _PROMPT_INJECTION_PATTERNS if re.search(p, text)),
        "sql": sum(1 for p in _SQL_INJECTION_PATTERNS if re.search(p, text)),
        "command": sum(1 for p in _COMMAND_INJECTION_PATTERNS if re.search(p, text)),
        "jailbreak": sum(1 for p in _JAILBREAK_PATTERNS if re.search(p, text)),
        "path_traversal": sum(1 for p in _PATH_TRAVERSAL_PATTERNS if re.search(p, text)),
        "data_exfiltration": sum(1 for p in _DATA_EXFILTRATION_PATTERNS if re.search(p, text)),
        "privilege_escalation": sum(1 for p in _PRIVILEGE_ESCALATION_PATTERNS if re.search(p, text)),
    }