"""Download and prepare the bundled real-world dataset.

Fetches the **SimpleMaps World Cities (Basic)** snapshot
(<https://simplemaps.com/data/world-cities>, CC BY 4.0), trims it to the
columns the TIL needs, and writes ``data/raw/world_cities.csv`` with a
provenance comment header.

Usage
-----
::

    python scripts/build_datasets.py

The output CSV must then be committed by the author so the rest of the
project can run without network access::

    git add data/raw/world_cities.csv
    git commit -m "chore(data): bundle SimpleMaps world-cities snapshot"
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

# SimpleMaps publishes versioned ZIPs. If this URL 404s, check
# https://simplemaps.com/data/world-cities for the current basic-version URL.
SIMPLEMAPS_URL = (
    "https://simplemaps.com/static/data/world-cities/basic/"
    "simplemaps_worldcities_basicv1.79.zip"
)
SOURCE_LICENSE = "CC BY 4.0 — SimpleMaps World Cities (Basic)"


def download_zip(url: str) -> bytes:
    """Fetch a ZIP archive into memory."""
    print(f"Downloading {url} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 - trusted URL
        return resp.read()


def extract_csv(zip_bytes: bytes) -> pd.DataFrame:
    """Find the worldcities CSV inside the ZIP and load it."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        csv_name = next(
            (n for n in zf.namelist() if n.lower().endswith(".csv")),
            None,
        )
        if csv_name is None:
            raise RuntimeError("No CSV found inside SimpleMaps ZIP")
        with zf.open(csv_name) as f:
            return pd.read_csv(f)


def trim(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the columns the TIL needs and drop rows without population."""
    keep = ["city", "country", "iso2", "population"]
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise RuntimeError(
            f"SimpleMaps schema changed: missing columns {missing}. "
            f"Available: {sorted(df.columns)}"
        )
    out = df[keep].copy()
    out = out.dropna(subset=["population"])
    out["population"] = out["population"].astype(int)
    return out.sort_values("population", ascending=False).reset_index(drop=True)


def write_with_header(df: pd.DataFrame, path: Path) -> None:
    """Write CSV with a provenance comment line."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    header = (
        f"# Source: {SIMPLEMAPS_URL}\n"
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
        zip_bytes = download_zip(SIMPLEMAPS_URL)
        raw = extract_csv(zip_bytes)
        trimmed = trim(raw)
        write_with_header(trimmed, OUT_CSV)
    except Exception as exc:  # noqa: BLE001 - script entry point
        print(f"build_datasets failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
