import requests, os
from dotenv import load_dotenv
load_dotenv()

BASE = "https://api.themoviedb.org/3"
KEY  = os.getenv("TMDB_API_KEY")

def get_now_playing(pages=3):
    movies = []
    for page in range(1, pages + 1):
        r = requests.get(f"{BASE}/movie/now_playing",
            params={"api_key": KEY, "language": "en-US", "page": page})
        movies.extend(r.json().get("results", []))
    return movies

def get_movie_details(tmdb_id):
    r = requests.get(f"{BASE}/movie/{tmdb_id}",
        params={"api_key": KEY, "append_to_response": "credits,keywords"})
    return r.json()

def get_tmdb_reviews(tmdb_id):
    r = requests.get(f"{BASE}/movie/{tmdb_id}/reviews",
        params={"api_key": KEY, "language": "en-US", "page": 1})
    results = r.json().get("results", [])
    # return list of review content strings
    return [rev["content"] for rev in results[:10]]

if __name__ == "__main__":
    movies = get_now_playing()
    print(f"Fetched {len(movies)} now-playing movies")
    for m in movies[:5]:
        print(f"  {m['title']} | TMDB Score: {m['vote_average']} | Votes: {m['vote_count']}")
