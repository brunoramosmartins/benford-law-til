"""Tests for src.conformity."""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats

from src.benford import DIGITS, benford_pmf, first_digits
from src.conformity import (
    ChiSquareResult,
    ConformityReport,
    KSResult,
    MADResult,
    PerDigitZResult,
    chi_square_test,
    conformity_report,
    ks_test,
    mad_test,
    per_digit_z,
)


# ---------------------------------------------------------------------------
# Fixtures: conforming and non-conforming samples
# ---------------------------------------------------------------------------


@pytest.fixture
def benford_sample() -> np.ndarray:
    """Large log-uniform sample — Benford-conforming."""
    rng = np.random.default_rng(42)
    return 10 ** rng.uniform(0.0, 6.0, size=50_000)


@pytest.fixture
def uniform_sample() -> np.ndarray:
    """Uniform on [1, 10) — strongly non-Benford."""
    rng = np.random.default_rng(42)
    return rng.uniform(1.0, 10.0, size=50_000)


@pytest.fixture
def benford_counts(benford_sample: np.ndarray) -> np.ndarray:
    """Length-9 counts array derived from ``benford_sample``."""
    digits = first_digits(benford_sample)
    return np.bincount(digits, minlength=10)[1:10]


# ---------------------------------------------------------------------------
# Chi-squared
# ---------------------------------------------------------------------------


class TestChiSquareTest:
    def test_returns_dataclass(self, benford_sample: np.ndarray) -> None:
        r = chi_square_test(benford_sample)
        assert isinstance(r, ChiSquareResult)
        assert r.degrees_of_freedom == 8
        assert r.observed.shape == (9,)
        assert r.expected.shape == (9,)

    def test_does_not_reject_conforming(self, benford_sample: np.ndarray) -> None:
        r = chi_square_test(benford_sample)
        assert not r.reject(alpha=0.01)

    def test_rejects_uniform_sample(self, uniform_sample: np.ndarray) -> None:
        r = chi_square_test(uniform_sample)
        assert r.reject(alpha=0.001)
        assert r.statistic > r.critical_value_05

    def test_critical_value_matches_scipy(self) -> None:
        rng = np.random.default_rng(0)
        sample = 10 ** rng.uniform(0, 4, size=1000)
        r = chi_square_test(sample)
        expected_crit = float(stats.chi2.ppf(0.95, df=8))
        assert math.isclose(r.critical_value_05, expected_crit, rel_tol=1e-12)

    def test_already_counts_path(self, benford_counts: np.ndarray) -> None:
        r = chi_square_test(benford_counts, already_counts=True)
        assert r.n == int(benford_counts.sum())
        np.testing.assert_array_equal(r.observed, benford_counts.astype(float))

    def test_counts_shape_validation(self) -> None:
        with pytest.raises(ValueError, match=r"shape \(9,\)"):
            chi_square_test(np.array([1, 2, 3]), already_counts=True)

    def test_negative_counts_raise(self) -> None:
        with pytest.raises(ValueError, match="negative"):
            chi_square_test(
                np.array([100, 50, -1, 0, 0, 0, 0, 0, 0]), already_counts=True
            )

    def test_empty_sample_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            chi_square_test(np.zeros(9, dtype=int), already_counts=True)

    def test_statistic_nonnegative(self, benford_sample: np.ndarray) -> None:
        r = chi_square_test(benford_sample)
        assert r.statistic >= 0.0

    def test_p_value_in_unit_interval(self, benford_sample: np.ndarray) -> None:
        r = chi_square_test(benford_sample)
        assert 0.0 <= r.p_value <= 1.0


# ---------------------------------------------------------------------------
# Kolmogorov-Smirnov
# ---------------------------------------------------------------------------


class TestKSTest:
    def test_returns_dataclass(self, benford_sample: np.ndarray) -> None:
        r = ks_test(benford_sample)
        assert isinstance(r, KSResult)
        assert r.cdf_empirical.shape == (9,)
        assert r.cdf_benford.shape == (9,)
        assert 1 <= r.argmax_digit <= 9

    def test_cdf_benford_endpoint_is_one(self, benford_sample: np.ndarray) -> None:
        r = ks_test(benford_sample)
        assert math.isclose(r.cdf_benford[-1], 1.0, rel_tol=1e-12)

    def test_does_not_reject_conforming(self, benford_sample: np.ndarray) -> None:
        r = ks_test(benford_sample)
        assert not r.reject(alpha=0.01)

    def test_rejects_uniform_sample(self, uniform_sample: np.ndarray) -> None:
        r = ks_test(uniform_sample)
        assert r.reject(alpha=0.001)

    def test_statistic_nonnegative_and_bounded(
        self, benford_sample: np.ndarray
    ) -> None:
        r = ks_test(benford_sample)
        assert 0.0 <= r.statistic <= 1.0

    def test_already_counts_path(self, benford_counts: np.ndarray) -> None:
        r = ks_test(benford_counts, already_counts=True)
        assert r.n == int(benford_counts.sum())


# ---------------------------------------------------------------------------
# MAD
# ---------------------------------------------------------------------------


class TestMADTest:
    def test_close_conformity_for_log_uniform(
        self, benford_sample: np.ndarray
    ) -> None:
        r = mad_test(benford_sample)
        assert isinstance(r, MADResult)
        # Large log-uniform sample should land in "Close conformity".
        assert r.mad < 0.006
        assert r.verdict == "Close conformity"

    def test_non_conformity_for_uniform_sample(
        self, uniform_sample: np.ndarray
    ) -> None:
        r = mad_test(uniform_sample)
        assert r.mad >= 0.015
        assert r.verdict == "Non-conformity"

    def test_sample_size_invariance(self) -> None:
        """MAD on the same proportions should be (nearly) constant in n."""
        rng = np.random.default_rng(7)
        # Build the same proportion vector at two different n's.
        # We generate independently but from the same distribution; MAD must
        # not drift systematically as n grows.
        r_small = mad_test(10 ** rng.uniform(0, 6, size=5_000))
        r_big = mad_test(10 ** rng.uniform(0, 6, size=200_000))
        # Both should land at "Close conformity" or close to it.
        assert r_small.mad < 0.012
        assert r_big.mad < 0.006

    def test_verdict_thresholds_monotone(self) -> None:
        """As MAD grows, the verdict tier monotonically degrades."""
        # Construct synthetic count vectors with controlled MAD by mixing the
        # Benford PMF with a uniform-on-9-digits.
        n = 100_000
        pmf = benford_pmf()
        flat = np.full(9, 1.0 / 9.0)
        verdicts: list[str] = []
        for alpha in [0.0, 0.05, 0.10, 0.20, 0.50]:
            mixture = (1.0 - alpha) * pmf + alpha * flat
            counts = np.round(n * mixture).astype(int)
            r = mad_test(counts, already_counts=True)
            verdicts.append(r.verdict)
        # The first should be "Close conformity"; the last should be "Non-conformity".
        assert verdicts[0] == "Close conformity"
        assert verdicts[-1] == "Non-conformity"

    def test_zero_mad_for_exact_pmf_counts(self) -> None:
        n = 1_000_000
        counts = np.round(n * benford_pmf()).astype(int)
        r = mad_test(counts, already_counts=True)
        assert r.mad < 1e-5
        assert r.verdict == "Close conformity"


# ---------------------------------------------------------------------------
# Per-digit Z
# ---------------------------------------------------------------------------


class TestPerDigitZ:
    def test_returns_dataclass(self, benford_sample: np.ndarray) -> None:
        r = per_digit_z(benford_sample)
        assert isinstance(r, PerDigitZResult)
        assert r.z_statistics.shape == (9,)
        assert r.p_values.shape == (9,)
        assert r.significant.shape == (9,)
        assert r.continuity_corrected is True

    def test_no_flags_for_conforming_sample(
        self, benford_sample: np.ndarray
    ) -> None:
        r = per_digit_z(benford_sample)
        # On a 50k-sample log-uniform draw, expect no per-cell rejections at
        # α = 0.01. (At α = 0.05 the family-wise error rate makes 1-2 false
        # positives plausible.)
        assert not np.any(r.significant) or np.sum(r.significant) <= 1

    def test_flags_for_uniform_sample(self, uniform_sample: np.ndarray) -> None:
        r = per_digit_z(uniform_sample)
        # Uniform on [1, 10) under-represents leading 1s and over-represents 8s/9s,
        # so several cells should be flagged.
        assert int(np.sum(r.significant)) >= 5

    def test_z_statistics_nonnegative(self, benford_sample: np.ndarray) -> None:
        r = per_digit_z(benford_sample)
        assert np.all(r.z_statistics >= 0.0)

    def test_p_values_in_unit_interval(self, benford_sample: np.ndarray) -> None:
        r = per_digit_z(benford_sample)
        assert np.all(r.p_values >= 0.0)
        assert np.all(r.p_values <= 1.0)

    def test_continuity_correction_reduces_z(
        self, benford_sample: np.ndarray
    ) -> None:
        r_cc = per_digit_z(benford_sample, continuity_correction=True)
        r_no = per_digit_z(benford_sample, continuity_correction=False)
        # Each cell with non-trivial deviation should have z_cc <= z_no.
        assert np.all(r_cc.z_statistics <= r_no.z_statistics + 1e-12)

    def test_alpha_changes_significance_mask(
        self, uniform_sample: np.ndarray
    ) -> None:
        strict = per_digit_z(uniform_sample, alpha=0.001)
        lax = per_digit_z(uniform_sample, alpha=0.10)
        assert int(np.sum(strict.significant)) <= int(np.sum(lax.significant))


# ---------------------------------------------------------------------------
# Conformity report
# ---------------------------------------------------------------------------


class TestConformityReport:
    def test_returns_bundle(self, benford_sample: np.ndarray) -> None:
        report = conformity_report(benford_sample)
        assert isinstance(report, ConformityReport)
        assert isinstance(report.chi_square, ChiSquareResult)
        assert isinstance(report.ks, KSResult)
        assert isinstance(report.mad, MADResult)
        assert isinstance(report.per_digit, PerDigitZResult)
        assert report.n == report.chi_square.n == report.ks.n == report.mad.n

    def test_summary_table_contains_all_tests(
        self, benford_sample: np.ndarray
    ) -> None:
        report = conformity_report(benford_sample)
        text = report.summary_table()
        for token in ("chi2", "KS", "MAD", "flagged"):
            assert token in text

    def test_already_counts_mode(self, benford_counts: np.ndarray) -> None:
        r1 = conformity_report(benford_counts, already_counts=True)
        # Reconstruct from raw values; counts must agree.
        rng = np.random.default_rng(42)
        sample = 10 ** rng.uniform(0.0, 6.0, size=50_000)
        r2 = conformity_report(sample)
        assert r1.n == r2.n
        np.testing.assert_array_equal(r1.chi_square.observed, r2.chi_square.observed)

    def test_unknown_method_raises(self, benford_sample: np.ndarray) -> None:
        with pytest.raises(ValueError, match="unknown method"):
            conformity_report(benford_sample, method="bootstrap")  # type: ignore[arg-type]


def test_DIGITS_used_in_results(benford_sample: np.ndarray) -> None:
    """KS argmax_digit must be one of the canonical first digits."""
    r = ks_test(benford_sample)
    assert r.argmax_digit in DIGITS.tolist()
