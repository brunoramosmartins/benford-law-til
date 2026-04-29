"""Download and prepare the bundled real-world dataset.

Fetches the **GeoNames cities5000** snapshot from the official GeoNames
download server (<https://download.geonames.org/export/dump/>, CC BY 4.0),
trims it to the columns the TIL needs, and writes
``data/raw/world_cities.csv`` with a provenance comment header.

GeoNames is the canonical free source of geographic data. ``cities5000.zip``
contains ~50,000 cities with population ≥ 5000 — plenty of orders of
magnitude for the Benford demo, and the URL has been stable for over a
decade.

Usage
-----
::

    python scripts/build_datasets.py

The output CSV must then be committed by the author so the rest of the
project can run without network access::

    git add data/raw/world_cities.csv
    git commit -m "chore(data): bundle GeoNames cities5000 snapshot"
"""

from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "data" / "raw"
OUT_CSV = OUT_DIR / "world_cities.csv"

GEONAMES_URL = "https://download.geonames.org/export/dump/cities5000.zip"
SOURCE_LICENSE = "CC BY 4.0 — GeoNames cities5000"

# GeoNames dump column layout (tab-separated, no header).
# See: https://download.geonames.org/export/dump/readme.txt
GEONAMES_COLUMNS = [
    "geonameid",
    "name",
    "asciiname",
    "alternatenames",
    "latitude",
    "longitude",
    "feature_class",
    "feature_code",
    "iso2",
    "cc2",
    "admin1_code",
    "admin2_code",
    "admin3_code",
    "admin4_code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification_date",
]


def download_zip(url: str) -> bytes:
    """Fetch a ZIP archive into memory.

    GeoNames does not require any auth or special headers, but we still
    advertise a desktop User-Agent for friendlier behaviour with caching
    proxies in between.
    """
    print(f"Downloading {url} ...", file=sys.stderr)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "application/zip,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as resp:  # noqa: S310 - trusted URL
        return resp.read()


def extract_csv(zip_bytes: bytes) -> pd.DataFrame:
    """Find the cities TXT inside the ZIP and parse it as TSV."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        txt_name = next(
            (n for n in zf.namelist() if n.lower().endswith(".txt")),
            None,
        )
        if txt_name is None:
            raise RuntimeError("No .txt found inside GeoNames ZIP")
        with zf.open(txt_name) as f:
            return pd.read_csv(
                f,
                sep="\t",
                header=None,
                names=GEONAMES_COLUMNS,
                dtype={"iso2": "string"},
                na_values=[""],
                keep_default_na=False,
                low_memory=False,
            )


def trim(df: pd.DataFrame) -> pd.DataFrame:
    """Keep the columns the TIL needs and drop rows without population."""
    out = df[["name", "iso2", "population"]].copy()
    out = out.rename(columns={"name": "city", "iso2": "country"})
    out = out.dropna(subset=["population", "city"])
    out = out[out["population"] > 0]
    out["population"] = out["population"].astype(int)
    return out.sort_values("population", ascending=False).reset_index(drop=True)


def write_with_header(df: pd.DataFrame, path: Path) -> None:
    """Write CSV with a provenance comment line."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = (
        f"# Source: {GEONAMES_URL}\n"
        f"# License: {SOURCE_LICENSE}\n"
        f"# Snapshot: {today}\n"
        f"# Rows: {len(df)}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write(header)
        df.to_csv(f, index=False)
    print(f"Wrote {path} ({len(df)} rows)", file=sys.stderr)


def main() -> int:
    try:
        zip_bytes = download_zip(GEONAMES_URL)
        raw = extract_csv(zip_bytes)
        trimmed = trim(raw)
        write_with_header(trimmed, OUT_CSV)
    except Exception as exc:  # noqa: BLE001 - script entry point
        print(f"build_datasets failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
