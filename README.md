# Benford's Law — TIL

> The first digit is not what you think.

A portfolio-grade **Today I Learned (TIL)** post on Benford's Law: the surprising statistical regularity that the first digit of numbers in many natural datasets follows a logarithmic distribution rather than a uniform one. The TIL combines a **rigorous mathematical derivation** (via log-uniform mantissa, plus Pinkham's scale-invariance theorem) with an **applied demonstration in fraud detection**.

**Target length:** 2,500–3,500 words. **Reader profile:** technically competent generalist comfortable with calculus and basic probability.

## Thesis (v0.1)

> The Benford distribution $P(d) = \log_{10}(1 + 1/d)$ is not an empirical curiosity to be memorized — it is the unique scale-invariant probability distribution over leading digits, derivable from two independent rigorous arguments (log-uniform mantissa and Pinkham's invariance principle). Its conformity is testable, its violations are diagnostic, and its everyday application to fraud detection is the cleanest possible demonstration that elementary measure theory matters in production data work.

The full thesis, scope, and anti-scope live in [`docs/thesis.md`](docs/thesis.md). For the personal motivation behind the project, see [`docs/motivation.md`](docs/motivation.md).

## Repository layout

```
benford-law-til/
├── article/      # Final TIL Markdown source
├── docs/         # Thesis, outline, planning docs
├── exercises/    # Paper exercises between phases
├── figures/      # Generated plots
├── notebooks/    # Exploratory Jupyter notebooks
├── notes/        # Phase-by-phase theory notes
├── scripts/      # Standalone experiment scripts
├── src/          # Reusable Python module
└── tests/        # Unit tests
```

## Quick start

Requires **Python 3.10+**.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/Scripts/activate    # Windows (Git Bash)
# .venv\Scripts\activate         # Windows (cmd / PowerShell)
# source .venv/bin/activate      # Linux / macOS

# 2. Editable install with dev and notebook extras
pip install -e ".[dev,notebook]"
```

Alternative (runtime only, no editable install):

```bash
pip install -r requirements.txt
```

## Common commands

```bash
# Lint
ruff check .

# Tests
pytest tests/

# Launch Jupyter
jupyter notebook
```

## Roadmap

The project unfolds across eight phases (Phase 0 — Foundation through Phase 7 — Review & Publish). Each phase ships as a squash-merged PR with its own milestone and tag. See [`docs/thesis.md`](docs/thesis.md) for the intellectual scope.

## License

[MIT](LICENSE).
