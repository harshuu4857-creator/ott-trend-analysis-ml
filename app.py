import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="OTT Intelligence Dashboard", layout="wide")

# ------------------ CUSTOM CSS ------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0F172A;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #1E293B);
}
.card {
    background-color: #1E293B;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}
img:hover {
    transform: scale(1.05);
    transition: 0.3s;
}
h1, h2, h3, h4 {
    color: #E2E8F0;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("# 🎬 OTT Content Intelligence Dashboard")
st.markdown("### Explore trends, insights and smart recommendations")

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

# ------------------ POSTERS ------------------
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

# ------------------ POSTER FUNCTION (UPDATED) ------------------
def show_posters(data):
    cols = st.columns(5)

    for i, row in data.iterrows():
        with cols[i % 5]:
            st.markdown(f"""
            <div style="text-align:center;">
                <img src="{row['poster']}" 
                     style="width:100%; height:260px; object-fit:cover; border-radius:10px;">

                <p style="color:white; font-weight:bold;">
                    {row['title'][:25]}
                </p>

                <p style="color:#9CA3AF; font-size:12px;">
                    🎬 {row['director'][:25]}
                </p>

                <p style="color:#9CA3AF; font-size:12px;">
                    ⭐ {row['rating']} | 📅 {row['release_year']}
                </p>
            </div>
            """, unsafe_allow_html=True)

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Recommendation", "📌 Insights"])

# ================== DASHBOARD ==================
with tab1:

    st.markdown("## 📊 Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="card"><h4>Total Content</h4><h2>{len(filtered_df)}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card"><h4>Countries</h4><h2>{filtered_df["country"].nunique()}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card"><h4>Genres</h4><h2>{filtered_df["listed_in"].nunique()}</h2></div>', unsafe_allow_html=True)

    avg = filtered_df["duration_num"].mean()
    avg = 0 if pd.isna(avg) else int(avg)

    col4.markdown(f'<div class="card"><h4>Avg Duration</h4><h2>{avg}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(filtered_df, x='type', title="Content Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(filtered_df, names='rating', title="Ratings")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## 🔥 Trending Content")

    if len(filtered_df) > 0:
        show_posters(filtered_df.sample(min(10, len(filtered_df))))

# ================== RECOMMENDATION ==================
with tab2:

    st.markdown("## 🎯 Smart Recommendation System")
    st.markdown("Filter content based on preferences")

    # 👉 NOW ONLY 3 COLUMNS (Country removed)
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

        st.markdown("### 🎬 Recommended Content")

        if len(filtered) == 0:
            st.warning("No matching content found")
        else:
            filtered = filtered.sort_values(by="release_year", ascending=False).head(10)
            show_posters(filtered)

# ================== INSIGHTS ==================
with tab3:

    st.markdown("## 📌 Key Insights")

    st.markdown("""
    - OTT content is growing rapidly  
    - Movies dominate the platform  
    - USA and India are top producers  
    - Drama & Comedy are most popular genres  
    """)

    st.markdown("## 💡 Business Recommendations")

    st.markdown("""
    - Invest in trending genres  
    - Focus on high-demand regions  
    - Optimize content duration  
    - Produce recent and engaging content  
    """)