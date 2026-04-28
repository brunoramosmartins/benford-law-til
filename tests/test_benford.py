"""Tests for src.benford."""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.benford import (
    DIGITS,
    benford_pmf,
    empirical_frequencies,
    first_digit,
    first_digits,
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
