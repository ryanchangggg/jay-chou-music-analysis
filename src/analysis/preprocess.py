"""
Data preprocessing — loading, cleaning, and merging all raw CSV sources
into the unified processed dataset for downstream analysis and frontend consumption.

Pipeline:
    1. Load each raw CSV into a pandas DataFrame
    2. Check encoding, duplicate songs, name consistency
    3. Clean column names and standardise data types
    4. Merge on song_name as primary key
    5. Handle missing values and aggregate tags
    6. Write processed JSON + CSV files to data/processed/
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.analysis.config import (
    ALBUM_COVERS_PATH,
    DISCOGRAPHY_PATH,
    LYRICS_PATH,
    MASTER_DATASET_PATH,
    PROCESSED_DATA_DIR,
    SONGS_JSON,
    SONG_TAGS_PATH,
    SPOTIFY_FEATURES_PATH,
    RANDOM_SEED,
)


# ---------------------------------------------------------------------------
# 1. Load functions
# ---------------------------------------------------------------------------


def load_master_dataset(path: Optional[Path] = None) -> pd.DataFrame:
    """Load the master dataset CSV into a DataFrame.

    Parameters
    ----------
    path : Path or None
        Path to the master dataset CSV. Defaults to MASTER_DATASET_PATH.

    Returns
    -------
    pd.DataFrame
        Raw master dataset.
    """
    p: Path = path or MASTER_DATASET_PATH
    if not p.exists():
        raise FileNotFoundError(f"Master dataset not found: {p}")
    df: pd.DataFrame = pd.read_csv(p, encoding="utf-8")
    return df


def load_discography(path: Optional[Path] = None) -> pd.DataFrame:
    """Load discography metadata (album, track number, composer, lyricist).

    Parameters
    ----------
    path : Path or None
        Path to the discography CSV. Defaults to DISCOGRAPHY_PATH.

    Returns
    -------
    pd.DataFrame
        Discography data with 7 columns.
    """
    p: Path = path or DISCOGRAPHY_PATH
    if not p.exists():
        raise FileNotFoundError(f"Discography not found: {p}")
    df: pd.DataFrame = pd.read_csv(p, encoding="utf-8")
    return df


def load_spotify_features(path: Optional[Path] = None) -> pd.DataFrame:
    """Load Spotify audio feature data.

    Parameters
    ----------
    path : Path or None
        Path to the Spotify features CSV. Defaults to SPOTIFY_FEATURES_PATH.

    Returns
    -------
    pd.DataFrame
        Audio features including danceability, energy, valence, tempo, etc.
    """
    p: Path = path or SPOTIFY_FEATURES_PATH
    if not p.exists():
        raise FileNotFoundError(f"Spotify features not found: {p}")
    df: pd.DataFrame = pd.read_csv(p, encoding="utf-8")
    return df


def load_lyrics(path: Optional[Path] = None) -> pd.DataFrame:
    """Load lyrics text data.

    Parameters
    ----------
    path : Path or None
        Path to the lyrics CSV. Defaults to LYRICS_PATH.

    Returns
    -------
    pd.DataFrame
        DataFrame with 3 columns: song_name, lyrics, source.
    """
    p: Path = path or LYRICS_PATH
    if not p.exists():
        raise FileNotFoundError(f"Lyrics not found: {p}")
    df: pd.DataFrame = pd.read_csv(p, encoding="utf-8")
    return df


def load_album_covers(path: Optional[Path] = None) -> pd.DataFrame:
    """Load album cover URL metadata.

    Parameters
    ----------
    path : Path or None
        Path to the album covers CSV. Defaults to ALBUM_COVERS_PATH.

    Returns
    -------
    pd.DataFrame
        DataFrame with 3 columns: album_en, album_cn, cover_url.
    """
    p: Path = path or ALBUM_COVERS_PATH
    if not p.exists():
        raise FileNotFoundError(f"Album covers not found: {p}")
    df: pd.DataFrame = pd.read_csv(p, encoding="utf-8")
    return df


def load_song_tags(path: Optional[Path] = None) -> pd.DataFrame:
    """Load song style tags in long format."""
    p: Path = path or SONG_TAGS_PATH
    if not p.exists():
        raise FileNotFoundError(f"Song tags not found: {p}")
    df: pd.DataFrame = pd.read_csv(p, encoding="utf-8")
    return df


def load_all_raw_data() -> Dict[str, pd.DataFrame]:
    """Load all raw data sources into a dictionary of DataFrames."""
    return {
        "discography": load_discography(),
        "spotify": load_spotify_features(),
        "lyrics": load_lyrics(),
        "album_covers": load_album_covers(),
        "song_tags": load_song_tags(),
    }


# ---------------------------------------------------------------------------
# 2. Data quality checks
# ---------------------------------------------------------------------------


def check_encoding(files: Optional[Dict[str, Path]] = None) -> Dict[str, str]:
    """Check file encoding — all files are expected to be UTF-8.

    Parameters
    ----------
    files : dict of str -> Path or None
        Optional mapping of name -> path to check.

    Returns
    -------
    dict of str -> str
        Mapping from filename to encoding label.
    """
    if files is None:
        files = {
            "discography": DISCOGRAPHY_PATH,
            "spotify": SPOTIFY_FEATURES_PATH,
            "lyrics": LYRICS_PATH,
            "album_covers": ALBUM_COVERS_PATH,
            "song_tags": SONG_TAGS_PATH,
        }
    results: Dict[str, str] = {}
    for name, path in files.items():
        with open(path, "rb") as fh:
            raw: bytes = fh.read(4)
        if raw[:3] == b"\xef\xbb\xbf":
            results[name] = "UTF-8 with BOM"
        elif raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
            results[name] = "UTF-16"
        else:
            results[name] = "UTF-8 (no BOM)"
    return results


def check_duplicates(
    dfs: Dict[str, pd.DataFrame],
) -> Dict[str, Dict[str, object]]:
    """Check for duplicate song names in each source DataFrame.

    Parameters
    ----------
    dfs : dict of str -> DataFrame
        Mapping from source name to DataFrame.

    Returns
    -------
    dict of str -> dict
        Per-source results: total_rows, unique_songs, duplicate_count,
        duplicate_details (if any).
    """
    results: Dict[str, Dict[str, object]] = {}
    for name, df in dfs.items():
        if "song_name" not in df.columns:
            results[name] = {
                "total_rows": len(df),
                "unique_songs": None,
                "duplicate_count": None,
                "duplicate_details": None,
            }
            continue
        dup_mask: pd.Series = df["song_name"].duplicated(keep=False)
        dups: pd.DataFrame = df[dup_mask] if dup_mask.any() else pd.DataFrame()
        results[name] = {
            "total_rows": len(df),
            "unique_songs": int(df["song_name"].nunique()),
            "duplicate_count": int(df["song_name"].duplicated().sum()),
            "duplicate_details": (
                dups[["song_name"]].drop_duplicates()["song_name"].tolist()
                if not dups.empty
                else []
            ),
        }
    return results


def check_name_consistency(
    dfs: Dict[str, pd.DataFrame],
) -> Dict[str, object]:
    """Compare song names across all sources and report mismatches.

    Parameters
    ----------
    dfs : dict of str -> DataFrame
        Mapping from source name to DataFrame.

    Returns
    -------
    dict of str -> object
        Consistency results: sets per source, intersections, differences.
    """
    names: Dict[str, set] = {}
    for name, df in dfs.items():
        if "song_name" in df.columns:
            names[name] = set(df["song_name"].dropna().unique())

    common: set = set.intersection(*names.values()) if names else set()
    union: set = set.union(*names.values()) if names else set()

    differences: Dict[str, set] = {}
    for src_name, src_set in names.items():
        others: set = set.union(
            *(v for k, v in names.items() if k != src_name)
        )
        diff: set = src_set - others
        if diff:
            differences[src_name] = diff

    return {
        "sources": {k: len(v) for k, v in names.items()},
        "common_all": len(common),
        "union_all": len(union),
        "differences": {k: sorted(v) for k, v in differences.items()},
    }


def generate_quality_report(
    dfs: Dict[str, pd.DataFrame],
) -> Dict[str, object]:
    """Generate a complete data quality report covering encoding, duplicates,
    name consistency, and per-source null counts.

    Parameters
    ----------
    dfs : dict of str -> DataFrame
        All raw DataFrames.

    Returns
    -------
    dict of str -> object
        Nested quality report.
    """
    report: Dict[str, object] = {}

    # Encoding
    report["encoding"] = check_encoding()

    # Per-source overview
    overview: Dict[str, Dict[str, object]] = {}
    for name, df in dfs.items():
        null_summary: Dict[str, int] = {
            col: int(df[col].isna().sum())
            for col in df.columns
            if df[col].isna().sum() > 0
        }
        overview[name] = {
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {str(col): str(df[col].dtype) for col in df.columns},
            "nulls": null_summary,
        }
    report["source_overview"] = overview

    # Duplicates
    report["duplicates"] = check_duplicates(dfs)

    # Name consistency
    report["name_consistency"] = check_name_consistency(dfs)

    return report


# ---------------------------------------------------------------------------
# 3. Data cleaning
# ---------------------------------------------------------------------------


def clean_song_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise song names by stripping whitespace and standardising
    full-width characters where applicable.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a song_name column.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with cleaned song_name.
    """
    df = df.copy()
    if "song_name" in df.columns:
        df["song_name"] = df["song_name"].str.strip()
    return df


def extract_year(df: pd.DataFrame) -> pd.DataFrame:
    """Extract year from release_date and add as integer column.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing a release_date column (string, 'YYYY-MM-DD').

    Returns
    -------
    pd.DataFrame
        Same DataFrame with an added 'year' column (int).
    """
    df = df.copy()
    df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year.astype(
        "Int64"
    )
    return df


def aggregate_tags(tags_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate long-format tags (one per row) into pipe-separated string per song.

    Parameters
    ----------
    tags_df : pd.DataFrame
        Long-format tags DataFrame with columns: song_name, tag.

    Returns
    -------
    pd.DataFrame
        Aggregated tags with one row per song: song_name, tags (pipe-separated).
    """
    grouped: pd.DataFrame = (
        tags_df.groupby("song_name")["tag"]
        .apply(lambda x: "|".join(sorted(x)))
        .reset_index()
    )
    return grouped


# ---------------------------------------------------------------------------
# 4. Merge pipeline
# ---------------------------------------------------------------------------


def merge_datasets(
    discography: pd.DataFrame,
    spotify: pd.DataFrame,
    lyrics: pd.DataFrame,
    tags: pd.DataFrame,
    covers: pd.DataFrame,
) -> pd.DataFrame:
    """Merge all raw datasets into a single unified DataFrame.

    The merge is performed on song_name (inner join) to keep only
    songs present in all required sources. Album cover URLs are
    joined on album_en.

    Parameters
    ----------
    discography : pd.DataFrame
    spotify : pd.DataFrame
    lyrics : pd.DataFrame
    tags : pd.DataFrame
    covers : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with all columns.
    """
    # Start with discography as the source of truth
    merged: pd.DataFrame = discography.copy()

    # Merge Spotify features
    merged = merged.merge(spotify, on="song_name", how="inner", suffixes=("", "_spot"))

    # Merge lyrics
    merged = merged.merge(lyrics, on="song_name", how="left", suffixes=("", "_lyr"))

    # Merge aggregated tags
    merged = merged.merge(tags.rename(columns={"tag": "tags"}), on="song_name", how="left")

    # Merge album covers
    merged = merged.merge(covers, on="album_en", how="left", suffixes=("", "_cov"))

    return merged


def run_pipeline(
    output_dir: Optional[Path] = None,
    seed: Optional[int] = None,
) -> Tuple[pd.DataFrame, Dict[str, Path]]:
    """Execute the full preprocessing pipeline end-to-end.

    Steps:
        1. Load all raw data sources
        2. Run data quality checks
        3. Clean song names
        4. Aggregate tags
        5. Merge into unified DataFrame
        6. Extract derived columns
        7. Write processed JSON + CSV files to data/processed/

    Parameters
    ----------
    output_dir : Path or None
        Directory for processed output. Defaults to PROCESSED_DATA_DIR.
    seed : int or None
        Random seed (unused during preprocessing, kept for API consistency).

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Path]]
        The unified DataFrame and a dict mapping output names to file paths.
    """
    _ = seed  # unused in preprocess, kept for API compatibility

    print("=" * 60)
    print("Jay Chou Music Analysis — Preprocessing Pipeline")
    print("=" * 60)

    # Step 1: Load all raw data
    print("\n[1/7] Loading raw data...")
    dfs: Dict[str, pd.DataFrame] = load_all_raw_data()
    for name, df in dfs.items():
        print(f"  {name:20s} {len(df):>5} rows  {list(df.columns)[:4]}...")

    # Step 2: Data quality report
    print("\n[2/7] Running data quality checks...")
    report: Dict[str, object] = generate_quality_report(dfs)

    enc: Dict[str, str] = report["encoding"]  # type: ignore
    print("  Encoding:")
    for name, enc_type in enc.items():
        print(f"    {name:20s} {enc_type}")

    dup: Dict[str, Dict[str, object]] = report["duplicates"]  # type: ignore
    print("  Duplicates:")
    for name, info in dup.items():
        cnt = info["duplicate_count"]
        print(f"    {name:20s} {info['unique_songs']} unique / {info['total_rows']} rows  duplicates={cnt if cnt is not None else str(cnt)}")  # type: ignore
        if cnt is not None and cnt > 0 and info["duplicate_details"]:
            print(f"      Duplicate names: {info['duplicate_details']}")  # type: ignore

    consistency: Dict[str, object] = report["name_consistency"]  # type: ignore
    print("  Name consistency:")
    print(f"    Common across all sources: {consistency['common_all']}")
    print(f"    Union across all sources:  {consistency['union_all']}")
    diffs: Dict[str, list] = consistency["differences"]  # type: ignore
    if diffs:
        for src, names in diffs.items():
            print(f"    {src} exclusive: {names}")
    else:
        print("    (no discrepancies)")

    nulls: Dict[str, Dict[str, int]] = {}
    for name, info in report["source_overview"].items():  # type: ignore
        if info["nulls"]:
            nulls[name] = info["nulls"]
    if nulls:
        print("  Null values:")
        for name, cols in nulls.items():
            for col, cnt in cols.items():
                print(f"    {name:20s} {col:15s} {cnt} nulls")

    # Step 3: Clean song names
    print("\n[3/7] Cleaning song names...")
    for name in dfs:
        if "song_name" in dfs[name].columns:
            before: int = int(dfs[name]["song_name"].str.strip().ne(dfs[name]["song_name"]).sum())
            dfs[name] = clean_song_names(dfs[name])
            if before > 0:
                print(f"  {name:20s} stripped {before} names")
            else:
                print(f"  {name:20s} already clean")

    # Step 4: Aggregate tags
    print("\n[4/7] Aggregating tags...")
    tags_agg: pd.DataFrame = aggregate_tags(dfs["song_tags"])
    print(f"  {len(tags_agg)} songs with aggregated tags")

    # Step 5: Merge
    print("\n[5/7] Merging datasets...")
    merged: pd.DataFrame = merge_datasets(
        discography=dfs["discography"],
        spotify=dfs["spotify"],
        lyrics=dfs["lyrics"],
        tags=tags_agg,
        covers=dfs["album_covers"],
    )
    print(f"  Merged: {len(merged)} rows, {merged.shape[1]} columns")

    # Step 6: Extract derived columns
    print("\n[6/7] Extracting derived columns...")
    merged = extract_year(merged)
    year_range: str = f"{merged['year'].min()} ~ {merged['year'].max()}"
    print(f"  Year range: {year_range}")

    # Check for duplicates in final merge
    if merged["song_name"].duplicated().any():
        dup_songs: list = merged[merged["song_name"].duplicated(keep=False)][
            "song_name"
        ].unique().tolist()
        print(f"  WARNING: {len(dup_songs)} duplicate songs in merged result: {dup_songs}")

    # Step 7: Write output
    out_dir: Path = output_dir or PROCESSED_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[7/7] Writing processed files to {out_dir}...")

    csv_path: Path = out_dir / "jay_music_dataset.csv"
    merged.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"  CSV:  {csv_path} ({csv_path.stat().st_size / 1024:.0f} KB)")

    json_path: Path = out_dir / "songs.json"
    merged.to_json(json_path, orient="records", force_ascii=False, indent=2)
    print(f"  JSON: {json_path}")

    # Also write a small album summary
    album_summary: pd.DataFrame = merged.groupby(["album_cn", "album_en"], sort=False).agg(
        song_count=("song_name", "count"),
        avg_popularity=("popularity", "mean"),
        avg_energy=("energy", "mean"),
        avg_valence=("valence", "mean"),
        year=("year", "first"),
    ).reset_index().sort_values("year")
    album_json_path: Path = out_dir / "albums.json"
    album_summary.to_json(album_json_path, orient="records", force_ascii=False, indent=2)
    print(f"  Albums JSON: {album_json_path}")

    # Final summary
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print(f"  Songs:    {len(merged)}")
    print(f"  Albums:   {merged['album_cn'].nunique()}")
    print(f"  Columns:  {merged.shape[1]}")
    print(f"  Year:     {year_range}")
    print(f"  Lyrics:   {merged['lyrics'].notna().sum()}/{len(merged)} have lyrics")
    print(f"  Tags:     {merged['tags'].notna().sum()}/{len(merged)} have tags")
    print("=" * 60)

    outputs: Dict[str, Path] = {
        "csv": csv_path,
        "songs_json": json_path,
        "albums_json": album_json_path,
    }
    return merged, outputs


if __name__ == "__main__":
    df, paths = run_pipeline()
