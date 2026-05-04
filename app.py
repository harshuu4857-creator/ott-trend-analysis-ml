import streamlit as st
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# =========================
# 🔑 TMDB API KEY
# =========================
TMDB_API_KEY = "YOUR_TMDB_API_KEY"

# =========================
# 🎬 Fetch Poster
# =========================
def fetch_poster(movie_name):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        data = requests.get(url).json()

        if data["results"]:
            poster_path = data["results"][0]["poster_path"]
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
        
        return "https://via.placeholder.com/300x450"
    except:
        return "https://via.placeholder.com/300x450"


# =========================
# 📊 SAMPLE DATASET
# =========================
data = {
    "title": [
        "Inception", "Interstellar", "The Dark Knight", "Tenet",
        "Avengers", "Iron Man", "Thor", "Captain America"
    ],
    "genre": [
        "Sci-Fi Action", "Sci-Fi Drama", "Action Crime", "Sci-Fi Thriller",
        "Action Superhero", "Action Superhero", "Action Fantasy", "Action Superhero"
    ]
}

df = pd.DataFrame(data)

# =========================
# 🤖 ML MODEL (Similarity)
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

    recommended = [df.iloc[i[0]].title for i in movies_list]
    return recommended


# =========================
# 🌐 UI
# =========================
st.set_page_config(layout="wide")
st.title("🎬 Netflix Style Movie Recommender")

# Dropdown for movie selection
selected_movie = st.selectbox("Select a movie", df["title"].values)

if st.button("Recommend"):
    recommendations = recommend(selected_movie)

    if recommendations:
        cols = st.columns(5)

        for i, movie in enumerate(recommendations):
            with cols[i]:
                st.image(fetch_poster(movie), use_container_width=True)
                st.caption(movie)
    else:
        st.write("Movie not found")