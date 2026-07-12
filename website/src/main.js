import DATA from './data.json'
import { t, tAll, setLang, currentLang } from './i18n.js'

const D = DATA
const { songs, features:FEATS, pca, umap, clusters:CL, yearly, albums, eras, recommender, word_freq, title_freq, insights, meta } = D

const COLORS = ['#5b9cf5','#845ef7','#20c997','#ff6b6b','#fcc419','#51cf66','#e64980','#9775fa','#38d9a9','#74c0fc']
const EVO_FEATS = ['energy','danceability','acousticness','valence','speechiness','loudness']

// ═══ 状态管理 ═══════════════════════════════════════════════════════════
let recMethod = 'cosine'
let recIdx = -1
let expFiltered = []
let expSort = { col:0, dir:1 }
let lang = 'zh'

// ═══ DOM 辅助 ═══════════════════════════════════════════════════════════
const $ = s => document.querySelector(s)
const $$ = s => document.querySelectorAll(s)

// ═══ 构建应用 ════════════════════════════════════════════════════════════
function buildApp() {
  document.getElementById('app').innerHTML = `
    <nav id="nav">
      <div class="brand">🎵 Jay Chou Music</div>
      <div style="display:flex;gap:4px;align-items:center">
        <button class="lang-btn" onclick="window.toggleLang()">${lang === 'zh' ? 'EN' : '中文'}</button>
      </div>
    </nav>
    <main>
      ${heroSection()}${overviewSection()}${evolutionSection()}${lyricsSection()}
      ${clusterSection()}${explorerSection()}${recommenderSection()}${aboutSection()}
    </main>
    <footer style="text-align:center;padding:40px 20px;color:var(--text3);font-size:.8em">
      ${t('footer')}
    </footer>`
  initScrollAnim()
  renderHomeCharts()
  renderEvoChart()
  renderLyricChart()
  renderClusterCharts()
  renderExplorer()
  renderRecommender()
  listenLang()
}

// ═══ 英雄页 ═══════════════════════════════════════════════════════════════
function heroSection() {
  return `<section id="hero" class="section-anim">
    <div class="inner">
      <p style="font-size:.85em;color:var(--text3);margin-bottom:12px;letter-spacing:4px;text-transform:uppercase">${t('hero.subtitle').split(' ')[0]}</p>
      <h1>${t('hero.title')}</h1>
      <p>${t('hero.subtitle')}</p>
      <button class="cta" onclick="document.getElementById('overview').scrollIntoView({behavior:'smooth'})">
        ${t('hero.cta')} →
      </button>
    </div>
    <div class="scroll-hint">${t('hero.scroll')}<br>↓</div>
  </section>`
}

// ═══ 概览页 ═══════════════════════════════════════════════════════════════
function overviewSection() {
  return `<section id="overview" class="section-anim">
    <div class="inner stagger">
      <div class="narrative stagger">
        <h2>${t('overview.title')}</h2>
        <p>${t('overview.desc', { years: `${meta.year_min}-${meta.year_max}`, albums: meta.albums, songs: meta.songs })}</p>
      </div>
      <div class="stats-strip stagger">
        <div class="stat-card"><div class="val">${meta.songs}</div><div class="lbl">${t('insights.songs')}</div></div>
        <div class="stat-card"><div class="val">${meta.albums}</div><div class="lbl">${t('insights.albums')}</div></div>
        <div class="stat-card"><div class="val">${meta.year_min}-${meta.year_max}</div><div class="lbl">${t('insights.years')}</div></div>
        <div class="stat-card"><div class="val">${meta.avg_pop}</div><div class="lbl">${t('insights.pop')}</div></div>
      </div>
      <div class="grid-2 stagger">
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">Popularity Distribution</h2><div id="pop-chart" class="chart-sm"></div></div>
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">Songs per Album</h2><div id="album-chart" class="chart-sm"></div></div>
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
  const eraNames = Object.keys(eras)
  const eraRadar = eraNames.map((en,i) => ({
    type:'scatterpolar',
    r: Object.values(eras[en].features).concat(Object.values(eras[en].features)[0]),
    theta: [...FEATS, FEATS[0]], fill:'toself', name: `${en}`,
    line:{color:COLORS[i]}, marker:{color:COLORS[i]}
  }))

  return `<section id="evolution" class="section-anim">
    <div class="inner">
      <div class="narrative stagger">
        <h2>${t('evolution.title')}</h2>
        <p>${t('evolution.desc1')} <span class="highlight">${FEATS[0]}</span> ${t('evolution.desc2', { feature:'energy' })}</p>
      </div>
      <div class="card glass stagger"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">Feature Trends (2000-2022)</h2>
        <div id="evo-chart" class="chart"></div></div>
      <div class="grid-2 stagger" style="margin-top:16px">
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">Era Radar</h2>
          <div id="era-chart" class="chart"></div></div>
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">Era Stats</h2>
          <div id="era-stats"></div></div>
      </div>
    </div>
  </section>`
}

function renderEvoChart() {
  Plotly.newPlot('evo-chart', EVO_FEATS.map(f => ({
    x:yearly.years, y:yearly[f], mode:'lines+markers', name:t(`evolution.${f}`),
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
    <tr><th>时代</th><th>歌曲数</th><th>平均流行度</th></tr>
    ${eraNames.map(en => `<tr><td>${en}</td><td>${eras[en].count}</td><td>${eras[en].popularity}</td></tr>`).join('')}</table>`
}

// ═══ 歌词页 ═══════════════════════════════════════════════════════════════
function lyricsSection() {
  const wfArr = Object.entries(word_freq).slice(0,20)
  const tfArr = Object.entries(title_freq).slice(0,10)
  const topW = insights.top_words?.[0] || '的'
  const theme = lang === 'zh' ? '浪漫与叙事' : 'romantic and narrative'

  return `<section id="lyrics" class="section-anim">
    <div class="inner">
      <div class="narrative stagger">
        <h2>${t('lyrics.title')}</h2>
        <p>${t('lyrics.desc1', { words:Math.round(insights.words_total/1000), unique:insights.words_unique })}</p>
        <p>${t('lyrics.desc2', { word:topW, theme })}</p>
      </div>
      <div class="grid-2 stagger">
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">Top Words</h2>
          <div id="wf-chart" class="chart"></div></div>
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">Title Characters</h2>
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
  const c0 = ca.c0, c1 = ca.c1
  const c0d = lang==='zh'?'快歌/高能量':'upbeat/energetic'
  const c1d = lang==='zh'?'抒情/慢歌':'ballad/melodic'

  return `<section id="cluster" class="section-anim">
    <div class="inner">
      <div class="narrative stagger">
        <h2>${t('cluster.title')}</h2>
        <p>${t('cluster.desc1', { c0:c0.size, c0a:c0.top_songs[0], c0d, c1:c1.size, c1a:c1.top_songs[0], c1d })}</p>
        <p>${t('cluster.desc2', { noise:insights.noise })}</p>
      </div>
      <div class="grid-2 stagger">
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">PCA + KMeans</h2>
          <div id="pca-chart" class="chart"></div></div>
        <div class="card glass"><h2 style="font-size:1em;margin-bottom:12px;color:var(--text2)">UMAP + HDBSCAN</h2>
          <div id="umap-chart" class="chart"></div></div>
      </div>
    </div>
  </section>`
}

function renderClusterCharts() {
  const h = songs.map((s,i) => `${s.name}<br>Album: ${s.album} (${s.year})<br>Pop: ${s.popularity}`)
  const ks = [...new Set(CL.kmeans)].sort()
  const pt = ks.map(k => ({ x:[],y:[],mode:'markers',name:`Cluster ${k}`,text:[],hoverinfo:'text',
    marker:{size:6,color:COLORS[k%COLORS.length]} }))
  songs.forEach((s,i) => { const ci=ks.indexOf(CL.kmeans[i]); if(ci>=0){pt[ci].x.push(pca.coords[i][0]);pt[ci].y.push(pca.coords[i][1]);pt[ci].text.push(h[i])} })
  Plotly.newPlot('pca-chart', pt, { margin:{l:40,r:10,t:10,b:40},paper_bgcolor:'transparent',plot_bgcolor:'transparent',
    font:{color:'#aaa',family:'Inter,-apple-system,BlinkMacSystemFont,sans-serif',size:11},xaxis:{gridcolor:'rgba(255,255,255,.04)',title:'主成分 1'},yaxis:{gridcolor:'rgba(255,255,255,.04)',title:'主成分 2'},
    legend:{font:{size:9}} }, { responsive:true,displayModeBar:false })

  const hs = [...new Set(CL.hdbscan)].sort((a,b)=>a-b)
  const ut = hs.map(k => ({ x:[],y:[],mode:'markers',name:k===-1?'噪声':`Cluster ${k}`,text:[],hoverinfo:'text',
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
      <div class="narrative stagger"><h2>${t('explorer.title')}</h2></div>
      <div class="exp-controls stagger">
        <input id="exp-search" placeholder="${t('explorer.search')}" oninput="window.filterExp()">
        <select id="exp-album" onchange="window.filterExp()">
          <option value="">${t('explorer.album')}</option>
          ${allAlbums.map(a=>`<option value="${a}">${a}</option>`).join('')}
        </select>
      </div>
      <div class="table-wrap stagger"><table class="song-table" id="exp-table">
        <thead><tr>
          <th onclick="window.sortExp(0)">#</th>
          <th onclick="window.sortExp(1)">Song</th>
          <th onclick="window.sortExp(2)">专辑</th>
          <th onclick="window.sortExp(3)">Year</th>
          <th onclick="window.sortExp(4)">Pop</th>
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
      <div class="narrative stagger">
        <h2>${t('recommender.title')}</h2>
        <p>${t('recommender.desc')}</p>
      </div>
      <div class="rec-controls stagger">
        <select id="rec-select">
          <option value="">${t('recommender.select')}...</option>
          ${songs.map((s,i)=>`<option value="${i}">${s.name} — ${s.album} (${s.year})</option>`).join('')}
        </select>
        <button class="cta" style="padding:10px 24px;font-size:.85em" onclick="window.doRec()">${t('recommender.recommend')}</button>
      </div>
      <div class="rec-controls stagger" style="margin-top:12px">
        <div class="method-btns">
          <button class="method-btn active" data-method="cosine" onclick="window.switchRecMethod(this,'cosine')">${t('recommender.cosine')}</button>
          <button class="method-btn" data-method="knn" onclick="window.switchRecMethod(this,'knn')">${t('recommender.knn')}</button>
          <button class="method-btn" data-method="pca_embed" onclick="window.switchRecMethod(this,'pca_embed')">${t('recommender.pca')}</button>
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
    <div class="rec-list glass"><h4>${t('recommender.top')}</h4>${list}</div>
    <div class="rec-list glass"><h4>Feature: ${s.name} vs ${songs[sims[0].idx].name}</h4>
      <div id="rec-radar" class="chart" style="height:320px"></div></div>
  </div>`
  // Radar
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
      <div class="narrative stagger">
        <h2>${t('about.title')}</h2>
        <p>${t('about.desc')}</p>
      </div>
      <div class="grid-2 stagger">
        <div class="card glass" style="padding:20px">
          <h3 style="font-size:1em;color:var(--accent);margin-bottom:12px">Data Sources</h3>
          <p style="color:var(--text2);font-size:.9em;line-height:1.8">
            • Spotify API — Audio features for 174 songs<br>
            • Lyrics — Full text of all songs<br>
            • Album metadata — 16 albums (2000-2022)
          </p>
        </div>
        <div class="card glass" style="padding:20px">
          <h3 style="font-size:1em;color:var(--accent);margin-bottom:12px">Methods</h3>
          <p style="color:var(--text2);font-size:.9em;line-height:1.8">
            • PCA / UMAP for dimensionality reduction<br>
            • KMeans / HDBSCAN for clustering<br>
            • Cosine Similarity / KNN for recommendation<br>
            • RandomForest / XGBoost / LightGBM / CatBoost for prediction<br>
            • SHAP for model interpretation
          </p>
        </div>
      </div>
      <div class="stagger text-center" style="margin-top:24px">
        <p style="color:var(--text3);font-size:.85em">${t('footer')}</p>
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
        // Also handle stagger children
        entry.target.querySelectorAll('.stagger').forEach(s => s.classList.add('visible'))
      }
    })
  }, { threshold:0.15 })
  $$('.section-anim').forEach(el => observer.observe(el))

  // Nav scroll effect
  window.addEventListener('scroll', () => {
    document.getElementById('nav').classList.toggle('scrolled', window.scrollY > 100)
  })
}

// ═══ 多语言 ═══════════════════════════════════════════════════════════════
function listenLang() {
  document.addEventListener('langchange', e => {
    lang = e.detail
    document.querySelector('.lang-btn').textContent = lang === 'zh' ? 'EN' : '中文'
    buildApp()
  })
}

function toggleLang() {
  setLang(lang === 'zh' ? 'en' : 'zh')
}

// ═══ 初始化 ═══════════════════════════════════════════════════════════════
window.toggleLang = toggleLang
window.filterExp = filterExp
window.sortExp = sortExp
window.doRec = doRec
window.selectRec = selectRec
window.switchRecMethod = switchRecMethod
buildApp()
