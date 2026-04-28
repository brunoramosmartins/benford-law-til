# Exercises — Phase 1: Empirical Observation

These are paper exercises to be done *before* moving on to the log-uniform derivation in Phase 2. Budget 1–2 hours.

---

## Computations (paper)

### 1. Fibonacci first digits (closed form)

Given a sample of $n = 100$ numbers from the Fibonacci sequence (starting at $F_1 = 1$), compute by hand the empirical first-digit frequencies $\hat{P}(d)$ for $d = 1, \ldots, 9$.

**Hint.** Use the closed form

$$
F_n = \frac{\varphi^n - \psi^n}{\sqrt{5}}, \qquad
\varphi = \frac{1 + \sqrt{5}}{2}, \quad \psi = \frac{1 - \sqrt{5}}{2},
$$

to avoid generating the sequence one term at a time. For $n \ge 5$ the term $\psi^n / \sqrt{5}$ is bounded in magnitude by $0.1$, so $F_n$ is the nearest integer to $\varphi^n / \sqrt{5}$.

**What to report.**

- The table $\hat{P}(1), \ldots, \hat{P}(9)$.
- The largest absolute deviation $\max_d |\hat{P}(d) - P(d)|$ from the Benford prediction.
- One sentence on why $n = 100$ is or is not enough to "see" Benford clearly.

---

### 2. Powers of two and Weyl's equidistribution

The first significant digit of $2^k$ for $k = 0, 1, \ldots, n-1$ converges to a Benford-distributed sample as $n \to \infty$. **Without running code**, argue *why* this is true.

**Approach.**

- Show that the first digit of $2^k$ depends only on the fractional part $\{k \log_{10} 2\}$.
- State **Weyl's equidistribution theorem**: if $\alpha \in \mathbb{R}$ is irrational, the sequence $\{n \alpha\}$ is equidistributed modulo $1$ (i.e., uniform on $[0, 1)$).
- Verify that $\log_{10} 2$ is irrational (a one-line proof by contradiction suffices).
- Conclude that the empirical first-digit frequencies of $\{2^k\}_{k=0}^{n-1}$ converge to the Benford PMF as $n \to \infty$.

**Bonus.** What happens if we replace $2^k$ with $10^k$? Why does the argument fail?

---

### 3. Three datasets where Benford is expected to fail

List **three datasets** where Benford's Law is *expected to fail*, and **justify each**:

1. **A dataset with a hard upper bound.** Example: percentage scores on an exam (0–100). Why does the upper bound break the law?
2. **An assigned-number dataset.** Example: phone numbers, social security numbers, ZIP codes. Why does the *process generating the values* matter more than the values themselves?
3. **A dataset spanning fewer than two orders of magnitude.** Example: adult human heights in centimetres. Why does narrow range imply non-Benford behaviour?

For each, sketch what the actual first-digit distribution looks like (uniform? sharply peaked? deterministic?) and contrast it with $\log_{10}(1 + 1/d)$.

---

## Acceptance check

By the time you have answered these three exercises you should be able to:

- Compute first-digit frequencies from a closed-form sequence with paper and pencil.
- State Weyl's theorem and recognise *why* it is the structural reason Benford appears in multiplicative-type sequences.
- Predict, before looking at the data, whether a given dataset will obey Benford or not — and articulate the specific structural reason.

This sets up Phase 2, which makes the "log-uniform mantissa" intuition rigorous.
