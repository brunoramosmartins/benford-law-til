# Phase 1 — Historical notes

## The worn pages of a logarithm table

In 1881 the Canadian-American astronomer **Simon Newcomb** published a two-page note in the *American Journal of Mathematics* with one of the most disarming opening lines in the history of statistics: *"That the ten digits do not occur with equal frequency must be evident to anyone making much use of logarithmic tables, and noticing how much faster the first pages wear out than the last ones."* [Newcomb 1881, p. 39].

The observation is mundane. Before pocket calculators, scientists looked up products and quotients in printed tables of logarithms, organised by the leading digits of the operand. Newcomb noticed — by simple inspection of a thumbed-through book — that the early pages were physically more worn. The pages indexing numbers that begin with $1$ or $2$ were grimy; those beginning with $8$ or $9$ were nearly pristine.

He reasoned about it: *"the law of probability of the occurrence of numbers is such that all mantissae of their logarithms are equally probable."* From this he wrote down the now-famous expression — without rigorous derivation — that the probability of leading digit $d$ is $\log_{10}(1 + 1/d)$. The note ran two pages, made no great splash, and was effectively forgotten.

## Benford's rediscovery

Fifty-seven years later, the General Electric physicist **Frank Benford** rediscovered the same regularity by an entirely different route. Working at the GE research lab in Schenectady, NY, Benford spent years compiling first-digit frequencies from anything he could get his hands on — *molecular weights*, *atomic weights*, *areas of rivers*, *populations of American cities*, *physical constants*, *baseball statistics*, *street addresses from* American Men of Science, *numbers appearing in* Reader's Digest *articles*. By the end he had pooled $20{,}229$ numbers across $20$ disparate datasets [Benford 1938, p. 553].

The result, published in the *Proceedings of the American Philosophical Society* under the title "The Law of Anomalous Numbers," was that the empirical first-digit frequency in his pooled sample agreed almost perfectly with $\log_{10}(1 + 1/d)$. The agreement held for digits two through nine across most individual datasets, and held best for those datasets that spanned many orders of magnitude. Benford did not cite Newcomb — almost certainly because he had not seen the 1881 note — and the law has carried Benford's name ever since.

What Benford added beyond Newcomb was scale. Newcomb saw the pattern in one specific kind of data (numbers that scientists chose to look up in log tables); Benford showed it across nature. He also noticed something Newcomb had not: the further a dataset spanned across orders of magnitude, the closer it tracked the logarithmic law. A column of numbers between $1$ and $10$ does not obey it; a column ranging from $10^{-3}$ to $10^9$ does.

## Towards a derivation

Benford's paper offered a rough probabilistic argument but no rigorous proof. The empirical evidence was overwhelming, but the question — *why* a logarithmic law, of all possible laws? — remained open for decades.

A rigorous answer came from **Roger Pinkham** in 1961, in the *Annals of Mathematical Statistics*: any leading-digit distribution that is invariant under change of unit (USD ↔ BRL ↔ JPY) must be the Benford distribution, and the only continuous probability density on $(0, \infty)$ inducing such an invariant distribution is $f(x) \propto 1/x$ [Pinkham 1961]. We will reach Pinkham in Phase 3. Before that, Phase 2 derives the same law from a complementary direction — the assumption that the fractional part of $\log_{10}(X)$ is uniform on $[0, 1)$.

## The empirical question

The remainder of this TIL is structured around answering, twice, the question Benford left hanging:

> Given that the first-digit distribution $P(d) = \log_{10}(1 + 1/d)$ holds empirically across an extraordinarily wide range of natural datasets, *why* does it hold? What property of those datasets forces this particular curve?

Phase 2 answers via the log-uniform mantissa. Phase 3 answers via scale invariance. The two paths converge on the same formula — and it is precisely that convergence that elevates Benford's Law from empirical curiosity to mathematical certainty.

## References

- **Newcomb, S.** (1881). Note on the frequency of use of the different digits in natural numbers. *American Journal of Mathematics*, **4**(1), 39–40.
- **Benford, F.** (1938). The law of anomalous numbers. *Proceedings of the American Philosophical Society*, **78**(4), 551–572.
- **Pinkham, R. S.** (1961). On the distribution of first significant digits. *Annals of Mathematical Statistics*, **32**(4), 1223–1230.
