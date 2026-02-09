def get_news_signal_features(ticker: str, date: str) -> dict:
    """
    Returns numeric RAG-based news features for a given stock and date.
    """
    return {
        "rag_sentiment": 0.0,
        "rag_sentiment_strength": 0.0,
        "rag_confidence": 0.0,
        "num_bullish_drivers": 0,
        "num_bearish_risks": 0,
        "event_present": 0,
        "uncertainity_present": 0
    }