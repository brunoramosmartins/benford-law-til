# Thesis & Scope — Benford's Law TIL

**Version:** v0.1 (draft)
**Status:** initial draft, pending author refinement

---

## Thesis (v0.1)

> The Benford distribution $P(d) = \log_{10}\!\big(1 + \tfrac{1}{d}\big)$ is not an empirical curiosity to be memorized — it is the unique scale-invariant probability distribution over leading digits, derivable from two independent rigorous arguments (log-uniform mantissa and Pinkham's invariance principle). Its conformity is testable, its violations are diagnostic, and its everyday application to fraud detection is the cleanest possible demonstration that elementary measure theory matters in production data work.

**Why falsifiable.** The thesis would fail if either (a) one of the two derivations turned out to depend on an unstated assumption equivalent to the conclusion, or (b) the conformity tests failed to discriminate between clean and tampered datasets at modest sample sizes ($n \approx 500$).

### Central axis

The same logarithmic curve falls out of two unrelated derivations — that is the signal that the law is structural, not coincidental.

```
Empirical observation → log-uniform mantissa → P(d) = log₁₀(1 + 1/d)
                     → scale invariance     → P(d) = log₁₀(1 + 1/d)
```

---

## Scope

The TIL covers, in order:

1. **History.** Newcomb (1881) on worn pages of logarithm tables; Benford (1938) tabulating 20+ datasets; Pinkham (1961) closing the theoretical gap.
2. **Empirical observation.** Reproducing Benford's tabulation on three to five modern open datasets (city populations, river lengths, physical constants).
3. **Log-uniform derivation.** $P(d) = \log_{10}(1 + 1/d)$ from the assumption that $\log_{10}(X) \bmod 1 \sim \text{Uniform}(0, 1)$.
4. **Scale invariance.** Pinkham's argument that the only continuous density producing a scale-invariant leading-digit distribution is $f(x) \propto 1/x$.
5. **Conformity tests.** $\chi^2$, Kolmogorov–Smirnov on the discrete CDF, Mean Absolute Deviation with Nigrini's thresholds, and the per-digit $Z$-statistic.
6. **Fraud detection demo.** A reproducible end-to-end experiment: clean conforming dataset → fabricated value injection → conformity tests cross from "accept" to "reject" — referenced against at least one publicly documented historical case.

### Anti-scope

Topics deliberately excluded to keep the TIL within 2,500–3,500 words:

- The **second- and third-digit laws** as primary subjects. The second-digit law appears only as a one-paragraph generalization in the log-uniform section.
- **Multivariate generalizations** (Benford for products of random variables, mixtures, etc.).
- **Full base-independence proofs.** Base invariance is mentioned as a corollary; the proof is sketched, not rigorous.
- **Real proprietary financial data.** The fraud demo uses a clean public dataset plus synthetic injection — not actual filings.
- **Production-grade software.** The code in `src/` exists to support the writing and the demo, not to be a library.

---

## Target reader

A technically competent generalist — analyst, junior data scientist, software engineer with mathematical curiosity — who:

- Is comfortable reading **calculus** (definite integrals, change of variables) and **basic probability** (PDF, CDF, expected value, hypothesis testing at the level of an introductory course).
- Has seen a $\chi^2$ test before but does not necessarily remember its derivation.
- Wants to understand *why* a result holds, not just memorize its statement.
- Does not need a measure-theory background; the TIL stops short of formal $\sigma$-algebra arguments.

### Prerequisites

| Topic | Depth required |
|---|---|
| Calculus | Definite integration, $u$-substitution, fractional part |
| Probability | Discrete and continuous distributions, hypothesis testing |
| Statistics | Familiarity with $\chi^2$ and $p$-values (refreshed in §5 of the TIL) |
| Python | Read-only — code is illustrative, not the focus |

---

## Abstract

Benford's Law states that the first digit of numbers in many natural datasets is not uniform but logarithmic: $P(d) = \log_{10}(1 + 1/d)$, so a leading 1 occurs about 30% of the time and a leading 9 less than 5%. This TIL presents two independent rigorous derivations — one from the assumption that the log-mantissa is uniform on $[0, 1)$, and one from Pinkham's theorem that scale invariance forces the density $f(x) \propto 1/x$ — and shows why the convergence of the two arguments is evidence that the law is structural rather than coincidental. It then derives four standard conformity tests ($\chi^2$, KS, MAD, per-digit $Z$) and applies them to a fraud-detection experiment in which fabricated values are injected into a clean Benford-conforming dataset; the tests cross from "accept" to "reject" sharply enough to be operationally useful. The piece targets a technically competent generalist and runs ~3,000 words.

---

## Open questions for v0.2

These should be revisited during Phase 6 (TIL writing) when the prose is condensed:

- [ ] Does the thesis sentence read better split into two? (Currently one ~80-word sentence — falsifiable but dense.)
- [ ] Should the abstract foreground the fraud demo or the dual derivation? (Currently leads with derivations.)
- [ ] Is the prerequisite list pitched correctly for a Medium audience vs. a GitHub-only audience?
