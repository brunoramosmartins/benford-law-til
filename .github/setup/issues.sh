#!/bin/bash
# Creates all project issues with full bodies. Run after labels and milestones.
# Usage: bash .github/setup/issues.sh owner/repo

set -euo pipefail

REPO="${1:?Usage: bash issues.sh owner/repo}"

echo "Creating issues for $REPO..."

# ──────────────────────────────────────────────
# PHASE 0 — Foundation
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 0] Write thesis and define scope" \
  --label "phase:0,type:documentation,priority:high" \
  --milestone "Phase 0 — Foundation" \
  --body "## Context
The thesis anchors the TIL. It must be a falsifiable claim about why the
Benford distribution is structural (not coincidental), and why a working
data scientist should care.

## Tasks
- [ ] Draft central claim (v0.1)
- [ ] Define scope: history, empirical observation, log-uniform derivation,
      scale invariance, conformity tests, fraud demo
- [ ] Define anti-scope: Benford for second/third digits as primary topic,
      multivariate generalizations, base-independence proofs in full,
      real proprietary financial data
- [ ] Identify target reader and prerequisites (calculus, basic probability)
- [ ] Write 1-paragraph abstract

## Definition of Done
- [ ] \`docs/thesis.md\` exists with thesis, scope, anti-scope, audience,
      and abstract
- [ ] Thesis is a single falsifiable sentence
- [ ] Scope clearly separates derivation phases from application phases

## References
- Prior conversation transcript with the LLM (kept in \`docs/prior-research.md\`)"

gh issue create --repo "$REPO" \
  --title "[Phase 0] Configure repository, GitHub templates, and Claude Code rules" \
  --label "phase:0,type:infrastructure,priority:high" \
  --milestone "Phase 0 — Foundation" \
  --body "## Context
Professional repository setup from day one. GitHub configuration ensures
consistent tracking. Claude Code rules enforce project conventions.

## Tasks
- [ ] Initialize all directories with \`.gitkeep\` where needed
- [ ] Create \`.claude/CLAUDE.md\` with all project rules
- [ ] Create \`.github/ISSUE_TEMPLATE/task.md\` and \`bug.md\`
- [ ] Create \`.github/PULL_REQUEST_TEMPLATE.md\`
- [ ] Create \`.github/setup/labels.sh\`, \`milestones.sh\`, \`issues.sh\`
- [ ] Write \`requirements.txt\` with pinned versions
- [ ] Write \`pyproject.toml\` with ruff config
- [ ] Write initial \`README.md\`

## Definition of Done
- [ ] Running the three setup scripts in order produces a fully configured repo
- [ ] All templates render correctly on GitHub
- [ ] \`ruff check .\` passes on the empty scaffold

## References
- This roadmap"

# ──────────────────────────────────────────────
# PHASE 1 — History & Empirical Observation
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 1] Write historical notes (Newcomb 1881, Benford 1938)" \
  --label "phase:1,type:documentation,priority:high" \
  --milestone "Phase 1 — History & Empirical Observation" \
  --body "## Context
The TIL opens with the historical hook: Newcomb noticed that earlier pages
of logarithm tables were more worn than later ones; Benford rediscovered
and tabulated the phenomenon across 20+ datasets.

## Tasks
- [ ] Source primary references (Newcomb 1881, American Journal of Mathematics;
      Benford 1938, Proceedings of the American Philosophical Society)
- [ ] Write a 600–800 word historical narrative for \`notes/phase1-history.md\`
- [ ] Note Pinkham (1961) as a forward reference to Phase 3

## Definition of Done
- [ ] All cited dates and venues are verified
- [ ] Narrative ends with the empirical question that motivates Phase 2

## References
- Newcomb, S. (1881). Note on the frequency of use of the different digits
  in natural numbers. American Journal of Mathematics, 4(1), 39–40.
- Benford, F. (1938). The law of anomalous numbers. Proceedings of the
  American Philosophical Society, 78(4), 551–572."

gh issue create --repo "$REPO" \
  --title "[Phase 1] Reproduce Benford's empirical observation on real datasets" \
  --label "phase:1,type:experiment,priority:high" \
  --milestone "Phase 1 — History & Empirical Observation" \
  --body "## Context
Reproducing Benford's original tabulation on modern, freely available
datasets is the empirical anchor for the TIL.

## Tasks
- [ ] Select 3–5 datasets spanning many orders of magnitude (e.g.,
      world city populations, river lengths, physical constants)
- [ ] Implement first-digit extraction in \`src/benford.py\`
- [ ] Tabulate empirical P̂(d) for each dataset
- [ ] Plot empirical vs theoretical bars (\`figures/empirical_match.png\`)
- [ ] Identify one dataset where the law clearly fails and explain why

## Definition of Done
- [ ] Figure produced at 300 DPI
- [ ] Tests cover the digit-extraction function for edge cases
      (negative numbers, zeros, scientific notation, leading zeros)

## References
- Notes from Phase 1 history task"

# ──────────────────────────────────────────────
# PHASE 2 — Log-Uniform Derivation
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 2] Derive Benford's Law from log-uniform mantissa" \
  --label "phase:2,type:theory,priority:critical" \
  --milestone "Phase 2 — Log-Uniform Derivation" \
  --body "## Context
This is the mathematical heart of the TIL. Derive P(d) = log10(1+1/d)
from the assumption that the fractional part of log10(X) is uniformly
distributed on [0,1).

## Tasks
- [ ] Define mantissa formally for X > 0
- [ ] State the log-uniform assumption and discuss when it holds
- [ ] Derive the digit probability via the integral of 1 over
      [log10(d), log10(d+1)]
- [ ] Compute the table of theoretical probabilities for d = 1..9
- [ ] Discuss the second-digit law as a brief generalization

## Definition of Done
- [ ] \`notes/phase2-log-uniform.md\` contains the full derivation with
      no skipped algebra
- [ ] \`exercises/ex02_log_uniform.md\` contains proofs and computations

## References
- Hill, T. (1995). A Statistical Derivation of the Significant-Digit Law.
  Statistical Science, 10(4), 354–363."

gh issue create --repo "$REPO" \
  --title "[Phase 2] Implement theoretical Benford PMF and visualize mantissa uniformity" \
  --label "phase:2,type:code,priority:high" \
  --milestone "Phase 2 — Log-Uniform Derivation" \
  --body "## Context
Provide a small computational sanity check that the log-mantissa of
log-uniform synthetic data is itself uniform on [0,1).

## Tasks
- [ ] Implement \`benford_pmf(d)\` in \`src/benford.py\`
- [ ] Generate synthetic data via X = 10^U where U ~ Uniform(0, k)
      for varying k
- [ ] Plot the histogram of (log10(X) mod 1) and overlay Uniform(0,1)
- [ ] Plot empirical first-digit frequencies and overlay the PMF

## Definition of Done
- [ ] Figure \`figures/log_uniform_intuition.png\` produced
- [ ] Tests verify benford_pmf sums to 1 and matches known values"

# ──────────────────────────────────────────────
# PHASE 3 — Scale Invariance
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 3] Derive Benford's Law from Pinkham's scale-invariance theorem" \
  --label "phase:3,type:theory,priority:critical" \
  --milestone "Phase 3 — Scale Invariance" \
  --body "## Context
The independent route to Benford. A density f(x) on (0, ∞) whose induced
distribution over leading digits is invariant under x ↦ cx for all c > 0
must satisfy f(x) ∝ 1/x — and integrating 1/x recovers Benford.

## Tasks
- [ ] State the scale-invariance condition formally
- [ ] Show that f(x) ∝ 1/x is the only continuous solution (sketch of proof)
- [ ] Integrate 1/x on [d, d+1) (after appropriate normalization on a
      finite window) to recover P(d) = log10(1 + 1/d)
- [ ] Discuss base invariance as a corollary

## Definition of Done
- [ ] \`notes/phase3-pinkham.md\` contains the derivation with figure
- [ ] \`exercises/ex03_invariance.md\` contains the relevant proofs

## References
- Pinkham, R. S. (1961). On the distribution of first significant digits.
  Annals of Mathematical Statistics, 32(4), 1223–1230."

gh issue create --repo "$REPO" \
  --title "[Phase 3] Demonstrate scale invariance numerically" \
  --label "phase:3,type:experiment,priority:medium" \
  --milestone "Phase 3 — Scale Invariance" \
  --body "## Context
Visually confirm that multiplying every value in a Benford-conforming
dataset by a constant (e.g., USD → BRL) does not change the first-digit
distribution.

## Tasks
- [ ] Implement \`scripts/exp_scale_invariance.py\`
- [ ] Take a Benford-conforming dataset, multiply by 5.5 (USD → BRL),
      by 0.91 (USD → EUR), and by π
- [ ] Plot the four bar charts side by side
- [ ] Quantify drift via L¹ distance from the theoretical PMF

## Definition of Done
- [ ] Figure \`figures/scale_invariance.png\` shows visually identical
      distributions"

# ──────────────────────────────────────────────
# PHASE 4 — Conformity Tests
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 4] Derive and implement four conformity tests" \
  --label "phase:4,type:theory,priority:high" \
  --milestone "Phase 4 — Conformity Tests" \
  --body "## Context
A working data scientist needs more than a bar chart. Implement and
explain χ², KS, MAD, and per-digit Z-statistic for Benford conformity.

## Tasks
- [ ] Derive the χ² test statistic for a discrete distribution with
      9 categories
- [ ] State the KS test in its discrete-CDF form
- [ ] Define MAD (Mean Absolute Deviation) and tabulate Nigrini's
      conformity thresholds
- [ ] Derive the Z-statistic for an individual digit's frequency
- [ ] Implement all four in \`src/conformity.py\`
- [ ] Write tests with synthetic conforming and non-conforming data

## Definition of Done
- [ ] All four tests return a structured result object
- [ ] Documentation explains when each test is appropriate"

# ──────────────────────────────────────────────
# PHASE 5 — Implementation & Fraud Demo
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 5] Build the fraud-injection demonstration" \
  --label "phase:5,type:experiment,priority:high" \
  --milestone "Phase 5 — Implementation & Fraud Demo" \
  --body "## Context
The TIL's payoff. Take a clean conforming dataset, inject fabricated
values, run the conformity tests, and show how detection works in
practice.

## Tasks
- [ ] Implement \`src/fraud.py\` with two injection strategies:
      uniform random in a plausible range; clustered around 'round
      numbers' that humans tend to invent
- [ ] Sweep the injection ratio from 0% to 50% in 5% steps
- [ ] For each ratio, run all four conformity tests and record results
- [ ] Plot detection-power curves: p-value (or MAD) vs injection ratio
- [ ] Reference (with citation) at least one publicly documented case
      where Benford-style analysis flagged real fraud

## Definition of Done
- [ ] \`figures/fraud_detection_power.png\` shows clear detection
      transitions
- [ ] One paragraph in the TIL grounds the demo in a real historical case"

# ──────────────────────────────────────────────
# PHASE 6 — TIL Writing
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 6] Assemble the TIL from theory notes and experiment outputs" \
  --label "phase:6,type:writing,priority:critical" \
  --milestone "Phase 6 — TIL Writing" \
  --body "## Context
Compose the final TIL in \`article/benford-law-til.md\`, drawing
condensed prose from the theory notes and embedding the figures.

## Tasks
- [ ] Draft sections 1–4 (history, empirical, log-uniform, invariance)
- [ ] Draft sections 5–7 (conformity tests, fraud demo, takeaways)
- [ ] Polish notation and align all LaTeX
- [ ] Verify every figure is referenced and every reference is cited

## Definition of Done
- [ ] Word count between 2,500 and 3,500
- [ ] Every derivation is condensed but no algebra is implicit"

# ──────────────────────────────────────────────
# PHASE 7 — Review & Publish
# ──────────────────────────────────────────────

gh issue create --repo "$REPO" \
  --title "[Phase 7] Mathematical and reproducibility review" \
  --label "phase:7,type:review,priority:critical" \
  --milestone "Phase 7 — Review & Publish" \
  --body "## Context
Final pass before publication.

## Tasks
- [ ] Re-derive every formula in the TIL on paper
- [ ] Run \`pytest tests/\` and \`ruff check .\` on a clean clone
- [ ] Re-run all scripts with fixed seeds and confirm figure parity
- [ ] Validate every external reference

## Definition of Done
- [ ] Reviewer's checklist (in PR description) is fully ticked"

gh issue create --repo "$REPO" \
  --title "[Phase 7] Publish to GitHub Pages and Medium" \
  --label "phase:7,type:content,priority:high" \
  --milestone "Phase 7 — Review & Publish" \
  --body "## Context
Push the TIL through the existing MD → HTML pipeline and cross-post.

## Tasks
- [ ] Push article through the MD → HTML pipeline
- [ ] Cross-post to Medium with canonical link to GitHub Pages
- [ ] Draft LinkedIn announcement post
- [ ] Tag \`v1.0.0\` and create stable release

## Definition of Done
- [ ] Public URL live on GitHub Pages
- [ ] Medium article published with canonical link"

echo "All issues created successfully."
