import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="OTT AI Dashboard", layout="wide")

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
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}
img:hover {
    transform: scale(1.05);
}
h1, h2, h3, h4 {
    color: #E2E8F0;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE ------------------
st.markdown("# 🎬 OTT Content Intelligence Dashboard")

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

# ------------------ DYNAMIC POSTERS ------------------
df["poster"] = df["title"].apply(
    lambda x: f"https://dummyimage.com/300x450/1E293B/ffffff&text={x[:15].replace(' ', '+')}"
)

# ------------------ RECOMMENDATION SYSTEM ------------------
df['combined'] = df['listed_in'] + " " + df['description']

cv = CountVectorizer(stop_words='english')
matrix = cv.fit_transform(df['combined'])
similarity = cosine_similarity(matrix)

def recommend(title):
    title = title.lower()

    if title not in df['title'].str.lower().values:
        return []

    idx = df[df['title'].str.lower() == title].index[0]

    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recs = []
    for i in scores[1:6]:
        recs.append(df.iloc[i[0]])
    return recs

# ------------------ SIDEBAR ------------------
st.sidebar.header("🎯 Filters")

content_type = st.sidebar.selectbox("Content Type", df['type'].unique())

year_range = st.sidebar.slider(
    "Release Year",
    int(df['release_year'].min()),
    int(df['release_year'].max()),
    (2000, 2020)
)

filtered_df = df[
    (df['type'] == content_type) &
    (df['release_year'].between(year_range[0], year_range[1]))
]

# ------------------ SEARCH ------------------
search = st.text_input("🔍 Search Content")

if search:
    temp = filtered_df[
        filtered_df['title'].str.contains(search, case=False, na=False)
    ]
    if len(temp) > 0:
        filtered_df = temp

# ------------------ POSTER FUNCTION ------------------
def show_posters(data):
    cols = st.columns(5)
    for i, row in data.iterrows():
        with cols[i % 5]:
            st.markdown(f"""
            <div style="text-align:center;">
                <img src="{row['poster']}" 
                     style="width:100%; height:260px; object-fit:cover; border-radius:10px;">
                <p style="color:white;">{row['title'][:25]}</p>
            </div>
            """, unsafe_allow_html=True)

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎯 Recommend", "📌 Insights"])

# ================== DASHBOARD ==================
with tab1:

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="card"><h4>Total</h4><h2>{len(filtered_df)}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card"><h4>Countries</h4><h2>{filtered_df["country"].nunique()}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card"><h4>Genres</h4><h2>{filtered_df["listed_in"].nunique()}</h2></div>', unsafe_allow_html=True)

    avg = filtered_df["duration_num"].mean()
    avg = 0 if pd.isna(avg) else int(avg)

    col4.markdown(f'<div class="card"><h4>Avg Duration</h4><h2>{avg}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Charts
    fig1 = px.bar(filtered_df, x='type', title="Content Type")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.pie(filtered_df, names='rating', title="Ratings")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("## 🔥 Trending")
    if len(filtered_df) > 0:
        show_posters(filtered_df.sample(min(10, len(filtered_df))))

# ================== RECOMMEND ==================
with tab2:

    st.markdown("## 🎯 Content Recommendation")

    user_input = st.text_input("Enter Movie/Show Name")

    if st.button("Recommend"):

        recs = recommend(user_input)

        if len(recs) == 0:
            st.warning("❌ Title not found")
        else:
            cols = st.columns(5)

            for i, row in enumerate(recs):
                with cols[i % 5]:
                    st.markdown(f"""
                    <div style="text-align:center;">
                        <img src="{row['poster']}" 
                             style="width:100%; height:260px; border-radius:10px;">
                        <p style="color:white;">{row['title']}</p>
                    </div>
                    """, unsafe_allow_html=True)

# ================== INSIGHTS ==================
with tab3:

    st.markdown("## 📌 Insights")

    st.markdown("""
    - OTT content is growing rapidly  
    - Movies dominate over TV Shows  
    - USA & India produce most content  
    """)

    st.markdown("## 💡 Recommendations")

    st.markdown("""
    - Focus on trending genres  
    - Invest in high-demand regions  
    - Optimize content duration  
    """)