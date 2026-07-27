# 🎬 Movie Recommendation Engine

A production-style movie recommendation engine built for **Task 3 — Final
Project (4-Week Track)**. It combines **content-based filtering**
(TF-IDF + cosine similarity) with **collaborative filtering** (matrix
factorization via Truncated SVD) and exposes both through an interactive
console shell and a Streamlit web GUI.

---

## ✨ Features

- **Content-based recommendations**
  - "Find movies similar to X" (TF-IDF over genres + plot overview, cosine similarity)
  - "Find movies matching these genres"
- **Collaborative filtering**
  - "Recommend for user N" (matrix factorization / Truncated SVD)
  - "Movies rated similarly to X" (item-based cosine similarity on the ratings matrix)
- **Hybrid mode** blending both signals with an adjustable weight
- **Interactive console shell** (`src/console_app.py`)
- **Streamlit web GUI** (`app.py`) with 5 tabs, one per recommendation mode
- **Jupyter notebook** walking through EDA, model building, evaluation, and live demo queries
- **Automated performance evaluation** (RMSE, MAE, Precision@K, Recall@K, genre-coherence, build/query timing) written to `docs/performance_report.md`
- Fully **offline / self-contained**: a reproducible synthetic dataset is generated locally, no external downloads required

---

## 📂 Project structure

```
movie-recommendation-system/
├── app.py                                  # Streamlit web GUI
├── requirements.txt
├── data/
│   ├── movies.csv                          # 300 movies (generated)
│   └── ratings.csv                         # ~10,000 ratings (generated)
├── src/
│   ├── generate_data.py                    # Reproducible synthetic dataset generator
│   ├── data_loader.py                      # CSV loading + cleaning
│   ├── content_based.py                    # TF-IDF + cosine similarity model
│   ├── collaborative_filtering.py          # Truncated SVD + item-KNN model
│   ├── recommender.py                      # Unified facade + hybrid mode
│   ├── evaluation.py                       # Metrics + report generation
│   └── console_app.py                      # Interactive CLI shell
├── notebooks/
│   └── movie_recommendation_engine.ipynb   # Full walkthrough, executed with outputs
├── docs/
│   ├── architecture.md                     # System design, data flow, pipeline
│   └── performance_report.md               # Auto-generated evaluation results
├── screenshots/                            # Add your console/Streamlit screenshots here
└── tests/
    └── test_recommender.py                 # Basic sanity tests
```

---

## 🚀 Setup instructions

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd movie-recommendation-system
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate the dataset

The repo already ships with `data/movies.csv` and `data/ratings.csv`
generated from a fixed random seed. To regenerate them from scratch:

```bash
python src/generate_data.py
```

### 3. Run the console app

```bash
cd src
python console_app.py
```

### 4. Run the Streamlit web GUI

```bash
streamlit run app.py
```
Then open the URL Streamlit prints (typically `http://localhost:8501`).

### 5. Run / explore the Jupyter notebook

```bash
jupyter notebook notebooks/movie_recommendation_engine.ipynb
```

### 6. Regenerate the performance report

```bash
python src/evaluation.py
```
This refreshes `docs/performance_report.md` with the latest metrics.

---

## 🖥️ Usage examples

### Console shell
```
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
```

### Python API
```python
from src.recommender import MovieRecommender

engine = MovieRecommender()

# Content-based
engine.by_title("Golden Echo", top_n=5)
engine.by_genres(["Sci-Fi", "Adventure"], top_n=5)

# Collaborative filtering
engine.for_user(user_id=1, top_n=5)
engine.similar_by_ratings(movie_id=3, top_n=5)

# Hybrid
engine.hybrid_for_user(user_id=1, top_n=5, cf_weight=0.6)
```

---

## 🧠 How it works (short version)

1. **Content-based filtering**: every movie's genres + plot overview are
   combined into one text field and vectorized with TF-IDF. Cosine
   similarity between vectors ranks how alike two movies are.
2. **Collaborative filtering**: the user-item ratings matrix is
   mean-centered and factorized with Truncated SVD to predict ratings
   for movies a user hasn't seen yet. An item-based cosine-similarity
   variant also answers "what else did people who liked X also like".
3. **Hybrid**: normalizes and blends both scores so recommendations stay
   personalized for users with rating history, while still working for
   new users via the content-based fallback.

Full details, diagrams, and design rationale are in
[`docs/architecture.md`](docs/architecture.md).

---

## 📊 Performance evaluation

See [`docs/performance_report.md`](docs/performance_report.md) for the
full, auto-generated report. Summary of what's measured:

| Model | Metrics |
|---|---|
| Content-based | Build time, avg. query time, intra-list genre-overlap coherence |
| Collaborative filtering | Build time, avg. query time, RMSE, MAE, Precision@10, Recall@10 |

Both models build in milliseconds and serve a single recommendation
request in a few milliseconds on the ~300-movie / 200-user dataset,
which comfortably supports an interactive console or multi-user web
session. See the report for notes on scaling to production-size
catalogues.

---

## 🧪 Tests

A basic sanity-check test suite is included:

```bash
python -m pytest tests/ -v
```

---

## 📝 Notes on the dataset

This project ships with a **synthetically generated but structurally
realistic** dataset (`src/generate_data.py`) instead of a third-party
download such as MovieLens, so the whole project runs fully offline and
reproducibly (fixed random seed = 42):

- 300 movies across 15 genres, each with a genre-consistent plot overview
- 200 synthetic users, each with 1–3 "favorite" genres that bias their
  simulated ratings — this gives the collaborative-filtering model real,
  learnable taste signal instead of pure noise
- ~10,000 ratings total

To swap in a real dataset (e.g. MovieLens), just replace `data/movies.csv`
and `data/ratings.csv` with files following the same column schema
(`movieId, title, genres, overview` / `userId, movieId, rating, timestamp`).

---

## 📌 Submission checklist (per Task 3 requirements)

- [x] Jupyter Notebook outlining recommendation logic — `notebooks/movie_recommendation_engine.ipynb`
- [x] Python script files — `src/*.py`
- [x] Interactive console shell — `src/console_app.py`
- [x] Graphical web GUI (Streamlit) — `app.py`
- [x] Performance evaluation report — `docs/performance_report.md`
- [x] Detailed architecture doc — `docs/architecture.md`
- [x] Well-documented README — this file
- [ ] Screenshots of the console/GUI — add your own to `screenshots/` (see note below)
- [ ] Demo video (2–5 minutes) — record your own walkthrough, since Claude cannot capture your live UI session

> **Note:** Screenshots and the demo video need to be captured from
> *your own* running instance (per the task's "submit only your own
> original work" requirement), so those two items are left for you to
> add before submission — everything else is complete and tested.
