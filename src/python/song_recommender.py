#!/usr/bin/env python3
"""
Jay Chou — Song Recommendation System
======================================
Methods: Cosine Similarity / KNN / PCA Embedding
Output: Standalone interactive HTML demo
"""
import os, sys, json, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
os.environ["MPLCONFIGDIR"] = "/private/tmp/matplotlib_cache"

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATA_PATH    = os.path.join(PROJECT_ROOT, "data/raw/spotify_features.csv")
DISC_PATH    = os.path.join(PROJECT_ROOT, "data/raw/jay_discography.csv")
COVERS_PATH  = os.path.join(PROJECT_ROOT, "data/raw/album_covers.csv")
OUTPUT_HTML  = os.path.join(PROJECT_ROOT, "reports/figures/song_recommender.html")

FEATURES = ["danceability","energy","valence","tempo",
            "acousticness","instrumentalness","speechiness",
            "loudness","key","duration_ms","mode"]
RS = 42
np.random.seed(RS)

# ── 1. Load & Prepare ───────────────────────────────────────────────
def load_data():
    df = pd.read_csv(DATA_PATH)
    disc = pd.read_csv(DISC_PATH)[["song_name","album_en","album_cn","release_date"]]
    covers = pd.read_csv(COVERS_PATH)
    df = df.merge(disc, on="song_name", how="left")
    df = df.merge(covers, on="album_en", how="left")
    df["year"] = pd.to_datetime(df["release_date"]).dt.year.fillna(0).astype(int)
    df["cover_url"] = df["cover_url"].fillna("")
    print(f"Loaded {len(df)} songs, {len(FEATURES)} features")
    return df

# ── 2. Compute Similarity Matrices ──────────────────────────────────
def compute_similarities(df):
    X = StandardScaler().fit_transform(df[FEATURES].values)
    n = len(df)

    # Method 1: Cosine Similarity
    cos_sim = cosine_similarity(X)
    print(f"  Cosine: {cos_sim.shape}")

    # Method 2: KNN (Euclidean distance → similarity)
    nn = NearestNeighbors(n_neighbors=n, metric="euclidean")
    nn.fit(X)
    knn_dist, knn_idx = nn.kneighbors(X)
    # Convert distances to similarities (normalize to 0-1)
    knn_sim = 1.0 / (1.0 + knn_dist)
    # Build full similarity matrix from KNN
    knn_matrix = np.eye(n)
    for i in range(n):
        knn_matrix[i, knn_idx[i]] = knn_sim[i]
    print(f"  KNN:     {knn_matrix.shape}")

    # Method 3: PCA Embedding + Cosine
    pca = PCA(n_components=min(6, len(FEATURES)), random_state=RS)
    X_pca = pca.fit_transform(X)
    pca_var = pca.explained_variance_ratio_.sum()
    pca_cos_sim = cosine_similarity(X_pca)
    print(f"  PCA-Cos: {pca_cos_sim.shape} ({pca_var:.1%} variance)")
    print()

    return {
        "Cosine_Similarity": cos_sim,
        "KNN": knn_matrix,
        "PCA_Embedding": pca_cos_sim,
    }, pca

# ── 3. Build HTML Template ──────────────────────────────────────────
def build_html(df, sims, pca):
    songs = []
    for _, row in df.iterrows():
        songs.append({
            "name": row["song_name"],
            "album_en": row["album_en"],
            "album_cn": row.get("album_cn", ""),
            "year": int(row["year"]),
            "cover_url": row.get("cover_url", ""),
            "feats": {f: round(float(row[f]), 4) for f in FEATURES},
        })

    song_data = json.dumps(songs, ensure_ascii=False)

    # Build similarity data (only top 30 per song to keep size manageable)
    method_names = ["Cosine_Similarity", "KNN", "PCA_Embedding"]
    sim_data = {}
    for m in method_names:
        mat = sims[m]
        top_k = {}
        for i in range(len(df)):
            # Get top 30 (including self)
            sim_row = mat[i]
            top_idx = np.argsort(-sim_row)[:31]  # 30 + self
            top_k[i] = [
                {"idx": int(j), "sim": round(float(sim_row[j]), 4)}
                for j in top_idx if i != j  # exclude self
            ][:10]
        sim_data[m] = {"top_k": top_k}

    pca_loadings = {
        "feature": FEATURES,
        "PC1": [round(float(v), 3) for v in pca.components_[0]],
    }
    if pca.n_components_ >= 2:
        pca_loadings["PC2"] = [round(float(v), 3) for v in pca.components_[1]]

    sim_json = json.dumps(sim_data, ensure_ascii=False)
    pca_json = json.dumps(pca_loadings, ensure_ascii=False)
    methods_json = json.dumps(method_names, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jay Chou — Song Recommender</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js" charset="utf-8"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       background: #0f0f1a; color: #e0e0e0; min-height: 100vh; }}
.container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
.header {{ text-align: center; padding: 20px 0 10px; }}
.header h1 {{ font-size: 1.8em; color: #fff; }}
.header p {{ color: #888; font-size: 0.9em; margin-top: 4px; }}
.selector {{ background: #1a1a2e; border-radius: 12px; padding: 20px; margin: 16px 0;
            display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }}
.selector label {{ font-weight: 600; font-size: 1em; color: #aaa; }}
.selector select {{ flex: 1; min-width: 250px; padding: 10px 14px; border-radius: 8px;
                    border: 1px solid #333; background: #16213e; color: #e0e0e0;
                    font-size: 0.95em; outline: none; cursor: pointer; }}
.selector select:focus {{ border-color: #4a9eff; }}
.btn {{ padding: 10px 28px; border: none; border-radius: 8px; background: linear-gradient(135deg,#4a9eff,#6c5ce7);
        color: #fff; font-size: 0.95em; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }}
.btn:hover {{ opacity: 0.85; }}
.info-bar {{ display: flex; align-items: center; gap: 16px; background: #1a1a2e; border-radius: 12px;
             padding: 16px 20px; margin: 12px 0; flex-wrap: wrap; }}
.info-bar .selected-song {{ display: flex; align-items: center; gap: 12px; }}
.info-bar .album-cover {{ width: 48px; height: 48px; border-radius: 6px; object-fit: cover; }}
.info-bar .song-info h3 {{ font-size: 1.1em; color: #fff; }}
.info-bar .song-info span {{ font-size: 0.85em; color: #888; }}
.methods {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 12px 0; }}
@media (max-width: 900px) {{ .methods {{ grid-template-columns: 1fr; }} }}
.method-card {{ background: #1a1a2e; border-radius: 12px; overflow: hidden; }}
.method-card .card-header {{ padding: 14px 16px; font-weight: 600; font-size: 1em;
                            border-bottom: 1px solid #2a2a3e; display: flex; justify-content: space-between; align-items: center; }}
.method-card .card-header .badge {{ font-size: 0.7em; background: #2a2a4e; padding: 2px 10px;
                                    border-radius: 10px; color: #888; }}
.result-list {{ padding: 8px 0; }}
.result-item {{ display: flex; align-items: center; padding: 8px 16px; gap: 10px;
               cursor: pointer; transition: background 0.15s; }}
.result-item:hover {{ background: #2a2a40; }}
.result-item .rank {{ width: 24px; height: 24px; border-radius: 50%; background: #2a2a4e;
                     display: flex; align-items: center; justify-content: center;
                     font-size: 0.75em; font-weight: 700; color: #888; flex-shrink: 0; }}
.result-item .song-details {{ flex: 1; min-width: 0; }}
.result-item .song-details .name {{ font-size: 0.9em; color: #e0e0e0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.result-item .song-details .meta {{ font-size: 0.75em; color: #666; }}
.result-item .sim-score {{ font-size: 0.85em; color: #4a9eff; font-weight: 600; white-space: nowrap; text-align: right; }}
.result-item .sim-bar {{ width: 60px; height: 4px; background: #2a2a4e; border-radius: 2px; overflow: hidden; flex-shrink: 0; }}
.result-item .sim-bar .fill {{ height: 100%; background: linear-gradient(90deg,#4a9eff,#6c5ce7); border-radius: 2px; transition: width 0.3s; }}
#radar-container {{ background: #1a1a2e; border-radius: 12px; padding: 16px; margin: 12px 0; }}
#radar-container h3 {{ font-size: 1em; margin-bottom: 8px; color: #aaa; }}
.legend {{ display: flex; gap: 20px; flex-wrap: wrap; margin: 8px 0; }}
.legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.85em; }}
.legend-item .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
.search-wrapper {{ position: relative; flex: 1; }}
.search-wrapper select {{ width: 100%; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>🎵 Jay Chou — Song Recommender</h1>
    <p>Content-based recommendation using audio features</p>
  </div>

  <div class="selector">
    <label for="song-select">Select a song:</label>
    <div class="search-wrapper">
      <select id="song-select">
        <option value="" disabled selected>Choose a song...</option>
      </select>
    </div>
    <button class="btn" onclick="recommend()">🎯 Recommend</button>
  </div>

  <div id="info-bar" class="info-bar" style="display:none">
    <div class="selected-song">
      <img id="cover-img" class="album-cover" src="" alt="">
      <div class="song-info">
        <h3 id="selected-name"></h3>
        <span id="selected-meta"></span>
      </div>
    </div>
    <div class="legend">
      <div class="legend-item"><span class="dot" style="background:#fff"></span> Input Song</div>
      <div class="legend-item"><span class="dot" style="background:#4a9eff"></span> #1 Recommendation</div>
    </div>
  </div>

  <div class="methods" id="methods-container"></div>
  <div id="radar-container"><h3>📊 Feature Comparison</h3><div id="radar-chart"></div></div>
</div>

<script>
// ═══ DATA ══════════════════════════════════════════════════════════
const SONGS = {song_data};
const SIMILARITIES = {sim_json};
const METHODS = {methods_json};
const PCA_LOADINGS = {pca_json};
const FEATURE_NAMES = {json.dumps(FEATURES, ensure_ascii=False)};

const METHOD_LABELS = {{
    "Cosine_Similarity": "Cosine Similarity",
    "KNN": "KNN (Euclidean)",
    "PCA_Embedding": "PCA Embedding"
}};

const METHOD_COLORS = {{
    "Cosine_Similarity": "#4a9eff",
    "KNN": "#6c5ce7",
    "PCA_Embedding": "#00cec9"
}};

let currentSongIdx = -1;

// ═══ INIT ══════════════════════════════════════════════════════════
function init() {{
    const sel = document.getElementById("song-select");
    SONGS.forEach((s, i) => {{
        const opt = document.createElement("option");
        opt.value = i;
        opt.textContent = `${{s.name}} — ${{s.album_en}} (${{s.year}})`;
        sel.appendChild(opt);
    }});
}}

// ═══ RECOMMEND ═════════════════════════════════════════════════════
function recommend() {{
    const sel = document.getElementById("song-select");
    const idx = parseInt(sel.value);
    if (isNaN(idx)) return;
    currentSongIdx = idx;
    renderInfo(idx);
    renderMethods(idx);
    renderRadar(idx);
}}

function renderInfo(idx) {{
    const s = SONGS[idx];
    document.getElementById("info-bar").style.display = "flex";
    document.getElementById("selected-name").textContent = s.name;
    document.getElementById("selected-meta").textContent = `${{s.album_en}} · ${{s.year}}`;
    document.getElementById("cover-img").src = s.cover_url || "";
}}

function renderMethods(idx) {{
    const container = document.getElementById("methods-container");
    container.innerHTML = "";
    METHODS.forEach(m => {{
        const results = SIMILARITIES[m].top_k[idx];
        const color = METHOD_COLORS[m];
        const card = document.createElement("div");
        card.className = "method-card";
        card.innerHTML = `
            <div class="card-header">
                <span>${{METHOD_LABELS[m]}}</span>
                <span class="badge">Top 10</span>
            </div>
            <div class="result-list">
                ${{results.map((r, i) => {{
                    const song = SONGS[r.idx];
                    const pct = (r.sim * 100).toFixed(1);
                    return `
                        <div class="result-item" onclick="selectComparison(${{idx}},${{r.idx}})">
                            <div class="rank">${{i+1}}</div>
                            <div class="song-details">
                                <div class="name">${{song.name}}</div>
                                <div class="meta">${{song.album_en}} · ${{song.year}}</div>
                            </div>
                            <div class="sim-bar"><div class="fill" style="width:${{pct}}%"></div></div>
                            <div class="sim-score">${{pct}}%</div>
                        </div>`;
                }}).join("")}}
            </div>`;
        container.appendChild(card);
    }});
}}

function renderRadar(idx) {{
    const s = SONGS[idx];
    const results = SIMILARITIES[METHODS[0]].top_k[idx];
    if (!results.length) return;

    const topSong = SONGS[results[0].idx];

    const categories = FEATURE_NAMES;
    const inputVals = categories.map(f => s.feats[f]);
    const topVals = categories.map(f => topSong.feats[f]);

    const traceInput = {{
        type: "scatterpolar",
        r: [...inputVals, inputVals[0]],
        theta: [...categories, categories[0]],
        fill: "toself",
        name: s.name,
        line: {{ color: "#fff", width: 2 }},
        marker: {{ color: "#fff" }},
    }};

    const traceTop = {{
        type: "scatterpolar",
        r: [...topVals, topVals[0]],
        theta: [...categories, categories[0]],
        fill: "toself",
        name: topSong.name,
        line: {{ color: "#4a9eff", width: 2 }},
        marker: {{ color: "#4a9eff" }},
    }};

    const layout = {{
        polar: {{
            bgcolor: "transparent",
            radialaxis: {{ visible: true, range: [0, 1], gridcolor: "#2a2a4e", color: "#666" }},
            angularaxis: {{ gridcolor: "#2a2a4e", color: "#888", tickfont: {{ size: 10 }} }},
        }},
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        margin: {{ l: 60, r: 60, t: 30, b: 30 }},
        font: {{ color: "#888" }},
        showlegend: true,
        legend: {{ font: {{ size: 10, color: "#aaa" }}, orientation: "h", y: -0.15 }},
        height: 400,
    }};

    Plotly.newPlot("radar-chart", [traceInput, traceTop], layout, {{ responsive: true, displayModeBar: false }});
}}

function selectComparison(inputIdx, resultIdx) {{
    const s = SONGS[inputIdx];
    const r = SONGS[resultIdx];
    const categories = FEATURE_NAMES;
    const inputVals = categories.map(f => s.feats[f]);
    const resVals = categories.map(f => r.feats[f]);

    const update = {{
        data: [
            {{ r: [...inputVals, inputVals[0]], theta: [...categories, categories[0]], name: s.name }},
            {{ r: [...resVals, resVals[0]], theta: [...categories, categories[0]], name: r.name }}
        ]
    }};
    Plotly.react("radar-chart", update.data, {{
        polar: {{
            bgcolor: "transparent",
            radialaxis: {{ visible: true, range: [0, 1], gridcolor: "#2a2a4e", color: "#666" }},
            angularaxis: {{ gridcolor: "#2a2a4e", color: "#888", tickfont: {{ size: 10 }} }},
        }},
        paper_bgcolor: "transparent",
        plot_bgcolor: "transparent",
        margin: {{ l: 60, r: 60, t: 30, b: 30 }},
        font: {{ color: "#888" }},
        showlegend: true,
        legend: {{ font: {{ size: 10, color: "#aaa" }}, orientation: "h", y: -0.15 }},
        height: 400,
    }}, {{ responsive: true, displayModeBar: false }});
}}

// ═══ ENTRY ═════════════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", init);
</script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Saved: {OUTPUT_HTML}")
    print(f"Size:  {os.path.getsize(OUTPUT_HTML)/1024:.0f} KB")

# ── 4. Main ─────────────────────────────────────────────────────────
def main():
    print("="*55)
    print("  Jay Chou — Song Recommender")
    print("="*55)
    print()

    df = load_data()
    print()

    sims, pca = compute_similarities(df)
    build_html(df, sims, pca)

    # Print a sample
    sample = "晴天"
    print(f"Sample recommendation for: {sample}")
    sample_idx = df[df["song_name"] == sample].index[0]
    for m in ["Cosine_Similarity", "KNN", "PCA_Embedding"]:
        mat = sims[m]
        sim_row = mat[sample_idx]
        top = np.argsort(-sim_row)[1:6]  # top 5 excluding self
        names = df.iloc[top]["song_name"].tolist()
        scores = [f"{sim_row[t]:.3f}" for t in top]
        print(f"  {m}: {', '.join(f'{n}({s})' for n,s in zip(names, scores))}")

    print()
    print(f"Open the HTML file in your browser.")
    print("="*55)


if __name__ == "__main__":
    main()
