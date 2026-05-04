import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

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
# 📊 DATASET (for prediction)
# =========================
data = {
    "title": [
        "Alias Grace", "Brave Miss World", "Power Rangers Beast Morphers",
        "One Punch Man", "Empire Games", "Cheer Squad",
        "Stranger Things", "Money Heist", "Breaking Bad"
    ],
    "genre": [
        "Drama Crime", "Documentary", "Action Sci-Fi",
        "Action Anime", "History Drama", "Reality Show",
        "Sci-Fi Drama", "Crime Thriller", "Crime Drama"
    ]
}

df = pd.DataFrame(data)

# =========================
# 🤖 ML MODEL
# =========================
cv = CountVectorizer()
vectors = cv.fit_transform(df["genre"]).toarray()
similarity = cosine_similarity(vectors)

# =========================
# 🎯 Recommendation Function
# =========================
def recommend(movie):
    if movie not in df["title"].values:
        return []

    index = df[df["title"] == movie].index[0]
    distances = list(enumerate(similarity[index]))
    movies_list = sorted(distances, reverse=True, key=lambda x: x[1])[1:6]

    return [df.iloc[i[0]].title for i in movies_list]


# =========================
# 🌐 Streamlit UI
# =========================
st.set_page_config(page_title="OTT Trend Analysis", layout="wide")

st.title("🔥 OTT Trend Analysis Dashboard")
st.write("Trending Movies with Posters + Recommendation System")

# =========================
# 🎬 TRENDING SECTION (Your original)
# =========================
st.subheader("🎬 Trending Movies")

movies = df["title"].values

cols = st.columns(3)

for i, movie in enumerate(movies):
    with cols[i % 3]:
        poster = fetch_poster(movie)
        title, rating, year = fetch_details(movie)

        st.image(poster, use_container_width=True)
        st.markdown(f"**🎬 {title}**")
        st.write(f"⭐ Rating: {rating}")
        st.write(f"📅 Year: {year}")

# =========================
# 🎯 PREDICTION SECTION
# =========================
st.markdown("---")
st.subheader("🎯 Movie Recommendation (Prediction)")

selected_movie = st.selectbox("Select a movie", df["title"].values)

if st.button("Recommend"):
    recommendations = recommend(selected_movie)

    cols = st.columns(5)

    for i, movie in enumerate(recommendations):
        with cols[i]:
            poster = fetch_poster(movie)
            title, rating, year = fetch_details(movie)

            st.image(poster, use_container_width=True)
            st.caption(title)