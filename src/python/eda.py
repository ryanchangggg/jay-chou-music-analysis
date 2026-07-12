"""
Exploratory Data Analysis for Jay Chou Music Deep Analysis project.

Generates all figures for the EDA section, including:
  1. Missing values analysis
  2. Outlier analysis (boxplots)
  3. Release year distribution
  4. Album statistics (song count + avg popularity)
  5. Song count per album
  6. Audio features distribution (histograms)
  7. Popularity distribution
  8. Correlation heatmap

Usage:
    cd <project_root>
    MPLCONFIGDIR=/tmp/matplotlib python3 -m src.python.eda

All figures are saved to reports/figures/.
"""

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import warnings
from typing import Final

import matplotlib
matplotlib.use("Agg")  # no display backend needed
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

from src.python.config import (
    AUDIO_FEATURES,
    NUMERIC_FEATURES,
    PROCESSED_DATA_DIR,
    REPORTS_DIR,
    RANDOM_SEED,
)

# ---------------------------------------------------------------------------
# 设置
# ---------------------------------------------------------------------------

warnings.filterwarnings("ignore", category=FutureWarning)

FIGS_DIR: Final[Path] = REPORTS_DIR / "figures"
FIGS_DIR.mkdir(parents=True, exist_ok=True)

DS_PATH: Final[Path] = PROCESSED_DATA_DIR / "jay_music_dataset.csv"

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.0)
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
})

np.random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# 加载数据
# ---------------------------------------------------------------------------

df: pd.DataFrame = pd.read_csv(DS_PATH, encoding="utf-8-sig")
df["release_date"] = pd.to_datetime(df["release_date"])
df["year"] = df["release_date"].dt.year

print(f"Dataset loaded: {df.shape[0]} songs, {df.shape[1]} columns")
print(f"Albums: {df['album_en'].nunique()},  Years: {df['year'].min()}--{df['year'].max()}")
print(f"Figures output: {FIGS_DIR}")

# ---------------------------------------------------------------------------
# 中文字体解析 — 尝试多个常见字体名称
# ---------------------------------------------------------------------------

_CN_FAMILIES: list[str] = ["PingFang SC", "Heiti SC", "STHeiti", "Microsoft YaHei", "Noto Sans CJK SC"]
_CN_FONT: str = "sans-serif"
for _fam in _CN_FAMILIES:
    try:
        matplotlib.font_manager.findfont(_fam, fallback_to_default=False)
        _CN_FONT = _fam
        break
    except Exception:
        continue
print(f"Chinese font: {_CN_FONT}")


def _set_cn_label(ax: plt.Axes, xlabel: str = "", ylabel: str = "", title: str = "") -> None:
    """Set axis labels with Chinese font fallback."""
    if xlabel:
        ax.set_xlabel(xlabel, fontfamily=_CN_FONT)
    if ylabel:
        ax.set_ylabel(ylabel, fontfamily=_CN_FONT)
    if title:
        ax.set_title(title, fontfamily=_CN_FONT, fontweight="bold")


# ===================================================================
# 1. 缺失值
# ===================================================================

print("\n[1/8] Missing values analysis ...")

fig, ax = plt.subplots(figsize=(8, 6))
missing = df.isnull().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    # No missing -- show a clean empty-state plot
    ax.text(0.5, 0.5, "No missing values detected\nacross all 26 columns",
            ha="center", va="center", fontsize=13, fontfamily=_CN_FONT,
            transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
else:
    colors = sns.color_palette("Reds_r", len(missing))
    bars = ax.barh(missing.index, missing.values, color=colors, edgecolor="gray", linewidth=0.5)
    for bar, count in zip(bars, missing.values):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{count}", va="center", fontsize=10, fontfamily=_CN_FONT)
    _set_cn_label(ax, xlabel="Missing Count", ylabel="Column",
                  title="Missing Values by Column")

fig.tight_layout()
fig.savefig(FIGS_DIR / "01_missing_values.png")
plt.close(fig)
print("  -> 01_missing_values.png")

# ===================================================================
# 2. 异常值分析 — 音频特征的箱线图
# ===================================================================

print("[2/8] Outlier analysis (boxplots) ...")

_FEATURE_LABELS: dict[str, str] = {
    "danceability":  "Danceability\n(0-1)",
    "energy":        "Energy\n(0-1)",
    "valence":       "Valence\n(0-1)",
    "tempo":         "Tempo\n(BPM)",
    "acousticness":  "Acousticness\n(0-1)",
    "instrumentalness": "Instrumentalness\n(0-1)",
    "speechiness":   "Speechiness\n(0-1)",
    "loudness":      "Loudness\n(dB)",
}

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes_flat = axes.flatten()

for i, feat in enumerate(AUDIO_FEATURES):
    ax = axes_flat[i]
    bp = ax.boxplot(df[feat].dropna(), patch_artist=True,
                    boxprops=dict(facecolor="#AED6F1", alpha=0.7),
                    medianprops=dict(color="#E74C3C", linewidth=2),
                    flierprops=dict(marker="o", markerfacecolor="#E74C3C",
                                    markersize=5, alpha=0.6))
    _set_cn_label(ax, title=_FEATURE_LABELS.get(feat, feat))
    ax.set_xticks([])

# 隐藏未使用的子图
for j in range(len(AUDIO_FEATURES), 8):
    axes_flat[j].set_visible(False)

fig.suptitle("Audio Feature Outlier Analysis (Boxplots)", fontsize=14,
             fontweight="bold", fontfamily=_CN_FONT, y=1.02)
fig.tight_layout()
fig.savefig(FIGS_DIR / "02_boxplots_features.png")
plt.close(fig)
print("  -> 02_boxplots_features.png")

# ===================================================================
# 3. 发行年份分布
# ===================================================================

print("[3/8] Release year distribution ...")

year_counts = df["year"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(14, 5))
colors = sns.color_palette("viridis", len(year_counts))
bars = ax.bar(year_counts.index.astype(str), year_counts.values,
              color=colors, edgecolor="gray", linewidth=0.5)
for bar, count in zip(bars, year_counts.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            str(count), ha="center", fontsize=9, fontfamily=_CN_FONT)
_set_cn_label(ax, xlabel="Year", ylabel="Song Count",
              title="Song Releases by Year (2000-2026)")
ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
fig.tight_layout()
fig.savefig(FIGS_DIR / "03_year_distribution.png")
plt.close(fig)
print("  -> 03_year_distribution.png")

# ===================================================================
# 4. 专辑统计
# ===================================================================

print("[4/8] Album statistics ...")

album_stats = (
    df.groupby(["album_en", "album_cn", "year"])
    .agg(song_count=("song_name", "count"),
         avg_popularity=("popularity", "mean"),
         avg_energy=("energy", "mean"),
         avg_valence=("valence", "mean"))
    .reset_index()
    .sort_values("year")
)

fig, ax1 = plt.subplots(figsize=(14, 6))

x = range(len(album_stats))

# 歌曲数量柱状图
bars = ax1.bar(x, album_stats["song_count"], width=0.6, color="#3498DB",
               alpha=0.75, edgecolor="gray", linewidth=0.5, label="Song Count")
ax1.set_ylabel("Song Count", fontfamily=_CN_FONT, color="#2C3E50")
ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# 平均流行度线图（次坐标轴）
ax2 = ax1.twinx()
ax2.plot(x, album_stats["avg_popularity"].round(1), color="#E74C3C",
         marker="o", linewidth=2, label="Avg Popularity")
ax2.set_ylabel("Avg Popularity", fontfamily=_CN_FONT, color="#E74C3C")
ax2.set_ylim(40, 80)

_labels = [
    f"{row['album_en']}\n({row['year']})"
    for _, row in album_stats.iterrows()
]
ax1.set_xticks(x)
ax1.set_xticklabels(_labels, rotation=45, ha="right", fontsize=8, fontfamily=_CN_FONT)
_set_cn_label(ax1, title="Album Statistics -- Song Count & Average Popularity")

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left",
           fontsize=10, prop={"family": _CN_FONT})

fig.tight_layout()
fig.savefig(FIGS_DIR / "04_album_statistics.png")
plt.close(fig)
print("  -> 04_album_statistics.png")

# ===================================================================
# 5. 歌曲数量统计
# ===================================================================

print("[5/8] Song count statistics ...")

song_counts = df.groupby("album_en")["song_name"].count().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 5))
colors = sns.color_palette("Blues_r", len(song_counts))
bars = ax.bar(range(len(song_counts)), song_counts.values,
              color=colors, edgecolor="gray", linewidth=0.5)
for bar, count in zip(bars, song_counts.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
            str(count), ha="center", fontsize=10, fontfamily=_CN_FONT, fontweight="bold")
ax.set_xticks(range(len(song_counts)))
ax.set_xticklabels(song_counts.index, rotation=30, ha="right", fontsize=9)
ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
_set_cn_label(ax, xlabel="Album", ylabel="Song Count",
              title="Song Count per Album (Descending)")
fig.tight_layout()
fig.savefig(FIGS_DIR / "05_song_count_statistics.png")
plt.close(fig)
print("  -> 05_song_count_statistics.png")

# ===================================================================
# 6. Audio Features Distribution
# ===================================================================

print("[6/8] Audio features distribution ...")

n_feats = len(AUDIO_FEATURES)
n_cols = 4
n_rows = int(np.ceil(n_feats / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3.5 * n_rows))
axes_flat = axes.flatten()

for i, feat in enumerate(AUDIO_FEATURES):
    ax = axes_flat[i]
    sns.histplot(df[feat].dropna(), bins=20, kde=True, color="#3498DB",
                 edgecolor="white", alpha=0.7, ax=ax)
    _label = _FEATURE_LABELS.get(feat, feat)
    _set_cn_label(ax, xlabel=_label, ylabel="Count",
                  title=_label.replace("\n", " "))

for j in range(n_feats, len(axes_flat)):
    axes_flat[j].set_visible(False)

fig.suptitle("Audio Features Distribution (Histogram + KDE)", fontsize=14,
             fontweight="bold", fontfamily=_CN_FONT, y=1.02)
fig.tight_layout()
fig.savefig(FIGS_DIR / "06_features_distribution.png")
plt.close(fig)
print("  -> 06_features_distribution.png")

# ===================================================================
# 7. 流行度分布
# ===================================================================

print("[7/8] Popularity distribution ...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 7a -- histogram + KDE
ax = axes[0]
sns.histplot(df["popularity"], bins=15, kde=True, color="#E67E22",
             edgecolor="white", alpha=0.7, ax=ax)
ax.axvline(df["popularity"].median(), color="#C0392B", linestyle="--",
           linewidth=1.5, label=f'Median={df["popularity"].median():.0f}')
ax.axvline(df["popularity"].mean(), color="#2C3E50", linestyle=":",
           linewidth=1.5, label=f'Mean={df["popularity"].mean():.1f}')
_set_cn_label(ax, xlabel="Spotify Popularity (0-100)",
              ylabel="Song Count", title="Popularity Distribution")
ax.legend(fontsize=10, prop={"family": _CN_FONT})

# 7b -- top-10 most popular
ax = axes[1]
top10 = df.nlargest(10, "popularity")[["song_name", "popularity", "year"]]
colors = sns.color_palette("YlOrRd", 10)[::-1]
bars = ax.barh(range(len(top10)), top10["popularity"].values,
               color=colors, edgecolor="gray", linewidth=0.5)
for bar, pop, name, yr in zip(bars, top10["popularity"], top10["song_name"], top10["year"]):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"{name} ({yr})", va="center", fontsize=9, fontfamily=_CN_FONT)
ax.set_yticks([])
ax.invert_yaxis()
_set_cn_label(ax, xlabel="Popularity", title="Top-10 Most Popular Songs")
ax.set_xlim(0, 100)

fig.tight_layout()
fig.savefig(FIGS_DIR / "07_popularity_distribution.png")
plt.close(fig)
print("  -> 07_popularity_distribution.png")

# ===================================================================
# 8. 相关热力图
# ===================================================================

print("[8/8] Correlation heatmap ...")

_corr_cols = NUMERIC_FEATURES + ["duration_ms"]
corr_df = df[_corr_cols].dropna()
corr_matrix = corr_df.corr()

# human-readable labels
_corr_labels = {
    "danceability": "Danceability",
    "energy":       "Energy",
    "valence":      "Valence",
    "tempo":        "Tempo",
    "acousticness": "Acousticness",
    "instrumentalness": "Instrumentalness",
    "speechiness":  "Speechiness",
    "loudness":     "Loudness",
    "popularity":   "Popularity",
    "duration_ms":  "Duration",
}

display_names = [_corr_labels.get(c, c) for c in corr_matrix.columns]

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, vmin=-1, vmax=1, square=True,
            linewidths=0.5, linecolor="white",
            xticklabels=display_names, yticklabels=display_names,
            cbar_kws={"shrink": 0.75, "label": "Pearson r"},
            ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=9)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
_set_cn_label(ax, title="Correlation Heatmap of Numeric Features")
fig.tight_layout()
fig.savefig(FIGS_DIR / "08_correlation_heatmap.png")
plt.close(fig)
print("  -> 08_correlation_heatmap.png")

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------

print(f"\nAll 8 figures saved to {FIGS_DIR}/")
print("EDA complete.")
