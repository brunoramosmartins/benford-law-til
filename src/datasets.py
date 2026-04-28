"""Dataset loaders for the empirical chapter.

Three datasets are exposed:

* :func:`load_world_cities` — real, Benford-conforming. Reads the
  bundled SimpleMaps snapshot from ``data/raw/world_cities.csv``.
* :func:`fibonacci_sample` — synthetic, Benford-conforming. Generated
  in code via the closed-form Binet expression.
* :func:`adult_heights` — synthetic, **expected to fail** Benford.
  Normal distribution centred at adult human mean height.

The first two are used as positive examples; the third is the failure
case discussed in §5 of the TIL outline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd
from numpy.typing import NDArray

REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent
DATA_DIR: Final[Path] = REPO_ROOT / "data" / "raw"
WORLD_CITIES_CSV: Final[Path] = DATA_DIR / "world_cities.csv"

_PHI: Final[float] = (1.0 + np.sqrt(5.0)) / 2.0
_PSI: Final[float] = (1.0 - np.sqrt(5.0)) / 2.0


def load_world_cities(min_population: int = 1) -> pd.DataFrame:
    """Load the bundled world-cities snapshot.

    The CSV is produced by ``scripts/build_datasets.py`` from the SimpleMaps
    World Cities (Basic) dataset (CC BY 4.0). It is **not** generated on
    demand — if the file is missing, the caller is told to run the build
    script.

    Parameters
    ----------
    min_population : int, default 1
        Filter rows whose ``population`` is below this threshold. Useful
        for excluding cities with missing or zero values that would break
        :func:`benford.first_digit`.

    Returns
    -------
    pandas.DataFrame
        Columns include at least ``city``, ``country``, ``population``.

    Raises
    ------
    FileNotFoundError
        If ``data/raw/world_cities.csv`` does not exist.
    """
    if not WORLD_CITIES_CSV.exists():
        raise FileNotFoundError(
            f"{WORLD_CITIES_CSV} not found. "
            "Run `python scripts/build_datasets.py` first."
        )
    df = pd.read_csv(WORLD_CITIES_CSV, comment="#")
    if "population" not in df.columns:
        raise ValueError(
            f"{WORLD_CITIES_CSV} is missing a 'population' column "
            "(rebuild it with scripts/build_datasets.py)"
        )
    df = df.dropna(subset=["population"])
    df = df[df["population"] >= min_population].copy()
    df["population"] = df["population"].astype(int)
    return df.reset_index(drop=True)


def fibonacci_sample(n: int = 1000) -> NDArray[np.float64]:
    """First ``n`` Fibonacci numbers via Binet's closed form.

    For very large ``n`` the closed form loses precision (the
    :math:`\\psi^n` term vanishes but ``float64`` rounding accumulates).
    Capped at ``n = 1000`` for safety; first-digit extraction depends only
    on the leading mantissa, which Binet preserves to far beyond float
    precision in the relevant range.

    Parameters
    ----------
    n : int, default 1000
        How many Fibonacci numbers to return, starting at ``F_1 = 1``.

    Returns
    -------
    ndarray of float, shape (n,)
        ``[F_1, F_2, ..., F_n]``.

    Notes
    -----
    Binet's formula:

    .. math::

        F_n = \\frac{\\varphi^n - \\psi^n}{\\sqrt{5}},

    where :math:`\\varphi = (1 + \\sqrt{5}) / 2` and
    :math:`\\psi = (1 - \\sqrt{5}) / 2`.
    """
    if n < 1:
        raise ValueError(f"fibonacci_sample: n must be >= 1, got {n}")
    if n > 1000:
        raise ValueError(
            f"fibonacci_sample: n={n} exceeds the precision-safe cap of 1000"
        )
    k = np.arange(1, n + 1, dtype=float)
    sqrt5 = np.sqrt(5.0)
    return (_PHI**k - _PSI**k) / sqrt5


def adult_heights(
    n: int = 10_000,
    mean_cm: float = 170.0,
    sd_cm: float = 10.0,
    seed: int | None = 0,
) -> NDArray[np.float64]:
    """Synthetic adult heights — a Benford-failing dataset.

    Heights are drawn from ``N(mean_cm, sd_cm)`` and clipped to a strictly
    positive range. This dataset spans less than one order of magnitude,
    so its first-digit distribution is sharply non-Benford (digit ``1``
    dominates not for measure-theoretic reasons but because heights cluster
    near 170 cm).

    Parameters
    ----------
    n : int, default 10_000
        Sample size.
    mean_cm : float, default 170.0
        Population mean.
    sd_cm : float, default 10.0
        Population standard deviation.
    seed : int or None, default 0
        Random seed for reproducibility. ``None`` uses fresh entropy.

    Returns
    -------
    ndarray of float, shape (n,)
        Strictly positive heights in centimetres.
    """
    if n < 1:
        raise ValueError(f"adult_heights: n must be >= 1, got {n}")
    if sd_cm <= 0:
        raise ValueError(f"adult_heights: sd_cm must be > 0, got {sd_cm}")
    rng = np.random.default_rng(seed)
    raw = rng.normal(loc=mean_cm, scale=sd_cm, size=n)
    return np.clip(raw, a_min=1.0, a_max=None)
