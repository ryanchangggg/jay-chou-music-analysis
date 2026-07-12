"""
Jay Chou Music Deep Analysis — Python Analysis Package.

This package provides all data processing, feature engineering,
clustering, NLP, and statistical analysis modules for the
Jay Chou music analysis project.

Exposed modules:
    config          — Unified project configuration
    preprocess      — Data loading, cleaning, and merging
    features        — Feature engineering and scaling
    clustering      — KMeans clustering and anomaly detection
    lyrics          — Chinese NLP (tokenization, LDA topic modeling)
    sentiment       — Lyric sentiment analysis
    stats           — Statistical hypothesis testing
"""

from src.python import config
from src.python import preprocess
from src.python import features
from src.python import clustering
from src.python import lyrics
from src.python import sentiment
from src.python import stats

__all__: list[str] = [
    "config",
    "preprocess",
    "features",
    "clustering",
    "lyrics",
    "sentiment",
    "stats",
]

__version__: str = "0.1.0"
