"""
recommender.py
---------------
Top-level facade that wires together the content-based and
collaborative-filtering recommenders behind one simple interface, plus a
naive hybrid mode that blends both signals. This is the module both the
console app and the Streamlit app import from.
"""

from __future__ import annotations

import pandas as pd

from data_loader import load_all
from content_based import ContentBasedRecommender
from collaborative_filtering import CollaborativeRecommender


class MovieRecommender:
    def __init__(self):
        self.movies, self.ratings = load_all()
        self.content_model = ContentBasedRecommender(self.movies)
        self.collab_model = CollaborativeRecommender(self.ratings, self.movies)

    # -- Content-based -----------------------------------------------
    def by_title(self, title: str, top_n: int = 10) -> pd.DataFrame:
        return self.content_model.recommend_by_title(title, top_n=top_n)

    def by_genres(self, genres: list[str], top_n: int = 10) -> pd.DataFrame:
        return self.content_model.recommend_by_genres(genres, top_n=top_n)

    def search_titles(self, query: str, limit: int = 10) -> list[str]:
        return self.content_model.find_titles(query, limit=limit)

    # -- Collaborative filtering ---------------------------------------
    def for_user(self, user_id: int, top_n: int = 10) -> pd.DataFrame:
        return self.collab_model.recommend_for_user(user_id, top_n=top_n)

    def similar_by_ratings(self, movie_id: int, top_n: int = 10) -> pd.DataFrame:
        return self.collab_model.similar_movies(movie_id, top_n=top_n)

    def known_users(self) -> list[int]:
        return self.collab_model.known_user_ids()

    # -- Hybrid ----------------------------------------------------------
    def hybrid_for_user(self, user_id: int, top_n: int = 10,
                         cf_weight: float = 0.6) -> pd.DataFrame:
        """
        Blend collaborative-filtering predicted ratings with a
        content-based score derived from the user's highest-rated genres.
        `cf_weight` controls how much the collaborative signal counts
        relative to the content signal (0-1).
        """
        cf_recs = self.collab_model.recommend_for_user(user_id, top_n=top_n * 3)

        user_ratings = self.ratings[self.ratings["userId"] == user_id]
        top_rated = user_ratings.sort_values("rating", ascending=False).head(5)
        top_movie_titles = self.movies[
            self.movies["movieId"].isin(top_rated["movieId"])
        ]["genres"].str.split("|").explode()
        favorite_genres = top_movie_titles.value_counts().head(3).index.tolist()

        if not favorite_genres:
            return cf_recs.head(top_n)

        content_recs = self.content_model.recommend_by_genres(
            favorite_genres, top_n=top_n * 3
        )

        merged = cf_recs.merge(
            content_recs[["movieId", "similarity_score"]],
            on="movieId", how="outer",
        )
        merged["predicted_rating"] = merged["predicted_rating"].fillna(
            merged["predicted_rating"].min() if merged["predicted_rating"].notna().any() else 0
        )
        merged["similarity_score"] = merged["similarity_score"].fillna(0)

        # Normalise both signals to 0-1 before blending
        pr = merged["predicted_rating"]
        cs = merged["similarity_score"]
        pr_norm = (pr - pr.min()) / (pr.max() - pr.min() + 1e-9)
        cs_norm = (cs - cs.min()) / (cs.max() - cs.min() + 1e-9)

        merged["hybrid_score"] = cf_weight * pr_norm + (1 - cf_weight) * cs_norm
        merged = merged.merge(
            self.movies[["movieId", "title", "genres"]], on="movieId", how="left",
            suffixes=("", "_movie"),
        )
        merged["title"] = merged["title"].combine_first(merged.get("title_movie"))
        merged["genres"] = merged["genres"].combine_first(merged.get("genres_movie"))

        result = merged.sort_values("hybrid_score", ascending=False).head(top_n)
        return result[["movieId", "title", "genres", "hybrid_score"]].reset_index(drop=True)


if __name__ == "__main__":
    engine = MovieRecommender()
    print("Sample content-based recommendation:")
    sample_title = engine.movies.iloc[0]["title"]
    print(engine.by_title(sample_title, top_n=5))

    print("\nSample collaborative-filtering recommendation:")
    sample_user = engine.known_users()[0]
    print(engine.for_user(sample_user, top_n=5))

    print("\nSample hybrid recommendation:")
    print(engine.hybrid_for_user(sample_user, top_n=5))
