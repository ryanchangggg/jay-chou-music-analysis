import DATA from './data.json'

const D = DATA
const { songs, features:FEATS, pca, umap, clusters:CL, yearly, albums, eras, recommender, word_freq, title_freq, insights, meta } = D

const COLORS = ['#5b9cf5','#845ef7','#20c997','#ff6b6b','#fcc419','#51cf66','#e64980','#9775fa','#38d9a9','#74c0fc']
const EVO_FEATS = ['energy','danceability','acousticness','valence','speechiness','loudness']

// ═══ 状态管理 ═══════════════════════════════════════════════════════════
let recMethod = 'cosine'
let recIdx = -1
let expFiltered = []
let expSort = { col:0, dir:1 }

// ═══ DOM 辅助 ═══════════════════════════════════════════════════════════
const $ = s => document.querySelector(s)
const $$ = s => document.querySelectorAll(s)

// ═══ 中文文案 ════════════════════════════════════════════════════════════
const T = {
  nav: '周杰伦音乐分析',
  heroSub: '基于 Spotify 音频特征的深度数据探索',
  heroTitle: '周杰伦音乐分析',
  heroCta: '开始探索',
  heroScroll: '向下滚动',
  overviewTitle: '数据概览',
  overviewDesc: `跨越 ${meta.year_min}-${meta.year_max} 年、${meta.albums} 张专辑、${meta.songs} 首歌曲的全面分析`,
  songs: '歌曲',
  albums: '专辑',
  years: '年跨度',
  pop: '平均人气',
  popDist: '流行度分布',
  songsPerAlbum: '每张专辑歌曲数',
  evoTitle: '音乐风格演变',
  evoDesc: `周杰伦的音乐风格经历了显著的演变。从早期《Jay》的 R&B 风格，到黄金时期天马行空的创作，再到近年来的沉淀。${EVO_FEATS[0]} 是最能区分不同时期的特征。`,
  featureTrends: '音频特征趋势 (2000-2022)',
  eraRadar: '时代雷达图',
  eraStats: '时代统计',
  era: '时代',
  songCount: '歌曲数',
  avgPop: '平均流行度',
  lyricsTitle: '歌词深度分析',
  lyricsDesc1: `对 ${Math.round(insights.words_total/1000)} 万字歌词进行了分词分析，发现 ${insights.words_unique} 个独特词汇。`,
  lyricsDesc2: `歌词中最高频的词汇是「${insights.top_words?.[0] || '的'}」，体现了周杰伦歌词的浪漫与叙事特征。`,
  topWords: '高频词 Top 20',
  titleChars: '歌名字频统计',
  clusterTitle: '歌曲聚类分析',
  clusterDesc1: `基于音频特征将歌曲分为两类：Cluster 0（${CL.analysis.c0.size} 首）以「${CL.analysis.c0.top_songs[0]}」为代表，偏快歌/高能量；Cluster 1（${CL.analysis.c1.size} 首）以「${CL.analysis.c1.top_songs[0]}」为代表，偏抒情/慢歌。`,
  clusterDesc2: `HDBSCAN 发现 ${insights.noise} 首「异常」歌曲——这些是最具实验性的作品。`,
  pcaKmeans: 'PCA + KMeans 聚类',
  umapHdbscan: 'UMAP + HDBSCAN 聚类',
  explorerTitle: '歌曲探索器',
  explorerSearch: '搜索歌曲...',
  explorerAlbum: '全部专辑',
  recommenderTitle: '智能推荐系统',
  recommenderDesc: '基于音频特征的相似度推荐。选择一首歌，发现你最爱的旋律。',
  recSelect: '选择歌曲...',
  recBtn: '开始推荐',
  recCosine: '余弦相似度',
  recKnn: 'KNN 欧氏距离',
  recPca: 'PCA 嵌入',
  recTop: '相似度 Top 10',
  featureCompare: '特征对比',
  aboutTitle: '关于本项目',
  aboutDesc: '本项目对周杰伦 174 首歌曲进行了全面的数据分析，涵盖音频特征分析、歌词挖掘、聚类分析、流行度预测和智能推荐。',
  dataSources: '数据来源',
  dataSrcList: '• Spotify API — 174 首歌曲的音频特征<br>• 歌词文本 — 全部歌曲的完整歌词<br>• 专辑元数据 — 16 张专辑 (2000-2022)',
  methods: '分析方法',
  methodList: '• PCA / UMAP 降维<br>• KMeans / HDBSCAN 聚类<br>• 余弦相似度 / KNN 推荐<br>• RandomForest / XGBoost / LightGBM / CatBoost 预测<br>• SHAP 模型解释',
  footer: '基于 Spotify 数据 · 数据科学 + 可视化 · 2026',
}

// ═══ 构建应用 ════════════════════════════════════════════════════════════
function buildApp() {
  document.getElementById('app').innerHTML = `
    <nav id="nav">
      <div class="brand">🎵 ${T.nav}</div>
    </nav>
    <main>
      ${heroSection()}${overviewSection()}${evolutionSection()}${lyricsSection()}
      ${clusterSection()}${explorerSection()}${recommenderSection()}${aboutSection()}
    </main>
    <footer style="text-align:center;padding:40px 20px;color:var(--text3);font-size:.85em">
      ${T.footer}
    </footer>`
  initScrollAnim()
  renderHomeCharts()
  renderEvoChart()
  renderLyricChart()
  renderClusterCharts()
  renderExplorer()
  renderRecommender()
}

// ═══ 英雄页 ═══════════════════════════════════════════════════════════════
function heroSection() {
  return `<section id="hero" class="section-anim">
    <div class="inner">
      <h1>${T.heroTitle}</h1>
      <p>${T.heroSub}</p>
      <button class="cta" onclick="document.getElementById('overview').scrollIntoView({behavior:'smooth'})">
        ${T.heroCta} →
      </button>
    </div>
    <div class="scroll-hint">${T.heroScroll}<br>↓</div>
  </section>`
}

// ═══ 概览页 ═══════════════════════════════════════════════════════════════
function overviewSection() {
  return `<section id="overview" class="section-anim">
    <div class="inner stagger">
      <div class="narrative">
        <h2>${T.overviewTitle}</h2>
        <p>${T.overviewDesc}</p>
      </div>
      <div class="stats-strip stagger">
        <div class="stat-card"><div class="val">${meta.songs}</div><div class="lbl">${T.songs}</div></div>
        <div class="stat-card"><div class="val">${meta.albums}</div><div class="lbl">${T.albums}</div></div>
        <div class="stat-card"><div class="val">${meta.year_min}-${meta.year_max}</div><div class="lbl">${T.years}</div></div>
        <div class="stat-card"><div class="val">${meta.avg_pop}</div><div class="lbl">${T.pop}</div></div>
      </div>
      <div class="grid-2">
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.popDist}</h3><div id="pop-chart" class="chart-sm"></div></div>
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.songsPerAlbum}</h3><div id="album-chart" class="chart-sm"></div></div>
      </div>
    </div>
  </section>`
}

function renderHomeCharts() {
  const pops = songs.map(s => s.popularity)
  Plotly.newPlot('pop-chart', [{ x:pops, type:'histogram', marker:{color:'#4a9eff',line:{color:'#0a0a14',width:1}}, nbinsx:12 }],
    { margin:{l:40,r:10,t:10,b:30},paper_bgcolor:'transparent',plot_bgcolor:'transparent',font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},
      xaxis:{title:'流行度',gridcolor:'rgba(255,255,255,.04)'},yaxis:{gridcolor:'rgba(255,255,255,.04)'},bargap:0.1 },
    { responsive:true,displayModeBar:false })

  const al = Object.entries(songs.reduce((a,s)=>(a[s.album]=(a[s.album]||0)+1,a),{})).sort((a,b)=>b[1]-a[1])
  Plotly.newPlot('album-chart', [{ x:al.map(a=>a[1]), y:al.map(a=>a[0]), type:'bar', orientation:'h',
    marker:{color:COLORS.map((_,i)=>COLORS[i%COLORS.length])}, text:al.map(a=>a[1]), textposition:'outside', textfont:{size:9} }],
    { margin:{l:120,r:30,t:10,b:30},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
      font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},xaxis:{gridcolor:'rgba(255,255,255,.04)'},yaxis:{autorange:'reversed'} },
    { responsive:true,displayModeBar:false })
}

// ═══ 演变页 ═══════════════════════════════════════════════════════════════
function evolutionSection() {
  return `<section id="evolution" class="section-anim">
    <div class="inner">
      <div class="narrative">
        <h2>${T.evoTitle}</h2>
        <p>${T.evoDesc}</p>
      </div>
      <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.featureTrends}</h3>
        <div id="evo-chart" class="chart"></div></div>
      <div class="grid-2" style="margin-top:16px">
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.eraRadar}</h3>
          <div id="era-chart" class="chart"></div></div>
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.eraStats}</h3>
          <div id="era-stats"></div></div>
      </div>
    </div>
  </section>`
}

function renderEvoChart() {
  Plotly.newPlot('evo-chart', EVO_FEATS.map(f => ({
    x:yearly.years, y:yearly[f], mode:'lines+markers',
    name: {energy:'能量',danceability:'舞曲性',acousticness:'声学性',valence:'积极度',speechiness:'口语性',loudness:'响度'}[f] || f,
    line:{width:2}, marker:{size:5}
  })), { margin:{l:50,r:10,t:10,b:40},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
    font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},xaxis:{dtick:2,gridcolor:'rgba(255,255,255,.04)'},yaxis:{gridcolor:'rgba(255,255,255,.04)',title:'均值'},
    legend:{font:{size:10},orientation:'h',y:1.05} }, { responsive:true,displayModeBar:false })

  const eraNames = Object.keys(eras)
  const eraRadar = eraNames.map((en,i) => ({
    type:'scatterpolar',
    r: Object.values(eras[en].features).concat(Object.values(eras[en].features)[0]),
    theta: [...FEATS, FEATS[0]], fill:'toself', name:`${en}`,
    line:{color:COLORS[i]}, marker:{color:COLORS[i]}
  }))
  Plotly.newPlot('era-chart', eraRadar, {
    polar:{bgcolor:'transparent',radialaxis:{visible:true,range:[0,1],gridcolor:'rgba(255,255,255,.04)',color:'#666'},
           angularaxis:{gridcolor:'rgba(255,255,255,.04)',color:'#888',tickfont:{size:9}}},
    paper_bgcolor:'transparent',margin:{l:60,r:60,t:10,b:30},font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},
    legend:{font:{size:8}} }, { responsive:true,displayModeBar:false })

  document.getElementById('era-stats').innerHTML = `<table class="song-table">
    <tr><th>${T.era}</th><th>${T.songCount}</th><th>${T.avgPop}</th></tr>
    ${eraNames.map(en => `<tr><td>${en}</td><td>${eras[en].count}</td><td>${eras[en].popularity}</td></tr>`).join('')}</table>`
}

// ═══ 歌词页 ═══════════════════════════════════════════════════════════════
function lyricsSection() {
  return `<section id="lyrics" class="section-anim">
    <div class="inner">
      <div class="narrative">
        <h2>${T.lyricsTitle}</h2>
        <p>${T.lyricsDesc1}</p>
        <p>${T.lyricsDesc2}</p>
      </div>
      <div class="grid-2">
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.topWords}</h3>
          <div id="wf-chart" class="chart"></div></div>
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.titleChars}</h3>
          <div id="tf-chart" class="chart"></div></div>
      </div>
    </div>
  </section>`
}

function renderLyricChart() {
  const wf = Object.entries(word_freq).slice(0,20)
  Plotly.newPlot('wf-chart', [{ x:wf.map(a=>a[1]), y:wf.map(a=>a[0]), type:'bar', orientation:'h',
    marker:{color:'#6c5ce7'}, text:wf.map(a=>a[1]), textposition:'outside', textfont:{size:9} }],
    { margin:{l:90,r:30,t:10,b:30},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
      font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},xaxis:{gridcolor:'rgba(255,255,255,.04)'},yaxis:{autorange:'reversed'} },
    { responsive:true,displayModeBar:false })

  const tf = Object.entries(title_freq).slice(0,10)
  Plotly.newPlot('tf-chart', [{ x:tf.map(a=>a[0]), y:tf.map(a=>a[1]), type:'bar',
    marker:{color:'#00cec9'}, text:tf.map(a=>a[1]), textposition:'outside', textfont:{size:9} }],
    { margin:{l:40,r:20,t:10,b:50},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
      font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},xaxis:{tickangle:-30},yaxis:{gridcolor:'rgba(255,255,255,.04)'} },
    { responsive:true,displayModeBar:false })
}

// ═══ 聚类页 ═══════════════════════════════════════════════════════════════
function clusterSection() {
  const ca = CL.analysis
  return `<section id="cluster" class="section-anim">
    <div class="inner">
      <div class="narrative">
        <h2>${T.clusterTitle}</h2>
        <p>${T.clusterDesc1}</p>
        <p>${T.clusterDesc2}</p>
      </div>
      <div class="grid-2">
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.pcaKmeans}</h3>
          <div id="pca-chart" class="chart"></div></div>
        <div class="card glass" style="padding:16px"><h3 style="font-size:1em;margin-bottom:12px;color:var(--text2)">${T.umapHdbscan}</h3>
          <div id="umap-chart" class="chart"></div></div>
      </div>
    </div>
  </section>`
}

function renderClusterCharts() {
  const h = songs.map((s,i) => `${s.name}<br>专辑: ${s.album} (${s.year})<br>流行度: ${s.popularity}`)
  const ks = [...new Set(CL.kmeans)].sort()
  const pt = ks.map(k => ({ x:[],y:[],mode:'markers',name:`聚类 ${k}`,text:[],hoverinfo:'text',
    marker:{size:6,color:COLORS[k%COLORS.length]} }))
  songs.forEach((s,i) => { const ci=ks.indexOf(CL.kmeans[i]); if(ci>=0){pt[ci].x.push(pca.coords[i][0]);pt[ci].y.push(pca.coords[i][1]);pt[ci].text.push(h[i])} })
  Plotly.newPlot('pca-chart', pt, { margin:{l:40,r:10,t:10,b:40},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
    font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},xaxis:{gridcolor:'rgba(255,255,255,.04)',title:'主成分 1'},yaxis:{gridcolor:'rgba(255,255,255,.04)',title:'主成分 2'},
    legend:{font:{size:9}} }, { responsive:true,displayModeBar:false })

  const hs = [...new Set(CL.hdbscan)].sort((a,b)=>a-b)
  const ut = hs.map(k => ({ x:[],y:[],mode:'markers',name:k===-1?'噪声':`聚类 ${k}`,text:[],hoverinfo:'text',
    marker:{size:6,color:k===-1?'#666':COLORS[(k+1)%COLORS.length],symbol:k===-1?'x':'circle'} }))
  songs.forEach((s,i) => { const ci=hs.indexOf(CL.hdbscan[i]); if(ci>=0){ut[ci].x.push(umap.coords[i][0]);ut[ci].y.push(umap.coords[i][1]);ut[ci].text.push(h[i])} })
  Plotly.newPlot('umap-chart', ut, { margin:{l:40,r:10,t:10,b:40},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
    font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},xaxis:{gridcolor:'rgba(255,255,255,.04)',title:'UMAP 1'},yaxis:{gridcolor:'rgba(255,255,255,.04)',title:'UMAP 2'},
    legend:{font:{size:9}} }, { responsive:true,displayModeBar:false })
}

// ═══ 探索器 ═══════════════════════════════════════════════════════════════
function explorerSection() {
  const allAlbums = [...new Set(songs.map(s=>s.album))].sort()
  return `<section id="explorer" class="section-anim">
    <div class="inner">
      <div class="narrative"><h2>${T.explorerTitle}</h2></div>
      <div class="exp-controls">
        <input id="exp-search" placeholder="${T.explorerSearch}" oninput="window.filterExp()">
        <select id="exp-album" onchange="window.filterExp()">
          <option value="">${T.explorerAlbum}</option>
          ${allAlbums.map(a=>`<option value="${a}">${a}</option>`).join('')}
        </select>
      </div>
      <div class="table-wrap"><table class="song-table" id="exp-table">
        <thead><tr>
          <th onclick="window.sortExp(0)">#</th>
          <th onclick="window.sortExp(1)">歌曲</th>
          <th onclick="window.sortExp(2)">专辑</th>
          <th onclick="window.sortExp(3)">年份</th>
          <th onclick="window.sortExp(4)">人气</th>
          ${FEATS.map((f,i)=>`<th onclick="window.sortExp(${i+5})">${f}</th>`).join('')}
        </tr></thead>
        <tbody id="exp-body"></tbody>
      </table></div>
    </div>
  </section>`
}

function renderExplorer() {
  expFiltered = [...songs]
  renderExpTable(expFiltered)
}

function filterExp() {
  const q = ($('#exp-search')?.value||'').toLowerCase()
  const a = ($('#exp-album')?.value||'')
  expFiltered = songs.filter(s => {
    if(q && !s.name.toLowerCase().includes(q) && !s.album.toLowerCase().includes(q)) return false
    if(a && s.album!==a) return false
    return true
  })
  renderExpTable(expFiltered)
}

function sortExp(col) {
  if(expSort.col===col) expSort.dir*=-1; else {expSort.col=col;expSort.dir=1}
  expFiltered.sort((a,b) => {
    const va = col<=1 ? songs.indexOf(a) : col===1 ? a.name : col===2 ? a.album : col===3 ? a.year : col===4 ? a.popularity : a.feats[FEATS[col-5]]
    const vb = col<=1 ? songs.indexOf(b) : col===1 ? b.name : col===2 ? b.album : col===3 ? b.year : col===4 ? b.popularity : b.feats[FEATS[col-5]]
    return typeof va==='string' ? expSort.dir*va.localeCompare(vb) : expSort.dir*(va-vb)
  })
  renderExpTable(expFiltered)
}

function renderExpTable(flt) {
  const body = document.getElementById('exp-body')
  if(!body) return
  body.innerHTML = flt.map((s,i) => `<tr class="clickable" onclick="window.selectRec(${songs.indexOf(s)})">
    <td>${i+1}</td><td>${s.name}</td><td>${s.album}</td><td>${s.year}</td><td>${s.popularity}</td>
    ${FEATS.map(f=>`<td>${(s.feats[f]*100).toFixed(1)}%</td>`).join('')}
  </tr>`).join('')
}

// ═══ 推荐器 ═══════════════════════════════════════════════════════════════
function recommenderSection() {
  return `<section id="recommender" class="section-anim">
    <div class="inner">
      <div class="narrative">
        <h2>${T.recommenderTitle}</h2>
        <p>${T.recommenderDesc}</p>
      </div>
      <div class="rec-controls">
        <select id="rec-select">
          <option value="">${T.recSelect}</option>
          ${songs.map((s,i)=>`<option value="${i}">${s.name} — ${s.album} (${s.year})</option>`).join('')}
        </select>
        <button class="cta" style="padding:10px 24px;font-size:.85em" onclick="window.doRec()">${T.recBtn}</button>
      </div>
      <div class="rec-controls" style="margin-top:12px">
        <div class="method-btns">
          <button class="method-btn active" data-method="cosine" onclick="window.switchRecMethod(this,'cosine')">${T.recCosine}</button>
          <button class="method-btn" data-method="knn" onclick="window.switchRecMethod(this,'knn')">${T.recKnn}</button>
          <button class="method-btn" data-method="pca_embed" onclick="window.switchRecMethod(this,'pca_embed')">${T.recPca}</button>
        </div>
      </div>
      <div id="rec-output" style="margin-top:16px"></div>
    </div>
  </section>`
}

function renderRecommender() {
}

function switchRecMethod(el, method) {
  recMethod = method
  $$('.method-btn').forEach(b=>b.classList.remove('active'))
  el.classList.add('active')
  doRec()
}

function doRec() {
  const sel = document.getElementById('rec-select')
  const idx = parseInt(sel?.value)
  if(isNaN(idx)||idx<0) return
  recIdx = idx
  const s = songs[idx]
  const mat = recommender[recMethod]
  const sims = mat[idx].map((v,i)=>({idx:i,sim:v})).filter(x=>x.idx!==idx).sort((a,b)=>b.sim-a.sim).slice(0,10)
  const list = sims.map((r,i) => {
    const rs = songs[r.idx]
    return `<div class="rec-item"><span><span class="rank">${i+1}</span> ${rs.name}</span><span class="score">${(r.sim*100).toFixed(1)}%</span></div>`
  }).join('')
  document.getElementById('rec-output').innerHTML = `<div class="grid-2">
    <div class="rec-list glass"><h4>${T.recTop}</h4>${list}</div>
    <div class="rec-list glass"><h4>${T.featureCompare}</h4>
      <div id="rec-radar" class="chart" style="min-height:320px"></div></div>
  </div>`
  const top = songs[sims[0].idx]
  Plotly.newPlot('rec-radar', [
    {type:'scatterpolar',r:[...FEATS.map(f=>s.feats[f]),s.feats[FEATS[0]]],
     theta:[...FEATS,FEATS[0]], fill:'toself', name:s.name, line:{color:'#fff',width:2}},
    {type:'scatterpolar',r:[...FEATS.map(f=>top.feats[f]),top.feats[FEATS[0]]],
     theta:[...FEATS,FEATS[0]], fill:'toself', name:top.name, line:{color:'#4a9eff',width:2}},
  ], {polar:{bgcolor:'transparent',radialaxis:{visible:true,range:[0,1],gridcolor:'rgba(255,255,255,.04)',color:'#666'},
             angularaxis:{gridcolor:'rgba(255,255,255,.04)',color:'#888',tickfont:{size:9}}},
      paper_bgcolor:'transparent',margin:{l:60,r:60,t:10,b:30},font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},
      legend:{font:{size:10},orientation:'h',y:-0.15} }, {responsive:true,displayModeBar:false})
}

function selectRec(idx) {
  const sel = document.getElementById('rec-select')
  if(sel) { sel.value = idx; document.getElementById('recommender').scrollIntoView({behavior:'smooth'}); setTimeout(doRec, 500) }
}

// ═══ 关于页 ═══════════════════════════════════════════════════════════════
function aboutSection() {
  return `<section id="about" class="section-anim">
    <div class="inner">
      <div class="narrative">
        <h2>${T.aboutTitle}</h2>
        <p>${T.aboutDesc}</p>
      </div>
      <div class="grid-2">
        <div class="card glass" style="padding:20px">
          <h3 style="font-size:1em;color:var(--accent);margin-bottom:12px">${T.dataSources}</h3>
          <p style="color:var(--text2);font-size:.9em;line-height:1.8">${T.dataSrcList}</p>
        </div>
        <div class="card glass" style="padding:20px">
          <h3 style="font-size:1em;color:var(--accent);margin-bottom:12px">${T.methods}</h3>
          <p style="color:var(--text2);font-size:.9em;line-height:1.8">${T.methodList}</p>
        </div>
      </div>
      <div class="text-center" style="margin-top:32px">
        <p style="color:var(--text3);font-size:.85em">${T.footer}</p>
      </div>
    </div>
  </section>`
}

// ═══ 滚动动画 ═════════════════════════════════════════════════════════════
function initScrollAnim() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting) {
        entry.target.classList.add('visible')
        entry.target.querySelectorAll('.stagger').forEach(s => s.classList.add('visible'))
      }
    })
  }, { threshold:0.15 })
  $$('.section-anim').forEach(el => observer.observe(el))

  window.addEventListener('scroll', () => {
    document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 100)
  })
}

// ═══ 初始化 ═══════════════════════════════════════════════════════════════
window.filterExp = filterExp
window.sortExp = sortExp
window.doRec = doRec
window.selectRec = selectRec
window.switchRecMethod = switchRecMethod
buildApp()
