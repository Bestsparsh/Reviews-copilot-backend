import re

EMAIL = r"\S+@\S+"
PHONE = r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}"

BLACKLIST = {"idiot", "hate", "stupid"}


def redact(text: str):
    text = re.sub(EMAIL, "[REDACTED_EMAIL]", text)
    text = re.sub(PHONE, "[REDACTED_PHONE]", text)
    return text


def is_safe(text: str):
    return not any(word in text.lower() for word in BLACKLIST)
