"""Benford's Law — first-digit extraction and theoretical PMF.

Implements the two primitives that every later phase depends on:

* :func:`first_digit` — extract the leading significant digit of a real
  number, robust to negative numbers, zeros, scientific notation, and
  values smaller than 1.
* :func:`benford_pmf` — the theoretical probability mass function
  :math:`P(d) = \\log_{10}\\!\\left(1 + \\tfrac{1}{d}\\right)` for
  :math:`d \\in \\{1, \\ldots, 9\\}`.
* :func:`empirical_frequencies` — count first-digit frequencies in a
  one-dimensional array of positive numbers.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final

import numpy as np
from numpy.typing import ArrayLike, NDArray

DIGITS: Final[NDArray[np.int_]] = np.arange(1, 10)
"""The nine possible first significant digits, ``[1, 2, ..., 9]``."""


def first_digit(x: float) -> int:
    """Return the first significant digit of a real number.

    The first significant digit is the leftmost non-zero digit of the decimal
    representation of ``|x|``. It is undefined for ``x = 0``; callers must
    filter zeros upstream.

    Parameters
    ----------
    x : float
        A nonzero real number. Negative inputs are handled via ``abs``.

    Returns
    -------
    int
        An integer in ``{1, 2, ..., 9}``.

    Raises
    ------
    ValueError
        If ``x`` is zero or not finite (NaN / inf).

    Examples
    --------
    >>> first_digit(1234.5)
    1
    >>> first_digit(0.000789)
    7
    >>> first_digit(-42)
    4
    >>> first_digit(9.99e-12)
    9
    """
    if not np.isfinite(x):
        raise ValueError(f"first_digit is undefined for non-finite input: {x!r}")
    if x == 0:
        raise ValueError("first_digit is undefined for zero")
    abs_x = abs(float(x))
    # Mantissa in [1, 10): m = abs_x / 10**floor(log10(abs_x))
    exponent = int(np.floor(np.log10(abs_x)))
    mantissa = abs_x / 10.0**exponent
    # Floating-point can push 9.9999... slightly below 10 or 1.0 slightly
    # below 1; clamp the integer part defensively.
    digit = int(mantissa)
    if digit < 1:
        digit = 1
    elif digit > 9:
        digit = 9
    return digit


def first_digits(values: ArrayLike) -> NDArray[np.int_]:
    """Vectorised :func:`first_digit` for a 1-D array of nonzero reals.

    Parameters
    ----------
    values : array-like of float
        Nonzero finite real numbers. Zeros and non-finite entries must be
        filtered by the caller.

    Returns
    -------
    ndarray of int
        Array of first significant digits, same length as ``values``.

    Raises
    ------
    ValueError
        If ``values`` contains zero or non-finite entries.
    """
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"first_digits expects a 1-D array, got ndim={arr.ndim}")
    if not np.all(np.isfinite(arr)):
        raise ValueError("first_digits: input contains NaN or inf")
    if np.any(arr == 0):
        raise ValueError("first_digits: input contains zero")

    abs_arr = np.abs(arr)
    exponents = np.floor(np.log10(abs_arr)).astype(int)
    mantissas = abs_arr / 10.0**exponents
    digits = mantissas.astype(int)
    return np.clip(digits, 1, 9)


def benford_pmf(d: int | Iterable[int] | None = None) -> float | NDArray[np.float64]:
    """Theoretical Benford probability mass function.

    Computes :math:`P(d) = \\log_{10}\\!\\left(1 + \\tfrac{1}{d}\\right)`
    for one or more leading-digit values.

    Parameters
    ----------
    d : int, iterable of int, or None
        - If ``int``: returns ``P(d)`` as a float.
        - If iterable: returns an array of ``P(d_i)``.
        - If ``None``: returns the full PMF over ``[1, 2, ..., 9]``.

    Returns
    -------
    float or ndarray of float
        Probability mass(es). Sums to 1 over ``d = 1..9``.

    Notes
    -----
    The Benford distribution is

    .. math::

        P(d) = \\log_{10}\\!\\left(1 + \\frac{1}{d}\\right),
        \\qquad d \\in \\{1, 2, \\ldots, 9\\}.

    Examples
    --------
    >>> round(benford_pmf(1), 4)
    0.301
    >>> round(benford_pmf(9), 4)
    0.0458
    >>> pmf = benford_pmf()
    >>> round(float(pmf.sum()), 6)
    1.0
    """
    if d is None:
        d_arr = DIGITS
        return np.log10(1.0 + 1.0 / d_arr)
    if isinstance(d, int):
        if not 1 <= d <= 9:
            raise ValueError(f"benford_pmf: d must be in 1..9, got {d}")
        return float(np.log10(1.0 + 1.0 / d))
    d_arr = np.asarray(list(d), dtype=int)
    if np.any((d_arr < 1) | (d_arr > 9)):
        raise ValueError("benford_pmf: all digits must be in 1..9")
    return np.log10(1.0 + 1.0 / d_arr)


def empirical_frequencies(values: ArrayLike) -> NDArray[np.float64]:
    """Empirical first-digit frequencies for a sample.

    Parameters
    ----------
    values : array-like of float
        Nonzero finite real numbers.

    Returns
    -------
    ndarray of float, shape (9,)
        Empirical proportion of values whose first significant digit is
        ``d``, for ``d = 1, 2, ..., 9``. Sums to 1.

    Examples
    --------
    >>> import numpy as np
    >>> rng = np.random.default_rng(0)
    >>> # Log-uniform sample is (asymptotically) Benford-conforming.
    >>> sample = 10 ** rng.uniform(0, 6, size=100_000)
    >>> freq = empirical_frequencies(sample)
    >>> bool(np.all(np.abs(freq - benford_pmf()) < 0.01))
    True
    """
    digits = first_digits(values)
    counts = np.bincount(digits, minlength=10)[1:10]
    n = counts.sum()
    if n == 0:
        raise ValueError("empirical_frequencies: empty input")
    return counts / n
