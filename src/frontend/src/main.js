/* ═══════════════════════════════════════════════════════════════════════════
   main.js — 应用入口与编排
   ─── 负责：数据加载、语言切换、状态管理、事件绑定、渲染调度
   ═══════════════════════════════════════════════════════════════════════════ */

import DATA from './data.json'
import { ZH_CN, ZH_TW } from './lang.js'
import {
  navHtml, heroHtml, overviewHtml, evolutionHtml, lyricsHtml,
  clusterHtml, popularityHtml, explorerHtml, recommenderHtml, aboutHtml,
} from './sections.js'
import {
  renderPopDist, renderAlbumSongs, renderEvoTrend, renderEraRadar,
  renderWordFreq, renderTitleFreq, renderPca, renderUmap,
  renderPopCompare, renderRecRadar,
} from './charts.js'

/* ─── 别名 ─── */
const D = DATA
const songs = D.songs
const yearly = D.yearly
const pca = D.pca
const umapD = D.umap
const clusters = D.clusters
const wordFreq = D.word_freq
const titleFreq = D.title_freq
const eras = D.eras
const recommender = D.recommender
const FEATS = D.features

/* ─── 探索器显示的特征（子集，去掉了人不易理解的 key/mode/duration/inst） ─── */
const EXP_FEATS = ['danceability', 'energy', 'valence', 'acousticness', 'speechiness', 'loudness']

/* ─── 状态 ─── */
let currentLang = 'zh_CN'
let recMethod = 'cosine'
let recIdx = -1
let expFiltered = []
let expSort = { col: 4, dir: -1 } // 默认按人气降序

/* ─── DOM 快捷引用 ─── */
const $ = s => document.querySelector(s)
const $$ = s => document.querySelectorAll(s)

/* ─── 获取当前语言文案 ─── */
function t() {
  return currentLang === 'zh_CN' ? ZH_CN : ZH_TW
}

/* ═══════════════════════════════════════════════════════════════════════════
   构建应用
   ═══════════════════════════════════════════════════════════════════════════ */
function buildApp() {
  const T = t()
  const app = document.getElementById('app')

  app.innerHTML = `
    ${navHtml(T)}
    <main>
      ${heroHtml(T)}
      ${overviewHtml(T, D)}
      ${evolutionHtml(T, D)}
      ${lyricsHtml(T, D)}
      ${clusterHtml(T, D)}
      ${popularityHtml(T, D)}
      ${explorerHtml(T, D)}
      ${recommenderHtml(T, D)}
      ${aboutHtml(T)}
    </main>`

  // 等 DOM 渲染后再注册事件、绘图
  requestAnimationFrame(() => {
    renderAllCharts()
    bindEvents()
    initScrollAnim()
    initCountUp()
    initExplorer()
  })
}

/* ═══════════════════════════════════════════════════════════════════════════
   渲染所有图表
   ═══════════════════════════════════════════════════════════════════════════ */
function renderAllCharts() {
  const T = t()
  const l = currentLang

  renderPopDist(document.getElementById('chart-pop-dist'), songs, l)
  renderAlbumSongs(document.getElementById('chart-album-songs'), songs)
  renderEvoTrend(document.getElementById('chart-evo'), yearly, FEATS, l)
  renderEraRadar(document.getElementById('chart-era-radar'), eras, FEATS, l)
  renderWordFreq(document.getElementById('chart-word-freq'), wordFreq)
  renderTitleFreq(document.getElementById('chart-title-freq'), titleFreq)
  renderPca(document.getElementById('chart-pca'), songs, pca, clusters)
  renderUmap(document.getElementById('chart-umap'), songs, umapD, clusters)
  renderPopCompare(document.getElementById('chart-pop-compare'), songs)
}

/* ═══════════════════════════════════════════════════════════════════════════
   CTA 点击跳转
   ─── 用 data-target 属性指向目标 section id
   ═══════════════════════════════════════════════════════════════════════════ */
function bindCtaClicks() {
  document.querySelectorAll('.cta[data-target]').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.dataset.target)
      if (target) target.scrollIntoView({ behavior: 'smooth' })
    })
  })
}

/* ═══════════════════════════════════════════════════════════════════════════
   语言切换
   ═══════════════════════════════════════════════════════════════════════════ */
function bindLangSwitch() {
  const btn = document.getElementById('lang-btn')
  if (!btn) return
  btn.addEventListener('click', () => {
    currentLang = currentLang === 'zh_CN' ? 'zh_TW' : 'zh_CN'
    buildApp()
  })
}

/* ═══════════════════════════════════════════════════════════════════════════
   探索器：搜索、筛选、排序
   ─── 关键设计：renderExpTable 只做渲染，sortExpData 只做排序（不渲染），
       避免循环调用
   ═══════════════════════════════════════════════════════════════════════════ */

function initExplorer() {
  // 初始化数据
  expFiltered = [...songs]
  // 默认排序
  sortExpData()
  // 渲染初始表
  renderExpTable()
  // 绑定表头点击排序
  bindExpSortHeaders()
  // 绑定搜索和筛选
  bindExpFilters()
}

function bindExpFilters() {
  const search = document.getElementById('exp-search')
  const album = document.getElementById('exp-album')
  if (search) search.addEventListener('input', filterExp)
  if (album) album.addEventListener('change', filterExp)
}

function filterExp() {
  const q = ($('#exp-search')?.value || '').toLowerCase()
  const a = ($('#exp-album')?.value || '')
  expFiltered = songs.filter(s => {
    if (q && !s.name.toLowerCase().includes(q) && !s.album.toLowerCase().includes(q)) return false
    if (a && s.album !== a) return false
    return true
  })
  sortExpData()
  renderExpTable()
}

function bindExpSortHeaders() {
  document.querySelectorAll('.exp-table th[data-col]').forEach(th => {
    th.addEventListener('click', () => {
      const col = parseInt(th.dataset.col)
      if (expSort.col === col) {
        expSort.dir *= -1
      } else {
        // 清除旧排序样式
        document.querySelectorAll('.exp-table th.sorted').forEach(h => {
          h.classList.remove('sorted', 'asc', 'desc')
          const arrow = h.querySelector('.sort-arrow')
          if (arrow) arrow.textContent = ''
        })
        expSort.col = col
        expSort.dir = 1
      }
      // 更新样式
      th.classList.add('sorted', expSort.dir === 1 ? 'asc' : 'desc')
      const arrow = th.querySelector('.sort-arrow')
      if (arrow) arrow.textContent = expSort.dir === 1 ? '▲' : '▼'
      // 排序 & 渲染
      sortExpData()
      renderExpTable()
    })
  })
}

function sortExpData() {
  const col = expSort.col
  const dir = expSort.dir
  expFiltered.sort((a, b) => {
    let va, vb
    if (col === 0) { va = songs.indexOf(a); vb = songs.indexOf(b) }
    else if (col === 1) { va = a.name; vb = b.name }
    else if (col === 2) { va = a.album; vb = b.album }
    else if (col === 3) { va = a.year; vb = b.year }
    else if (col === 4) { va = a.popularity; vb = b.popularity }
    else {
      const f = EXP_FEATS[col - 5]
      va = a.feats[f]; vb = b.feats[f]
    }
    if (typeof va === 'string') return dir * va.localeCompare(vb, 'zh')
    return dir * (va - vb)
  })
}

function renderExpTable() {
  const body = document.getElementById('exp-body')
  const empty = document.getElementById('exp-empty')
  const count = document.getElementById('exp-count')
  if (!body) return

  const T = t()
  if (count) {
    count.textContent = expFiltered.length > 0
      ? T.expResult(expFiltered.length)
      : T.expNoResult
  }
  if (empty) {
    empty.style.display = expFiltered.length === 0 ? 'block' : 'none'
  }

  body.innerHTML = expFiltered.map((s, i) => `
    <tr class="exp-row" data-idx="${songs.indexOf(s)}">
      <td class="col-idx">${i + 1}</td>
      <td>${s.name}</td>
      <td>${s.album}</td>
      <td>${s.year}</td>
      <td><span class="pop-badge" style="--pop:${s.popularity / 100}">${s.popularity}</span></td>
      ${EXP_FEATS.map(f => `<td>${(s.feats[f] * 100).toFixed(0)}</td>`).join('')}
    </tr>
  `).join('')

  // 点击行跳转到推荐
  body.querySelectorAll('.exp-row').forEach(row => {
    row.addEventListener('click', () => {
      const idx = parseInt(row.dataset.idx)
      selectRec(idx)
    })
  })
}

/* ═══════════════════════════════════════════════════════════════════════════
   推荐系统
   ═══════════════════════════════════════════════════════════════════════════ */

function bindRecommender() {
  const btn = document.getElementById('rec-btn')
  const sel = document.getElementById('rec-select')
  if (btn) btn.addEventListener('click', doRec)
  if (sel) sel.addEventListener('change', doRec)

  // 方法标签切换
  document.querySelectorAll('.method-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.method-tab').forEach(t => t.classList.remove('active'))
      tab.classList.add('active')
      recMethod = tab.dataset.method
      doRec()
    })
  })
}

function doRec() {
  const sel = document.getElementById('rec-select')
  const idx = parseInt(sel?.value)
  const T = t()

  if (isNaN(idx) || idx < 0) {
    document.getElementById('rec-output').innerHTML = `
      <div class="rec-empty">${T.recNoSelect}</div>`
    return
  }
  recIdx = idx
  const song = songs[idx]
  const mat = recommender[recMethod]
  const sims = mat[idx]
    .map((v, i) => ({ idx: i, sim: v }))
    .filter(x => x.idx !== idx)
    .sort((a, b) => b.sim - a.sim)
    .slice(0, 10)

  const output = document.getElementById('rec-output')
  if (!output) return

  output.innerHTML = `
    <div class="rec-grid">
      <div class="rec-list-card">
        <div class="rec-list-title">${T.recTop10}</div>
        <div class="rec-list-body">
          ${sims.map((r, i) => {
            const rs = songs[r.idx]
            const pct = (r.sim * 100).toFixed(1)
            return `
              <div class="rec-item" data-idx="${r.idx}">
                <div class="rec-rank">${i + 1}</div>
                <div class="rec-info">
                  <div class="rec-name">${rs.name}</div>
                  <div class="rec-meta">${rs.album} · ${rs.year}</div>
                </div>
                <div class="rec-score">
                  <div class="rec-bar" style="width:${Math.min(pct, 100)}%"></div>
                  <span>${pct}%</span>
                </div>
              </div>`
          }).join('')}
        </div>
      </div>
      <div class="rec-chart-card">
        <div class="rec-list-title">${T.recCompare}</div>
        <div id="rec-radar" class="chart-sm"></div>
      </div>
    </div>`

  // 渲染雷达图
  const topSong = songs[sims[0].idx]
  renderRecRadar(document.getElementById('rec-radar'), song, topSong, FEATS)
}

function selectRec(idx) {
  const sel = document.getElementById('rec-select')
  if (sel) {
    sel.value = idx
    const sec = document.getElementById('recommender')
    if (sec) sec.scrollIntoView({ behavior: 'smooth' })
    setTimeout(doRec, 400)
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   数字滚动动画
   ═══════════════════════════════════════════════════════════════════════════ */
function initCountUp() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return
      const el = entry.target
      const target = parseFloat(el.dataset.count)
      const decimals = parseInt(el.dataset.decimals) || 0
      if (isNaN(target)) return
      const duration = 1200
      const start = performance.now()
      function step(now) {
        const progress = Math.min((now - start) / duration, 1)
        // ease-out
        const eased = 1 - Math.pow(1 - progress, 3)
        el.textContent = (target * eased).toFixed(decimals)
        if (progress < 1) requestAnimationFrame(step)
        else el.textContent = target.toFixed(decimals)
      }
      requestAnimationFrame(step)
      observer.unobserve(el)
    })
  }, { threshold: 0.5 })

  document.querySelectorAll('.stat-num[data-count]').forEach(el => observer.observe(el))
}

/* ═══════════════════════════════════════════════════════════════════════════
   滚动动画（IntersectionObserver）
   ═══════════════════════════════════════════════════════════════════════════ */
function initScrollAnim() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
        // 触发 staggered 子元素
        entry.target.querySelectorAll('.staggered').forEach(el => {
          el.classList.add('visible')
        })
      }
    })
  }, { threshold: 0.08 })

  document.querySelectorAll('.section-anim').forEach(el => observer.observe(el))

  // 导航栏滚动效果
  const nav = document.getElementById('nav')
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 80)
    }, { passive: true })
  }
}

/* ═══════════════════════════════════════════════════════════════════════════
   事件绑定汇总
   ═══════════════════════════════════════════════════════════════════════════ */
function bindEvents() {
  bindCtaClicks()
  bindLangSwitch()
  // 探索器的事件绑定在 initExplorer() 中完成
  bindRecommender()
}

/* ═══════════════════════════════════════════════════════════════════════════
   启动
   ═══════════════════════════════════════════════════════════════════════════ */
buildApp()
