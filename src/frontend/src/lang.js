/* ═══════════════════════════════════════════════════════════════════════════
   lang.js — 简体中文 / 繁體中文 双语支持
   ═══════════════════════════════════════════════════════════════════════════ */

export const ZH_CN = {
  // ─── 导航 ───
  navBrand: '周杰伦音乐分析',
  langSwitch: '繁體',

  // ─── Hero ───
  heroTitle: '周杰伦音乐分析',
  heroSub: '基于 Spotify 音频特征的深度数据探索',
  heroCta: '开始探索',
  heroScroll: '向下滚动探索',

  // ─── 数据概览 ───
  overviewTitle: '数据概览',
  overviewDesc: (m) => `跨越 ${m.year_min}–${m.year_max} 年、${m.albums} 张专辑、${m.songs} 首歌曲的全面分析`,
  statSongs: '歌曲总数',
  statAlbums: '专辑数量',
  statYears: '时间跨度',
  statPop: '平均人气值',
  chartPopDist: '流行度分布',
  chartSongsPerAlbum: '各专辑歌曲数',

  // ─── 音乐风格演变 ───
  evoTitle: '音乐风格演变',
  evoDesc: '周杰伦的音乐风格经历了显著的演变。从早期 R&B 风格，到黄金时期天马行空的创作，再到近年来的沉淀与突破。以下图表展现了二十余年间音频特征的变迁轨迹。',
  evoFeatureTrends: '音频特征趋势',
  evoEraRadar: '时代特征雷达',
  evoEraStats: '时代数据',
  evoTableEra: '时代',
  evoTableSongs: '歌曲数',
  evoTablePop: '平均人气',
  featEnergy: '能量',
  featDanceability: '舞曲性',
  featValence: '积极度',
  featAcousticness: '原声性',
  featSpeechiness: '口语度',
  featLoudness: '响度',
  featTempo: '速度',
  featInstrumentalness: '器乐性',
  eraEarly: '早期 (2000–2003)',
  eraGolden: '黄金期 (2004–2007)',
  eraExperimental: '实验期 (2008–2012)',
  eraRecent: '近期 (2013–2026)',

  // ─── 聚类分析 ───
  clusterTitle: '歌曲聚类分析',
  clusterDesc1: (a) => `基于音频特征将歌曲分为两类：Cluster 0（${a.c0.size} 首）以「${a.c0.top_songs[0]}」为代表，偏快歌/高能量；Cluster 1（${a.c1.size} 首）以「${a.c1.top_songs[0]}」为代表，偏抒情/慢歌。`,
  clusterDesc2: (noise) => `HDBSCAN 算法发现了 ${noise} 首「异常」歌曲——这些是周杰伦最具实验性的作品。`,
  clusterPca: 'PCA + KMeans 聚类',
  clusterUmap: 'UMAP + HDBSCAN 聚类',

  // ─── 歌词分析 ───
  lyricsTitle: '歌词深度分析',
  lyricsDesc1: (i) => `对 ${i.words_total} 个歌词词汇进行了分词分析，共发现 ${i.words_unique} 个独特词汇。`,
  lyricsDesc2: (i) => `高频词包括「${i.top_words[0]}」「${i.top_words[1]}」「${i.top_words[2]}」等，体现了周杰伦歌词的浪漫与叙事特征。`,
  lyricsTopWords: '高频词 Top 20',
  lyricsTitleChars: '歌名用字统计',

  // ─── 热门度分析 ───
  popTitle: '热门度分析',
  popDesc: (i) => `人气最高的歌曲「${i.top_song}」以 ${i.top_pop} 分位居榜首。高人气歌曲通常节奏感更强、能量值更高。`,
  popCompare: '全部歌曲人气排行',
  popHighlight: '高人气 (≥85 分)',
  popLowlight: '低人气 (≤50 分)',

  // ─── 歌曲探索器 ───
  expTitle: '歌曲探索器',
  expSearch: '搜索歌曲名称…',
  expAlbumAll: '全部专辑',
  expResult: (n) => `共 ${n} 首歌曲`,
  expNoResult: '没有匹配的歌曲',
  expColIdx: '#',
  expColName: '歌曲',
  expColAlbum: '专辑',
  expColYear: '年份',
  expColPop: '人气',
  expClickHint: '点击行可跳转至推荐系统',
  // 探索器特征列名
  expFeat: {
    danceability: '舞曲性',
    energy: '能量',
    valence: '欢快度',
    acousticness: '原声性',
    speechiness: '口语度',
    loudness: '响度',
  },

  // ─── 推荐系统 ───
  recTitle: '智能推荐系统',
  recDesc: '基于音频特征的相似度计算，发现与你最爱歌曲风格相近的其他作品。',
  recSelect: '请选择一首歌曲…',
  recBtn: '开始推荐',
  recCos: '余弦相似度',
  recKnn: 'KNN 欧氏距离',
  recPca: 'PCA 嵌入',
  recTop10: '最相似歌曲 Top 10',
  recCompare: '特征对比',
  recSim: '相似度',
  recNoSelect: '请先选择一首歌曲',

  // ─── 关于 ───
  aboutTitle: '关于本项目',
  aboutDesc: '本项目对周杰伦全部 174 首歌曲进行全面的数据分析，涵盖音频特征分析、歌词挖掘、聚类分析、热门度与智能推荐。',
  aboutSources: '数据来源',
  aboutSourceList: [
    'Spotify API — 174 首歌曲的音频特征',
    '歌词文本 — 全部歌曲的完整歌词',
    '专辑元数据 — 16 张专辑 (2000–2026)',
  ],
  aboutMethods: '分析方法',
  aboutMethodList: [
    'PCA / UMAP 降维 · KMeans / HDBSCAN 聚类',
    '余弦相似度 / KNN / PCA 嵌入推荐',
    'jieba 中文分词 · 词频统计',
  ],
  aboutFooter: '基于 Spotify 开放数据 · 数据科学 + 可视化 · 2026',
}

/* ─── 繁體中文 ──────────────────────────────────────────────────────────── */
export const ZH_TW = {
  navBrand: '周杰倫音樂分析',
  langSwitch: '简体',

  heroTitle: '周杰倫音樂分析',
  heroSub: '基於 Spotify 音訊特徵的深度數據探索',
  heroCta: '開始探索',
  heroScroll: '向下滾動探索',

  overviewTitle: '資料概覽',
  overviewDesc: (m) => `跨越 ${m.year_min}–${m.year_max} 年、${m.albums} 張專輯、${m.songs} 首歌曲的全面分析`,
  statSongs: '歌曲總數',
  statAlbums: '專輯數量',
  statYears: '時間跨度',
  statPop: '平均人氣值',
  chartPopDist: '流行度分佈',
  chartSongsPerAlbum: '各專輯歌曲數',

  evoTitle: '音樂風格演變',
  evoDesc: '周杰倫的音樂風格經歷了顯著的演變。從早期 R&B 風格，到黄金時期天馬行空的創作，再到近年來的沉澱與突破。以下圖表展現了二十餘年間音訊特徵的變遷軌跡。',
  evoFeatureTrends: '音訊特徵趨勢',
  evoEraRadar: '時代特徵雷達',
  evoEraStats: '時代資料',
  evoTableEra: '時代',
  evoTableSongs: '歌曲數',
  evoTablePop: '平均人氣',
  featEnergy: '能量',
  featDanceability: '舞曲性',
  featValence: '積極度',
  featAcousticness: '原聲性',
  featSpeechiness: '口語度',
  featLoudness: '響度',
  featTempo: '速度',
  featInstrumentalness: '器樂性',
  eraEarly: '早期 (2000–2003)',
  eraGolden: '黄金期 (2004–2007)',
  eraExperimental: '實驗期 (2008–2012)',
  eraRecent: '近期 (2013–2026)',

  // ─── 聚类分析 ───
  clusterTitle: '歌曲聚類分析',
  clusterDesc1: (a) => `基於音訊特徵將歌曲分為兩類：Cluster 0（${a.c0.size} 首）以「${a.c0.top_songs[0]}」為代表，偏快歌/高能量；Cluster 1（${a.c1.size} 首）以「${a.c1.top_songs[0]}」為代表，偏抒情/慢歌。`,
  clusterDesc2: (noise) => `HDBSCAN 演算法發現了 ${noise} 首「異常」歌曲——這些是周杰倫最具實驗性的作品。`,
  clusterPca: 'PCA + KMeans 聚類',
  clusterUmap: 'UMAP + HDBSCAN 聚類',

  // ─── 歌词分析 ───
  lyricsTitle: '歌詞深度分析',
  lyricsDesc1: (i) => `對 ${i.words_total} 個歌詞詞彙進行了分詞分析，共發現 ${i.words_unique} 個獨特詞彙。`,
  lyricsDesc2: (i) => `高頻詞包括「${i.top_words[0]}」「${i.top_words[1]}」「${i.top_words[2]}」等，體現了周杰倫歌詞的浪漫與敘事特徵。`,
  lyricsTopWords: '高頻詞 Top 20',
  lyricsTitleChars: '歌名用字統計',

  // ─── 热门度分析 ───
  popTitle: '熱門度分析',
  popDesc: (i) => `人氣最高的歌曲「${i.top_song}」以 ${i.top_pop} 分位居榜首。高人氣歌曲通常節奏感更強、能量值更高。`,
  popCompare: '全部歌曲人氣排行',
  popHighlight: '高人氣 (≥85 分)',
  popLowlight: '低人氣 (≤50 分)',

  // ─── 歌曲探索器 ───
  expTitle: '歌曲探索器',
  expSearch: '搜尋歌曲名稱…',
  expAlbumAll: '全部專輯',
  expResult: (n) => `共 ${n} 首歌曲`,
  expNoResult: '沒有符合的歌曲',
  expColIdx: '#',
  expColName: '歌曲',
  expColAlbum: '專輯',
  expColYear: '年份',
  expColPop: '人氣',
  expClickHint: '點選行可跳轉至推薦系統',
  expFeat: {
    danceability: '舞曲性',
    energy: '能量',
    valence: '歡快度',
    acousticness: '原聲性',
    speechiness: '口語度',
    loudness: '響度',
  },

  // ─── 推荐系统 ───
  recTitle: '智能推薦系統',
  recDesc: '基於音訊特徵的相似度計算，發現與你最愛歌曲風格相近的其他作品。',
  recSelect: '請選擇一首歌曲…',
  recBtn: '開始推薦',
  recCos: '餘弦相似度',
  recKnn: 'KNN 歐氏距離',
  recPca: 'PCA 嵌入',
  recTop10: '最相似歌曲 Top 10',
  recCompare: '特徵對比',
  recSim: '相似度',
  recNoSelect: '請先選擇一首歌曲',

  // ─── 关于 ───
  aboutTitle: '關於本專案',
  aboutDesc: '本專案對周杰倫全部 174 首歌曲進行全面的數據分析，涵蓋音訊特徵分析、歌詞挖掘、聚類分析、熱門度與智能推薦。',
  aboutSources: '資料來源',
  aboutSourceList: [
    'Spotify API — 174 首歌曲的音訊特徵',
    '歌詞文本 — 全部歌曲的完整歌詞',
    '專輯元資料 — 16 張專輯 (2000–2026)',
  ],
  aboutMethods: '分析方法',
  aboutMethodList: [
    'PCA / UMAP 降維 · KMeans / HDBSCAN 聚類',
    '餘弦相似度 / KNN / PCA 嵌入推薦',
    'jieba 中文分詞 · 詞頻統計',
  ],
  aboutFooter: '基於 Spotify 開放資料 · 資料科學 + 視覺化 · 2026',
}
