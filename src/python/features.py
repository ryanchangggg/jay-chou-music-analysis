"""
Feature engineering — standardisation, dimensionality reduction,
and derived feature creation for Jay Chou audio data.

Transforms raw Spotify features into analysis-ready representations
including scaled values, principal components, and composite indices.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from src.python.config import (
    AUDIO_FEATURES,
    SCALE_COLUMNS,
    RANDOM_SEED,
)


def create_feature_matrix(
    df: pd.DataFrame,
    feature_columns: Optional[List[str]] = None,
) -> np.ndarray:
    """Extract a numeric feature matrix from the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing audio feature columns.
    feature_columns : list of str or None
        Columns to include. Defaults to AUDIO_FEATURES.

    Returns
    -------
    np.ndarray
        2D feature matrix of shape (n_songs, n_features).
    """
    ...


def fit_scaler(
    features: np.ndarray,
) -> StandardScaler:
    """Fit a StandardScaler on the feature matrix.

    Parameters
    ----------
    features : np.ndarray
        Raw feature matrix.

    Returns
    -------
    StandardScaler
        Fitted scaler object.
    """
    ...


def scale_features(
    features: np.ndarray,
    scaler: Optional[StandardScaler] = None,
) -> np.ndarray:
    """Scale features using a fitted StandardScaler.

    If no scaler is provided, fits a new one on the given features.

    Parameters
    ----------
    features : np.ndarray
        Feature matrix to scale.
    scaler : StandardScaler or None
        Pre-fitted scaler. If None, a new scaler is fit.

    Returns
    -------
    np.ndarray
        Scaled feature matrix.
    """
    ...


def compute_valence_energy_quadrant(df: pd.DataFrame) -> pd.DataFrame:
    """Assign each song to a quadrant based on valence and energy medians.

    Quadrants:
        - High Energy / High Valence (Exciting)
        - High Energy / Low Valence  (Tense)
        - Low Energy  / High Valence (Calm)
        - Low Energy  / Low Valence  (Melancholic)

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with valence and energy columns.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with an added 'quadrant' column.
    """
    ...


def compute_danceability_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    """Compute danceability-per-energy ratio as a dance efficiency metric.

    High ratio = energetic but not bouncy; low ratio = easy to dance to.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with danceability and energy columns.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with an added 'dance_efficiency' column.
    """
    ...


def build_feature_pipeline(
    df: pd.DataFrame,
    scale: bool = True,
) -> Tuple[np.ndarray, Dict[str, object]]:
    """Run the complete feature engineering pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with audio feature columns.
    scale : bool
        Whether to apply StandardScaler.

    Returns
    -------
    Tuple[np.ndarray, Dict[str, object]]
        Feature matrix and metadata dict (scaler, feature_names).
    """
    ...
