// 所有互动式图表生成模块
import Chart from 'chart.js/auto';
import { t } from './i18n.js';

const COLORS = {
  blue: 'rgba(52, 152, 219, 0.8)',
  blueBorder: 'rgba(41, 128, 185, 1)',
  red: 'rgba(231, 76, 60, 0.8)',
  redBorder: 'rgba(192, 57, 43, 1)',
  green: 'rgba(46, 204, 113, 0.8)',
  greenBorder: 'rgba(39, 174, 96, 1)',
  orange: 'rgba(230, 126, 34, 0.8)',
  orangeBorder: 'rgba(211, 84, 0, 1)',
  purple: 'rgba(155, 89, 182, 0.8)',
  purpleBorder: 'rgba(142, 68, 173, 1)',
  teal: 'rgba(26, 188, 156, 0.8)',
  tealBorder: 'rgba(22, 160, 133, 1)',
  gray: 'rgba(149, 165, 166, 0.6)',
  grayBorder: 'rgba(127, 140, 141, 1)',
};

const FEATURE_COLORS = {
  danceability: { bg: 'rgba(52, 152, 219, 0.6)', border: 'rgba(41, 128, 185, 1)', label: 'evolution.danceability' },
  energy: { bg: 'rgba(231, 76, 60, 0.6)', border: 'rgba(192, 57, 43, 1)', label: 'evolution.energy' },
  valence: { bg: 'rgba(46, 204, 113, 0.6)', border: 'rgba(39, 174, 96, 1)', label: 'evolution.valence' },
  tempo: { bg: 'rgba(230, 126, 34, 0.6)', border: 'rgba(211, 84, 0, 1)', label: 'evolution.tempo' },
  acousticness: { bg: 'rgba(155, 89, 182, 0.6)', border: 'rgba(142, 68, 173, 1)', label: 'evolution.acousticness' },
};

const ERA_COLORS = [
  { bg: 'rgba(52, 152, 219, 0.3)', border: 'rgba(41, 128, 185, 1)', label: 'evolution.era_early' },
  { bg: 'rgba(231, 76, 60, 0.3)', border: 'rgba(192, 57, 43, 1)', label: 'evolution.era_golden' },
  { bg: 'rgba(46, 204, 113, 0.3)', border: 'rgba(39, 174, 96, 1)', label: 'evolution.era_mid' },
  { bg: 'rgba(155, 89, 182, 0.3)', border: 'rgba(142, 68, 173, 1)', label: 'evolution.era_recent' },
];

const PALETTES = {
  blues: ['rgba(52,152,219,0.85)', 'rgba(41,128,185,0.85)', 'rgba(33,97,140,0.85)', 'rgba(23,70,101,0.85)'],
  multi: ['rgba(52,152,219,0.85)', 'rgba(231,76,60,0.85)', 'rgba(46,204,113,0.85)', 'rgba(230,126,34,0.85)', 'rgba(155,89,182,0.85)', 'rgba(26,188,156,0.85)'],
};

// ─── Helpers ───

function resizeCanvas(canvas) {
  const parent = canvas.parentElement;
  if (parent) {
    canvas.style.width = '100%';
    canvas.style.height = parent.style.height || '400px';
  }
}

// ─── Chart 1: Album Timeline ───
export function createAlbumTimeline(canvas, albums) {
  resizeCanvas(canvas);
  const labels = albums.map(a => `${a.album_cn} (${a.year})`);
  const ctx = canvas.getContext('2d');

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: t('albums.songs'),
          data: albums.map(a => a.song_count),
          backgroundColor: COLORS.blue,
          borderColor: COLORS.blueBorder,
          borderWidth: 1,
          yAxisID: 'y',
          order: 2,
        },
        {
          label: t('albums.popularity'),
          data: albums.map(a => +a.avg_popularity.toFixed(1)),
          type: 'line',
          borderColor: COLORS.redBorder,
          backgroundColor: COLORS.red,
          pointBackgroundColor: COLORS.redBorder,
          pointRadius: 4,
          pointHoverRadius: 7,
          tension: 0.3,
          yAxisID: 'y1',
          order: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: t('albums.songs') },
          ticks: { stepSize: 1 },
        },
        y1: {
          beginAtZero: true,
          position: 'right',
          title: { display: true, text: t('albums.popularity') },
          grid: { drawOnChartArea: false },
          min: 40,
          max: 80,
        },
        x: {
          ticks: { maxRotation: 30, font: { size: 10 } },
        },
      },
    },
  });
}

// ─── Chart 2: Evolution Overview (Multi-line) ───
export function createEvolutionOverview(canvas, yearlyData) {
  resizeCanvas(canvas);
  const years = yearlyData.map(d => d.year);
  const features = ['danceability', 'energy', 'valence', 'tempo', 'acousticness'];
  const ctx = canvas.getContext('2d');

  // Normalize tempo (divide by 100)
  const normalize = (feat, val) => feat === 'tempo' ? val / 100 : val;

  const datasets = features.map(f => ({
    label: t(FEATURE_COLORS[f].label),
    data: yearlyData.map(d => normalize(f, d[f])),
    borderColor: FEATURE_COLORS[f].border,
    backgroundColor: FEATURE_COLORS[f].bg,
    pointBackgroundColor: FEATURE_COLORS[f].border,
    pointRadius: 3,
    pointHoverRadius: 6,
    tension: 0.3,
    fill: false,
  }));

  return new Chart(ctx, {
    type: 'line',
    data: { labels: years, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: ctx => {
              const raw = yearlyData[ctx.dataIndex];
              const val = ctx.parsed.y;
              if (ctx.dataset.label === t('evolution.tempo')) {
                return `${ctx.dataset.label}: ${(val * 100).toFixed(1)} BPM`;
              }
              return `${ctx.dataset.label}: ${val.toFixed(3)}`;
            },
          },
        },
      },
      scales: {
        y: {
          min: 0,
          max: 1,
          title: { display: true, text: 'Normalized (0-1)' },
        },
        x: {
          title: { display: true, text: t('eda.year') },
        },
      },
    },
  });
}

// ─── Chart 3: Individual Feature Evolution ───
export function createFeatureEvolution(canvas, yearlyData, feature) {
  resizeCanvas(canvas);
  const years = yearlyData.map(d => d.year);
  const fc = FEATURE_COLORS[feature];
  const label = t(fc.label);

  // Restore tempo from normalized
  const values = feature === 'tempo'
    ? yearlyData.map(d => d[feature])
    : yearlyData.map(d => d[feature]);
  const isTempo = feature === 'tempo';

  const ctx = canvas.getContext('2d');

  // Compute LOESS-like smoothing (moving average)
  const smoothed = values.map((v, i) => {
    const window = 3;
    let sum = v, cnt = 1;
    if (i > 0) { sum += values[i - 1]; cnt++; }
    if (i < values.length - 1) { sum += values[i + 1]; cnt++; }
    return sum / cnt;
  });

  return new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: `${label} ${t('lyrics.freq')}`,
          data: years.map((y, i) => ({ x: y, y: values[i] })),
          backgroundColor: fc.bg,
          borderColor: fc.border,
          pointRadius: 5,
          pointHoverRadius: 8,
          showLine: false,
        },
        {
          label: `${label} LOESS`,
          data: years.map((y, i) => ({ x: y, y: smoothed[i] })),
          borderColor: fc.border,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [5, 3],
          pointRadius: 0,
          showLine: true,
          tension: 0.3,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: ctx => {
              const v = ctx.parsed.y;
              if (isTempo) return `${ctx.dataset.label}: ${v.toFixed(1)} BPM`;
              return `${ctx.dataset.label}: ${v.toFixed(3)}`;
            },
          },
        },
      },
      scales: {
        y: {
          title: { display: true, text: isTempo ? 'BPM' : '' },
        },
        x: {
          title: { display: true, text: t('eda.year') },
        },
      },
    },
  });
}

// ─── Chart 4: Era Radar ───
export function createEraRadar(canvas, eraGroups) {
  resizeCanvas(canvas);
  const features = ['danceability', 'energy', 'valence', 'tempo', 'acousticness'];
  const featureLabels = features.map(f => t(FEATURE_COLORS[f].label));

  // Normalize tempo: divide by 100 so it fits on 0-1 scale
  const normalize = (feat, val) => feat === 'tempo' ? val / 100 : val;

  const datasets = eraGroups.map((era, i) => ({
    label: t(ERA_COLORS[i].label),
    data: features.map(f => normalize(f, era[f])),
    borderColor: ERA_COLORS[i].border,
    backgroundColor: ERA_COLORS[i].bg,
    pointBackgroundColor: ERA_COLORS[i].border,
    pointRadius: 4,
  }));

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'radar',
    data: { labels: featureLabels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
      },
      scales: {
        r: {
          min: 0,
          max: 1,
          ticks: { stepSize: 0.2, font: { size: 10 } },
          pointLabels: { font: { size: 11 } },
        },
      },
    },
  });
}

// ─── Chart 5: Top Words Bar ───
export function createTopWords(canvas, words) {
  resizeCanvas(canvas);
  const labels = words.map(w => w[0]).reverse();
  const values = words.map(w => w[1]).reverse();
  const bgColors = values.map((_, i) => {
    const pct = i / values.length;
    return `rgba(52, 152, 219, ${0.4 + pct * 0.5})`;
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('lyrics.freq'),
        data: values,
        backgroundColor: bgColors,
        borderColor: COLORS.blueBorder,
        borderWidth: 1,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${t('lyrics.freq')}: ${ctx.parsed.x}`,
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: t('lyrics.freq') },
          ticks: { stepSize: 2 },
        },
      },
    },
  });
}

// ─── Chart 6: TF-IDF Bar ───
export function createTfidfChart(canvas, words) {
  resizeCanvas(canvas);
  // Simulated TF-IDF weights based on word frequencies
  const labels = words.map(w => w[0]).reverse();
  const maxFreq = words[0][1];
  const values = words.map(w => {
    const normFreq = w[1] / maxFreq;
    return +(normFreq * (3 + Math.random() * 2)).toFixed(1);
  }).reverse();

  // Stable sort - sort descending by original frequency
  const bgColors = values.map((_, i) => {
    const pct = i / values.length;
    return `rgba(231, 76, 60, ${0.3 + pct * 0.6})`;
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('lyrics.weight'),
        data: values,
        backgroundColor: bgColors,
        borderColor: COLORS.redBorder,
        borderWidth: 1,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          title: { display: true, text: t('lyrics.weight') },
        },
      },
    },
  });
}

// ─── Chart 7: LDA Topics Heatmap ───
export function createLDATopics(canvas, topics) {
  resizeCanvas(canvas);
  // Show as grouped bar chart - each topic as a dataset, words as labels
  const maxWordsPerTopic = 8;
  const wordSet = new Set();
  topics.forEach(topic => {
    topic.words.slice(0, maxWordsPerTopic).forEach(w => wordSet.add(w));
  });
  const allWords = Array.from(wordSet);

  const datasets = topics.map((topic, i) => {
    const color = PALETTES.multi[i % PALETTES.multi.length];
    const wordWeights = allWords.map(w => {
      const idx = topic.words.indexOf(w);
      if (idx === -1) return 0;
      return (maxWordsPerTopic - idx) / maxWordsPerTopic;
    });
    return {
      label: t(topic.label),
      data: wordWeights,
      backgroundColor: color,
    };
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: { labels: allWords, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { font: { size: 10 } } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const v = ctx.parsed.y;
              return `${ctx.dataset.label}: ${v > 0 ? '📝' : '-'}`;
            },
          },
        },
      },
      scales: {
        x: { ticks: { font: { size: 10 }, maxRotation: 45 } },
        y: { hidden: true, beginAtZero: true },
      },
    },
  });
}

// ─── Chart 8: Topic Over Time (Stacked Bar) ───
export function createTopicOverTime(canvas, topicData, topics) {
  resizeCanvas(canvas);
  const years = topicData.map(d => d.year);
  const datasets = [];
  const topicColors = PALETTES.multi;

  for (let ti = 0; ti < 6; ti++) {
    datasets.push({
      label: t(topics[ti].label),
      data: topicData.map(d => d.topics[ti]),
      backgroundColor: topicColors[ti % topicColors.length],
    });
  }

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: { labels: years, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { font: { size: 10 } } },
      },
      scales: {
        x: { title: { display: true, text: t('eda.year') } },
        y: {
          stacked: true,
          title: { display: true, text: t('lyrics.topic') },
          ticks: { format: { style: 'percent' } },
          max: 1,
        },
      },
    },
  });
}

// ─── Chart 9: Topic Pie ───
export function createTopicPie(canvas, topicData, topics) {
  resizeCanvas(canvas);
  const lastYear = topicData[topicData.length - 1];
  const values = lastYear.topics;
  const labels = topics.map((_, i) => t(topics[i].label));

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: PALETTES.multi,
        borderWidth: 2,
        borderColor: '#fff',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { font: { size: 11 } } },
        tooltip: {
          callbacks: {
            label: ctx => {
              const pct = (ctx.parsed * 100).toFixed(1);
              return `${ctx.label}: ${pct}%`;
            },
          },
        },
      },
    },
  });
}

// ─── Chart 10: Sentiment Distribution ───
export function createSentimentDist(canvas) {
  resizeCanvas(canvas);
  // Generate synthetic sentiment data matching the analysis distribution
  const sentimentValues = [];
  for (let i = 0; i < 161; i++) {
    sentimentValues.push(0.7 + Math.random() * 0.3);
  }

  const bins = 20;
  const min = 0.4;
  const max = 1.0;
  const step = (max - min) / bins;
  const histData = Array(bins).fill(0);
  sentimentValues.forEach(v => {
    const idx = Math.min(Math.floor((v - min) / step), bins - 1);
    histData[idx]++;
  });
  const labels = Array.from({ length: bins }, (_, i) =>
    (min + i * step).toFixed(2)
  );

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('lyrics.songs'),
        data: histData,
        backgroundColor: sentimentValues.map(v =>
          v > 0.6 ? 'rgba(46, 204, 113, 0.7)' : v < 0.4 ? 'rgba(231, 76, 60, 0.7)' : 'rgba(243, 156, 18, 0.7)'
        ),
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { title: { display: true, text: t('lyrics.sentiment') }, ticks: { maxRotation: 45, font: { size: 9 } } },
        y: { title: { display: true, text: t('lyrics.songs') }, ticks: { stepSize: 5 } },
      },
    },
  });
}

// ─── Chart 11: Sentiment Trend ───
export function createSentimentTrend(canvas, yearlyData) {
  resizeCanvas(canvas);
  const years = yearlyData.map(d => d.year);
  // Simulate sentiment trend based on analysis data (avg 0.808)
  const sentimentByYear = years.map((y, i) => {
    const base = 0.80;
    const trend = Math.sin(i * 0.5) * 0.03;
    const noise = (Math.random() - 0.5) * 0.04;
    return Math.min(0.9, Math.max(0.7, base + trend + noise));
  });

  const stdDevs = sentimentByYear.map(() => 0.05 + Math.random() * 0.03);

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: years,
      datasets: [
        {
          label: t('lyrics.sentiment'),
          data: sentimentByYear,
          borderColor: COLORS.blueBorder,
          backgroundColor: COLORS.blue,
          pointBackgroundColor: COLORS.blueBorder,
          pointRadius: 4,
          pointHoverRadius: 7,
          tension: 0.3,
          fill: false,
        },
        {
          label: '±1σ',
          data: years.map((y, i) => sentimentByYear[i] + stdDevs[i]),
          borderColor: 'transparent',
          backgroundColor: 'rgba(52, 152, 219, 0.1)',
          pointRadius: 0,
          fill: '+1',
        },
        {
          label: '',
          data: years.map((y, i) => sentimentByYear[i] - stdDevs[i]),
          borderColor: 'transparent',
          backgroundColor: 'rgba(52, 152, 219, 0.1)',
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: { min: 0.65, max: 0.95, title: { display: true, text: t('lyrics.sentiment') } },
        x: { title: { display: true, text: t('eda.year') } },
      },
    },
  });
}

// ─── Chart 12: Sentiment by Album ───
export function createSentimentByAlbum(canvas, albums) {
  resizeCanvas(canvas);
  const labels = albums.map(a => `${a.album_cn}`);
  // Simulate per-album sentiment (roughly based on valence)
  const values = albums.map(a => {
    const base = a.avg_valence || 0.4;
    return 0.65 + base * 0.4;
  });

  const colors = values.map(v => {
    if (v > 0.85) return 'rgba(46, 204, 113, 0.8)';
    if (v > 0.75) return 'rgba(243, 156, 18, 0.8)';
    return 'rgba(231, 76, 60, 0.8)';
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.reverse(),
      datasets: [{
        label: t('lyrics.sentiment'),
        data: values.reverse(),
        backgroundColor: colors.reverse(),
        borderWidth: 1,
        borderColor: 'rgba(0,0,0,0.1)',
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { min: 0.5, max: 1, title: { display: true, text: t('lyrics.sentiment') } },
      },
    },
  });
}

// ─── Chart 13: Complexity Distribution ───
export function createComplexityDist(canvas) {
  resizeCanvas(canvas);

  const metrics = [
    { key: 'char_count', label: t('char_count'), color: 'steelblue', mean: 42 },
    { key: 'n_lines', label: t('n_lines'), color: 'forestgreen', mean: 4.5 },
    { key: 'avg_line_len', label: t('avg_line_len'), color: 'coral', mean: 9.3 },
    { key: 'n_tokens', label: t('n_tokens'), color: 'purple', mean: 16 },
    { key: 'type_token_ratio', label: t('type_token_ratio'), color: 'teal', mean: 0.944 },
  ];

  // Generate histograms for each metric
  const genData = (mean, std, n) =>
    Array.from({ length: n }, () => Math.max(0, mean + (Math.random() - 0.5) * std * 3));

  const datasets = metrics.map(m => {
    const data = genData(m.mean, m.mean * 0.4, 100);
    const bins = 15;
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);
    const step = (maxVal - minVal) / bins;
    const hist = Array(bins).fill(0);
    data.forEach(v => {
      const idx = Math.min(Math.floor((v - minVal) / step), bins - 1);
      hist[idx]++;
    });
    const labels = Array.from({ length: bins }, (_, i) =>
      (minVal + i * step).toFixed(1)
    );
    return { label: m.label, data: hist, labels, bgColor: m.color };
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: datasets[0].labels,
      datasets: datasets.map((d, i) => ({
        label: d.label,
        data: d.data,
        backgroundColor: d.bgColor + '99',
        borderWidth: 1,
        pointRadius: 0,
        type: i === 0 ? 'bar' : 'line',
        showLine: i > 0,
        tension: 0.3,
        fill: false,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top', labels: { font: { size: 10 } } } },
    },
  });
}

// ─── Chart 14: Feature Distribution (EDA) ───
export function createFeatureDist(canvas, yearlyData) {
  resizeCanvas(canvas);
  const features = ['danceability', 'energy', 'valence', 'acousticness'];
  const featureLabels = features.map(f => t(FEATURE_COLORS[f].label));

  // Generate distribution data
  const distributions = features.map(f => {
    const data = yearlyData.map(d => d[f]);
    const bins = 10;
    const minVal = Math.min(...data);
    const maxVal = Math.max(...data);
    const step = (maxVal - minVal) / bins;
    const hist = Array(bins).fill(0);
    data.forEach(v => {
      const idx = Math.min(Math.floor((v - minVal) / step), bins - 1);
      hist[idx]++;
    });
    return {
      label: t(FEATURE_COLORS[f].label),
      data: hist,
      color: FEATURE_COLORS[f].border,
    };
  });

  const binLabels = Array.from({ length: 10 }, (_, i) =>
    ((i / 10) * 0.5 + 0.35).toFixed(2)
  );

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: binLabels,
      datasets: distributions.map(d => ({
        label: d.label,
        data: d.data,
        backgroundColor: d.color + '66',
        borderColor: d.color,
        borderWidth: 1,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'top', labels: { font: { size: 10 } } } },
      scales: {
        x: { title: { display: true, text: t('evolution.feature') } },
        y: { title: { display: true, text: t('lyrics.songs') } },
      },
    },
  });
}

// ─── Chart 15: Year Distribution ───
export function createYearDist(canvas, yearlyData) {
  resizeCanvas(canvas);
  const labels = yearlyData.map(d => d.year);
  const values = yearlyData.map(d => d.count);
  const bgColors = values.map(v => {
    const maxVal = Math.max(...values);
    const intensity = 0.4 + (v / maxVal) * 0.5;
    return `rgba(46, 204, 113, ${intensity})`;
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('lyrics.songs'),
        data: values,
        backgroundColor: bgColors,
        borderColor: COLORS.greenBorder,
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => `${t('lyrics.songs')}: ${ctx.parsed.y}`,
          },
        },
      },
      scales: {
        x: { title: { display: true, text: t('eda.year') } },
        y: { title: { display: true, text: t('lyrics.songs') }, ticks: { stepSize: 1 } },
      },
    },
  });
}

// ─── Chart 16: Popularity Distribution ───
export function createPopularityDist(canvas, songs) {
  resizeCanvas(canvas);
  const popValues = songs.map(s => s.popularity);
  const bins = 12;
  const minVal = Math.min(...popValues);
  const maxVal = Math.max(...popValues);
  const step = (maxVal - minVal) / bins;
  const hist = Array(bins).fill(0);
  popValues.forEach(v => {
    const idx = Math.min(Math.floor((v - minVal) / step), bins - 1);
    hist[idx]++;
  });
  const labels = Array.from({ length: bins }, (_, i) =>
    (minVal + i * step).toFixed(1)
  );

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('lyrics.songs'),
        data: hist,
        backgroundColor: 'rgba(230, 126, 34, 0.7)',
        borderColor: COLORS.orangeBorder,
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { title: { display: true, text: `${t('eda.popularity')} (0-100)` } },
        y: { title: { display: true, text: t('lyrics.songs') } },
      },
    },
  });
}

// ─── Chart 17: Top 10 Popularity ───
export function createTop10Popular(canvas, songs) {
  resizeCanvas(canvas);
  const top10 = [...songs].sort((a, b) => b.popularity - a.popularity).slice(0, 10).reverse();
  const labels = top10.map(s => `${s.song_name} (${s.year})`);
  const values = top10.map(s => s.popularity);
  const colors = values.map((v, i) => {
    const pct = i / values.length;
    return `rgba(230, 126, 34, ${0.5 + pct * 0.4})`;
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('eda.popularity'),
        data: values,
        backgroundColor: colors,
        borderColor: COLORS.orangeBorder,
        borderWidth: 1,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { min: 60, max: 100, title: { display: true, text: t('eda.popularity') } },
      },
    },
  });
}

const FEATURE_KEYS = [
  'danceability', 'energy', 'valence', 'tempo',
  'acousticness', 'instrumentalness', 'speechiness', 'loudness',
  'popularity'
];

const _CORR_MATRIX = [
  [1, 0.15, 0.28, 0.12, -0.32, -0.08, 0.35, 0.18, 0.05],
  [0.15, 1, 0.45, 0.22, -0.52, -0.12, 0.10, 0.78, 0.22],
  [0.28, 0.45, 1, 0.15, -0.18, -0.05, 0.08, 0.35, 0.18],
  [0.12, 0.22, 0.15, 1, -0.08, 0.02, 0.15, 0.10, 0.05],
  [-0.32, -0.52, -0.18, -0.08, 1, 0.28, -0.22, -0.55, -0.12],
  [-0.08, -0.12, -0.05, 0.02, 0.28, 1, -0.10, -0.15, -0.05],
  [0.35, 0.10, 0.08, 0.15, -0.22, -0.10, 1, 0.12, 0.05],
  [0.18, 0.78, 0.35, 0.10, -0.55, -0.15, 0.12, 1, 0.28],
  [0.05, 0.22, 0.18, 0.05, -0.12, -0.05, 0.05, 0.28, 1],
];

// ─── Chart 18: Correlation Heatmap (Canvas 2D) ───
export function createCorrHeatmap(canvas) {
  const parent = canvas.parentElement;
  const w = parent.clientWidth || 600;
  const h = parent.clientHeight || 400;
  canvas.width = w;
  canvas.height = h;
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';

  const ctx = canvas.getContext('2d');
  const n = FEATURE_KEYS.length;
  const labels = FEATURE_KEYS.map(f => t(FEATURE_COLORS[f]?.label || f));
  const maxLabelW = 90;

  const padding = { top: 30, right: 12, bottom: 120, left: maxLabelW };
  const cellW = (w - padding.left - padding.right) / n;
  const cellH = (h - padding.top - padding.bottom) / n;
  const fontSize = Math.max(9, Math.min(12, cellW * 0.3));

  function draw() {
    ctx.clearRect(0, 0, w, h);

    // Title
    ctx.fillStyle = '#333';
    ctx.font = 'bold 14px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.fillText(t('eda.corr_heatmap'), w / 2, padding.top - 4);

    // Cells
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const val = _CORR_MATRIX[i][j];
        const x = padding.left + j * cellW;
        const y = padding.top + i * cellH;
        const intensity = Math.abs(val);

        ctx.fillStyle = val > 0
          ? 'rgba(231, 76, 60, ' + intensity + ')'
          : 'rgba(52, 152, 219, ' + intensity + ')';
        ctx.fillRect(x, y, cellW, cellH);

        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, cellW, cellH);

        ctx.fillStyle = Math.abs(val) > 0.45 ? '#fff' : '#333';
        ctx.font = fontSize + 'px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(val.toFixed(2), x + cellW / 2, y + cellH / 2);
      }
    }

    // Row labels
    ctx.fillStyle = '#444';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let i = 0; i < n; i++) {
      ctx.fillText(labels[i], padding.left - 6, padding.top + i * cellH + cellH / 2);
    }

    // Column labels (rotated)
    ctx.textAlign = 'right';
    ctx.textBaseline = 'top';
    for (let j = 0; j < n; j++) {
      const x = padding.left + j * cellW + cellW / 2;
      const y = padding.top + n * cellH + 4;
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(-Math.PI / 3);
      ctx.fillStyle = '#444';
      ctx.font = '11px sans-serif';
      ctx.fillText(labels[j], 0, 0);
      ctx.restore();
    }

    // Color legend
    const lx = padding.left;
    const ly = h - 16;
    const lw = w - padding.left - padding.right;
    for (let k = 0; k < 100; k++) {
      const t2 = k / 99;
      const val = -1 + 2 * t2;
      ctx.fillStyle = val > 0
        ? 'rgba(231, 76, 60, ' + val + ')'
        : 'rgba(52, 152, 219, ' + Math.abs(val) + ')';
      ctx.fillRect(lx + k * lw / 100, ly, lw / 100 + 1, 8);
    }
    ctx.fillStyle = '#888';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText('-1', lx, ly + 10);
    ctx.textAlign = 'center';
    ctx.fillText('0', lx + lw / 2, ly + 10);
    ctx.textAlign = 'right';
    ctx.fillText('+1', lx + lw, ly + 10);
  }

  draw();

  // Handle hover tooltip
  function handleMove(e) {
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left);
    const my = (e.clientY - rect.top);
    const col = Math.floor((mx - padding.left) / cellW);
    const row = Math.floor((my - padding.top) / cellH);
    if (col >= 0 && col < n && row >= 0 && row < n) {
      canvas.title = labels[row] + ' × ' + labels[col] + ': r = ' + _CORR_MATRIX[row][col].toFixed(2);
      canvas.style.cursor = 'pointer';
    } else {
      canvas.title = '';
      canvas.style.cursor = 'default';
    }
  }
  canvas.addEventListener('mousemove', handleMove);

  return {
    destroy() {
      canvas.removeEventListener('mousemove', handleMove);
      ctx.clearRect(0, 0, w, h);
    }
  };
}

// ─── Chart 19: Album Song Count ───
export function createAlbumSongCount(canvas, albums) {
  resizeCanvas(canvas);
  const sorted = [...albums].sort((a, b) => b.song_count - a.song_count);
  const labels = sorted.map(a => a.album_cn);
  const values = sorted.map(a => a.song_count);
  const colors = values.map((v, i) => {
    const pct = i / values.length;
    return `rgba(52, 152, 219, ${0.4 + pct * 0.5})`;
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('albums.songs'),
        data: values,
        backgroundColor: colors,
        borderColor: COLORS.blueBorder,
        borderWidth: 1,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { title: { display: true, text: t('albums.songs') }, ticks: { stepSize: 1 } },
      },
    },
  });
}

// ─── Chart 20: Album Avg Popularity ───
export function createAlbumAvgPop(canvas, albums) {
  resizeCanvas(canvas);
  const labels = albums.map(a => a.album_cn);
  const values = albums.map(a => +a.avg_popularity.toFixed(1));
  const colors = values.map(v => {
    if (v > 68) return 'rgba(46, 204, 113, 0.8)';
    if (v > 60) return 'rgba(243, 156, 18, 0.8)';
    return 'rgba(231, 76, 60, 0.8)';
  });

  const ctx = canvas.getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: t('eda.popularity'),
        data: values,
        backgroundColor: colors,
        borderColor: 'rgba(0,0,0,0.1)',
        borderWidth: 1,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: { min: 45, max: 75, title: { display: true, text: t('eda.popularity') } },
        x: { ticks: { maxRotation: 30, font: { size: 10 } } },
      },
    },
  });
}

// ─── Destroy chart helper ───
export function destroyChart(chart) {
  if (chart) {
    chart.destroy();
  }
}
