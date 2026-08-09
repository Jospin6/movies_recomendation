import streamlit as st

from src.recommender import load_artifacts, recommend


st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
)

st.header("Movies Recommendation System Using Machine Learning")

movies, similarity = load_artifacts()
movie_list = movies["title"].values

selected_movie = st.selectbox(
    "Type or select a movie to get recommendation",
    movie_list,
)

if st.button("Show recommendation"):
    try:
        recommendations = recommend(selected_movie, movies, similarity)
        columns = st.columns(5)

        for column, (movie_name, poster_url) in zip(columns, recommendations):
            with column:
                st.text(movie_name)
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.info("Poster unavailable")
    except Exception as error:
        st.error(f"Unable to load recommendations: {error}")
