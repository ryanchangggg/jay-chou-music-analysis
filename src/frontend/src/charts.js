/* ═══════════════════════════════════════════════════════════════════════════
   charts.js — Plotly 图表渲染器
   ─── 统一暗色主题配置，所有图表通过 Plotly.newPlot 渲染
   ═══════════════════════════════════════════════════════════════════════════ */

/* ─── 暗色主题统一配置 ─── */
const THEME = {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { color: '#b0b0c8', family: '"Noto Sans SC","Inter",-apple-system,sans-serif', size: 11 },
  hoverlabel: { bgcolor: '#1a1a2e', bordercolor: 'rgba(255,255,255,0.08)', font: { color: '#e0e0f0', size: 12 } },
}

const COLORS = [
  '#4a9eff', '#6c5ce7', '#00cec9', '#ff6b6b',
  '#fcc419', '#51cf66', '#e64980', '#9775fa',
  '#38d9a9', '#74c0fc', '#ff922b', '#20c997',
]

const FEAT_CN = {
  zh_CN: {
    energy: '能量', danceability: '舞曲性', valence: '积极度',
    acousticness: '原声性', speechiness: '口语度', loudness: '响度',
    tempo: '速度', instrumentalness: '器乐性',
  },
  zh_TW: {
    energy: '能量', danceability: '舞曲性', valence: '積極度',
    acousticness: '原聲性', speechiness: '口語度', loudness: '響度',
    tempo: '速度', instrumentalness: '器樂性',
  },
}

function featLabel(lang, f) {
  return FEAT_CN[lang]?.[f] || f
}

/* ─── 工具：设置 Plotly 图表响应式 ─── */
function plot(el, data, layout, config = {}) {
  Plotly.newPlot(el, data, {
    ...layout,
    ...THEME,
    margin: { l: 48, r: 16, t: 16, b: 48, ...layout?.margin },
  }, {
    responsive: true,
    displayModeBar: false,
    ...config,
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   1. 流行度分布图（直方图）
   ────────────────────────────────────────────────────────────────────────── */
export function renderPopDist(el, songs, lang) {
  const pops = songs.map(s => s.popularity)
  // 按区间分段着色：低（<=50）、中（51-69）、高（70-84）、顶（>=85）
  const colorMap = [
    { min: 0, max: 45, color: 'rgba(74,158,255,0.35)' },
    { min: 46, max: 55, color: 'rgba(74,158,255,0.55)' },
    { min: 56, max: 65, color: 'rgba(74,158,255,0.72)' },
    { min: 66, max: 75, color: 'rgba(74,158,255,0.85)' },
    { min: 76, max: 85, color: 'rgba(108,92,231,0.85)' },
    { min: 86, max: 100, color: 'rgba(255,107,107,0.85)' },
  ]
  function getColor(v) {
    for (const c of colorMap) { if (v >= c.min && v <= c.max) return c.color }
    return 'rgba(74,158,255,0.5)'
  }

  // 计算统计数据
  const avg = (pops.reduce((a, b) => a + b, 0) / pops.length).toFixed(1)
  const max = Math.max(...pops)
  const min = Math.min(...pops)

  plot(el, [{
    x: pops,
    type: 'histogram',
    nbinsx: 14,
    marker: {
      color: pops.map(getColor),
      line: { color: '#0d0d1a', width: 1 },
    },
    hovertemplate: '流行度 %{x}<br>歌曲数: %{y}<extra></extra>',
  }], {
    xaxis: {
      title: { text: (lang === 'zh_TW' ? '流行度' : '流行度'), font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
      range: [35, 95],
    },
    yaxis: {
      title: { text: (lang === 'zh_TW' ? '歌曲數' : '歌曲数'), font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
    },
    bargap: 0.06,
    annotations: [{
      x: 0.5, y: -0.28,
      xref: 'paper', yref: 'paper',
      text: (lang === 'zh_TW'
        ? `平均 ${avg} · 最高 ${max} · 最低 ${min}　　顏色越深表示人氣越高`
        : `平均 ${avg} · 最高 ${max} · 最低 ${min}　　颜色越深表示人气越高`),
      showarrow: false,
      font: { size: 11, color: '#888' },
      xanchor: 'center',
    }],
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   2. 各专辑歌曲数（水平柱状图）
   ────────────────────────────────────────────────────────────────────────── */
export function renderAlbumSongs(el, songs) {
  const map = {}
  songs.forEach(s => { map[s.album] = (map[s.album] || 0) + 1 })
  const entries = Object.entries(map).sort((a, b) => b[1] - a[1])

  plot(el, [{
    x: entries.map(e => e[1]),
    y: entries.map(e => e[0]),
    type: 'bar',
    orientation: 'h',
    marker: {
      color: '#4a9eff',
      opacity: 0.85,
    },
    text: entries.map(e => e[1]),
    textposition: 'outside',
    textfont: { size: 10, color: '#4a9eff' },
    hovertemplate: '%{y}<br>歌曲数: %{x}<extra></extra>',
  }], {
    xaxis: { gridcolor: 'rgba(255,255,255,0.04)', zeroline: false, title: { text: '歌曲数', font: { size: 11 } } },
    yaxis: { autorange: 'reversed', tickfont: { size: 10 } },
    margin: { l: 150, r: 30, t: 8, b: 32 },
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   3. 音频特征演变趋势（折线图）
   ────────────────────────────────────────────────────────────────────────── */
export function renderEvoTrend(el, yearly, features, lang) {
  const displayFeats = ['energy', 'danceability', 'acousticness', 'valence', 'speechiness', 'loudness']
  const data = displayFeats.map((f, i) => ({
    x: yearly.years,
    y: yearly[f],
    mode: 'lines+markers',
    name: featLabel(lang, f),
    line: { width: 2.5, color: COLORS[i % COLORS.length] },
    marker: { size: 4, color: COLORS[i % COLORS.length] },
    hovertemplate: '%{x}<br>' + featLabel(lang, f) + ': %{y:.3f}<extra></extra>',
  }))

  plot(el, data, {
    xaxis: {
      dtick: 2,
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
    },
    yaxis: {
      title: { text: '均值', font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
      range: [0, 1],
    },
    legend: {
      orientation: 'h',
      y: 1.12,
      x: 0,
      font: { size: 10 },
    },
    margin: { l: 44, r: 16, t: 40, b: 44 },
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   4. 时代雷达图
   ────────────────────────────────────────────────────────────────────────── */
export function renderEraRadar(el, eras, features, lang) {
  const eraNames = Object.keys(eras)
  const eraLabelShort = {
    'Early (2000-2003)': lang === 'zh_TW' ? '早期' : '早期',
    'Golden (2004-2007)': lang === 'zh_TW' ? '黃金期' : '黄金期',
    'Experimental (2008-2012)': lang === 'zh_TW' ? '實驗期' : '实验期',
    'Recent (2013-2022)': lang === 'zh_TW' ? '近期' : '近期',
  }

  // 时代特征键名 → 中文标签
  const featLabelMap = {
    zh_CN: {
      danceability: '舞曲性', energy: '能量', valence: '积极度',
      acousticness: '原声性', speechiness: '口语度', loudness: '响度',
      tempo: '速度', instrumentalness: '器乐性', key: '调性',
      duration_ms: '时长', mode: '调式',
    },
    zh_TW: {
      danceability: '舞曲性', energy: '能量', valence: '積極度',
      acousticness: '原聲性', speechiness: '口語度', loudness: '響度',
      tempo: '速度', instrumentalness: '器樂性', key: '調性',
      duration_ms: '時長', mode: '調式',
    },
  }
  const fl = featLabelMap[lang] || featLabelMap.zh_CN
  const thetaLabels = features.map(f => fl[f] || f)

  const data = eraNames.map((en, i) => {
    const vals = Object.values(eras[en].features)
    return {
      type: 'scatterpolar',
      r: [...vals, vals[0]],
      theta: [...thetaLabels, thetaLabels[0]],
      fill: 'toself',
      name: eraLabelShort[en] || en,
      line: { color: COLORS[i % COLORS.length], width: 2 },
      opacity: 0.8,
      hovertemplate: '%{theta}: %{r:.3f}<extra>' + (eraLabelShort[en] || en) + '</extra>',
      connectgaps: true,
    }
  })

  plot(el, data, {
    polar: {
      bgcolor: 'transparent',
      radialaxis: {
        visible: true,
        range: [0, 1],
        gridcolor: 'rgba(255,255,255,0.06)',
        color: '#666',
        tickfont: { size: 9 },
        ticksuffix: ' ',
      },
      angularaxis: {
        gridcolor: 'rgba(255,255,255,0.06)',
        color: '#aaa',
        tickfont: { size: 10, color: '#aaa' },
      },
    },
    legend: {
      orientation: 'h',
      y: -0.08,
      x: 0.5,
      xanchor: 'center',
      font: { size: 10 },
    },
    margin: { l: 30, r: 30, t: 30, b: 40 },
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   5. 歌词高频词（水平柱状图）
   ────────────────────────────────────────────────────────────────────────── */
export function renderWordFreq(el, wordFreq) {
  const entries = Object.entries(wordFreq).slice(0, 20)
  plot(el, [{
    x: entries.map(e => e[1]),
    y: entries.map(e => e[0]),
    type: 'bar',
    orientation: 'h',
    marker: {
      color: entries.map((_, i) => `hsl(260, 60%, ${45 + i * 1.2}%)`),
    },
    text: entries.map(e => e[1]),
    textposition: 'outside',
    textfont: { size: 9, color: '#888' },
    hovertemplate: '%{y}: %{x} 次<extra></extra>',
  }], {
    xaxis: { gridcolor: 'rgba(255,255,255,0.04)', zeroline: false },
    yaxis: { autorange: 'reversed', tickfont: { size: 10 } },
    margin: { l: 70, r: 30, t: 8, b: 32 },
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   6. 歌名用字频率（柱状图）
   ────────────────────────────────────────────────────────────────────────── */
export function renderTitleFreq(el, titleFreq) {
  const entries = Object.entries(titleFreq).slice(0, 12)
  plot(el, [{
    x: entries.map(e => e[0]),
    y: entries.map(e => e[1]),
    type: 'bar',
    marker: {
      color: '#00cec9',
      line: { color: 'rgba(0,206,201,0.3)', width: 1 },
    },
    text: entries.map(e => e[1]),
    textposition: 'outside',
    textfont: { size: 10, color: '#888' },
    hovertemplate: '%{x}: %{y} 次<extra></extra>',
  }], {
    xaxis: { tickangle: 0, gridcolor: 'rgba(255,255,255,0.04)', zeroline: false },
    yaxis: { gridcolor: 'rgba(255,255,255,0.04)', zeroline: false },
    margin: { l: 32, r: 24, t: 8, b: 48 },
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   7. PCA+KMeans 散点图
   ────────────────────────────────────────────────────────────────────────── */
export function renderPca(el, songs, pca, clusters) {
  const labels = [...new Set(clusters.kmeans)].sort()
  const hover = songs.map((s, i) =>
    `<b>${s.name}</b><br>专辑: ${s.album}（${s.year}）<br>人气: ${s.popularity}`
  )
  const data = labels.map((k, li) => {
    const pts = { x: [], y: [], text: [] }
    songs.forEach((s, i) => {
      if (clusters.kmeans[i] === k) {
        pts.x.push(pca.coords[i][0])
        pts.y.push(pca.coords[i][1])
        pts.text.push(hover[i])
      }
    })
    return {
      x: pts.x, y: pts.y,
      mode: 'markers',
      name: `聚类 ${k}（${pts.x.length}）`,
      text: pts.text,
      hoverinfo: 'text',
      marker: {
        size: 7,
        color: COLORS[li % COLORS.length],
        opacity: 0.85,
        line: { color: 'rgba(255,255,255,0.08)', width: 0.5 },
      },
    }
  })

  plot(el, data, {
    xaxis: {
      title: { text: '主成分 1', font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
    },
    yaxis: {
      title: { text: '主成分 2', font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
    },
    legend: { font: { size: 10 } },
    margin: { l: 44, r: 16, t: 8, b: 44 },
    hovermode: 'closest',
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   8. UMAP+HDBSCAN 散点图
   ────────────────────────────────────────────────────────────────────────── */
export function renderUmap(el, songs, umap, clusters) {
  const labels = [...new Set(clusters.hdbscan)].sort((a, b) => a - b)
  const hover = songs.map((s, i) =>
    `<b>${s.name}</b><br>专辑: ${s.album}（${s.year}）<br>人气: ${s.popularity}`
  )
  const data = labels.map((k, li) => {
    const pts = { x: [], y: [], text: [] }
    songs.forEach((s, i) => {
      if (clusters.hdbscan[i] === k) {
        pts.x.push(umap.coords[i][0])
        pts.y.push(umap.coords[i][1])
        pts.text.push(hover[i])
      }
    })
    return {
      x: pts.x, y: pts.y,
      mode: 'markers',
      name: k === -1 ? `异常（${pts.x.length}）` : `聚类 ${k}（${pts.x.length}）`,
      text: pts.text,
      hoverinfo: 'text',
      marker: {
        size: k === -1 ? 6 : 7,
        color: k === -1 ? '#888' : COLORS[(li + 1) % COLORS.length],
        symbol: k === -1 ? 'x' : 'circle',
        opacity: k === -1 ? 0.7 : 0.85,
        line: { color: 'rgba(255,255,255,0.08)', width: 0.5 },
      },
    }
  })

  plot(el, data, {
    xaxis: {
      title: { text: 'UMAP 1', font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
    },
    yaxis: {
      title: { text: 'UMAP 2', font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
    },
    legend: { font: { size: 10 } },
    margin: { l: 44, r: 16, t: 8, b: 44 },
    hovermode: 'closest',
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   9. 全量歌曲人气对比（柱状图）
   ────────────────────────────────────────────────────────────────────────── */
export function renderPopCompare(el, songs) {
  const sorted = [...songs].sort((a, b) => a.popularity - b.popularity)
  const colors = sorted.map(s =>
    s.popularity >= 85 ? '#ff6b6b' :
    s.popularity <= 50 ? '#4a9eff' :
    'rgba(74,158,255,0.25)'
  )

  plot(el, [{
    x: sorted.map(s => s.name),
    y: sorted.map(s => s.popularity),
    type: 'bar',
    marker: { color: colors },
    hovertemplate: '<b>%{x}</b><br>人气: %{y}<extra></extra>',
  }], {
    xaxis: {
      tickangle: -60,
      showgrid: false,
      tickfont: { size: 7 },
      zeroline: false,
    },
    yaxis: {
      title: { text: '人气值', font: { size: 11 } },
      gridcolor: 'rgba(255,255,255,0.04)',
      zeroline: false,
    },
    showlegend: false,
    margin: { l: 44, r: 16, t: 8, b: 140 },
  })
}

/* ──────────────────────────────────────────────────────────────────────────
   10. 推荐系统特征对比雷达图
   ────────────────────────────────────────────────────────────────────────── */
export function renderRecRadar(el, songA, songB, features) {
  const valsA = [...features.map(f => songA.feats[f]), songA.feats[features[0]]]
  const valsB = [...features.map(f => songB.feats[f]), songB.feats[features[0]]]
  const theta = [...features, features[0]]

  plot(el, [
    {
      type: 'scatterpolar',
      r: valsA,
      theta,
      fill: 'toself',
      name: songA.name,
      line: { color: '#ffffff', width: 2.5 },
      opacity: 0.85,
    },
    {
      type: 'scatterpolar',
      r: valsB,
      theta,
      fill: 'toself',
      name: songB.name,
      line: { color: '#4a9eff', width: 2.5 },
      opacity: 0.85,
    },
  ], {
    polar: {
      bgcolor: 'transparent',
      radialaxis: {
        visible: true,
        range: [0, 1],
        gridcolor: 'rgba(255,255,255,0.06)',
        color: '#666',
        tickfont: { size: 9 },
      },
      angularaxis: {
        gridcolor: 'rgba(255,255,255,0.06)',
        color: '#888',
        tickfont: { size: 10 },
      },
    },
    legend: {
      orientation: 'h',
      y: -0.15,
      font: { size: 10 },
    },
    margin: { l: 50, r: 50, t: 8, b: 60 },
  })
}
