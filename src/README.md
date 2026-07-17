# Source Code

```
src/
├── analysis/   # Python analysis package
└── frontend/   # Vite vanilla-JS data-narrative app (separate project)
```

## Analysis Package

The `src/analysis/` package provides the data analysis backend:

| Module | Purpose |
|--------|---------|
| `config.py` | Unified paths, column names, analysis parameters |
| `preprocess.py` | Data loading, cleaning, and merging |
| `eda.py` | Exploratory data analysis visualizations |
| `cluster_analysis.py` | KMeans clustering, PCA, anomaly detection |
| `lyrics_analysis.py` | Chinese NLP (Jieba, TF-IDF, LDA) |
| `music_evolution.py` | Temporal feature evolution analysis |
| `popularity_prediction.py` | Popularity prediction model |
| `song_recommender.py` | Content-based song recommendation |
| `generate_dashboard.py` | Interactive dashboard generation |

## Frontend Application

The `src/frontend/` directory contains the interactive SPA built with
Vite and vanilla JavaScript. See the root `README.md` for setup instructions.
