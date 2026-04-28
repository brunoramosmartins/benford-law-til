#!/bin/bash
# Creates all project milestones. Run once after repo creation.
# Usage: bash .github/setup/milestones.sh owner/repo

set -euo pipefail

REPO="${1:?Usage: bash milestones.sh owner/repo}"

echo "Creating milestones for $REPO..."

gh api "repos/$REPO/milestones" -f title="Phase 0 — Foundation" \
  -f description="Thesis, scope, project scaffold, GitHub configuration." \
  -f state="open" --silent

gh api "repos/$REPO/milestones" -f title="Phase 1 — History & Empirical Observation" \
  -f description="Newcomb, Benford, Pinkham. Reproduce the empirical observation on real datasets." \
  -f state="open" --silent

gh api "repos/$REPO/milestones" -f title="Phase 2 — Log-Uniform Derivation" \
  -f description="Rigorous derivation of P(d)=log10(1+1/d) via uniform distribution of the log-mantissa." \
  -f state="open" --silent

gh api "repos/$REPO/milestones" -f title="Phase 3 — Scale Invariance" \
  -f description="Pinkham's theorem and the uniqueness of the 1/x density under scale transformations." \
  -f state="open" --silent

gh api "repos/$REPO/milestones" -f title="Phase 4 — Conformity Tests" \
  -f description="Chi-square, Kolmogorov-Smirnov, MAD, and Z-statistic for Benford conformity." \
  -f state="open" --silent

gh api "repos/$REPO/milestones" -f title="Phase 5 — Implementation & Fraud Demo" \
  -f description="Reusable Benford module, datasets, and end-to-end fraud injection demonstration." \
  -f state="open" --silent

gh api "repos/$REPO/milestones" -f title="Phase 6 — TIL Writing" \
  -f description="Full TIL assembly from theory notes, experiments, and figures." \
  -f state="open" --silent

gh api "repos/$REPO/milestones" -f title="Phase 7 — Review & Publish" \
  -f description="Mathematical validation, code reproducibility, publication." \
  -f state="open" --silent

echo "All milestones created successfully."
