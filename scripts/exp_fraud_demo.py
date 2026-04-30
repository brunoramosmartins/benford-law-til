"""Phase 5 experiment: fraud injection and detection-power demonstration.

Two figures:

* ``figures/fraud_before_after.png`` — first-digit histogram of clean vs
  contaminated city populations side-by-side, plus the four-test verdict
  for each.
* ``figures/fraud_detection_power.png`` — sweep of the contamination
  fraction against MAD, the Pearson chi-squared statistic, and the
  empirical chi-squared rejection rate at alpha = 0.05.

Usage
-----
::

    python scripts/exp_fraud_demo.py
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
from src.datasets import load_world_cities  # noqa: E402
from src.fraud import detection_power_curve, inject_fraud  # noqa: E402

FIG_DIR = REPO_ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)
OUT_BEFORE_AFTER = FIG_DIR / "fraud_before_after.png"
OUT_POWER = FIG_DIR / "fraud_detection_power.png"

CONTAMINATION_FRACTIONS = np.linspace(0.0, 1.0, 21)
"""21 contamination levels from 0% to 100% (5%-resolution sweep)."""

N_TRIALS = 30
"""Independent injections per contamination level."""

DEMO_FRACTION = 0.30
"""Fraction used in the before/after panel."""


def _format_panel_title(label: str, n: int, report) -> str:  # type: ignore[no-untyped-def]
    flagged = [int(d) for d, s in zip(DIGITS, report.per_digit.significant) if s]
    flagged_str = ",".join(str(d) for d in flagged) if flagged else "none"
    rejected = "REJECT" if report.chi_square.reject(alpha=0.05) else "ACCEPT"
    return (
        f"{label}  ($n = {n:,}$)\n"
        f"$\\chi^2 = {report.chi_square.statistic:.1f}$ "
        f"($p = {report.chi_square.p_value:.3g}$, $\\alpha = 0.05$: {rejected})\n"
        f"$\\mathrm{{MAD}} = {report.mad.mad:.4f}$  ({report.mad.verdict})\n"
        f"flagged $d$: {flagged_str}"
    )


def _plot_before_after(
    clean: np.ndarray,
    contaminated: np.ndarray,
    pmf: np.ndarray,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    bar_x = DIGITS - 0.18
    line_x = DIGITS + 0.18

    clean_freq = empirical_frequencies(clean)
    cont_freq = empirical_frequencies(contaminated)
    clean_report = conformity_report(clean)
    cont_report = conformity_report(contaminated)

    axes[0].bar(bar_x, clean_freq, width=0.36, label="Empirical", color="#3b6ea8")
    axes[0].bar(line_x, pmf, width=0.36, label="Benford", color="#d68a3e")
    axes[0].set_title(_format_panel_title("Clean", clean.size, clean_report), fontsize=9)
    axes[0].set_ylabel("Probability")

    axes[1].bar(bar_x, cont_freq, width=0.36, label="Empirical", color="#a83b3b")
    axes[1].bar(line_x, pmf, width=0.36, label="Benford", color="#d68a3e")
    axes[1].set_title(
        _format_panel_title(
            f"Contaminated ({int(DEMO_FRACTION * 100)}% uniform-digit)",
            contaminated.size,
            cont_report,
        ),
        fontsize=9,
    )

    for ax in axes:
        ax.set_xticks(DIGITS)
        ax.set_xlabel("First digit $d$")
        ax.grid(axis="y", linestyle=":", alpha=0.4)

    axes[0].legend(loc="upper right", frameon=False, fontsize=9)
    fig.suptitle(
        f"Fraud injection: 30% uniform-digit contamination of world city populations",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT_BEFORE_AFTER, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _plot_power_curve(
    curves: dict[str, "object"],  # mapping kind -> DetectionCurve
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = {
        "uniform_digit": "#3b6ea8",
        "round_numbers": "#a83b3b",
        "psychological": "#3ea872",
    }
    labels = {
        "uniform_digit": "Uniform-digit",
        "round_numbers": "Round-number",
        "psychological": "Psychological",
    }

    # Panel 1: MAD with Nigrini thresholds.
    for kind, curve in curves.items():
        axes[0].plot(
            curve.fractions,  # type: ignore[attr-defined]
            curve.mad,  # type: ignore[attr-defined]
            marker="o",
            linewidth=1.5,
            color=colors[kind],
            label=labels[kind],
        )
    for thr, label in [
        (0.006, "Acceptable"),
        (0.012, "Marginally acc."),
        (0.015, "Non-conformity"),
    ]:
        axes[0].axhline(thr, color="grey", linestyle=":", alpha=0.6)
        axes[0].text(0.02, thr, label, fontsize=8, color="grey", va="bottom")
    axes[0].set_xlabel("Contamination fraction")
    axes[0].set_ylabel("MAD")
    axes[0].set_title("MAD vs contamination\n(with Nigrini thresholds)", fontsize=10)
    axes[0].grid(linestyle=":", alpha=0.4)
    axes[0].legend(frameon=False, fontsize=9)

    # Panel 2: chi-squared statistic on log scale.
    for kind, curve in curves.items():
        axes[1].plot(
            curve.fractions,  # type: ignore[attr-defined]
            curve.chi_square,  # type: ignore[attr-defined]
            marker="o",
            linewidth=1.5,
            color=colors[kind],
            label=labels[kind],
        )
    crit = 15.51  # chi^2_8, 95th percentile
    axes[1].axhline(crit, color="grey", linestyle=":", alpha=0.6)
    axes[1].text(
        0.02, crit, f"$\\chi^2_{{8, 0.95}} \\approx {crit}$",
        fontsize=8, color="grey", va="bottom",
    )
    axes[1].set_xlabel("Contamination fraction")
    axes[1].set_ylabel("$\\chi^2$ statistic")
    axes[1].set_yscale("log")
    axes[1].set_title("Pearson $\\chi^2$ vs contamination", fontsize=10)
    axes[1].grid(linestyle=":", alpha=0.4, which="both")
    axes[1].legend(frameon=False, fontsize=9)

    # Panel 3: empirical rejection rate.
    for kind, curve in curves.items():
        axes[2].plot(
            curve.fractions,  # type: ignore[attr-defined]
            curve.rejection_rate_chi2_05,  # type: ignore[attr-defined]
            marker="o",
            linewidth=1.5,
            color=colors[kind],
            label=labels[kind],
        )
    axes[2].axhline(0.05, color="grey", linestyle=":", alpha=0.6)
    axes[2].text(0.02, 0.05, "$\\alpha = 0.05$", fontsize=8, color="grey", va="bottom")
    axes[2].set_xlabel("Contamination fraction")
    axes[2].set_ylabel("Rejection rate (chi-squared at $\\alpha = 0.05$)")
    axes[2].set_ylim(-0.05, 1.05)
    axes[2].set_title("Empirical detection power", fontsize=10)
    axes[2].grid(linestyle=":", alpha=0.4)
    axes[2].legend(frameon=False, fontsize=9)

    sample_curve = next(iter(curves.values()))
    n = sample_curve.n  # type: ignore[attr-defined]
    n_trials = sample_curve.n_trials  # type: ignore[attr-defined]
    fig.suptitle(
        f"Detection power: world city populations ($n = {n:,}$, "
        f"{n_trials} trials per fraction)",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(OUT_POWER, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    try:
        cities = load_world_cities(min_population=1)
    except FileNotFoundError as exc:
        print(f"exp_fraud_demo: {exc}", file=sys.stderr)
        return 1

    populations = cities["population"].to_numpy(dtype=float)
    pmf = benford_pmf()
    rng = np.random.default_rng(0)

    print(f"Loaded {len(populations):,} city populations")
    print(f"Sweeping {len(CONTAMINATION_FRACTIONS)} contamination levels, "
          f"{N_TRIALS} trials each, across 3 fabrication kinds...")

    # ----- before/after panel -----
    contaminated = inject_fraud(
        populations, fraction=DEMO_FRACTION, kind="uniform_digit", rng=rng
    )
    _plot_before_after(populations, contaminated, pmf)
    print(f"Wrote {OUT_BEFORE_AFTER}")

    # ----- detection-power sweep -----
    curves: dict[str, object] = {}
    for kind in ("uniform_digit", "round_numbers", "psychological"):
        print(f"  sweeping kind={kind}...")
        curves[kind] = detection_power_curve(
            populations,
            fractions=CONTAMINATION_FRACTIONS,
            kind=kind,  # type: ignore[arg-type]
            n_trials=N_TRIALS,
            rng=np.random.default_rng(0),
        )

    _plot_power_curve(curves)
    print(f"Wrote {OUT_POWER}")

    # ----- summary table -----
    print("\nDetection-power summary (chi-squared rejection rate at alpha = 0.05):")
    header = "  fraction  | " + " | ".join(f"{k:>14}" for k in curves)
    print(header)
    print("-" * len(header))
    for i, f in enumerate(CONTAMINATION_FRACTIONS):
        rates = " | ".join(
            f"{c.rejection_rate_chi2_05[i]:>14.2f}"  # type: ignore[attr-defined]
            for c in curves.values()
        )
        print(f"  {f:>8.2f}  | {rates}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
