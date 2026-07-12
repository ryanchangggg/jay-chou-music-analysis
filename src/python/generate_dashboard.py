#!/usr/bin/env python3
"""周杰伦音乐分析 — 完整 Dashboard 生成器"""
import os, sys, json, warnings, re
warnings.filterwarnings("ignore")
os.environ["MPLCONFIGDIR"] = "/private/tmp/matplotlib_cache"

import numpy as np
import pandas as pd
import jieba
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import hdbscan
import umap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUT_HTML = os.path.join(ROOT, "reports/figures/dashboard.html")

RS = 42
np.random.seed(RS)

# ── 1. 加载数据 ────────────────────────────────────────────────────
def load():
    feats = pd.read_csv(os.path.join(ROOT, "data/raw/spotify_features.csv"))
    disc  = pd.read_csv(os.path.join(ROOT, "data/raw/jay_discography.csv"))[["song_name","album_en","album_cn","release_date"]]
    cov   = pd.read_csv(os.path.join(ROOT, "data/raw/album_covers.csv"))
    df = feats.merge(disc, on="song_name").merge(cov, on="album_en")
    df["year"] = pd.to_datetime(df["release_date"]).dt.year
    df["cover_url"] = df["cover_url"].fillna("")
    print(f"Loaded {len(df)} songs")

    # Lyrics
    try:
        lyr = pd.read_csv(os.path.join(ROOT, "data/raw/lyrics.csv"))
        print(f"Loaded {len(lyr)} lyrics")
    except:
        lyr = None
    return df, lyr

# ── 2. 计算分析 ──────────────────────────────────────────────────────
FEATURES = ["danceability","energy","valence","tempo",
            "acousticness","instrumentalness","speechiness",
            "loudness","key","duration_ms","mode"]

def compute_all(df, lyr):
    X = StandardScaler().fit_transform(df[FEATURES].values)
    n = len(df)

    # PCA
    pca = PCA(n_components=2, random_state=RS)
    X_pca = pca.fit_transform(X)
    pca_var = pca.explained_variance_ratio_.tolist()

    # UMAP
    reducer = umap.UMAP(n_components=2, random_state=RS, n_neighbors=15, min_dist=0.1)
    X_umap = reducer.fit_transform(X)

    # KMeans (k=2 based on optimal silhouette)
    km = KMeans(n_clusters=2, random_state=RS, n_init=10)
    km_labels = km.fit_predict(X).tolist()

    # HDBSCAN
    hdb = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=2)
    hdb_labels = hdb.fit_predict(X).tolist()

    # Similarities for recommender (cosine)
    cos_sim = cosine_similarity(X).tolist()

    # KNN similarity
    nn = NearestNeighbors(n_neighbors=n, metric="euclidean")
    nn.fit(X)
    knn_dist, knn_idx = nn.kneighbors(X)
    knn_sim = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j, d in zip(knn_idx[i], knn_dist[i]):
            knn_sim[i][j] = round(1.0/(1.0+d), 4)
    cos_sim = [[round(v,4) for v in row] for row in cos_sim]

    # PCA-Embedding Cosine
    pca6 = PCA(n_components=6, random_state=RS)
    X_pca6 = pca6.fit_transform(X)
    pca_cos = cosine_similarity(X_pca6)
    pca_cos = [[round(v,4) for v in row] for row in pca_cos]

    # Yearly trends
    yearly = df.groupby("year")[FEATURES].mean().reset_index()

    # Album stats
    album_stats = df.groupby("album_en").agg(
        song_count=("song_name","count"),
        avg_popularity=("popularity","mean"),
        year=("year","mean"),
    ).reset_index()

    # Era stats
    era_map = {"Early (2000-2003)": (2000,2003), "Golden (2004-2007)": (2004,2007),
               "Experimental (2008-2012)": (2008,2012), "Recent (2013-2022)": (2013,2022)}
    era_data = {}
    for ename, (s,e) in era_map.items():
        m = df[(df["year"]>=s)&(df["year"]<=e)]
        era_data[ename] = {
            "count": len(m),
            "features": {f: round(float(m[f].mean()),3) for f in FEATURES},
            "popularity": round(float(m["popularity"].mean()),1),
        }

    # Lyrics word frequency
    wf = {}
    if lyr is not None:
        all_text = " ".join(lyr["lyrics"].dropna().tolist())
        words = jieba.lcut(all_text)
        stopwords = {"的","了","是","在","有","和","就","也","都","不","我","被","把","可","这","那","到","去","说","为","中","与","而","但","没","之","看","一","个","她","他","会","你","对","要","自己"}
        stopwords = {"的","了","是","在","有","和","就","也","都","不","我","被","把","可","这","那","到","去","说","为","中","与","而","但","没","之","看","一","个","她","他","会","你","对","要","自己"}
        filtered = [w for w in words if len(w) > 1 and w not in stopwords]
        wc = pd.Series(filtered).value_counts().head(30)
        wf = {str(k): int(v) for k,v in wc.items()}
        print(f"  Lyrics: {len(words)} words, {len(filtered)} filtered, {len(wf)} top")

    # Song title character frequency
    titles = "".join(df["song_name"].tolist())
    char_freq = pd.Series(list(titles)).value_counts().head(20)
    tf = {str(k): int(v) for k,v in char_freq.items()}

    # Build song data
    songs = []
    for _, r in df.iterrows():
        songs.append({
            "name": r["song_name"], "album": r["album_en"], "year": int(r["year"]),
            "cover": r.get("cover_url",""),
            "feats": {f: round(float(r[f]),3) for f in FEATURES},
            "popularity": int(r["popularity"]),
        })

    data = {
        "songs": songs,
        "pca": {"coords": X_pca.tolist(), "var": pca_var, "loadings": {
            "f": FEATURES,
            "PC1": [round(float(v),3) for v in pca.components_[0]],
            "PC2": [round(float(v),3) for v in pca.components_[1]],
        }},
        "umap": {"coords": X_umap.tolist()},
        "clusters": {"kmeans": km_labels, "hdbscan": hdb_labels},
        "yearly": {"years": yearly["year"].tolist(),
                   **{f: [round(float(v),3) for v in yearly[f]] for f in FEATURES}},
        "albums": album_stats.to_dict(orient="records"),
        "eras": era_data,
        "recommender": {
            "cosine": cos_sim,
            "knn": knn_sim,
            "pca_embed": pca_cos,
        },
        "lyrics_word_freq": wf,
        "title_char_freq": tf,
        "features": FEATURES,
    }
    return data


# ── 3. 构建 HTML ──────────────────────────────────────────────────
def build_html(data):
    jdata = json.dumps(data, ensure_ascii=False)
    wc_url = os.path.join(ROOT, "reports/figures/02_wordcloud.png")
    wc_b64 = ""
    if os.path.exists(wc_url):
        import base64
        with open(wc_url, "rb") as f:
            wc_b64 = base64.b64encode(f.read()).decode()
    wc_html = f'<div class="card"><h2>Word Cloud</h2><img class="wc-img" src="data:image/png;base64,{wc_b64}" alt="Word Cloud"></div>' if wc_b64 else ""

    TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jay Chou Music Analysis Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,sans-serif; background:#0a0a1a; color:#ccc; }}
.nav {{ position:sticky; top:0; z-index:100; background:#12122a; border-bottom:1px solid #2a2a4a;
        display:flex; align-items:center; gap:4px; padding:0 20px; overflow-x:auto; }}
.nav .brand {{ font-size:1em; font-weight:700; color:#fff; margin-right:16px; white-space:nowrap;
               background:linear-gradient(135deg,#4a9eff,#6c5ce7); -webkit-background-clip:text;
               -webkit-text-fill-color:transparent; }}
.nav button {{ padding:12px 16px; border:none; background:transparent; color:#777; font-size:0.85em;
               cursor:pointer; white-space:nowrap; transition:all 0.2s; border-bottom:2px solid transparent; }}
.nav button:hover {{ color:#aaa; background:#1a1a34; }}
.nav button.active {{ color:#4a9eff; border-bottom-color:#4a9eff; }}
.page {{ display:none; max-width:1400px; margin:0 auto; padding:20px; }}
.page.active {{ display:block; }}
.card {{ background:#12122a; border-radius:10px; padding:16px; margin:12px 0; }}
.card h2 {{ font-size:1.2em; margin-bottom:12px; color:#ddd; }}
.stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:12px 0; }}
.stat {{ background:#1a1a34; border-radius:8px; padding:12px; text-align:center; }}
.stat .val {{ font-size:1.6em; font-weight:700; color:#4a9eff; }}
.stat .lbl {{ font-size:0.8em; color:#666; margin-top:4px; }}
.plot {{ width:100%; height:420px; }}
table.data {{ width:100%; border-collapse:collapse; font-size:0.85em; }}
table.data th {{ background:#1a1a34; padding:8px 10px; text-align:left; color:#888; cursor:pointer;
                 position:sticky; top:48px; z-index:10; }}
table.data td {{ padding:6px 10px; border-bottom:1px solid #1a1a34; }}
table.data tr:hover td {{ background:#1a1a34; }}
tr.clickable {{ cursor:pointer; }}
.search-input {{ width:100%; padding:10px 14px; border-radius:8px; border:1px solid #333;
                background:#16213e; color:#e0e0e0; font-size:0.9em; outline:none; margin-bottom:10px; }}
.sel {{ padding:8px 14px; border-radius:6px; border:1px solid #333; background:#16213e; color:#e0e0e0; font-size:0.9em; outline:none; }}
.btn {{ padding:8px 20px; border:none; border-radius:6px; background:linear-gradient(135deg,#4a9eff,#6c5ce7); color:#fff;
        font-size:0.9em; cursor:pointer; }}
.flex {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap; }}
.flex-grow {{ flex:1; min-width:200px; }}
.grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
@media(max-width:768px) {{ .grid-2 {{ grid-template-columns:1fr; }} }}
.wc-img {{ max-width:100%; border-radius:8px; }}
.rec-results {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }}
@media(max-width:900px) {{ .rec-results {{ grid-template-columns:1fr; }} }}
.rec-card {{ background:#1a1a34; border-radius:8px; padding:10px; }}
.rec-card h4 {{ font-size:0.9em; color:#4a9eff; margin-bottom:8px; }}
.rec-item {{ display:flex; justify-content:space-between; padding:4px 0; font-size:0.85em; border-bottom:1px solid #2a2a4e; }}
.rec-item:last-child {{ border:none; }}
.rec-item .rn {{ color:#666; width:20px; }}
.rec-item .rn {{ color:#666; width:20px; }}
#about p {{ margin:8px 0; line-height:1.6; font-size:0.9em; color:#999; }}
#about strong {{ color:#ddd; }}
</style>
</head><body>

<div class="nav">
  <span class="brand">🎵 Jay Chou</span>
  <button class="active" onclick="switchTab('home')">🏠 Home</button>
  <button onclick="switchTab('evolution')">📈 Evolution</button>
  <button onclick="switchTab('lyrics')">📝 Lyrics</button>
  <button onclick="switchTab('cluster')">🔮 Cluster</button>
  <button onclick="switchTab('explorer')">🔍 Explorer</button>
  <button onclick="switchTab('recommender')">🎯 Recommend</button>
  <button onclick="switchTab('about')">ℹ️ About</button>
</div>

<div id="page-home" class="page active"></div>
<div id="page-evolution" class="page"></div>
<div id="page-lyrics" class="page"></div>
<div id="page-cluster" class="page"></div>
<div id="page-explorer" class="page"></div>
<div id="page-recommender" class="page"></div>
<div id="page-about" class="page"></div>

<script>
// ══════════════════════════════════════════════════════════════════
const D = __DATA__;
const {songs, pca, umap, clusters, yearly, albums, eras, recommender, lyrics_word_freq:wf, title_char_freq:tf, features:FEATS} = D;
const COLORS = ['#4a9eff','#6c5ce7','#00cec9','#e17055','#fdcb6e','#00b894','#6c5ce7','#e84393','#00cec9','#e17055'];

// ═══ TAB ══════════════════════════════════════════════════════════
function switchTab(name) {{
    document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
    document.querySelector(`.nav button[onclick*='{name}']`).classList.add('active');
    document.getElementById(`page-${{name}}`).classList.add('active');
    if (name==='home') renderHome();
    if (name==='evolution') renderEvolution();
    if (name==='cluster') renderCluster();
    if (name==='explorer') renderExplorer();
}}

// ═══ HOME ══════════════════════════════════════════════════════════
let homeRendered = false;
function renderHome() {{
    if (homeRendered) return; homeRendered=true;
    const page = document.getElementById('page-home');
    const years = [...new Set(songs.map(s=>s.year))].sort();
    const avgPop = (songs.reduce((s,x)=>s+x.popularity,0)/songs.length).toFixed(1);
    page.innerHTML = `
    <div class="stats">
      <div class="stat"><div class="val">${{songs.length}}</div><div class="lbl">Songs</div></div>
      <div class="stat"><div class="val">${{new Set(songs.map(s=>s.album)).size}}</div><div class="lbl">Albums</div></div>
      <div class="stat"><div class="val">${{years[0]}}-${{years[years.length-1]}}</div><div class="lbl">Years Span</div></div>
      <div class="stat"><div class="val">${{avgPop}}</div><div class="lbl">Avg Popularity</div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Popularity Distribution</h2><div id="pop-dist" class="plot"></div></div>
      <div class="card"><h2>Songs per Album</h2><div id="album-bar" class="plot"></div></div>
    </div>
    <div class="card"><h2>Feature Overview</h2><div id="feat-overview" class="plot"></div></div>`;

    // Popularity distribution
    Plotly.newPlot('pop-dist', [{{
        x: songs.map(s=>s.popularity), type:'histogram', marker:{{color:'#4a9eff',line:{{color:'#0a0a1a',width:1}}}},
        nbinsx:15, name:''
    }}], {{margin:{{l:40,r:10,t:10,b:30}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
        font:{{color:'#888'}},xaxis:{{title:'Popularity',gridcolor:'#2a2a4e'}},yaxis:{{gridcolor:'#2a2a4e'}},
        bargap:0.1}}, {{responsive:true,displayModeBar:false}});

    // Albums per song count
    const albumCnt = Object.entries(songs.reduce((a,s)=>{{a[s.album]=(a[s.album]||0)+1;return a}},{{}}))
        .sort((a,b)=>b[1]-a[1]);
    Plotly.newPlot('album-bar', [{{
        x: albumCnt.map(a=>a[1]), y: albumCnt.map(a=>a[0]),
        type:'bar', orientation:'h', marker:{{color:COLORS.map((_,i)=>COLORS[i%COLORS.length])}},
        text: albumCnt.map(a=>a[1]), textposition:'outside', textfont:{{color:'#888',size:10}},
    }}], {{margin:{{l:120,r:30,t:10,b:30}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
        font:{{color:'#888'}},xaxis:{{gridcolor:'#2a2a4e'}},yaxis:{{autorange:'reversed'}}}},
        {{responsive:true,displayModeBar:false}});

    // Feature overview parallel coordinates
    const fmeans = FEATS.map(f => ({{
        label: f, mean: songs.reduce((s,x)=>s+x.feats[f],0)/songs.length
    }}));
    Plotly.newPlot('feat-overview', [{{
        type:'box', q1:[], median:[], q3:[], lowerfence:[], upperfence:[],
        y: songs.flatMap(s => FEATS.map(f => s.feats[f])),
        x: songs.flatMap(s => FEATS),
        marker:{{color:'#4a9eff',opacity:0.6}},
        boxmean:'sd',
    }}], {{margin:{{l:40,r:10,t:10,b:60}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
        font:{{color:'#888'}},xaxis:{{tickangle:-30}},yaxis:{{gridcolor:'#2a2a4e',title:'Scaled Value'}}}},
        {{responsive:true,displayModeBar:false}});
}}

// ═══ EVOLUTION ═══════════════════════════════════════════════════
let evoRendered = false;
function renderEvolution() {{
    if (evoRendered) return; evoRendered=true;
    const page = document.getElementById('page-evolution');
    const evoFeats = ['energy','danceability','acousticness','valence','speechiness','loudness'];
    page.innerHTML = `
    <div class="card"><h2>Feature Trends Over Years</h2><div id="evo-trend" class="plot" style="height:500px"></div></div>
    <div class="grid-2">
      <div class="card"><h2>Era Comparison</h2><div id="era-comp" class="plot"></div></div>
      <div class="card"><h2>Era Statistics</h2><div id="era-table"></div></div>
    </div>`;

    // Trends
    const traces = evoFeats.map(f => ({{
        x: yearly.years, y: yearly[f], mode:'lines+markers', name:f,
        line:{{width:2}}, marker:{{size:5}},
    }}));
    Plotly.newPlot('evo-trend', traces, {{
        margin:{{l:50,r:10,t:10,b:40}}, paper_bgcolor:'transparent', plot_bgcolor:'transparent',
        font:{{color:'#888'}}, xaxis:{{dtick:2,gridcolor:'#2a2a4e'}},
        yaxis:{{gridcolor:'#2a2a4e',title:'Mean Value'}},
        legend:{{font:{{size:10}},orientation:'h',y:1.05}},
    }}, {{responsive:true,displayModeBar:false}});

    // Era radar
    const eraNames = Object.keys(eras);
    const eraRadar = eraNames.map((en,i) => ({{
        type:'scatterpolar', r: Object.values(eras[en].features).concat(Object.values(eras[en].features)[0]),
        theta: [...FEATS, FEATS[0]], fill:'toself', name:`${{en}} (n=${{eras[en].count}},pop=${{eras[en].popularity}})`,
        line:{{color:COLORS[i]}}, marker:{{color:COLORS[i]}},
    }}));
    Plotly.newPlot('era-comp', eraRadar, {{
        polar:{{bgcolor:'transparent',radialaxis:{{visible:true,range:[0,1],gridcolor:'#2a2a4e',color:'#666'}},
               angularaxis:{{gridcolor:'#2a2a4e',color:'#888',tickfont:{{size:9}}}}}},
        paper_bgcolor:'transparent', margin:{{l:60,r:60,t:10,b:30}}, font:{{color:'#888'}},
        legend:{{font:{{size:8}}}},
    }}, {{responsive:true,displayModeBar:false}});

    // Era table
    const et = eraNames.map(en => `<tr><td>${{en}}</td><td>${{eras[en].count}}</td><td>${{eras[en].popularity}}</td></tr>`).join('');
    document.getElementById('era-table').innerHTML = `<table class="data"><tr><th>Era</th><th>Songs</th><th>Avg Pop.</th></tr>${{et}}</table>`;
}}

// ═══ LYRICS ═══════════════════════════════════════════════════════
let lyrRendered = false;
function renderLyrics() {{
    if (lyrRendered) return; lyrRendered=true;
    const page = document.getElementById('page-lyrics');
    const wfArr = Object.entries(wf).sort((a,b)=>b[1]-a[1]).slice(0,25);
    const tfArr = Object.entries(tf).sort((a,b)=>b[1]-a[1]).slice(0,15);
    page.innerHTML = `
    <div class="grid-2">
      <div class="card"><h2>Top Word Frequency (Jieba)</h2><div id="wf-chart" class="plot"></div></div>
      <div class="card"><h2>Song Title Character Frequency</h2><div id="tf-chart" class="plot"></div></div>
    </div>
    ${{imgHtml}}`;

    // Word freq bar
    Plotly.newPlot('wf-chart', [{{
        x: wfArr.map(a=>a[1]), y: wfArr.map(a=>a[0]), type:'bar', orientation:'h',
        marker:{{color:'#6c5ce7'}},
        text: wfArr.map(a=>a[1]), textposition:'outside', textfont:{{size:9,color:'#888'}},
    }}], {{margin:{{l:90,r:30,t:10,b:30}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
        font:{{color:'#888'}},xaxis:{{gridcolor:'#2a2a4e'}},yaxis:{{autorange:'reversed'}}}},
        {{responsive:true,displayModeBar:false}});

    // Title char freq
    Plotly.newPlot('tf-chart', [{{
        x: tfArr.map(a=>a[0]), y: tfArr.map(a=>a[1]), type:'bar',
        marker:{{color:'#00cec9'}},
        text: tfArr.map(a=>a[1]), textposition:'outside', textfont:{{size:9,color:'#888'}},
    }}], {{margin:{{l:40,r:20,t:10,b:60}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
        font:{{color:'#888'}},xaxis:{{tickangle:-30}},yaxis:{{gridcolor:'#2a2a4e'}}}},
        {{responsive:true,displayModeBar:false}});
}}

// ═══ CLUSTER ═════════════════════════════════════════════════════
let cluRendered = false;
function renderCluster() {{
    if (cluRendered) return; cluRendered=true;
    const page = document.getElementById('page-cluster');
    const hover = songs.map(s => `${{s.name}}<br>Album: ${{s.album}} (${{s.year}})<br>Pop: ${{s.popularity}}`);
    page.innerHTML = `
    <div class="grid-2">
      <div class="card"><h2>PCA + KMeans (k=2)</h2><div id="clu-pca" class="plot"></div></div>
      <div class="card"><h2>UMAP + HDBSCAN</h2><div id="clu-umap" class="plot"></div></div>
    </div>
    <div class="card"><h2>Feature Profiles by KMeans Cluster</h2><div id="clu-profile" class="plot"></div></div>`;

    // PCA scatter
    const ks = [...new Set(clusters.kmeans)].sort();
    const pcTraces = ks.map(k => ({{
        x: [], y: [], mode:'markers', name:`Cluster ${{k}}`, text:[], hoverinfo:'text',
        marker:{{size:6,color:COLORS[k]}},
    }}));
    songs.forEach((s,i) => {{
        const k = clusters.kmeans[i];
        const ci = ks.indexOf(k);
        pcTraces[ci].x.push(pca.coords[i][0]);
        pcTraces[ci].y.push(pca.coords[i][1]);
        pcTraces[ci].text.push(hover[i]);
    }});
    Plotly.newPlot('clu-pca', pcTraces, {{
        margin:{{l:40,r:10,t:10,b:40}}, paper_bgcolor:'transparent', plot_bgcolor:'transparent',
        font:{{color:'#888'}}, xaxis:{{gridcolor:'#2a2a4e',title:'PC1'}}, yaxis:{{gridcolor:'#2a2a4e',title:'PC2'}},
        legend:{{font:{{size:9}}}},
    }}, {{responsive:true,displayModeBar:false}});

    // UMAP scatter (HDBSCAN)
    const hs = [...new Set(clusters.hdbscan)].sort((a,b)=>a-b);
    const umTraces = hs.map(k => {{
        const lab = k===-1?'Noise':`Cluster ${{k}}`;
        return {{x:[],y:[],mode:'markers',name:lab,text:[],hoverinfo:'text',
                marker:{{size:6,color:k===-1?'#666':COLORS[(k+1)%COLORS.length],
                        symbol:k===-1?'x':'circle'}}}};
    }});
    songs.forEach((s,i) => {{
        const k = clusters.hdbscan[i];
        const ci = hs.indexOf(k);
        if (ci<0) return;
        umTraces[ci].x.push(umap.coords[i][0]);
        umTraces[ci].y.push(umap.coords[i][1]);
        umTraces[ci].text.push(hover[i]);
    }});
    Plotly.newPlot('clu-umap', umTraces, {{
        margin:{{l:40,r:10,t:10,b:40}}, paper_bgcolor:'transparent', plot_bgcolor:'transparent',
        font:{{color:'#888'}}, xaxis:{{gridcolor:'#2a2a4e',title:'UMAP1'}}, yaxis:{{gridcolor:'#2a2a4e',title:'UMAP2'}},
        legend:{{font:{{size:9}}}},
    }}, {{responsive:true,displayModeBar:false}});

    // Cluster feature profiles
    const clust0 = songs.filter((_,i)=>clusters.kmeans[i]===0);
    const clust1 = songs.filter((_,i)=>clusters.kmeans[i]===1);
    const avg0 = FEATS.map(f => clust0.reduce((s,x)=>s+x.feats[f],0)/clust0.length);
    const avg1 = FEATS.map(f => clust1.reduce((s,x)=>s+x.feats[f],0)/clust1.length);
    Plotly.newPlot('clu-profile', [
        {{type:'bar',x:FEATS,y:avg0,name:'Cluster 0',marker:{{color:COLORS[0]}}}},
        {{type:'bar',x:FEATS,y:avg1,name:'Cluster 1',marker:{{color:COLORS[1]}}}},
    ], {{barmode:'group',margin:{{l:40,r:10,t:10,b:60}},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
        font:{{color:'#888'}},xaxis:{{tickangle:-30,gridcolor:'#2a2a4e'}},yaxis:{{gridcolor:'#2a2a4e'}},
        legend:{{font:{{size:9}}}}}}, {{responsive:true,displayModeBar:false}});
}}

// ═══ EXPLORER ════════════════════════════════════════════════════
let expRendered = false;
function renderExplorer() {{
    if (expRendered) return; expRendered=true;
    const page = document.getElementById('page-explorer');
    const allAlbums = [...new Set(songs.map(s=>s.album))].sort();
    page.innerHTML = `
    <div class="flex">
      <div class="flex-grow"><input class="search-input" id="exp-search" placeholder="Search songs..." oninput="filterExplorer()"></div>
      <select class="sel" id="exp-album" onchange="filterExplorer()">
        <option value="">All Albums</option>
        ${{allAlbums.map(a=>`<option value="${{a}}">${{a}}</option>`).join('')}}
      </select>
    </div>
    <div style="overflow-x:auto"><table class="data" id="exp-table">
      <thead><tr>
        <th onclick="sortExplorer(0)">#</th>
        <th onclick="sortExplorer(1)">Song</th>
        <th onclick="sortExplorer(2)">Album</th>
        <th onclick="sortExplorer(3)">Year</th>
        <th onclick="sortExplorer(4)">Popularity</th>
        ${{FEATS.map((f,i)=>`<th onclick="sortExplorer(${{i+5}})">${{f}}</th>`).join('')}}
      </tr></thead>
      <tbody id="exp-body"></tbody>
    </table></div>`;
    window.expSort = {{col:0,dir:1}};
    filterExplorer();
}}

function filterExplorer() {{
    const q = (document.getElementById('exp-search')?.value||'').toLowerCase();
    const alb = document.getElementById('exp-album')?.value||'';
    let flt = songs.filter(s => {{
        if (q && !s.name.toLowerCase().includes(q) && !s.album.toLowerCase().includes(q)) return false;
        if (alb && s.album !== alb) return false;
        return true;
    }});
    window.expFiltered = flt;
    renderExplorerTable(flt);
}}

function sortExplorer(col) {{
    const flt = window.expFiltered||songs;
    if (window.expSort.col === col) window.expSort.dir *= -1;
    else {{window.expSort.col=col; window.expSort.dir=1;}}
    flt.sort((a,b) => {{
        let va = col===0 ? songs.indexOf(a) : col===1 ? a.name : col===2 ? a.album : col===3 ? a.year : col===4 ? a.popularity : a.feats[FEATS[col-5]];
        let vb = col===0 ? songs.indexOf(b) : col===1 ? b.name : col===2 ? b.album : col===3 ? b.year : col===4 ? b.popularity : b.feats[FEATS[col-5]];
        if (typeof va==='string') return window.expSort.dir * va.localeCompare(vb);
        return window.expSort.dir * (va - vb);
    }});
    renderExplorerTable(flt);
}}

function renderExplorerTable(flt) {{
    const tbody = document.getElementById('exp-body');
    tbody.innerHTML = flt.map((s,i) => `<tr class="clickable" onclick="selectSongForRec('${{s.name}}')">
        <td>${{i+1}}</td>
        <td>${{s.name}}</td>
        <td>${{s.album}}</td>
        <td>${{s.year}}</td>
        <td>${{s.popularity}}</td>
        ${{FEATS.map(f=>`<td>${{(s.feats[f]*100).toFixed(1)}}%</td>`).join('')}}
    </tr>`).join('');
}}

function selectSongForRec(name) {{
    const sel = document.getElementById('rec-select');
    if (sel) {{ sel.value = name; switchTab('recommender'); recommend(); }}
}}

// ═══ RECOMMENDER ═════════════════════════════════════════════════
let selectedMethod = 'cosine';
function renderRec() {{
    const page = document.getElementById('page-recommender');
    const options = songs.map((s,i) => `<option value="${{i}}">${{s.name}} — ${{s.album}} (${{s.year}})</option>`).join('');
    page.innerHTML = `
    <div class="flex" style="margin-bottom:12px">
      <div class="flex-grow"><select class="sel" id="rec-select" style="width:100%">${{options}}</select></div>
      <button class="btn" onclick="recommend()">🎯 Recommend</button>
    </div>
    <div class="flex" style="margin-bottom:12px">
      <select class="sel" id="rec-method" onchange="selectedMethod=this.value;recommend()">
        <option value="cosine">Cosine Similarity</option>
        <option value="knn">KNN (Euclidean)</option>
        <option value="pca_embed">PCA Embedding</option>
      </select>
    </div>
    <div id="rec-results"></div>
    <div class="card"><div id="rec-radar" class="plot" style="height:350px"></div></div>`;
}}

function recommend() {{
    const sel = document.getElementById('rec-select');
    const idx = parseInt(sel?.value);
    if (isNaN(idx) || idx<0) return;
    const s = songs[idx];
    const mat = recommender[document.getElementById('rec-method')?.value||'cosine'];
    const sims = mat[idx].map((v,i)=>({{idx:i,sim:v}})).filter(x=>x.idx!==idx).sort((a,b)=>b.sim-a.sim).slice(0,10);
    const html = sims.map((r,i) => {{
        const rs = songs[r.idx];
        return `<div class="rec-item"><span><span class="rn">${{i+1}}</span> ${{rs.name}}</span><span style="color:#4a9eff">${{(r.sim*100).toFixed(1)}}%</span></div>`;
    }}).join('');
    document.getElementById('rec-results').innerHTML = `<div class="rec-card"><h4>Top 10 Similar to "${'{s.name}'}"</h4>${{html}}</div>`;

    // Radar
    const top = songs[sims[0].idx];
    Plotly.newPlot('rec-radar', [
        {{type:'scatterpolar', r:[...FEATS.map(f=>s.feats[f]),s.feats[FEATS[0]]],
          theta:[...FEATS,FEATS[0]], fill:'toself', name:s.name, line:{{color:'#fff',width:2}}}},
        {{type:'scatterpolar', r:[...FEATS.map(f=>top.feats[f]),top.feats[FEATS[0]]],
          theta:[...FEATS,FEATS[0]], fill:'toself', name:top.name, line:{{color:'#4a9eff',width:2}}}},
    ], {{polar:{{bgcolor:'transparent',radialaxis:{{visible:true,range:[0,1],gridcolor:'#2a2a4e',color:'#666'}},
             angularaxis:{{gridcolor:'#2a2a4e',color:'#888',tickfont:{{size:9}}}}}},
       paper_bgcolor:'transparent',margin:{{l:60,r:60,t:10,b:30}},font:{{color:'#888'}},
       legend:{{font:{{size:10}},orientation:'h',y:-0.15}}}},
       {{responsive:true,displayModeBar:false}});
}}

// ═══ ABOUT ═══════════════════════════════════════════════════════
function renderAbout() {{
    document.getElementById('page-about').innerHTML = `
    <div class="card">
      <h2>About This Dashboard</h2>
      <p><strong>Project:</strong> Comprehensive music analysis of Jay Chou's discography, covering 174 songs across 16 albums from 2000 to 2022.</p>
      <p><strong>Data:</strong> Audio features from Spotify API (danceability, energy, valence, tempo, acousticness, etc.), lyrics text, and album metadata.</p>
      <p><strong>Methods:</strong>
        <br>• <strong>Evolution:</strong> Yearly feature trends and era comparison
        <br>• <strong>Lyrics:</strong> Jieba word segmentation, character frequency analysis
        <br>• <strong>Clustering:</strong> PCA/UMAP dimensionality reduction, KMeans and HDBSCAN clustering
        <br>• <strong>Recommender:</strong> Content-based recommendation via Cosine Similarity, KNN, and PCA Embedding
        <br>• <strong>Prediction:</strong> RandomForest, XGBoost, LightGBM, CatBoost with SHAP analysis
      </p>
      <p><strong>Tech Stack:</strong> Python (scikit-learn, xgboost, lightgbm, catboost, umap-learn, hdbscan, shap), Plotly.js for interactive visualization.</p>
      <p><strong>Generated:</strong> July 2026</p>
    </div>`;
}}

// ═══ INIT ════════════════════════════════════════════════════════
renderRec();
renderAbout();
</script>
</body></html>"""
    html = TEMPLATE.replace("__DATA__", jdata).replace("__WC_HTML__", wc_html)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard: {os.path.getsize(OUT_HTML)/1024:.0f} KB")


# ── 主程序 ────────────────────────────────────────────────────────────
def main():
    print("="*55)
    print("  Jay Chou — Dashboard Generator")
    print("="*55)
    df, lyr = load()
    data = compute_all(df, lyr)
    build_html(data)
    print("Done.")

if __name__ == "__main__":
    main()
