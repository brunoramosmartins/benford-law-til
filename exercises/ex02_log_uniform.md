# Exercises — Phase 2: Log-Uniform Mantissa

These are paper exercises to be done *before* moving on to Pinkham's scale-invariance argument in Phase 3. Budget 2–3 hours.

The derivation in `notes/phase2-log-uniform.md` is the reference.

---

## Proofs (paper)

### 1. Uniqueness of the mantissa decomposition

**Define formally** the mantissa $r$ and order of magnitude $k$ of a positive real $X$ via $X = r \cdot 10^k$ with $r \in [1, 10)$ and $k \in \mathbb{Z}$. **Prove that this decomposition is unique.**

*Hint.* Take $\log_{10}$ of both sides and use that $\log_{10}(r) \in [0, 1)$ to pin $k$.

---

### 2. First digit ↔ log-mantissa interval

**Prove** that the first significant digit of $X > 0$ equals $d \in \{1, \ldots, 9\}$ if and only if the fractional part

$$
Y = \log_{10}(X) \bmod 1
$$

satisfies

$$
\log_{10}(d) \le Y < \log_{10}(d+1).
$$

*Hint.* Start from the definition $D_1 = \lfloor r \rfloor$ where $r$ is the mantissa, and apply $\log_{10}$ monotonically.

---

### 3. The Benford PMF from log-uniformity

**Derive** the Benford PMF. Assume $Y \sim \text{Uniform}(0, 1)$. **Show:**

$$
P(d) = \int_{\log_{10}(d)}^{\log_{10}(d+1)} 1 \, dy = \log_{10}\!\left(\frac{d+1}{d}\right) = \log_{10}\!\left(1 + \frac{1}{d}\right).
$$

State explicitly which step uses Exercise 2 and which step uses the uniformity assumption.

---

### 4. The second-digit law

**Generalize** to the second significant digit. Derive

$$
P(D_1 = d_1, D_2 = d_2) = \log_{10}\!\left(1 + \frac{1}{10 d_1 + d_2}\right),
\qquad d_1 \in \{1, \ldots, 9\},\ d_2 \in \{0, \ldots, 9\},
$$

and marginalise to obtain the second-digit law

$$
P(D_2 = d_2) = \sum_{d_1 = 1}^{9} P(D_1 = d_1, D_2 = d_2).
$$

**Compute the table** for $d_2 = 0, 1, \ldots, 9$ to four decimal places.

*Comment.* Compare the spread $\max - \min$ for the first-digit and second-digit laws. What does this suggest about the distribution of, say, the *fifth* significant digit?

---

### 5. The Benford PMF is a valid distribution

**Prove** that the Benford PMF is a valid probability distribution: $P(d) > 0$ for $d = 1, \ldots, 9$ and $\sum_{d=1}^{9} P(d) = 1$.

*Hint.* The positivity is immediate from $\log_{10}(1 + 1/d) > 0$. For the normalisation, write $P(d) = \log_{10}(d+1) - \log_{10}(d)$ and use telescoping.

---

## Computations (paper)

### 6. The probabilities to four decimal places

Compute $P(1), P(2), \ldots, P(9)$ to four decimal places using $\log_{10}(2) \approx 0.30103$. **Verify the sum equals $1$** (to within rounding error in the fourth decimal).

| $d$ | $P(d)$ |
|---:|---:|
| 1 | _____ |
| 2 | _____ |
| ⋮ | ⋮ |
| 9 | _____ |
| **Sum** | _____ |

---

### 7. Decay ratios

The ratio $P(d) / P(d+1)$ governs how quickly the curve decays. **Compute this ratio** for $d = 1, 2, \ldots, 8$. **Is it monotonic?** **What is its limit as $d \to \infty$?**

*Hint.* Write the ratio as

$$
\frac{P(d)}{P(d+1)}
= \frac{\log_{10}(1 + 1/d)}{\log_{10}(1 + 1/(d+1))}.
$$

For the limit, use $\log_{10}(1 + \varepsilon) \approx \varepsilon / \ln(10)$ as $\varepsilon \to 0$.

---

### 8. A standardised deviation under Benford

A dataset has $n = 500$ values, of which $172$ start with the digit $1$. Under Benford, the expected count is $500 \cdot \log_{10}(2) \approx 150.5$.

**Compute** the standardised deviation

$$
z = \frac{172 - 150.5}{\sqrt{500 \cdot 0.301 \cdot 0.699}}.
$$

**Is this surprising at $\alpha = 0.05$** (two-sided)?

*Hint.* The denominator is the standard deviation of a Binomial$(n = 500,\ p = 0.301)$ count. At $\alpha = 0.05$ two-sided, the rejection threshold is $|z| > 1.96$.

---

## Acceptance check

By the time you finish these exercises you should be able to:

- Give a one-sentence statement of Definition 1 (mantissa decomposition) without looking it up.
- Explain *why* the interval-width derivation in Exercise 3 is clean: it reduces a question about discrete digits to a question about lengths of subintervals of $[0, 1)$.
- Recognise the second-digit law as a flatter cousin of the first-digit law and predict that further significant digits approach the uniform distribution.
- Read a Benford-conformity claim and immediately know which test statistic to compute (we will formalise this in Phase 4).

The phase ends having pinned $P(d) = \log_{10}(1 + 1/d)$ to a single mathematical premise. **Phase 3** will pin it to a *different* premise (scale invariance) and the convergence is the central evidence the law is structural.
