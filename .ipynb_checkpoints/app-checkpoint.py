import streamlit as st
import pandas as pd
import plotly.express as px
import joblib

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="OTT AI Dashboard", layout="wide")

# ------------------ TITLE ------------------
st.markdown("## 🎬 AI-Powered OTT Content Intelligence Dashboard")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("netflix_titles.csv")

# ------------------ PREPROCESSING ------------------
df.fillna({
    'director': "Unknown",
    'cast': "Unknown",
    'country': "Unknown",
    'rating': "Unknown"
}, inplace=True)

df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['year_added'] = df['date_added'].dt.year
df['duration_num'] = df['duration'].str.extract(r'(\d+)').astype(float)

# ------------------ SIDEBAR ------------------
st.sidebar.header("🎯 Filters")

content_type = st.sidebar.selectbox("Select Type", df['type'].unique())

year_range = st.sidebar.slider(
    "Select Release Year",
    int(df['release_year'].min()),
    int(df['release_year'].max()),
    (2000, 2020)
)

# ------------------ FILTER DATA ------------------
filtered_df = df[
    (df['type'] == content_type) &
    (df['release_year'].between(year_range[0], year_range[1]))
]

# ------------------ KPI CARDS ------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("🎬 Total Content", len(filtered_df))
col2.metric("🌍 Countries", filtered_df['country'].nunique())
col3.metric("🎭 Genres", filtered_df['listed_in'].nunique())
col4.metric("⏱ Avg Duration", int(filtered_df['duration_num'].mean()))

st.markdown("---")

# ------------------ CHARTS ROW 1 ------------------
col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        filtered_df,
        x='type',
        color='type',
        title="Content Distribution",
        color_discrete_sequence=['#38BDF8']
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.pie(
        filtered_df,
        names='rating',
        title="Rating Distribution"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ------------------ CHARTS ROW 2 ------------------
col1, col2 = st.columns(2)

with col1:
    year_trend = filtered_df['release_year'].value_counts().sort_index()
    fig3 = px.line(
        x=year_trend.index,
        y=year_trend.values,
        title="Content Growth Over Time"
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    top_countries = filtered_df['country'].value_counts().head(10)
    fig4 = px.bar(
        x=top_countries.values,
        y=top_countries.index,
        orientation='h',
        title="Top Countries",
        color=top_countries.values,
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ------------------ DATA TABLE ------------------
st.subheader("📊 Filtered Data Preview")
st.dataframe(filtered_df.head(10))

# ------------------ PREDICTION SECTION ------------------
st.markdown("## 🎯 Content Type Prediction")

try:
    model = joblib.load("model.pkl")

    col1, col2, col3 = st.columns(3)

    release_year = col1.number_input("Release Year", 2000, 2025)
    duration = col2.number_input("Duration", 1, 300)
    rating = col3.selectbox("Rating", df['rating'].unique())

    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    df['rating_encoded'] = le.fit_transform(df['rating'])
    rating_encoded = le.transform([rating])[0]

    if st.button("🚀 Predict"):
        prediction = model.predict([[release_year, duration, rating_encoded]])

        if prediction[0] == 0:
            st.success("🎬 Predicted: Movie")
        else:
            st.success("📺 Predicted: TV Show")

except:
    st.warning("⚠️ Model not found. Please save model.pkl")