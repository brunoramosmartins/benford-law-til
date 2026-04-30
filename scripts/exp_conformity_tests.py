"""Phase 4 experiment: run the four conformity tests on three datasets.

Applies ``chi_square_test``, ``ks_test``, ``mad_test``, and ``per_digit_z`` to
three reference samples:

* World city populations (real, Benford-conforming).
* Fibonacci numbers (synthetic, deterministic, Benford-conforming).
* Adult heights (synthetic, Benford-failing — too narrow a window).

The figure shows the empirical-vs-Benford bars per dataset, with each panel's
title carrying the four test verdicts. This is the headline figure for §4 of
the TIL.

Output: ``figures/conformity_test_demo.png``.

Usage
-----
::

    python scripts/exp_conformity_tests.py
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
from src.conformity import conformity_report  # noqa: E402
from src.datasets import (  # noqa: E402
    adult_heights,
    fibonacci_sample,
    load_world_cities,
)

FIG_DIR = REPO_ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)
OUT_PATH = FIG_DIR / "conformity_test_demo.png"


def _format_panel_title(label: str, n: int, report) -> str:  # type: ignore[no-untyped-def]
    """Compact summary string for a panel title."""
    flagged = [int(d) for d, s in zip(DIGITS, report.per_digit.significant) if s]
    flagged_str = ",".join(str(d) for d in flagged) if flagged else "none"
    return (
        f"{label}  ($n = {n:,}$)\n"
        f"$\\chi^2 = {report.chi_square.statistic:.2f}$ "
        f"($p = {report.chi_square.p_value:.3g}$)   "
        f"$\\mathrm{{MAD}} = {report.mad.mad:.4f}$\n"
        f"KS $= {report.ks.statistic:.4f}$   "
        f"flagged $d$: {flagged_str}\n"
        f"verdict: {report.mad.verdict}"
    )


def main() -> int:
    pmf = benford_pmf()

    # --- Dataset 1: world cities. -------------------------------------------
    try:
        cities = load_world_cities(min_population=1)
        cities_pop = cities["population"].to_numpy(dtype=float)
    except FileNotFoundError as exc:
        print(f"exp_conformity_tests: {exc}", file=sys.stderr)
        return 1

    # --- Dataset 2: Fibonacci. ----------------------------------------------
    fib = fibonacci_sample(n=1000)

    # --- Dataset 3: heights. -------------------------------------------------
    heights = adult_heights(n=10_000, mean_cm=170.0, sd_cm=10.0, seed=0)

    datasets: list[tuple[str, np.ndarray]] = [
        ("World city populations", cities_pop),
        ("Fibonacci numbers", fib),
        ("Adult heights (cm)", heights),
    ]

    results = []
    print(f"{'dataset':<28} {'n':>8}  {'chi2':>8}  {'p':>9}  {'MAD':>9}  verdict")
    print("-" * 85)
    for label, sample in datasets:
        report = conformity_report(sample)
        freq = empirical_frequencies(sample)
        results.append((label, sample, freq, report))
        print(
            f"{label:<28} {report.n:>8}  "
            f"{report.chi_square.statistic:>8.2f}  "
            f"{report.chi_square.p_value:>9.3g}  "
            f"{report.mad.mad:>9.5f}  {report.mad.verdict}"
        )

    # ----- figure -----
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    bar_x = DIGITS - 0.18
    line_x = DIGITS + 0.18

    for ax, (label, _sample, freq, report) in zip(axes, results):
        ax.bar(bar_x, freq, width=0.36, label="Empirical", color="#3b6ea8")
        ax.bar(line_x, pmf, width=0.36, label="Benford", color="#d68a3e")
        ax.set_xticks(DIGITS)
        ax.set_xlabel("First digit $d$")
        ax.set_title(_format_panel_title(label, report.n, report), fontsize=9)
        ax.grid(axis="y", linestyle=":", alpha=0.4)

    axes[0].set_ylabel("Probability")
    axes[0].legend(loc="upper right", frameon=False, fontsize=9)
    fig.suptitle(
        "Phase 4: four-test conformity bundle on three reference datasets",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=300, bbox_inches="tight")
    print(f"\nWrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
