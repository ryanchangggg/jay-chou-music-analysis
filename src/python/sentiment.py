"""
Sentiment analysis — estimating emotional polarity and subjectivity
of Jay Chou's lyrics using lexicon-based approaches.

Employs multiple Chinese sentiment lexicons (DUTIR, HowNet) and
SnowNLP for polarity scoring. Also computes valence-lyrics sentiment
discrepancy as a signal of emotional complexity.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.python.config import MIN_LYRICS_LENGTH_FOR_SENTIMENT, RANDOM_SEED


def compute_snownlp_sentiment(
    lyrics_series: pd.Series,
    min_length: Optional[int] = None,
) -> pd.Series:
    """Compute sentiment polarity using SnowNLP (0.0 = negative, 1.0 = positive).

    Skips texts shorter than min_length characters.

    Parameters
    ----------
    lyrics_series : pd.Series
        Series of Chinese lyric strings.
    min_length : int or None
        Minimum text length for analysis. Defaults to
        MIN_LYRICS_LENGTH_FOR_SENTIMENT.

    Returns
    -------
    pd.Series
        Sentiment polarity scores. NaN for skipped texts.
    """
    ...


def compute_dutir_sentiment(
    tokenised_lyrics: List[List[str]],
) -> np.ndarray:
    """Compute sentiment polarity using DUTIR (Dalian University of Technology)
    sentiment word ontology.

    Returns a score in [-1, 1] where negative = negative emotion.

    Parameters
    ----------
    tokenised_lyrics : List[List[str]]
        List of token lists, one per song.

    Returns
    -------
    np.ndarray
        Sentiment scores per song.
    """
    ...


def compute_sentiment_delta(
    lyrics_sentiment: np.ndarray,
    valence_scores: np.ndarray,
    song_names: List[str],
) -> pd.DataFrame:
    """Compute discrepancy between lyrics sentiment and audio valence.

    A large |delta| suggests the lyrics express a different emotional
    tone than the musical arrangement.

    Parameters
    ----------
    lyrics_sentiment : np.ndarray
        Sentiment score from lyrics (-1 to 1).
    valence_scores : np.ndarray
        Spotify valence score (0 to 1), normalised to -1 to 1.
    song_names : list of str
        Song names for the result table.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: song_name, lyrics_sentiment, valence,
        delta, abs_delta. Sorted by abs_delta descending.
    """
    ...


def classify_emotion_category(
    sentiment_score: float,
    threshold: float = 0.2,
) -> str:
    """Classify a sentiment score into an emotional category.

    Parameters
    ----------
    sentiment_score : float
        Sentiment score in [-1, 1].
    threshold : float
        Threshold for neutrality. Defaults to 0.2.

    Returns
    -------
    str
        One of "positive", "negative", "neutral".
    """
    ...


def sentiment_over_time(
    df: pd.DataFrame,
    sentiment_column: str,
    year_column: str = "year",
) -> pd.DataFrame:
    """Aggregate sentiment by year to show emotional trends over time.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with year and sentiment columns.
    sentiment_column : str
        Name of the sentiment score column.
    year_column : str
        Name of the year column.

    Returns
    -------
    pd.DataFrame
        Yearly mean sentiment with song count per year.
    """
    ...


def run_sentiment_pipeline(
    df: pd.DataFrame,
    lyrics_column: str = "lyrics",
    song_column: str = "song_name",
    seed: Optional[int] = None,
) -> Dict[str, object]:
    """Run the complete sentiment analysis pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with song metadata and lyrics.
    lyrics_column : str
        Name of the lyrics text column.
    song_column : str
        Name of the song identifier column.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    Dict[str, object]
        Dictionary containing:
            - "snownlp_sentiment": array of SnowNLP scores
            - "dutir_sentiment": array of DUTIR lexicon scores
            - "sentiment_delta": DataFrame of sentiment-valence mismatches
            - "yearly_trend": DataFrame of sentiment over time
    """
    ...
