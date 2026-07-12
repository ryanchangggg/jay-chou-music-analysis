"""
Lyrics NLP — Chinese text processing for Jay Chou's song lyrics.

Provides tokenisation (Jieba with custom dictionary), TF-IDF keyword
extraction, LDA topic modelling, and vocabulary analysis.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.python.config import (
    LDA_N_TOPICS,
    LDA_N_PASSES,
    LDA_TOP_N_WORDS,
    RANDOM_SEED,
    WORDCLOUD_TOP_N,
)


def load_jieba_custom_dict(path: Optional[str] = None) -> None:
    """Load a custom Jieba dictionary with Jay Chou-specific vocabulary.

    Adds song-specific terms, artist names, and creative vocabulary
    to improve tokenisation accuracy.

    Parameters
    ----------
    path : str or None
        Path to custom dictionary file. If None, uses a default built-in list.
    """
    ...


def tokenise_lyrics(
    lyrics_series: pd.Series,
    stopwords: Optional[List[str]] = None,
) -> List[List[str]]:
    """Tokenise a series of lyrics texts using Jieba.

    Parameters
    ----------
    lyrics_series : pd.Series
        Series of Chinese lyric strings.
    stopwords : list of str or None
        List of stopwords to filter out. If None, a default Chinese
        stopword list is used.

    Returns
    -------
    List[List[str]]
        List of token lists, one per song.
    """
    ...


def compute_tfidf(
    tokenised_lyrics: List[List[str]],
    max_features: Optional[int] = None,
) -> Tuple[np.ndarray, List[str]]:
    """Compute TF-IDF weighted term matrix from tokenised lyrics.

    Parameters
    ----------
    tokenised_lyrics : List[List[str]]
        List of token lists, one per song.
    max_features : int or None
        Maximum number of features for the vectorizer.

    Returns
    -------
    Tuple[np.ndarray, List[str]]
        TF-IDF matrix (n_songs, n_features) and feature names.
    """
    ...


def get_top_keywords(
    tfidf_matrix: np.ndarray,
    feature_names: List[str],
    top_n: Optional[int] = None,
) -> List[List[Tuple[str, float]]]:
    """Extract top-N keywords per song from TF-IDF matrix.

    Parameters
    ----------
    tfidf_matrix : np.ndarray
        TF-IDF feature matrix.
    feature_names : list of str
        Vocabulary feature names.
    top_n : int or None
        Number of keywords per song. Defaults to WORDCLOUD_TOP_N.

    Returns
    -------
    List[List[Tuple[str, float]]]
        Per-song list of (keyword, weight) tuples.
    """
    ...


def fit_lda_model(
    tokenised_lyrics: List[List[str]],
    n_topics: Optional[int] = None,
    n_passes: Optional[int] = None,
    seed: Optional[int] = None,
) -> Tuple[object, np.ndarray]:
    """Fit an LDA topic model on tokenised lyrics.

    Parameters
    ----------
    tokenised_lyrics : List[List[str]]
        List of token lists.
    n_topics : int or None
        Number of topics. Defaults to LDA_N_TOPICS.
    n_passes : int or None
        Number of passes. Defaults to LDA_N_PASSES.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    Tuple[object, np.ndarray]
        Trained LDA model and document-topic distribution matrix.
    """
    ...


def get_topic_keywords(
    lda_model: object,
    n_words: Optional[int] = None,
) -> List[List[Tuple[str, float]]]:
    """Extract top-N keywords for each topic from a fitted LDA model.

    Parameters
    ----------
    lda_model : object
        Fitted Gensim LDA model.
    n_words : int or None
        Words per topic. Defaults to LDA_TOP_N_WORDS.

    Returns
    -------
    List[List[Tuple[str, float]]]
        Per-topic list of (keyword, weight) tuples.
    """
    ...


def get_overall_word_frequencies(
    tokenised_lyrics: List[List[str]],
) -> Dict[str, int]:
    """Compute global word frequency across all lyrics.

    Parameters
    ----------
    tokenised_lyrics : List[List[str]]
        List of token lists.

    Returns
    -------
    Dict[str, int]
        Word-to-frequency mapping, sorted descending.
    """
    ...


def run_lyrics_pipeline(
    df: pd.DataFrame,
    lyrics_column: str = "lyrics",
    song_column: str = "song_name",
    seed: Optional[int] = None,
) -> Dict[str, object]:
    """Run the complete lyrics analysis pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with song_name and lyrics columns.
    lyrics_column : str
        Name of the lyrics text column.
    song_column : str
        Name of the song identifier column.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    Dict[str, object]
        Dictionary with keys:
            - "tokenised_lyrics"
            - "top_keywords"
            - "word_frequencies"
            - "lda_model"
            - "document_topic_distribution"
            - "topic_keywords"
    """
    ...
