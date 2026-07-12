"""
Clustering and anomaly detection — unsupervised learning on Jay Chou's
audio features to discover style groups and statistical outliers.

Uses KMeans (with elbow method for optimal k) for clustering and
Isolation Forest for anomaly detection. PCA is applied for visualisation.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest

from src.python.config import (
    DEFAULT_N_CLUSTERS,
    ISOLATION_FOREST_CONTAMINATION,
    ISOLATION_FOREST_N_ESTIMATORS,
    N_CLUSTERS_RANGE,
    PCA_N_COMPONENTS_2D,
    PCA_N_COMPONENTS_3D,
    RANDOM_SEED,
)


def find_optimal_k(
    features: np.ndarray,
    k_range: Optional[range] = None,
    seed: Optional[int] = None,
) -> Tuple[int, Dict[int, float]]:
    """Run elbow method to find the optimal number of clusters.

    Parameters
    ----------
    features : np.ndarray
        Scaled feature matrix.
    k_range : range or None
        Range of k values to evaluate. Defaults to N_CLUSTERS_RANGE.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    Tuple[int, Dict[int, float]]
        Optimal k and a dict of {k: inertia} for all evaluated values.
    """
    ...


def fit_kmeans(
    features: np.ndarray,
    n_clusters: Optional[int] = None,
    seed: Optional[int] = None,
) -> KMeans:
    """Fit a KMeans model on the feature matrix.

    Parameters
    ----------
    features : np.ndarray
        Scaled feature matrix.
    n_clusters : int or None
        Number of clusters. Defaults to DEFAULT_N_CLUSTERS.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    KMeans
        Fitted KMeans model.
    """
    ...


def compute_pca(
    features: np.ndarray,
    n_components: Optional[int] = None,
    seed: Optional[int] = None,
) -> Tuple[PCA, np.ndarray]:
    """Compute PCA decomposition for visualisation.

    Parameters
    ----------
    features : np.ndarray
        Scaled feature matrix.
    n_components : int or None
        Number of principal components. Defaults to PCA_N_COMPONENTS_2D.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    Tuple[PCA, np.ndarray]
        Fitted PCA object and the transformed coordinates.
    """
    ...


def fit_isolation_forest(
    features: np.ndarray,
    contamination: Optional[float] = None,
    n_estimators: Optional[int] = None,
    seed: Optional[int] = None,
) -> IsolationForest:
    """Fit an Isolation Forest model for anomaly detection.

    Parameters
    ----------
    features : np.ndarray
        Scaled feature matrix.
    contamination : float or None
        Expected proportion of outliers. Defaults to ISOLATION_FOREST_CONTAMINATION.
    n_estimators : int or None
        Number of base estimators. Defaults to ISOLATION_FOREST_N_ESTIMATORS.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    IsolationForest
        Fitted Isolation Forest model.
    """
    ...


def score_anomalies(
    model: IsolationForest,
    features: np.ndarray,
) -> np.ndarray:
    """Compute anomaly scores for each sample.

    Lower scores indicate more anomalous samples.

    Parameters
    ----------
    model : IsolationForest
        Fitted Isolation Forest model.
    features : np.ndarray
        Scaled feature matrix.

    Returns
    -------
    np.ndarray
        Anomaly scores (lower = more anomalous).
    """
    ...


def run_clustering_pipeline(
    features: np.ndarray,
    song_names: List[str],
    n_clusters: Optional[int] = None,
    seed: Optional[int] = None,
) -> Dict[str, object]:
    """Run the complete clustering and anomaly detection pipeline.

    Parameters
    ----------
    features : np.ndarray
        Scaled feature matrix.
    song_names : list of str
        Corresponding song names for result annotation.
    n_clusters : int or None
        Number of clusters. Defaults to optimal found via elbow method.
    seed : int or None
        Random seed. Defaults to RANDOM_SEED.

    Returns
    -------
    Dict[str, object]
        Dictionary with keys:
            - "cluster_labels": array of cluster assignments
            - "cluster_centers": cluster centroids
            - "anomaly_scores": anomaly scores
            - "anomaly_flags": boolean array (-1 = anomaly)
            - "pca_2d": 2D PCA coordinates
            - "pca_3d": 3D PCA coordinates (or None)
            - "explained_variance": PCA explained variance ratio
            - "silhouette_score": silhouette score for the clustering
    """
    ...
