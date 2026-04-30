# Phase 3 — Scale invariance and Pinkham's theorem

Phase 2 derived $P(d) = \log_{10}(1 + 1/d)$ from a *probabilistic* premise: the log-mantissa of $X$ is uniform on $[0, 1)$. This phase derives the same formula from a *structural* premise: the leading-digit distribution must not depend on the unit of measurement.

The two derivations land on the same curve. That coincidence is the central evidence that Benford's law is structural rather than accidental.

---

## 1. The scale-invariance condition

Let $X$ be a positive random variable and $D(X)$ its first significant digit. Money offers the canonical motivation: a quantity measured in BRL or USD or JPY differs by a multiplicative constant, but the *first digit* is a property of the number itself, not of the unit. Pinkham's argument is that, *if a leading-digit law is to apply across units*, the law must satisfy:

### Definition (scale invariance).

For every $c > 0$ and every $d \in \{1, \ldots, 9\}$,

$$
\Pr[D(cX) = d] = \Pr[D(X) = d].
$$

This is a strong constraint. It rules out, for example, the uniform distribution on digits $1$–$9$: a uniform digit law for one unit will typically not be uniform after multiplying every value by $\pi$.

---

## 2. From scale invariance to translation invariance on $[0, 1)$

Take logs (base $10$). Write $Y = \log_{10}(X) \bmod 1$ and $\alpha = \log_{10}(c) \bmod 1$. By Phase 2's Proposition 2,

$$
D(X) = d \iff \log_{10}(d) \le Y < \log_{10}(d+1).
$$

The transformation $X \mapsto cX$ acts on $Y$ as

$$
Y' = \log_{10}(cX) \bmod 1 = (Y + \alpha) \bmod 1.
$$

So scale invariance of $X$ is equivalent to **translation invariance of $Y$ on the circle $[0, 1)$** (additively, modulo $1$):

$$
\boxed{\Pr[\,Y \in B\,] = \Pr[\,(Y + \alpha) \bmod 1 \in B\,]
\quad \text{for every Borel } B \subset [0, 1) \text{ and every } \alpha \in [0, 1).}
$$

The set of values $\alpha = \log_{10}(c) \bmod 1$ for $c > 0$ exhausts $[0, 1)$, so the condition really is "for every $\alpha$".

---

## 3. The only translation-invariant distribution on the circle is uniform

### Lemma.

If a probability distribution on $[0, 1)$ is invariant under all translations modulo $1$, then it is the uniform distribution.

**Sketch of proof (elementary version).** Let $F$ be the CDF on $[0, 1)$. Translation invariance forces, for any $\alpha \in [0, 1)$ and any $0 \le a < b \le 1$,

$$
F(b) - F(a) = \Pr[a \le Y < b] = \Pr[a + \alpha \le Y < b + \alpha \pmod 1].
$$

Apply the case $a = 0$ to two intervals $[0, b)$ and $[\alpha, \alpha + b) \pmod 1$ of equal length: they have equal probability. So the probability of an interval depends only on its length. Combined with countable additivity, this forces $F$ to be the identity on $[0, 1)$ — i.e., $Y \sim \text{Uniform}(0, 1)$.

(The measure-theoretic version is the uniqueness of normalised Haar measure on the compact abelian group $\mathbb{R} / \mathbb{Z}$; see Berger & Hill 2015 Ch. 4.)

$\blacksquare$

---

## 4. Closing the loop: Pinkham → Benford

Combine §2 and §3:

> Scale invariance of $X$ $\;\Longleftrightarrow\;$ translation invariance of $Y = \log_{10}(X) \bmod 1$ on $[0, 1)$ $\;\Longleftrightarrow\;$ $Y \sim \text{Uniform}(0, 1)$.

But $Y \sim \text{Uniform}(0, 1)$ is exactly Phase 2's premise. By Phase 2's theorem,

$$
P(D(X) = d) = \log_{10}\!\left(1 + \frac{1}{d}\right).
$$

So **scale invariance forces Benford** — and conversely, the Benford distribution is the *unique* leading-digit law that is scale invariant.

---

## 5. The density form: $f(x) \propto 1/x$

The exercises take a complementary route through the density of $X$ rather than its log-mantissa $Y$. The two views are equivalent; this section spells out the density picture for completeness.

### Definition (density on a finite window).

Fix a window $[a, b] \subset (0, \infty)$ with $a < b$. A probability density $f \colon [a, b] \to \mathbb{R}_{\ge 0}$ is **scale invariant on $[a, b]$** if, for every $c > 0$ such that $[ca, cb] \subset (0, \infty)$, the distribution of $cX$ (when $X$ has density $f$) restricted to $[ca, cb]$ has density $f(x/c)/c$ that, after change of variables, has the same shape as $f$ — equivalently, the density is invariant under multiplicative dilation up to a normalising constant.

### Proposition.

The unique continuous probability density on $[a, b]$ satisfying scale invariance is

$$
f(x) = \frac{1}{x \, \log(b/a)}, \qquad x \in [a, b].
$$

**Proof sketch.** Substitute $u = \log_{10}(x)$. Scale invariance $x \mapsto cx$ becomes translation invariance $u \mapsto u + \log_{10}(c)$ on the interval $[\log_{10} a, \log_{10} b]$. By §3, the only continuous translation-invariant density on this interval is uniform: $g(u) = 1/(\log_{10} b - \log_{10} a)$. Pulling back to $x$ via $du = (\ln 10)^{-1} \, dx/x$ and reabsorbing $\ln 10$ into the normalisation gives $f(x) = 1/(x \log(b/a))$. $\blacksquare$

### Recovering Benford from $f(x) = 1/(x \ln 10)$.

Take the window $[10^k, 10^{k+1})$ for any integer $k$, so $\log(b/a) = \ln 10$. Compute

$$
P(D = d)
= \int_{d \cdot 10^k}^{(d+1) \cdot 10^k} \frac{1}{x \ln 10} \, dx
= \frac{1}{\ln 10} \big[\ln((d+1) \cdot 10^k) - \ln(d \cdot 10^k)\big]
= \frac{1}{\ln 10} \ln\!\left(\frac{d+1}{d}\right)
= \log_{10}\!\left(1 + \frac{1}{d}\right).
$$

(The factor $10^k$ cancels — this is exactly the scale invariance, made arithmetic.)

---

## 6. Base invariance as a corollary

Repeat the §5 derivation in an arbitrary base $b \ge 2$. The window becomes $[b^k, b^{k+1})$ with $\log_b(b^{k+1} / b^k) = 1$, and the scale-invariant density on the window is

$$
f(x) = \frac{1}{x \ln b}.
$$

Integrating over the digit interval $[d \cdot b^k, (d+1) \cdot b^k)$ for $d \in \{1, 2, \ldots, b - 1\}$ gives

$$
P_b(d) = \log_b\!\left(1 + \frac{1}{d}\right).
$$

For $b = 10$ this is the original Benford PMF; for $b = 2$ it reduces (vacuously) to $P_2(1) = 1$; for $b = 8$ it gives $P_8(1) = \log_8 2 = 1/3$, somewhat *more* than the decimal $P_{10}(1) \approx 0.301$. This is **base invariance**: a Benford-conforming dataset has a leading-digit distribution governed by $\log_b(1 + 1/d)$ in *every* base, not just base $10$. The choice of base is a notational artefact; the law itself is structural.

---

## 7. The empirical signature: cross-currency stability

The cleanest empirical confirmation of scale invariance is to take a Benford-conforming dataset, multiply every value by various constants, and watch the leading-digit distribution stay put. The companion script `scripts/exp_scale_invariance.py` does exactly this:

- Take world city populations (Phase 1's bundled GeoNames snapshot, ~50,000 cities).
- Multiply each value by $1$, $5.0$ (USD → BRL on a chosen day), $0.91$ (USD → EUR), and $\pi$.
- Compute the empirical first-digit distribution for each scaled version.
- Quantify drift by the $L^1$ distance from the theoretical Benford PMF:
  $\Delta = \sum_{d=1}^{9} |\hat{P}(d) - P(d)|$.

Under scale invariance the four distributions should be visually indistinguishable from each other and from the Benford PMF. Phase 4's conformity tests will give us a quantitative way to say *exactly* how indistinguishable.

---

## 8. Where this leaves us

We now have **two independent derivations** of $P(d) = \log_{10}(1 + 1/d)$:

| Phase | Premise | Mechanism |
|---|---|---|
| 2 | $\log_{10}(X) \bmod 1 \sim \text{Uniform}(0, 1)$ | Direct integration |
| 3 | $\Pr[D(cX) = d] = \Pr[D(X) = d]$ for all $c > 0$ | Translation invariance ⇒ uniform $Y$ ⇒ Phase 2 |

Notice that Phase 3 *reduces* to Phase 2 — scale invariance forces the log-uniform premise. So the two derivations are not literally independent; they share a final step. The point is that they start from **structurally different** assumptions: one probabilistic, one symmetry-based. Convergence on the same answer means the formula is robust to which assumption you find more natural.

**Phase 4** moves from "what is the law?" to "does this dataset obey it?" — deriving the four standard conformity tests ($\chi^2$, KS, MAD, per-digit $Z$).

---

## References

- **Pinkham, R. S.** (1961). On the distribution of first significant digits. *Annals of Mathematical Statistics*, **32**(4), 1223–1230. — The original paper. Pinkham frames the argument in terms of distributions on $(0, \infty)$ rather than the modular log-mantissa, but the ideas are the same.
- **Berger, A. & Hill, T. P.** (2015). *An Introduction to Benford's Law*. Princeton University Press. — Chapter 4 covers scale invariance and base invariance in measure-theoretic generality.
- **Hill, T. P.** (1995). A statistical derivation of the significant-digit law. *Statistical Science*, **10**(4), 354–363. — Hill's theorem (a strengthening of Pinkham) shows that *every* mixture of distributions over scale and base is Benford, which is the strongest known structural justification.
