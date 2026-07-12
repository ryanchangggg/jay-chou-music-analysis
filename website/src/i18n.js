const translations = {
  zh: {
    nav: { home:"首页", overview:"概览", evolution:"演变", lyrics:"歌词", cluster:"聚类", explorer:"探索", recommender:"推荐", about:"关于" },
    hero: { title:"周杰伦音乐分析", subtitle:"基于 Spotify 音频特征的深度数据探索", cta:"开始探索", scroll:"向下滚动" },
    overview: { title:"数据概览", desc:"跨越 22 年、{albums} 张专辑、{songs} 首歌曲的全面分析" },
    evolution: { title:"音乐风格演变", energy:"能量", danceability:"舞曲性", acousticness:"声学性", valence:"积极度",
      desc1:"周杰伦的音乐风格经历了显著的演变。从早期《Jay》的R&B风格，到黄金时期天马行空的创作，再到近年来的沉淀。",
      desc2:"数据显示，{feature} 是最能区分不同时期的特征。" },
    lyrics: { title:"歌词深度分析", desc1:"对 {words} 万字歌词进行了分词分析，发现 {unique} 个独特词汇。",
      desc2:"歌词中最高频的词汇是「{word}」，体现了周杰伦歌词的 {theme} 特征。" },
    cluster: { title:"歌曲聚类分析", desc1:"基于音频特征将歌曲分为两类：Cluster 0（{c0} 首）以 {c0a} 为代表，偏 {c0d}；Cluster 1（{c1} 首）以 {c1a} 为代表，偏 {c1d}。",
      desc2:"HDBSCAN 发现 {noise} 首「异常」歌曲——这些是最具实验性的作品。" },
    explorer: { title:"歌曲探索器", search:"搜索歌曲...", album:"全部专辑", year:"全部年份", pop:"人气" },
    recommender: { title:"智能推荐系统", desc:"基于音频特征的相似度推荐。选择一首歌，发现你最爱的旋律。",
      select:"选择歌曲", cosine:"余弦相似度", knn:"KNN 欧氏距离", pca:"PCA 嵌入", recommend:"推荐", top:"相似度 Top 10" },
    about: { title:"关于本项目", desc:"本项目对周杰伦 174 首歌曲进行了全面的数据分析，涵盖音频特征分析、歌词挖掘、聚类分析、流行度预测和智能推荐。" },
    footer: "基于 Spotify 数据 · 数据科学 + 可视化 · 2026",
    insights: {
      e1:"早期", e2:"黄金", e3:"实验", e4:"近期",
      cluster0:"高能量", cluster1:"抒情",
      pop:"平均人气", songs:"歌曲", albums:"专辑", years:"年跨度",
    }
  },
  en: {
    nav: { home:"Home", overview:"Overview", evolution:"Evolution", lyrics:"Lyrics", cluster:"Clusters", explorer:"Explore", recommender:"Recommend", about:"About" },
    hero: { title:"Jay Chou Music Analysis", subtitle:"Deep data exploration based on Spotify audio features", cta:"Start Exploring", scroll:"Scroll down" },
    overview: { title:"Data Overview", desc:"Comprehensive analysis spanning {years} years, {albums} albums, {songs} songs" },
    evolution: { title:"Musical Evolution", energy:"Energy", danceability:"Danceability", acousticness:"Acousticness", valence:"Valence",
      desc1:"Jay Chou's musical style evolved significantly, from early R&B roots through a golden age of creativity to his recent mature period.",
      desc2:"Data shows that {feature} is the most distinguishing feature across eras." },
    lyrics: { title:"Lyrics Deep Dive", desc1:"Analyzed {words}K characters of lyrics, discovering {unique} unique words.",
      desc2:"The most frequent word is \"{word}\", reflecting the {theme} nature of his lyrics." },
    cluster: { title:"Song Clustering", desc1:"Songs divide into two clusters: Cluster 0 ({c0} songs, led by {c0a}) leans energetic; Cluster 1 ({c1} songs, led by {c1a}) leans melodic.",
      desc2:"HDBSCAN identified {noise} \"outlier\" songs — his most experimental work." },
    explorer: { title:"Song Explorer", search:"Search songs...", album:"All Albums", year:"All Years", pop:"Popularity" },
    recommender: { title:"Smart Recommender", desc:"Content-based recommendation using audio features. Pick a song and discover your next favorite.",
      select:"Pick a song", cosine:"Cosine Similarity", knn:"KNN Euclidean", pca:"PCA Embedding", recommend:"Recommend", top:"Top 10 Similar" },
    about: { title:"About This Project", desc:"A comprehensive data analysis of 174 songs by Jay Chou, covering audio features, lyrics mining, clustering analysis, popularity prediction, and intelligent recommendations." },
    footer: "Powered by Spotify Data · Data Science + Visualization · 2026",
    insights: {
      e1:"Early", e2:"Golden", e3:"Experimental", e4:"Recent",
      cluster0:"Energetic", cluster1:"Ballad",
      pop:"Avg Popularity", songs:"Songs", albums:"Albums", years:"Years Span",
    }
  }
}

export let currentLang = 'zh'

export function setLang(lang) {
  currentLang = lang
  document.documentElement.lang = lang
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const keys = el.dataset.i18n.split('.')
    let t = translations[lang]
    for (const k of keys) t = t?.[k]
    if (t) el.textContent = t
  })
  document.dispatchEvent(new CustomEvent('langchange', { detail: lang }))
}

export function t(key, vars = {}) {
  const keys = key.split('.')
  let val = translations[currentLang]
  for (const k of keys) val = val?.[k]
  if (!val) return key
  return val.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? `{${k}}`)
}

export function tAll(key) {
  return { zh: t(key, {}), en: (()=>{let v=translations.en;for(const k of key.split('.'))v=v?.[k];return v??key})() }
}
