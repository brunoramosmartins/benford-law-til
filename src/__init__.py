"""Reusable Benford's Law module.

Public API
----------

* :mod:`src.benford` — first-digit extraction, mantissa decomposition,
  theoretical PMFs.
* :mod:`src.conformity` — chi-squared, Kolmogorov-Smirnov, MAD, and
  per-digit Z conformity tests with structured result objects.
* :mod:`src.fraud` — fraud-injection and detection-power experiments.
* :mod:`src.datasets` — bundled-data loaders and synthetic samples
  (world cities, Fibonacci, adult heights).

Most users will import the headline helpers from the submodules directly,
e.g. ``from src.benford import benford_pmf, first_digits`` and
``from src.conformity import conformity_report``.
"""

from __future__ import annotations

__version__ = "0.6.0"
