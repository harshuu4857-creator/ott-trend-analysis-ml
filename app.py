import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from functools import lru_cache

# ------------------ CONFIG ------------------
st.set_page_config(page_title="OTT Intelligence Dashboard", layout="wide")

TMDB_API_KEY = "YOUR_TMDB_API_KEY"  # 🔥 PUT YOUR KEY HERE
IMG_BASE = "https://image.tmdb.org/t/p/w500"

# ------------------ HEADER ------------------
st.title("🎬 OTT Content Intelligence Dashboard")
st.markdown("Explore trends, insights and smart recommendations")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    return pd.read_csv("netflix_titles.csv")

df = load_data()

# ------------------ PREPROCESS ------------------
df.fillna({
    'director': "Unknown",
    'country': "Unknown",
    'rating': "Unknown"
}, inplace=True)

df['duration_num'] = df['duration'].str.extract(r'(\d+)').astype(float)

# ------------------ TMDB POSTER ------------------
@lru_cache(maxsize=1000)
def get_poster_tmdb(title):
    try:
        title_clean = title.split(":")[0]

        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title_clean}"
        response = requests.get(url).json()

        if response["results"]:
            poster_path = response["results"][0]["poster_path"]

            if poster_path:
                return IMG_BASE + poster_path

        return "https://via.placeholder.com/300x450?text=No+Poster"

    except:
        return "https://via.placeholder.com/300x450?text=Error"

# ------------------ POSTER GRID ------------------
def show_posters(data):
    cols = st.columns(5)

    for i, row in data.iterrows():
        col = cols[i % 5]

        with col:
            poster = get_poster_tmdb(row['title'])

            st.image(poster, use_container_width=True)

            st.markdown(
                f"<div style='text-align:center; font-size:14px; font-weight:600;'>"
                f"{row['title'][:25]}</div>",
                unsafe_allow_html=True
            )

            st.caption(f"🎬 {row['director']}")

# ------------------ SIDEBAR ------------------
st.sidebar.header("🎯 Filters")

content_type_filter = st.sidebar.selectbox("Content Type", ["Movie", "TV Show"])

year_range = st.sidebar.slider(
    "Release Year",
    int(df['release_year'].min()),
    int(df['release_year'].max()),
    (2010, 2020)
)

filtered_df = df[
    (df['type'] == content_type_filter) &
    (df['release_year'].between(year_range[0], year_range[1]))
]

# ------------------ SEARCH ------------------
search = st.text_input("🔍 Search Content")

if search:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search, case=False, na=False)
    ]

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Recommendation", "📌 Insights"])

# ================== DASHBOARD ==================
with tab1:

    st.subheader("📊 Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Content", len(filtered_df))
    c2.metric("Countries", filtered_df['country'].nunique())
    c3.metric("Genres", filtered_df['listed_in'].nunique())

    avg = filtered_df["duration_num"].mean()
    avg = 0 if pd.isna(avg) else int(avg)
    c4.metric("Avg Duration", avg)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(filtered_df, x='type', title="Content Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(filtered_df, names='rating', title="Ratings")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🔥 Trending Content")

    if len(filtered_df) > 0:
        show_posters(filtered_df.sample(min(10, len(filtered_df))))

# ================== RECOMMENDATION ==================
with tab2:

    st.subheader("🎯 Smart Recommendation System")

    col1, col2, col3 = st.columns(3)

    release_year = col1.slider(
        "Release Year",
        int(df['release_year'].min()),
        int(df['release_year'].max()),
        2018
    )

    content_type = col2.selectbox("Content Type", ["Movie", "TV Show"])

    genre_list = sorted(set(df['listed_in'].str.split(', ').sum()))
    genre = col3.selectbox("Genre", genre_list)

    if st.button("🔍 Get Recommendations"):

        filtered = df.copy()

        filtered = filtered[
            (filtered['release_year'] >= release_year - 2) &
            (filtered['release_year'] <= release_year + 2)
        ]

        filtered = filtered[filtered['type'] == content_type]

        filtered = filtered[
            filtered['listed_in'].str.contains(genre, case=False, na=False)
        ]

        st.subheader("🎬 Recommended Content")

        if len(filtered) == 0:
            st.warning("No matching content found")
        else:
            filtered = filtered.sort_values(by="release_year", ascending=False).head(10)
            show_posters(filtered)

# ================== INSIGHTS ==================
with tab3:

    st.subheader("📌 Key Insights")

    st.markdown("""
    - OTT content is growing rapidly  
    - Movies dominate the platform  
    - USA and India are top producers  
    - Drama & Comedy are most popular genres  
    """)

    st.subheader("💡 Business Recommendations")

    st.markdown("""
    - Invest in trending genres  
    - Focus on high-demand regions  
    - Optimize content duration  
    - Produce recent and engaging content  
    """)