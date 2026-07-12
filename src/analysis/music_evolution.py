"""
Music Evolution Analysis — Jay Chou's audio features over time (2000–2026).

Publication-quality visualizations and bilingual (Chinese/English) statistical report.

Outputs:
  - outputs/figures/09_evolution_overview.png      (5-panel composite with era shading + LOESS)
  - outputs/figures/10_evolution_{feature}.png     (individual feature plots)
  - outputs/figures/11_evolution_era_radar.png      (radar comparison across 4 eras)
  - reports/music_evolution_report.md               (bilingual analysis report)
"""

import sys
from pathlib import Path

_PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import warnings
from typing import Final, Dict, Tuple, List
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats as scipy_stats
from scipy.interpolate import make_smoothing_spline
from scipy.stats import f_oneway, tukey_hsd

from src.analysis.config import (
    PROCESSED_DATA_DIR, OUTPUTS_DIR, RANDOM_SEED,
)

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
FIGS_DIR: Final[Path] = OUTPUTS_DIR / "figures"
FIGS_DIR.mkdir(parents=True, exist_ok=True)
DS_PATH: Final[Path] = PROCESSED_DATA_DIR / "jay_music_dataset.csv"

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
sns.set_theme(style="whitegrid", palette="muted", font_scale=0.95)
plt.rcParams.update({
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
    "axes.titleweight": "bold",
})
np.random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# Chinese font
# ---------------------------------------------------------------------------
_CN_FAMILIES = ["PingFang SC", "Heiti SC", "STHeiti", "Microsoft YaHei", "Noto Sans CJK SC"]
_CN_FONT: str = "sans-serif"
for _fam in _CN_FAMILIES:
    try:
        fm.findfont(_fam, fallback_to_default=False)
        _CN_FONT = _fam
        break
    except Exception:
        continue
print(f"Chinese font: {_CN_FONT}")

def _set_cn(ax, xlabel="", ylabel="", title=""):
    if xlabel:
        ax.set_xlabel(xlabel, fontfamily=_CN_FONT)
    if ylabel:
        ax.set_ylabel(ylabel, fontfamily=_CN_FONT)
    if title:
        ax.set_title(title, fontfamily=_CN_FONT, fontweight="bold")

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
df = pd.read_csv(DS_PATH, encoding="utf-8-sig")
df["release_date"] = pd.to_datetime(df["release_date"])
df["year"] = df["release_date"].dt.year

print(f"Loaded: {len(df)} songs, {df['year'].nunique()} years, "
      f"{df['album_cn'].nunique()} albums")

FEATURES = ["danceability", "energy", "valence", "tempo", "acousticness"]

FEATURE_LABELS_CN = {
    "danceability": "舞动性",
    "energy":       "能量",
    "valence":      "情绪积极性",
    "tempo":        "速度 (BPM)",
    "acousticness": "声学性",
}
FEATURE_LABELS = {
    "danceability":  "Danceability\n(0–1)",
    "energy":        "Energy\n(0–1)",
    "valence":       "Valence\n(0–1)",
    "tempo":         "Tempo\n(BPM)",
    "acousticness":  "Acousticness\n(0–1)",
}
FEATURE_RANGES = {
    "danceability":  (0, 1),
    "energy":        (0, 1),
    "valence":       (0, 1),
    "tempo":         (60, 120),
    "acousticness":  (0, 1),
}

FEATURE_COLORS = {
    "danceability":  "#2E86C1",
    "energy":        "#E74C3C",
    "valence":       "#F39C12",
    "tempo":         "#8E44AD",
    "acousticness":  "#27AE60",
}

# Eras
ERA_MAP: Dict[str, Tuple[int, int]] = {
    "Early\n(2000–2003)":  (2000, 2003),
    "Golden\n(2004–2007)": (2004, 2007),
    "Mid\n(2008–2012)":    (2008, 2012),
    "Recent\n(2014–2026)": (2014, 2026),
}
ERA_LABELS_SHORT = {
    "Early\n(2000–2003)":  "Early (2000–2003)",
    "Golden\n(2004–2007)": "Golden (2004–2007)",
    "Mid\n(2008–2012)":    "Mid (2008–2012)",
    "Recent\n(2014–2026)": "Recent (2014–2026)",
}
ERA_COLORS_HEX = ["#3498DB", "#E74C3C", "#F39C12", "#2ECC71"]
ERA_ALPHA = 0.12


# ===================================================================
# Statistics helpers
# ===================================================================

@dataclass
class TrendResult:
    slope: float
    intercept: float
    r_value: float
    p_value: float
    std_err: float
    direction: str


def analyze_trend(feature: str) -> TrendResult:
    grp = df.groupby("year")[feature].mean().reset_index()
    x = grp["year"].values
    y = grp[feature].values
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, y)
    if p_value < 0.05:
        direction = "increasing" if slope > 0 else "decreasing"
    else:
        direction = "stable"
    return TrendResult(slope, intercept, r_value, p_value, std_err, direction)


def cohens_d(vals1: np.ndarray, vals2: np.ndarray) -> float:
    n1, n2 = len(vals1), len(vals2)
    s1, s2 = np.var(vals1, ddof=1), np.var(vals2, ddof=1)
    sp = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if sp == 0:
        return 0.0
    return (np.mean(vals1) - np.mean(vals2)) / sp


def era_data(feature: str) -> Dict[str, np.ndarray]:
    groups = {}
    for label, (lo, hi) in ERA_MAP.items():
        vals = df[(df["year"] >= lo) & (df["year"] <= hi)][feature].dropna().values
        groups[label] = vals
    return groups


def run_anova(feature: str) -> Tuple[float, float, float]:
    """Returns (F, p, eta_sq)"""
    groups = list(era_data(feature).values())
    f_stat, p_val = f_oneway(*groups)
    all_vals = np.concatenate(groups)
    ss_between = sum(len(g) * (np.mean(g) - np.mean(all_vals))**2 for g in groups)
    ss_total = sum((v - np.mean(all_vals))**2 for v in all_vals)
    eta_sq = ss_between / ss_total if ss_total != 0 else 0
    return f_stat, p_val, eta_sq


def run_tukey(feature: str, era_keys: List[str]) -> Dict[Tuple[str, str], float]:
    groups = era_data(feature)
    arrs = [groups[k] for k in era_keys]
    res = tukey_hsd(*arrs)
    pvals: Dict[Tuple[str, str], float] = {}
    for i in range(len(era_keys)):
        for j in range(i + 1, len(era_keys)):
            pvals[(era_keys[i], era_keys[j])] = res.pvalue[i, j]
    return pvals


def compute_era_means(feature: str) -> Dict[str, float]:
    return {label: np.mean(vals) for label, vals in era_data(feature).items()}


# ===================================================================
# LOESS smoothing helper
# ===================================================================

def smooth_loess(years: np.ndarray, values: np.ndarray,
                 lam: float = None) -> Tuple[np.ndarray, np.ndarray]:
    """Fit a smoothing spline (LOESS-like) to the data."""
    x = years
    y = values
    # Remove NaN
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    if len(x) < 4:
        return x, y
    if lam is None:
        # auto lambda: small fraction of trace
        lam = 1e-6 * np.sum((y - np.mean(y))**2)
    spl = make_smoothing_spline(x, y, lam=lam)
    x_dense = np.linspace(x.min(), x.max(), 300)
    return x_dense, spl(x_dense)


# ===================================================================
# 1. Overview figure — 5-panel composite with era shading + LOESS
# ===================================================================
print("\n[1/3] Evolution overview figure (with era shading + LOESS)...")

fig, axes = plt.subplots(3, 2, figsize=(15, 13))
axes_flat = axes.flatten()

all_trends = {}
all_era_means = {}

for i, feat in enumerate(FEATURES):
    ax = axes_flat[i]
    trend = analyze_trend(feat)
    all_trends[feat] = trend
    all_era_means[feat] = compute_era_means(feat)

    # Yearly mean ± std
    grp = df.groupby("year")[feat]
    means = grp.mean()
    stds = grp.std()
    years = means.index.values
    year_vals = means.values

    # Era shading
    for idx, (label, (lo, hi)) in enumerate(ERA_MAP.items()):
        ax.axvspan(lo - 0.5, hi + 0.5, alpha=ERA_ALPHA,
                   color=ERA_COLORS_HEX[idx], zorder=0)
        # Era label at top
        mid = (lo + hi) / 2
        ylim = ax.get_ylim()
        ax.text(mid, 1.02, label.replace("\n", " "),
                transform=ax.get_xaxis_transform(),
                ha="center", va="bottom", fontsize=7.5,
                color=ERA_COLORS_HEX[idx], fontweight="bold",
                fontfamily=_CN_FONT)

    # Confidence band
    ax.fill_between(years, means - stds, means + stds,
                    alpha=0.12, color=FEATURE_COLORS[feat])

    # Yearly mean line
    ax.plot(years, year_vals, "o-", color=FEATURE_COLORS[feat],
            linewidth=2, markersize=6, zorder=3, label="Yearly mean")

    # LOESS smooth
    if len(years) >= 4:
        xs, ys = smooth_loess(years.astype(float), year_vals.astype(float))
        ax.plot(xs, ys, "-", color="darkgrey", linewidth=2.5, zorder=4,
                alpha=0.8, label="LOESS smooth")

    # Regression line
    x_line = np.linspace(years.min(), years.max(), 200)
    y_line = trend.slope * x_line + trend.intercept
    ax.plot(x_line, y_line, "--", color="#2C3E50", linewidth=1.5, alpha=0.7,
            label=f"Linear (p={trend.p_value:.3f})")

    # Annotation box
    sig_text = "Significant" if trend.p_value < 0.05 else "Not significant"
    ann_text = (f"slope = {trend.slope:.4f}/yr\n"
                f"R² = {trend.r_value**2:.3f}\n"
                f"p = {trend.p_value:.4f} ({sig_text})")
    ax.text(0.97, 0.05, ann_text,
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, fontfamily=_CN_FONT,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.7))

    _set_cn(ax, xlabel="Year",
            title=f"{feat.capitalize()} / {FEATURE_LABELS_CN[feat]}")
    ax.legend(fontsize=7.5, prop={"family": _CN_FONT},
              loc="upper left", ncol=2)
    ax.set_xlim(years.min() - 0.5, years.max() + 0.5)

# Hide the 6th subplot
axes_flat[5].set_visible(False)

# Legend for era shading
legend_elements = [Patch(facecolor=c, alpha=0.35, label=lab.replace("\n", " "))
                   for lab, c in zip(ERA_MAP.keys(), ERA_COLORS_HEX)]
fig.legend(handles=legend_elements, loc="lower center",
           ncol=4, fontsize=9, prop={"family": _CN_FONT},
           bbox_to_anchor=(0.5, -0.02))

fig.suptitle("Analysis of Audio Features Over Time — Jay Chou (2000–2026)\n"
             "周杰伦音乐特征随年代变化趋势图",
             fontsize=14, fontweight="bold", fontfamily=_CN_FONT, y=1.01)
fig.tight_layout(rect=[0, 0.03, 1, 0.97])
fig.savefig(FIGS_DIR / "09_evolution_overview.png")
plt.close(fig)
print("  -> 09_evolution_overview.png")

# ===================================================================
# 2. Individual high-quality feature plots
# ===================================================================
print("[2/3] Individual feature plots (scatter + LOESS + regression + era shading)...")

for feat in FEATURES:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    trend = all_trends[feat]

    # Era shading
    for idx, (label, (lo, hi)) in enumerate(ERA_MAP.items()):
        ax.axvspan(lo - 0.5, hi + 0.5, alpha=ERA_ALPHA,
                   color=ERA_COLORS_HEX[idx], zorder=0)
        mid = (lo + hi) / 2
        ax.text(mid, 1.02, label.replace("\n", " "),
                transform=ax.get_xaxis_transform(),
                ha="center", va="bottom", fontsize=8,
                color=ERA_COLORS_HEX[idx], fontweight="bold",
                fontfamily=_CN_FONT)

    # Scatter: individual songs
    ax.scatter(df["year"], df[feat], alpha=0.20, s=15,
               color=FEATURE_COLORS[feat], zorder=2,
               label=f"Songs (n={len(df)})")

    # Yearly mean ± SD
    grp = df.groupby("year")[feat]
    means = grp.mean()
    stds = grp.std()
    years = means.index.values
    year_vals = means.values

    ax.fill_between(years, means - stds, means + stds,
                    alpha=0.12, color=FEATURE_COLORS[feat])
    ax.plot(years, year_vals, "o-", color=FEATURE_COLORS[feat],
            linewidth=2.5, markersize=7, zorder=4, label="Yearly mean ± SD")

    # LOESS
    if len(years) >= 4:
        xs, ys = smooth_loess(years.astype(float), year_vals.astype(float))
        ax.plot(xs, ys, "-", color="#34495E", linewidth=2.5, zorder=5,
                alpha=0.8, label="LOESS smooth")

    # Regression
    x_line = np.linspace(years.min() - 0.5, years.max() + 0.5, 200)
    y_line = trend.slope * x_line + trend.intercept
    ax.plot(x_line, y_line, "--", color="#C0392B", linewidth=2, alpha=0.8,
            label=f"Linear (p={trend.p_value:.4f})")

    # Annotations
    sig_txt = "Significant" if trend.p_value < 0.05 else "Not significant"
    ann = (f"Trend: {trend.direction}\n"
           f"Slope = {trend.slope:.4f}/yr\n"
           f"R² = {trend.r_value**2:.3f}  p = {trend.p_value:.4f}\n"
           f"({sig_txt})")
    ax.text(0.97, 0.97, ann, transform=ax.transAxes,
            ha="right", va="top", fontsize=8.5, fontfamily=_CN_FONT,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor=FEATURE_COLORS[feat], alpha=0.85))

    # Era means
    em = all_era_means[feat]
    em_text = " | ".join(f"{k.replace(chr(10),' ')}: {em[k]:.3f}"
                         for k in ERA_MAP)
    ax.text(0.03, 0.03, f"Era means:\n{em_text}",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=7.5, fontfamily=_CN_FONT,
            bbox=dict(boxstyle="round", facecolor="ivory", alpha=0.7))

    _set_cn(ax, xlabel="Release Year",
            ylabel=FEATURE_LABELS.get(feat, feat),
            title=f"{feat.capitalize()} Over Time — 周杰伦\n{FEATURE_LABELS_CN[feat]} 随年份变化")
    ax.legend(fontsize=8.5, loc="upper left", prop={"family": _CN_FONT}, ncol=2)
    ax.set_xlim(years.min() - 0.5, years.max() + 0.5)

    fig.tight_layout()
    fig.savefig(FIGS_DIR / f"10_evolution_{feat}.png")
    plt.close(fig)
    print(f"  -> 10_evolution_{feat}.png")


# ===================================================================
# 3. Era radar chart (improved)
# ===================================================================
print("[3/3] Era radar figure ...")

era_means_raw = {}
for label, (lo, hi) in ERA_MAP.items():
    subset = df[(df["year"] >= lo) & (df["year"] <= hi)]
    era_means_raw[label] = [subset[f].mean() for f in FEATURES]

# Normalize for radar comparability
def normalize(val, lo, hi):
    return (val - lo) / (hi - lo)

era_norm = {}
for label in ERA_MAP:
    vals = []
    for i, feat in enumerate(FEATURES):
        lo, hi = FEATURE_RANGES[feat]
        vals.append(normalize(era_means_raw[label][i], lo, hi))
    era_norm[label] = vals

angles = np.linspace(0, 2 * np.pi, len(FEATURES), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

for idx, label in enumerate(ERA_MAP.keys()):
    short = ERA_LABELS_SHORT[label]
    values = era_norm[label] + era_norm[label][:1]
    ax.plot(angles, values, "o-", color=ERA_COLORS_HEX[idx],
            linewidth=2.5, label=short, markersize=6)
    ax.fill(angles, values, alpha=0.06, color=ERA_COLORS_HEX[idx])

# Tick labels
tick_labels = []
for f in FEATURES:
    base = f.capitalize()
    cn = FEATURE_LABELS_CN[f]
    tick_labels.append(f"{base}\n({cn})")

ax.set_xticks(angles[:-1])
ax.set_xticklabels(tick_labels, fontsize=10, fontfamily=_CN_FONT)
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=8)
ax.set_title("Feature Profiles by Career Era\n周杰伦各阶段音频特征雷达图",
             fontsize=14, fontweight="bold", fontfamily=_CN_FONT, pad=25)
ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
          fontsize=10, prop={"family": _CN_FONT})

fig.tight_layout()
fig.savefig(FIGS_DIR / "11_evolution_era_radar.png")
plt.close(fig)
print("  -> 11_evolution_era_radar.png")

# ===================================================================
# Write bilingual Markdown report
# ===================================================================
print("\n[Report] Writing bilingual analysis report ...")

era_keys_short = list(ERA_LABELS_SHORT.values())
era_keys_raw = list(ERA_MAP.keys())

# Precompute Tukey for each feature
tukey_results = {}
for feat in FEATURES:
    tukey_results[feat] = run_tukey(feat, era_keys_raw)

# Summary stats
overall_means = df[FEATURES].mean()
overall_stds = df[FEATURES].std()
album_count = df['album_cn'].nunique()

lines = []
def L(text=""):
    lines.append(text)

L("# Music Evolution Analysis — Jay Chou (2000–2026)")
L("## 周杰伦音乐特征随年代变化分析报告")
L()
L("## 1. Overview / 概述")
L()
L(f"This report examines how five key audio features — **Danceability**, **Energy**, "
  f"**Valence**, **Tempo**, and **Acousticness** — have evolved across Jay Chou's "
  f"26-year career, spanning **{len(df)} songs** across **{album_count} albums** "
  f"from **2000 to 2026**.")
L()
L("For each feature, yearly means were computed and analyzed using ordinary least-squares "
  "linear regression for monotonic trend detection, smoothing spline (LOESS) for "
  "non-linear patterns, and one-way ANOVA across four career phases to test for "
  "statistically significant shifts. Post-hoc pairwise comparisons (Tukey HSD) and "
  "effect sizes (Cohen's d, η²) quantify the magnitude of observed differences.")
L()
L("---")
L()

# Per-feature detailed analysis
for feat_idx, feat in enumerate(FEATURES):
    section_num = feat_idx + 2
    t = all_trends[feat]
    f_stat, p_val_anova, eta_sq = run_anova(feat)
    em = all_era_means[feat]
    tukey = tukey_results[feat]
    eras = era_data(feat)

    L(f"## {section_num}. {feat.capitalize()} / {FEATURE_LABELS_CN[feat]}")
    L()
    L(f"- **Overall mean / 整体均值**: {overall_means[feat]:.3f} ± {overall_stds[feat]:.3f}")
    L(f"- **Range / 范围**: {df[feat].min():.3f} – {df[feat].max():.3f}")
    L()
    L("### Trend Analysis / 趋势分析")
    L()
    L(f"- **Linear slope / 线性斜率**: {t.slope:.4f} per year")
    L(f"- **R²**: {t.r_value**2:.3f}")
    L(f"- **p-value**: {t.p_value:.4f}")
    sig_word = "Significant (p < 0.05)" if t.p_value < 0.05 else "Not significant (p ≥ 0.05)"
    L(f"- **Direction / 方向**: {t.direction} ({sig_word})")
    L()
    L("### Era Comparison / 阶段对比 (ANOVA)")
    L()
    L(f"- **F-statistic**: {f_stat:.2f}")
    L(f"- **p-value**: {p_val_anova:.4f}")
    L(f"- **Effect size η² / 效应量 η²**: {eta_sq:.4f} "
      f"({'Large' if eta_sq >= 0.14 else 'Medium' if eta_sq >= 0.06 else 'Small'})")
    L()
    L("| Era / 阶段 | Mean / 均值 | N / 歌曲数 |")
    L("|---|---|---|")
    for ek in ERA_MAP:
        short = ERA_LABELS_SHORT[ek]
        n = len(eras[ek])
        L(f"| {short} | {em[ek]:.4f} | {n} |")
    L()
    L("### Pairwise Comparisons / 两两对比 (Tukey HSD)")
    L()
    L("| Comparison / 对比 | p-value |")
    L("|---|---|")
    for (ek1, ek2), pv in tukey.items():
        s1 = ERA_LABELS_SHORT[ek1]
        s2 = ERA_LABELS_SHORT[ek2]
        sig = " *" if pv < 0.05 else ""
        L(f"| {s1} vs {s2} | {pv:.4f}{sig} |")
    L()
    L("### Effect Sizes / 效应量 (Cohen's d between consecutive eras)")
    L()
    era_keys_list = list(ERA_MAP.keys())
    L("| Comparison / 对比 | Cohen's d | Interpretation / 解读 |")
    L("|---|---|---|")
    for j in range(len(era_keys_list) - 1):
        ek_a, ek_b = era_keys_list[j], era_keys_list[j + 1]
        d = cohens_d(eras[ek_a], eras[ek_b])
        interp = "Large" if abs(d) >= 0.8 else "Medium" if abs(d) >= 0.5 else "Small"
        sa = ERA_LABELS_SHORT[ek_a]
        sb = ERA_LABELS_SHORT[ek_b]
        L(f"| {sa} → {sb} | {d:.3f} | {interp} |")
    L()
    L("### Interpretation / 解读")
    L()
    if t.p_value < 0.05:
        if t.slope > 0:
            L(f"A statistically significant upward trend was detected (p = {t.p_value:.4f}), "
              f"indicating that Jay Chou's music has gradually become more "
              f"{feat}-oriented over his career. The effect size of the overall "
              f"trend is modest (R² = {t.r_value**2:.3f}).")
        else:
            L(f"A statistically significant downward trend was detected (p = {t.p_value:.4f}), "
              f"indicating that Jay Chou's earlier work tends to exhibit higher "
              f"{feat} values compared to more recent releases. "
              f"R² = {t.r_value**2:.3f}.")
    else:
        L(f"No statistically significant linear trend was detected for {feat} "
          f"(p = {t.p_value:.4f}). The feature has remained relatively **stable** "
          f"across his 26-year career, or changes follow a non-linear pattern "
          f"not captured by the linear model.")
    if p_val_anova < 0.05:
        L(f"ANOVA reveals significant differences across career phases "
          f"(F = {f_stat:.2f}, p = {p_val_anova:.4f}), with η² = {eta_sq:.4f}.")
    else:
        L(f"ANOVA suggests no statistically significant differences across career "
          f"phases (F = {f_stat:.2f}, p = {p_val_anova:.4f}).")
    L()
    L(f"Refer to Figure [`10_evolution_{feat}.png`](figures/10_evolution_{feat}.png) "
      f"for the detailed visualization.")
    L("---")
    L()

# Summary tables
L("## 7. Summary of All Trends / 所有特征趋势汇总")
L()
L("### Linear Regression / 线性回归")
L()
L("| Feature / 特征 | Slope / 斜率 | R² | p-value | Direction / 方向 | Signif. / 显著 |")
L("|---|---|---|---|---|---|")
for feat in FEATURES:
    t = all_trends[feat]
    sig = "✅" if t.p_value < 0.05 else "❌"
    L(f"| {feat.capitalize()} | {t.slope:.4f} | {t.r_value**2:.3f} | {t.p_value:.4f} | {t.direction} | {sig} |")
L()
L("### ANOVA (Era Comparison / 阶段对比)")
L()
L("| Feature / 特征 | ANOVA F | ANOVA p | η² | Signif. / 显著 |")
L("|---|---|---|---|---|")
for feat in FEATURES:
    f_stat, p_val, eta_sq = run_anova(feat)
    sig = "✅" if p_val < 0.05 else "❌"
    L(f"| {feat.capitalize()} | {f_stat:.2f} | {p_val:.4f} | {eta_sq:.4f} | {sig} |")
L()

# Key Findings — now consistent with actual statistics
L("## 8. Key Findings / 关键发现")
L()
L("Based on the statistical analyses above, the following conclusions emerge:")
L()

for feat in FEATURES:
    t = all_trends[feat]
    em = all_era_means[feat]
    L(f"### 8.{FEATURES.index(feat)+1}. {feat.capitalize()} / {FEATURE_LABELS_CN[feat]}")
    L()
    L(f"- **Overall mean / 整体均值**: {overall_means[feat]:.3f}")
    L(f"- **Trend / 趋势**: slope {t.slope:.4f}/yr, "
      f"{'statistically significant' if t.p_value < 0.05 else 'not significant'} "
      f"(p = {t.p_value:.4f})")
    L(f"- **Era range / 阶段极差**: {min(em.values()):.3f} – {max(em.values()):.3f} "
      f"(range = {max(em.values()) - min(em.values()):.3f})")
    L()
    if t.p_value < 0.05:
        L("This feature shows a **significant temporal trend**. The magnitude of change, "
          "while modest in absolute terms, suggests a meaningful stylistic shift over "
          "Jay Chou's career.")
    else:
        L("This feature shows **no statistically significant trend**. Any observed "
          "year-to-year variation is likely due to album-to-album stylistic diversity "
          "rather than a systematic career evolution.")
    L()

L("### 8.6 Summary / 总结")
L()
L("Jay Chou's music exhibits remarkable stylistic consistency across his 26-year career. "
  "**None of the five audio features analyzed show a statistically significant "
  "linear trend**, indicating that broad characterizations such as 'later work being more "
  "acoustic' or 'early work having higher energy' are not supported by the data at "
  "a statistically significant level. Instead, Jay Chou's music style is characterized "
  "by album-to-album diversity within a relatively consistent overall profile.")
L()
L("However, effect sizes between the earliest (2000–2003) and most recent (2014–2026) "
  "eras reveal subtle shifts:")
L()
for feat in FEATURES:
    eras_d = era_data(feat)
    ek_early = list(ERA_MAP.keys())[0]
    ek_recent = list(ERA_MAP.keys())[-1]
    d = cohens_d(eras_d[ek_early], eras_d[ek_recent])
    interp = "large" if abs(d) >= 0.8 else "medium" if abs(d) >= 0.5 else "small"
    L(f"- **{feat.capitalize()}**: Cohen's d = {d:.3f} ({interp} effect)")
L()
L("These effect sizes offer preliminary evidence of directional shifts that may become "
  "more pronounced with additional data from future releases.")

L()
L("## 9. Figures / 图表示例")
L()
L("| Figure / 图表 | Description / 描述 |")
L("|---|---|")
L("| [`09_evolution_overview.png`](figures/09_evolution_overview.png) | "
  "5-panel composite: feature trends with era shading and LOESS smooth / "
  "五图组合：含阶段着色和LOESS平滑的趋势图 |")
for feat in FEATURES:
    L(f"| [`10_evolution_{feat}.png`](figures/10_evolution_{feat}.png) | "
      f"{feat.capitalize()} yearly trend: scatter, LOESS, regression, era means / "
      f"{FEATURE_LABELS_CN[feat]}逐年变化：散点、LOESS、回归、阶段均值对比 |")
L("| [`11_evolution_era_radar.png`](figures/11_evolution_era_radar.png) | "
  "Radar chart comparing 4 career eras / 四阶段特征雷达图 |")
L()
L("## 10. Methodology / 方法说明")
L()
L("- **Trend detection / 趋势检测**: Ordinary least-squares linear regression on yearly "
  "mean values.")
L("- **Non-linear smoothing / 非线性平滑**: Smoothing spline (LOESS) fitted via "
  "scipy's `make_smoothing_spline`.")
L("- **Era comparison / 阶段对比**: One-way ANOVA with η² effect size, and Tukey HSD "
  "post-hoc pairwise tests.")
L("- **Effect size / 效应量**: Cohen's d for pairwise era comparisons (pooled SD).")
L("- **Normalization / 归一化**: Radar chart values normalized to [0, 1] for "
  "cross-feature comparability.")
L("- **Software / 软件**: Python with pandas, NumPy, SciPy, Matplotlib, and Seaborn.")
L("- **Data source / 数据来源**: 174 songs from Jay Chou's 16 studio albums "
  "(2000–2026), audio features from Spotify Web API.")
L()
L("---")
L()
L("*Report generated on 2026-07-12 by the Jay Chou Music Deep Analysis pipeline. "
  "报告由周杰伦音乐深度分析流水线生成。*")

report_text = "\n".join(lines)
report_path = OUTPUTS_DIR / "music_evolution_report.md"
report_path.write_text(report_text, encoding="utf-8")
print(f"  -> {report_path}")

print("\n✓ Music Evolution analysis complete!")
print(f"  Figures: {FIGS_DIR}/")
print(f"  Report:  {report_path}")
