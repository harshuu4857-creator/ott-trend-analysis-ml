import streamlit as st
import requests

# =========================
# 🔑 TMDB API KEY
# =========================
TMDB_API_KEY = "5609ab5a9c50d7e2e03b53ff1e36401a"

# =========================
# 🎬 Fetch Movie Data
# =========================
def fetch_movie(movie_name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        data = requests.get(url).json()

        if data["results"]:
            movie = data["results"][0]
            poster_path = movie["poster_path"]

            poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/300x450"

            return {
                "title": movie["title"],
                "rating": movie["vote_average"],
                "year": movie["release_date"][:4] if movie["release_date"] else "N/A",
                "poster": poster
            }
    except:
        pass

    return {
        "title": movie_name,
        "rating": "N/A",
        "year": "N/A",
        "poster": "https://via.placeholder.com/300x450"
    }


# =========================
# 🌐 PAGE CONFIG
# =========================
st.set_page_config(page_title="OTT Trend Analysis", layout="wide")

# =========================
# 🎨 CUSTOM CSS (Netflix Feel)
# =========================
st.markdown("""
    <style>
    body {
        background-color: #0b0c10;
        color: white;
    }
    .movie-card {
        background-color: #111;
        border-radius: 12px;
        padding: 10px;
        transition: transform 0.3s ease;
    }
    .movie-card:hover {
        transform: scale(1.05);
    }
    .movie-title {
        font-size: 16px;
        font-weight: bold;
        margin-top: 8px;
    }
    .movie-info {
        font-size: 13px;
        color: #bbb;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# 🎬 HEADER
# =========================
st.title("🔥 OTT Trend Analysis")
st.markdown("### Trending Movies")

# =========================
# 🎥 MOVIE LIST
# =========================
movies = [
    "Alias Grace",
    "Brave Miss World",
    "Power Rangers Beast Morphers",
    "One Punch Man",
    "Empire Games",
    "Cheer Squad",
    "Stranger Things",
    "Money Heist",
    "Breaking Bad"
]

# =========================
# 🎬 GRID DISPLAY (NETFLIX STYLE)
# =========================
cols = st.columns(5)

for i, movie in enumerate(movies):
    with cols[i % 5]:
        data = fetch_movie(movie)

        st.markdown('<div class="movie-card">', unsafe_allow_html=True)

        st.image(data["poster"], use_container_width=True)

        st.markdown(f'<div class="movie-title">{data["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="movie-info">⭐ {data["rating"]} | 📅 {data["year"]}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)