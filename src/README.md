# Source Code

```
src/
├── python/     # Python analysis package
└── web/        # React frontend application (separate project)
```

## Python Package

The `src/python/` package provides the data analysis backend:

| Module | Purpose |
|--------|---------|
| `config.py` | Unified paths, column names, analysis parameters |
| `preprocess.py` | Data loading, cleaning, and merging |
| `features.py` | Feature engineering and scaling |
| `clustering.py` | KMeans clustering and anomaly detection |
| `lyrics.py` | Chinese NLP (Jieba, TF-IDF, LDA) |
| `sentiment.py` | Lyric sentiment analysis |
| `stats.py` | Statistical hypothesis testing |

## Web Application

The `src/web/` directory contains the React + TypeScript frontend
(initialised separately with Vite).
