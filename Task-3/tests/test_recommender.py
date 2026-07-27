"""
test_recommender.py
---------------------
Basic sanity tests for the movie recommendation engine. These are not
exhaustive, but they guard against the most common regressions: models
failing to build, empty results, and obviously malformed output shapes.

Run with:
    python -m pytest tests/ -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from data_loader import load_all  # noqa: E402
from content_based import ContentBasedRecommender  # noqa: E402
from collaborative_filtering import CollaborativeRecommender  # noqa: E402
from recommender import MovieRecommender  # noqa: E402


@pytest.fixture(scope="module")
def data():
    return load_all()


@pytest.fixture(scope="module")
def engine():
    return MovieRecommender()


def test_data_loads(data):
    movies, ratings = data
    assert len(movies) > 0
    assert len(ratings) > 0
    assert {"movieId", "title", "genres", "overview"}.issubset(movies.columns)
    assert {"userId", "movieId", "rating"}.issubset(ratings.columns)


def test_content_based_recommendations_not_empty(data):
    movies, _ = data
    model = ContentBasedRecommender(movies)
    sample_title = movies.iloc[0]["title"]
    result = model.recommend_by_title(sample_title, top_n=5)
    assert not result.empty
    assert len(result) <= 5
    # The seed movie itself should never appear in its own recommendations
    assert sample_title not in result["title"].values


def test_content_based_genre_search(data):
    movies, _ = data
    model = ContentBasedRecommender(movies)
    result = model.recommend_by_genres(["Action"], top_n=5)
    assert not result.empty


def test_content_based_unknown_title_raises(data):
    movies, _ = data
    model = ContentBasedRecommender(movies)
    with pytest.raises(ValueError):
        model.recommend_by_title("Definitely Not A Real Movie Title XYZ123", top_n=5)


def test_collaborative_recommendations_not_empty(data):
    movies, ratings = data
    model = CollaborativeRecommender(ratings, movies)
    sample_user = model.known_user_ids()[0]
    result = model.recommend_for_user(sample_user, top_n=5)
    assert not result.empty
    assert len(result) <= 5


def test_collaborative_unknown_user_raises(data):
    movies, ratings = data
    model = CollaborativeRecommender(ratings, movies)
    with pytest.raises(ValueError):
        model.recommend_for_user(user_id=-999, top_n=5)


def test_collaborative_similar_movies(data):
    movies, ratings = data
    model = CollaborativeRecommender(ratings, movies)
    sample_movie_id = int(movies.iloc[0]["movieId"])
    result = model.similar_movies(sample_movie_id, top_n=5)
    assert not result.empty


def test_hybrid_recommendations(engine):
    sample_user = engine.known_users()[0]
    result = engine.hybrid_for_user(sample_user, top_n=5)
    assert not result.empty
    assert "hybrid_score" in result.columns


def test_recommended_movie_ids_exist_in_catalogue(engine):
    sample_user = engine.known_users()[0]
    result = engine.for_user(sample_user, top_n=5)
    valid_ids = set(engine.movies["movieId"])
    assert set(result["movieId"]).issubset(valid_ids)
