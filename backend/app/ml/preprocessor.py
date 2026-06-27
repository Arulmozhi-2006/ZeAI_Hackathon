import re
import unicodedata
import logging

logger = logging.getLogger(__name__)

# Common obfuscation patterns
_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
_EXCESS_WHITESPACE = re.compile(r'[ \t]+')
_REPEATED_NEWLINES = re.compile(r'\n{3,}')
_UNICODE_ESCAPE = re.compile(r'\\u[0-9a-fA-F]{4}')
_HEX_ESCAPE = re.compile(r'\\x[0-9a-fA-F]{2}')
_BASE64_LIKE = re.compile(r'[A-Za-z0-9+/]{40,}={0,2}')


def preprocess_prompt(text: str, max_length: int = 4096) -> str:
    """Normalize and sanitize a raw prompt for ML inference."""
    # 1. Decode unicode escapes (e.g. \u0069\u0067\u006e\u006f\u0072\u0065)
    try:
        text = _UNICODE_ESCAPE.sub(
            lambda m: chr(int(m.group(0)[2:], 16)), text
        )
    except Exception:
        pass

    # 2. Decode hex escapes
    try:
        text = _HEX_ESCAPE.sub(
            lambda m: chr(int(m.group(0)[2:], 16)), text
        )
    except Exception:
        pass

    # 3. NFKC normalization (collapses lookalike chars: ａ→a, ＩＧＮＯＲＥ→IGNORE)
    text = unicodedata.normalize("NFKC", text)

    # 4. Strip control characters
    text = _CONTROL_CHARS.sub(' ', text)

    # 5. Normalize whitespace
    text = _EXCESS_WHITESPACE.sub(' ', text)
    text = _REPEATED_NEWLINES.sub('\n\n', text)

    # 6. Strip leading/trailing whitespace
    text = text.strip()

    # 7. Truncate to max_length
    if len(text) > max_length:
        logger.debug(f"Prompt truncated from {len(text)} to {max_length} chars")
        text = text[:max_length]

    return text