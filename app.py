import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Title
st.title("🎬 OTT Trend Analysis (Netflix Dataset)")

# Load dataset
df = pd.read_csv("netflix_titles.csv")

# Preprocessing (same as notebook)
df.fillna({
    'director': "Unknown",
    'cast': "Unknown",
    'country': "Unknown",
    'rating': "Unknown"
}, inplace=True)

df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['year_added'] = df['date_added'].dt.year
df['duration_num'] = df['duration'].str.extract(r'(\d+)').astype(float)

# Sidebar
st.sidebar.header("Filters")

content_type = st.sidebar.selectbox("Select Type", df['type'].unique())
year = st.sidebar.slider("Select Release Year", int(df['release_year'].min()), int(df['release_year'].max()))

# Filter data
filtered_df = df[(df['type'] == content_type) & (df['release_year'] >= year)]

# Show data
st.subheader("Filtered Data")
st.write(filtered_df.head())

# Charts
st.subheader("Content Distribution")

type_count = df['type'].value_counts()
st.bar_chart(type_count)

# Year trend
st.subheader("Content Added Over Years")
year_trend = df['year_added'].value_counts().sort_index()
st.line_chart(year_trend)

# Top countries
st.subheader("Top Countries")
top_countries = df['country'].value_counts().head(10)
st.bar_chart(top_countries)

# Prediction section
st.subheader("🎯 Predict Content Type")

try:
    model = joblib.load("model.pkl")

    release_year = st.number_input("Release Year", 2000, 2025)
    duration = st.number_input("Duration", 1, 300)
    rating = st.selectbox("Rating", df['rating'].unique())

    # Encode rating
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    df['rating_encoded'] = le.fit_transform(df['rating'])
    rating_encoded = le.transform([rating])[0]

    if st.button("Predict"):
        prediction = model.predict([[release_year, duration, rating_encoded]])

        if prediction[0] == 0:
            st.success("🎬 Movie")
        else:
            st.success("📺 TV Show")

except:
    st.warning("Model not found. Please run notebook and save model.pkl")