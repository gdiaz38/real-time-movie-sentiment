from textblob import TextBlob

def score_sentiment(texts: list[str]) -> dict:
    """
    Takes a list of strings, returns aggregate sentiment stats.
    polarity: -1 (negative) to +1 (positive)
    """
    if not texts:
        return {"positive_pct": None, "avg_polarity": None, "sample_size": 0}

    polarities = []
    for text in texts:
        blob = TextBlob(str(text))
        polarities.append(blob.sentiment.polarity)

    positive = sum(1 for p in polarities if p > 0.05)
    negative = sum(1 for p in polarities if p < -0.05)
    neutral  = len(polarities) - positive - negative

    return {
        "positive_pct":  round(positive / len(polarities) * 100, 1),
        "negative_pct":  round(negative / len(polarities) * 100, 1),
        "neutral_pct":   round(neutral  / len(polarities) * 100, 1),
        "avg_polarity":  round(sum(polarities) / len(polarities), 3),
        "sample_size":   len(polarities)
    }

if __name__ == "__main__":
    sample = ["This movie was absolutely amazing!", "Worst film I have seen in years.",
              "Pretty average, nothing special.", "The visuals were stunning but plot was weak"]
    print(score_sentiment(sample))
