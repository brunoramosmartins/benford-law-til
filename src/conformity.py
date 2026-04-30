"""Statistical conformity tests for Benford's Law.

Phase 4 — given an empirical first-digit distribution, decide *how well* it
matches the theoretical Benford PMF :math:`P(d) = \\log_{10}(1 + 1/d)`. Four
complementary tests are implemented:

* :func:`chi_square_test` — Pearson :math:`\\chi^2` goodness-of-fit on the
  9-cell first-digit table. Sensitive to any per-cell deviation; suffers from
  the *excess-power* problem at very large ``n`` (any micro-deviation becomes
  "significant").
* :func:`ks_test` — Kolmogorov–Smirnov statistic on the discrete CDF. Less
  sensitive to single-cell spikes, more sensitive to *cumulative* drift.
* :func:`mad_test` — Mean Absolute Deviation, with Nigrini's empirical
  thresholds for "close conformity" / "acceptable" / "marginally acceptable"
  / "non-conformity". Sample-size *invariant*, so it does not over-reject at
  large ``n`` the way :math:`\\chi^2` does.
* :func:`per_digit_z` — per-cell two-sided :math:`z`-statistic with optional
  continuity correction. The diagnostic tool: tells you *which* digit is
  pulling the data away from Benford.

Each function returns a structured dataclass so downstream code can format,
plot, or compare results without re-deriving the test statistic.

References
----------
* **Nigrini, M. J.** (2012). *Benford's Law: Applications for Forensic
  Accounting, Auditing, and Fraud Detection*. Wiley. — Source of the MAD
  thresholds.
* **Morrow, J.** (2014). *Benford's Law, families of distributions and a test
  basis*. CEP Discussion Paper. — Survey of the discrete-KS and chi-square
  variants used here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import stats

from src.benford import DIGITS, benford_pmf, first_digits


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChiSquareResult:
    """Result of a Pearson chi-squared goodness-of-fit test against Benford."""

    statistic: float
    """The :math:`\\chi^2` statistic, ``sum_d (O_d - E_d)^2 / E_d``."""

    p_value: float
    """Two-sided p-value under :math:`\\chi^2_8`."""

    degrees_of_freedom: int
    """Degrees of freedom (always 8 for the first-digit table)."""

    n: int
    """Sample size."""

    observed: NDArray[np.float64]
    """Observed counts for digits 1..9."""

    expected: NDArray[np.float64]
    """Expected counts ``n * P(d)`` for digits 1..9."""

    critical_value_05: float
    """Critical value at :math:`\\alpha = 0.05` (``chi2.ppf(0.95, df=8)``)."""

    def reject(self, alpha: float = 0.05) -> bool:
        """``True`` iff the test rejects Benford at level ``alpha``."""
        return self.p_value < alpha


@dataclass(frozen=True)
class KSResult:
    """Result of a one-sample Kolmogorov-Smirnov test on the discrete CDF."""

    statistic: float
    """KS statistic, :math:`D_n = \\max_d |F_n(d) - F(d)|`."""

    p_value: float
    """Asymptotic p-value from the Kolmogorov distribution."""

    n: int
    """Sample size."""

    cdf_empirical: NDArray[np.float64]
    """Empirical CDF at digits 1..9."""

    cdf_benford: NDArray[np.float64]
    """Benford CDF at digits 1..9 (cumulative ``log10(1 + 1/d)``)."""

    argmax_digit: int
    """The digit at which the CDF gap is maximised."""

    def reject(self, alpha: float = 0.05) -> bool:
        """``True`` iff the test rejects Benford at level ``alpha``."""
        return self.p_value < alpha


_MAD_THRESHOLDS: tuple[tuple[float, str], ...] = (
    (0.000, "Close conformity"),
    (0.006, "Acceptable conformity"),
    (0.012, "Marginally acceptable conformity"),
    (0.015, "Non-conformity"),
)
"""Nigrini (2012) thresholds for first-digit MAD.

The verdict is the label whose threshold the MAD is above. ``MAD < 0.006`` →
"Close conformity"; ``MAD >= 0.015`` → "Non-conformity".
"""


@dataclass(frozen=True)
class MADResult:
    """Mean Absolute Deviation against Benford with Nigrini's verdict."""

    mad: float
    """:math:`\\frac{1}{9} \\sum_{d=1}^{9} |\\hat P(d) - P(d)|`."""

    verdict: str
    """Nigrini's qualitative label (see :data:`_MAD_THRESHOLDS`)."""

    n: int
    """Sample size."""

    empirical: NDArray[np.float64]
    """Empirical proportions for digits 1..9."""

    expected: NDArray[np.float64]
    """Benford PMF for digits 1..9."""


@dataclass(frozen=True)
class PerDigitZResult:
    """Per-digit two-sided z-statistic with optional continuity correction."""

    z_statistics: NDArray[np.float64]
    """Per-digit ``z_d``, length 9."""

    p_values: NDArray[np.float64]
    """Per-digit two-sided p-values, length 9."""

    significant: NDArray[np.bool_]
    """Boolean mask: ``|z_d| > critical_value`` (default 1.96 for α = 0.05)."""

    n: int
    """Sample size."""

    empirical: NDArray[np.float64]
    """Empirical proportions, length 9."""

    expected: NDArray[np.float64]
    """Benford PMF, length 9."""

    continuity_corrected: bool
    """Whether the :math:`1/(2n)` continuity correction was applied."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _counts_from_input(
    values: ArrayLike,
    *,
    already_counts: bool,
) -> tuple[NDArray[np.int_], int]:
    """Return ``(counts_d1..d9, n)`` from either raw values or precomputed counts.

    ``already_counts=True`` lets callers pass an integer length-9 vector of
    counts directly, bypassing :func:`first_digits`. This matters for tests
    that consume cross-tabulated data without access to the underlying sample.
    """
    arr = np.asarray(values)
    if already_counts:
        if arr.shape != (9,):
            raise ValueError(
                f"counts input must have shape (9,), got {arr.shape}"
            )
        if np.any(arr < 0):
            raise ValueError("counts input contains negative entries")
        counts = arr.astype(int)
    else:
        digits = first_digits(arr)
        counts = np.bincount(digits, minlength=10)[1:10]
    n = int(counts.sum())
    if n == 0:
        raise ValueError("conformity test received an empty sample")
    return counts, n


# ---------------------------------------------------------------------------
# Chi-squared
# ---------------------------------------------------------------------------


def chi_square_test(
    values: ArrayLike,
    *,
    already_counts: bool = False,
) -> ChiSquareResult:
    """Pearson chi-squared goodness-of-fit test against Benford.

    The null hypothesis is that the leading digits are drawn from
    :math:`P(d) = \\log_{10}(1 + 1/d)`. The test statistic is

    .. math::

        \\chi^2 = \\sum_{d=1}^{9} \\frac{(O_d - E_d)^2}{E_d},
        \\qquad E_d = n \\cdot P(d),

    asymptotically distributed as :math:`\\chi^2_8` under the null.

    Parameters
    ----------
    values : array-like
        Either a 1-D array of nonzero finite reals (default), or a length-9
        vector of counts when ``already_counts=True``.
    already_counts : bool, default False
        If ``True``, treat ``values`` as the digit-count vector itself.

    Returns
    -------
    ChiSquareResult
        Statistic, p-value, observed/expected, and the :math:`\\alpha=0.05`
        critical value.

    Notes
    -----
    The :math:`\\chi^2` test is *over-powered* on huge samples: for
    :math:`n \\sim 10^6` even tiny per-cell drifts (~0.001) become
    "significant". This is a feature of the test, not a bug — but it is also
    why MAD with Nigrini's thresholds is the practitioner's preferred summary
    for large datasets.

    Examples
    --------
    >>> import numpy as np
    >>> rng = np.random.default_rng(42)
    >>> sample = 10 ** rng.uniform(0, 6, size=20_000)
    >>> r = chi_square_test(sample)
    >>> bool(r.statistic < r.critical_value_05)
    True
    """
    counts, n = _counts_from_input(values, already_counts=already_counts)
    pmf = benford_pmf()
    expected = n * pmf
    statistic = float(np.sum((counts - expected) ** 2 / expected))
    df = 8
    p_value = float(stats.chi2.sf(statistic, df=df))
    critical = float(stats.chi2.ppf(0.95, df=df))
    return ChiSquareResult(
        statistic=statistic,
        p_value=p_value,
        degrees_of_freedom=df,
        n=n,
        observed=counts.astype(float),
        expected=expected,
        critical_value_05=critical,
    )


# ---------------------------------------------------------------------------
# Kolmogorov-Smirnov (discrete one-sample)
# ---------------------------------------------------------------------------


def ks_test(
    values: ArrayLike,
    *,
    already_counts: bool = False,
) -> KSResult:
    """One-sample Kolmogorov-Smirnov test against the Benford CDF.

    The KS statistic is

    .. math::

        D_n = \\max_{d \\in \\{1, \\ldots, 9\\}}
        \\bigl| F_n(d) - F(d) \\bigr|,

    where :math:`F` is the Benford CDF (cumulative sum of
    :math:`\\log_{10}(1 + 1/d)`). The asymptotic p-value uses the Kolmogorov
    distribution:

    .. math::

        p \\approx 1 - K(\\sqrt{n} \\, D_n),

    via :func:`scipy.stats.kstwobign.sf`.

    Parameters
    ----------
    values : array-like
        See :func:`chi_square_test`.
    already_counts : bool, default False
        See :func:`chi_square_test`.

    Returns
    -------
    KSResult
        Statistic, asymptotic p-value, both CDFs, and the digit at which the
        gap is maximised.

    Notes
    -----
    The continuous-CDF KS p-value is *conservative* on a discrete distribution
    — the true level is below the nominal one. Treat the p-value as a guide,
    not a sharp threshold; for sharp inference use the chi-squared test or a
    bootstrap.
    """
    counts, n = _counts_from_input(values, already_counts=already_counts)
    pmf = benford_pmf()
    cdf_benford = np.cumsum(pmf)
    empirical_pmf = counts / n
    cdf_empirical = np.cumsum(empirical_pmf)
    diffs = np.abs(cdf_empirical - cdf_benford)
    statistic = float(diffs.max())
    argmax_idx = int(np.argmax(diffs))
    argmax_digit = int(DIGITS[argmax_idx])
    # Asymptotic p-value via Kolmogorov distribution.
    p_value = float(stats.kstwobign.sf(np.sqrt(n) * statistic))
    return KSResult(
        statistic=statistic,
        p_value=p_value,
        n=n,
        cdf_empirical=cdf_empirical,
        cdf_benford=cdf_benford,
        argmax_digit=argmax_digit,
    )


# ---------------------------------------------------------------------------
# MAD (Mean Absolute Deviation)
# ---------------------------------------------------------------------------


def mad_test(
    values: ArrayLike,
    *,
    already_counts: bool = False,
) -> MADResult:
    """Mean Absolute Deviation with Nigrini's qualitative thresholds.

    .. math::

        \\mathrm{MAD} = \\frac{1}{9} \\sum_{d=1}^{9}
        \\bigl| \\hat P(d) - P(d) \\bigr|.

    The verdict comes from Nigrini (2012, Ch. 7), calibrated for the *first*
    significant digit:

    ===========  =====================================
    MAD range    Verdict
    ===========  =====================================
    ``< 0.006``  Close conformity
    ``< 0.012``  Acceptable conformity
    ``< 0.015``  Marginally acceptable conformity
    ``>= 0.015`` Non-conformity
    ===========  =====================================

    Parameters
    ----------
    values : array-like
        See :func:`chi_square_test`.
    already_counts : bool, default False
        See :func:`chi_square_test`.

    Returns
    -------
    MADResult
        Numeric MAD, qualitative verdict, observed/expected vectors.

    Notes
    -----
    Unlike :func:`chi_square_test`, MAD is **sample-size invariant**: a given
    set of empirical proportions yields the same verdict whether ``n = 1000``
    or ``n = 10^6``. This makes it the practitioner's tool of choice for
    forensic accounting on large transaction sets.
    """
    counts, n = _counts_from_input(values, already_counts=already_counts)
    pmf = benford_pmf()
    empirical = counts / n
    mad = float(np.mean(np.abs(empirical - pmf)))
    verdict = _MAD_THRESHOLDS[0][1]
    for threshold, label in _MAD_THRESHOLDS:
        if mad >= threshold:
            verdict = label
    return MADResult(
        mad=mad,
        verdict=verdict,
        n=n,
        empirical=empirical,
        expected=pmf,
    )


# ---------------------------------------------------------------------------
# Per-digit Z statistic
# ---------------------------------------------------------------------------


def per_digit_z(
    values: ArrayLike,
    *,
    already_counts: bool = False,
    continuity_correction: bool = True,
    alpha: float = 0.05,
) -> PerDigitZResult:
    """Per-cell two-sided z-test for each digit.

    For digit ``d``, under the null,

    .. math::

        z_d = \\frac{|\\hat P(d) - P(d)| - 1/(2n)}
                   {\\sqrt{P(d) (1 - P(d)) / n}},

    where the :math:`1/(2n)` term is Yates' continuity correction (omitted if
    ``continuity_correction=False`` or whenever it would push the numerator
    below zero). The p-value uses the standard normal,
    :math:`p_d = 2 \\, (1 - \\Phi(z_d))`.

    The "significant" mask is the diagnostic: if cell ``d=1`` is the only one
    flagged, the data are short of leading 1s. If cells :math:`\\{7, 8, 9\\}`
    are flagged, the data are *over-rich* in tail digits — Nigrini's
    "round-number-bias" signature.

    Parameters
    ----------
    values : array-like
        See :func:`chi_square_test`.
    already_counts : bool, default False
        See :func:`chi_square_test`.
    continuity_correction : bool, default True
        Apply Yates' :math:`1/(2n)` correction.
    alpha : float, default 0.05
        Significance level for the two-sided test.

    Returns
    -------
    PerDigitZResult
        Per-digit z, p, significant mask, plus the observed/expected vectors.

    Notes
    -----
    The per-cell test does **not** correct for the family-wise error rate
    across the 9 cells. Treat the mask as descriptive (which digits are out
    of line), not as a multiple-comparisons-corrected hypothesis test. For
    family-wise inference use the :math:`\\chi^2` test on all 9 cells at
    once.
    """
    counts, n = _counts_from_input(values, already_counts=already_counts)
    pmf = benford_pmf()
    empirical = counts / n
    abs_diff = np.abs(empirical - pmf)
    if continuity_correction:
        cc = 1.0 / (2.0 * n)
        # Only subtract the correction where it doesn't flip the sign.
        adjusted = np.where(abs_diff > cc, abs_diff - cc, 0.0)
    else:
        adjusted = abs_diff
    se = np.sqrt(pmf * (1.0 - pmf) / n)
    # se is strictly positive for d in 1..9 since pmf in (0, 1).
    z = adjusted / se
    p_values = 2.0 * stats.norm.sf(z)
    critical = float(stats.norm.ppf(1.0 - alpha / 2.0))
    significant = z > critical
    return PerDigitZResult(
        z_statistics=z,
        p_values=p_values,
        significant=significant,
        n=n,
        empirical=empirical,
        expected=pmf,
        continuity_corrected=continuity_correction,
    )


# ---------------------------------------------------------------------------
# Convenience: run all four tests at once
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConformityReport:
    """Bundle of all four conformity tests on a single sample."""

    n: int
    chi_square: ChiSquareResult
    ks: KSResult
    mad: MADResult
    per_digit: PerDigitZResult

    def summary_table(self) -> str:
        """Human-readable one-line-per-test summary."""
        rows = [
            f"n = {self.n}",
            f"chi2  = {self.chi_square.statistic:8.3f}  "
            f"(p = {self.chi_square.p_value:.4f}, "
            f"crit_0.05 = {self.chi_square.critical_value_05:.3f})",
            f"KS    = {self.ks.statistic:8.4f}  "
            f"(p = {self.ks.p_value:.4f}, "
            f"argmax at d = {self.ks.argmax_digit})",
            f"MAD   = {self.mad.mad:8.5f}  ({self.mad.verdict})",
            f"flagged digits (per-digit Z): "
            f"{[int(d) for d, s in zip(DIGITS, self.per_digit.significant) if s]}",
        ]
        return "\n".join(rows)


def conformity_report(
    values: ArrayLike,
    *,
    already_counts: bool = False,
    method: Literal["all"] = "all",
) -> ConformityReport:
    """Run all four conformity tests and return a single bundled report.

    Parameters
    ----------
    values : array-like
        See :func:`chi_square_test`.
    already_counts : bool, default False
        See :func:`chi_square_test`.
    method : ``"all"``
        Reserved for future single-test selection; currently always runs
        all four tests.

    Returns
    -------
    ConformityReport
        Bundled :class:`ChiSquareResult`, :class:`KSResult`, :class:`MADResult`,
        :class:`PerDigitZResult`.
    """
    if method != "all":
        raise ValueError(f"conformity_report: unknown method {method!r}")
    if already_counts:
        # Avoid re-walking the input four times.
        chi = chi_square_test(values, already_counts=True)
        ks = ks_test(values, already_counts=True)
        mad = mad_test(values, already_counts=True)
        pdz = per_digit_z(values, already_counts=True)
    else:
        # Compute counts once, then forward as already_counts.
        digits = first_digits(np.asarray(values, dtype=float))
        counts = np.bincount(digits, minlength=10)[1:10]
        chi = chi_square_test(counts, already_counts=True)
        ks = ks_test(counts, already_counts=True)
        mad = mad_test(counts, already_counts=True)
        pdz = per_digit_z(counts, already_counts=True)
    return ConformityReport(
        n=chi.n,
        chi_square=chi,
        ks=ks,
        mad=mad,
        per_digit=pdz,
    )


__all__ = [
    "ChiSquareResult",
    "ConformityReport",
    "KSResult",
    "MADResult",
    "PerDigitZResult",
    "chi_square_test",
    "conformity_report",
    "ks_test",
    "mad_test",
    "per_digit_z",
]
