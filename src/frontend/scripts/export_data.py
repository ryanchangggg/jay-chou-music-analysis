#!/usr/bin/env python3
import os, sys, json, warnings
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

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
DATA_DIR = os.path.join(ROOT, "data/raw")
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
RS = 42
np.random.seed(RS)
FEATURES = ["danceability","energy","valence","tempo","acousticness","instrumentalness","speechiness","loudness","key","duration_ms","mode"]

def export():
    feats = pd.read_csv(os.path.join(DATA_DIR, "spotify_features.csv"))
    disc = pd.read_csv(os.path.join(DATA_DIR, "jay_discography.csv"))[["song_name","album_en","album_cn","release_date"]]
    cov = pd.read_csv(os.path.join(DATA_DIR, "album_covers.csv"))
    lyr = pd.read_csv(os.path.join(DATA_DIR, "lyrics.csv"))
    df = feats.merge(disc, on="song_name").merge(cov, on="album_en")
    df["year"] = pd.to_datetime(df["release_date"]).dt.year.fillna(0).astype(int)
    df["cover_url"] = df["cover_url"].fillna("")

    X = StandardScaler().fit_transform(df[FEATURES].values); n = len(df)
    pca = PCA(n_components=2, random_state=RS); X_pca = pca.fit_transform(X)
    reducer = umap.UMAP(n_components=2, random_state=RS, n_neighbors=15, min_dist=0.1); X_umap = reducer.fit_transform(X)
    km = KMeans(n_clusters=2, random_state=RS, n_init=10); km_labels = km.fit_predict(X)
    hdb = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=2); hdb_labels = hdb.fit_predict(X)
    cos_sim = cosine_similarity(X)
    nn = NearestNeighbors(n_neighbors=n, metric="euclidean"); nn.fit(X)
    knn_d, knn_i = nn.kneighbors(X)
    knn_sim = np.zeros((n,n))
    for i in range(n):
        for j, d in zip(knn_i[i], knn_d[i]): knn_sim[i][j] = 1.0/(1.0+d)
    pca6 = PCA(n_components=6, random_state=RS); X_pca6 = pca6.fit_transform(X); pca_cos = cosine_similarity(X_pca6)

    yearly = df.groupby("year")[FEATURES].mean().reset_index()
    album_stats = df.groupby("album_en").agg(song_count=("song_name","count"),avg_popularity=("popularity","mean"),avg_year=("year","mean")).reset_index().sort_values("avg_year")
    eras = {"Early (2000-2003)":(2000,2003),"Golden (2004-2007)":(2004,2007),"Experimental (2008-2012)":(2008,2012),"Recent (2013-2022)":(2013,2022)}
    era_data = {}
    for en,(s,e) in eras.items():
        m=df[(df["year"]>=s)&(df["year"]<=e)]
        era_data[en]={"count":len(m),"features":{f:round(float(m[f].mean()),3) for f in FEATURES},"popularity":round(float(m["popularity"].mean()),1)}

    words = jieba.lcut(" ".join(lyr["lyrics"].dropna().tolist()))
    stpw = {"的","了","是","在","有","和","就","也","都","不","我","被","把","可","这","那","到","去","说","为","中","与","而","但","没","之","看","一","个","她","他","会","你","对","要","自己"}
    fw = [w for w in words if len(w)>1 and w not in stpw]
    wc = pd.Series(fw).value_counts().head(30); word_freq = {str(k):int(v) for k,v in wc.items()}
    cf = pd.Series(list("".join(df["song_name"]))).value_counts().head(20); title_freq = {str(k):int(v) for k,v in cf.items()}

    df["km"]=km_labels
    ca = {}
    for c in [0,1]:
        s=df[df["km"]==c]
        ca[f"c{c}"]={"size":len(s),"top_album":s.groupby("album_en").size().idxmax(),"top_songs":s.nlargest(5,"popularity")["song_name"].tolist()}
    maxp=df.loc[df["popularity"].idxmax()]; minp=df.loc[df["popularity"].idxmin()]

    songs = [{**{"name":r["song_name"],"album":r["album_en"],"year":int(r["year"]),"cover":r.get("cover_url",""),"popularity":int(r["popularity"])},
              "feats":{f:round(float(r[f]),3) for f in FEATURES}} for _,r in df.iterrows()]

    data = {
        "meta":{"songs":n,"albums":int(df["album_en"].nunique()),"year_min":int(df["year"].min()),"year_max":int(df["year"].max()),"avg_pop":round(float(df["popularity"].mean()),1)},
        "songs":songs, "features":FEATURES,
        "pca":{"coords":[[round(float(x),4) for x in r] for r in X_pca],"var":[round(float(v),4) for v in pca.explained_variance_ratio_]},
        "umap":{"coords":[[round(float(x),4) for x in r] for r in X_umap]},
        "clusters":{"kmeans":[int(x) for x in km_labels],"hdbscan":[int(x) for x in hdb_labels],"analysis":ca},
        "yearly":{"years":[int(y) for y in yearly["year"]],**{f:[round(float(v),4) for v in yearly[f]] for f in FEATURES}},
        "albums":album_stats.to_dict(orient="records"),"eras":era_data,
        "word_freq":word_freq,"title_freq":title_freq,
        "recommender":{"cosine":[[round(float(v),4) for v in r] for r in cos_sim],"knn":[[round(float(v),4) for v in r] for r in knn_sim],"pca_embed":[[round(float(v),4) for v in r] for r in pca_cos]},
        "insights":{"top_song":maxp["song_name"],"top_pop":int(maxp["popularity"]),"low_pop":int(minp["popularity"]),"noise":int(sum(hdb_labels==-1)),
                    "top_words":list(word_freq.keys())[:5],"top_char":list(title_freq.keys())[0],"words_total":len(fw),"words_unique":len(set(fw))},
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "data.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"Exported {os.path.getsize(os.path.join(OUT_DIR,'data.json'))/1024:.0f} KB")

export()
