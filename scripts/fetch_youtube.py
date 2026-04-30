import requests, os
from dotenv import load_dotenv
load_dotenv()

KEY = os.getenv("YOUTUBE_API_KEY")

def find_trailer(movie_title, year=None):
    query = f"{movie_title} {year} official trailer" if year else f"{movie_title} official trailer"
    r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
        "key": KEY, "q": query, "part": "snippet",
        "type": "video", "maxResults": 1,
        "order": "relevance"
    })
    items = r.json().get("items", [])
    if not items:
        return None
    return items[0]["id"]["videoId"]

def get_trailer_comments(video_id, max_comments=100):
    comments = []
    params = {
        "key": KEY, "videoId": video_id,
        "part": "snippet", "maxResults": 100,
        "order": "relevance", "textFormat": "plainText"
    }
    r = requests.get("https://www.googleapis.com/youtube/v3/commentThreads", params=params)
    for item in r.json().get("items", []):
        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        likes = item["snippet"]["topLevelComment"]["snippet"]["likeCount"]
        comments.append({"text": text, "likes": likes})
    return comments[:max_comments]

if __name__ == "__main__":
    vid_id = find_trailer("Minecraft Movie", 2025)
    print(f"Trailer video ID: {vid_id}")
    comments = get_trailer_comments(vid_id)
    print(f"Fetched {len(comments)} comments")
    print(f"Top comment: {comments[0]['text'][:100]}")
