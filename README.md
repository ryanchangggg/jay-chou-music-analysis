# Jay Chou Music Deep Analysis

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **26 years, 16 albums, 174 songs.** An interactive data storytelling project that
> explores Jay Chou's musical evolution through Spotify audio features, lyrics NLP,
> clustering, and statistical analysis.

---

## Provocative Finding

> **《双截棍》is not just iconic — it's a statistical outlier.** With energy at 0.85 (top 2%),
> tempo at 106 BPM (fastest 5%), and speechiness at 0.30 (top 1%), Isolation Forest
> ranks it as the single most "un-Jay-Chou" song in the entire catalog — yet it's
> also the song that defined his global image.

## What This Project Does

| Page | Question Answered |
|---|---|
| Panorama | What does 26 years of Jay Chou look like at a glance? |
| Era | How did his sound drift across decades? |
| Style Fingerprint | Do Chinese-wind songs have a quantifiable audio signature? |
| Creator Code | Do lyricists leave measurable fingerprints on songs? |
| Lyric Lens | How do lyrical themes and sentiment evolve over time? |
| Outliers | Which songs are statistically the "least Jay Chou"? |
| Explorer | Freely explore and compare any songs across all 8 audio features. |

## Skills Demonstrated

| Area | Tools & Techniques |
|---|---|
| Data Engineering | Pandas, scikit-learn pipelines, data merging & cleaning |
| Machine Learning | KMeans clustering, PCA, Isolation Forest, Random Forest |
| NLP | Jieba tokenization, TF-IDF, LDA topic modeling, sentiment analysis |
| Statistics | ANOVA, effect size, Kruskal-Wallis, post-hoc tests |
| Visualization | ECharts, D3.js, radar charts, confusion matrices, 3D scatter plots |
| Web App | React 18, TypeScript, Vite, Tailwind CSS |

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/jay-chou-music-analysis.git
cd jay-chou-music-analysis

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
make install

# 3. Run the data pipeline
make data

# 4. Explore with notebooks
make notebooks     # launches Jupyter Lab
```

## Project Structure

```
jay-chou-music-analysis/
├── data/
│   ├── raw/             # Raw CSV files (read-only)
│   └── processed/       # Preprocessed JSON for frontend
├── notebooks/           # Jupyter analysis notebooks
├── src/
│   └── python/          # Python analysis package
│       ├── config.py         # Unified configuration
│       ├── preprocess.py     # Data cleaning & merging
│       ├── features.py       # Feature engineering
│       ├── clustering.py     # Clustering & anomaly detection
│       ├── lyrics.py         # Lyrics NLP (tokenization, LDA)
│       ├── sentiment.py      # Sentiment analysis
│       └── stats.py          # Statistical tests
├── models/              # Serialized ML models
├── docs/                # Documentation & PRD
├── reports/             # Generated visual outputs
└── assets/              # Static resources
```

## Data Sources

- **Spotify Web API** — Audio features (danceability, energy, valence, tempo, acousticness, etc.)
- **Manual collection** — Lyrics, album metadata, style tags, album covers (Wikimedia Commons)

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- Data collected via Spotify Web API for educational analysis purposes
- Jay Chou for 26 years of groundbreaking music
- Album cover images from Wikimedia Commons (Fair Use)
