# Exercises — Phase 4: Conformity Tests

These are paper exercises to be done *before* moving on to applied audits in Phase 5. Budget 2–3 hours.

The derivation in `notes/phase4-conformity.md` is the reference.

---

## Proofs (paper)

### 1. Chi-squared as a multinomial limit

**State** the multinomial central limit theorem for the count vector $(O_1, \ldots, O_9)$ under $H_0$, and **derive** that

$$
\chi^2 = \sum_{d=1}^{9} \frac{(O_d - n P(d))^2}{n P(d)}
$$

converges in distribution to $\chi^2_8$ as $n \to \infty$.

*Hint.* Standardize the residuals $Z_d = (O_d - n P(d)) / \sqrt{n P(d)}$. The constraint $\sum_d O_d = n$ forces the joint distribution of $(Z_1, \ldots, Z_9)$ onto a hyperplane; the squared norm on that hyperplane is $\chi^2_8$.

**Bonus.** Why can't the test statistic be $\chi^2_9$ if the count vector has 9 cells? Where exactly does the constraint subtract one degree of freedom?

---

### 2. The excess-power asymptotic

**Suppose** the true distribution is *not* Benford but differs by a *fixed* per-cell amount $\delta_d$, i.e. $\Pr[D = d] = P(d) + \delta_d$ with $\sum_d \delta_d = 0$ and $\max_d \lvert \delta_d \rvert$ small but positive.

**Show** that $\chi^2$ scales linearly in $n$:

$$
\mathbb{E}[\chi^2] \sim n \sum_{d=1}^{9} \frac{\delta_d^2}{P(d)} \quad \text{as } n \to \infty.
$$

**Conclude** that for any fixed $\delta \neq 0$, $\chi^2$ rejects $H_0$ with probability $\to 1$ as $n \to \infty$. This is the formal statement of the "excess-power problem" in §2.3 of the notes.

*Hint.* Decompose $O_d = n(P(d) + \delta_d) + (O_d - \mathbb{E} O_d)$. The first term contributes the linear-in-$n$ piece; the second contributes an $O(1)$ piece that you should bound using $\mathrm{Var}(O_d) = n P(d)(1 - P(d))$.

---

### 3. KS as a maximum of a Brownian bridge

**Sketch** why $\sqrt{n} \, D_n$ converges to the supremum of a Brownian bridge under $H_0$ in the *continuous-CDF* case, and **explain** in one paragraph why the resulting Kolmogorov distribution is *conservative* on a discrete distribution.

*Hint.* The Brownian-bridge limit comes from the Donsker invariance principle applied to the standardized empirical CDF process. Discreteness collapses the bridge onto a finite grid, which can only *reduce* the supremum — hence "conservative" (true level below nominal).

---

### 4. The per-digit $Z$ statistic as a binomial $z$-test

**Derive** the per-digit $Z$ statistic from the binomial distribution. Under $H_0$, $O_d \sim \text{Binomial}(n, P(d))$. **Show** that

$$
\frac{\hat P(d) - P(d)}{\sqrt{P(d)(1 - P(d)) / n}}
$$

is approximately standard normal for moderate $n$, and **explain** the role of the continuity correction $1 / (2 n)$: when does the correction matter, and when is it negligible?

**Bonus.** Show that the family-wise error rate of running 9 independent two-sided $z$-tests at $\alpha = 0.05$ (with no correction) is approximately $1 - 0.95^9 \approx 0.37$. State this in plain English: "out of every three Benford-conforming datasets you audit, roughly one will produce at least one spurious flag."

---

## Computations (paper)

### 5. Critical value of $\chi^2_8$ at $\alpha = 0.05$

**Look up or compute** the critical value of $\chi^2_8$ at $\alpha = 0.05$. **Verify** that it is approximately $15.51$.

A dataset of $n = 1000$ Benford-conforming observations produces $\chi^2 = 7.2$. **Should you reject $H_0$? At what level?** Compute the (approximate) p-value via $1 - F_{\chi^2_8}(7.2)$ from a table or with the known relation between $\chi^2_8$ and the regularised incomplete gamma function $P(4, x/2)$.

---

### 6. MAD on a small synthetic dataset

The first-digit counts of an $n = 200$ sample of vendor-payment amounts are

| $d$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| $O_d$ | 53 | 35 | 26 | 22 | 14 | 13 | 14 | 12 | 11 |

**Compute** $\hat P(d)$, $\lvert \hat P(d) - P(d) \rvert$, and $\mathrm{MAD}$. **Read off the verdict** from Nigrini's table. **Compute also** $\chi^2$ and the p-value (use $\chi^2_8$).

**Reconcile** the two: do they agree on whether the data conform? If they disagree, which one would you trust on a sample this small, and why?

---

### 7. Per-digit $Z$ on the same vendor-payment data

Using the same counts as Exercise 6, **compute** $z_d$ for each $d \in \{1, \ldots, 9\}$ (with continuity correction), and **list** the digits flagged at $\alpha = 0.05$ (i.e., $|z_d| > 1.96$).

**Interpret** the result: which digits are over-represented and which are under-represented? Does the pattern look like *round-number bias*, *threshold-effect bias* (an artificial cap at some round value pushing leading-1s up), or something else?

*Hint.* Round-number bias inflates $d \in \{8, 9\}$ (people round up to the next 100 / 1000 / etc.). Threshold bias inflates $d = 1$ (everyone is just under the threshold).

---

## Acceptance check

By the time you finish these exercises you should be able to:

- State and derive the chi-squared limit for the multinomial first-digit count vector, including the degrees-of-freedom argument.
- Explain — in one sentence — why $\chi^2$ over-rejects on huge samples and how MAD sidesteps the problem.
- Pick the right test for the right question (single test vs. cumulative drift vs. localisation vs. forensic-scale audit).
- Compute all four statistics by hand on a small dataset and reconcile their verdicts.

**Phase 5** moves to applied audits: run the four-test bundle on real datasets (city populations, Fibonacci, heights, transaction logs) and compare the verdicts dataset-by-dataset.
