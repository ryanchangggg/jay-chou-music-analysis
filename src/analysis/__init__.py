"""
Jay Chou Music Deep Analysis — Python Analysis Package.

This package provides all data processing, feature engineering,
clustering, NLP, and statistical analysis modules for the
Jay Chou music analysis project.

Exposed modules:
    config          — Unified project configuration
    preprocess      — Data loading, cleaning, and merging
"""

from src.analysis import config
from src.analysis import preprocess

__all__: list[str] = [
    "config",
    "preprocess",
]

__version__: str = "0.1.0"
