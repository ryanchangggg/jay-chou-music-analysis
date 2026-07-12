#!/usr/bin/env python3
"""
周杰伦 — 流行度预测模型分析
模型: RandomForest / XGBoost / LightGBM / CatBoost
输出: 特征重要性 · SHAP · 偏依赖图 · 模型评估
"""
import os, sys, warnings
warnings.filterwarnings("ignore")
os.environ["MPLCONFIGDIR"] = "/private/tmp/matplotlib_cache"

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import partial_dependence
import xgboost as xgb, lightgbm as lgb, catboost as cb, shap
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
OUTPUT_HTML  = os.path.join(PROJECT_ROOT, "outputs/figures/popularity_prediction.html")
DATA_PATH    = os.path.join(PROJECT_ROOT, "data/raw/spotify_features.csv")

TARGET   = "popularity"
FEATURES = ["danceability","energy","valence","tempo",
            "acousticness","instrumentalness","speechiness",
            "loudness","key","duration_ms","mode"]
RS, N_EST = 42, 300
np.random.seed(RS)

def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} songs, {len(FEATURES)} features"); return df

def prep(df):
    X_train, X_test, y_train, y_test = train_test_split(
        df[FEATURES].values, df[TARGET].values, test_size=0.2, random_state=RS)
    print(f"Train: {len(X_train)}  Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test

def build_models():
    rf  = RandomForestRegressor(n_estimators=N_EST, max_depth=8, min_samples_leaf=2, random_state=RS, n_jobs=-1)
    xg  = xgb.XGBRegressor(n_estimators=N_EST, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, enable_categorical=False, random_state=RS, verbosity=0, n_jobs=-1)
    lgbm = lgb.LGBMRegressor(n_estimators=N_EST, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, random_state=RS, verbose=-1, n_jobs=-1)
    cb_m = cb.CatBoostRegressor(iterations=N_EST, depth=6, learning_rate=0.1, subsample=0.8, random_seed=RS, verbose=0, allow_writing_files=False)
    return {"RandomForest": rf, "XGBoost": xg, "LightGBM": lgbm, "CatBoost": cb_m}

def evaluate(models, X_train, X_test, y_train, y_test):
    results, trained, fi = [], {}, {}
    colors = {"RandomForest":"#2E86AB","XGBoost":"#A23B72","LightGBM":"#F18F01","CatBoost":"#C73E1D"}
    for name, model in models.items():
        print(f"  {name}...", end=" ", flush=True)
        model.fit(X_train, y_train) if name != "CatBoost" else model.fit(X_train, y_train, cat_features=[])
        yp = model.predict(X_test)
        r2, rmse, mae = r2_score(y_test, yp), np.sqrt(mean_squared_error(y_test, yp)), mean_absolute_error(y_test, yp)
        results.append({"Model": name, "R²": round(r2, 3), "RMSE": round(rmse, 2), "MAE": round(mae, 2)})
        trained[name] = model
        imp = model.feature_importances_
        fi[name] = pd.DataFrame({"feature": FEATURES, "importance": imp / imp.sum()}).sort_values("importance", ascending=False)
        print(f"R²={r2:.3f}  RMSE={rmse:.2f}  MAE={mae:.2f}")
    return pd.DataFrame(results), trained, fi, colors

def compute_shap(models, X_train, X_test):
    sr = {}
    for name, model in models.items():
        print(f"  SHAP {name}...", end=" ", flush=True)
        try:
            kw = {"feature_perturbation": "tree_path_dependent"} if name == "XGBoost" else {}
            sv = shap.TreeExplainer(model, X_train[:100], **kw).shap_values(X_test[:100])
            sv = sv[0] if isinstance(sv, list) else sv
            sr[name] = pd.DataFrame({"feature": FEATURES, "mean_abs_shap": np.abs(sv).mean(axis=0)}).sort_values("mean_abs_shap", ascending=False)
            print("done")
        except Exception as e:
            print(f"SKIP ({e})")
            sr[name] = None
    return sr

def compute_pdp(models, X_train, top_n=6):
    avg_imp = pd.DataFrame({n: m.feature_importances_ for n, m in models.items()}, index=FEATURES).mean(axis=1).sort_values(ascending=False)
    top_fs = avg_imp.head(top_n).index.tolist()
    top_ix = [FEATURES.index(f) for f in top_fs]
    pdp = {}
    for f, ix in zip(top_fs, top_ix):
        pdp[f] = {}
        for name, model in models.items():
            try:
                res = partial_dependence(model, X_train[:300], [ix], kind="average")
                pdp[f][name] = {"values": res["values"][0], "average": res["average"][0]}
            except:
                pdp[f][name] = None
    return pdp, top_fs

def build_main(results_df, fi, shap_r, colors, y_test, models, X_test):
    fig = make_subplots(rows=5, cols=2,
        subplot_titles=("Model Comparison", "Predicted vs Actual",
            "RandomForest Importance", "XGBoost Importance",
            "LightGBM Importance", "CatBoost Importance",
            "SHAP: RandomForest", "SHAP: LightGBM",
            "SHAP: CatBoost", ""),
        specs=[[{"type":"table"},{"type":"scatter"}],
               [{"type":"bar"},{"type":"bar"}],
               [{"type":"bar"},{"type":"bar"}],
               [{"type":"bar"},{"type":"bar"}],
               [{"type":"bar"},{"type":"bar"}]],
        row_heights=[0.35, 0.6, 0.6, 0.6, 0.6],
        horizontal_spacing=0.08, vertical_spacing=0.06)

    # Row 1 Col 1: Table
    fig.add_trace(go.Table(header=dict(values=["<b>Model</b>","<b>R²</b>","<b>RMSE</b>","<b>MAE</b>"], fill_color="paleturquoise", align="left"),
        cells=dict(values=[results_df["Model"],[f"{v:.3f}" for v in results_df["R²"]],[f"{v:.2f}" for v in results_df["RMSE"]],[f"{v:.2f}" for v in results_df["MAE"]]], align="left")),
        row=1, col=1)

    # Row 1 Col 2: Pred vs Actual
    for name, model in models.items():
        yp = model.predict(X_test)
        fig.add_trace(go.Scatter(x=y_test, y=yp, mode="markers", name=name,
            marker=dict(color=colors[name], size=6, opacity=0.7),
            text=[f"P:{p:.0f} A:{a:.0f}" for p,a in zip(yp,y_test)], hoverinfo="text"),
            row=1, col=2)
    fig.add_trace(go.Scatter(x=[y_test.min(),y_test.max()], y=[y_test.min(),y_test.max()],
        mode="lines", name="Perfect", line=dict(color="gray", dash="dash")), row=1, col=2)

    # Rows 2-3: Feature Importance
    for i, name in enumerate(["RandomForest","XGBoost","LightGBM","CatBoost"]):
        r, c = [(2,1),(2,2),(3,1),(3,2)][i]
        d = fi[name].head(11)
        fig.add_trace(go.Bar(x=d["importance"], y=d["feature"], orientation="h",
            marker=dict(color=colors[name]),
            text=[f"{v:.1%}" for v in d["importance"]], textposition="outside", textfont=dict(size=8)),
            row=r, col=c)

    # Rows 4-5: SHAP
    shap_names = [n for n in ["RandomForest","LightGBM","CatBoost"] if shap_r.get(n) is not None]
    shap_pos = [(4,1),(4,2),(5,1)]
    for i, name in enumerate(shap_names[:3]):
        r, c = shap_pos[i]
        d = shap_r[name].head(11)
        fig.add_trace(go.Bar(x=d["mean_abs_shap"], y=d["feature"], orientation="h",
            marker=dict(color=colors[name]),
            text=[f"{v:.2f}" for v in d["mean_abs_shap"]], textposition="outside", textfont=dict(size=8)),
            row=r, col=c)
        fig.update_xaxes(title_text="mean |SHAP|", row=r, col=c)
        fig.update_yaxes(title_text="", row=r, col=c)

    fig.update_layout(title=dict(text="<b>Jay Chou — Popularity Prediction</b>", font=dict(size=16)),
        height=1800, template="plotly_white", legend=dict(font=dict(size=9), orientation="h"),
        margin=dict(l=50, r=80, t=100, b=50))
    return fig

def build_pdp_page(pdp_r, top_fs, models, colors):
    nf = len(top_fs)
    fig = make_subplots(rows=nf, cols=1, subplot_titles=[f"Partial Dependence: {f}" for f in top_fs], vertical_spacing=0.04)
    for i, f in enumerate(top_fs):
        for name in models:
            p = pdp_r.get(f, {}).get(name)
            if p is None: continue
            fig.add_trace(go.Scatter(x=p["values"], y=p["average"], mode="lines+markers",
                name=name, legendgroup=name, marker=dict(size=5, color=colors[name]),
                line=dict(width=2, color=colors[name]), showlegend=(i==0)),
                row=i+1, col=1)
        fig.update_xaxes(title_text=f, row=i+1, col=1)
        fig.update_yaxes(title_text="Popularity", row=i+1, col=1)
    fig.update_layout(title=dict(text="<b>Partial Dependence Plots</b>", font=dict(size=16)),
        height=300*nf, template="plotly_white", legend=dict(font=dict(size=9)),
        margin=dict(l=50, r=50, t=80, b=30))
    return fig

def main():
    print("="*60)
    print("  Jay Chou — Popularity Prediction")
    print("="*60)
    print(f"  Features: {', '.join(FEATURES)}\n")

    df = load_data()
    X_train, X_test, y_train, y_test = prep(df)
    models = build_models()
    results_df, trained, fi, colors = evaluate(models, X_train, X_test, y_train, y_test)

    print(f"\n{'='*60}\n  SHAP Analysis\n{'='*60}")
    shap_r = compute_shap(trained, X_train, X_test)

    print(f"\n{'='*60}\n  Partial Dependence\n{'='*60}")
    pdp_r, top_fs = compute_pdp(trained, X_train, top_n=6)
    print(f"  Top features: {', '.join(top_fs)}")

    print(f"\n{'='*60}\n  Building visualizations...")
    fig_m = build_main(results_df, fi, shap_r, colors, y_test, trained, X_test)
    fig_p = build_pdp_page(pdp_r, top_fs, trained, colors)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w") as f:
        f.write(f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Jay Chou — Popularity Prediction</title>
<style>body{{font-family:-apple-system,sans-serif;margin:0;padding:20px;background:#f8f9fa}}
.s{{background:white;border-radius:8px;padding:10px 20px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}}</style></head><body>
<div class="s"><h2>📊 Model Comparison &amp; Feature Analysis</h2>{fig_m.to_html(include_plotlyjs="cdn", full_html=False)}</div>
<div class="s"><h2>📈 Partial Dependence Plots</h2>{fig_p.to_html(include_plotlyjs=False, full_html=False)}</div>
</body></html>""")

    print(f"\n  Saved: {OUTPUT_HTML}")
    print(f"  Size:  {os.path.getsize(OUTPUT_HTML)/1024:.0f} KB")
    print("="*60)

if __name__ == "__main__":
    main()
