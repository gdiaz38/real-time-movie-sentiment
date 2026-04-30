import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Movie Sentiment Tracker",
    page_icon="🎬",
    layout="wide"
)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv("data/movies.csv")

    df["rt_numeric"] = (
        df["rt_score"]
        .str.replace("%", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )
    df["meta_numeric"] = (
        df["metacritic"]
        .str.split("/").str[0]
        .pipe(pd.to_numeric, errors="coerce")
    )
    df["imdb_numeric"] = pd.to_numeric(df["imdb_rating"], errors="coerce")
    df["tmdb_100"]     = df["tmdb_score"] * 10
    df["imdb_100"]     = df["imdb_numeric"] * 10
    df["critic_score"] = df[["rt_numeric","meta_numeric","tmdb_100","imdb_100"]].mean(axis=1)
    df["divergence"]   = df["audience_positive"] - df["critic_score"]
    df["bo_clean"] = (
        df["box_office"]
        .str.replace(r"[\$,]", "", regex=True)
        .pipe(pd.to_numeric, errors="coerce")
        .div(1_000_000)
    )
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    # Drop placeholder/unreleased entries
    df = df[df["tmdb_score"] > 0]

    return df.sort_values("tmdb_votes", ascending=False)

df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎬 Real-Time Movie Sentiment Tracker")
st.caption(f"Last refreshed: {df['fetched_at'].max()} UTC  •  {len(df)} movies tracked")

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

top_audience = df.loc[df["audience_positive"].idxmax(), "title"]  if df["audience_positive"].notna().any() else "N/A"
top_critic   = df.loc[df["rt_numeric"].idxmax(),        "title"]  if df["rt_numeric"].notna().any()        else "N/A"
biggest_gap  = df.loc[df["divergence"].abs().idxmax(),  "title"]  if df["divergence"].notna().any()        else "N/A"
top_bo       = df.loc[df["bo_clean"].idxmax(),          "title"]  if df["bo_clean"].notna().any()          else "N/A"

k1.metric("🏆 Highest Audience Sentiment",  top_audience,
          f"{df['audience_positive'].max():.1f}% positive" if df["audience_positive"].notna().any() else "")
k2.metric("🍅 Highest RT Score",            top_critic,
          f"{df['rt_numeric'].max():.0f}%"  if df["rt_numeric"].notna().any()                       else "")
k3.metric("⚡ Biggest Critic/Audience Gap", biggest_gap,
          f"{df['divergence'].abs().max():.1f} pts" if df["divergence"].notna().any()               else "")
k4.metric("💰 Top Box Office",              top_bo,
          f"${df['bo_clean'].max():.1f}M"   if df["bo_clean"].notna().any()                         else "")

st.divider()

# ── Row 1: Scatter + Divergence bar ───────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Audience vs Critic Score")
    plot_df = df.dropna(subset=["critic_score", "audience_positive"]).head(25)
    if not plot_df.empty:
        fig = px.scatter(
            plot_df,
            x="critic_score", y="audience_positive",
            text="title", size="tmdb_votes",
            color="divergence", color_continuous_scale="RdYlGn",
            labels={
                "critic_score":      "Critic Score (0–100)",
                "audience_positive": "Audience Positive %",
                "divergence":        "Audience − Critic"
            },
            hover_data=["rt_score", "imdb_rating", "box_office"]
        )
        fig.add_shape(type="line", x0=0, y0=0, x1=100, y1=100,
                      line=dict(dash="dash", color="gray", width=1))
        fig.add_annotation(x=75, y=78, text="Perfect agreement line",
                           showarrow=False, font=dict(color="gray", size=10))
        fig.update_traces(textposition="top center", textfont_size=9)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data with both critic and audience scores yet.")

with col2:
    st.subheader("Critic vs Audience Divergence")
    div_df = df.dropna(subset=["divergence"]).nlargest(12, "divergence")
    if not div_df.empty:
        fig2 = px.bar(
            div_df, x="divergence", y="title", orientation="h",
            color="divergence", color_continuous_scale="RdYlGn",
            labels={"divergence": "Audience − Critic Score", "title": ""}
        )
        fig2.update_layout(height=420, showlegend=False, coloraxis_showscale=False,
                           yaxis=dict(tickfont=dict(size=10)))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Not enough divergence data yet.")

# ── Row 2: Multi-score comparison + Box office ────────────────────────────────
col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("Score Breakdown by Source")
    top15 = df.dropna(subset=["tmdb_score"]).head(15)
    fig3  = go.Figure()
    sources = {
        "TMDB (×10)":    ("tmdb_100",          "#00B4D8"),
        "IMDB (×10)":    ("imdb_100",           "#F77F00"),
        "RT Score":      ("rt_numeric",         "#E63946"),
        "Metacritic":    ("meta_numeric",        "#2DC653"),
        "Audience Pos%": ("audience_positive",   "#9B5DE5"),
    }
    for label, (c, color) in sources.items():
        mask = top15[c].notna()
        fig3.add_trace(go.Bar(
            name=label,
            x=top15.loc[mask, "title"],
            y=top15.loc[mask, c],
            marker_color=color
        ))
    fig3.update_layout(
        barmode="group", height=380,
        xaxis_tickangle=-35, xaxis_tickfont=dict(size=9),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Box Office vs Audience Sentiment")
    bo_df = df.dropna(subset=["bo_clean", "audience_positive"])
    if not bo_df.empty:
        fig4 = px.scatter(
            bo_df,
            x="audience_positive", y="bo_clean",
            text="title", color="rt_numeric",
            color_continuous_scale="RdYlGn",
            labels={
                "audience_positive": "Audience Positive %",
                "bo_clean":          "Box Office ($M)",
                "rt_numeric":        "RT Score"
            }
        )
        fig4.update_traces(textposition="top center", textfont_size=8)
        fig4.update_layout(height=380)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Box office data not yet available for current films.")

# ── Row 3: Sentiment sample size + release timeline ───────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Audience Sentiment Sample Size")
    samp_df = df.dropna(subset=["audience_samples"]).nlargest(15, "audience_samples")
    if not samp_df.empty:
        fig5 = px.bar(
            samp_df, x="title", y="audience_samples",
            color="audience_positive", color_continuous_scale="Blues",
            labels={"audience_samples": "YouTube Comments Analyzed", "title": ""}
        )
        fig5.update_layout(height=340, xaxis_tickangle=-35, xaxis_tickfont=dict(size=9))
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No audience sample data yet.")

with col6:
    st.subheader("Release Timeline — TMDB Score")
    time_df = df.dropna(subset=["release_date", "tmdb_score"]).sort_values("release_date")
    if not time_df.empty:
        fig6 = px.scatter(
            time_df,
            x="release_date", y="tmdb_score",
            size="tmdb_votes", color="audience_positive",
            color_continuous_scale="RdYlGn", hover_name="title",
            labels={"release_date": "Release Date", "tmdb_score": "TMDB Score"}
        )
        fig6.update_layout(height=340)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Not enough release date data.")

st.divider()

# ── Search & Filter ───────────────────────────────────────────────────────────
st.subheader("🔍 Search & Filter Movies")

search_col, filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1, 1])

with search_col:
    search_query = st.text_input(
        "Search by title",
        placeholder="e.g. Minecraft, Demon Slayer, Scream...",
        label_visibility="collapsed"
    )
with filter_col1:
    min_tmdb = st.number_input("Min TMDB Score", 0.0, 10.0, 1.0, step=0.5,
                               help="Filters out unreleased/placeholder entries")
with filter_col2:
    has_rt        = st.checkbox("Has RT Score",      value=False)
with filter_col3:
    has_sentiment = st.checkbox("Has Audience Data", value=False)

filtered_df = df.copy()
if search_query:
    filtered_df = filtered_df[filtered_df["title"].str.contains(search_query, case=False, na=False)]
if min_tmdb > 0:
    filtered_df = filtered_df[filtered_df["tmdb_score"] >= min_tmdb]
if has_rt:
    filtered_df = filtered_df[filtered_df["rt_numeric"].notna()]
if has_sentiment:
    filtered_df = filtered_df[filtered_df["audience_positive"].notna()]

st.caption(f"Showing {len(filtered_df)} of {len(df)} movies")

# ── Data table ────────────────────────────────────────────────────────────────
st.subheader("📋 Full Movie Data")

display_cols = {
    "title":             "Title",
    "release_date":      "Release",
    "tmdb_score":        "TMDB",
    "rt_score":          "RT",
    "imdb_rating":       "IMDB",
    "metacritic":        "Metacritic",
    "audience_positive": "Audience +%",
    "divergence":        "Gap",
    "box_office":        "Box Office",
    "audience_samples":  "YT Samples",
}

show_df = (
    filtered_df[list(display_cols.keys())]
    .rename(columns=display_cols)
    .reset_index(drop=True)
)

def color_divergence(val):
    if pd.isna(val): return ""
    if val > 10:     return "color: green"
    if val < -10:    return "color: red"
    return "color: orange"

def color_score(val):
    if pd.isna(val): return ""
    try:
        v = float(str(val).replace("%", "").split("/")[0])
        if v >= 75: return "background-color: #1a472a; color: white"
        if v >= 50: return "background-color: #856404; color: white"
        return              "background-color: #6b1a1a; color: white"
    except:
        return ""

st.dataframe(
    show_df.style
        .applymap(color_divergence, subset=["Gap"])
        .applymap(color_score,      subset=["RT"]),
    use_container_width=True,
    height=450
)

# ── Movie detail card ─────────────────────────────────────────────────────────
st.subheader("🎥 Movie Detail")

if not filtered_df.empty:
    selected_title = st.selectbox(
        "Pick a movie for full breakdown",
        options=filtered_df["title"].tolist(),
        index=0
    )

    row = filtered_df[filtered_df["title"] == selected_title].iloc[0]

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("TMDB",        f"{row['tmdb_score']:.1f}/10"        if pd.notna(row['tmdb_score'])        else "N/A")
    d2.metric("RT",          row['rt_score']                       if pd.notna(row['rt_score'])          else "N/A")
    d3.metric("IMDB",        row['imdb_rating']                    if pd.notna(row['imdb_rating'])       else "N/A")
    d4.metric("Metacritic",  row['metacritic']                     if pd.notna(row['metacritic'])        else "N/A")
    d5.metric("Audience +%", f"{row['audience_positive']:.1f}%"   if pd.notna(row['audience_positive']) else "N/A")

    if pd.notna(row.get("divergence")):
        gap = row["divergence"]
        if gap > 5:
            st.success(f"📈 Audiences like this **{gap:.1f} pts more** than critics")
        elif gap < -5:
            st.error(f"📉 Critics like this **{abs(gap):.1f} pts more** than audiences")
        else:
            st.info("⚖️ Critics and audiences are roughly aligned on this film")

    if pd.notna(row.get("box_office")):
        st.write(f"💰 **Box Office:** {row['box_office']}")
else:
    st.info("No movies match your current filters.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📊 Dashboard Info")
    st.markdown(f"**Movies tracked:** {len(df)}")
    st.markdown(f"**With RT scores:** {df['rt_numeric'].notna().sum()}")
    st.markdown(f"**With audience data:** {df['audience_positive'].notna().sum()}")
    st.markdown(f"**Last updated:** {df['fetched_at'].max()}")
    st.markdown("---")
    st.markdown("**Data Sources**")
    st.markdown("- 🎬 TMDB — ratings & reviews")
    st.markdown("- 🍅 OMDb — RT & Metacritic")
    st.markdown("- 📺 YouTube — trailer comments")
    st.markdown("---")
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()