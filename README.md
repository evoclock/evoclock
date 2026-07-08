<p align="center">
  <img src="assets/readme-banner.png" alt="Origami bird attractor banner" width="100%">
</p>

ML/AI engineer. Currently evaluating and hardening local LLMs on a
DGX Spark at home. Less interested in which model is generally
smartest, more in which specific capabilities hold up under the
conditions I actually run models in: life-science workloads,
reproducibility of academic-publication pipelines, and the coding
that ties both together.

![status: ongoing series](https://img.shields.io/badge/benchmark-series%20in%20progress-0f6e69?style=flat-square)

## Showcase

<table>
  <tr>
    <td align="center" width="33%">
      <img src="https://raw.githubusercontent.com/evoclock/nuthatch/main/assets/Nuthatch_bgrm.png" alt="Nuthatch" width="180"><br>
      <strong><a href="https://github.com/evoclock/nuthatch">nuthatch</a></strong>
    </td>
    <td align="center" width="33%">
      <img src="https://raw.githubusercontent.com/evoclock/hillstar-orchestrator/main/assets/icons/Hillstar_icon_small.png" alt="Hillstar" width="180"><br>
      <strong><a href="https://github.com/evoclock/hillstar-orchestrator">hillstar-orchestrator</a></strong>
    </td>
    <td align="center" width="33%">
      <img src="https://raw.githubusercontent.com/evoclock/testudo/main/assets/testudo_80s_font-trans-tight.png" alt="Testudo" width="180"><br>
      <strong><a href="https://github.com/evoclock/testudo">testudo</a></strong>
    </td>
  </tr>
  <tr>
    <td valign="top">

- A knowledge-base layer for LLM-on-corpus workflows. Drop a paper corpus in, point an agent at it, get principled routing instead of "embed and pray"
- Read-only MCP query surface
- Schema-quarantined ingest with file-level validation
- Routing via a proprietary degree-corrected SBM
- Sub-community detection other graph-RAG lacks
- Per-tool token-economy accounting (BM25, card-sum)

</td>
    <td valign="top">

- A multi-provider LLM workflow orchestrator for research pipelines that need to be reproducible and auditable end-to-end
- Audit trails on top of GenAI tooling
- Per-step audit, lane-level concurrency

</td>
    <td valign="top">

- A hardened agent runtime for executing LLM-generated code in a sandboxed, auditable container
- Containerised end-to-end
- Sanitisation, MCP isolation, audit logs

</td>
  </tr>
</table>

## Working on today

- **CRUXEval-O supplement A/B (184 problems, in progress).** Same
  reviewer-seat battery, larger discriminating set, A/B framing. Phase
  1 (bare, no mitigation) is in progress; qwen3.6-35b bare complete at
  154/184 (83.7%), with 30 fails classified as 18 trailing-junk parse,
  3 metavariable emission, 2 prose-copy, 7 genuine tracing errors.
  Phase 2 (mitigated, v3 prompt + per-model system message + `_trim`)
  is the lightest tier of harness-only mitigations; it targets the
  prompt- and parser-artifact modes only and deliberately does not
  touch genuine tracing errors or inconsistency. The point of the A/B
  is to read the Δ: a large positive Δ means the bare fails were
  mostly artifacts (mitigable), a near-zero Δ means they were genuine
  model errors. Preliminary, a first pass to decide whether more
  focused mitigations (constrained-decoding hook, multi-sample cons@k,
  fine-tuning) are warranted.

## Thoughts

<details>
<summary><strong>I recently got a DGX Spark, then I got curious</strong></summary>

DGX Spark at home, more ideas than time, and a specific use case pulling
harder than the others. The general question I keep coming back to isn't
"which model is generally smarter"; it's "which model holds the *seat*
I need it to hold, and what do I do when it doesn't." That decomposes
into three things I want a battery to actually measure:

- Per-model failure modes: what does this model get wrong, and under
  what conditions? Authority pressure, buried ledes, re-derivation,
  drift under a long context, the things a leaderboard score doesn't
  surface.
- Per-seat benchmarking: different roles in an agentic setup (planner,
  retriever, executor, critic) need different strengths. A general
  benchmark averages over the wrong axis; I want to know which model
  wins which seat, and on what evidence.
- Intervention levels: when a model fails, the fix lives at one of
  several levels, fine-tuning, harness engineering, prompt/context
  distillation, OPRO / promptbreeding-style search. Different failures
  want different fixes; conflating them is the expensive mistake.

What I want from a benchmark, broadly:

- A pass-or-fail signal on the thing the model is actually being
  asked to do, not a composite score.
- A way to see which failure mode fires when it fails, not just that
  it failed.
- A methodology that points at which rung of the intervention ladder
  the result wants, based on what the eval surfaces, not on what was
  assumed going in.

</details>

<details>
<summary><strong>Memory management for LLM-on-corpus</strong></summary>

Not an exhaustive list, but if you have an interest in memory
management, these are some of the areas I have been experimenting on
or validating against:

- **Parametric** (Mamba, SSMs, Jamba hybrids; [Gu & Dao
  2023](https://arxiv.org/abs/2312.00752)) compresses context into a
  bounded recurrent state during inference. Deterministic for a given
  input, ephemeral across calls.
- **Chain-of-thought.** The model's own scratchpad; pays tokens for
  working memory on every call. Poor ROI for the token cost and
  overhead.
- **External flat RAG** (vector similarity, BM25). Memory in an index;
  freshness wins, recall is bounded by embedding quality.
- **Graph-RAG.** Same external memory, but with structure (nodes,
  edges, communities). The partitioning algorithm is what separates
  the principled tools from the embedding-only ones. Microsoft's
  GraphRAG uses [Leiden community
  detection](https://arxiv.org/abs/2404.16130); [nuthatch](https://github.com/evoclock/nuthatch)
  is the proprietary SBM-based entry in this space.

Worth saying why frontier labs might not be too eager to solve this:
the more rounds you need to take to solve a problem, the more tokens
you burn, and that is ultimately in their commercial interest.

</details>

<details>
<summary><strong>Fable trap battery eval (Sonnet 5 A/B), published</strong></summary>

9 traps across 8 failure modes, control arm vs the arm that read a
reasoning "operating manual" written by Claude Fable 5. 9/9 pass on
both arms; the manual lifted the fingerprint score (3.6 -> 4.9 / 5)
without changing which traps fired. The framing for this one came from
a post on X by
[@alex_prompter](https://x.com/alex_prompter/status/2074186423121690765)
suggesting the Fable 5 operating manual should be portable into
Opus 4.8. The trap battery was a way of testing whether "portable"
means *capability* or *communication discipline*. The eval lands on
the latter. [Read the writeup ->](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/d80dd9b13ac8f7c2e8f9565285702588/raw/trap_eval.html)

</details>

<details>
<summary><strong>Capability-grade screen (Sonnet 5, Run 3), published, uninformative by design</strong></summary>

Three arms (control / sham / real manual) on three difficulty tiers
(easy / medium / hard), n=3 per cell = 27 agents, single-turn, model
held constant. Result: 27/27 pass. Control, sham, and manual all
correct at every tier, including hard. The pre-registered calibration
gate fired as designed: control must fail 25-75% to give the manual
headroom, and it failed 0%, so by the rule all three tasks are cut.
With no failures to flip, this run is uninformative about capability,
not evidence the manual doesn't help, just evidence this task family
can't test it at Sonnet tier.

The sham arm did its job. On correctness, sham = manual = control.
On style, manual > sham > control, but the sham closed most of the
care-gap, so the style effect is mostly priming ("any careful-sounding
preamble"), not the manual's specific procedures. The markers unique
to the real manual (provenance grades, named disconfirming test,
explicit independent re-derivation route) appear only in the manual
arm; the shared "careful-sounding prose" is what the sham reproduces.

Three converging runs at the same wall: Run 1 (Opus control vs
placebo manual, never read the file), Run 2 (Sonnet + real manual,
single-turn), Run 3 (Sonnet + sham + 3 tiers). All three saturate.
The ceiling is the model, not the manual. The recommended next step
is a weaker base model that fails these single-turn traps 30-50% of
the time, reusing the whole battery + sham design unchanged. Run 4
picked that up (Qwen3.6-35B local vLLM, H0) and is published
below. [Read the writeup ->](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/b253c018f36e262b1e1abff72a46e7ae/raw/screen_eval.html)

</details>

<details>
<summary><strong>Capability-grade screen (Qwen3.6-35B, Run 4), published, H0</strong></summary>

Same three-arm battery, single-turn, sham manual unchanged. The
change is the model: Sonnet is gone, Qwen3.6-35B served locally via
vLLM, thinking off, temp 0.7, n=8 per arm. Plus a new harder trap (X:
a 90-day retention / cumulative-storage worksheet where the agent had
to catch the days-in-month vs retention substitution, a 3x cost
understatement).

First time the calibration gate opened. The hard Simpson's reversal
calibrated at 2/8 control fail (25%), brushing the bottom of the
pre-registered 25-75% headroom band. The new X trap saturated at
0/8 control fail and was not armed. Run the 3-arm test on H with
the gate open.

H0, no capability effect. The arm run's independent control draw
produced 0/8 fails. Sham 8/8, manual 8/8, control 8/8. The 25% vs
0% gap across the two draws is sampling noise at n=8 and temp 0.7,
not a contradiction. The pre-registered rule calls all-arms-within-
15pp as H0, and that is the verdict. Headroom was marginal, not
durable, so there were no failures for the manual to flip.

The one genuine methodological learning is buried-reversal grading.
Qwen sometimes opens with the wrong verdict, re-derives mid-answer,
and lands on the right one in a labelled Conclusion or Recommendation
section. A naive first-word grader marks these wrong. The grader
now reads the labelled conclusion (falling back to the opening only
when there is no label) and strips markdown emphasis so `do **not**
ship` still parses as a negation. Every graded row was eyeballed
against the full answer; the FAILs are genuine ships-of-B.

Four runs converge. Sonnet (runs 1-3) saturates. Qwen3.6-35B
brushes the gate on H but can't sustain it. The single-turn
verify-an-artifact family is done. To detect a capability effect
the next move is either a still-weaker model (Nemotron-30B queued)
that fails H ~30-50% reliably, or a multi-step task family where
re-derivation has room to flip an answer.
[Read the writeup ->](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/d190c2c8ebb94651ae7db7dc680c7e9f/raw/screen_eval_run4.html)

</details>

<details>
<summary><strong>CRUXEval-O 100-problem run (7 local models), published</strong></summary>

First published instance of the reviewer-seat battery. 100 CRUXEval-O
problems (a subset, not classified by difficulty), 7 local models,
Python output prediction, deterministic grading via
`ast.literal_eval`. Final scores: super-120b 98, gemma-4-26b 98,
qwen3.6-35b 97, nemotron-30b 96, ornith-fp8 94, holo-3.1-35b 88,
granite-small 81. All 7 cards clean: 0 prompt/parse/harness
exclusions.

The 18-point spread across 7 models is narrower than the raw
numbers suggest. Most of the headroom gap was prompt/parse artifact,
not model inability. The published writeup walks through every
fix: gemma's code-reproduction recovery (80 → 98), qwen's
metavariable + example-answer + reasoning-bleed fix chain (84 → 97
across four prompt variants), the parse fix that recovered
trailing-junk false-fails across qwen and ornith, and the
targeted reruns on reasoning-bleed fails for ornith and holo. Read
the gist for the per-problem verdict and the issue log.

**Failure-mode distribution (post-clean, all genuine fails).**
Across the 7 models, 48 fail-pairs hit 28 distinct problems. 43
common (≥2 models hit the same problem, 90% of the pairs); 5
unique (1 model only, 10%). The common/unique split is the
substantive finding, not the scoreboard: a battery that surfaces
mostly common fails is testing *failure modes*, not *model
idiosyncrasies*. The supplement (Working on today above)
over-samples the high-frequency common modes to push this
further.

The dominant mode is string-transform errors: off-by-char (10
pairs), truncation (5), case (3), short-string overproduce (2),
other (2) = 22 of 48 pairs (~46%). Container-shape errors are
the second cluster (~23%). The single hardest mode is
`dict_string` (4 models fail the one problem, s33), and only 1
more `dict_string` problem exists in the remaining 700, a hard
anchor that cannot be grown as a stratum. Numeric errors are
entirely unique to granite, confirming the weighting rule:
large pool, single-model, rare, so over-sampling numeric is
noise.

The data is what seeded the supplement (Regime B stratification)
and the failure-mode-driven analysis in
`benchmark-failure-modes.md`.
[7-model scoreboard ->](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/5c294ce71af4d67c8d7580a83a4ab512/raw/cruxeval-o-results.html)

</details>

<details>
<summary><strong>What I'm running on the machine (as of 2026-07-08)</strong></summary>

A dated snapshot of the daily-driver eval cycle. This will rotate;
for current work, see "Working on today" above.

- **AIME 2024 + 2025** (60-problem balanced subset across both years).
  2025 is the post-cutoff half; 2024 is the contamination-baseline
  half. Running both lets the same problem style separate *recalled*
  from *reasoned*. Pairs with CRUXEval-O as the math half of the
  reviewer-seat battery.
- **LiveCodeBench v6** (40-problem balanced subset, drawn from the
  1,055-problem upstream release). Three metrics, all from the same
  k-sampled run: self-consistency (majority answer is right, so does
  the model *converge*), pass@k (any correct in k, so can the model
  *ever* do it), and pass^k (all k correct, so does the model do it
  *reliably*). Self-repair is a separate axis.
- **CRUXEval-O supplement (A/B, 184 problems, in progress).** A
  larger CRUXEval-O set drawn from the 700 rows not in the original
  100, stratified by SHARP common-mode failure detectors so it
  separates artifact from genuine fails. Same 7 local models, same
  184 problems in both phases; only the prompt + parse + system
  message differ. Phase 1 is **bare** (v1 prompt, no system message,
  no `_trim`); Phase 2 is **mitigated** (v3 prompt, per-model
  system message, `_trim` on). The mitigation is the lightest tier
  (harness only, no hooks, no fine-tuning) and targets the
  prompt- and parser-artifact modes only. Genuine tracing errors
  and inconsistency are out of scope. Preliminary: a first pass
  to decide whether more focused mitigations are warranted.
- **HumanEval+** (164 problems, full set), single-shot code synthesis;
  per-problem checkpoints so failures are diagnosable, not summary-only.
- [**tool-eval-bench**](https://github.com/SeraphimSerapis/tool-eval-bench),
  function-calling and tool-use evaluation. The part of an agentic
  loop that most general benchmarks skip.

</details>

<details>
<summary><strong>On cooling: 6.6W versus 35W, watts-per-token, and a desk-scale PUE argument</strong></summary>

Sustained eval workloads are watts-bound on a desk-scale box. Using
an external Noctua NF-A14 industrialPPC-3000 (drawing 6.6W versus
the ~35W a desk fan pulls to move the same air through a hot chassis)
keeps watts-per-token down. That saves on power and prolongs the
hardware, and the watts/token argument is the main one. Same idea as
a datacenter PUE argument, just at desk scale.

</details>
