#!/usr/bin/env python3
"""
周杰伦歌曲聚类分析
基于 Spotify 音频特征

使用: PCA / UMAP / KMeans / HDBSCAN
输出: 交互式 Plotly HTML 可视化
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import hdbscan
import umap

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ── 配置 ──────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data/raw/spotify_features.csv")
DISC_PATH = os.path.join(PROJECT_ROOT, "data/raw/jay_discography.csv")
OUTPUT_HTML = os.path.join(PROJECT_ROOT, "reports/figures/clustering_interactive.html")

# Features to use for clustering
FEATURE_COLS = [
    "danceability", "energy", "valence", "tempo",
    "acousticness", "instrumentalness", "speechiness",
    "loudness", "key", "duration_ms", "popularity", "mode",
]

np.random.seed(42)


# ── 1. 加载数据 ────────────────────────────────────────────────────
def load_data():
    features = pd.read_csv(DATA_PATH)
    disc = pd.read_csv(DISC_PATH)[["song_name", "album_cn", "album_en", "release_date"]]
    df = features.merge(disc, on="song_name", how="left")
    df["album_en"] = df["album_en"].fillna("Unknown")
    df["year"] = pd.to_datetime(df["release_date"]).dt.year
    print(f"Loaded {len(df)} songs with {len(FEATURE_COLS)} features")
    return df


# ── 2. 标准化 ──────────────────────────────────────────────────
def standardize(df):
    X = df[FEATURE_COLS].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, scaler


# ── 3. PCA 降维 ──────────────────────────────────────────────────────────
def compute_pca(X_scaled):
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    var_explained = pca.explained_variance_ratio_.sum()
    print(f"PCA 2D explains {var_explained:.1%} variance")
    components_df = pd.DataFrame({
        "feature": FEATURE_COLS,
        "PC1": pca.components_[0],
        "PC2": pca.components_[1],
    })
    return X_pca, pca, components_df


# ── 4. UMAP 降维 ─────────────────────────────────────────────────────────
def compute_umap(X_scaled):
    reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15,
                        min_dist=0.1, metric="euclidean")
    X_umap = reducer.fit_transform(X_scaled)
    print(f"UMAP 2D computed ({X_umap.shape})")
    return X_umap, reducer


# ── 5. KMeans + 自动选 k ──────────────────────────────────────────────
def find_optimal_k(X_scaled, k_range=range(2, 13)):
    scores = []
    models = {}
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        try:
            sil = silhouette_score(X_scaled, labels)
        except Exception:
            sil = -1
        scores.append({"k": k, "silhouette": sil})
        models[k] = (km, labels)
    scores_df = pd.DataFrame(scores)
    best_k = scores_df.loc[scores_df["silhouette"].idxmax(), "k"]
    print(f"Optimal K (silhouette): k={int(best_k)} with score={scores_df['silhouette'].max():.3f}")
    print("\nk vs Silhouette:")
    print(scores_df.to_string(index=False))
    return int(best_k), models, scores_df


# ── 6. HDBSCAN + 自动调参 ────────────────────────────────────────
def find_optimal_hdbscan(X_scaled):
    results = []
    models = {}
    best_sil = -1
    best_min_cluster = 5
    for min_size in range(3, 16):
        for min_samples in [None, min_size, min_size // 2]:
            try:
                clusterer = hdbscan.HDBSCAN(
                    min_cluster_size=min_size,
                    min_samples=min_samples if min_samples else None,
                    gen_min_span_tree=False,
                    prediction_data=False,
                )
                labels = clusterer.fit_predict(X_scaled)
                n_clusters = len(set(labels) - {-1})
                n_noise = sum(labels == -1)
                if n_clusters >= 2:
                    sil = silhouette_score(X_scaled, labels)
                else:
                    sil = -1
                noise_pct = n_noise / len(labels) * 100
                entry = {
                    "min_cluster_size": min_size,
                    "min_samples": str(min_samples),
                    "n_clusters": n_clusters,
                    "noise_pct": round(noise_pct, 1),
                    "silhouette": round(sil, 3),
                }
                results.append(entry)
                if sil > best_sil:
                    best_sil = sil
                    best_min_cluster = min_size
                    best_min_samples = min_samples
                models[(min_size, str(min_samples))] = (clusterer, labels)
            except Exception:
                continue
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("silhouette", ascending=False)
    print("\nHDBSCAN top-5 parameter combos by silhouette:")
    print(results_df.head(5).to_string(index=False))
    best_entry = results_df.iloc[0]
    print(f"\nOptimal HDBSCAN: min_cluster_size={int(best_entry['min_cluster_size'])}, "
          f"min_samples={best_entry['min_samples']}, "
          f"clusters={int(best_entry['n_clusters'])}, "
          f"silhouette={best_entry['silhouette']:.3f}")
    return results_df, models, dict(best_entry)


# ── 7. 交互可视化 ────────────────────────────────────
def build_interactive_chart(df, X_pca, X_umap, best_k, best_km_labels,
                            hdbscan_labels, best_hdbscan_entry,
                            pca_components):
    colors_km = px.colors.qualitative.Set2
    colors_hdb = px.colors.qualitative.Set1

    # Build hover texts
    df["hover_km"] = df.apply(
        lambda r: f"<b>{r['song_name']}</b><br>Album: {r['album_en']}<br>Year: {r['year']}<br>Cluster: {r['km_label']}"
                   f"<br>Dance: {r['danceability']:.2f} | Energy: {r['energy']:.2f}"
                   f"<br>Valence: {r['valence']:.2f} | Acoustic: {r['acousticness']:.2f}"
                   f"<br>Popularity: {r['popularity']:.0f}",
        axis=1,
    )
    df["hover_hdb"] = df.apply(
        lambda r: f"<b>{r['song_name']}</b><br>Album: {r['album_en']}<br>Year: {r['year']}<br>Cluster: {r['hdb_label']}"
                   f"<br>Dance: {r['danceability']:.2f} | Energy: {r['energy']:.2f}"
                   f"<br>Valence: {r['valence']:.2f} | Acoustic: {r['acousticness']:.2f}"
                   f"<br>Popularity: {r['popularity']:.0f}",
        axis=1,
    )

    # Build figure: 2 rows x 3 cols
    # (1,1) PCA+KMeans | (1,2) PCA+HDBSCAN | (1,3) Metrics table
    # (2,1) UMAP+KMeans | (2,2) UMAP+HDBSCAN | (2,3) Feature table
    fig = make_subplots(
        rows=2, cols=3,
        column_widths=[0.40, 0.40, 0.20],
        row_heights=[0.5, 0.5],
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}, {"type": "table"}],
            [{"type": "scatter"}, {"type": "scatter"}, {"type": "table"}],
        ],
        subplot_titles=(
            "PCA + KMeans", "PCA + HDBSCAN", "Metrics",
            "UMAP + KMeans", "UMAP + HDBSCAN", "Feature Contributions",
        ),
        horizontal_spacing=0.06,
        vertical_spacing=0.12,
    )

    # ── PCA + KMeans ──
    for cluster_id in sorted(df["km_label"].unique()):
        mask = df["km_label"] == cluster_id
        c = colors_km[int(cluster_id) % len(colors_km)]
        fig.add_trace(
            go.Scatter(
                x=X_pca[mask, 0], y=X_pca[mask, 1],
                mode="markers",
                name=f"Cluster {cluster_id}",
                legendgroup=f"km_{cluster_id}",
                marker=dict(size=7, color=c, line=dict(width=0.5, color="white")),
                text=df.loc[mask, "hover_km"],
                hoverinfo="text",
            ),
            row=1, col=1,
        )

    # ── PCA + HDBSCAN ──
    for cluster_id in sorted(df["hdb_label"].unique()):
        mask = df["hdb_label"] == cluster_id
        if cluster_id == "-1":  # Noise
            c = "#aaaaaa"
            label = "Noise"
            sym = "x"
        else:
            c = colors_hdb[hash(cluster_id) % len(colors_hdb)]
            label = f"Cluster {cluster_id}"
            sym = "circle"
        fig.add_trace(
            go.Scatter(
                x=X_pca[mask, 0], y=X_pca[mask, 1],
                mode="markers",
                name=label, legendgroup=f"hdb_{cluster_id}",
                marker=dict(size=7, color=c, symbol=sym,
                            line=dict(width=0.5, color="white")),
                text=df.loc[mask, "hover_hdb"],
                hoverinfo="text",
            ),
            row=1, col=2,
        )

    # ── UMAP + KMeans ──
    for cluster_id in sorted(df["km_label"].unique()):
        mask = df["km_label"] == cluster_id
        c = colors_km[int(cluster_id) % len(colors_km)]
        fig.add_trace(
            go.Scatter(
                x=X_umap[mask, 0], y=X_umap[mask, 1],
                mode="markers",
                name=f"Cluster {cluster_id}",
                legendgroup=f"km_{cluster_id}",
                marker=dict(size=7, color=c, line=dict(width=0.5, color="white")),
                text=df.loc[mask, "hover_km"],
                hoverinfo="text",
                showlegend=False,
            ),
            row=2, col=1,
        )

    # ── UMAP + HDBSCAN ──
    for cluster_id in sorted(df["hdb_label"].unique()):
        mask = df["hdb_label"] == cluster_id
        if cluster_id == "-1":
            c = "#aaaaaa"
            sym = "x"
        else:
            c = colors_hdb[hash(cluster_id) % len(colors_hdb)]
            sym = "circle"
        fig.add_trace(
            go.Scatter(
                x=X_umap[mask, 0], y=X_umap[mask, 1],
                mode="markers",
                name="Noise" if cluster_id == "-1" else f"Cluster {cluster_id}", legendgroup=f"hdb_{cluster_id}",
                marker=dict(size=7, color=c, symbol=sym,
                            line=dict(width=0.5, color="white")),
                text=df.loc[mask, "hover_hdb"],
                hoverinfo="text",
                showlegend=False,
            ),
            row=2, col=2,
        )

    # ── Metrics Table ──
    n_clusters_hdb = int(best_hdbscan_entry["n_clusters"])
    noise_hdb = best_hdbscan_entry["noise_pct"]
    sil_hdb = best_hdbscan_entry["silhouette"]
    sil_km = round(silhouette_score(
        StandardScaler().fit_transform(df[FEATURE_COLS].values),
        best_km_labels.astype(int)
    ), 3)

    metrics_table = go.Table(
        header=dict(
            values=["<b>Metric</b>", "<b>KMeans</b>", "<b>HDBSCAN</b>"],
            fill_color="paleturquoise", align="left", font=dict(size=11),
        ),
        cells=dict(
            values=[
                ["Clusters", "Silhouette", "Noise %"],
                [f"k={best_k}", f"{sil_km:.3f}", "0%"],
                [f"n={n_clusters_hdb}", f"{sil_hdb:.3f}", f"{noise_hdb}%"],
            ],
            align="left", font=dict(size=10), height=24,
        ),
    )
    fig.add_trace(metrics_table, row=1, col=3)

    # ── Feature Contributions Table ──
    feature_table = go.Table(
        header=dict(
            values=["<b>Feature</b>", "<b>PC1</b>", "<b>PC2</b>"],
            fill_color="lightcyan", align="left", font=dict(size=10),
        ),
        cells=dict(
            values=[
                pca_components["feature"],
                [f"{v:.3f}" for v in pca_components["PC1"]],
                [f"{v:.3f}" for v in pca_components["PC2"]],
            ],
            align="left", font=dict(size=9), height=20,
        ),
    )
    fig.add_trace(feature_table, row=2, col=3)

    # ── Layout ──
    fig.update_layout(
        title=dict(
            text="<b>Jay Chou — Song Clustering Analysis</b><br>"
                 "<sup>Spotify Audio Features · KMeans vs HDBSCAN · PCA vs UMAP</sup>",
            font=dict(size=18),
        ),
        height=900,
        hovermode="closest",
        template="plotly_white",
        legend=dict(font=dict(size=9), itemsizing="constant"),
        margin=dict(l=50, r=50, t=100, b=50),
    )

    # Axis labels
    fig.update_xaxes(title_text="PC1", row=1, col=1)
    fig.update_yaxes(title_text="PC2", row=1, col=1)
    fig.update_xaxes(title_text="PC1", row=1, col=2)
    fig.update_yaxes(title_text="PC2", row=1, col=2)
    fig.update_xaxes(title_text="UMAP1", row=2, col=1)
    fig.update_yaxes(title_text="UMAP2", row=2, col=1)
    fig.update_xaxes(title_text="UMAP1", row=2, col=2)
    fig.update_yaxes(title_text="UMAP2", row=2, col=2)

    return fig


# ── 8. 主程序 ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Jay Chou Music — Song Clustering Analysis")
    print("=" * 60)
    print()

    # 1. Load
    df = load_data()
    print(f"  Songs: {len(df)}, Features: {len(FEATURE_COLS)}")
    print()

    # 2. Standardize
    X_scaled, scaler = standardize(df)
    print(f"  Standardized: {X_scaled.shape}")
    print()

    # 3. PCA
    X_pca, pca_model, pca_components = compute_pca(X_scaled)
    print()

    # 4. UMAP
    X_umap, umap_model = compute_umap(X_scaled)
    print()

    # 5. KMeans
    best_k, km_models, sil_scores = find_optimal_k(X_scaled)
    best_km_labels = km_models[best_k][1]
    print()

    # 6. HDBSCAN
    hdbscan_results, hdbscan_models, best_hdb_entry = find_optimal_hdbscan(X_scaled)
    best_hdb_labels = hdbscan_models[
        (int(best_hdb_entry["min_cluster_size"]), best_hdb_entry["min_samples"])
    ][1]
    print()

    # 7. Annotate cluster labels
    df["km_label"] = best_km_labels.astype(str)
    df["hdb_label"] = best_hdb_labels.astype(str)

    # 8. Print cluster summary
    print("-" * 60)
    print("  Cluster Summary")
    print("-" * 60)
    for method, label_col in [("KMeans", "km_label"), ("HDBSCAN", "hdb_label")]:
        print(f"\n  {method}:")
        for label in sorted(df[label_col].unique()):
            subset = df[df[label_col] == label]
            albums = subset.groupby("album_en").size().sort_values(ascending=False)
            top_album = albums.index[0]
            top_count = albums.iloc[0]
            top_songs = ", ".join(subset["song_name"].head(5).tolist())
            label_str = f"Cluster {label}" if label != "-1" else "Noise"
            print(f"    {label_str}: {len(subset)} songs | Top album: {top_album} ({top_count})")
            print(f"      Songs: {top_songs}")

    # 9. Metrics comparison
    print()
    print("-" * 60)
    print("  Metrics Comparison")
    print("-" * 60)
    noise_mask = best_hdb_labels != -1
    if len(set(best_hdb_labels[noise_mask])) >= 2:
        sil_hdb_val = silhouette_score(X_scaled[noise_mask], best_hdb_labels[noise_mask])
    else:
        sil_hdb_val = 0
    sil_km_val = silhouette_score(X_scaled, best_km_labels)
    print(f"  KMeans:    k={best_k}, Silhouette={sil_km_val:.3f}, Noise=0%")
    print(f"  HDBSCAN:   clusters={int(best_hdb_entry['n_clusters'])}, "
          f"Silhouette={best_hdb_entry['silhouette']:.3f}, "
          f"Noise={best_hdb_entry['noise_pct']}%")

    # 10. Build interactive chart
    print()
    print("Building interactive visualization...")
    fig = build_interactive_chart(
        df, X_pca, X_umap, best_k, best_km_labels,
        best_hdb_labels, best_hdb_entry, pca_components,
    )

    # 11. Save
    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    fig.write_html(OUTPUT_HTML, include_plotlyjs="cdn", full_html=True)
    print(f"\nSaved to: {OUTPUT_HTML}")
    print(f"File size: {os.path.getsize(OUTPUT_HTML) / 1024:.0f} KB")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
