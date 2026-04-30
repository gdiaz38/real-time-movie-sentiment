import requests, os, time
from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv("OMDB_API_KEY")

def get_omdb_scores(title, year=None):
    params = {"apikey": KEY, "t": title, "type": "movie"}
    if year:
        params["y"] = year
    r = requests.get("https://www.omdbapi.com/", params=params)
    data = r.json()

    if data.get("Response") == "False":
        return None

    scores = {"title": data.get("Title"), "imdb_rating": data.get("imdbRating"),
              "imdb_votes": data.get("imdbVotes"), "box_office": data.get("BoxOffice"),
              "awards": data.get("Awards"), "rt_score": None, "metacritic": None}

    for rating in data.get("Ratings", []):
        if rating["Source"] == "Rotten Tomatoes":
            scores["rt_score"] = rating["Value"]
        if rating["Source"] == "Metacritic":
            scores["metacritic"] = rating["Value"]

    return scores

if __name__ == "__main__":
    test = get_omdb_scores("Minecraft Movie", 2025)
    print(test)
