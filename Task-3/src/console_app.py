"""
console_app.py
---------------
Interactive command-line shell for the movie recommendation engine.
Satisfies the "Interactive console shell" technical requirement.

Run with:
    python src/console_app.py
"""

from __future__ import annotations

import sys

from recommender import MovieRecommender

MENU = """
==================================================
   MOVIE RECOMMENDATION ENGINE - Console Shell
==================================================
1. Recommend by movie title   (content-based)
2. Recommend by genre(s)      (content-based)
3. Recommend for a user       (collaborative filtering)
4. Similar movies by ratings   (collaborative filtering)
5. Hybrid recommendation for a user
6. List sample user ids
7. Search movie titles
0. Exit
--------------------------------------------------
"""


def print_df(df):
    if df.empty:
        print("No results found.\n")
        return
    print(df.to_string(index=False))
    print()


def handle_by_title(engine: MovieRecommender):
    query = input("Enter a movie title (or part of it): ").strip()
    matches = engine.search_titles(query, limit=5)
    if not matches:
        print("No matching movie found.\n")
        return
    if len(matches) > 1:
        print("Multiple matches found, using the first:")
        for m in matches:
            print(f"  - {m}")
    title = matches[0]
    try:
        result = engine.by_title(title, top_n=10)
        print(f"\nBecause you looked at '{title}':\n")
        print_df(result)
    except ValueError as e:
        print(f"Error: {e}\n")


def handle_by_genres(engine: MovieRecommender):
    raw = input("Enter genre(s), comma-separated (e.g. Action, Comedy): ").strip()
    genres = [g.strip() for g in raw.split(",") if g.strip()]
    if not genres:
        print("No genres provided.\n")
        return
    result = engine.by_genres(genres, top_n=10)
    print(f"\nTop matches for genres {genres}:\n")
    print_df(result)


def handle_for_user(engine: MovieRecommender):
    raw = input("Enter a user id: ").strip()
    try:
        user_id = int(raw)
        result = engine.for_user(user_id, top_n=10)
        print(f"\nRecommended for user {user_id}:\n")
        print_df(result)
    except ValueError as e:
        print(f"Error: {e}\n")


def handle_similar_by_ratings(engine: MovieRecommender):
    raw = input("Enter a movie title to base similarity on: ").strip()
    matches = engine.search_titles(raw, limit=5)
    if not matches:
        print("No matching movie found.\n")
        return
    title = matches[0]
    movie_row = engine.movies[engine.movies["title"] == title].iloc[0]
    try:
        result = engine.similar_by_ratings(int(movie_row["movieId"]), top_n=10)
        print(f"\nUsers who rated '{title}' highly also rated these highly:\n")
        print_df(result)
    except ValueError as e:
        print(f"Error: {e}\n")


def handle_hybrid(engine: MovieRecommender):
    raw = input("Enter a user id: ").strip()
    try:
        user_id = int(raw)
        result = engine.hybrid_for_user(user_id, top_n=10)
        print(f"\nHybrid recommendations for user {user_id}:\n")
        print_df(result)
    except ValueError as e:
        print(f"Error: {e}\n")


def handle_list_users(engine: MovieRecommender):
    users = engine.known_users()
    print(f"\n{len(users)} users available. Sample: {users[:20]}\n")


def handle_search(engine: MovieRecommender):
    query = input("Search text: ").strip()
    matches = engine.search_titles(query, limit=15)
    if not matches:
        print("No matches.\n")
        return
    print("\nMatches:")
    for m in matches:
        print(f"  - {m}")
    print()


def main():
    print("Loading data and building models, please wait...")
    try:
        engine = MovieRecommender()
    except FileNotFoundError as e:
        print(f"\n{e}\n")
        sys.exit(1)
    print("Ready!\n")

    handlers = {
        "1": handle_by_title,
        "2": handle_by_genres,
        "3": handle_for_user,
        "4": handle_similar_by_ratings,
        "5": handle_hybrid,
        "6": handle_list_users,
        "7": handle_search,
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        handler = handlers.get(choice)
        if handler is None:
            print("Invalid option, please try again.\n")
            continue
        try:
            handler(engine)
        except Exception as e:  # keep the shell alive on any bad input
            print(f"Something went wrong: {e}\n")


if __name__ == "__main__":
    main()
