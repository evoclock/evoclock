PhD student. DGX Spark at home, mostly life-science workloads and the
code that ties them together. Less interested in which model is generally
smartest, more in which capabilities hold up under the conditions I
actually run models in, and what to do when they don't.

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

- Read-only MCP query surface the agent cannot mutate
- Schema-quarantined ingest with reasoned per-file validation
- Community-aware routing via Bayesian degree-corrected SBM, reimplemented from the original papers (not graph-tool)
- Token-economy accounting vs the right counterfactuals (BM25, card-token-sum), not whole-corpus

</td>
    <td valign="top">

- Multi-provider LLM workflow orchestrator
- Reproducibility and audit trails for research-lab GenAI tooling
- Coordinated retries, per-step audit, lane-level concurrency

</td>
    <td valign="top">

- Hardened agent runtime
- Containerised end-to-end with declarative permissioning
- Layered sanitisation, MCP server isolation, audit logging
- Permissioned, auditable execution for untrusted code paths

</td>
  </tr>
</table>

## Working on today

- **Local-model port of the capability-grade battery.** The Run 3
  capability-grade screen saturated at Sonnet 5 (control / sham / real
  manual all 9/9 at every difficulty tier; the calibration gate fired,
  so by the pre-registered rule the task family can't measure a
  capability effect at Sonnet tier). The recommended next step from
  Run 3 is a weaker base model that fails these single-turn traps
  ~30-50% of the time, reusing the same battery and sham design
  unchanged. Same three-arm battery, same pre-registered hypotheses,
  same >=15pp pooled threshold; running on local candidates on the
  Spark instead of via the API. Extracts the rest of the problems
  for the recurring failure modes into a deeper subset before choosing
  an intervention size. The rung of the ladder (fine-tune, harness,
  OPRO) gets picked from the data, not assumed.

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
<summary><strong>Memory management for LLM-on-corpus, a 4-way taxonomy</strong></summary>

The approaches I keep coming back to:

- **Parametric** (Mamba, SSMs, Jamba hybrids; [Gu & Dao
  2023](https://arxiv.org/abs/2312.00752)) compresses context into a
  bounded recurrent state during inference. Deterministic for a given
  input, ephemeral across calls.
- **Chain-of-thought.** The model's own scratchpad; pays tokens for
  working memory on every call.
- **External flat RAG** (vector similarity, BM25). Memory in an index;
  freshness wins, recall is bounded by embedding quality.
- **Graph-RAG.** Same external memory, but with structure (nodes,
  edges, communities). The partitioning algorithm is what separates
  the principled tools from the embedding-only ones. Microsoft's
  GraphRAG uses [Leiden community
  detection](https://arxiv.org/abs/2404.16130); nuthatch uses a
  Bayesian degree-corrected SBM, reimplemented from the original
  papers (graph-tool is copyleft). Most graph-RAG tools cluster by
  embedding similarity and stop there; nuthatch is the
  principled-partitioning entry in this taxonomy.

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
the time, reusing the whole battery + sham design unchanged. That's
the "Working on today" item. [Read the writeup ->](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/b253c018f36e262b1e1abff72a46e7ae/raw/screen_eval.html)

</details>

<details>
<summary><strong>What I'm running on the machine (as of 2026-07-07)</strong></summary>

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
- **CRUXEval-O** (100 problems, full set), code-reasoning *output*
  prediction. Given a Python function and an input, predict the exact
  return value. Step-by-step code reasoning without running it. This
  is the core of code verification and review, and the code-tracing
  half of the reviewer-seat battery. Deterministic grading via
  `ast.literal_eval`; no execution of model output. A model that's
  consistent on AIME but inconsistent at tracing code, or vice versa,
  is not a reliable reviewer, so the reviewer verdict is the combined
  picture across both, not either alone. The AIME writeup will pair
  with this one when it lands.
  [7-model scoreboard ->](https://htmlpreview.github.io/?https://gist.githubusercontent.com/evoclock/5c294ce71af4d67c8d7580a83a4ab512/raw/cruxeval-o-results.html)
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
