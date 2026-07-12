#!/usr/bin/env python3
"""
周杰伦音乐深度分析 — Lyrics Analysis 模块
===========================================
涵盖：中文分词、停用词处理、TF-IDF、高频词、Topic Modeling、情绪分析、歌词复杂度分析
输出所有可视化到 outputs/ 目录
"""

import os, re, sys, warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# ── Chinese font setup ──
def _find_chinese_font():
    candidates = ['PingFang SC', 'Heiti SC', 'STHeiti', 'STKaiti', 'SimHei', 'Microsoft YaHei']
    for c in candidates:
        try:
            fp = fm.findfont(c, fallback_to_system=False)
            if fp and os.path.exists(fp):
                return c
        except:
            continue
    # fallback: scan system fonts
    for f in fm.findSystemFonts():
        try:
            p = fm.FontProperties(fname=f)
            n = p.get_name()
            if any(k in n.lower() for k in ['pingfang','heiti','stheit','stkait','simhei','noto']):
                return f
        except:
            continue
    return None

_CN_FONT = _find_chinese_font()
if _CN_FONT:
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = [_CN_FONT]
plt.rcParams['axes.unicode_minus'] = False

# ── Paths ──
BASE = os.path.dirname(os.path.abspath(__file__))
WORK = BASE
DATA = os.path.join(BASE, '..', 'work')
OUTPUTS = os.path.join(BASE, '..', 'outputs')
os.makedirs(OUTPUTS, exist_ok=True)

LYRICS_CSV = os.path.join(WORK, 'lyrics.csv')
MASTER_CSV = os.path.join(WORK, 'jay_chou_master_dataset.csv')
STOPWORDS_PATH = os.path.join(WORK, 'stopwords', 'cn_stopwords.txt')
JAY_DICT_PATH = os.path.join(WORK, 'jay_dict.txt')

print("=" * 60)
print("周杰伦音乐深度分析 — Lyrics Analysis 模块")
print("=" * 60)

# ============================================================
# 1. DATA LOADING & PREPROCESSING
# ============================================================
print("\n[1/8] 加载数据 ...")

# Load lyrics
lyrics_df = pd.read_csv(LYRICS_CSV)
# Load master dataset for metadata
master = pd.read_csv(MASTER_CSV)

# Merge to get release_date
merged = lyrics_df.merge(master[['song_name', 'release_date']], on='song_name', how='left')
merged['year'] = pd.to_datetime(merged['release_date'], errors='coerce').dt.year
merged['decade'] = (merged['year'] // 5 * 5).astype('Int64')

# Filter out instrumental songs that have no Chinese lyrics
def has_chinese(text):
    if pd.isna(text):
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', str(text)))

merged = merged[merged['lyrics'].apply(has_chinese)].copy()
print(f"  歌曲数量: {len(merged)}")
print(f"  年份范围: {int(merged['year'].min())} - {int(merged['year'].max())}")
print(f"  专辑数量: {merged['release_date'].nunique()}")

# ============================================================
# 2. CHINESE WORD SEGMENTATION (中文分词)
# ============================================================
print("\n[2/8] 中文分词 (Jieba) ...")
import jieba

# Load custom dictionary
if os.path.exists(JAY_DICT_PATH):
    jieba.load_userdict(JAY_DICT_PATH)
    print(f"  加载自定义词典: {JAY_DICT_PATH}")

# Load stopwords
stopwords = set()
if os.path.exists(STOPWORDS_PATH):
    with open(STOPWORDS_PATH, 'r', encoding='utf-8') as f:
        stopwords = set(line.strip() for line in f if line.strip())
    print(f"  停用词数量: {len(stopwords)}")

def tokenize(text):
    """Tokenize Chinese text with jieba, remove stopwords and short tokens."""
    if pd.isna(text):
        return []
    words = jieba.lcut(str(text))
    return [w.strip() for w in words
            if w.strip() and w.strip() not in stopwords
            and len(w.strip()) > 1]

merged['tokens'] = merged['lyrics'].apply(tokenize)
merged['token_count'] = merged['tokens'].apply(len)

# Statistics
print(f"  平均每首歌分词数: {merged['token_count'].mean():.1f}")
print(f"  中位数分词数: {merged['token_count'].median():.0f}")
print(f"  总词汇量: {sum(merged['token_count'])}")

# ============================================================
# 3. WORD FREQUENCY & WORD CLOUD (高频词)
# ============================================================
print("\n[3/8] 高频词分析 & 词云 ...")
from collections import Counter

# Global word frequency
all_tokens = [t for tokens in merged['tokens'] for t in tokens]
word_freq = Counter(all_tokens)
top_40 = word_freq.most_common(40)

print("  全局 Top 20 高频词:")
for word, count in top_40[:20]:
    print(f"    {word}: {count}")

# Bar chart: Top 30 words
fig, ax = plt.subplots(figsize=(12, 8))
words_top30 = [w for w, _ in word_freq.most_common(30)]
counts_top30 = [c for _, c in word_freq.most_common(30)]
colors = plt.cm.Blues(np.linspace(0.4, 0.9, 30))
bars = ax.barh(range(len(words_top30)), counts_top30, color=colors[::-1])
ax.set_yticks(range(len(words_top30)))
ax.set_yticklabels(words_top30)
ax.invert_yaxis()
ax.set_xlabel('词频')
ax.set_title('周杰伦歌词 Top 30 高频词', fontsize=14, fontweight='bold')
for bar, val in zip(bars, counts_top30):
    ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
            str(val), va='center', fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '01_top30_words.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 01_top30_words.png")

# Word Cloud
from wordcloud import WordCloud
wc_font_path = None
if _CN_FONT:
    try:
        wc_font_path = fm.findfont(_CN_FONT)
    except:
        pass

wc = WordCloud(
    font_path=wc_font_path,
    width=1200, height=800,
    background_color='white',
    max_words=100,
    collocations=False,
    colormap='viridis',
    random_state=42
)
wc.generate_from_frequencies(dict(word_freq.most_common(100)))
wc.to_file(os.path.join(OUTPUTS, '02_wordcloud.png'))
print(f"  ✓ 02_wordcloud.png")

# ============================================================
# 4. TF-IDF ANALYSIS
# ============================================================
print("\n[4/8] TF-IDF 分析 ...")
from sklearn.feature_extraction.text import TfidfVectorizer

# Build TF-IDF from tokenized lyrics
merged['lyrics_joined'] = merged['tokens'].apply(lambda x: ' '.join(x))

vectorizer = TfidfVectorizer(max_features=2000, sublinear_tf=True)
tfidf_matrix = vectorizer.fit_transform(merged['lyrics_joined'])
feature_names = vectorizer.get_feature_names_out()
print(f"  TF-IDF 矩阵形状: {tfidf_matrix.shape}")

# Top keywords per song
def top_keywords_per_song(matrix, features, n=10):
    results = []
    for i in range(matrix.shape[0]):
        row = matrix[i].toarray().flatten()
        top_indices = row.argsort()[-n:][::-1]
        results.append([features[idx] for idx in top_indices])
    return results

top_kw_per_song = top_keywords_per_song(tfidf_matrix, feature_names, n=10)
merged['top_keywords'] = top_kw_per_song

# Show some examples
print("  歌曲 Top 关键词示例:")
for i in range(min(5, len(merged))):
    print(f"    「{merged.iloc[i]['song_name']}»: {', '.join(merged.iloc[i]['top_keywords'][:6])}...")

# Global TF-IDF aggregate (sum across all songs)
tfidf_sums = np.array(tfidf_matrix.sum(axis=0)).flatten()
top_tfidf_indices = tfidf_sums.argsort()[-30:][::-1]
top_tfidf_words = [(feature_names[i], tfidf_sums[i]) for i in top_tfidf_indices]

fig, ax = plt.subplots(figsize=(12, 8))
words = [w for w, _ in top_tfidf_words]
weights = [s for _, s in top_tfidf_words]
colors = plt.cm.Reds(np.linspace(0.3, 0.9, 30))
bars = ax.barh(range(len(words)), weights, color=colors[::-1])
ax.set_yticks(range(len(words)))
ax.set_yticklabels(words)
ax.invert_yaxis()
ax.set_xlabel('TF-IDF 权重 (累计)')
ax.set_title('全局 TF-IDF Top 30 关键词', fontsize=14, fontweight='bold')
for bar, val in zip(bars, weights):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}', va='center', fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '03_tfidf_top30.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 03_tfidf_top30.png")

# ============================================================
# 5. TOPIC MODELING (LDA)
# ============================================================
print("\n[5/8] Topic Modeling (LDA) ...")
from sklearn.decomposition import LatentDirichletAllocation

n_topics = 6
lda = LatentDirichletAllocation(
    n_components=n_topics,
    max_iter=50,
    random_state=42,
    learning_method='online',
    learning_offset=50.
)
doc_topic_dist = lda.fit_transform(tfidf_matrix)
merged['dominant_topic'] = doc_topic_dist.argmax(axis=1)
merged['topic_weight'] = doc_topic_dist.max(axis=1)

print(f"  主题数量: {n_topics}")
print(f"  平均主题置信度: {merged['topic_weight'].mean():.3f}")

# Display top words per topic
def print_topics(model, features, n_words=15):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        top_idx = topic.argsort()[-n_words:][::-1]
        top_words = [features[i] for i in top_idx]
        topics.append(top_words)
        print(f"  Topic {topic_idx+1}: {', '.join(top_words[:10])}...")
    return topics

topic_words = print_topics(lda, feature_names, n_words=15)

# Heatmap: topic distribution
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()
for t_idx in range(n_topics):
    ax = axes[t_idx]
    top_idx = lda.components_[t_idx].argsort()[-12:][::-1]
    top_w = [feature_names[i] for i in top_idx]
    top_v = [lda.components_[t_idx][i] for i in top_idx]
    colors = plt.cm.Set2(np.linspace(0.2, 0.8, 12))
    bars = ax.barh(range(len(top_w)), top_v, color=colors[::-1])
    ax.set_yticks(range(len(top_w)))
    ax.set_yticklabels(top_w)
    ax.invert_yaxis()
    ax.set_title(f'Topic {t_idx+1}', fontsize=12)
    ax.tick_params(axis='x', labelsize=8)
plt.suptitle('LDA 主题模型 — 各主题 Top 12 词', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '04_lda_topics.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 04_lda_topics.png")

# Topic distribution over time
topic_by_year = merged.groupby('year')['dominant_topic'].value_counts(normalize=True).unstack(fill_value=0)
fig, ax = plt.subplots(figsize=(14, 6))
topic_colors = plt.cm.Set2(np.linspace(0, 1, n_topics))
topic_by_year.plot(kind='bar', stacked=True, ax=ax, color=topic_colors, width=0.85)
ax.set_xlabel('年份')
ax.set_ylabel('主题占比')
ax.set_title('周杰伦歌词主题随时间演变', fontsize=14, fontweight='bold')
ax.legend([f'Topic {i+1}: {topic_words[i][0]}...' for i in range(n_topics)],
          loc='upper left', bbox_to_anchor=(1, 1), fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '05_topic_over_time.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 05_topic_over_time.png")

# Topic distribution pie (overall)
topic_counts = merged['dominant_topic'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    topic_counts.values, labels=[f'Topic {i+1}' for i in topic_counts.index],
    autopct='%1.1f%%',
    colors=plt.cm.Set2(np.linspace(0, 1, n_topics)),
    startangle=90,
    textprops={'fontsize': 10}
)
# Add topic keywords in legend
legend_labels = [f'Topic {i+1}: {", ".join(topic_words[i][:5])}' for i in range(n_topics)]
ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
ax.set_title('歌词主题分布', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '06_topic_pie.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 06_topic_pie.png")

# ============================================================
# 6. SENTIMENT ANALYSIS (情绪分析)
# ============================================================
print("\n[6/8] 情绪分析 ...")
from snownlp import SnowNLP

def snownlp_sentiment(text):
    try:
        if pd.isna(text) or len(str(text).strip()) < 20:
            return np.nan
        s = SnowNLP(str(text))
        return s.sentiments
    except:
        return np.nan

merged['snownlp_sentiment'] = merged['lyrics'].apply(snownlp_sentiment)
print(f"  SnowNLP 有效样本: {merged['snownlp_sentiment'].notna().sum()}/{len(merged)}")
print(f"  平均情绪值: {merged['snownlp_sentiment'].mean():.3f} (0=负面, 1=正面)")
print(f"  最正面歌曲 Top 5:")
for _, row in merged.nlargest(5, 'snownlp_sentiment')[['song_name', 'snownlp_sentiment']].iterrows():
    print(f"    {row['song_name']}: {row['snownlp_sentiment']:.3f}")
print(f"  最负面歌曲 Top 5:")
for _, row in merged.nsmallest(5, 'snownlp_sentiment')[['song_name', 'snownlp_sentiment']].iterrows():
    print(f"    {row['song_name']}: {row['snownlp_sentiment']:.3f}")

# Sentiment histogram
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.hist(merged['snownlp_sentiment'].dropna(), bins=30, color='steelblue', edgecolor='white', alpha=0.8)
ax.axvline(merged['snownlp_sentiment'].mean(), color='red', linestyle='--', label=f'均值: {merged["snownlp_sentiment"].mean():.3f}')
ax.axvline(0.5, color='gray', linestyle=':', label='中性: 0.5')
ax.set_xlabel('SnowNLP 情绪值 (0=负面 → 1=正面)')
ax.set_ylabel('歌曲数量')
ax.set_title('歌词情绪分布')
ax.legend(fontsize=9)

ax = axes[1]
# Classify sentiment
def classify(val):
    if pd.isna(val):
        return '未知'
    if val > 0.6:
        return '积极'
    elif val < 0.4:
        return '消极'
    else:
        return '中性'
merged['sentiment_class'] = merged['snownlp_sentiment'].apply(classify)
class_counts = merged['sentiment_class'].value_counts()
colors = {'积极': '#2ecc71', '中性': '#f39c12', '消极': '#e74c3c'}
ax.pie(class_counts.values,
       labels=[f'{k}\n({v}首, {v/len(merged)*100:.1f}%)' for k, v in class_counts.items()],
       colors=[colors.get(k, '#95a5a6') for k in class_counts.index],
       autopct='', startangle=90,
       textprops={'fontsize': 10})
ax.set_title('情绪分类占比')

plt.suptitle('周杰伦歌词 SnowNLP 情绪分析', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '07_sentiment_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 07_sentiment_distribution.png")

# Sentiment trend over years
sent_by_year = merged.groupby('year')['snownlp_sentiment'].agg(['mean', 'std', 'count']).dropna()
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(sent_by_year.index, sent_by_year['mean'], 'o-', color='steelblue', markersize=5, linewidth=2)
ax.fill_between(sent_by_year.index,
                sent_by_year['mean'] - sent_by_year['std'],
                sent_by_year['mean'] + sent_by_year['std'],
                alpha=0.15, color='steelblue')
ax.axhline(0.5, color='gray', linestyle=':', alpha=0.6)
ax.set_xlabel('年份')
ax.set_ylabel('平均情绪值')
ax.set_title('歌词情绪值随时间变化趋势', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '08_sentiment_trend.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 08_sentiment_trend.png")

# Sentiment by album era
if 'album_cn' in merged.columns:
    sent_by_album = merged.groupby('album_cn')['snownlp_sentiment'].mean().sort_values()
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(sent_by_album)))
    bars = ax.barh(range(len(sent_by_album)), sent_by_album.values, color=colors)
    ax.set_yticks(range(len(sent_by_album)))
    ax.set_yticklabels(sent_by_album.index)
    ax.invert_yaxis()
    ax.axvline(0.5, color='gray', linestyle=':')
    ax.set_xlabel('平均情绪值')
    ax.set_title('各专辑歌词平均情绪值', fontsize=14, fontweight='bold')
    for bar, val in zip(bars, sent_by_album.values):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                f'{val:.3f}', va='center', fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUTS, '09_sentiment_by_album.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 09_sentiment_by_album.png")

# ============================================================
# 7. LYRICS COMPLEXITY ANALYSIS (歌词复杂度)
# ============================================================
print("\n[7/8] 歌词复杂度分析 ...")

def compute_complexity(text, tokens):
    """Compute various complexity metrics for a song's lyrics."""
    if pd.isna(text) or not text:
        return {}
    text = str(text)
    # Character count (Chinese chars only)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # Total characters
    total_chars = len(text)
    # Number of lines
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    n_lines = len(lines)
    # Average line length (Chinese chars)
    avg_line_len = chinese_chars / max(n_lines, 1)
    # Vocabulary size (unique tokens)
    unique_tokens = len(set(tokens))
    # Type-token ratio (lexical diversity)
    ttr = unique_tokens / max(len(tokens), 1)
    # Sentence count (rough: split by punctuation)
    sentences = re.split(r'[。！？，；：、\n]', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 1]
    avg_sentence_len = chinese_chars / max(len(sentences), 1)
    # Lexical density (ratio of content words to total words)
    # Using token count as a proxy for word count
    lexical_density = min(ttr * 2, 1.0)  # Normalized lexical diversity

    return {
        'char_count': chinese_chars,
        'total_chars': total_chars,
        'n_lines': n_lines,
        'avg_line_len': round(avg_line_len, 1),
        'n_tokens': len(tokens),
        'unique_tokens': unique_tokens,
        'type_token_ratio': round(ttr, 3),
        'avg_sentence_len': round(avg_sentence_len, 1),
        'lexical_density': round(lexical_density, 3),
    }

complexity_df = merged.join(
    merged.apply(lambda r: pd.Series(compute_complexity(r['lyrics'], r['tokens'])), axis=1)
)

print(f"  平均字符数: {complexity_df['char_count'].mean():.0f}")
print(f"  平均行数: {complexity_df['n_lines'].mean():.1f}")
print(f"  平均每行字数: {complexity_df['avg_line_len'].mean():.1f}")
print(f"  平均词汇量: {complexity_df['n_tokens'].mean():.0f}")
print(f"  平均 TTR: {complexity_df['type_token_ratio'].mean():.3f}")
print(f"  平均词汇密度: {complexity_df['lexical_density'].mean():.3f}")

# Most lexically diverse songs
print("  词汇多样性最高 Top 5:")
for _, row in complexity_df.nlargest(5, 'type_token_ratio')[['song_name', 'type_token_ratio', 'n_tokens']].iterrows():
    print(f"    {row['song_name']}: TTR={row['type_token_ratio']:.3f}, 词汇量={int(row['n_tokens'])}")

print("  歌词最长的 Top 5:")
for _, row in complexity_df.nlargest(5, 'char_count')[['song_name', 'char_count', 'n_lines']].iterrows():
    print(f"    {row['song_name']}: {int(row['char_count'])}字, {int(row['n_lines'])}行")

# Complexity visualizations
# Panel A: Complexity metrics distribution
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
metrics = [
    ('char_count', '歌词字数', 'steelblue', '字数'),
    ('n_lines', '歌词行数', 'forestgreen', '行数'),
    ('avg_line_len', '平均每行字数', 'coral', '字/行'),
    ('n_tokens', '分词数量', 'purple', '词数'),
    ('type_token_ratio', '词汇多样性 (TTR)', 'teal', 'TTR'),
    ('lexical_density', '词汇密度', 'darkorange', '密度'),
]
for ax, (col, title, color, xlabel) in zip(axes.flatten(), metrics):
    if col == 'lexical_density':
        # Normalize to 0-1 for easy comparison
        pass
    data = complexity_df[col].dropna()
    ax.hist(data, bins=25, color=color, edgecolor='white', alpha=0.8)
    ax.axvline(data.mean(), color='darkred', linestyle='--', label=f'均值: {data.mean():.2f}')
    ax.set_xlabel(xlabel)
    ax.set_ylabel('歌曲数')
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8)
plt.suptitle('歌词复杂度指标分布', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '10_complexity_distribution.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 10_complexity_distribution.png")

# Panel B: Complexity over time
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
time_metrics = [('char_count', '歌词字数', '字数'),
                ('type_token_ratio', '词汇多样性 (TTR)', 'TTR'),
                ('avg_line_len', '平均每行字数', '字/行')]
for ax, (col, title, ylabel) in zip(axes, time_metrics):
    yearly = complexity_df.groupby('year')[col].mean()
    ax.plot(yearly.index, yearly.values, 'o-', color='steelblue', markersize=5, linewidth=2)
    # Moving average smoothing
    if len(yearly) > 5:
        ma = yearly.rolling(window=3, center=True).mean()
        ax.plot(ma.index, ma.values, '-', color='coral', linewidth=1.5, alpha=0.7, label='3年移动平均')
    ax.set_xlabel('年份')
    ax.set_ylabel(ylabel)
    ax.set_title(f'{title} 随时间变化', fontsize=11)
    ax.legend(fontsize=8)
plt.suptitle('歌词复杂度随时间演变趋势', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '11_complexity_trend.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 11_complexity_trend.png")

# ============================================================
# 8. COMPREHENSIVE LYRICS ANALYSIS DASHBOARD
# ============================================================
print("\n[8/8] 综合分析报告 ...")

# Lyrics-valence correlation
has_valence = merged.merge(master[['song_name', 'valence']], on='song_name', how='left')
merged['valence'] = has_valence['valence']
corr = merged[['snownlp_sentiment', 'valence']].dropna().corr().iloc[0, 1]
print(f"  歌词情绪-音乐valence相关系数: {corr:.3f}")

fig, ax = plt.subplots(figsize=(8, 6))
scatter_df = merged[['snownlp_sentiment', 'valence']].dropna()
ax.scatter(scatter_df['valence'], scatter_df['snownlp_sentiment'],
           alpha=0.5, c='steelblue', s=30)
ax.plot([0, 1], [0, 1], 'r--', alpha=0.3, label='y=x (完全一致)')
ax.set_xlabel('Spotify Valence (音乐情感)')
ax.set_ylabel('SnowNLP 情绪值 (歌词情感)')
ax.set_title(f'歌词情绪 vs 音乐情感 (r={corr:.3f})', fontsize=12)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '12_sentiment_vs_valence.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 12_sentiment_vs_valence.png")

# Correlation heatmap of all lyrics-derived features
lyrics_features = ['char_count', 'n_lines', 'avg_line_len', 'n_tokens',
                   'unique_tokens', 'type_token_ratio', 'lexical_density',
                   'snownlp_sentiment']
feat_corr = complexity_df[lyrics_features].dropna().corr()
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(feat_corr, dtype=bool), k=1)
sns.heatmap(feat_corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, square=True, linewidths=0.5, ax=ax,
            vmin=-1, vmax=1)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
ax.set_title('歌词特征相关性矩阵', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUTS, '13_feature_correlation.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 13_feature_correlation.png")

# ============================================================
# SUMMARY REPORT
# ============================================================
print("\n" + "=" * 60)
print("分析完成！所有可视化已输出到 outputs/ 目录")
print("=" * 60)

# Generate summary statistics text
summary_lines = [
    "=" * 60,
    "周杰伦音乐深度分析 — Lyrics Analysis 模块",
    "=" * 60,
    "",
    f"分析歌曲数: {len(merged)}",
    f"年份范围: {int(merged['year'].min())} - {int(merged['year'].max())}",
    f"总词汇量: {sum(merged['token_count'])}",
    f"去重词汇: {len(word_freq)}",
    f"平均每首歌分词数: {merged['token_count'].mean():.1f}",
    "",
    "--- 高频词 Top 20 ---",
]
for w, c in word_freq.most_common(20):
    summary_lines.append(f"  {w}: {c}")

summary_lines.extend([
    "",
    "--- LDA 主题 ---",
])
for i, tw in enumerate(topic_words):
    summary_lines.append(f"  Topic {i+1}: {', '.join(tw[:8])}")

summary_lines.extend([
    "",
    "--- SnowNLP 情绪 ---",
    f"  平均情绪值: {merged['snownlp_sentiment'].mean():.3f} (0=负, 1=正)",
    f"  积极歌曲: {(merged['sentiment_class']=='积极').sum()} ({((merged['sentiment_class']=='积极').sum()/len(merged))*100:.1f}%)",
    f"  中性歌曲: {(merged['sentiment_class']=='中性').sum()} ({((merged['sentiment_class']=='中性').sum()/len(merged))*100:.1f}%)",
    f"  消极歌曲: {(merged['sentiment_class']=='消极').sum()} ({((merged['sentiment_class']=='消极').sum()/len(merged))*100:.1f}%)",
    "",
    "--- 歌词复杂度 ---",
    f"  平均字数: {complexity_df['char_count'].mean():.0f}",
    f"  平均行数: {complexity_df['n_lines'].mean():.1f}",
    f"  平均词汇量: {complexity_df['n_tokens'].mean():.0f}",
    f"  平均TTR: {complexity_df['type_token_ratio'].mean():.3f}",
    f"  歌词-音乐情绪相关系数: {corr:.3f}",
    "",
    "--- 输出文件 ---",
])
for f in sorted(os.listdir(OUTPUTS)):
    fpath = os.path.join(OUTPUTS, f)
    if os.path.isfile(fpath):
        size = os.path.getsize(fpath)
        summary_lines.append(f"  {f} ({size/1024:.1f} KB)")

summary_lines.append("")
summary_lines.append("=" * 60)

summary_text = '\n'.join(summary_lines)
with open(os.path.join(OUTPUTS, 'analysis_summary.txt'), 'w', encoding='utf-8') as f:
    f.write(summary_text)
print(summary_text)
