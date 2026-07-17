# Jay Chou Music Deep Analysis

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **26 years, 16 albums, 174 songs.** An interactive data-narrative project exploring Jay Chou's musical evolution through Spotify audio features, NLP on Chinese lyrics, clustering analysis, and statistical modeling.

---

## Core Finding

> **"Double Blade" isn't just iconic — it's a statistical outlier.** With energy at 0.85 (top 2%), tempo at 106 BPM (top 5%), and speechiness at 0.30 (top 1%), Isolation Forest flags it as the most "un-Jay-like" song in the entire catalog — yet it's the track that defined his global image.

## Project Capabilities

| Page | Question Answered |
|------|-------------------|
| Overview | What does 26 years of Jay Chou look like? |
| Eras | How has his style evolved across eras? |
| Style Fingerprint | Do Chinese-style songs have quantifiable audio signatures? |
| Creator Fingerprint | Do different lyricists leave measurable fingerprints? |
| Lyrics Lens | How have lyrics themes and sentiment changed over time? |
| Outliers | Which songs are statistically "least Jay-like"? |
| Explorer | Freely browse and compare audio features across any song. |

## Skills Demonstrated

| Domain | Tools & Techniques |
|--------|-------------------|
| Data Engineering | Pandas, scikit-learn pipelines, data merging & cleaning |
| Machine Learning | KMeans clustering, PCA, Isolation Forest, Random Forest |
| NLP | Jieba tokenization, TF-IDF, LDA topic modeling, sentiment analysis |
| Statistics | ANOVA, effect size, Kruskal-Wallis, post-hoc tests |
| Visualization | ECharts, D3.js, radar charts, confusion matrices, 3D scatter plots |
| Frontend | Vite, vanilla JavaScript, responsive design, interactive data narratives |

## Interactive Website

The project includes a complete interactive data-narrative website at `src/frontend/`:

```bash
cd src/frontend
npm install        # Install dependencies
npx vite build     # Production build
npx vite preview   # Local preview
```

Features:
- **Apple × Spotify Wrapped** visual design
- **8 narrative chapters**: Intro → Overview → Evolution → Lyrics → Clustering → Explorer → Recommender → About
- **Chinese / English toggle**
- **Scroll-driven animations** with Intersection Observer
- **Interactive charts** (hover, zoom, filter)

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/ryanchangggg/jay-chou-music-analysis.git
cd jay-chou-music-analysis

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
make install

# 3. Run the data pipeline
make data

# 4. (Optional) Start the frontend dev server
cd src/frontend && npm install && npx vite
```

## Project Structure

```
jay-chou-music-analysis/
├── data/
│   ├── raw/             # Raw CSV files (read-only source data)
│   ├── processed/       # Preprocessed datasets for analysis & frontend
│   └── stopwords/       # Chinese stopword lists for NLP
├── src/
│   ├── analysis/        # Python analysis package
│   │   ├── config.py         # Unified paths, columns, parameters
│   │   ├── preprocess.py     # Data cleaning & merging pipeline
│   │   ├── eda.py            # EDA figures (8 PNG: missing values, boxplots, etc.)
│   │   ├── cluster_analysis.py   # KMeans, PCA, HDBSCAN, UMAP clustering
│   │   ├── lyrics_analysis.py    # NLP: Jieba, TF-IDF, LDA, SnowNLP
│   │   ├── music_evolution.py    # Feature evolution + bilingual report
│   │   ├── popularity_prediction.py  # RF/XGB/LGBM/CatBoost + SHAP
│   │   ├── song_recommender.py   # Cosine/KNN/PCA recommender
│   │   └── generate_dashboard.py # Standalone Plotly dashboard HTML
│   └── frontend/        # Interactive SPA (Vite + vanilla JS)
│       ├── index.html         # Entry point
│       ├── package.json       # Node dependencies (Chart.js, Vite)
│       ├── vite.config.js     # Vite build configuration
│       ├── src/               # Vanilla JS application code
│       │   ├── main.js        # App bootstrap, scroll nav, section builders
│       │   ├── charts.js      # All Chart.js chart functions (20 charts)
│       │   ├── data.js        # Data loading + aggregation utilities
│       │   ├── i18n.js        # zh-CN / zh-TW translations (~150 keys)
│       │   └── styles.css     # Apple-inspired responsive styles
│       ├── public/data/       # JSON data for frontend (from data/processed/)
│       └── dist/              # Production build output
├── outputs/             # Generated figures and reports
│   ├── figures/             # 30+ PNG plots + 4 interactive HTMLs
│   ├── music_evolution_report.md
│   └── analysis_summary.txt   # Lyrics analysis text summary
├── docs/                # Documentation & PRD
├── Makefile             # Automation commands
└── requirements.txt     # Python dependencies
```

## Analysis Methods

### 1. Audio Feature Analysis
- 11 audio features from Spotify Web API
- PCA dimensionality reduction for music space visualization
- UMAP for non-linear manifold learning
- KMeans and HDBSCAN for song clustering

### 2. Lyrics Analysis
- Jieba Chinese word segmentation
- TF-IDF keyword extraction
- LDA topic modeling
- SnowNLP sentiment analysis

### 3. Popularity Prediction
- Random Forest, XGBoost, LightGBM, CatBoost model comparison
- SHAP model explanations
- Partial dependence plots

### 4. Recommender System
- Content-based collaborative filtering
- Cosine similarity, KNN, PCA embedding methods
- Interactive recommender demo

## Data Sources

- **Spotify Web API** — Audio features (danceability, energy, valence, tempo, acousticness, etc.)
- **Manual collection** — Lyrics, album metadata, style tags, album covers (Wikimedia Commons)

## License

MIT License — see [LICENSE](LICENSE)

## Acknowledgements

- Data collected via Spotify Web API for educational analysis only
- Thanks to Jay Chou for 26 years of groundbreaking music
- Album cover images from Wikimedia Commons (fair use)
