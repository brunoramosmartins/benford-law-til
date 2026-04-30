"""Fraud injection and detection-power experiments.

Phase 5 — given a clean Benford-conforming dataset, fabricate plausible
"cooked" values, inject them at increasing rates, and watch the conformity
tests cross from *accept* to *reject*. The detection-power curve is the
article's payoff plot: it answers the operational question, **how much
contamination does it take before Benford-style auditing reliably flags a
dataset?**

The module exposes three layers:

* :func:`fabricate_values` — generate a synthetic batch of non-Benford
  numbers in three flavours: uniform-on-leading-digits, "round-number" bias,
  and a psychological-bias model (humans avoid extremes).
* :func:`inject_fraud` — replace a chosen fraction of a real sample with
  fabricated entries, matching the magnitude window of the original data so
  the spike is in the *digit distribution*, not in the order of magnitude.
* :func:`detection_power_curve` — sweep contamination fractions, run the
  full :func:`src.conformity.conformity_report` bundle on each, and bundle
  the resulting test statistics into a :class:`DetectionCurve` dataclass.

Historical motivation
---------------------
Benford-style first-digit analysis has flagged real fraud in:

* **Greek fiscal statistics (2010).** Rauch, Göttsche, Brähler & Engel
  (2011, *German Economic Review*) applied first-digit analysis to EU
  member-state macroeconomic deficit reports for 1999–2009 and found Greece
  the only state whose deficit reports significantly violated Benford's
  Law — published months before the official acknowledgment of statistical
  manipulation.
* **Iranian presidential election (2009).** Multiple post-hoc analyses
  (Mebane 2010 onward) found anomalies consistent with Benford-style
  irregularities at the polling-station level.
* **Forensic accounting practice.** Nigrini's *Benford's Law* (2012) is the
  textbook for the practical version of this experiment, applied across
  thousands of corporate datasets.

The fabrication-and-detection demo in :func:`detection_power_curve`
recreates the *mechanism* by which these audits work: under the null, the
empirical first-digit distribution sits on top of the Benford curve;
contamination pushes it off, and conformity tests measure the push.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

from src.conformity import conformity_report

FabricationKind = Literal["uniform_digit", "round_numbers", "psychological"]
"""The three built-in fabrication strategies. See :func:`fabricate_values`."""

_PSYCHOLOGICAL_WEIGHTS: NDArray[np.float64] = np.array(
    [0.04, 0.10, 0.15, 0.18, 0.18, 0.16, 0.10, 0.06, 0.03],
    dtype=float,
)
"""Empirical weights for the *psychological* model.

When humans pick "random-looking" first digits, they over-pick the middle
digits (3–6) and under-pick the extremes (1 and 9). The exact weights here
are stylised — they are not fitted to any particular dataset, only chosen to
produce a clearly non-Benford profile while still looking superficially
plausible. Used by :func:`fabricate_values` with ``kind="psychological"``.
"""

_DEFAULT_ROUND_BASES: tuple[int, ...] = (
    100,
    200,
    250,
    500,
    1000,
    2000,
    5000,
    10_000,
)
"""Round-number anchors used by ``kind="round_numbers"``.

Fabricated invoices in many fraud cases cluster at "round" amounts because
the fraudster rounds mentally. We sample uniformly from these anchors and
add a small log-normal jitter, which produces an empirical first-digit
distribution heavy on 1, 2, and 5.
"""


# ---------------------------------------------------------------------------
# Fabrication
# ---------------------------------------------------------------------------


def fabricate_values(
    n: int,
    *,
    kind: FabricationKind = "uniform_digit",
    magnitude_window: tuple[float, float] = (1e2, 1e6),
    rng: np.random.Generator | None = None,
) -> NDArray[np.float64]:
    """Generate ``n`` fabricated values whose leading-digit distribution is
    intentionally non-Benford.

    Parameters
    ----------
    n : int
        Number of values to fabricate. Must be non-negative.
    kind : {"uniform_digit", "round_numbers", "psychological"}
        Fabrication strategy:

        * ``"uniform_digit"`` — first digit uniform on ``{1, ..., 9}``,
          mantissa tail uniform on ``[0, 1)``, magnitude uniform on the
          ``magnitude_window``. The classic textbook violation: every digit
          appears ~11.1 % of the time, vs Benford's 30.1 % for digit 1.
        * ``"round_numbers"`` — sample from ``_DEFAULT_ROUND_BASES`` with a
          log-normal jitter. Mimics the fraudster who rounds mentally to
          $100, $250, $1,000, etc.
        * ``"psychological"`` — first digit drawn from
          :data:`_PSYCHOLOGICAL_WEIGHTS` (over-picks 3–6, under-picks 1
          and 9). Mimics humans asked to write down "random" numbers.
    magnitude_window : tuple of (float, float)
        ``(lo, hi)`` — magnitude range, in original units, over which the
        synthetic values are spread. Only used by ``"uniform_digit"`` and
        ``"psychological"``. Must satisfy ``0 < lo < hi``.
    rng : numpy.random.Generator or None
        Random generator. Defaults to a fresh ``default_rng`` (no seed).
        Pass an explicit ``rng`` for reproducibility.

    Returns
    -------
    ndarray of float, shape (n,)
        Strictly positive synthetic values.

    Raises
    ------
    ValueError
        If ``n < 0``, the magnitude window is invalid, or ``kind`` is
        unknown.

    Examples
    --------
    >>> import numpy as np
    >>> rng = np.random.default_rng(0)
    >>> fake = fabricate_values(10_000, kind="uniform_digit", rng=rng)
    >>> from src.benford import empirical_frequencies, benford_pmf
    >>> freq = empirical_frequencies(fake)
    >>> # Each digit should appear ~11.1 % — far from Benford's 30.1 % for d=1.
    >>> bool(abs(freq[0] - 1.0 / 9.0) < 0.02)
    True
    """
    if n < 0:
        raise ValueError(f"fabricate_values: n must be >= 0, got {n}")
    if n == 0:
        return np.empty(0, dtype=float)
    lo, hi = magnitude_window
    if not (0 < lo < hi):
        raise ValueError(
            f"fabricate_values: magnitude_window must satisfy 0 < lo < hi, "
            f"got {magnitude_window!r}"
        )
    rng = rng if rng is not None else np.random.default_rng()
    log_lo, log_hi = float(np.log10(lo)), float(np.log10(hi))

    if kind == "uniform_digit":
        first = rng.integers(1, 10, size=n).astype(float)
        magnitude = rng.uniform(log_lo, log_hi, size=n)
        # Place each value as (first + tail) * 10**floor(magnitude), where
        # tail in [0, 1). Because first is in [1, 9] and tail in [0, 1), the
        # leading digit of the constructed value is exactly ``first``.
        tail = rng.uniform(0.0, 1.0, size=n)
        return (first + tail) * 10.0 ** np.floor(magnitude)

    if kind == "round_numbers":
        bases = np.asarray(_DEFAULT_ROUND_BASES, dtype=float)
        idx = rng.integers(0, len(bases), size=n)
        chosen = bases[idx]
        # Multiplicative log-normal jitter (~5%) so values aren't pixel-identical.
        jitter = rng.lognormal(mean=0.0, sigma=0.05, size=n)
        values = chosen * jitter
        # Guarantee strict positivity.
        return np.clip(values, a_min=1.0, a_max=None)

    if kind == "psychological":
        weights = _PSYCHOLOGICAL_WEIGHTS / _PSYCHOLOGICAL_WEIGHTS.sum()
        first = rng.choice(np.arange(1, 10), size=n, p=weights).astype(float)
        magnitude = rng.uniform(log_lo, log_hi, size=n)
        tail = rng.uniform(0.0, 1.0, size=n)
        return (first + tail) * 10.0 ** np.floor(magnitude)

    raise ValueError(f"fabricate_values: unknown kind {kind!r}")


# ---------------------------------------------------------------------------
# Injection
# ---------------------------------------------------------------------------


def inject_fraud(
    values: ArrayLike,
    fraction: float,
    *,
    kind: FabricationKind = "uniform_digit",
    rng: np.random.Generator | None = None,
) -> NDArray[np.float64]:
    """Return a copy of ``values`` with a ``fraction`` of entries replaced by
    fabricated ones.

    The fabricated batch is drawn over the same magnitude window as the
    real data (5th to 95th log-percentile), so the fraud signal appears
    in the *digit distribution* and not in the order of magnitude.

    Parameters
    ----------
    values : array-like
        The clean dataset, a 1-D array of strictly positive finite reals.
    fraction : float
        Fraction of entries to replace, in ``[0, 1]``. ``0`` returns a copy
        unchanged; ``1`` returns a fully fabricated array.
    kind : :data:`FabricationKind`, default ``"uniform_digit"``
        Fabrication strategy. See :func:`fabricate_values`.
    rng : numpy.random.Generator or None
        Random generator (also forwarded to :func:`fabricate_values`).

    Returns
    -------
    ndarray of float, shape (len(values),)
        A new array, never the input. The original ``values`` is never
        mutated.

    Raises
    ------
    ValueError
        If ``fraction`` is outside ``[0, 1]``, or the input contains
        zeros / non-finite entries.
    """
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"inject_fraud: fraction must be in [0, 1], got {fraction}")
    arr = np.asarray(values, dtype=float).copy()
    if arr.ndim != 1:
        raise ValueError(f"inject_fraud: expected 1-D input, got ndim={arr.ndim}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("inject_fraud: input contains NaN or inf")
    if np.any(arr <= 0):
        raise ValueError("inject_fraud: input must be strictly positive")
    n = arr.size
    n_swap = int(round(fraction * n))
    if n_swap == 0:
        return arr
    rng = rng if rng is not None else np.random.default_rng()
    # Magnitude window: 5th–95th log-percentile of the real data, so we don't
    # let extreme outliers dominate the fabrication range.
    log_arr = np.log10(arr)
    lo_log = float(np.percentile(log_arr, 5.0))
    hi_log = float(np.percentile(log_arr, 95.0))
    if not lo_log < hi_log:
        # Degenerate case: data spans <1 order of magnitude. Widen.
        lo_log -= 0.5
        hi_log += 0.5
    magnitude_window = (10.0**lo_log, 10.0**hi_log)
    fabricated = fabricate_values(
        n_swap, kind=kind, magnitude_window=magnitude_window, rng=rng
    )
    idx = rng.choice(n, size=n_swap, replace=False)
    arr[idx] = fabricated
    return arr


# ---------------------------------------------------------------------------
# Detection power curve
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DetectionCurve:
    """The detection-power sweep across contamination fractions.

    All arrays have the same length as :attr:`fractions`; each entry is a
    test-statistic value (or per-trial mean) at the corresponding fraction.
    """

    fractions: NDArray[np.float64]
    """Contamination fractions tested, monotonically increasing."""

    n: int
    """Sample size of the underlying dataset."""

    n_trials: int
    """Number of independent injection trials averaged at each fraction."""

    kind: FabricationKind
    """Fabrication strategy used."""

    mad: NDArray[np.float64]
    """Mean Absolute Deviation, averaged over trials."""

    chi_square: NDArray[np.float64]
    """Pearson :math:`\\chi^2` statistic, averaged over trials."""

    chi_square_p: NDArray[np.float64]
    """Mean p-value of the chi-squared test."""

    ks: NDArray[np.float64]
    """KS statistic :math:`D_n`, averaged over trials."""

    rejection_rate_chi2_05: NDArray[np.float64]
    """Empirical rejection rate of :math:`\\chi^2` at :math:`\\alpha = 0.05`.

    Across ``n_trials`` injections at each fraction, what proportion of them
    is flagged by the chi-squared test? This is the *empirical detection
    power* and the headline number for the article's audit-power claim.
    """


def detection_power_curve(
    values: ArrayLike,
    fractions: ArrayLike,
    *,
    kind: FabricationKind = "uniform_digit",
    n_trials: int = 30,
    rng: np.random.Generator | None = None,
) -> DetectionCurve:
    """Sweep contamination fractions and record conformity-test statistics.

    For each ``f in fractions``, run ``n_trials`` independent injections at
    that level, compute the four-test bundle on each contaminated dataset,
    and record the per-trial mean of MAD / :math:`\\chi^2` / KS along with
    the empirical rejection rate of :math:`\\chi^2` at
    :math:`\\alpha = 0.05`.

    Parameters
    ----------
    values : array-like
        The clean dataset (assumed Benford-conforming).
    fractions : array-like of float
        Contamination fractions to sweep. Each in ``[0, 1]``.
    kind : :data:`FabricationKind`, default ``"uniform_digit"``
        Fabrication strategy.
    n_trials : int, default 30
        Independent injection trials per fraction. Higher = smoother curves.
    rng : numpy.random.Generator or None
        Random generator. Pass a seeded ``rng`` for reproducible sweeps.

    Returns
    -------
    DetectionCurve
        See dataclass for the per-field meaning.

    Notes
    -----
    The sweep is the costliest computation in the project (each fraction
    runs ``n_trials`` four-test bundles), but for ``n_trials = 30`` and
    typical ``len(fractions) ~ 15`` it still completes in seconds on the
    bundled GeoNames data.
    """
    arr = np.asarray(values, dtype=float)
    fractions_arr = np.asarray(fractions, dtype=float)
    if np.any((fractions_arr < 0.0) | (fractions_arr > 1.0)):
        raise ValueError("detection_power_curve: every fraction must be in [0, 1]")
    if n_trials < 1:
        raise ValueError(f"detection_power_curve: n_trials must be >= 1, got {n_trials}")
    rng = rng if rng is not None else np.random.default_rng()

    n_pts = len(fractions_arr)
    mad = np.zeros(n_pts)
    chi2 = np.zeros(n_pts)
    chi2_p = np.zeros(n_pts)
    ks = np.zeros(n_pts)
    reject_rate = np.zeros(n_pts)

    for i, f in enumerate(fractions_arr):
        mad_runs = np.zeros(n_trials)
        chi2_runs = np.zeros(n_trials)
        chi2_p_runs = np.zeros(n_trials)
        ks_runs = np.zeros(n_trials)
        rejected = 0
        for t in range(n_trials):
            contaminated = inject_fraud(arr, float(f), kind=kind, rng=rng)
            report = conformity_report(contaminated)
            mad_runs[t] = report.mad.mad
            chi2_runs[t] = report.chi_square.statistic
            chi2_p_runs[t] = report.chi_square.p_value
            ks_runs[t] = report.ks.statistic
            if report.chi_square.reject(alpha=0.05):
                rejected += 1
        mad[i] = float(np.mean(mad_runs))
        chi2[i] = float(np.mean(chi2_runs))
        chi2_p[i] = float(np.mean(chi2_p_runs))
        ks[i] = float(np.mean(ks_runs))
        reject_rate[i] = rejected / n_trials

    return DetectionCurve(
        fractions=fractions_arr,
        n=int(arr.size),
        n_trials=n_trials,
        kind=kind,
        mad=mad,
        chi_square=chi2,
        chi_square_p=chi2_p,
        ks=ks,
        rejection_rate_chi2_05=reject_rate,
    )


__all__ = [
    "DetectionCurve",
    "FabricationKind",
    "detection_power_curve",
    "fabricate_values",
    "inject_fraud",
]
