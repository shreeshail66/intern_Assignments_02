# 🌸 Iris Flower Classification — Machine Learning Pipeline

**DevRise Internship Program — Batch 1 (2026)**
**Domain:** AI & ML | **Task:** Task 2 — Machine Learning Model

An end-to-end, leakage-safe supervised machine learning pipeline that classifies
Iris flowers into three species (*setosa*, *versicolor*, *virginica*) using
Scikit-Learn. The project covers data cleaning, exploratory data analysis,
preprocessing, training of three classifiers, full evaluation, and decision
boundary visualization.

---

## 📁 Project Structure

```
DevRise-Iris-Classification/
├── notebooks/
│   └── Iris_Classification.ipynb     # Main end-to-end notebook (run this)
├── data/
│   └── iris.csv                      # Exported raw dataset (reference copy)
├── outputs/
│   ├── plots/                        # All exported evaluation/EDA plots
│   │   ├── feature_distributions.png
│   │   ├── pairplot.png
│   │   ├── correlation_heatmap.png
│   │   ├── boxplots_outliers.png
│   │   ├── confusion_matrix_heatmaps.png
│   │   ├── model_comparison_metrics.png
│   │   ├── decision_boundaries.png
│   │   └── feature_importance.png
│   └── reports/
│       ├── model_comparison_results.csv   # Full metrics table (all models)
│       └── final_summary.json             # Best model + final metrics
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🎯 Project Overview

The goal is to build and evaluate an end-to-end classification pipeline on the
classic Iris dataset (150 samples, 4 numeric features, 3 balanced classes).

**Pipeline stages implemented in the notebook:**

1. **Data Loading & Cleaning** — load via `sklearn.datasets.load_iris`, check
   for missing values, duplicates, and data types.
2. **Exploratory Data Analysis (EDA)** — feature distribution histograms,
   pair-grid (pairplot), correlation heatmap, boxplots for outlier detection.
3. **Preprocessing** — stratified train/test split (80/20) performed **before**
   scaling, with `StandardScaler` fit only on training data, to avoid data
   leakage.
4. **Model Training** — three classifiers trained and 5-fold cross-validated:
   - Logistic Regression
   - Decision Tree Classifier
   - Random Forest Classifier
5. **Evaluation** — Accuracy, macro-averaged Precision/Recall/F1-Score, full
   classification reports, and confusion matrix heatmaps for every model.
6. **Comparative Analysis** — bar chart comparing all models on all metrics.
7. **Decision Boundary Visualization** — 2D decision boundary plots (petal
   length vs. petal width) for each classifier.
8. **Feature Importance** — importance rankings from the tree-based models.
9. **Export** — all plots saved to `outputs/plots/`, metrics saved to
   `outputs/reports/`.

---

## 📊 Results Summary

| Model               | Accuracy | Precision (macro) | Recall (macro) | F1-Score (macro) |
|---------------------|:--------:|:------------------:|:----------------:|:-------------------:|
| **Random Forest**   | 0.967    | 0.970               | 0.967             | 0.967                |
| Logistic Regression | 0.933    | 0.933               | 0.933             | 0.933                |
| Decision Tree       | 0.933    | 0.933               | 0.933             | 0.933                |

**Best performing model: Random Forest Classifier**
(exact figures are re-generated on every notebook run and saved to
`outputs/reports/final_summary.json`; test-set results can vary very slightly
depending on the environment's library versions, though the random seed is
fixed for reproducibility.)

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd DevRise-Iris-Classification
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

### Option A — Run interactively in Jupyter
```bash
jupyter notebook notebooks/Iris_Classification.ipynb
```
Then run all cells: **Kernel → Restart & Run All**.

### Option B — Execute headlessly from the command line
```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/Iris_Classification.ipynb
```
This regenerates all cell outputs, plots (`outputs/plots/`), and metric
reports (`outputs/reports/`) in one command.

---

## 🧪 Technical Details

| Aspect                  | Choice                                                             |
|--------------------------|---------------------------------------------------------------------|
| Dataset                 | Iris (150 samples, 4 features, 3 classes) via `sklearn.datasets`   |
| Train/Test Split        | 80% / 20%, **stratified**, `random_state=42`                       |
| Leakage Prevention       | Scaler fit only on training data, applied to test data after split |
| Scaling                 | `StandardScaler` (zero mean, unit variance)                        |
| Models                  | Logistic Regression, Decision Tree, Random Forest                  |
| Validation               | 5-fold cross-validation on the training set                        |
| Metrics                 | Accuracy, macro Precision, macro Recall, macro F1-Score            |
| Visualization            | Confusion matrices, decision boundaries, feature importance         |

---

## 📦 Deliverables Checklist

- [x] Jupyter Notebook (`.ipynb`) with preprocessing, training, and comparative tests
- [x] Exported ML performance plots (confusion matrix heatmaps, decision boundaries)
- [x] Well-documented `README.md` with setup instructions and overview
- [x] Clean, organized project structure
- [ ] Demo video (2–5 minutes) — to be recorded separately and linked here before submission
- [ ] GitHub repository link — add after pushing this project

---

## 👤 Author

Submitted for the **DevRise Internship Program — Batch 1 (2026)**, AI & ML
Domain, Task 2. All work is original.

## 📄 License

This project is submitted for academic/internship evaluation purposes as part
of the DevRise Internship Program.
