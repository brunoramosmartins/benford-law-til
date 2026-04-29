# Phase 2 — Rigorous derivation: log-uniform mantissa

This is the analytic spine of the TIL. We derive

$$
P(d) = \log_{10}\!\left(1 + \frac{1}{d}\right), \qquad d \in \{1, 2, \ldots, 9\},
$$

from one premise: the fractional part of $\log_{10}(X)$ is uniform on $[0, 1)$. The derivation is short, but it requires care about a definition (the **mantissa**) and one easy-to-miss equivalence (the **first digit ↔ log-mantissa interval** correspondence).

---

## 1. The mantissa decomposition

### Definition 1 (mantissa and order of magnitude).

For any $X > 0$, the **mantissa** of $X$ is the unique real $r \in [1, 10)$ and the **order of magnitude** is the unique integer $k \in \mathbb{Z}$ such that

$$
X = r \cdot 10^k.
$$

### Proposition 1 (uniqueness).

The pair $(r, k)$ in Definition 1 is unique.

**Proof.** Take logarithms: $\log_{10}(X) = \log_{10}(r) + k$. Because $r \in [1, 10)$, we have $\log_{10}(r) \in [0, 1)$. So $k = \lfloor \log_{10}(X) \rfloor$ is forced (it is the unique integer such that $\log_{10}(X) - k \in [0, 1)$), and $r = X / 10^k$ then follows. $\blacksquare$

The mantissa carries all the information about *significant digits*: the first significant digit of $X$ equals $\lfloor r \rfloor$, the second is the first digit of $10 \cdot (r - \lfloor r \rfloor)$, and so on.

---

## 2. The log-uniform premise

Let $X$ be a positive random variable. Define

$$
Y := \log_{10}(X) \bmod 1 = \log_{10}(X) - \lfloor \log_{10}(X) \rfloor \in [0, 1).
$$

By Proposition 1, $Y = \log_{10}(r)$, i.e. $Y$ is the **log of the mantissa**.

### Premise (log-uniform mantissa).

$$
Y \sim \text{Uniform}(0, 1).
$$

This is *not* a tautology. It is an empirical assumption about the distribution of $X$. We will discuss when it holds in §6.

---

## 3. Connecting the first digit to $Y$

### Proposition 2 (first digit ↔ log-mantissa interval).

For $X > 0$ and $d \in \{1, 2, \ldots, 9\}$, the first significant digit of $X$ equals $d$ if and only if

$$
\log_{10}(d) \le Y < \log_{10}(d+1).
$$

**Proof.** Let $D_1$ be the first significant digit. Writing $X = r \cdot 10^k$ with $r \in [1, 10)$,

$$
D_1 = d \iff d \le r < d + 1.
$$

Take $\log_{10}$ on the inequality (it is monotone increasing on $(0, \infty)$):

$$
\log_{10}(d) \le \log_{10}(r) < \log_{10}(d + 1).
$$

But $\log_{10}(r) = Y$, so this is exactly $\log_{10}(d) \le Y < \log_{10}(d+1)$. $\blacksquare$

The intervals $[\log_{10}(d), \log_{10}(d+1))$ for $d = 1, \ldots, 9$ partition $[0, 1)$:

| $d$ | $\log_{10}(d)$ | $\log_{10}(d+1)$ | Width |
|---|---:|---:|---:|
| 1 | 0.00000 | 0.30103 | 0.30103 |
| 2 | 0.30103 | 0.47712 | 0.17609 |
| 3 | 0.47712 | 0.60206 | 0.12494 |
| 4 | 0.60206 | 0.69897 | 0.09691 |
| 5 | 0.69897 | 0.77815 | 0.07918 |
| 6 | 0.77815 | 0.84510 | 0.06695 |
| 7 | 0.84510 | 0.90309 | 0.05799 |
| 8 | 0.90309 | 0.95424 | 0.05115 |
| 9 | 0.95424 | 1.00000 | 0.04576 |

The widths shrink — this is what makes the distribution non-uniform.

---

## 4. Deriving the Benford PMF

### Theorem (Benford's law from the log-uniform premise).

Under the premise $Y \sim \text{Uniform}(0, 1)$,

$$
P(D_1 = d) = \log_{10}\!\left(1 + \frac{1}{d}\right), \qquad d \in \{1, \ldots, 9\}.
$$

**Proof.** By Proposition 2,

$$
P(D_1 = d) = \Pr\!\big[ \log_{10}(d) \le Y < \log_{10}(d+1) \big].
$$

Because $Y \sim \text{Uniform}(0, 1)$, the probability of the event $a \le Y < b$ for $0 \le a < b \le 1$ is just the length of the interval, which equals $\int_a^b 1 \, dy$. Substituting $a = \log_{10}(d)$ and $b = \log_{10}(d+1)$,

$$
P(D_1 = d) = \int_{\log_{10}(d)}^{\log_{10}(d+1)} 1 \, dy
            = \log_{10}(d+1) - \log_{10}(d).
$$

Combining the two log terms (single rule: $\log a - \log b = \log(a/b)$),

$$
P(D_1 = d) = \log_{10}\!\left(\frac{d+1}{d}\right) = \log_{10}\!\left(1 + \frac{1}{d}\right).
$$

$\blacksquare$

### Sanity check: the PMF sums to 1.

A telescoping sum:

$$
\sum_{d=1}^{9} P(d) = \sum_{d=1}^{9} \big[\log_{10}(d+1) - \log_{10}(d)\big]
                    = \log_{10}(10) - \log_{10}(1)
                    = 1.
$$

### Numerical table.

| $d$ | $P(d)$ |
|---:|---:|
| 1 | 0.30103 |
| 2 | 0.17609 |
| 3 | 0.12494 |
| 4 | 0.09691 |
| 5 | 0.07918 |
| 6 | 0.06695 |
| 7 | 0.05799 |
| 8 | 0.05115 |
| 9 | 0.04576 |

These are exactly the interval widths from §3. The figure $\approx 30\%$ chance of a leading $1$ versus $\approx 4.6\%$ for a leading $9$ is the headline result.

---

## 5. Generalization: the second-digit law

The same derivation extends to *pairs* of significant digits. Write $X = r \cdot 10^k$ as before, and let $D_1, D_2$ be the first two significant digits. Then $D_1 = d_1$ and $D_2 = d_2$ if and only if

$$
\frac{10 d_1 + d_2}{10} \le r < \frac{10 d_1 + d_2 + 1}{10},
$$

equivalently

$$
\log_{10}(10 d_1 + d_2) - 1 \le Y < \log_{10}(10 d_1 + d_2 + 1) - 1.
$$

(The $-1$ is the $\log_{10}(10)$ from dividing by $10$.) Under $Y \sim \text{Uniform}(0, 1)$ the width of this interval is

$$
P(D_1 = d_1, D_2 = d_2) = \log_{10}\!\left(1 + \frac{1}{10 d_1 + d_2}\right).
$$

Marginalising over $d_1$ gives the **second-digit law**:

$$
P(D_2 = d_2) = \sum_{d_1 = 1}^{9} \log_{10}\!\left(1 + \frac{1}{10 d_1 + d_2}\right),
\qquad d_2 \in \{0, 1, \ldots, 9\}.
$$

| $d_2$ | $P(D_2 = d_2)$ |
|---:|---:|
| 0 | 0.11968 |
| 1 | 0.11389 |
| 2 | 0.10882 |
| 3 | 0.10433 |
| 4 | 0.10031 |
| 5 | 0.09668 |
| 6 | 0.09337 |
| 7 | 0.09035 |
| 8 | 0.08757 |
| 9 | 0.08499 |

Notice how flat this is compared to the first-digit law — the spread between the largest and smallest entries is about $0.035$, versus $0.255$ for the first-digit law. The further into the significant digits one goes, the closer the distribution gets to uniform — a fact that is itself diagnostic in fraud detection.

---

## 6. When is the log-uniform premise plausible?

The derivation is unconditional: *given* $Y \sim \text{Uniform}(0, 1)$, Benford follows. The empirical question is when the premise itself holds. Three rules of thumb:

1. **The data must span many orders of magnitude.** If $X$ ranges only between, say, $50$ and $500$, the support of $Y$ is concentrated in $[\log_{10} 50 - 1, \log_{10} 500 - 1] = [0.699, 0.699]$ — a single point modulo $1$ — and is nowhere near uniform. (Adult human heights, in centimetres, span about $1.5$–$2.0$ — less than $0.13$ orders of magnitude. They fail Benford for exactly this reason; see Phase 1's empirical figure.)

2. **No hard bounds.** If the data is censored at a maximum (e.g., scores out of $100$), the upper tail of $\log_{10}(X)$ is truncated, which biases $Y$.

3. **Multiplicative-type processes.** When $X = X_1 \cdot X_2 \cdots X_n$ for independent positive factors, $\log(X) = \sum \log(X_i)$ approaches a normal distribution by the central limit theorem. A normal $\log_{10}(X)$ with large enough variance is well-approximated by a uniform $\log_{10}(X) \bmod 1$ (the wider the bell, the closer the mod-$1$ residue is to uniform — formally, this is again equidistribution).

These conditions are *empirical*, not necessary. There exist exotic distributions that satisfy the premise without satisfying any of (1)–(3); but in applied work, (1)–(3) are the practical signal that Benford should hold.

---

## 7. What is left to do

This phase derived $P(d) = \log_{10}(1 + 1/d)$ from a *probabilistic* premise about the log-mantissa. Phase 3 will derive the same formula from a completely different premise — **scale invariance** under change of unit — and demonstrate that the two paths converge on the same curve for non-coincidental reasons.

That convergence is the central evidence that Benford's law is structural rather than accidental.

---

## References

- **Hill, T. P.** (1995). A statistical derivation of the significant-digit law. *Statistical Science*, **10**(4), 354–363.
- **Berger, A. & Hill, T. P.** (2015). *An Introduction to Benford's Law*. Princeton University Press. — Chapter 4 covers the significant-digit law in measure-theoretic generality.
