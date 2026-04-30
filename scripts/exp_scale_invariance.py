"""Phase 3 experiment: scale invariance of the leading-digit distribution.

Takes the bundled GeoNames world-cities population dataset, multiplies each
value by several constants (currency conversions and pi), and confirms that
the empirical first-digit distribution does not move. Drift is quantified
as the L1 distance from the theoretical Benford PMF.

Output: ``figures/scale_invariance.png``.

Usage
-----
::

    python scripts/exp_scale_invariance.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.benford import (  # noqa: E402 - sys.path tweak above is intentional
    DIGITS,
    benford_pmf,
    empirical_frequencies,
)
from src.datasets import load_world_cities  # noqa: E402

FIG_DIR = REPO_ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)
OUT_PATH = FIG_DIR / "scale_invariance.png"

# Multipliers chosen to be "interesting": one identity, two currency
# conversions (approximate USD-relative rates), one transcendental.
MULTIPLIERS: list[tuple[str, float]] = [
    ("Identity (×1)", 1.0),
    ("USD → BRL (×5.0)", 5.0),
    ("USD → EUR (×0.91)", 0.91),
    ("Transcendental (×π)", float(np.pi)),
]


def l1_distance(empirical: np.ndarray, theoretical: np.ndarray) -> float:
    """L1 distance ``sum_d |emp(d) - theo(d)|``."""
    return float(np.sum(np.abs(empirical - theoretical)))


def main() -> int:
    try:
        cities = load_world_cities(min_population=1)
    except FileNotFoundError as exc:
        print(f"exp_scale_invariance: {exc}", file=sys.stderr)
        return 1

    populations = cities["population"].to_numpy(dtype=float)
    pmf = benford_pmf()
    n = len(populations)

    print(f"n = {n:,} cities")
    print(f"{'multiplier':<22} {'L1 from Benford':>16}")
    print("-" * 40)

    results: list[tuple[str, np.ndarray, float]] = []
    for label, c in MULTIPLIERS:
        scaled = populations * c
        freq = empirical_frequencies(scaled)
        delta = l1_distance(freq, pmf)
        results.append((label, freq, delta))
        print(f"{label:<22} {delta:>16.6f}")

    # ----- figure -----
    fig, axes = plt.subplots(1, 4, figsize=(15, 4), sharey=True)
    bar_x = DIGITS - 0.18
    line_x = DIGITS + 0.18

    for ax, (label, freq, delta) in zip(axes, results):
        ax.bar(bar_x, freq, width=0.36, label="Empirical", color="#3b6ea8")
        ax.bar(line_x, pmf, width=0.36, label="Benford", color="#d68a3e")
        ax.set_xticks(DIGITS)
        ax.set_xlabel("First digit $d$")
        ax.set_title(f"{label}\n$L_1 = {delta:.4f}$", fontsize=10)
        ax.grid(axis="y", linestyle=":", alpha=0.4)

    axes[0].set_ylabel("Probability")
    axes[0].legend(loc="upper right", frameon=False, fontsize=9)
    fig.suptitle(
        f"Scale invariance: leading-digit distribution survives unit changes "
        f"($n = {n:,}$ world cities)",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
    print(f"\nWrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
