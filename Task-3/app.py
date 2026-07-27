"""
app.py
-------
Streamlit web GUI for the Movie Recommendation Engine.
Satisfies the "graphical web GUI (e.g. Streamlit / Gradio)" requirement.

Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from recommender import MovieRecommender  # noqa: E402

st.set_page_config(
    page_title="Movie Recommendation Engine",
    page_icon="🎬",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading data and building models...")
def get_engine() -> MovieRecommender:
    return MovieRecommender()


def render_results(df, empty_message="No recommendations found."):
    if df is None or df.empty:
        st.info(empty_message)
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


def main():
    st.title("🎬 Movie Recommendation Engine")
    st.caption(
        "Content-based filtering (TF-IDF + cosine similarity) and "
        "collaborative filtering (matrix factorization) over a synthetic "
        "300-movie / 200-user dataset."
    )

    try:
        engine = get_engine()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    tab_title, tab_genre, tab_user, tab_similar, tab_hybrid = st.tabs(
        [
            "🔎 By Movie Title",
            "🏷️ By Genre",
            "👤 For a User",
            "🤝 Similar by Ratings",
            "✨ Hybrid",
        ]
    )

    all_genres = sorted({
        g for genres in engine.movies["genres"].str.split("|") for g in genres
    })

    # --- Tab 1: content-based by title -----------------------------------
    with tab_title:
        st.subheader("Find movies similar to one you already like")
        query = st.text_input("Search for a movie title", key="title_search")
        if query:
            matches = engine.search_titles(query, limit=10)
            if matches:
                chosen = st.selectbox("Select the exact movie", matches)
                top_n = st.slider("Number of recommendations", 5, 20, 10, key="tn1")
                if st.button("Get recommendations", key="btn1"):
                    result = engine.by_title(chosen, top_n=top_n)
                    render_results(result)
            else:
                st.warning("No movies matched your search.")

    # --- Tab 2: content-based by genre ------------------------------------
    with tab_genre:
        st.subheader("Discover movies matching your favorite genres")
        chosen_genres = st.multiselect("Pick one or more genres", all_genres)
        top_n = st.slider("Number of recommendations", 5, 20, 10, key="tn2")
        if st.button("Get recommendations", key="btn2"):
            if chosen_genres:
                result = engine.by_genres(chosen_genres, top_n=top_n)
                render_results(result)
            else:
                st.warning("Please select at least one genre.")

    # --- Tab 3: collaborative filtering for a user -------------------------
    with tab_user:
        st.subheader("Personalized recommendations from user rating history")
        user_ids = engine.known_users()
        user_id = st.selectbox("Select a user id", user_ids)
        top_n = st.slider("Number of recommendations", 5, 20, 10, key="tn3")
        if st.button("Get recommendations", key="btn3"):
            result = engine.for_user(user_id, top_n=top_n)
            render_results(result)

        with st.expander("This user's rating history"):
            history = engine.ratings[engine.ratings["userId"] == user_id].merge(
                engine.movies[["movieId", "title", "genres"]], on="movieId"
            )[["title", "genres", "rating"]].sort_values("rating", ascending=False)
            st.dataframe(history, use_container_width=True, hide_index=True)

    # --- Tab 4: item-based collaborative filtering --------------------------
    with tab_similar:
        st.subheader("Movies rated similarly by the community")
        query = st.text_input("Search for a movie title", key="similar_search")
        if query:
            matches = engine.search_titles(query, limit=10)
            if matches:
                chosen = st.selectbox("Select the exact movie", matches, key="similar_select")
                top_n = st.slider("Number of recommendations", 5, 20, 10, key="tn4")
                if st.button("Get recommendations", key="btn4"):
                    movie_id = int(
                        engine.movies[engine.movies["title"] == chosen]["movieId"].iloc[0]
                    )
                    result = engine.similar_by_ratings(movie_id, top_n=top_n)
                    render_results(result)
            else:
                st.warning("No movies matched your search.")

    # --- Tab 5: hybrid ------------------------------------------------------
    with tab_hybrid:
        st.subheader("Blend of collaborative filtering + content signals")
        user_ids = engine.known_users()
        user_id = st.selectbox("Select a user id", user_ids, key="hybrid_user")
        cf_weight = st.slider(
            "Collaborative-filtering weight", 0.0, 1.0, 0.6, 0.1,
            help="Higher = trust the user's rating history more; "
                 "lower = trust genre-based content similarity more.",
        )
        top_n = st.slider("Number of recommendations", 5, 20, 10, key="tn5")
        if st.button("Get recommendations", key="btn5"):
            result = engine.hybrid_for_user(user_id, top_n=top_n, cf_weight=cf_weight)
            render_results(result)

    st.divider()
    with st.expander("📊 Dataset overview"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Movies", len(engine.movies))
        col2.metric("Ratings", len(engine.ratings))
        col3.metric("Users", engine.ratings["userId"].nunique())
        st.dataframe(engine.movies.head(20)[["title", "genres"]],
                     use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
