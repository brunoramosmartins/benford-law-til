# Exercises — Phase 3: Scale Invariance and Base Invariance

These are paper exercises to be done *before* moving on to the conformity tests in Phase 4. Budget 2–3 hours.

The derivation in `notes/phase3-pinkham.md` is the reference.

---

## Proofs (paper)

### 1. The scale-invariance condition, formally

**State** the scale-invariance condition. Let $D(X)$ denote the first significant digit of a positive random variable $X$. **Show** that scale invariance requires

$$
\Pr[D(cX) = d] = \Pr[D(X) = d]
\qquad \text{for every } c > 0 \text{ and every } d \in \{1, \ldots, 9\}.
$$

**Bonus.** Argue that requiring the equality "for every $c > 0$" is *equivalent* to requiring it "for every $c$ in a dense subset of $(0, \infty)$". Why does this strengthening not change anything?

---

### 2. The unique scale-invariant density on $[a, b]$

**Prove** that, on the multiplicative group of positive reals, the only continuous density (up to a normalisation constant on a finite window $[a, b] \subset (0, \infty)$) satisfying scale invariance is

$$
f(x) = \frac{1}{x \, \log(b/a)}.
$$

*Hint.* Change variable to $u = \log(x)$. Scale invariance becomes translation invariance, whose only continuous solution on a finite interval is the uniform density. Pull back to $x$ via $du = dx / x$.

---

### 3. Recovering the Benford PMF from $f(x) \propto 1/x$

**Derive** the Benford PMF from $f(x) \propto 1/x$. On a window $[10^k, 10^{k+1})$, integrate $f(x)$ over $[d \cdot 10^k, (d+1) \cdot 10^k)$ for $d = 1, \ldots, 9$ and recover

$$
P(d) = \log_{10}\!\left(1 + \frac{1}{d}\right).
$$

Show explicitly that the factor $10^k$ cancels — this cancellation *is* the scale invariance, made arithmetic.

---

### 4. Base invariance as a corollary

**Prove base invariance.** Show that the analogous derivation in base $b > 1$ yields

$$
P_b(d) = \log_b\!\left(1 + \frac{1}{d}\right)
\qquad \text{for } d = 1, \ldots, b - 1,
$$

and **verify** that the base-$10$ case is recovered for $b = 10$.

*Hint.* Replace $\ln 10$ in §5 of the notes with $\ln b$ and adjust the digit interval to $[d \cdot b^k, (d+1) \cdot b^k)$.

---

## Computations (paper)

### 5. BRL → USD doesn't change the first digit

A dataset of revenues in BRL is multiplied by $0.18$ (BRL → USD on a chosen day).

**Argue, without recomputing anything**, that the first-digit distribution is identical before and after conversion. **Then compute** by how much the empirical $\hat{P}(1)$ would have to drift to **reject** scale invariance at the $5\%$ level for $n = 1000$.

*Hint.* Under Benford and scale invariance, $\hat{P}(1)$ has approximately a normal distribution centred at $\log_{10}(2) \approx 0.301$ with standard deviation $\sqrt{0.301 \cdot 0.699 / n}$. The two-sided rejection threshold at $\alpha = 0.05$ is at $|z| > 1.96$.

---

### 6. Octal Benford

In base $b = 8$ (octal), **compute** the Benford PMF for $d = 1, \ldots, 7$. **Are octal-1 leading digits more or less common than base-10 leading 1s?**

*Hint.* $P_8(d) = \log_8(1 + 1/d) = \ln(1 + 1/d) / \ln 8$. Compute to four decimal places.

You should find $P_8(1) = \log_8(2) = 1/3 \approx 0.3333$, slightly more than $P_{10}(1) = \log_{10}(2) \approx 0.3010$.

---

### 7. Density vs probability density: normalisation

**Show** that the density $f(x) = 1/x$ on $[1, 10)$ is *not* a probability density without normalisation, but $f(x) = 1/(x \ln 10)$ on $[1, 10)$ is.

**Compute the CDF** $F(x) = \int_1^x \frac{dt}{t \ln 10}$ and **verify the leading-digit derivation directly from the CDF**: show that $F(d+1) - F(d) = \log_{10}(1 + 1/d)$ for $d \in \{1, \ldots, 9\}$.

---

## Acceptance check

By the time you finish these exercises you should be able to:

- State the scale-invariance condition without looking it up.
- Reduce scale invariance on $(0, \infty)$ to translation invariance on $[0, 1)$ with a single change of variables ($u = \log x$).
- Recognise that *Pinkham → log-uniform → Phase 2 → Benford* is a single logical chain — Phase 3 strictly *implies* Phase 2's premise.
- Predict the leading-digit distribution of any Benford-conforming dataset *in any base*, using only the formula $\log_b(1 + 1/d)$.

The phase ends having pinned $P(d) = \log_{10}(1 + 1/d)$ to a *second* premise — scale invariance — that is structurally different from Phase 2's log-uniformity. The two derivations meeting at the same formula is the central evidence that Benford's law is structural rather than coincidental.

**Phase 4** moves from "what is the law?" to "does this dataset obey it?" — deriving and implementing the four standard conformity tests ($\chi^2$, KS, MAD, per-digit $Z$).
