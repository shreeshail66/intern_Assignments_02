"""
data_loader.py
--------------
Handles loading and pre-processing of the movie catalogue and ratings
data used throughout the project. Centralising this logic keeps the
content-based, collaborative-filtering and evaluation modules free of
duplicated I/O and cleaning code.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MOVIES_PATH = DATA_DIR / "movies.csv"
RATINGS_PATH = DATA_DIR / "ratings.csv"


def load_movies(path: Path = MOVIES_PATH) -> pd.DataFrame:
    """Load the movie catalogue and perform light pre-processing."""
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run `python src/generate_data.py` first."
        )

    movies = pd.read_csv(path)

    # Basic cleaning: drop duplicate movie ids, fill any missing text
    # fields so downstream vectorizers never choke on NaN values.
    movies = movies.drop_duplicates(subset="movieId").reset_index(drop=True)
    movies["genres"] = movies["genres"].fillna("")
    movies["overview"] = movies["overview"].fillna("")

    # Combined text field used as the input to the TF-IDF vectorizer for
    # content-based filtering. Genres are repeated to give them more
    # weight relative to the free-text overview.
    movies["content_soup"] = (
        movies["genres"].str.replace("|", " ", regex=False) + " " +
        movies["genres"].str.replace("|", " ", regex=False) + " " +
        movies["overview"]
    )
    return movies


def load_ratings(path: Path = RATINGS_PATH) -> pd.DataFrame:
    """Load the user-ratings dataset and perform light pre-processing."""
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run `python src/generate_data.py` first."
        )

    ratings = pd.read_csv(path)
    ratings = ratings.dropna(subset=["userId", "movieId", "rating"])
    ratings["userId"] = ratings["userId"].astype(int)
    ratings["movieId"] = ratings["movieId"].astype(int)
    ratings["rating"] = ratings["rating"].astype(float)
    return ratings


def load_all() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convenience helper returning (movies, ratings)."""
    return load_movies(), load_ratings()


if __name__ == "__main__":
    movies_df, ratings_df = load_all()
    print(f"Loaded {len(movies_df)} movies and {len(ratings_df)} ratings.")
    print(movies_df.head())
