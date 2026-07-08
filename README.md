## Hi, I recently got a DGX Spark, then I got curious.

DGX Spark at home, more ideas than time, and a specific use case pulling
harder than the others. I'm less interested in which model is generally
smarter and more in **which specific capabilities hold up under the
conditions I actually run models in**: life-science and computational
biology workloads, reproducibility of academic-publication pipelines,
and the coding work that ties both together. Leaderboard scores don't
always neatly translate to applicability for any of that.

What I want from a benchmark, broadly:

- A **pass-or-fail** signal on the thing the model is actually being
  asked to do, not a composite score.
- A way to see **which failure mode fires** when it fails, not just
  that it failed.
- A methodology that points at *which rung of the intervention ladder*
  the result wants: fine-tuning, harness engineering, prompt/context
  distillation, OPRO / promptbreeding-style search, based on what the
  eval surfaces, not on what was assumed going in.

![status: ongoing series](https://img.shields.io/badge/benchmark-series%20in%20progress-0f6e69?style=flat-square)

<details>
<summary><strong>What I'm running day-to-day</strong></summary>

Stratified subsets, not the full corpora. Running the full sets would
occupy the machine for weeks. Calibration matters: the benchmarks below
are sized to fit a real run inside a day-or-two window so the results
are reproducible and the failures are diagnosable, not summary-only.

- **AIME 2024 + 2025** (60-problem balanced subset across both years).
  2025 is the post-cutoff half; 2024 is the contamination-baseline
  half. Running both lets the same problem style separate *recalled*
  from *reasoned*.
- **LiveCodeBench v6** (40-problem balanced subset, drawn from the
  1,055-problem upstream release). Three metrics, all from the same
  k-sampled run: **self-consistency** (majority answer is right, so does
  the model *converge*), **pass@k** (any correct in k, so can the model
  *ever* do it), and **pass^k** (all k correct, so does the model do it
  *reliably*). Self-repair is a separate axis.
- **CRUXEval-O** (100 problems), code-reasoning *output* prediction.
  Pairs with HumanEval+ to cover the input->code->output chain at the
  reasoning rather than the generation step.
- **HumanEval+** (164 problems, full set), single-shot code synthesis;
  per-problem checkpoints so failures are diagnosable, not summary-only.
- [**tool-eval-bench**](https://github.com/SeraphimSerapis/tool-eval-bench),
  function-calling and tool-use evaluation. The part of an agentic
  loop that most general benchmarks skip.

</details>

<details open>
<summary><strong>Current experiment: published writeup</strong></summary>

**Run 1: the Fable trap battery (published).** 9 traps across 8
failure modes, control arm vs the arm that read a reasoning "operating
manual" written by Claude Fable 5. 9/9 pass on both arms; the manual
lifted the fingerprint score (3.6 -> 4.9 / 5) without changing which
traps fired. The framing for this one came from a post on X by
[@alex_prompter](https://x.com/alex_prompter/status/2074186423121690765)
suggesting the Fable 5 operating manual should be portable into
Opus 4.8. The trap battery was a way of testing whether "portable"
means *capability* or *communication discipline*. The eval lands on
the latter. **[Read the writeup ->](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/d80dd9b13ac8f7c2e8f9565285702588/raw/trap_eval.html)**

</details>

<details>
<summary><strong>Current experiment: capability-grade battery (in progress)</strong></summary>

The trap battery saturated: a single-turn battery where the model
passes 9/9 can't separate "has the discipline" from "read the manual,"
because the discipline is already in the base model. The follow-up is
built so the model *sometimes fails* and fails in the specific way the
manual's procedures would prevent, with a sham manual (length-matched,
plausible structure, zero specific procedures) as the control. Three
arms: control / sham / real. n=8 per arm per task, ~6 tasks,
pre-registered hypotheses H0/H1/H2 with a >=15pp pooled threshold for
the manual-content effect, blind label-stripped grading, and **token
cost per answer as a secondary DV**: the reliability-per-token question
is the part that decides whether the lift, if it lands, is worth the
runtime cost.

</details>

<details>
<summary><strong>Current experiment: local-model port (downstream)</strong></summary>

Once the API eval tells us what the manual actually does, the same
three-arm battery runs on local candidates running on the Spark. The
question isn't "is the 7B as good as the 70B"; it's whether the local
model gets the same lift under the same conditions, and on which
failure modes the lift holds vs. breaks. Extracts the rest of the
problems for the recurring failure modes into a deeper subset before
choosing an intervention size. The rung of the ladder (fine-tune,
harness, OPRO) gets picked from the data, not assumed.

</details>

<details>
<summary><strong>Cooling</strong></summary>

Sustained eval workloads are watts-bound on a desk-scale box. Using
an external Noctua NF-A14 industrialPPC-3000 (drawing 6.6W versus
the ~35W a desk fan pulls to move the same air through a hot chassis)
keeps watts-per-token down. That saves on power and prolongs the
hardware, and the watts/token argument is the main one. Same idea as
a datacenter PUE argument, just at desk scale.

</details>

<details>
<summary><strong>Other work</strong></summary>

Three public repos carry the engineering surface of what the profile
describes; each needs a release pass before the work is presentable
in full, so what's here is the shape rather than the polished writeup.

- [**hillstar-orchestrator**](https://github.com/evoclock/hillstar-orchestrator):
  a workflow orchestrator for multi-provider LLM coordination, aimed
  at scientific research labs that need reproducibility and audit
  trails on top of GenAI tooling. The seat/lane model in the
  "What I'm running" section comes out of this work.
- [**testudo**](https://github.com/evoclock/testudo): a hardened agent
  runtime, containerised end-to-end with declarative permissioning,
  layered sanitisation, MCP server isolation, and audit logging.
  The "harness engineering" rung of the intervention ladder.
- [**nuthatch**](https://github.com/evoclock/nuthatch): a Graph-RAG
  that treats sources as primitives because garbage in is garbage
  out. Bayesian SBM clustering, community-aware MCP retrieval, strict
  schema validation, and honest per-tool token-economy accounting.
  The KB side of "reproducibility of academic publications."

</details>
