"""
evaluation.py
--------------
Performance evaluation utilities for both recommendation approaches.
Implements the "Performance evaluation reports mapping model efficiency
and user requests" deliverable required by the task brief.

Metrics implemented:
  - Content-based: intra-list genre-similarity (how coherent the
    recommended list is with the seed movie).
  - Collaborative filtering: RMSE / MAE on a held-out test split of
    ratings, plus Precision@K / Recall@K for the top-N recommendation
    task.
  - Efficiency: wall-clock time to build each model and to serve a
    single recommendation request, used to characterise how the system
    would behave under real user load.
"""

from __future__ import annotations

import time
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from data_loader import load_all
from content_based import ContentBasedRecommender
from collaborative_filtering import CollaborativeRecommender

REPORT_PATH = Path(__file__).resolve().parent.parent / "docs" / "performance_report.md"


def time_block(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def evaluate_content_based(movies: pd.DataFrame, n_queries: int = 30) -> dict:
    model, build_time = time_block(ContentBasedRecommender, movies)

    sample_titles = movies["title"].sample(
        n=min(n_queries, len(movies)), random_state=42
    ).tolist()

    query_times = []
    genre_overlap_scores = []

    for title in sample_titles:
        recs, elapsed = time_block(model.recommend_by_title, title, 10)
        query_times.append(elapsed)

        seed_genres = set(
            movies.loc[movies["title"] == title, "genres"].iloc[0].split("|")
        )
        overlaps = []
        for _, row in recs.iterrows():
            rec_genres = set(row["genres"].split("|"))
            if seed_genres:
                overlaps.append(len(seed_genres & rec_genres) / len(seed_genres))
        if overlaps:
            genre_overlap_scores.append(np.mean(overlaps))

    return {
        "model_build_time_sec": round(build_time, 4),
        "avg_query_time_sec": round(float(np.mean(query_times)), 6),
        "avg_intra_list_genre_overlap": round(float(np.mean(genre_overlap_scores)), 4),
        "n_queries": len(sample_titles),
    }


def evaluate_collaborative(ratings: pd.DataFrame, movies: pd.DataFrame,
                            k: int = 10, rating_threshold: float = 3.5) -> dict:
    train, test = train_test_split(ratings, test_size=0.2, random_state=42)

    model, build_time = time_block(CollaborativeRecommender, train, movies)

    # --- RMSE / MAE on held-out ratings the model can actually score ---
    test_known = test[
        test["userId"].isin(model.predicted_ratings.index) &
        test["movieId"].isin(model.predicted_ratings.columns)
    ]
    if len(test_known) > 0:
        preds = test_known.apply(
            lambda r: model.predicted_ratings.loc[r["userId"], r["movieId"]], axis=1
        )
        errors = preds.values - test_known["rating"].values
        rmse = float(np.sqrt(np.mean(errors ** 2)))
        mae = float(np.mean(np.abs(errors)))
    else:
        rmse, mae = float("nan"), float("nan")

    # --- Precision@K / Recall@K for the top-N recommendation task ---
    precisions, recalls = [], []
    query_times = []
    eval_users = [u for u in test["userId"].unique() if u in model.predicted_ratings.index][:40]

    for user_id in eval_users:
        relevant = set(
            test[(test["userId"] == user_id) & (test["rating"] >= rating_threshold)]["movieId"]
        )
        if not relevant:
            continue

        recs, elapsed = time_block(model.recommend_for_user, user_id, k)
        query_times.append(elapsed)
        recommended = set(recs["movieId"])

        hits = recommended & relevant
        precisions.append(len(hits) / k)
        recalls.append(len(hits) / len(relevant))

    return {
        "model_build_time_sec": round(build_time, 4),
        "rmse": round(rmse, 4) if rmse == rmse else None,  # NaN check
        "mae": round(mae, 4) if mae == mae else None,
        "avg_query_time_sec": round(float(np.mean(query_times)), 6) if query_times else None,
        f"precision_at_{k}": round(float(np.mean(precisions)), 4) if precisions else None,
        f"recall_at_{k}": round(float(np.mean(recalls)), 4) if recalls else None,
        "n_users_evaluated": len(precisions),
    }


def generate_report() -> dict:
    movies, ratings = load_all()

    content_metrics = evaluate_content_based(movies)
    collab_metrics = evaluate_collaborative(ratings, movies)

    report = {
        "dataset_summary": {
            "n_movies": int(len(movies)),
            "n_ratings": int(len(ratings)),
            "n_users": int(ratings["userId"].nunique()),
            "avg_ratings_per_user": round(len(ratings) / ratings["userId"].nunique(), 2),
        },
        "content_based": content_metrics,
        "collaborative_filtering": collab_metrics,
    }

    _write_markdown_report(report)
    return report


def _write_markdown_report(report: dict) -> None:
    ds = report["dataset_summary"]
    cb = report["content_based"]
    cf = report["collaborative_filtering"]

    md = f"""# Performance Evaluation Report

_Auto-generated by `src/evaluation.py`. Re-run `python src/evaluation.py`
to refresh these numbers after any change to the data or models._

## Dataset Summary

| Metric | Value |
|---|---|
| Movies in catalogue | {ds['n_movies']} |
| Total ratings | {ds['n_ratings']} |
| Unique users | {ds['n_users']} |
| Avg. ratings per user | {ds['avg_ratings_per_user']} |

## Content-Based Filtering (TF-IDF + Cosine Similarity)

| Metric | Value | What it means |
|---|---|---|
| Model build time | {cb['model_build_time_sec']} s | Time to vectorize the catalogue and build the similarity matrix |
| Avg. query time | {cb['avg_query_time_sec']} s | Time to serve one "similar movies" request |
| Avg. intra-list genre overlap | {cb['avg_intra_list_genre_overlap']} | Fraction of the seed movie's genres shared by each recommendation (higher = more coherent) |
| Queries evaluated | {cb['n_queries']} | |

## Collaborative Filtering (Truncated SVD + Item-KNN)

| Metric | Value | What it means |
|---|---|---|
| Model build time | {cf['model_build_time_sec']} s | Time to build the user-item matrix and factorize it |
| RMSE (held-out ratings) | {cf['rmse']} | Average error, in rating-scale points, between predicted and actual ratings |
| MAE (held-out ratings) | {cf['mae']} | Mean absolute error, same units as RMSE |
| Avg. query time | {cf['avg_query_time_sec']} s | Time to serve one "recommend for user" request |
| Precision@10 | {cf['precision_at_10']} | Of the top 10 recommended movies, the fraction the user actually rated highly |
| Recall@10 | {cf['recall_at_10']} | Of all movies the user rated highly, the fraction captured in the top 10 |
| Users evaluated | {cf['n_users_evaluated']} | |

## Interpreting model efficiency vs. user requests

- Both models build in well under a second on this ~{ds['n_movies']}-movie /
  {ds['n_ratings']}-rating dataset, and serve a single recommendation
  request in a few milliseconds — comfortably fast enough for an
  interactive console or web session with many concurrent users.
- The **content-based** model scales with catalogue size (it must hold an
  N x N similarity matrix in memory), so at production scale (tens of
  thousands of movies) it would need to move to approximate nearest
  neighbour search (e.g. FAISS/Annoy) instead of a dense matrix.
- The **collaborative filtering** model scales with the number of users
  and movies in the rating matrix. Precision/Recall depend heavily on
  how much rating history a user has — new users with few ratings
  ("cold start") are better served by the content-based or hybrid path.
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(md, encoding="utf-8")


if __name__ == "__main__":
    report = generate_report()
    print(json.dumps(report, indent=2))
    print(f"\nMarkdown report written to {REPORT_PATH}")
