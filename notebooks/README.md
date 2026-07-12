# Analysis Notebooks

Jupyter notebooks for the Jay Chou Music Deep Analysis project.

## Notebooks (in order)

| # | Notebook | Contents |
|---|----------|----------|
| 01 | `01_eda.ipynb` | Exploratory Data Analysis — feature distributions, correlations, missing values |
| 02 | `02_clustering.ipynb` | KMeans clustering, PCA visualisation, Isolation Forest anomaly detection |
| 03 | `03_lyrics_analysis.ipynb` | Jieba tokenisation, TF-IDF, LDA topic modelling, keywords extraction |
| 04 | `04_statistical_tests.ipynb` | ANOVA, Kruskal-Wallis, effect sizes, pairwise comparisons |
| 05 | `05_classifier.ipynb` | Random Forest style classifier, feature importance, confusion matrix |
| 06 | `06_prepare_frontend_data.ipynb` | Export all analysis results as processed JSON for the frontend |

## Usage

```bash
# Launch from project root
make notebooks

# Or directly
jupyter lab notebooks/
```
