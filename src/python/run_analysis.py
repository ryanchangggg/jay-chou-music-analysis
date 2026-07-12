#!/usr/bin/env python3
"""
周杰伦音乐深度分析 — Lyrics Analysis 模块
===========================================
涵盖：中文分词、停用词处理、TF-IDF、高频词、Topic Modeling、情绪分析、歌词复杂度分析
输出所有可视化到 outputs/ 目录
"""

import os, re, sys, warnings, subprocess
warnings.filterwarnings('ignore')

# ── Matplotlib cache fix ──
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/mplcache')
os.makedirs('/private/tmp/mplcache', exist_ok=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd

# ── Chinese font setup ──
_ARIAL_UNICODE = '/Library/Fonts/Arial Unicode.ttf'
try:
    _CN_FP = fm.FontProperties(fname=_ARIAL_UNICODE)
    _CN_FONT_NAME = _CN_FP.get_name()
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = [_CN_FONT_NAME]
    plt.rcParams['axes.unicode_minus'] = False
    print(f"Font loaded: {_CN_FONT_NAME} from {_ARIAL_UNICODE}")
except Exception as e:
    print(f"Font load failed: {e}, falling back")
    _CN_FP = None

def cn_font():
    """Return FontProperties for Chinese text."""
    return fm.FontProperties(fname=_ARIAL_UNICODE) if _CN_FP else None

# ── Paths ──
WORK = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.join(WORK, '..', 'outputs')
os.makedirs(OUTPUTS, exist_ok=True)

LYRICS_CSV = os.path.join(WORK, 'lyrics.csv')
MASTER_CSV = os.path.join(WORK, 'jay_chou_master_dataset.csv')
STOPWORDS_PATH = os.path.join(WORK, 'stopwords', 'cn_stopwords.txt')
JAY_DICT_PATH = os.path.join(WORK, 'jay_dict.txt')

FP = cn_font()  # FontProperties for all Chinese text

# ============================================================
# 1. DATA LOADING
# ============================================================
print("=" * 60)
print("周杰伦音乐深度分析 — Lyrics Analysis 模块")
print("=" * 60)
print("\n[1/7] 加载数据 ...")

lyrics_df = pd.read_csv(LYRICS_CSV)
master = pd.read_csv(MASTER_CSV)

# Merge metadata
merged = lyrics_df.merge(
    master[['song_name', 'release_date', 'album_cn', 'valence']],
    on='song_name', how='left'
)
merged['year'] = pd.to_datetime(merged['release_date'], errors='coerce').dt.year.astype('Int64')
merged['era'] = (merged['year'].astype(float) // 5 * 5).astype('Int64')

# Filter to Chinese lyrics only
def has_chinese(text):
    return bool(pd.notna(text) and re.search(r'[\u4e00-\u9fff]', str(text)))

merged = merged[merged['lyrics'].apply(has_chinese)].copy().reset_index(drop=True)
print(f"  歌曲数量: {len(merged)}")
print(f"  年份范围: {int(merged['year'].min())} - {int(merged['year'].max())}")

# ============================================================
# 2. CHINESE WORD SEGMENTATION (中文分词 + 停用词处理)
# ============================================================
print("\n[2/7] 中文分词 & 停用词处理 ...")
import jieba

if os.path.exists(JAY_DICT_PATH):
    jieba.load_userdict(JAY_DICT_PATH)

# Load stopwords
stopwords = set()
if os.path.exists(STOPWORDS_PATH):
    with open(STOPWORDS_PATH, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip() for line in f if line.strip())

def tokenize(text):
    if pd.isna(text):
        return []
    text = str(text)
    # Basic cleanup
    text = re.sub(r'[a-zA-Z0-9]', '', text)
    text = re.sub(r'[^\u4e00-\u9fff，。！？、；：""''（）\n ]', '', text)
    words = jieba.lcut(text)
    filtered = []
    for w in words:
        w = w.strip()
        if not w:
            continue
        # Filter: keep only Chinese-origin content words
        if w in stopwords:
            continue
        if w == ' ' or w == '':
            continue
        # Must contain at least one Chinese character
        if not re.search(r'[\u4e00-\u9fff]', w):
            continue
        filtered.append(w)
    return filtered

merged['tokens'] = merged['lyrics'].apply(tokenize)
merged['token_count'] = merged['tokens'].apply(len)

# Stats
all_tokens = [t for ts in merged['tokens'] for t in ts]
print(f"  总词汇量: {len(all_tokens):,}")
print(f"  去重词汇数: {len(set(all_tokens)):,}")
print(f"  平均每首词数: {merged['token_count'].mean():.1f}")
print(f"  中位数词数: {int(merged['token_count'].median())}")

# ============================================================
# 3. HIGH-FREQUENCY WORDS + WORD CLOUD (高频词)
# ============================================================
print("\n[3/7] 高频词 & 词云 ...")
from collections import Counter

word_freq = Counter(all_tokens)
top_40 = word_freq.most_common(40)

print("  Top 20 高频词:")
for w, c in top_40[:20]:
    print(f"    {w}: {c}")

# ── Bar chart: Top 30 words ──
fig, ax = plt.subplots(figsize=(14, 9))
words_top30 = [w for w, _ in word_freq.most_common(30)]
counts_top30 = [c for _, c in word_freq.most_common(30)]
colors = plt.cm.Blues(np.linspace(0.35, 0.95, 30))
bars = ax.barh(range(len(words_top30)), counts_top30, color=colors[::-1], edgecolor='white')
ax.set_yticks(range(len(words_top30)))
ax.set_yticklabels(words_top30, fontproperties=FP, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('词频 (出现次数)', fontproperties=FP, fontsize=11)
ax.set_title('周杰伦歌词 Top 30 高频词', fontproperties=FP, fontsize=15, fontweight='bold')
for bar, val in zip(bars, counts_top30):
    ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
            str(val), va='center', fontsize=9, ha='left')
sns.despine()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '01_top30_words.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 01_top30_words.png")

# ── Word Cloud ──
from wordcloud import WordCloud
wc = WordCloud(
    font_path=_ARIAL_UNICODE,
    width=1400, height=900,
    background_color='white',
    max_words=120,
    collocations=False,
    colormap='viridis',
    random_state=42
)
wc.generate_from_frequencies(dict(word_freq.most_common(120)))
wc.to_file(os.path.join(OUTPUTS, '02_wordcloud.png'))
print(f"  ✓ 02_wordcloud.png")

# ============================================================
# 4. TF-IDF ANALYSIS
# ============================================================
print("\n[4/7] TF-IDF 分析 ...")
from sklearn.feature_extraction.text import TfidfVectorizer

merged['lyrics_joined'] = merged['tokens'].apply(lambda x: ' '.join(x))

vectorizer = TfidfVectorizer(max_features=2500, sublinear_tf=True,
                             max_df=0.85, min_df=2)
tfidf_matrix = vectorizer.fit_transform(merged['lyrics_joined'])
feature_names = vectorizer.get_feature_names_out()
print(f"  TF-IDF 矩阵: {tfidf_matrix.shape[0]} 首歌 × {tfidf_matrix.shape[1]} 特征")

# Top keywords per song
def top_keywords_per_song(matrix, features, n=10):
    results = []
    for i in range(min(matrix.shape[0], 5)):
        row = matrix[i].toarray().flatten()
        top_idx = row.argsort()[-n:][::-1]
        results.append([features[idx] for idx in top_idx])
    return results

print("  歌曲 Top 关键词示例:")
for i in range(min(5, len(merged))):
    row = merged.iloc[i]
    row_vec = tfidf_matrix[i].toarray().flatten()
    top_idx = row_vec.argsort()[-10:][::-1]
    kw = [feature_names[j] for j in top_idx]
    print(f"    「{row['song_name']}»: {', '.join(kw[:6])}...")

# ── Global TF-IDF Top 30 ──
tfidf_sums = np.array(tfidf_matrix.sum(axis=0)).flatten()
top_tfidf_idx = tfidf_sums.argsort()[-30:][::-1]
top_tfidf = [(feature_names[i], tfidf_sums[i]) for i in top_tfidf_idx]

fig, ax = plt.subplots(figsize=(14, 9))
words = [w for w, _ in top_tfidf]
weights = [s for _, s in top_tfidf]
colors = plt.cm.Reds(np.linspace(0.25, 0.95, 30))
bars = ax.barh(range(len(words)), weights, color=colors[::-1], edgecolor='white')
ax.set_yticks(range(len(words)))
ax.set_yticklabels(words, fontproperties=FP, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('TF-IDF 权重 (累计)', fontproperties=FP, fontsize=11)
ax.set_title('全局 TF-IDF Top 30 关键词', fontproperties=FP, fontsize=15, fontweight='bold')
for bar, val in zip(bars, weights):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}', va='center', fontsize=9)
sns.despine()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '03_tfidf_top30.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 03_tfidf_top30.png")

# ============================================================
# 5. TOPIC MODELING — LDA (主题建模)
# ============================================================
print("\n[5/7] Topic Modeling (LDA) ...")
from sklearn.decomposition import LatentDirichletAllocation

N_TOPICS = 6
lda = LatentDirichletAllocation(
    n_components=N_TOPICS, max_iter=100, random_state=42,
    learning_method='online', learning_offset=50.
)
doc_topic = lda.fit_transform(tfidf_matrix)
merged['dominant_topic'] = doc_topic.argmax(axis=1)
merged['topic_weight'] = doc_topic.max(axis=1)

print(f"  主题数: {N_TOPICS}, 平均置信度: {merged['topic_weight'].mean():.3f}")

# Topic words
topic_word_list = []
for t in range(N_TOPICS):
    top_idx = lda.components_[t].argsort()[-15:][::-1]
    tw = [feature_names[i] for i in top_idx]
    topic_word_list.append(tw)
    print(f"  Topic {t+1}: {', '.join(tw[:8])}...")

# ── Topic horizontal bar charts ──
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()
colors_set2 = plt.cm.Set2(np.linspace(0.1, 0.9, N_TOPICS))
for t in range(N_TOPICS):
    ax = axes[t]
    top_idx = lda.components_[t].argsort()[-12:][::-1]
    tw = [feature_names[i] for i in top_idx]
    tv = [lda.components_[t][i] for i in top_idx]
    bars = ax.barh(range(len(tw)), tv, color=colors_set2[t], edgecolor='white')
    ax.set_yticks(range(len(tw)))
    ax.set_yticklabels(tw, fontproperties=FP, fontsize=9)
    ax.invert_yaxis()
    ax.set_title(f'Topic {t+1}', fontproperties=FP, fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', labelsize=8)
plt.suptitle('LDA 主题模型 — 每个主题的 Top 12 关键词', fontproperties=FP,
             fontsize=15, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '04_lda_topics.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 04_lda_topics.png")

# ── Topic distribution over time ──
topic_by_year = merged.groupby('year')['dominant_topic'].value_counts(normalize=True).unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(16, 6))
topic_by_year.plot(kind='bar', stacked=True, ax=ax, color=colors_set2, width=0.85)
ax.set_xlabel('年份', fontproperties=FP, fontsize=11)
ax.set_ylabel('主题占比', fontproperties=FP, fontsize=10)
ax.set_title('周杰伦歌词主题随时间的演变', fontproperties=FP, fontsize=14, fontweight='bold')
ax.legend([f'T{t+1}: {topic_word_list[t][0]}...' for t in range(N_TOPICS)],
          loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '05_topic_over_time.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 05_topic_over_time.png")

# ── Topic pie chart ──
topic_counts = merged['dominant_topic'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax.pie(
    topic_counts.values,
    labels=[f'Topic {i+1}' for i in range(N_TOPICS)],
    autopct='%1.1f%%',
    colors=colors_set2,
    startangle=90,
    textprops={'fontproperties': FP}
)
legend_labels = [f'T{i+1}: {", ".join(topic_word_list[i][:4])}' for i in range(N_TOPICS)]
ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5),
          fontsize=9, prop=FP)
ax.set_title('歌词主题全局分布', fontproperties=FP, fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '06_topic_pie.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 06_topic_pie.png")

# ============================================================
# 6. SENTIMENT ANALYSIS (情绪分析)
# ============================================================
print("\n[6/7] 情绪分析 (SnowNLP) ...")
from snownlp import SnowNLP

def snownlp_sent(text):
    try:
        t = str(text).strip()
        if len(t) < 20:
            return np.nan
        return SnowNLP(t).sentiments
    except Exception:
        return np.nan

merged['snownlp'] = merged['lyrics'].apply(snownlp_sent)
valid = merged['snownlp'].notna()
print(f"  有效分析: {valid.sum()}/{len(merged)}")
print(f"  平均情绪值: {merged.loc[valid, 'snownlp'].mean():.3f} (0=消极, 1=积极)")

# Top/Bottom 5
print("  最积极 Top 5:")
for _, r in merged.nlargest(5, 'snownlp')[['song_name', 'snownlp']].iterrows():
    print(f"    {r['song_name']}: {r['snownlp']:.3f}")
print("  最消极 Top 5:")
for _, r in merged.nsmallest(5, 'snownlp')[['song_name', 'snownlp']].iterrows():
    print(f"    {r['song_name']}: {r['snownlp']:.3f}")

# ── Sentiment histogram + pie ──
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

ax = axes[0]
s_vals = merged['snownlp'].dropna()
ax.hist(s_vals, bins=30, color='steelblue', edgecolor='white', alpha=0.8)
ax.axvline(s_vals.mean(), color='red', linestyle='--',
           label=f'均值: {s_vals.mean():.3f}', linewidth=2)
ax.axvline(0.5, color='gray', linestyle=':', alpha=0.6, label='中性线: 0.5')
ax.set_xlabel('SnowNLP 情绪值 (0=消极 → 1=积极)', fontproperties=FP, fontsize=10)
ax.set_ylabel('歌曲数量', fontproperties=FP, fontsize=10)
ax.set_title('歌词情绪分布', fontproperties=FP, fontsize=13, fontweight='bold')
ax.legend(prop=FP, fontsize=9)

ax = axes[1]
def classify_sent(v):
    if pd.isna(v):
        return "未知"
    if v > 0.6:
        return "积极"
    elif v < 0.4:
        return "消极"
    return "中性"
merged['class'] = merged['snownlp'].apply(classify_sent)
cc = merged['class'].value_counts()
colors_pie = {'积极': '#2ecc71', '中性': '#f39c12', '消极': '#e74c3c'}
try:
    pie_out = ax.pie(cc.values, labels=[f'{k}\n({v}首)' for k,v in cc.items()], colors=[colors_pie.get(k,'#95a5a6') for k in cc.index], startangle=90)
    if len(pie_out) == 3:
        for t in pie_out[1]:
            t.set_color('black')
except Exception:
    ax.bar(range(len(cc)), cc.values, tick_label=list(cc.index), color=[colors_pie.get(k,'#95a5a6') for k in cc.index])
ax.set_title('情绪分类占比', fontproperties=FP, fontsize=13, fontweight='bold')

plt.suptitle('周杰伦歌词 SnowNLP 情绪分析', fontproperties=FP,
             fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '07_sentiment_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 07_sentiment_distribution.png")

# ── Sentiment trend over time ──
sent_yr = merged.groupby('year')['snownlp'].agg(['mean', 'std', 'count']).dropna()
fig, ax = plt.subplots(figsize=(16, 5))
ax.plot(sent_yr.index.astype(str), sent_yr['mean'], 'o-', color='steelblue',
        markersize=6, linewidth=2, markerfacecolor='white', markeredgecolor='steelblue')
ax.fill_between(range(len(sent_yr)),
                sent_yr['mean'] - sent_yr['std'],
                sent_yr['mean'] + sent_yr['std'],
                alpha=0.12, color='steelblue')
ax.axhline(0.5, color='gray', linestyle=':', alpha=0.6, linewidth=1)
ax.set_xlabel('年份', fontproperties=FP, fontsize=11)
ax.set_ylabel('平均情绪值', fontproperties=FP, fontsize=11)
ax.set_title('歌词情绪随时间变化趋势', fontproperties=FP, fontsize=14, fontweight='bold')
for i, (yr, row) in enumerate(sent_yr.iterrows()):
    ax.annotate(f'n={int(row["count"])}', (i, row['mean']),
                textcoords='offset points', xytext=(0, 8),
                fontsize=8, ha='center', color='gray')
plt.xticks(rotation=45)
sns.despine()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '08_sentiment_trend.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 08_sentiment_trend.png")

# ── Sentiment by album ──
if 'album_cn' in merged.columns:
    sent_alb = merged.groupby('album_cn')['snownlp'].mean().sort_values()
    fig, ax = plt.subplots(figsize=(14, 7))
    colors_alb = plt.cm.RdYlGn(np.linspace(0.2, 0.85, len(sent_alb)))
    bars = ax.barh(range(len(sent_alb)), sent_alb.values, color=colors_alb, edgecolor='white')
    ax.set_yticks(range(len(sent_alb)))
    ax.set_yticklabels(sent_alb.index, fontproperties=FP, fontsize=9)
    ax.invert_yaxis()
    ax.axvline(0.5, color='gray', linestyle=':', alpha=0.6)
    ax.axvline(sent_alb.mean(), color='darkred', linestyle='--', alpha=0.5,
               label=f'全局均值: {sent_alb.mean():.3f}')
    ax.set_xlabel('平均情绪值', fontproperties=FP, fontsize=11)
    ax.set_title('各专辑歌词平均情绪值', fontproperties=FP, fontsize=14, fontweight='bold')
    for bar, val in zip(bars, sent_alb.values):
        ax.text(val + 0.003, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=8)
    ax.legend(prop=FP, fontsize=9)
    sns.despine()
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS, '09_sentiment_by_album.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 09_sentiment_by_album.png")

# ============================================================
# 7. LYRICS COMPLEXITY (歌词复杂度分析)
# ============================================================
print("\n[7/7] 歌词复杂度分析 ...")

def lyrics_complexity(text, tokens):
    if pd.isna(text) or not text:
        return {}
    text = str(text)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    n_lines = max(len(lines), 1)
    avg_line_len = round(chinese_chars / n_lines, 1)
    n_tokens = len(tokens)
    unique_tokens = len(set(tokens))
    ttr = round(unique_tokens / max(n_tokens, 1), 3)
    # Sentences by punctuation
    sents = re.split(r'[。！？，；：、\n]', text)
    sents = [s.strip() for s in sents if len(s.strip()) > 1]
    avg_sent_len = round(chinese_chars / max(len(sents), 1), 1)
    return {
        'char_count': chinese_chars,
        'n_lines': n_lines,
        'avg_line_len': avg_line_len,
        'n_tokens': n_tokens,
        'unique_tokens': unique_tokens,
        'ttr': ttr,
        'avg_sent_len': avg_sent_len,
    }

comp = merged.join(
    merged.apply(lambda r: pd.Series(lyrics_complexity(r['lyrics'], r['tokens'])), axis=1)
)

print(f"  平均字数: {comp['char_count'].mean():.0f}")
print(f"  平均每行字数: {comp['avg_line_len'].mean():.1f}")
print(f"  平均词汇量: {comp['n_tokens'].mean():.0f}")
print(f"  平均 TTR: {comp['ttr'].mean():.3f}")

# Most complex songs
print("  TTR 最高 Top 5:")
for _, r in comp.nlargest(5, 'ttr')[['song_name', 'ttr', 'n_tokens']].iterrows():
    print(f"    {r['song_name']}: TTR={r['ttr']:.3f}, 词数={int(r['n_tokens'])}")
print("  歌词最长 Top 5:")
for _, r in comp.nlargest(5, 'char_count')[['song_name', 'char_count', 'n_lines']].iterrows():
    print(f"    {r['song_name']}: {int(r['char_count'])}字, {int(r['n_lines'])}行")

# ── Complexity distribution histograms ──
metrics = [
    ('char_count', '歌词总字数', 'steelblue', '字数'),
    ('n_lines', '歌词行数', 'forestgreen', '行数'),
    ('avg_line_len', '平均每行字数', 'coral', '字/行'),
    ('n_tokens', '分词数量', 'purple', '词数'),
    ('ttr', '词汇多样性 (TTR)', 'teal', 'TTR'),
    ('avg_sent_len', '平均句长', 'darkorange', '字/句'),
]
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
for ax, (col, title, color, xlbl) in zip(axes.flatten(), metrics):
    data = comp[col].dropna()
    ax.hist(data, bins=25, color=color, edgecolor='white', alpha=0.8)
    ax.axvline(data.mean(), color='darkred', linestyle='--',
               label=f'均值: {data.mean():.2f}', linewidth=1.5)
    ax.set_xlabel(xlbl, fontproperties=FP, fontsize=10)
    ax.set_ylabel('歌曲数', fontproperties=FP, fontsize=10)
    ax.set_title(title, fontproperties=FP, fontsize=12, fontweight='bold')
    ax.legend(prop=FP, fontsize=8)
plt.suptitle('歌词复杂度指标分布', fontproperties=FP, fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '10_complexity_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 10_complexity_distribution.png")

# ── Complexity trends over time ──
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, (col, title, ylbl) in zip(axes, [
    ('char_count', '歌词字数变化', '字数'),
    ('ttr', '词汇多样性变化', 'TTR'),
    ('avg_line_len', '平均每行字数变化', '字/行'),
]):
    yearly = comp.groupby('year')[col].mean()
    ax.plot(yearly.index.astype(str), yearly.values, 'o-', color='steelblue',
            markersize=5, linewidth=2)
    if len(yearly) > 5:
        ma = yearly.rolling(window=3, center=True).mean()
        ax.plot(ma.index.astype(str), ma.values, '-', color='coral',
                linewidth=1.5, alpha=0.7, label='3年移动平均')
    ax.set_xlabel('年份', fontproperties=FP, fontsize=10)
    ax.set_ylabel(ylbl, fontproperties=FP, fontsize=10)
    ax.set_title(title, fontproperties=FP, fontsize=12, fontweight='bold')
    ax.legend(prop=FP, fontsize=8)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
plt.suptitle('歌词复杂度随时间演变趋势', fontproperties=FP, fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '11_complexity_trend.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 11_complexity_trend.png")

# ============================================================
# BONUS: Sentiment-Valence comparison & Feature correlation
# ============================================================
# ── Sentiment vs Valence scatter ──
sv = merged[['snownlp', 'valence']].dropna()
corr = sv['snownlp'].corr(sv['valence'])
print(f"\n[Bonus] 歌词情绪-音乐Valence相关系数: {corr:.3f}")

fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(sv['valence'], sv['snownlp'], alpha=0.5, c='steelblue', s=35, edgecolor='white')
ax.plot([0, 1], [0, 1], 'r--', alpha=0.3, linewidth=1, label='y=x (完全一致)')
ax.set_xlabel('Spotify Valence (音频情感)', fontproperties=FP, fontsize=11)
ax.set_ylabel('SnowNLP 情绪值 (歌词情感)', fontproperties=FP, fontsize=11)
ax.set_title(f'歌词情绪 vs 音频情感 (r = {corr:.3f})', fontproperties=FP,
             fontsize=13, fontweight='bold')
ax.legend(prop=FP, fontsize=9)
sns.despine()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '12_sentiment_vs_valence.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 12_sentiment_vs_valence.png")

# ── Feature correlation heatmap ──
feat_cols = ['char_count', 'n_lines', 'avg_line_len', 'n_tokens',
             'unique_tokens', 'ttr', 'snownlp']
feat_corr = comp[feat_cols].dropna().corr()
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(feat_corr, dtype=bool), k=1)
sns.heatmap(feat_corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, square=True, linewidths=0.5, ax=ax,
            vmin=-1, vmax=1,
            xticklabels=feat_cols, yticklabels=feat_cols)
ax.set_title('歌词特征相关性矩阵', fontproperties=FP, fontsize=14, fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '13_feature_correlation.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 13_feature_correlation.png")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("分析完成！")
print("=" * 60)

summary = [
    "=" * 60,
    "周杰伦音乐深度分析 — Lyrics Analysis 模块",
    "=" * 60,
    "",
    f"分析歌曲数: {len(merged)}",
    f"年份范围: {int(merged['year'].min())} - {int(merged['year'].max())}",
    f"总词汇量: {len(all_tokens):,}",
    f"去重词汇: {len(word_freq):,}",
    f"平均每首分词数: {merged['token_count'].mean():.1f}",
    "",
    "--- 高频词 Top 20 ---",
]
for w, c in word_freq.most_common(20):
    summary.append(f"  {w}: {c}")

summary.append("")
summary.append("--- LDA 主题 ---")
for i, tw in enumerate(topic_word_list):
    summary.append(f"  Topic {i+1}: {', '.join(tw[:8])}")

summary.extend([
    "",
    "--- SnowNLP 情绪 ---",
    f"  平均情绪值: {merged['snownlp'].mean():.3f}",
    f"  积极歌曲: {(merged['class']=='积极 😊').sum()} ({(merged['class']=='积极 😊').sum()/len(merged)*100:.1f}%)",
    f"  中性歌曲: {(merged['class']=='中性 😐').sum()} ({(merged['class']=='中性 😐').sum()/len(merged)*100:.1f}%)",
    f"  消极歌曲: {(merged['class']=='消极 😢').sum()} ({(merged['class']=='消极 😢').sum()/len(merged)*100:.1f}%)",
    "",
    "--- 歌词复杂度 ---",
    f"  平均字数: {comp['char_count'].mean():.0f}",
    f"  平均行数: {comp['n_lines'].mean():.1f}",
    f"  平均词汇量: {comp['n_tokens'].mean():.0f}",
    f"  平均 TTR: {comp['ttr'].mean():.3f}",
    f"  歌词-音乐情绪相关系数: {corr:.3f}",
    "",
    "--- 输出文件 ---",
])
for f in sorted(os.listdir(OUTPUTS)):
    fpath = os.path.join(OUTPUTS, f)
    if os.path.isfile(fpath):
        summary.append(f"  {f} ({os.path.getsize(fpath)/1024:.1f} KB)")

summary.append("")
summary.append("=" * 60)
summary_text = '\n'.join(summary)
with open(os.path.join(OUTPUTS, 'analysis_summary.txt'), 'w', encoding='utf-8') as f:
    f.write(summary_text)
print(summary_text)
