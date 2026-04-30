import pandas as pd, time, os
from datetime import datetime
from fetch_tmdb import get_now_playing, get_tmdb_reviews
from fetch_omdb import get_omdb_scores
from fetch_youtube import find_trailer, get_trailer_comments
from sentiment import score_sentiment

# Use absolute paths so it saves to the root 'data' folder
# This finds the directory of pipeline.py, then goes up one level
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def run():
    print(f"\n🎬 Pipeline started at {datetime.now()}")
    movies_raw = get_now_playing(pages=2)  # ~40 movies
    rows = []

    for i, m in enumerate(movies_raw):
        title = m["title"]
        year  = m["release_date"][:4] if m.get("release_date") else None
        print(f"  [{i+1}/{len(movies_raw)}] Processing: {title}")

        # TMDB reviews sentiment
        tmdb_reviews = get_tmdb_reviews(m["id"])
        tmdb_sentiment = score_sentiment(tmdb_reviews)

        # OMDb critic scores
        omdb = get_omdb_scores(title, year) or {}

        # YouTube trailer comment sentiment
        vid_id = find_trailer(title, year)
        yt_comments = get_trailer_comments(vid_id) if vid_id else []
        yt_sentiment = score_sentiment([c["text"] for c in yt_comments])

        rows.append({
            "title":              title,
            "release_date":       m.get("release_date"),
            "tmdb_score":         m.get("vote_average"),
            "tmdb_votes":         m.get("vote_count"),
            "rt_score":           omdb.get("rt_score"),
            "metacritic":         omdb.get("metacritic"),
            "imdb_rating":        omdb.get("imdb_rating"),
            "box_office":         omdb.get("box_office"),
            "audience_positive":  yt_sentiment.get("positive_pct", 0),
            "audience_polarity":  yt_sentiment.get("avg_polarity", 0),
            "audience_samples":   yt_sentiment.get("sample_size", 0),
            "review_positive":    tmdb_sentiment.get("positive_pct", 0),
            "review_polarity":    tmdb_sentiment.get("avg_polarity", 0),
            "fetched_at":         datetime.utcnow().isoformat()
        })

        time.sleep(0.3)  # be polite to APIs

    df = pd.DataFrame(rows)
    
    # Create the data folder in the project root
    os.makedirs(DATA_DIR, exist_ok=True)
    file_path = os.path.join(DATA_DIR, "movies.csv")
    
    df.to_csv(file_path, index=False)
    print(f"\n✅ Saved {len(df)} movies to {file_path}")
    print(df[["title","tmdb_score","rt_score","audience_positive"]].to_string())

if __name__ == "__main__":
    run()

