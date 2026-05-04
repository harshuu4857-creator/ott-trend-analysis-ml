import streamlit as st
import requests

# =========================
# 🔑 TMDB API KEY
# =========================
TMDB_API_KEY = "5609ab5a9c50d7e2e03b53ff1e36401a"

# =========================
# 🎬 Fetch Movie Poster
# =========================
def fetch_poster(movie_name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        data = requests.get(url).json()

        if data["results"]:
            poster_path = data["results"][0]["poster_path"]
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
        
        return "https://via.placeholder.com/300x450?text=No+Image"

    except:
        return "https://via.placeholder.com/300x450?text=Error"


# =========================
# 🎥 Fetch Movie Details
# =========================
def fetch_details(movie_name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        data = requests.get(url).json()

        if data["results"]:
            movie = data["results"][0]
            title = movie["title"]
            rating = movie["vote_average"]
            release = movie["release_date"][:4] if movie["release_date"] else "N/A"

            return title, rating, release

        return movie_name, "N/A", "N/A"

    except:
        return movie_name, "N/A", "N/A"


# =========================
# 🌐 PAGE CONFIG
# =========================
st.set_page_config(page_title="OTT Trend Analysis", layout="wide")

# =========================
# 🎨 CLEAN UI STYLE
# =========================
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .movie-card {
        padding: 5px;
        border-radius: 10px;
        text-align: center;
    }
    .movie-title {
        font-size: 15px;
        font-weight: bold;
        margin-top: 5px;
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
st.title("🔥 OTT Trend Analysis Dashboard")
st.write("Trending Movies with Posters")

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
# 🎬 NETFLIX STYLE GRID
# =========================
num_cols = 5
for i in range(0, len(movies), num_cols):
    cols = st.columns(num_cols)

    for j in range(num_cols):
        if i + j < len(movies):
            movie = movies[i + j]

            with cols[j]:
                poster = fetch_poster(movie)
                title, rating, year = fetch_details(movie)

                st.image(poster, use_container_width=True)

                st.markdown(f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='movie-info'>⭐ {rating} | 📅 {year}</div>", unsafe_allow_html=True)