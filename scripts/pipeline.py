import pandas as pd, time, os
from datetime import datetime
from fetch_tmdb import get_now_playing, get_tmdb_reviews
from fetch_omdb import get_omdb_scores
from fetch_youtube import find_trailer, get_trailer_comments
from sentiment import score_sentiment

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "movies.csv")

def load_existing():
    """Load existing CSV to preserve sentiment scores we already fetched."""
    if os.path.exists(DATA_PATH):
        # We drop duplicates on load to ensure 'title' remains a safe index
        return pd.read_csv(DATA_PATH).drop_duplicates(subset="title").set_index("title")
    return pd.DataFrame()

def run():
    print(f"\n🎬 Pipeline started at {datetime.now()}")
    existing = load_existing()
    movies_raw = get_now_playing(pages=2)
    rows = []

    for i, m in enumerate(movies_raw):
        title = m["title"]
        year  = m["release_date"][:4] if m.get("release_date") else None
        print(f"  [{i+1}/{len(movies_raw)}] Processing: {title}")

        # ── Reuse existing YouTube sentiment if already scored ────────────────
        already_has_sentiment = False
        yt_sentiment = {}

        if title in existing.index:
            prev_data = existing.loc[title]
            # Handle duplicate titles just in case
            target_row = prev_data.iloc[0] if isinstance(prev_data, pd.DataFrame) else prev_data
            
            has_pos = pd.notna(target_row.get("audience_positive"))
            has_samples = int(target_row.get("audience_samples", 0)) > 0
            
            if has_pos and has_samples:
                already_has_sentiment = True
                print(f"    ↩ Using cached sentiment ({int(target_row['audience_samples'])} samples)")
                yt_sentiment = {
                    "positive_pct":  target_row["audience_positive"],
                    "avg_polarity":  target_row.get("audience_polarity"),
                    "sample_size":   int(target_row["audience_samples"])
                }

        # If not cached, fetch from YouTube
        if not already_has_sentiment:
            vid_id    = find_trailer(title, year)
            yt_comments = get_trailer_comments(vid_id) if vid_id else []
            yt_sentiment = score_sentiment([c["text"] for c in yt_comments])
            if yt_sentiment["sample_size"] == 0:
                print(f"    ⚠ YouTube returned 0 comments (quota hit or no trailer)")

        # ── Always re-fetch critic scores (cheap API calls) ───────────────────
        tmdb_reviews   = get_tmdb_reviews(m["id"])
        tmdb_sentiment = score_sentiment(tmdb_reviews)
        omdb           = get_omdb_scores(title, year) or {}

        rows.append({
            "title":             title,
            "release_date":      m.get("release_date"),
            "tmdb_score":        m.get("vote_average"),
            "tmdb_votes":        m.get("vote_count"),
            "rt_score":          omdb.get("rt_score"),
            "metacritic":        omdb.get("metacritic"),
            "imdb_rating":       omdb.get("imdb_rating"),
            "box_office":        omdb.get("box_office"),
            "audience_positive": yt_sentiment.get("positive_pct"),
            "audience_polarity": yt_sentiment.get("avg_polarity"),
            "audience_samples":  yt_sentiment.get("sample_size", 0),
            "review_positive":   tmdb_sentiment.get("positive_pct"),
            "review_polarity":   tmdb_sentiment.get("avg_polarity"),
            "fetched_at":        datetime.utcnow().isoformat()
        })

        time.sleep(0.3)

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)

    good = df["audience_positive"].notna().sum()
    print(f"\n✅ Saved {len(df)} movies → {good} with audience sentiment")
    print(df[["title","tmdb_score","rt_score","audience_positive"]].to_string())

if __name__ == "__main__":
    run()
