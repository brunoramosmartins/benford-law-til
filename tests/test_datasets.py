"""Tests for src.datasets."""

from __future__ import annotations

import numpy as np
import pytest

from src.benford import benford_pmf, empirical_frequencies
from src.datasets import (
    WORLD_CITIES_CSV,
    adult_heights,
    fibonacci_sample,
    load_world_cities,
)


class TestFibonacciSample:
    def test_first_terms(self) -> None:
        fib = fibonacci_sample(10)
        # F_1..F_10 = 1, 1, 2, 3, 5, 8, 13, 21, 34, 55
        np.testing.assert_allclose(
            fib, [1, 1, 2, 3, 5, 8, 13, 21, 34, 55], atol=1e-6
        )

    def test_default_length(self) -> None:
        assert fibonacci_sample().shape == (1000,)

    def test_strictly_positive(self) -> None:
        fib = fibonacci_sample(100)
        assert np.all(fib > 0)

    def test_first_digits_approach_benford(self) -> None:
        # Fibonacci first digits are equidistributed mod 1 in log10 → Benford.
        fib = fibonacci_sample(1000)
        freq = empirical_frequencies(fib)
        # Looser tolerance than the log-uniform test: 1000 samples is small.
        np.testing.assert_allclose(freq, benford_pmf(), atol=0.04)

    @pytest.mark.parametrize("bad", [0, -1, 1001])
    def test_invalid_n_raises(self, bad: int) -> None:
        with pytest.raises(ValueError):
            fibonacci_sample(bad)


class TestAdultHeights:
    def test_shape(self) -> None:
        assert adult_heights(n=500).shape == (500,)

    def test_strictly_positive(self) -> None:
        h = adult_heights(n=10_000)
        assert np.all(h > 0)

    def test_seed_reproducibility(self) -> None:
        a = adult_heights(n=100, seed=7)
        b = adult_heights(n=100, seed=7)
        np.testing.assert_array_equal(a, b)

    def test_does_not_match_benford(self) -> None:
        # The whole point of this dataset.
        h = adult_heights(n=20_000, seed=0)
        freq = empirical_frequencies(h)
        # Heights cluster near 170 → digit 1 dominates well above the
        # Benford prediction of ~0.30.
        assert freq[0] > 0.55

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"n": 0},
            {"n": -5},
            {"sd_cm": 0},
            {"sd_cm": -1.0},
        ],
    )
    def test_invalid_args_raise(self, kwargs: dict) -> None:
        with pytest.raises(ValueError):
            adult_heights(**kwargs)


class TestLoadWorldCities:
    def test_missing_file_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Point the loader at a path that doesn't exist.
        from src import datasets

        monkeypatch.setattr(datasets, "WORLD_CITIES_CSV", WORLD_CITIES_CSV.with_name("nope.csv"))
        with pytest.raises(FileNotFoundError, match="build_datasets"):
            datasets.load_world_cities()

    @pytest.mark.skipif(
        not WORLD_CITIES_CSV.exists(),
        reason="data/raw/world_cities.csv not built — run scripts/build_datasets.py",
    )
    def test_loads_when_file_present(self) -> None:
        df = load_world_cities()
        assert len(df) > 0
        assert "population" in df.columns
        assert (df["population"] >= 1).all()

    @pytest.mark.skipif(
        not WORLD_CITIES_CSV.exists(),
        reason="data/raw/world_cities.csv not built — run scripts/build_datasets.py",
    )
    def test_population_first_digits_close_to_benford(self) -> None:
        df = load_world_cities(min_population=1)
        freq = empirical_frequencies(df["population"].to_numpy())
        # GeoNames cities5000 has a hard 5,000-population floor. This
        # creates a structural spike at d=5 (cities at 5,xxx are common
        # because everything below 5,000 was excluded) and shifts the
        # tail digits up. The fit is still qualitatively Benford —
        # digit 1 dominates and the overall L1 distance is modest — but
        # we cannot expect strict monotonicity nor a textbook tolerance.
        assert abs(freq[0] - benford_pmf(1)) < 0.02
        assert freq[0] == freq.max()
        l1 = float(np.sum(np.abs(freq - benford_pmf())))
        assert l1 < 0.35
