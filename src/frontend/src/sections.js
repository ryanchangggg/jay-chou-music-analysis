/* ═══════════════════════════════════════════════════════════════════════════
   sections.js — HTML 模板构建器
   ─── 每个函数接收 T（当前语言文案）和 D（数据），返回 HTML 字符串
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * 导航栏
 */
export function navHtml(T) {
  return `
    <nav id="nav">
      <div class="nav-inner">
        <div class="nav-brand">🎵 ${T.navBrand}</div>
        <button id="lang-btn" class="lang-btn">${T.langSwitch}</button>
      </div>
    </nav>`
}

/**
 * Hero 区
 */
export function heroHtml(T) {
  return `
    <section id="hero" class="section-anim">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <h1>${T.heroTitle}</h1>
        <p>${T.heroSub}</p>
        <button class="cta" data-target="overview">
          ${T.heroCta}
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </button>
        <div class="scroll-hint">
          ${T.heroScroll}
          <svg width="16" height="24" viewBox="0 0 16 24" fill="none"><rect x="1" y="1" width="14" height="22" rx="7" stroke="currentColor" stroke-width="2"/><circle cx="8" cy="7" r="2" fill="currentColor" class="scroll-dot"/></svg>
        </div>
      </div>
    </section>`
}

/**
 * 数据概览
 */
export function overviewHtml(T, D) {
  const { songs, albums, year_min, year_max, avg_pop } = D.meta
  return `
    <section id="overview" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.overviewTitle}</h2>
          <p>${T.overviewDesc(D.meta)}</p>
        </div>
        <div class="stats-row staggered">
          <div class="stat-card" style="--stat-delay:0">
            <div class="stat-num" data-count="${songs}">0</div>
            <div class="stat-label">${T.statSongs}</div>
          </div>
          <div class="stat-card" style="--stat-delay:0.1">
            <div class="stat-num" data-count="${albums}">0</div>
            <div class="stat-label">${T.statAlbums}</div>
          </div>
          <div class="stat-card" style="--stat-delay:0.2">
            <div class="stat-num">${year_min}–${year_max}</div>
            <div class="stat-label">${T.statYears}</div>
          </div>
          <div class="stat-card" style="--stat-delay:0.3">
            <div class="stat-num" data-count="${avg_pop}" data-decimals="1">0</div>
            <div class="stat-label">${T.statPop}</div>
          </div>
        </div>
        <div class="grid-2 staggered">
          <div class="chart-card" style="--card-delay:0">
            <div class="chart-card-title">${T.chartPopDist}</div>
            <div id="chart-pop-dist" class="chart-sm"></div>
          </div>
          <div class="chart-card" style="--card-delay:0.1">
            <div class="chart-card-title">${T.chartSongsPerAlbum}</div>
            <div id="chart-album-songs" class="chart-sm"></div>
          </div>
        </div>
      </div>
    </section>`
}

/**
 * 音乐风格演变
 */
export function evolutionHtml(T, D) {
  const eraNames = Object.keys(D.eras)
  const eraLabel = (en) => {
    if (en.includes('Early')) return T.eraEarly
    if (en.includes('Golden')) return T.eraGolden
    if (en.includes('Experimental')) return T.eraExperimental
    if (en.includes('Recent')) return T.eraRecent
    return en
  }
  return `
    <section id="evolution" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.evoTitle}</h2>
          <p>${T.evoDesc}</p>
        </div>
        <div class="chart-card full-width staggered">
          <div class="chart-card-title">${T.evoFeatureTrends}</div>
          <div id="chart-evo" class="chart-lg"></div>
        </div>
        <div class="grid-2 staggered">
          <div class="chart-card" style="--card-delay:0">
            <div class="chart-card-title">${T.evoEraRadar}</div>
            <div id="chart-era-radar" class="chart"></div>
          </div>
          <div class="chart-card" style="--card-delay:0.1">
            <div class="chart-card-title">${T.evoEraStats}</div>
            <div class="era-table-wrap" id="era-table-wrap">
              <table class="era-table">
                <thead>
                  <tr>
                    <th>${T.evoTableEra}</th>
                    <th>${T.evoTableSongs}</th>
                    <th>${T.evoTablePop}</th>
                  </tr>
                </thead>
                <tbody>
                  ${eraNames.map(en => `
                    <tr>
                      <td><span class="era-dot" style="--dot-color:hsl(${eraNames.indexOf(en) * 60 + 200}, 70%, 55%)"></span>${eraLabel(en)}</td>
                      <td>${D.eras[en].count}</td>
                      <td>${D.eras[en].popularity}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>`
}

/**
 * 歌词分析
 */
export function lyricsHtml(T, D) {
  const insights = D.insights
  return `
    <section id="lyrics" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.lyricsTitle}</h2>
          <p>${T.lyricsDesc1(insights)}</p>
          <p>${T.lyricsDesc2(insights)}</p>
        </div>
        <div class="grid-2 staggered">
          <div class="chart-card" style="--card-delay:0">
            <div class="chart-card-title">${T.lyricsTopWords}</div>
            <div id="chart-word-freq" class="chart"></div>
          </div>
          <div class="chart-card" style="--card-delay:0.1">
            <div class="chart-card-title">${T.lyricsTitleChars}</div>
            <div id="chart-title-freq" class="chart"></div>
          </div>
        </div>
      </div>
    </section>`
}

/**
 * 聚类分析
 */
export function clusterHtml(T, D) {
  const a = D.clusters.analysis
  const noise = D.insights.noise
  return `
    <section id="cluster" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.clusterTitle}</h2>
          <p>${T.clusterDesc1(a)}</p>
          <p>${T.clusterDesc2(noise)}</p>
        </div>
        <div class="grid-2 staggered">
          <div class="chart-card" style="--card-delay:0">
            <div class="chart-card-title">${T.clusterPca}</div>
            <div id="chart-pca" class="chart"></div>
          </div>
          <div class="chart-card" style="--card-delay:0.1">
            <div class="chart-card-title">${T.clusterUmap}</div>
            <div id="chart-umap" class="chart"></div>
          </div>
        </div>
      </div>
    </section>`
}

/**
 * 热门度分析
 */
export function popularityHtml(T, D) {
  const sorted = [...D.songs].sort((a, b) => b.popularity - a.popularity)
  const top3 = sorted.slice(0, 3)
  return `
    <section id="popularity" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.popTitle}</h2>
          <p>${T.popDesc(D.insights)}</p>
        </div>
        <div class="pop-podium staggered">
          ${top3.map((s, i) => `
            <div class="podium-card" style="--podium-rank:${i + 1};--podium-delay:${i * 0.12}s">
              <div class="podium-rank">#${i + 1}</div>
              <div class="podium-name">${s.name}</div>
              <div class="podium-album">${s.album} · ${s.year}</div>
              <div class="podium-score">${s.popularity}</div>
              <div class="podium-label">${T.chartPopDist}</div>
            </div>
          `).join('')}
        </div>
        <div class="chart-card full-width staggered">
          <div class="chart-card-title">${T.popCompare}</div>
          <div id="chart-pop-compare" class="chart-lg"></div>
        </div>
      </div>
    </section>`
}

/**
 * 歌曲探索器
 */
export function explorerHtml(T, D) {
  const allAlbums = [...new Set(D.songs.map(s => s.album))].sort()
  const feats = ['danceability', 'energy', 'valence', 'acousticness', 'speechiness', 'loudness']
  return `
    <section id="explorer" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.expTitle}</h2>
        </div>
        <div class="exp-toolbar staggered">
          <div class="exp-filters">
            <div class="exp-search-wrap">
              <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              <input type="text" id="exp-search" class="exp-input" placeholder="${T.expSearch}">
            </div>
            <select id="exp-album" class="exp-select">
              <option value="">${T.expAlbumAll}</option>
              ${allAlbums.map(a => `<option value="${a}">${a}</option>`).join('')}
            </select>
          </div>
          <div id="exp-count" class="exp-count"></div>
        </div>
        <div class="exp-table-wrap staggered">
          <table class="exp-table" id="exp-table">
            <thead>
              <tr>
                <th class="col-idx" data-col="0">${T.expColIdx} <span class="sort-arrow"></span></th>
                <th data-col="1">${T.expColName} <span class="sort-arrow"></span></th>
                <th data-col="2">${T.expColAlbum} <span class="sort-arrow"></span></th>
                <th data-col="3">${T.expColYear} <span class="sort-arrow"></span></th>
                <th data-col="4" class="sorted desc">${T.expColPop} <span class="sort-arrow">▼</span></th>
                ${feats.map((f, i) => `
                  <th data-col="${i + 5}">${T.expFeat[f]} <span class="sort-arrow"></span></th>
                `).join('')}
              </tr>
            </thead>
            <tbody id="exp-body"></tbody>
          </table>
          <div class="exp-empty" id="exp-empty">${T.expNoResult}</div>
        </div>
      </div>
    </section>`
}

/**
 * 智能推荐系统
 */
export function recommenderHtml(T, D) {
  return `
    <section id="recommender" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.recTitle}</h2>
          <p>${T.recDesc}</p>
        </div>
        <div class="rec-controls staggered">
          <div class="rec-select-row">
            <select id="rec-select" class="exp-select">
              <option value="">${T.recSelect}</option>
              ${D.songs.map((s, i) => `<option value="${i}">${s.name} — ${s.album}（${s.year}）</option>`).join('')}
            </select>
            <button id="rec-btn" class="cta secondary">${T.recBtn}</button>
          </div>
          <div class="method-tabs">
            <button class="method-tab active" data-method="cosine">${T.recCos}</button>
            <button class="method-tab" data-method="knn">${T.recKnn}</button>
            <button class="method-tab" data-method="pca_embed">${T.recPca}</button>
          </div>
        </div>
        <div id="rec-output" class="rec-output staggered"></div>
      </div>
    </section>`
}

/**
 * 关于
 */
export function aboutHtml(T) {
  return `
    <section id="about" class="section-anim">
      <div class="container">
        <div class="section-header staggered">
          <h2>${T.aboutTitle}</h2>
          <p>${T.aboutDesc}</p>
        </div>
        <div class="grid-2 staggered">
          <div class="info-card" style="--card-delay:0">
            <div class="info-card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
            </div>
            <h3>${T.aboutSources}</h3>
            <ul>
              ${T.aboutSourceList.map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
          <div class="info-card" style="--card-delay:0.1">
            <div class="info-card-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <h3>${T.aboutMethods}</h3>
            <ul>
              ${T.aboutMethodList.map(s => `<li>${s}</li>`).join('')}
            </ul>
          </div>
        </div>
      </div>
      <div class="about-footer">${T.aboutFooter}</div>
    </section>`
}
