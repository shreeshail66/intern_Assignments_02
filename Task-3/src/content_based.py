"""
content_based.py
-----------------
Content-based movie recommender using TF-IDF vectorization of each
movie's genres + plot overview, with cosine similarity used to find the
most similar movies to a given title.

This directly implements the "4-Week Interns" requirement:
    Movie Recommendation System using content-based filtering / tf-idf.
"""

from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel


class ContentBasedRecommender:
    """
    Fits a TF-IDF vectorizer over each movie's combined genre/overview
    text ("content soup") and exposes cosine-similarity based lookups.
    """

    def __init__(self, movies: pd.DataFrame):
        self.movies = movies.reset_index(drop=True)
        self._title_to_index = pd.Series(
            self.movies.index, index=self.movies["title"]
        )
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            min_df=1,
            ngram_range=(1, 2),
        )
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self._fit()

    def _fit(self) -> None:
        self.tfidf_matrix = self.vectorizer.fit_transform(
            self.movies["content_soup"]
        )
        # linear_kernel is equivalent to cosine_similarity for L2-normalised
        # TF-IDF vectors but is noticeably faster on larger matrices.
        self.similarity_matrix = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)

    def recommend_by_title(self, title: str, top_n: int = 10) -> pd.DataFrame:
        """Return the top_n movies most similar in content to `title`."""
        matches = self.movies[self.movies["title"].str.contains(
            title, case=False, na=False, regex=False)]
        if matches.empty:
            raise ValueError(f"No movie found matching '{title}'.")

        idx = matches.index[0]
        scores = list(enumerate(self.similarity_matrix[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        # Skip index 0 result, which is always the movie itself.
        scores = [s for s in scores if s[0] != idx][:top_n]

        result_indices = [s[0] for s in scores]
        result = self.movies.iloc[result_indices][
            ["movieId", "title", "genres"]
        ].copy()
        result["similarity_score"] = [round(s[1], 4) for s in scores]
        return result.reset_index(drop=True)

    def recommend_by_genres(self, genres: list[str], top_n: int = 10) -> pd.DataFrame:
        """Return top_n movies whose content best matches a list of genres."""
        query = " ".join(genres) + " " + " ".join(genres)  # weight genres
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_n]
        result_indices = [r[0] for r in ranked]
        result = self.movies.iloc[result_indices][
            ["movieId", "title", "genres"]
        ].copy()
        result["similarity_score"] = [round(r[1], 4) for r in ranked]
        return result.reset_index(drop=True)

    def find_titles(self, query: str, limit: int = 10) -> list[str]:
        """Helper for search/autocomplete in the UI layers."""
        matches = self.movies[self.movies["title"].str.contains(
            query, case=False, na=False, regex=False)]
        return matches["title"].head(limit).tolist()


if __name__ == "__main__":
    from data_loader import load_movies

    movies_df = load_movies()
    recommender = ContentBasedRecommender(movies_df)
    sample_title = movies_df.iloc[0]["title"]
    print(f"Recommendations similar to: {sample_title}\n")
    print(recommender.recommend_by_title(sample_title, top_n=5))
