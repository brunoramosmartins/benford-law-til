# Phase 4 — Statistical conformity tests

Phases 1–3 answered *what is the law?* Phase 4 answers *does this dataset obey it?* Given an empirical first-digit distribution $\hat{P}(1), \ldots, \hat{P}(9)$, we want a principled way to decide how close it is to the theoretical $P(d) = \log_{10}(1 + 1/d)$.

This phase derives **four** complementary tests, each with a different sensitivity profile, and gives the rule for choosing among them.

| Test | Statistic | Sensitive to | Sample-size invariant? |
|---|---|---|---|
| Pearson $\chi^2$ | $\sum_d (O_d - E_d)^2 / E_d$ | per-cell deviation | No (over-rejects at large $n$) |
| Kolmogorov–Smirnov | $\max_d \lvert F_n(d) - F(d) \rvert$ | cumulative drift | No |
| MAD | $\frac{1}{9} \sum_d \lvert \hat{P}(d) - P(d) \rvert$ | average per-cell drift | **Yes** |
| Per-digit $Z$ | per-cell $z_d$ | which digit is off | No |

Each test has a different failure mode. No single statistic is "the right one"; the four together form a diagnostic toolkit.

---

## 1. Setup and notation

Let $X_1, \ldots, X_n$ be a sample of positive reals. Write $D_i = D(X_i)$ for the first significant digit of $X_i$. Define

$$
O_d = \#\{i : D_i = d\}, \qquad \hat{P}(d) = O_d / n, \qquad E_d = n \, P(d),
$$

with $P(d) = \log_{10}(1 + 1/d)$ the theoretical Benford PMF. The null hypothesis throughout is

$$
H_0: \Pr[D_i = d] = P(d) \quad \text{for all } d \in \{1, \ldots, 9\}.
$$

The four tests differ in *how* they collapse the 9-dimensional vector $(O_1, \ldots, O_9)$ into a single statistic.

---

## 2. Pearson's chi-squared test

### 2.1 Derivation

If $H_0$ holds and the $D_i$ are i.i.d., the count vector $(O_1, \ldots, O_9)$ is multinomial with parameters $(n; P(1), \ldots, P(9))$. The classical theorem (Cramér 1946) says the rescaled deviations

$$
\chi^2 = \sum_{d=1}^{9} \frac{(O_d - E_d)^2}{E_d}
$$

converge in distribution, as $n \to \infty$, to $\chi^2_{k-1}$ where $k = 9$ is the number of cells. Eight degrees of freedom: there are 9 cells, but they sum to $n$, removing one.

**Sketch of why $\chi^2_8$.** Under $H_0$, by the multinomial central limit theorem the standardized residuals $Z_d = (O_d - E_d) / \sqrt{E_d}$ are jointly asymptotically normal with mean $0$ and a covariance whose only off-diagonal structure comes from the constraint $\sum O_d = n$. The constraint forces the joint distribution onto an 8-dimensional hyperplane; the squared norm $\sum Z_d^2$ on that hyperplane is exactly $\chi^2_8$.

### 2.2 Decision rule

Reject $H_0$ at level $\alpha$ iff $\chi^2 > \chi^2_{8, 1 - \alpha}$. For $\alpha = 0.05$ the critical value is $\chi^2_{8, 0.95} \approx 15.51$.

### 2.3 The excess-power problem

The chi-squared test has an unavoidable defect when used on real datasets: as $n \to \infty$ with a fixed *deviation pattern*, $\chi^2$ scales linearly in $n$. A per-cell drift of $0.001$ — too small to matter for any forensic purpose — becomes "statistically significant" once $n$ crosses $\sim 10^5$.

This is not a bug; it is the test answering the question it was designed to answer ("is the deviation literally zero?"). For real applications, the question of interest is "is the deviation *practically meaningful*?", which $\chi^2$ does not address. That is the gap MAD fills (§4).

---

## 3. Kolmogorov–Smirnov

### 3.1 Statistic

The discrete-CDF KS statistic is

$$
D_n = \max_{d \in \{1, \ldots, 9\}} \lvert F_n(d) - F(d) \rvert,
\qquad
F(d) = \sum_{j=1}^{d} P(j),
\qquad
F_n(d) = \sum_{j=1}^{d} \hat{P}(j).
$$

By the Glivenko–Cantelli theorem $D_n \to 0$ a.s. under $H_0$, and $\sqrt{n} \, D_n$ converges to the supremum of a Brownian bridge — the *Kolmogorov distribution*. The asymptotic p-value is

$$
p \approx 1 - K(\sqrt{n} \, D_n), \qquad K(x) = 1 - 2 \sum_{k=1}^{\infty} (-1)^{k - 1} e^{-2 k^2 x^2}.
$$

We compute it via `scipy.stats.kstwobign.sf`.

### 3.2 What KS sees that $\chi^2$ does not

Suppose the data are systematically biased toward small digits — every $\hat{P}(d)$ for small $d$ is slightly inflated, every $\hat{P}(d)$ for large $d$ slightly deflated. Each per-cell deviation is small (so $\chi^2$ may not flag), but the *cumulative* gap $F_n(d) - F(d)$ grows with $d$ before shrinking back to zero at $d = 9$. KS picks this up; $\chi^2$ averages it away.

### 3.3 The discreteness caveat

The Kolmogorov distribution is derived for *continuous* CDFs. On a discrete distribution the test is **conservative** — the true level is below the nominal $\alpha$. For sharp inference on a small support like $\{1, \ldots, 9\}$, prefer the chi-squared test or a parametric bootstrap. KS is included here as a *diagnostic*: its argmax (which digit maximises the gap) is a useful fingerprint of the deviation pattern.

---

## 4. MAD with Nigrini's thresholds

### 4.1 Statistic

$$
\mathrm{MAD} = \frac{1}{9} \sum_{d=1}^{9} \lvert \hat{P}(d) - P(d) \rvert.
$$

Notice that MAD depends only on the empirical *proportions*, not on the sample size. This is the property that makes it useful at scale.

### 4.2 Nigrini's verdict table

Nigrini (2012, *Benford's Law*, Wiley, Ch. 7) calibrates MAD against thousands of forensic-accounting datasets and gives a qualitative scale:

| MAD range | Verdict |
|---|---|
| $[0, 0.006)$ | Close conformity |
| $[0.006, 0.012)$ | Acceptable conformity |
| $[0.012, 0.015)$ | Marginally acceptable conformity |
| $[0.015, \infty)$ | Non-conformity |

These cut-points are *empirical*, not derived from a sampling distribution. Their virtue is operational: they map a single number to an action ("investigate" vs. "move on") without depending on $n$.

### 4.3 Why sample-size invariance matters

Imagine auditing a stream of $10^7$ transactions. Even if the data are essentially Benford-conforming, $\chi^2$ will reject because tiny deviations get amplified to "significance" by the sample size. MAD does not. In practice, Nigrini's MAD is the workhorse of forensic Benford auditing precisely because it asks the *right* question: how big is the average deviation, regardless of how much data we have?

The trade-off: MAD has no formal sampling distribution, no p-value, and no calibration to a specific level $\alpha$. It is a *summary*, not a *test*. We use it alongside $\chi^2$ — not instead of it — to triangulate.

---

## 5. Per-digit $Z$-statistic

### 5.1 Statistic

For each digit $d \in \{1, \ldots, 9\}$, treat $O_d \sim \text{Binomial}(n, P(d))$ under $H_0$ and form the standardized two-sided $z$:

$$
z_d = \frac{\lvert \hat{P}(d) - P(d) \rvert - \frac{1}{2 n}}
            {\sqrt{P(d) (1 - P(d)) / n}}.
$$

The $\frac{1}{2 n}$ term is *Yates' continuity correction* — it adjusts for the discreteness of the binomial when approximated by the normal. We apply it whenever it does not flip the numerator's sign.

### 5.2 Decision and diagnostic role

Reject the per-cell null at level $\alpha$ iff $z_d > z_{1 - \alpha/2}$. For $\alpha = 0.05$ this is $|z_d| > 1.96$.

The per-digit test has no claim to *family-wise* error control — at $\alpha = 0.05$ across nine cells we expect $\sim 0.45$ false positives per Benford-conforming dataset. Treat the significant mask as descriptive: it flags *which* digits the data are pulling away from. A single flag at $d = 1$ (under-represented) suggests data with a hard floor or padded categories; flags at $d \in \{8, 9\}$ (over-represented) are Nigrini's classic "round-number-bias" signature, where humans round up to the next 100 / 1000 / etc.

### 5.3 Combining with chi-squared

The clean workflow is:
1. Run $\chi^2$ for an honest family-wise test.
2. *If* $\chi^2$ rejects, run per-digit $Z$ to localise *where* the deviation is.

Reversing the order leads to the standard multiple-comparisons fallacy.

---

## 6. Choosing among the four

| Goal | Use |
|---|---|
| Honest hypothesis test, moderate $n$ | $\chi^2$ |
| Localise *which* digit is off | per-digit $Z$ |
| Audit a forensic dataset with $n \gg 10^5$ | MAD |
| Detect *cumulative* (not per-cell) drift | KS |
| Single dataset, general conformity check | All four — `conformity_report` |

The four-test bundle is what `src.conformity.conformity_report` returns. The three follow-up phases use it in increasing order of stakes:

* **Phase 5** — apply the bundle to four datasets (cities, Fibonacci, heights, COVID-19 county-day counts) and compare.
* **Phase 6** — calibrate the *detection-power* trade-off for forensic use: how large does a cooked-books deviation need to be before the bundle reliably flags it?
* **Phase 7** — final article. The bundle is the empirical thread that runs from "the law" to "the test" to "the audit".

---

## 7. Implementation map

The implementation in `src/conformity.py` mirrors §§2–5 one-to-one:

| Function | Returns | Section |
|---|---|---|
| `chi_square_test` | `ChiSquareResult` | §2 |
| `ks_test` | `KSResult` | §3 |
| `mad_test` | `MADResult` (with Nigrini verdict) | §4 |
| `per_digit_z` | `PerDigitZResult` (with significant mask) | §5 |
| `conformity_report` | `ConformityReport` (all four bundled) | §6 |

All four accept either raw values or a precomputed length-9 count vector via `already_counts=True`. The dataclasses are frozen so a result can be safely passed around and re-rendered without mutation.

---

## 8. References

* **Cramér, H.** (1946). *Mathematical Methods of Statistics*. Princeton University Press. — Source for the chi-squared multinomial limit.
* **Nigrini, M. J.** (2012). *Benford's Law: Applications for Forensic Accounting, Auditing, and Fraud Detection*. Wiley. Chapter 7. — MAD thresholds.
* **Morrow, J.** (2014). *Benford's Law, families of distributions and a test basis*. CEP Discussion Paper No. 1291. — Survey and comparison of the four-test family.
* **Kolmogorov, A. N.** (1933). *Sulla determinazione empirica di una legge di distribuzione*. Giornale dell'Istituto Italiano degli Attuari. — Original KS distribution.

**Phase 5** moves to applied territory: take real-world datasets and run the four-test bundle against each.
