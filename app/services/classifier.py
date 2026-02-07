"""
Simple classifier for review sentiment and topic using keyword matching.
"""


def classify_review(text: str, rating: int) -> tuple[str, str]:
    text_lower = text.lower()
    
    if rating >= 4:
        sentiment = "Positive"
    elif rating <= 2:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    
    if any(word in text_lower for word in ["staff", "service", "friendly", "rude", "wait", "slow", "quick", "helpful"]):
        topic = "Service"
    elif any(word in text_lower for word in ["clean", "dirty", "messy", "hygiene", "sanitized"]):
        topic = "Cleanliness"
    elif any(word in text_lower for word in ["price", "expensive", "cheap", "cost", "value", "overpriced"]):
        topic = "Price"
    elif any(word in text_lower for word in ["app", "crash", "bug", "website", "order", "technical", "glitch"]):
        topic = "App"
    elif any(word in text_lower for word in ["delivery", "late", "missing", "deliver", "driver"]):
        topic = "Delivery"
    else:
        topic = "Other"
    
    return sentiment, topic
