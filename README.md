## Hi — I run small A/B tests on LLM behavior.

The current series asks whether reasoning "operating manuals" (in the
prompt-optimization / OPRO family) change what a model *catches*, or
just how plainly it shows its work. Model held constant, manual held
constant, the battery held constant — only the arm that reads the
manual varies.

![status: ongoing series](https://img.shields.io/badge/benchmark-series%20in%20progress-0f6e69?style=flat-square)

### Writeups

- 🔬 [**Fable trap battery eval — Sonnet 5 A/B**](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/d80dd9b13ac8f7c2e8f9565285702588/raw/trap_eval.html) — 9 traps across 8 failure modes, control vs manual arm, 0% pass-rate delta. The manual lifted the fingerprint score (3.6 → 4.9 / 5) but did not change which traps fired. Communication-discipline intervention, not a capability one.
