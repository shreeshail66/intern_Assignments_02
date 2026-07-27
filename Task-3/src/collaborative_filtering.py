"""
collaborative_filtering.py
---------------------------
Collaborative-filtering movie recommender built on a user-item rating
matrix. Two complementary techniques are implemented:

1. Matrix factorization (Truncated SVD) to predict a user's rating for
   movies they have not yet seen.
2. Item-based nearest neighbours (cosine similarity between movie rating
   vectors) to answer "users who rated X highly also rated ... highly".

Both approaches only need pandas/numpy/scikit-learn, so the project has
no heavyweight dependency such as `surprise` to install.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity


class CollaborativeRecommender:
    def __init__(self, ratings: pd.DataFrame, movies: pd.DataFrame,
                 n_factors: int = 20):
        self.ratings = ratings
        self.movies = movies
        self.n_factors = n_factors

        self.user_item_matrix = ratings.pivot_table(
            index="userId", columns="movieId", values="rating"
        )
        self._fit_svd()

    # ------------------------------------------------------------------
    # Matrix factorization (user -> predicted rating for every movie)
    # ------------------------------------------------------------------
    def _fit_svd(self) -> None:
        # Mean-center each user's ratings so users with different rating
        # scales (e.g. a generous 4-5 rater vs a harsh 1-2 rater) are
        # comparable, then fill unseen entries with 0 for the SVD input.
        matrix = self.user_item_matrix.copy()
        self.user_means = matrix.mean(axis=1)
        matrix_filled = matrix.sub(self.user_means, axis=0).fillna(0)

        n_components = min(self.n_factors, min(matrix_filled.shape) - 1)
        n_components = max(n_components, 2)

        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        user_factors = self.svd.fit_transform(matrix_filled)
        item_factors = self.svd.components_

        predicted = user_factors @ item_factors
        predicted = predicted + self.user_means.values.reshape(-1, 1)

        self.predicted_ratings = pd.DataFrame(
            predicted,
            index=self.user_item_matrix.index,
            columns=self.user_item_matrix.columns,
        )

    def recommend_for_user(self, user_id: int, top_n: int = 10) -> pd.DataFrame:
        """Recommend movies a user has not yet rated, ranked by predicted rating."""
        if user_id not in self.predicted_ratings.index:
            raise ValueError(f"Unknown userId: {user_id}")

        already_rated = self.user_item_matrix.loc[user_id].dropna().index
        predictions = self.predicted_ratings.loc[user_id].drop(
            index=already_rated, errors="ignore"
        )
        top_movie_ids = predictions.sort_values(ascending=False).head(top_n)

        result = self.movies[self.movies["movieId"].isin(top_movie_ids.index)][
            ["movieId", "title", "genres"]
        ].copy()
        result["predicted_rating"] = result["movieId"].map(top_movie_ids).round(2)
        return result.sort_values("predicted_rating", ascending=False).reset_index(drop=True)

    # ------------------------------------------------------------------
    # Item-based collaborative filtering ("movies rated similarly to X")
    # ------------------------------------------------------------------
    def similar_movies(self, movie_id: int, top_n: int = 10) -> pd.DataFrame:
        """Find movies with the most similar pattern of user ratings."""
        if movie_id not in self.user_item_matrix.columns:
            raise ValueError(f"Unknown movieId: {movie_id}")

        item_matrix = self.user_item_matrix.fillna(0).T  # movies x users
        similarities = cosine_similarity(item_matrix)
        movie_ids = item_matrix.index.tolist()
        idx = movie_ids.index(movie_id)

        scores = list(enumerate(similarities[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        scores = [s for s in scores if movie_ids[s[0]] != movie_id][:top_n]

        result_ids = [movie_ids[s[0]] for s in scores]
        result = self.movies[self.movies["movieId"].isin(result_ids)][
            ["movieId", "title", "genres"]
        ].copy()
        score_map = {movie_ids[s[0]]: round(s[1], 4) for s in scores}
        result["similarity_score"] = result["movieId"].map(score_map)
        return result.sort_values("similarity_score", ascending=False).reset_index(drop=True)

    def known_user_ids(self) -> list[int]:
        return self.user_item_matrix.index.tolist()


if __name__ == "__main__":
    from data_loader import load_all

    movies_df, ratings_df = load_all()
    cf = CollaborativeRecommender(ratings_df, movies_df)
    sample_user = cf.known_user_ids()[0]
    print(f"Recommendations for user {sample_user}:\n")
    print(cf.recommend_for_user(sample_user, top_n=5))
