// ─── IMPORTS ───
import { t } from './i18n.js';
import Chart from 'chart.js/auto';
import * as Data from './data.js';
import * as Charts from './charts.js';
import './styles.css';

// ─── STATE ───
let albums = [], songs = [], yearlyData = [], eraGroups = [], topics = [];
let charts = {};
let currentSection = 'overview';

// ─── LANGUAGE ───
// ─── SCROLL NAVIGATION ───
const navTabs = document.querySelectorAll('.nav-tab');
const sections = document.querySelectorAll('.section-scroll');

navTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const section = document.getElementById(`section-${tab.dataset.section}`);
    if (section) {
      const offset = 56 + 52 + 16;
      const top = section.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// IntersectionObserver for fade-in animation only
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1 });

// Scroll-based nav tracking
function updateActiveNav() {
  const offset = 130;
  let active = 'overview';
  sections.forEach(s => {
    if (s.getBoundingClientRect().top <= offset) {
      active = s.dataset.section;
    }
  });
  if (active && active !== currentSection) {
    currentSection = active;
    navTabs.forEach(t => t.classList.remove('active'));
    document.querySelector(`.nav-tab[data-section="${active}"]`)?.classList.add('active');
  }
}
window.addEventListener('scroll', updateActiveNav);

// Scroll progress
function updateProgress() {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const pct = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
  document.getElementById('progress-bar').style.width = `${pct}%`;
}
window.addEventListener('scroll', updateProgress);

// ─── HELPER: chart container ───
function container(title, desc) {
  const div = document.createElement('div');
  div.className = 'chart-block';
  div.innerHTML = `<h3 class="chart-title">${title}</h3>${desc ? `<p class="chart-desc">${desc}</p>` : ''}<div class="chart-wrapper"><canvas></canvas></div>`;
  return div;
}

function clearCharts() {
  Object.values(charts).forEach(c => { if (c && typeof c.destroy === 'function') try { c.destroy(); } catch(e) {} });
  charts = {};
}

function buildSection(section, builder) {
  section.innerHTML = '';
  builder(section);
  observer.observe(section);
  if (section.getBoundingClientRect().top < window.innerHeight) section.classList.add('visible');
}

// ─── SECTION: Overview ───
function buildOverview(section) {
  const stats = Data.getOverallStats();
  const header = document.createElement('div'); header.className = 'section-header';
  header.innerHTML = `<h2>${t('overview.title')}</h2><p class="section-subtitle">${t('overview.subtitle')}</p>`;
  section.appendChild(header);

  const grid = document.createElement('div'); grid.className = 'stats-grid';
  [
    [t('overview.stats.songs'), stats.songCount],
    [t('overview.stats.years'), `${stats.yearMin}-${stats.yearMax}`],
    [t('overview.stats.albums'), stats.albumCount],
    [t('overview.stats.avg_pop'), stats.avgPopularity.toFixed(1)],
    [t('overview.stats.avg_energy'), stats.avgEnergy.toFixed(3)],
    [t('overview.stats.avg_dance'), stats.avgDanceability.toFixed(3)],
    [t('overview.stats.avg_valence'), stats.avgValence.toFixed(3)],
    [t('overview.stats.avg_tempo'), Math.round(stats.avgTempo)],
  ].forEach(([l, v]) => {
    const card = document.createElement('div'); card.className = 'stat-card';
    card.innerHTML = `<div class="stat-value">${v}</div><div class="stat-label">${l}</div>`;
    grid.appendChild(card);
  });
  section.appendChild(grid);

  const c = container(t('overview.timeline.title'), t('overview.timeline.subtitle'));
  section.appendChild(c);
  charts['timeline'] = Charts.createAlbumTimeline(c.querySelector('canvas'), albums);
}

// ─── SECTION: Evolution ───
function buildEvolution(section) {
  const header = document.createElement('div'); header.className = 'section-header';
  header.innerHTML = `<h2>${t('evolution.title')}</h2><p class="section-subtitle">${t('evolution.subtitle')}</p>`;
  section.appendChild(header);

  const oc = container(t('evolution.overview_chart'), t('evolution.overview_desc'));
  section.appendChild(oc);
  charts['evo-overview'] = Charts.createEvolutionOverview(oc.querySelector('canvas'), yearlyData);

  const sub = document.createElement('h3'); sub.className = 'section-subhead'; sub.textContent = t('evolution.detail');
  section.appendChild(sub);

  ['danceability','energy','valence','tempo','acousticness'].forEach(f => {
    const c = container(t(`evolution.${f}`), '');
    section.appendChild(c);
    charts[`evo-${f}`] = Charts.createFeatureEvolution(c.querySelector('canvas'), yearlyData, f);
  });

  const rc = container(t('evolution.era_radar'), t('evolution.era_radar_desc'));
  section.appendChild(rc);
  charts['evo-radar'] = Charts.createEraRadar(rc.querySelector('canvas'), eraGroups);

  const sh = document.createElement('h3'); sh.className = 'section-subhead'; sh.textContent = t('evolution.summary');
  section.appendChild(sh);
  const sd = document.createElement('p'); sd.className = 'chart-desc'; sd.textContent = t('evolution.summary_desc');
  section.appendChild(sd);

  const trends = Data.getEvolutionTrends();
  const headers = ['evolution.feature','evolution.slope_per_year','evolution.r_squared','evolution.pvalue','evolution.overall_mean','evolution.anova_f','evolution.anova_p','evolution.eta_sq'];
  const keys = ['feature','slope','r2','p','mean','anovaF','anovaP','eta2'];
  const table = document.createElement('div'); table.className = 'table-wrapper';
  let html = '<table class="data-table"><thead><tr>' + headers.map(h => `<th>${t(h)}</th>`).join('') + '</tr></thead><tbody>';
  trends.forEach(tr => {
    html += '<tr>' + keys.map(k => `<td>${k === 'feature' ? t(`evolution.${tr[k]}`) : tr[k]}</td>`).join('') + '</tr>';
  });
  table.innerHTML = html + '</tbody></table>';
  section.appendChild(table);
}

// ─── SECTION: Lyrics ───
function buildLyrics(section) {
  const header = document.createElement('div'); header.className = 'section-header';
  header.innerHTML = `<h2>${t('lyrics.title')}</h2><p class="section-subtitle">${t('lyrics.subtitle')}</p>`;
  section.appendChild(header);

  const ls = Data.getLyricsStats();
  const grid = document.createElement('div'); grid.className = 'stats-grid';
  [
    [t('lyrics.stat_vocab'), ls.totalVocab],
    [t('lyrics.stat_unique'), ls.uniqueVocab],
    [t('lyrics.stat_avg_tokens'), ls.avgTokensPerSong],
    [t('lyrics.stat_avg_sentiment'), ls.avgSentiment.toFixed(3)],
    [t('lyrics.stat_avg_chars'), ls.avgChars],
    [t('lyrics.stat_avg_lines'), ls.avgLines],
    [t('lyrics.stat_avg_ttr'), ls.avgTTR.toFixed(3)],
    [t('lyrics.stat_corr'), ls.sentimentValenceCorr.toFixed(3)],
  ].forEach(([l, v]) => {
    const card = document.createElement('div'); card.className = 'stat-card';
    card.innerHTML = `<div class="stat-value">${v}</div><div class="stat-label">${l}</div>`;
    grid.appendChild(card);
  });
  section.appendChild(grid);

  const topWords = Data.getTopWords();
  const c1 = container(t('lyrics.word_freq'), t('lyrics.word_freq_desc'));
  section.appendChild(c1);
  charts['wf'] = Charts.createTopWords(c1.querySelector('canvas'), topWords);

  const c2 = container(t('lyrics.tfidf'), t('lyrics.tfidf_desc'));
  section.appendChild(c2);
  charts['tfidf'] = Charts.createTfidfChart(c2.querySelector('canvas'), topWords);

  const ldaTopics = Data.getLDATopics();
  const c3 = container(t('lyrics.lda_topics'), t('lyrics.lda_topics_desc'));
  section.appendChild(c3);
  charts['lda'] = Charts.createLDATopics(c3.querySelector('canvas'), ldaTopics);

  const topicData = Data.getTopicOverTime();
  const c4 = container(t('lyrics.topic_over_time'), t('lyrics.topic_over_time_desc'));
  section.appendChild(c4);
  charts['topic-time'] = Charts.createTopicOverTime(c4.querySelector('canvas'), topicData, ldaTopics);

  const c5 = container(t('lyrics.topic_pie'), t('lyrics.topic_pie_desc'));
  section.appendChild(c5);
  charts['topic-pie'] = Charts.createTopicPie(c5.querySelector('canvas'), topicData, ldaTopics);

  const c6 = container(t('lyrics.sentiment_dist'), t('lyrics.sentiment_dist_desc'));
  section.appendChild(c6);
  charts['sent-dist'] = Charts.createSentimentDist(c6.querySelector('canvas'));

  const c7 = container(t('lyrics.sentiment_trend'), t('lyrics.sentiment_trend_desc'));
  section.appendChild(c7);
  charts['sent-trend'] = Charts.createSentimentTrend(c7.querySelector('canvas'), yearlyData);

  const c8 = container(t('lyrics.sentiment_by_album'), t('lyrics.sentiment_by_album_desc'));
  section.appendChild(c8);
  charts['sent-album'] = Charts.createSentimentByAlbum(c8.querySelector('canvas'), albums);
}

// ─── SECTION: EDA ───
function buildEDA(section) {
  const header = document.createElement('div'); header.className = 'section-header';
  header.innerHTML = `<h2>${t('eda.title')}</h2><p class="section-subtitle">${t('eda.subtitle')}</p>`;
  section.appendChild(header);

  const mv = container(t('eda.missing_values'), t('eda.missing_values_desc'));
  section.appendChild(mv);
  const w = mv.querySelector('.chart-wrapper');
  w.innerHTML = `<div class="no-missing"><div class="no-missing-icon">✓</div><div class="no-missing-text">${t('eda.no_missing')}</div></div>`;

  const yd = container(t('eda.year_dist'), t('eda.year_dist_desc'));
  section.appendChild(yd);
  charts['yd'] = Charts.createYearDist(yd.querySelector('canvas'), yearlyData);

  const fd = container(t('eda.feature_dist'), t('eda.feature_dist_desc'));
  section.appendChild(fd);
  charts['fd'] = Charts.createFeatureDist(fd.querySelector('canvas'), yearlyData);

  const pd = container(t('eda.popularity_dist'), t('eda.popularity_dist_desc'));
  section.appendChild(pd);
  charts['pd'] = Charts.createPopularityDist(pd.querySelector('canvas'), songs);

  const tp = container(t('eda.top10'), '');
  section.appendChild(tp);
  charts['top10'] = Charts.createTop10Popular(tp.querySelector('canvas'), songs);

  const ch = container(t('eda.corr_heatmap'), t('eda.corr_heatmap_desc'));
  section.appendChild(ch);
  charts['corr'] = Charts.createCorrHeatmap(ch.querySelector('canvas'));
}

// ─── SECTION: Albums ───
function buildAlbums(section) {
  const header = document.createElement('div'); header.className = 'section-header';
  header.innerHTML = `<h2>${t('albums.title')}</h2><p class="section-subtitle">${t('albums.subtitle')}</p>`;
  section.appendChild(header);

  const sc = container(t('albums.song_count'), t('albums.song_count_desc'));
  section.appendChild(sc);
  charts['asc'] = Charts.createAlbumSongCount(sc.querySelector('canvas'), albums);

  const ap = container(t('albums.avg_popularity'), t('albums.avg_popularity_desc'));
  section.appendChild(ap);
  charts['aap'] = Charts.createAlbumAvgPop(ap.querySelector('canvas'), albums);

  const rc = container(t('albums.features_comparison'), t('albums.features_comparison_desc'));
  section.appendChild(rc);
  charts['ar'] = Charts.createEraRadar(rc.querySelector('canvas'), eraGroups);

  const tw = document.createElement('div'); tw.className = 'table-wrapper';
  let html = '<table class="data-table"><thead><tr><th>' + t('albums.album') + '</th><th>' + t('albums.year') + '</th><th>' + t('albums.songs') + '</th><th>' + t('albums.popularity') + '</th><th>' + t('evolution.energy') + '</th><th>' + t('evolution.danceability') + '</th><th>' + t('evolution.valence') + '</th></tr></thead><tbody>';
  albums.forEach(a => {
    html += `<tr><td>${a.album_cn}</td><td>${a.year}</td><td>${a.song_count}</td><td>${a.avg_popularity.toFixed(1)}</td><td>${a.avg_energy.toFixed(3)}</td><td>${(a.avg_danceability || '-')}</td><td>${a.avg_valence.toFixed(3)}</td></tr>`;
  });
  tw.innerHTML = html + '</tbody></table>';
  section.appendChild(tw);
}

// ══════════════════════════════════════════════════════════════════
// ─── SECTION: Recommender ───
// ══════════════════════════════════════════════════════════════════

const METHODS = ["Cosine_Similarity", "KNN", "PCA_Embedding"];
const FEATURES = ["danceability","energy","valence","tempo","acousticness","instrumentalness","speechiness","loudness","key","duration_ms","mode"];
const FEATURE_LABELS = ["舞动性","能量","情绪积极性","速度","声学性","乐器感","语言清晰度","响度","调性","时长","调式"];
const METHOD_LABELS = {
  Cosine_Similarity: () => t('rec.cos_similarity'),
  KNN: () => t('rec.knn'),
  PCA_Embedding: () => t('rec.pca_embedding'),
};
const METHOD_COLORS = { Cosine_Similarity: '#0071e3', KNN: '#5e5ce6', PCA_Embedding: '#00b894' };

let recData = null;
let recSongs = [];
let currentSongIdx = -1;
let radarChart = null;

function populateRecSelect(sel) {
  sel.innerHTML = `<option value="" disabled selected>${t('rec.select_placeholder')}</option>`;
  recSongs.forEach((s, i) => {
    const opt = document.createElement('option');
    opt.value = i;
    opt.textContent = `${s.song_name} — ${s.album_cn || s.album_en} (${s.year})`;
    sel.appendChild(opt);
  });
}

function renderRecInfo(idx) {
  const s = recSongs[idx];
  document.getElementById('rec-info-bar').classList.add('visible');
  document.getElementById('rec-selected-name').textContent = s.song_name;
  const album = s.album_cn || s.album_en;
  document.getElementById('rec-selected-meta').textContent = `${album} · ${s.year}`;
  const img = document.getElementById('rec-cover-img');
  img.src = s.cover_url || '';
  img.onerror = () => { img.src = ''; img.style.display = 'none'; };
}

function renderRecMethods(idx) {
  const container = document.getElementById('rec-methods');
  container.innerHTML = '';
  METHODS.forEach(m => {
    const results = recData[m].top_k[idx];
    const color = METHOD_COLORS[m];
    const card = document.createElement('div'); card.className = 'rec-method-card';
    card.innerHTML = `
      <div class="rec-card-header">
        <span style="color:${color}">${METHOD_LABELS[m]()}</span>
        <span class="rec-badge">${t('rec.top10')}</span>
      </div>
      <div class="rec-result-list">
        ${results.map((r, i) => {
          const song = recSongs[r.idx];
          const pct = (r.sim * 100).toFixed(1);
          return `<div class="rec-result-item" data-input="${idx}" data-result="${r.idx}">
            <div class="rec-rank">${i + 1}</div>
            <div class="rec-song-details">
              <div class="rec-name">${song.song_name}</div>
              <div class="rec-meta">${song.album_cn || song.album_en} · ${song.year}</div>
            </div>
            <div class="rec-sim-bar"><div class="rec-fill" style="width:${pct}%;background:${color}"></div></div>
            <div class="rec-sim-score" style="color:${color}">${pct}%</div>
          </div>`;
        }).join('')}
      </div>`;
    container.appendChild(card);

    card.querySelectorAll('.rec-result-item').forEach(el => {
      el.addEventListener('click', () => {
        const iIdx = parseInt(el.dataset.input);
        const rIdx = parseInt(el.dataset.result);
        renderRecRadar(iIdx, rIdx);
      });
    });
  });
}

function renderRecRadar(inputIdx, resultIdx) {
  const wrap = document.getElementById('rec-radar-chart');
  wrap.innerHTML = '';

  if (resultIdx === undefined || resultIdx < 0) {
    wrap.innerHTML = `<div class="rec-loading">${t('rec.select_prompt')}</div>`;
    return;
  }

  const s = recSongs[inputIdx], r = recSongs[resultIdx];
  const inputVals = FEATURES.map(f => s[f] ?? 0);
  const resVals = FEATURES.map(f => r[f] ?? 0);

  // Normalize tempo
  const norm = (v, f) => f === 'tempo' ? v / 120 : v;

  // Destroy previous chart
  if (radarChart) {
    radarChart.destroy();
    radarChart = null;
  }

  const canvas = document.createElement('canvas');
  wrap.style.width = '100%';
  wrap.style.height = '400px';
  wrap.appendChild(canvas);

  radarChart = new Chart(canvas, {
    type: 'radar',
    data: {
      labels: FEATURE_LABELS,
      datasets: [
        {
          label: s.song_name,
          data: inputVals.map((v, i) => norm(v, FEATURES[i])),
          borderColor: '#1d1d1f',
          backgroundColor: 'rgba(29, 29, 31, 0.1)',
          pointBackgroundColor: '#1d1d1f',
          pointBorderColor: '#fff',
          pointHoverRadius: 5,
          borderWidth: 2,
        },
        {
          label: r.song_name,
          data: resVals.map((v, i) => norm(v, FEATURES[i])),
          borderColor: '#0071e3',
          backgroundColor: 'rgba(0, 113, 227, 0.1)',
          pointBackgroundColor: '#0071e3',
          pointBorderColor: '#fff',
          pointHoverRadius: 5,
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { font: { size: 11 }, color: '#6e6e73' },
        },
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 1,
          ticks: { stepSize: 0.2, font: { size: 10 }, color: '#6e6e73' },
          grid: { color: '#e8e8ed' },
          pointLabels: { font: { size: 11 }, color: '#888' },
          angleLines: { color: '#e8e8ed' },
        },
      },
    },
  });
}

// ─── SECTION: Recommender Builder ───
function buildRecommender(section) {
  const hero = document.createElement('div'); hero.className = 'recommender-hero';
  hero.innerHTML = `<h2>${t('rec.title')}</h2><p>${t('rec.subtitle')}</p>`;
  section.appendChild(hero);

  recSongs = Data.getSongs();

  const selector = document.createElement('div'); selector.className = 'rec-selector';
  selector.innerHTML = `
    <label>${t('rec.select')}</label>
    <div style="flex:1"><select id="rec-song-select"></select></div>
    <button class="rec-btn" id="rec-btn">${t('rec.recommend')}</button>`;
  section.appendChild(selector);

  const info = document.createElement('div'); info.className = 'rec-info-bar'; info.id = 'rec-info-bar';
  info.innerHTML = `
    <div style="display:flex;align-items:center;gap:12px">
      <img id="rec-cover-img" class="rec-album-cover" alt="">
      <div class="rec-song-info">
        <h3 id="rec-selected-name"></h3>
        <span id="rec-selected-meta"></span>
      </div>
    </div>
    <div class="rec-legend">
      <div class="rec-legend-item"><span class="rec-legend-dot" style="background:#1d1d1f"></span> ${t('rec.input_song')}</div>
      <div class="rec-legend-item"><span class="rec-legend-dot" style="background:#0071e3"></span> ${t('rec.top_recommend')}</div>
    </div>`;
  section.appendChild(info);

  const methods = document.createElement('div'); methods.className = 'rec-methods'; methods.id = 'rec-methods';
  section.appendChild(methods);

  const radar = document.createElement('div'); radar.id = 'rec-radar-wrapper';
  radar.innerHTML = `<h3>📊 ${t('rec.feature_compare')}</h3><div id="rec-radar-chart"><div class="rec-loading">${t('rec.select_prompt')}</div></div>`;
  section.appendChild(radar);

  // Populate select & setup handler
  populateRecSelect(document.getElementById('rec-song-select'));
  document.getElementById('rec-btn').addEventListener('click', () => {
    const sel = document.getElementById('rec-song-select');
    const idx = parseInt(sel.value);
    if (isNaN(idx)) return;
    currentSongIdx = idx;
    renderRecInfo(idx);
    renderRecMethods(idx);
    const results = recData[METHODS[0]].top_k[idx];
    if (results && results.length) renderRecRadar(idx, results[0].idx);
  });
}

// ─── FULL RENDER ───
function fullRender() {
  clearCharts();
  document.getElementById('app-title').textContent = '周杰伦音乐深度分析';
  document.querySelector('.footer-text').textContent = t('footer');

  const sectionIds = ['section-overview','section-evolution','section-lyrics','section-eda','section-albums','section-recommender'];
  const builders = [buildOverview, buildEvolution, buildLyrics, buildEDA, buildAlbums, buildRecommender];
  sectionIds.forEach((id, i) => buildSection(document.getElementById(id), builders[i]));

  // Ensure all sections become visible after rendering,
  // regardless of IntersectionObserver timing.
  requestAnimationFrame(() => {
    document.querySelectorAll('.section-scroll').forEach(s => s.classList.add('visible'));
  });
}

// ═══ INIT ═══
async function init() {
  const result = await Data.loadData();
  if (!result) {
    document.getElementById('main').innerHTML = `<div class="error-msg">${t('error_load')}</div>`;
    return;
  }
  albums = result.albums;
  songs = result.songs;
  yearlyData = Data.getYearlyAverages();
  eraGroups = Data.getEraGroups();

  // Load recommender data
  try {
    const res = await fetch('/data/recommender_data.json');
    recData = await res.json();
  } catch(e) {
    console.warn('Recommender data not loaded');
  }

  fullRender();
}

init().catch(err => {
  console.error(err);
  document.getElementById('main').innerHTML = `<div class="error-msg">加载失败: ${err.message}</div>`;
});
