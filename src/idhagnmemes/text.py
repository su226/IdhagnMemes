def has_wrap(text: str) -> bool:
    return "\r" in text or "\n" in text or "\u2028" in text or "\u2029" in text
