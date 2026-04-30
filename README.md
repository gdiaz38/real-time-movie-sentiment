# 🎬 Real-Time Movie Sentiment Tracker

A fully automated pipeline that tracks audience vs critic sentiment for currently playing films — refreshed daily with no manual intervention.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-live-FF4B4B?logo=streamlit)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-automated-2088FF?logo=githubactions)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📊 Live Dashboard

👉 **[View Live App](https://gdiaz38-real-time-movie-sentiment.streamlit.app)**

---

## Overview

Most movie score trackers are static snapshots. This project pulls **live data every day** from three sources, runs sentiment analysis on real audience comments, and surfaces the gap between what critics say and what audiences actually feel.

Key question it answers: *Are critics and audiences watching the same movie?*

---

## Features

- **Daily automated refresh** via GitHub Actions cron — zero manual work after deployment
- **Critic vs audience divergence** scored across TMDB, RT, IMDB, and Metacritic
- **YouTube trailer comment sentiment** analyzed with TextBlob across up to 100 comments per film
- **Box office correlation** — does audience positivity predict revenue?
- **Live search and filtering** by title, score threshold, data availability
- **Movie detail card** with plain-English verdict on critic/audience alignment

---

## Data Sources

| Source | Data | Update Frequency |
|---|---|---|
| [TMDB API](https://www.themoviedb.org/documentation/api) | Now-playing films, ratings, vote counts, reviews | Daily |
| [OMDb API](https://www.omdbapi.com/) | Rotten Tomatoes %, Metacritic, IMDB rating, box office | Daily |
| [YouTube Data API v3](https://developers.google.com/youtube/v3) | Trailer comments for audience sentiment | Daily |

---

## Project Structure

```
real-time-movie-sentiment/
├── .github/
│   └── workflows/
│       └── refresh.yml        # Daily cron — runs pipeline, commits CSV
├── app/
│   └── dashboard.py           # Streamlit dashboard
├── scripts/
│   ├── fetch_tmdb.py          # TMDB now-playing + reviews
│   ├── fetch_omdb.py          # OMDb critic scores + box office
│   ├── fetch_youtube.py       # YouTube trailer search + comments
│   ├── sentiment.py           # TextBlob sentiment scoring
│   └── pipeline.py            # Orchestrates all scripts → data/movies.csv
├── data/
│   └── movies.csv             # Auto-generated, committed by Actions
├── requirements.txt
└── .env                       # API keys — never committed
```

---

## How It Works

```
GitHub Actions (cron: daily noon UTC)
        ↓
pipeline.py fetches ~40 now-playing films from TMDB
        ↓
For each film:
  ├── OMDb  → RT score, Metacritic, IMDB rating, box office
  └── YouTube → find trailer → pull 100 comments → TextBlob sentiment
        ↓
Writes data/movies.csv → commits → pushes to main
        ↓
Streamlit Community Cloud detects push → auto-redeploys
```

---

## Dashboard Sections

**KPI Row** — highest audience sentiment, highest RT score, biggest critic/audience gap, top box office

**Audience vs Critic Scatter** — each bubble is a film; size = vote count; color = divergence; dashed line = perfect agreement

**Divergence Bar Chart** — top 12 films where audiences and critics disagree most

**Score Breakdown** — grouped bar comparing TMDB, IMDB, RT, Metacritic, and audience sentiment side by side

**Box Office vs Sentiment** — does being audience-loved translate to revenue?

**Search & Filter** — live title search, min score filter, toggles for RT-only and sentiment-only films

**Movie Detail Card** — pick any film for a full score breakdown and a plain-English critic/audience verdict

---

## Local Setup

### 1. Clone and create environment

```bash
git clone https://github.com/gdiaz38/real-time-movie-sentiment
cd real-time-movie-sentiment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Get free API keys

| Key | Where |
|---|---|
| TMDB | [themoviedb.org](https://www.themoviedb.org/settings/api) → Request API Key |
| OMDb | [omdbapi.com](https://www.omdbapi.com/apikey.aspx) → Free tier |
| YouTube | [console.cloud.google.com](https://console.cloud.google.com) → YouTube Data API v3 |

### 3. Create `.env`

```bash
TMDB_API_KEY=your_key
OMDB_API_KEY=your_key
YOUTUBE_API_KEY=your_key
```

### 4. Run pipeline and launch dashboard

```bash
cd scripts && python3 pipeline.py
cd ..
streamlit run app/dashboard.py
```

---

## Deployment

### GitHub Actions (auto-refresh)

Secrets required in your repo settings (`Settings → Secrets → Actions`):

```
TMDB_API_KEY
OMDB_API_KEY
YOUTUBE_API_KEY
```

The workflow runs daily at noon UTC, commits the refreshed CSV, and pushes to main.

### Streamlit Community Cloud

1. Connect repo at [share.streamlit.io](https://share.streamlit.io)
2. Set main file to `app/dashboard.py`
3. Add the same API keys under Advanced Settings → Secrets
4. Deploy — app auto-redeploys on every push from Actions

---

## Sample Output

| Title | TMDB | RT | Audience +% | Gap |
|---|---|---|---|---|
| Project Hail Mary | 8.2 | 94% | 59% | −9.4 |
| Demon Slayer: Infinity Castle | 7.7 | 98% | 47% | −21.8 |
| Hoppers | 7.7 | 94% | 48% | −18.4 |
| GOAT | 7.9 | 85% | 45% | −17.0 |
| Scream 7 | 6.1 | 30% | N/A | N/A |

---

## Tech Stack

`Python 3.11` · `Streamlit` · `Plotly` · `Pandas` · `TextBlob` · `GitHub Actions` · `TMDB API` · `OMDb API` · `YouTube Data API v3`

---

## Affiliation

University of California, Riverside — MS in Engineering Management  
Part of a portfolio of 10 live data science projects spanning computer vision, NLP, supply chain, and healthcare ML.

---

## License

MIT
