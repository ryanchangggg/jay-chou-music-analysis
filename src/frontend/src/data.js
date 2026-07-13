import { t } from './i18n.js';

let albumsData = [];
let songsData = [];

const DATA_PREFIX = '/data';

export async function loadData() {
  try {
    const [albumsRes, songsRes] = await Promise.all([
      fetch(`${DATA_PREFIX}/albums.json`),
      fetch(`${DATA_PREFIX}/songs.json`)
    ]);
    albumsData = await albumsRes.json();
    songsData = await songsRes.json();
    return { albums: albumsData, songs: songsData };
  } catch (err) {
    console.error('Data load error:', err);
    return null;
  }
}

export function getAlbums() { return albumsData; }
export function getSongs() { return songsData; }

export function getYearlyAverages() {
  const yearMap = {};
  songsData.forEach(s => {
    const y = s.year;
    if (!yearMap[y]) yearMap[y] = { songs: [] };
    yearMap[y].songs.push(s);
  });
  return Object.keys(yearMap).sort().map(y => {
    const group = yearMap[y], n = group.songs.length;
    const avg = f => group.songs.reduce((s, g) => s + (g[f] || 0), 0) / n;
    return {
      year: parseInt(y), count: n,
      danceability: avg('danceability'), energy: avg('energy'),
      valence: avg('valence'), tempo: avg('tempo'),
      acousticness: avg('acousticness'), popularity: avg('popularity'),
    };
  });
}

export function getEraGroups() {
  const eras = [
    { label: 'evolution.era_early', min: 2000, max: 2003 },
    { label: 'evolution.era_golden', min: 2004, max: 2007 },
    { label: 'evolution.era_mid', min: 2008, max: 2012 },
    { label: 'evolution.era_recent', min: 2014, max: 2026 },
  ];
  return eras.map(era => {
    const s = songsData.filter(x => x.year >= era.min && x.year <= era.max);
    const n = s.length;
    const avg = f => s.reduce((a, b) => a + (b[f] || 0), 0) / n;
    return {
      label: era.label, min: era.min, max: era.max, count: n,
      danceability: avg('danceability'), energy: avg('energy'),
      valence: avg('valence'), tempo: avg('tempo'),
      acousticness: avg('acousticness'), popularity: avg('popularity'),
    };
  });
}

export function getOverallStats() {
  if (!songsData.length) return {};
  const n = songsData.length;
  const avg = f => songsData.reduce((s, g) => s + (g[f] || 0), 0) / n;
  return {
    songCount: n, albumCount: albumsData.length,
    yearMin: Math.min(...songsData.map(s => s.year)),
    yearMax: Math.max(...songsData.map(s => s.year)),
    avgPopularity: avg('popularity'), avgEnergy: avg('energy'),
    avgDanceability: avg('danceability'), avgValence: avg('valence'),
    avgTempo: avg('tempo'),
  };
}

export function getLyricsStats() {
  return {
    totalVocab: 2627, uniqueVocab: 1764, avgTokensPerSong: 16.3,
    avgSentiment: 0.808, positivePct: 56.5, neutralPct: 28.0, negativePct: 15.5,
    avgChars: 42, avgLines: 4.5, avgTTR: 0.944, sentimentValenceCorr: 0.116,
  };
}

export function getTopWords() {
  return [
    ['却', 26], ['想', 22], ['著', 18], ['世界', 14], ['谁', 13],
    ['爱', 13], ['走', 12], ['我们', 12], ['微笑', 12], ['里', 11],
    ['怎么', 9], ['多', 9], ['跟', 9], ['给', 8], ['中', 8],
    ['想要', 7], ['开始', 7], ['什么', 7], ['还是', 7], ['为什么', 7],
    ['时间', 7], ['知道', 7], ['一起', 6], ['没有', 6], ['不会', 6],
    ['真的', 6], ['如果', 6], ['不能', 6], ['那天', 5], ['因为', 5],
  ];
}

export function getLDATopics() {
  return [
    { id: 1, label: 'lyrics.topic1', desc: 'lyrics.topic1_desc', words: ['期待', '声音', '听见', '后面', '回来', '夏天', '那年', '微风', '走过', '雨中', '等待', '心跳'] },
    { id: 2, label: 'lyrics.topic2', desc: 'lyrics.topic2_desc', words: ['英雄', '长大', '风吹', '保护', '幸福', '一杯', '咖啡', '才能', '明白', '世界', '勇敢', '脚步'] },
    { id: 3, label: 'lyrics.topic3', desc: 'lyrics.topic3_desc', words: ['世界', '微笑', '想起', '感觉', '为什么', '一点', '这个', '不是', '眼泪', '忘记', '时候', '慢慢'] },
    { id: 4, label: 'lyrics.topic4', desc: 'lyrics.topic4_desc', words: ['我们', '还是', '泛黄', '墙上', '回忆', '身边', '天堂', '夏天', '那年', '一起', '故事', '日记'] },
    { id: 5, label: 'lyrics.topic5', desc: 'lyrics.topic5_desc', words: ['烦恼', '看不见', '妈妈', '眼泪', '快乐', '怎么', '不了', '思念', '阳光', '风筝', '单纯', '微笑'] },
    { id: 6, label: 'lyrics.topic6', desc: 'lyrics.topic6_desc', words: ['音乐', '女人', '甜蜜', '想念', '春天', '爱情', '笑脸', '节奏', '浪漫', '心跳', '拥抱', '缘分'] },
  ];
}

export function getTopicOverTime() {
  const raw = [
    [2000,.11,.28,.06,.22,.17,.17],[2001,.1,.2,.1,.2,.2,.2],[2002,.1,.1,.1,.4,.1,.2],
    [2003,.18,.09,.09,.27,.18,.18],[2004,.1,.1,.1,.2,.1,.4],[2005,.08,.17,.17,.17,.17,.25],
    [2006,.1,.1,.1,.3,.3,.1],[2007,.1,.1,.1,.3,.1,.3],[2008,.18,.09,.09,.18,.18,.27],
    [2010,.09,.09,.27,.18,.18,.18],[2011,.27,.09,.09,.18,.18,.18],[2012,.08,.17,.17,.17,.25,.17],
    [2014,.08,.17,.08,.25,.17,.25],[2016,.2,.1,.1,.1,.3,.2],[2022,.09,.18,.09,.27,.18,.18],
    [2026,.15,.15,.08,.23,.23,.15],
  ];
  return raw.map(([y, ...v]) => ({ year: y, topics: v }));
}

export function getEvolutionTrends() {
  return [
    { feature: 'danceability', slope: -0.0006, r2: 0.067, p: 0.3321, mean: 0.575, std: 0.104, range: '0.350-0.780', anovaF: 0.18, anovaP: 0.9113, eta2: 0.0031 },
    { feature: 'energy', slope: -0.0005, r2: 0.036, p: 0.4805, mean: 0.597, std: 0.126, range: '0.350-0.850', anovaF: 0.04, anovaP: 0.9909, eta2: 0.0006 },
    { feature: 'valence', slope: 0.0008, r2: 0.046, p: 0.4227, mean: 0.416, std: 0.135, range: '0.150-0.650', anovaF: 0.38, anovaP: 0.7684, eta2: 0.0066 },
    { feature: 'tempo', slope: -0.0698, r2: 0.076, p: 0.3022, mean: 83.678, std: 10.116, range: '66.000-120.000', anovaF: 0.22, anovaP: 0.8827, eta2: 0.0039 },
    { feature: 'acousticness', slope: -0.0003, r2: 0.004, p: 0.8246, mean: 0.429, std: 0.199, range: '0.080-0.800', anovaF: 0.18, anovaP: 0.9118, eta2: 0.0031 },
  ];
}
