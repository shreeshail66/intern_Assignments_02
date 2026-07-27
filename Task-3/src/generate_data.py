"""
generate_data.py
-----------------
Generates a synthetic but realistic movie catalogue and a user-ratings
dataset used to power both the content-based and collaborative-filtering
recommenders in this project.

The dataset is generated with a fixed random seed so it is fully
reproducible. Running this script regenerates data/movies.csv and
data/ratings.csv from scratch.

Usage:
    python src/generate_data.py
"""

import random
import itertools
from pathlib import Path

import pandas as pd
import numpy as np

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Vocabulary used to build movie titles, genres and plot overviews
# ---------------------------------------------------------------------------

GENRES = [
    "Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance",
    "Thriller", "Animation", "Fantasy", "Documentary", "Crime",
    "Adventure", "Mystery", "War", "Musical",
]

# Genre -> plot keyword bank. These keywords are combined into short
# overview sentences so that the TF-IDF vectors used for content-based
# filtering carry genuine, genre-consistent signal instead of random noise.
GENRE_KEYWORDS = {
    "Action": ["explosive chase", "rogue agent", "high-stakes heist",
               "relentless pursuit", "elite soldier", "daring escape"],
    "Comedy": ["awkward misunderstanding", "wisecracking best friend",
               "chaotic wedding", "mistaken identity", "slapstick disaster",
               "unlikely roommates"],
    "Drama": ["family secret", "personal redemption", "difficult choice",
              "broken relationship", "quiet sacrifice", "coming of age"],
    "Horror": ["haunted house", "ancient curse", "sinister entity",
               "isolated cabin", "creeping dread", "possessed doll"],
    "Sci-Fi": ["distant galaxy", "rogue artificial intelligence",
               "time-traveling scientist", "colony on Mars",
               "dystopian future", "first contact"],
    "Romance": ["star-crossed lovers", "second chance at love",
                "childhood sweethearts", "forbidden affair",
                "long-distance romance", "unexpected chemistry"],
    "Thriller": ["cat-and-mouse investigation", "conspiracy unravels",
                 "double agent", "race against time",
                 "hidden identity", "high-stakes negotiation"],
    "Animation": ["talking animals", "magical kingdom",
                  "young hero's journey", "whimsical adventure",
                  "enchanted forest", "toy come to life"],
    "Fantasy": ["ancient prophecy", "hidden kingdom", "dragon rider",
                "cursed sword", "mythical creatures", "portal to another world"],
    "Documentary": ["untold true story", "investigative journey",
                    "archival footage", "expert interviews",
                    "historical reckoning", "behind-the-scenes look"],
    "Crime": ["organized crime family", "undercover detective",
              "unsolved murder", "corrupt officials", "prison escape",
              "underworld rivalry"],
    "Adventure": ["treasure hunt", "uncharted island", "epic voyage",
                  "survival in the wild", "lost city", "perilous expedition"],
    "Mystery": ["locked-room puzzle", "vanishing witness",
                "cryptic clues", "small-town secret",
                "unreliable narrator", "cold case reopened"],
    "War": ["front-line soldiers", "battle for survival",
            "resistance fighters", "wartime romance",
            "occupied homeland", "final stand"],
    "Musical": ["Broadway dreams", "rival dance crews",
                "aspiring singer", "big city audition",
                "small-town talent show", "band on the rise"],
}

TITLE_ADJECTIVES = ["Silent", "Last", "Broken", "Hidden", "Golden", "Final",
                     "Lost", "Crimson", "Endless", "Forgotten", "Midnight",
                     "Shattered", "Distant", "Eternal", "Wandering"]
TITLE_NOUNS = ["Horizon", "Shadow", "Legacy", "Kingdom", "Signal", "Harbor",
               "Echo", "Voyage", "Reckoning", "Requiem", "Frontier",
               "Ascension", "Descent", "Covenant", "Symphony"]


def make_title(used_titles: set) -> str:
    """
    Builds a unique two-word title from the adjective/noun banks. Since the
    banks only produce a finite number of combinations, once they are
    exhausted a numeric suffix guarantees uniqueness without looping forever.
    """
    base = f"{random.choice(TITLE_ADJECTIVES)} {random.choice(TITLE_NOUNS)}"
    if base not in used_titles:
        used_titles.add(base)
        return base

    suffix = 2
    while f"{base} {suffix}" in used_titles:
        suffix += 1
    title = f"{base} {suffix}"
    used_titles.add(title)
    return title


def make_overview(genres: list) -> str:
    parts = []
    for g in genres:
        parts.append(random.choice(GENRE_KEYWORDS[g]))
    random.shuffle(parts)
    return f"A story of {', '.join(parts[:-1])} and {parts[-1]}." if len(parts) > 1 \
        else f"A story of {parts[0]}."


def generate_movies(n_movies: int = 300) -> pd.DataFrame:
    used_titles = set()
    rows = []
    for movie_id in range(1, n_movies + 1):
        n_genres = random.choice([1, 1, 2, 2, 3])
        genres = random.sample(GENRES, n_genres)
        title = make_title(used_titles)
        year = random.randint(1985, 2025)
        overview = make_overview(genres)
        rows.append({
            "movieId": movie_id,
            "title": f"{title} ({year})",
            "year": year,
            "genres": "|".join(genres),
            "overview": overview,
        })
    return pd.DataFrame(rows)


def generate_ratings(movies: pd.DataFrame, n_users: int = 200,
                      min_ratings: int = 20, max_ratings: int = 90) -> pd.DataFrame:
    """
    Each synthetic user has 1-3 'favorite' genres. Movies matching a
    favorite genre receive a higher expected rating, which injects a
    realistic collaborative-filtering signal (users who like the same
    genres end up with correlated rating patterns).
    """
    rows = []
    base_timestamp = 1_600_000_000  # arbitrary epoch anchor
    for user_id in range(1, n_users + 1):
        favorite_genres = set(random.sample(GENRES, random.choice([1, 2, 3])))
        n_ratings = random.randint(min_ratings, max_ratings)
        rated_movies = movies.sample(n=min(n_ratings, len(movies)), replace=False)

        for _, movie in rated_movies.iterrows():
            movie_genres = set(movie["genres"].split("|"))
            overlap = len(favorite_genres & movie_genres)

            # Base rating skews upward when the movie matches the user's taste
            mean_rating = 2.6 + overlap * 0.9
            rating = np.clip(np.random.normal(loc=mean_rating, scale=0.8), 1, 5)
            rating = round(rating * 2) / 2  # round to nearest 0.5

            rows.append({
                "userId": user_id,
                "movieId": int(movie["movieId"]),
                "rating": rating,
                "timestamp": base_timestamp + random.randint(0, 90_000_000),
            })
    return pd.DataFrame(rows)


def main():
    print("Generating synthetic movie catalogue...")
    movies = generate_movies(n_movies=300)
    movies.to_csv(DATA_DIR / "movies.csv", index=False)
    print(f"  -> {len(movies)} movies written to data/movies.csv")

    print("Generating synthetic user ratings...")
    ratings = generate_ratings(movies, n_users=200)
    ratings.to_csv(DATA_DIR / "ratings.csv", index=False)
    print(f"  -> {len(ratings)} ratings written to data/ratings.csv "
          f"({ratings['userId'].nunique()} users)")


if __name__ == "__main__":
    main()
