"""Tests for src.fraud."""

from __future__ import annotations

import numpy as np
import pytest

from src.benford import benford_pmf, empirical_frequencies
from src.fraud import (
    DetectionCurve,
    detection_power_curve,
    fabricate_values,
    inject_fraud,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_sample() -> np.ndarray:
    """Log-uniform Benford-conforming sample, n = 5,000."""
    rng = np.random.default_rng(7)
    return 10 ** rng.uniform(2.0, 6.0, size=5_000)


@pytest.fixture
def small_clean_sample() -> np.ndarray:
    """Smaller log-uniform sample for fast sweeps, n = 1,000."""
    rng = np.random.default_rng(11)
    return 10 ** rng.uniform(2.0, 5.0, size=1_000)


# ---------------------------------------------------------------------------
# fabricate_values
# ---------------------------------------------------------------------------


class TestFabricateValues:
    def test_returns_correct_length(self) -> None:
        rng = np.random.default_rng(0)
        out = fabricate_values(500, kind="uniform_digit", rng=rng)
        assert out.shape == (500,)

    def test_strictly_positive(self) -> None:
        rng = np.random.default_rng(1)
        for kind in ("uniform_digit", "round_numbers", "psychological"):
            out = fabricate_values(2_000, kind=kind, rng=rng)  # type: ignore[arg-type]
            assert np.all(out > 0), f"{kind!r} produced non-positive values"

    def test_uniform_digit_first_digits_uniform(self) -> None:
        rng = np.random.default_rng(2)
        out = fabricate_values(50_000, kind="uniform_digit", rng=rng)
        freq = empirical_frequencies(out)
        # Each first digit should appear ~11.1 %; tolerance generous.
        np.testing.assert_allclose(freq, np.full(9, 1.0 / 9.0), atol=0.01)

    def test_uniform_digit_violates_benford(self) -> None:
        rng = np.random.default_rng(3)
        out = fabricate_values(20_000, kind="uniform_digit", rng=rng)
        freq = empirical_frequencies(out)
        # Specifically: digit 1 should be ~11 %, far from Benford's ~30 %.
        assert abs(freq[0] - 1.0 / 9.0) < 0.01
        assert freq[0] < benford_pmf(1) - 0.10

    def test_psychological_overweights_middle_digits(self) -> None:
        rng = np.random.default_rng(4)
        out = fabricate_values(50_000, kind="psychological", rng=rng)
        freq = empirical_frequencies(out)
        # Middle digits 4 and 5 should be the modal first digits; 1 and 9 the
        # least common.
        assert freq[3] > freq[0]  # P(4) > P(1)
        assert freq[3] > freq[8]  # P(4) > P(9)
        assert freq[8] < 0.05  # digit 9 explicitly underweighted

    def test_round_numbers_concentrate_on_125(self) -> None:
        rng = np.random.default_rng(5)
        out = fabricate_values(20_000, kind="round_numbers", rng=rng)
        freq = empirical_frequencies(out)
        # Round-number anchors are 100, 200, 250, 500, 1000, 2000, 5000, 10000
        # (leading digits {1, 2, 5}). The 5% log-normal jitter bleeds some
        # mass to neighbouring digits (e.g. 100 -> 95 -> d=9), so we cannot
        # require the {1, 2, 5} mass to be near 1.0. We do require it to
        # exceed Benford's expectation P(1) + P(2) + P(5) ~ 0.556 by a
        # comfortable margin.
        assert (freq[0] + freq[1] + freq[4]) > 0.65

    def test_zero_n_returns_empty(self) -> None:
        out = fabricate_values(0)
        assert out.shape == (0,)

    def test_invalid_n_raises(self) -> None:
        with pytest.raises(ValueError, match="n must be >= 0"):
            fabricate_values(-1)

    @pytest.mark.parametrize(
        "window",
        [(0, 1e3), (1e3, 1e3), (-1, 1e3), (1e6, 1e3)],
    )
    def test_invalid_window_raises(self, window: tuple[float, float]) -> None:
        with pytest.raises(ValueError, match="magnitude_window"):
            fabricate_values(10, magnitude_window=window)

    def test_unknown_kind_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown kind"):
            fabricate_values(10, kind="bogus")  # type: ignore[arg-type]

    def test_seed_reproducibility(self) -> None:
        a = fabricate_values(100, rng=np.random.default_rng(123))
        b = fabricate_values(100, rng=np.random.default_rng(123))
        np.testing.assert_array_equal(a, b)


# ---------------------------------------------------------------------------
# inject_fraud
# ---------------------------------------------------------------------------


class TestInjectFraud:
    def test_returns_copy_not_view(self, clean_sample: np.ndarray) -> None:
        contaminated = inject_fraud(clean_sample, fraction=0.3)
        assert contaminated is not clean_sample
        assert not np.shares_memory(contaminated, clean_sample)

    def test_does_not_mutate_input(self, clean_sample: np.ndarray) -> None:
        before = clean_sample.copy()
        _ = inject_fraud(clean_sample, fraction=0.5, rng=np.random.default_rng(0))
        np.testing.assert_array_equal(clean_sample, before)

    def test_zero_fraction_returns_unchanged_copy(
        self, clean_sample: np.ndarray
    ) -> None:
        out = inject_fraud(clean_sample, fraction=0.0)
        np.testing.assert_array_equal(out, clean_sample)
        assert out is not clean_sample

    def test_full_fraction_replaces_everything(
        self, clean_sample: np.ndarray
    ) -> None:
        out = inject_fraud(clean_sample, fraction=1.0, rng=np.random.default_rng(0))
        # Identical-by-coincidence is astronomically unlikely; require zero overlap.
        overlap = np.intersect1d(out, clean_sample).size
        assert overlap < 5

    def test_intermediate_fraction_drifts_toward_uniform(
        self, clean_sample: np.ndarray
    ) -> None:
        rng = np.random.default_rng(0)
        contaminated = inject_fraud(
            clean_sample, fraction=0.5, kind="uniform_digit", rng=rng
        )
        freq = empirical_frequencies(contaminated)
        # Mid-mix: digit 1 should fall well below clean Benford and well
        # above the uniform-on-9 floor.
        assert 0.13 < freq[0] < benford_pmf(1)

    def test_invalid_fraction_raises(self, clean_sample: np.ndarray) -> None:
        with pytest.raises(ValueError, match="fraction"):
            inject_fraud(clean_sample, fraction=-0.1)
        with pytest.raises(ValueError, match="fraction"):
            inject_fraud(clean_sample, fraction=1.5)

    def test_rejects_non_positive(self) -> None:
        with pytest.raises(ValueError, match="strictly positive"):
            inject_fraud(np.array([1.0, 0.0, 3.0]), fraction=0.5)

    def test_rejects_2d(self) -> None:
        with pytest.raises(ValueError, match="1-D"):
            inject_fraud(np.array([[1.0, 2.0], [3.0, 4.0]]), fraction=0.5)

    def test_rejects_nan(self) -> None:
        with pytest.raises(ValueError, match="NaN or inf"):
            inject_fraud(np.array([1.0, float("nan"), 3.0]), fraction=0.5)

    def test_seed_reproducibility(self, clean_sample: np.ndarray) -> None:
        a = inject_fraud(
            clean_sample, fraction=0.3, rng=np.random.default_rng(99)
        )
        b = inject_fraud(
            clean_sample, fraction=0.3, rng=np.random.default_rng(99)
        )
        np.testing.assert_array_equal(a, b)


# ---------------------------------------------------------------------------
# detection_power_curve
# ---------------------------------------------------------------------------


class TestDetectionPowerCurve:
    def test_returns_dataclass(self, small_clean_sample: np.ndarray) -> None:
        curve = detection_power_curve(
            small_clean_sample,
            fractions=[0.0, 0.1, 0.5],
            n_trials=3,
            rng=np.random.default_rng(0),
        )
        assert isinstance(curve, DetectionCurve)
        assert curve.n == small_clean_sample.size
        assert curve.n_trials == 3
        assert curve.fractions.shape == (3,)
        assert curve.mad.shape == (3,)
        assert curve.chi_square.shape == (3,)
        assert curve.ks.shape == (3,)
        assert curve.rejection_rate_chi2_05.shape == (3,)

    def test_mad_increases_with_contamination(
        self, small_clean_sample: np.ndarray
    ) -> None:
        curve = detection_power_curve(
            small_clean_sample,
            fractions=[0.0, 0.25, 0.5, 0.75, 1.0],
            kind="uniform_digit",
            n_trials=5,
            rng=np.random.default_rng(42),
        )
        # MAD at 100 % contamination must exceed MAD at 0 %.
        assert curve.mad[-1] > curve.mad[0] + 0.01
        # Monotone-non-decreasing in expectation; allow a bit of MC noise.
        assert curve.mad[-1] > curve.mad[1]

    def test_rejection_rate_in_unit_interval(
        self, small_clean_sample: np.ndarray
    ) -> None:
        curve = detection_power_curve(
            small_clean_sample,
            fractions=[0.0, 0.5, 1.0],
            n_trials=4,
            rng=np.random.default_rng(0),
        )
        assert np.all(curve.rejection_rate_chi2_05 >= 0.0)
        assert np.all(curve.rejection_rate_chi2_05 <= 1.0)

    def test_full_contamination_always_rejects(
        self, small_clean_sample: np.ndarray
    ) -> None:
        # At 100 % contamination on uniform_digit fabrication, chi-squared
        # must reject every trial.
        curve = detection_power_curve(
            small_clean_sample,
            fractions=[1.0],
            kind="uniform_digit",
            n_trials=5,
            rng=np.random.default_rng(1),
        )
        assert curve.rejection_rate_chi2_05[0] == 1.0

    def test_invalid_fraction_raises(self, small_clean_sample: np.ndarray) -> None:
        with pytest.raises(ValueError, match="fraction"):
            detection_power_curve(
                small_clean_sample,
                fractions=[0.0, 1.5],
                n_trials=1,
            )

    def test_invalid_n_trials_raises(self, small_clean_sample: np.ndarray) -> None:
        with pytest.raises(ValueError, match="n_trials"):
            detection_power_curve(
                small_clean_sample,
                fractions=[0.0, 0.5],
                n_trials=0,
            )

    def test_p_value_in_unit_interval(
        self, small_clean_sample: np.ndarray
    ) -> None:
        curve = detection_power_curve(
            small_clean_sample,
            fractions=[0.0, 0.5],
            n_trials=3,
            rng=np.random.default_rng(0),
        )
        assert np.all(curve.chi_square_p >= 0.0)
        assert np.all(curve.chi_square_p <= 1.0)
