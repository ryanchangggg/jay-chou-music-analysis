"""
Statistical hypothesis testing — comparing audio features across
style groups, lyricists, albums, and time periods.

Provides ANOVA, Kruskal-Wallis, effect size, and post-hoc tests
to quantify whether observed differences are statistically significant.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import f_oneway, kruskal

from src.python.config import ANOVA_ALPHA, AUDIO_FEATURES, RANDOM_SEED


def anova_by_group(
    df: pd.DataFrame,
    feature: str,
    group_column: str,
) -> Dict[str, object]:
    """Perform one-way ANOVA to test if feature means differ across groups.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the feature and group columns.
    feature : str
        Name of the numeric feature column.
    group_column : str
        Name of the categorical group column.

    Returns
    -------
    Dict[str, object]
        Dictionary with keys: "f_statistic", "p_value", "significant",
        "group_means" (dict), "group_counts" (dict).
    """
    ...


def kruskal_wallis_by_group(
    df: pd.DataFrame,
    feature: str,
    group_column: str,
) -> Dict[str, object]:
    """Perform Kruskal-Wallis H-test (non-parametric alternative to ANOVA).

    Used when normality or homoscedasticity assumptions are violated.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the feature and group columns.
    feature : str
        Name of the numeric feature column.
    group_column : str
        Name of the categorical group column.

    Returns
    -------
    Dict[str, object]
        Dictionary with keys: "h_statistic", "p_value", "significant".
    """
    ...


def compute_effect_size(
    df: pd.DataFrame,
    feature: str,
    group_column: str,
) -> Dict[str, float]:
    """Compute eta-squared (ANOVA) or epsilon-squared (Kruskal-Wallis)
    as a measure of effect size.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the feature and group columns.
    feature : str
        Name of the numeric feature column.
    group_column : str
        Name of the categorical group column.

    Returns
    -------
    Dict[str, float]
        Dictionary with keys: "eta_squared", "interpretation".
    """
    ...


def pairwise_tukey_hsd(
    df: pd.DataFrame,
    feature: str,
    group_column: str,
) -> pd.DataFrame:
    """Perform Tukey HSD post-hoc test for pairwise group comparisons.

    Only meaningful if ANOVA was significant.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with the feature and group columns.
    feature : str
        Name of the numeric feature column.
    group_column : str
        Name of the categorical group column.

    Returns
    -------
    pd.DataFrame
        Pairwise comparison results with columns: group1, group2,
        meandiff, p_adjusted, reject, significant.
    """
    ...


def compare_lyricists(
    df: pd.DataFrame,
    lyricist_column: str = "lyricist",
    min_songs: int = 5,
) -> Dict[str, pd.DataFrame]:
    """Compare audio features between lyricists with enough data.

    Filters to lyricists with >= min_songs, then runs ANOVA
    and effect size for each audio feature.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with lyricist and audio feature columns.
    lyricist_column : str
        Name of the lyricist column.
    min_songs : int
        Minimum songs per lyricist to include.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary with keys:
            - "feature_comparison": per-feature ANOVA results
            - "lyricist_means": mean features per lyricist
    """
    ...


def compare_tags(
    df: pd.DataFrame,
    tag_column: str = "tags",
    min_songs: int = 5,
) -> Dict[str, pd.DataFrame]:
    """Compare audio features between style tags.

    Since songs can have multiple tags, this uses a one-vs-rest approach
    for each tag with enough songs.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with tags and audio feature columns.
    tag_column : str
        Name of the tags column (pipe-separated).
    min_songs : int
        Minimum songs per tag to include.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of per-feature comparison results.
    """
    ...


def compare_eras(
    df: pd.DataFrame,
    year_column: str = "year",
    era_breaks: Optional[List[int]] = None,
) -> Dict[str, object]:
    """Compare audio features across defined musical eras.

    Default eras:
        - Golden Age (2000-2004): debut to peak creativity
        - Mature Era (2005-2010): refined style
        - Middle Era (2011-2016): experimentation
        - Recent Era (2017-2026): consolidation

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with year and audio feature columns.
    year_column : str
        Name of the year column.
    era_breaks : list of int or None
        Break points for era boundaries.

    Returns
    -------
    Dict[str, object]
        Dictionary with per-feature ANOVA, effect sizes, and era means.
    """
    ...


def correlation_analysis(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Compute Pearson correlation matrix for specified numeric columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with numeric columns.
    columns : list of str or None
        Columns to correlate. Defaults to all AUDIO_FEATURES + popularity.

    Returns
    -------
    pd.DataFrame
        Correlation matrix.
    """
    ...


def run_stats_pipeline(
    df: pd.DataFrame,
    seed: Optional[int] = None,
) -> Dict[str, object]:
    """Run the complete statistical analysis pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        Unified DataFrame with all features and metadata.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    Dict[str, object]
        Dictionary with all statistical test results.
    """
    ...
