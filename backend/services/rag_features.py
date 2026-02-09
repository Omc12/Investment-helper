def rag_signal_to_features(signal: dict) -> dict:
    sentiment_map = {
        "bullish": 1,
        "neutral": 0,
        "bearish": -1
    }

    sentiment_score = sentiment_map.get(signal["overall_sentiment"], 0)

    return {
        "rag_sentiment": sentiment_score
            * signal["sentiment_strength"]
            * signal["confidence"],

        "rag_sentiment_strength": signal["sentiment_strength"],
        "rag_confidence": signal["confidence"],

        "num_bullish_drivers": len(signal["bullish_drivers"]),
        "num_bearish_risks": len(signal["bearish_risks"]),

        "event_present": int(len(signal["key_events"]) > 0),
        "uncertainty_present": int(len(signal["uncertainty_flags"]) > 0),
    }
