import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from sklearn.preprocessing import LabelEncoder

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
    margin-bottom: 15px;
}
img {
    border-radius: 10px;
    transition: 0.3s;
}
img:hover {
    transform: scale(1.08);
}
h1, h2, h3, h4 {
    color: #E2E8F0;
}
</style>
""", unsafe_allow_html=True)

# ------------------ TITLE + HERO ------------------
st.markdown("# 🎬 OTT Content Intelligence Dashboard")

st.markdown("""
<div style="
background: linear-gradient(to right, #000000, #1e293b);
padding: 30px;
border-radius: 15px;
margin-bottom: 20px;
">
<h2 style="color:white;">Discover Trending Content</h2>
<p style="color:gray;">AI-powered OTT insights</p>
</div>
""", unsafe_allow_html=True)

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

# 🎬 ADD POSTER COLUMN
df["poster"] = "https://dummyimage.com/300x450/000/fff&text=OTT"

# ------------------ SIDEBAR ------------------
st.sidebar.markdown("## 🎯 Filters")
st.sidebar.markdown("---")

content_type = st.sidebar.selectbox("Content Type", df['type'].unique())

year_range = st.sidebar.slider(
    "Release Year",
    int(df['release_year'].min()),
    int(df['release_year'].max()),
    (2000, 2020)
)

# ------------------ FILTER DATA ------------------
filtered_df = df[
    (df['type'] == content_type) &
    (df['release_year'].between(year_range[0], year_range[1]))
]

# ------------------ SEARCH BAR ------------------
search = st.text_input("🔍 Search Content")

if search:
    filtered_df = filtered_df[
        filtered_df['title'].str.contains(search, case=False, na=False)
    ]

# ------------------ POSTER FUNCTION ------------------
def show_posters(data):
    cols = st.columns(5)
    for i, row in data.iterrows():
        with cols[i % 5]:
            st.markdown(f"""
            <div style="text-align:center;">
                <img src="{row['poster']}" style="width:100%;">
                <p style="color:white;font-size:14px;">{row['title'][:30]}</p>
            </div>
            """, unsafe_allow_html=True)

# ------------------ TABS ------------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🤖 Prediction", "📌 Insights"])

# ================== TAB 1 ==================
with tab1:

    # KPI CARDS
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="card"><h4>🎬 Total</h4><h2>{len(filtered_df)}</h2></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="card"><h4>🌍 Countries</h4><h2>{filtered_df["country"].nunique()}</h2></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="card"><h4>🎭 Genres</h4><h2>{filtered_df["listed_in"].nunique()}</h2></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="card"><h4>⏱ Duration</h4><h2>{int(filtered_df["duration_num"].mean())}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")

    # CHARTS
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.bar(filtered_df, x='type', color='type', title="Content Distribution")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(filtered_df, names='rating', title="Rating Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        year_trend = filtered_df['release_year'].value_counts().sort_index()
        fig3 = px.line(x=year_trend.index, y=year_trend.values, title="Content Growth")
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        top_countries = filtered_df['country'].value_counts().head(10)
        fig4 = px.bar(x=top_countries.values, y=top_countries.index, orientation='h', title="Top Countries")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")

    # 🎬 NETFLIX STYLE SECTIONS
    st.markdown("## 🔥 Trending Now")
    show_posters(filtered_df.sample(10))

    st.markdown("## 🎬 Movies")
    movies = filtered_df[filtered_df['type'] == 'Movie']
    show_posters(movies.head(10))

    st.markdown("## 📺 TV Shows")
    tv = filtered_df[filtered_df['type'] == 'TV Show']
    show_posters(tv.head(10))

# ================== TAB 2 ==================
with tab2:

    st.markdown("## 🎯 Predict Content Type")

    try:
        model = joblib.load("model.pkl")

        col1, col2, col3 = st.columns(3)

        release_year = col1.number_input("Release Year", 2000, 2025)
        duration = col2.number_input("Duration", 1, 300)
        rating = col3.selectbox("Rating", df['rating'].unique())

        le = LabelEncoder()
        df['rating_encoded'] = le.fit_transform(df['rating'])
        rating_encoded = le.transform([rating])[0]

        if st.button("🚀 Predict"):
            prediction = model.predict([[release_year, duration, rating_encoded]])

            if prediction[0] == 0:
                st.success("🎬 Movie")
            else:
                st.success("📺 TV Show")

    except:
        st.warning("⚠️ model.pkl not found")

# ================== TAB 3 ==================
with tab3:

    st.markdown("## 📌 Key Insights")

    st.markdown("""
    - 🎬 Movies dominate OTT  
    - 📈 Content increasing yearly  
    - 🌍 USA & India lead  
    - ⏱ Medium duration performs best  
    """)

    st.markdown("---")

    st.markdown("## 💡 Recommendations")

    st.markdown("""
    - Invest in trending genres  
    - Focus on high-growth regions  
    - Optimize duration strategy  
    """)