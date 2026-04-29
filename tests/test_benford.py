"""Tests for src.benford."""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.benford import (
    DIGITS,
    SECOND_DIGITS,
    benford_pmf,
    empirical_frequencies,
    first_digit,
    first_digits,
    joint_first_two_digits_pmf,
    log_mantissa,
    mantissa,
    second_digit_pmf,
)


class TestFirstDigit:
    """Edge cases for first_digit (single-value)."""

    @pytest.mark.parametrize(
        "x, expected",
        [
            (1, 1),
            (9, 9),
            (10, 1),
            (1234, 1),
            (9876, 9),
            (0.000789, 7),  # leading zeros
            (1e-12, 1),  # very small
            (9.99e12, 9),  # very large
            (-42, 4),  # negative
            (3.14, 3),
        ],
    )
    def test_known_values(self, x: float, expected: int) -> None:
        assert first_digit(x) == expected

    def test_scientific_notation_python_literal(self) -> None:
        # Python parses 7e-3 as the float 0.007, whose first digit is 7.
        assert first_digit(7e-3) == 7

    @pytest.mark.parametrize("bad", [0, 0.0, -0.0])
    def test_zero_raises(self, bad: float) -> None:
        with pytest.raises(ValueError, match="zero"):
            first_digit(bad)

    @pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
    def test_non_finite_raises(self, bad: float) -> None:
        with pytest.raises(ValueError, match="non-finite"):
            first_digit(bad)

    def test_returns_int_not_numpy(self) -> None:
        result = first_digit(123.45)
        assert isinstance(result, int)


class TestFirstDigitsVectorised:
    """Vectorised first_digits."""

    def test_matches_scalar(self) -> None:
        values = [1, 9, 10, 1234, 0.000789, -42, 3.14]
        expected = np.array([first_digit(v) for v in values])
        np.testing.assert_array_equal(first_digits(values), expected)

    def test_rejects_2d(self) -> None:
        with pytest.raises(ValueError, match="1-D"):
            first_digits(np.array([[1, 2], [3, 4]]))

    def test_rejects_zero(self) -> None:
        with pytest.raises(ValueError, match="zero"):
            first_digits([1, 2, 0, 4])

    def test_rejects_nan(self) -> None:
        with pytest.raises(ValueError, match="NaN or inf"):
            first_digits([1.0, float("nan"), 3.0])


class TestBenfordPMF:
    """Theoretical PMF properties."""

    def test_known_value_d1(self) -> None:
        # P(1) = log10(2) ≈ 0.30103
        assert math.isclose(benford_pmf(1), math.log10(2.0), rel_tol=1e-12)

    def test_known_value_d9(self) -> None:
        # P(9) = log10(10/9) ≈ 0.04576
        assert math.isclose(benford_pmf(9), math.log10(10.0 / 9.0), rel_tol=1e-12)

    def test_full_pmf_sums_to_one(self) -> None:
        pmf = benford_pmf()
        assert math.isclose(float(pmf.sum()), 1.0, rel_tol=1e-12)

    def test_full_pmf_shape(self) -> None:
        pmf = benford_pmf()
        assert pmf.shape == (9,)

    def test_iterable_input(self) -> None:
        pmf = benford_pmf([1, 2, 3])
        np.testing.assert_allclose(
            pmf,
            [math.log10(2), math.log10(1.5), math.log10(4 / 3)],
            rtol=1e-12,
        )

    def test_monotonically_decreasing(self) -> None:
        pmf = benford_pmf()
        assert np.all(np.diff(pmf) < 0)

    @pytest.mark.parametrize("bad", [0, 10, -1, 100])
    def test_invalid_digit_raises(self, bad: int) -> None:
        with pytest.raises(ValueError):
            benford_pmf(bad)


class TestEmpiricalFrequencies:
    """Empirical frequency tabulation."""

    def test_log_uniform_converges_to_benford(self) -> None:
        rng = np.random.default_rng(42)
        sample = 10 ** rng.uniform(0.0, 6.0, size=200_000)
        freq = empirical_frequencies(sample)
        np.testing.assert_allclose(freq, benford_pmf(), atol=0.005)

    def test_uniform_does_not_match_benford(self) -> None:
        rng = np.random.default_rng(42)
        sample = rng.uniform(1.0, 10.0, size=200_000)
        freq = empirical_frequencies(sample)
        # Uniform on [1, 10) gives roughly 1/9 per digit; this is far from
        # Benford for d=1.
        assert abs(freq[0] - benford_pmf(1)) > 0.10

    def test_returns_proportions(self) -> None:
        freq = empirical_frequencies([1, 2, 3, 4, 5, 6, 7, 8, 9])
        np.testing.assert_allclose(freq, np.full(9, 1.0 / 9.0))

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            empirical_frequencies(np.array([], dtype=float))


def test_DIGITS_constant() -> None:
    np.testing.assert_array_equal(DIGITS, np.arange(1, 10))


def test_SECOND_DIGITS_constant() -> None:
    np.testing.assert_array_equal(SECOND_DIGITS, np.arange(0, 10))


class TestMantissa:
    """Mantissa decomposition X = r * 10**k with r in [1, 10)."""

    @pytest.mark.parametrize(
        "x, expected",
        [
            (1.0, 1.0),
            (9.99, 9.99),
            (1234.0, 1.234),
            (0.0789, 7.89),
            (-42.0, 4.2),
            (1e-12, 1.0),
            (9.99e12, 9.99),
        ],
    )
    def test_known_values(self, x: float, expected: float) -> None:
        np.testing.assert_allclose(mantissa(x), expected, rtol=1e-10)

    def test_in_range(self) -> None:
        rng = np.random.default_rng(0)
        # Spread across many orders of magnitude.
        sample = 10 ** rng.uniform(-12, 12, size=10_000)
        m = mantissa(sample)
        assert np.all(m >= 1.0)
        assert np.all(m < 10.0)

    def test_first_digit_consistency(self) -> None:
        """floor(mantissa(X)) == first_digit(X) for all valid X."""
        rng = np.random.default_rng(1)
        sample = 10 ** rng.uniform(-6, 6, size=5_000)
        np.testing.assert_array_equal(
            np.floor(mantissa(sample)).astype(int),
            first_digits(sample),
        )

    def test_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="zero"):
            mantissa([1.0, 0.0, 3.0])


class TestLogMantissa:
    """Fractional part of log10(|X|), in [0, 1)."""

    def test_in_range(self) -> None:
        rng = np.random.default_rng(2)
        sample = 10 ** rng.uniform(-9, 9, size=10_000)
        y = log_mantissa(sample)
        assert np.all(y >= 0.0)
        assert np.all(y < 1.0)

    def test_log_uniform_input_yields_uniform_y(self) -> None:
        """If X = 10**U with U ~ Unif(0, k), then log_mantissa(X) ~ Unif(0,1)."""
        rng = np.random.default_rng(3)
        sample = 10 ** rng.uniform(0.0, 6.0, size=200_000)
        y = log_mantissa(sample)
        # Histogram: 10 bins, each should hold about 10% of samples.
        counts, _ = np.histogram(y, bins=10, range=(0.0, 1.0))
        proportions = counts / counts.sum()
        np.testing.assert_allclose(proportions, np.full(10, 0.1), atol=0.005)

    def test_matches_log10_mantissa(self) -> None:
        rng = np.random.default_rng(4)
        sample = 10 ** rng.uniform(-3, 3, size=1_000)
        np.testing.assert_allclose(
            log_mantissa(sample), np.log10(mantissa(sample)), rtol=1e-10
        )

    def test_first_digit_consistency(self) -> None:
        """First digit = d iff log10(d) <= log_mantissa(X) < log10(d+1)."""
        rng = np.random.default_rng(5)
        sample = 10 ** rng.uniform(-3, 3, size=2_000)
        y = log_mantissa(sample)
        digits = first_digits(sample)
        for d in range(1, 10):
            mask = digits == d
            if mask.sum() == 0:
                continue
            lo, hi = np.log10(d), np.log10(d + 1)
            assert np.all(y[mask] >= lo - 1e-12)
            assert np.all(y[mask] < hi + 1e-12)


class TestJointFirstTwoDigitsPMF:
    def test_known_value_10(self) -> None:
        # P(D1=1, D2=0) = log10(1 + 1/10) = log10(11/10)
        assert math.isclose(
            joint_first_two_digits_pmf(1, 0), math.log10(1.1), rel_tol=1e-12
        )

    def test_known_value_99(self) -> None:
        # P(D1=9, D2=9) = log10(1 + 1/99) = log10(100/99)
        assert math.isclose(
            joint_first_two_digits_pmf(9, 9),
            math.log10(100.0 / 99.0),
            rel_tol=1e-12,
        )

    def test_full_table_sums_to_one(self) -> None:
        total = sum(
            joint_first_two_digits_pmf(d1, d2)
            for d1 in range(1, 10)
            for d2 in range(0, 10)
        )
        assert math.isclose(total, 1.0, rel_tol=1e-12)

    @pytest.mark.parametrize(
        "d1, d2",
        [(0, 0), (10, 0), (-1, 5), (1, -1), (1, 10)],
    )
    def test_invalid_digits_raise(self, d1: int, d2: int) -> None:
        with pytest.raises(ValueError):
            joint_first_two_digits_pmf(d1, d2)


class TestSecondDigitPMF:
    def test_known_value_0(self) -> None:
        # Standard reference: P(D2=0) ≈ 0.11968.
        assert math.isclose(second_digit_pmf(0), 0.11968, abs_tol=5e-5)

    def test_known_value_9(self) -> None:
        # Standard reference: P(D2=9) ≈ 0.08499.
        assert math.isclose(second_digit_pmf(9), 0.08499, abs_tol=5e-5)

    def test_full_pmf_sums_to_one(self) -> None:
        pmf = second_digit_pmf()
        assert math.isclose(float(pmf.sum()), 1.0, rel_tol=1e-12)
        assert pmf.shape == (10,)

    def test_monotonically_decreasing(self) -> None:
        pmf = second_digit_pmf()
        # The second-digit law is monotonically decreasing across d=0..9.
        assert np.all(np.diff(pmf) < 0)

    def test_flatter_than_first_digit_law(self) -> None:
        # max - min for first-digit law:
        first_range = float(benford_pmf().max() - benford_pmf().min())
        second_range = float(second_digit_pmf().max() - second_digit_pmf().min())
        assert second_range < 0.5 * first_range

    @pytest.mark.parametrize("bad", [-1, 10, 99])
    def test_invalid_digit_raises(self, bad: int) -> None:
        with pytest.raises(ValueError):
            second_digit_pmf(bad)
