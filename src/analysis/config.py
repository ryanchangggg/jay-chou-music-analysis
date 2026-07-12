"""
Unified configuration for the Jay Chou Music Deep Analysis project.

All project paths, column names, analysis parameters, and random seeds
are defined here as module-level constants. Import this module wherever
you need access to data locations or analysis settings.

Usage:
    from src.analysis.config import RAW_DATA_DIR, AUDIO_FEATURES, RANDOM_SEED
"""

from pathlib import Path
from typing import Final

# ---------------------------------------------------------------------------
# 路径 — 项目根目录自动检测（从此文件向上两级）
# ---------------------------------------------------------------------------

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

RAW_DATA_DIR: Final[Path] = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR: Final[Path] = PROJECT_ROOT / "data" / "processed"
MODELS_DIR: Final[Path] = PROJECT_ROOT / "models"
NOTEBOOKS_DIR: Final[Path] = PROJECT_ROOT / "notebooks"
OUTPUTS_DIR: Final[Path] = PROJECT_ROOT / "outputs"

# ---------------------------------------------------------------------------
# 原始数据文件
# ---------------------------------------------------------------------------

MASTER_DATASET_PATH: Final[Path] = RAW_DATA_DIR / "jay_chou_master_dataset.csv"
DISCOGRAPHY_PATH: Final[Path] = RAW_DATA_DIR / "jay_discography.csv"
SPOTIFY_FEATURES_PATH: Final[Path] = RAW_DATA_DIR / "spotify_features.csv"
LYRICS_PATH: Final[Path] = RAW_DATA_DIR / "lyrics.csv"
ALBUM_COVERS_PATH: Final[Path] = RAW_DATA_DIR / "album_covers.csv"
SONG_TAGS_PATH: Final[Path] = RAW_DATA_DIR / "song_tags.csv"

# ---------------------------------------------------------------------------
# 处理后的输出文件（由 preprocess.py 生成）
# ---------------------------------------------------------------------------

SONGS_JSON: Final[Path] = PROCESSED_DATA_DIR / "songs.json"
ALBUMS_JSON: Final[Path] = PROCESSED_DATA_DIR / "albums.json"
FEATURES_BY_YEAR_JSON: Final[Path] = PROCESSED_DATA_DIR / "features_by_year.json"
CLUSTERING_JSON: Final[Path] = PROCESSED_DATA_DIR / "clustering.json"
LYRICS_ANALYSIS_JSON: Final[Path] = PROCESSED_DATA_DIR / "lyrics_analysis.json"
TOPIC_MODELING_JSON: Final[Path] = PROCESSED_DATA_DIR / "topic_modeling.json"

# ---------------------------------------------------------------------------
# 列名
# ---------------------------------------------------------------------------

# 通用标识符
SONG_NAME: Final[str] = "song_name"
ALBUM_CN: Final[str] = "album_cn"
ALBUM_EN: Final[str] = "album_en"
RELEASE_DATE: Final[str] = "release_date"
COMPOSER: Final[str] = "composer"
LYRICIST: Final[str] = "lyricist"
TRACK_NUMBER: Final[str] = "track_number"

# Spotify 音频特征
DANCEABILITY: Final[str] = "danceability"
ENERGY: Final[str] = "energy"
VALENCE: Final[str] = "valence"
TEMPO: Final[str] = "tempo"
ACOUSTICNESS: Final[str] = "acousticness"
INSTRUMENTALNESS: Final[str] = "instrumentalness"
SPEECHINESS: Final[str] = "speechiness"
LOUDNESS: Final[str] = "loudness"
KEY: Final[str] = "key"
MODE: Final[str] = "mode"
DURATION_MS: Final[str] = "duration_ms"

# 衍生 / 外部数据
POPULARITY: Final[str] = "popularity"
PLAY_COUNT_EST: Final[str] = "play_count_est"
TAGS: Final[str] = "tags"
HAS_LYRICS: Final[str] = "has_lyrics"
ALBUM_COVER_URL: Final[str] = "album_cover_url"

# 歌词
LYRICS: Final[str] = "lyrics"
SOURCE: Final[str] = "source"

# 专辑封面
COVER_URL: Final[str] = "cover_url"

# 歌曲标签（长格式）
TAG: Final[str] = "tag"

# ---------------------------------------------------------------------------
# 特征分组
# ---------------------------------------------------------------------------

AUDIO_FEATURES: Final[list[str]] = [
    DANCEABILITY,
    ENERGY,
    VALENCE,
    TEMPO,
    ACOUSTICNESS,
    INSTRUMENTALNESS,
    SPEECHINESS,
    LOUDNESS,
]

NUMERIC_FEATURES: Final[list[str]] = [
    DANCEABILITY,
    ENERGY,
    VALENCE,
    TEMPO,
    ACOUSTICNESS,
    INSTRUMENTALNESS,
    SPEECHINESS,
    LOUDNESS,
    POPULARITY,
    DURATION_MS,
]

CATEGORICAL_FEATURES: Final[list[str]] = [
    KEY,
    MODE,
]

IDENTIFIER_COLUMNS: Final[list[str]] = [
    SONG_NAME,
    ALBUM_CN,
    ALBUM_EN,
    RELEASE_DATE,
    COMPOSER,
    LYRICIST,
    TRACK_NUMBER,
]

# ---------------------------------------------------------------------------
# 音调映射（音高级别 → 人类可读）
# ---------------------------------------------------------------------------

PITCH_CLASS_NAMES: Final[dict[int, str]] = {
    0: "C",
    1: "C# / Db",
    2: "D",
    3: "D# / Eb",
    4: "E",
    5: "F",
    6: "F# / Gb",
    7: "G",
    8: "G# / Ab",
    9: "A",
    10: "A# / Bb",
    11: "B",
}

MODE_NAMES: Final[dict[int, str]] = {
    0: "minor",
    1: "major",
}

# ---------------------------------------------------------------------------
# 分析参数
# ---------------------------------------------------------------------------

RANDOM_SEED: Final[int] = 42

# 聚类
N_CLUSTERS_RANGE: Final[range] = range(2, 10)
DEFAULT_N_CLUSTERS: Final[int] = 5

# PCA
PCA_N_COMPONENTS_2D: Final[int] = 2
PCA_N_COMPONENTS_3D: Final[int] = 3

# 异常检测
ISOLATION_FOREST_CONTAMINATION: Final[float] = 0.05
ISOLATION_FOREST_N_ESTIMATORS: Final[int] = 200

# LDA 主题建模
LDA_N_TOPICS: Final[int] = 5
LDA_N_PASSES: Final[int] = 20
LDA_TOP_N_WORDS: Final[int] = 15

# 歌词 analysis
MIN_LYRICS_LENGTH_FOR_SENTIMENT: Final[int] = 50
WORDCLOUD_TOP_N: Final[int] = 80

# 统计检验
ANOVA_ALPHA: Final[float] = 0.05

# 分类
CLASSIFIER_CV_FOLDS: Final[int] = 5

# ---------------------------------------------------------------------------
# 数据处理常量
# ---------------------------------------------------------------------------

# 标准化器将在这些列上拟合用于聚类
SCALE_COLUMNS: Final[list[str]] = [
    DANCEABILITY,
    ENERGY,
    VALENCE,
    TEMPO,
    ACOUSTICNESS,
    INSTRUMENTALNESS,
    SPEECHINESS,
    LOUDNESS,
    POPULARITY,
]
