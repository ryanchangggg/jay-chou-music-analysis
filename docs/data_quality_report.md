# Data Quality Report — Jay Chou Music Deep Analysis

**Generated**: 2026-07-12  
**Source**: Preprocessing pipeline (`src/python/preprocess.py`)  
**Output**: `data/processed/jay_music_dataset.csv`

---

## 1. Encoding

All 6 raw CSV files are **UTF-8 (no BOM)** — no encoding conversion needed.

| File | Encoding |
|------|----------|
| `jay_discography.csv` | UTF-8 (no BOM) |
| `spotify_features.csv` | UTF-8 (no BOM) |
| `lyrics.csv` | UTF-8 (no BOM) |
| `album_covers.csv` | UTF-8 (no BOM) |
| `song_tags.csv` | UTF-8 (no BOM) |
| `jay_chou_master_dataset.csv` | UTF-8 (no BOM) |

## 2. Dataset Overview

| Source | Rows | Columns |
|--------|------|---------|
| discography | 174 | 7 |
| spotify_features | 174 | 14 |
| lyrics | 174 | 3 |
| album_covers | 16 | 3 |
| song_tags | 228 | 2 |

## 3. Duplicate Song Names

| Source | Unique | Duplicates | Notes |
|--------|--------|------------|-------|
| discography | 174 / 174 | 0 | Clean |
| spotify_features | 174 / 174 | 0 | Clean |
| lyrics | 174 / 174 | 0 | Clean |
| song_tags | 174 / 228 | 54 | **Expected** — long format (multiple tags per song) |

## 4. Song Name Consistency

- **Common across all sources**: 174 songs
- **Total unique names**: 174
- **No name mismatches** across any source file.
- Song names use consistent Chinese characters across all files.

## 5. Missing Values

| Source | Column | Missing | Rate |
|--------|--------|---------|------|
| lyrics | lyrics | 13 | 7.5% |

13 songs have no lyrics text (instrumental or unavailable). All other columns are complete.

## 6. Output Dataset

| Metric | Value |
|--------|-------|
| File | `data/processed/jay_music_dataset.csv` |
| Format | CSV (UTF-8 BOM for Excel compatibility) + JSON |
| Rows | 174 |
| Columns | 26 |
| File size | 65 KB |

### Columns

| # | Column | Type | Description |
|---|--------|------|-------------|
| 1 | `song_name` | str | Song title (Chinese) |
| 2 | `album_cn` | str | Album name (Chinese) |
| 3 | `album_en` | str | Album name (English) |
| 4 | `track_number` | int | Track position on album |
| 5 | `release_date` | str | Release date (YYYY-MM-DD) |
| 6 | `composer` | str | Composer (all 周杰伦) |
| 7 | `lyricist` | str | Lyricist name |
| 8 | `danceability` | float | Spotify audio feature [0,1] |
| 9 | `energy` | float | Spotify audio feature [0,1] |
| 10 | `valence` | float | Spotify audio feature [0,1] |
| 11 | `tempo` | int | Beats per minute |
| 12 | `acousticness` | float | Spotify audio feature [0,1] |
| 13 | `instrumentalness` | float | Spotify audio feature [0,1] |
| 14 | `speechiness` | float | Spotify audio feature [0,1] |
| 15 | `loudness` | float | Decibels (dB) |
| 16 | `key` | int | Pitch class (0=C, 1=C#, ...) |
| 17 | `duration_ms` | int | Duration in milliseconds |
| 18 | `popularity` | int | Spotify popularity [0,100] |
| 19 | `mode` | int | Musical mode (0=minor, 1=major) |
| 20 | `play_count_est` | int | Estimated play count |
| 21 | `lyrics` | str | Full lyrics text (13 nulls) |
| 22 | `source` | str | Lyrics source label |
| 23 | `tags` | str | Pipe-separated style tags |
| 24 | `album_cn_cov` | str | Album name (Chinese, from covers) |
| 25 | `cover_url` | str | Album cover image URL |
| 26 | `year` | int | Extracted release year |

## 7. Key Statistics

| Metric | Value |
|--------|-------|
| Total songs | 174 |
| Total albums | 16 |
| Year range | 2000 — 2026 |
| Songs with lyrics | 161 (92.5%) |
| Songs with tags | 174 (100.0%) |
| Unique lyricists | 14 |
| Unique composers | 2 (周杰伦 + 1 other) |
| Tag categories | 10 |
| Major key songs | 112 (64.4%) |

### Audio Feature Ranges

| Feature | Min | Max | Mean |
|---------|-----|-----|------|
| danceability | 0.350 | 0.780 | 0.575 |
| energy | 0.350 | 0.850 | 0.597 |
| valence | 0.150 | 0.650 | 0.416 |
| tempo | 66.0 | 120.0 | 83.7 |
| acousticness | 0.080 | 0.800 | 0.429 |
| instrumentalness | 0.001 | 0.050 | 0.005 |
| speechiness | 0.020 | 0.350 | 0.083 |
| loudness | -9.200 | -3.500 | -6.633 |
| popularity | 45.0 | 88.0 | 63.5 |
| duration_ms | 170,000 | 335,000 | 265,471 |

### Albums in Collection

| Year | Album | Songs |
|------|-------|-------|
| 2000 | Jay (杰伦) | 10 |
| 2001 | Fantasy (范特西) | 10 |
| 2002 | The Eight Dimensions (八度空间) | 10 |
| 2003 | Ye Huimei (叶惠美) | 11 |
| 2004 | Common Jasmine Orange (七里香) | 10 |
| 2005 | November's Chopin (11月的萧邦) | 12 |
| 2006 | Still Fantasy (依然范特西) | 10 |
| 2007 | On the Run (我很忙) | 10 |
| 2008 | Capricorn (魔杰座) | 11 |
| 2010 | The Era (跨时代) | 11 |
| 2011 | Exclamation Point (惊叹号) | 11 |
| 2012 | Opus 12 (12新作) | 12 |
| 2014 | Aiyo, Not Bad (哎呦，不错哦) | 12 |
| 2016 | Jay Chou's Bedtime Stories (周杰伦的床边故事) | 10 |
| 2022 | Greatest Works of Art (最伟大的作品) | 11 |
| 2026 | Children of the Sun (太阳之子) | 13 |

## 8. Data Quality Flags

**No data quality issues detected.**

- All numeric features within expected ranges
- No duplicate songs in merged output
- All song names consistent across sources
- All album covers mapped correctly (16/16)
- All songs have at least one tag

### Known Characteristics

- `instrumentalness` is near-zero for all songs (expected: Jay Chou is vocal-centric)
- `speechiness` has a wide range (0.02-0.35), driven by rap-heavy songs (双截棍, 忍者)
- 13 songs lack lyrics text — these are skipped in NLP analysis
- `song_tags.csv` intentionally contains 54 "duplicates" (multi-tag songs, long format)

## 9. Files Generated

| File | Description |
|------|-------------|
| `data/processed/jay_music_dataset.csv` | Unified dataset (65 KB, UTF-8 BOM) |
| `data/processed/songs.json` | Unified dataset as JSON |
| `data/processed/albums.json` | Album-level aggregates |

---

*Report generated by preprocessing pipeline.*
