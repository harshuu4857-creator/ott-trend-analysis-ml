import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="OTT Intelligence Dashboard", layout="wide")

# ------------------ HEADER ------------------
st.title("🎬 OTT Content Intelligence Dashboard")
st.markdown("Explore trends, insights and smart recommendations")

# ------------------ LOAD DATA ------------------
df = pd.read_csv("netflix_titles.csv")

# ------------------ PREPROCESSING ------------------
df.fillna({
    'director': "Unknown",
    'cast': "Unknown",
    'country': "Unknown",
    'rating': "Unknown"
}, inplace=True)

df['duration_num'] = df['duration'].str.extract(r'(\d+)').astype(float)

# ------------------ POSTERS (Dummy) ------------------
df["poster"] = df["title"].apply(
    lambda x: f"https://dummyimage.com/300x450/1E293B/ffffff&text={x[:15].replace(' ', '+')}"
)

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

# ------------------ POSTER FUNCTION (FIXED) ------------------
def show_posters(data):
    cols = st.columns(5)

    for i, row in data.iterrows():
        with cols[i % 5]:

            # Poster
            st.image(row["poster"], use_container_width=True)

            # Title
            st.markdown(f"**{row['title'][:25]}**")

            # 👉 ONLY DIRECTOR NAME (as you asked)
            st.caption(f"🎬 {row['director']}")

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Recommendation", "📌 Insights"])

# ================== DASHBOARD ==================
with tab1:

    st.subheader("📊 Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Content", len(filtered_df))
    col2.metric("Countries", filtered_df['country'].nunique())
    col3.metric("Genres", filtered_df['listed_in'].nunique())

    avg = filtered_df["duration_num"].mean()
    avg = 0 if pd.isna(avg) else int(avg)

    col4.metric("Avg Duration", avg)

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
    st.write("Filter content based on preferences")

    col1, col2, col3 = st.columns(3)

    release_year = col1.slider(
        "Release Year",
        int(df['release_year'].min()),
        int(df['release_year'].max()),
        2018
    )

    content_type = col2.selectbox(
        "Content Type",
        ["Movie", "TV Show"]
    )

    genre_list = sorted(set(df['listed_in'].str.split(', ').sum()))
    genre = col3.selectbox("Genre", genre_list)

    if st.button("🔍 Get Recommendations"):

        filtered = df.copy()

        # Year filter
        filtered = filtered[
            (filtered['release_year'] >= release_year - 2) &
            (filtered['release_year'] <= release_year + 2)
        ]

        # Type filter
        filtered = filtered[filtered['type'] == content_type]

        # Genre filter
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