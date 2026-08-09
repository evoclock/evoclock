<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/readme-banner-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="assets/readme-banner.png">
    <img src="assets/readme-banner.png" alt="Origami bird attractor banner" width="100%">
  </picture>
</p>

ML/AI engineer. Less interested in which model is generally
smartest, more in which specific capabilities hold up under the
conditions I actually run models in: life-science workloads,
reproducibility of academic-publication pipelines, and the infrastructure that make it possible.

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

A live feed of what is actually in progress.

- **MicroVM-isolated autonomous agents.** A supervisor across the Mac, Linux and
  Spark hosts, so an agent can work to a spec overnight inside a VM it cannot
  reach out of, and deposit finished work on a branch for review. Signed leases,
  runtime attestation and capability tokens are built and validated; the
  supervisor, the vsock transport and the host-side publisher are next.

- **[prime-agent-cantus](https://github.com/evoclock/prime-agent-cantus).** Two
  launch profiles for [Prime Agent](https://github.com/PrimeIntellect-ai/prime-agent)
  so autonomous and interactive work share one harness, with a checkpoint before
  risky actions and screening of results before they reach a model.

- **[Circadian ChIP-seq reproducibility audit](https://github.com/evoclock/Circadian-ChIP-seq-reproducibility-audit).**
  Published. Extending the sensitivity analysis and the local ENCODE-equivalent
  comparison.

<details>
<summary><strong>Current benchmark queue</strong></summary>

This is the machine-facing eval queue. The date is intentionally not
embedded in the heading; this table should be regenerated from the
benchmark plan when the queue changes. When this project rotates out,
this table can be archived as a dated snapshot and the same shape reused
for the next active project. For the active narrative, see "Working on
today" above.

| benchmark / run | descriptor | role | metric | status |
|---|---|---|---|---|
| Fable operating-manual trap battery, Run 5 | granite-4.0-h-small-FP8 tier-X control/sham/manual run; 90-day retention trap; manual 16/24 vs control 8/24 and sham 7/24 | reasoning discipline / reviewer stressor | arm delta | done: H1 |
| CRUXEval-O supplement cons@k | 184 code-tracing problems, repeated samples after prompt A/B | reviewer | cons@k + pass^k | running |
| AIME 2024 + 2025 | 60-problem balanced reasoning subset across contamination-baseline and post-cutoff years | reviewer + planner | cons@k + pass^k | queued |
| tool-eval-bench | Deterministic tool-use and multi-turn orchestration scenarios | planner | pass@k + pass^k / harness trials | planned |
| LiveCodeBench v6 | Coding generation subset, rebuilt for stratification before publication | implementer | pass@k + pass^k | planned |
| HumanEval+ | 164-problem code generation set with per-problem checkpoints | implementer | pass@k + pass^k | planned |
| Terminal Bench hard subset | Hard terminal-agent tasks that test command planning, state tracking, recovery, and execution over a real shell workflow | planner finalist confirmation | pass@k + pass^k | planned |
| HMMT Feb25 + GPQA | Hard competition-math and graduate science QA, run with and without tools to check whether reviewer finalists can verify difficult reasoning rather than only trace code | reviewer finalist confirmation | cons@k + pass^k | planned |

Seat shorthand follows the way Hillstar-style multi-agent
orchestrators divide work: **reviewer** reads and checks reasoning or
code, **planner** chooses tools and orders work, and **implementer**
writes code or concrete artifacts. The final public reports should
separate selection runs from finalist-confirmation runs so expensive
confirmation probes do not get mixed with the cheaper full-panel sweeps.

</details>

## Fieldnotes: technical reports, experiments, evals and thoughts

<p align="center">
  <a href="https://evoclock.github.io/fieldnotes/">
    <img src="assets/Sentoku-origami-removebg-preview.png" alt="fieldnotes" width="150">
  </a>
</p>

<p align="center"><strong><a href="https://evoclock.github.io/fieldnotes/">fieldnotes</a></strong><br>
<sub>Agent systems, models, evaluation and computational biology.</sub></p>

<p align="center">
  <a href="https://evoclock.github.io/fieldnotes/"><img src="https://img.shields.io/badge/read-fieldnotes-79c39e?style=for-the-badge&labelColor=151719" alt="Read fieldnotes"></a>
  <a href="https://evoclock.github.io/fieldnotes/feed.xml"><img src="https://img.shields.io/badge/subscribe-RSS-e77843?style=for-the-badge&logo=rss&logoColor=white&labelColor=151719" alt="Subscribe by RSS"></a>
</p>

<details>
<summary><strong>Agent systems</strong> (2)</summary>

Harnesses, gates, sandboxes, orchestration, and the products built on them.

<img src="assets/Shibuichi-origami-removebg-preview.png" alt="" width="58" align="right">

- **[Memory management for LLM-on-corpus](https://evoclock.github.io/fieldnotes/notes/memory-management.html)**  
  <sub>Note · agent systems · 9 August 2026</sub>  
  Parametric state, chain-of-thought, flat RAG and graph-RAG are four answers to the same question, and the partitioning algorithm separates the principled tools from the rest.

- **[Why I Started Building a Local Multi-Model Workforce, and Why the Industry May Be Heading There Too](https://evoclock.github.io/fieldnotes/articles/local-multi-model-workforce.html)**  
  <sub>Multi-model systems · 30 July 2026</sub>  
  How a self-directed effort grew into a supervised multi-model architecture, a set of working products, and an emerging professional direction.

</details>

<details>
<summary><strong>Models</strong> (4)</summary>

Adapting models to a job, and serving them on hardware I own.

<img src="assets/Shibuichi-origami-removebg-preview.png" alt="" width="58" align="right">

- **[Building a 4B Local Implementer](https://evoclock.github.io/fieldnotes/publications/project-brief.html)**  
  <sub>LLM fine-tuning · 29 July 2026</sub>  
  The task-bound Implementer, its behavioural adaptation, repeated coding evaluation, evidence flywheel and next steps.

- **[Building a 4B Local Implementer: technical report](https://evoclock.github.io/fieldnotes/publications/technical-report.html)**  
  <sub>Technical report · 27 July 2026</sub>  
  Training regime, paired evaluation across fifteen HumanEval+ runs, and what the numbers do and do not support.

- **[The prompt is not the model](https://evoclock.github.io/fieldnotes/evals/cruxeval-o-ab-184.html)**  
  <sub>CRUXEval-O · A/B · 10 July 2026</sub>  
  Seven models over 184 output-prediction problems. The headline change is meaningless on its own, the effect is bimodal, and the real signal is the floor.

- **[Seven local models on output prediction](https://evoclock.github.io/fieldnotes/evals/cruxeval-o-results.html)**  
  <sub>CRUXEval-O · reviewer seat · 8 July 2026</sub>  
  100 Python problems, graded strictly at Pass@1 and reported together with its prompt, infrastructure and harness failures.

</details>

<details>
<summary><strong>Evaluation</strong> (10)</summary>

Designing a study, running it, and reporting what it did and did not show.

<img src="assets/Sentoku-origami-removebg-preview.png" alt="" width="58" align="right">

- **[Circadian ChIP-seq reproducibility audit](https://evoclock.github.io/fieldnotes/compbio/circadian-chipseq-audit.html)**  
  <sub>Reproducibility audit · 9 August 2026</sub>  
  A method reconstruction, sensitivity analysis and local ENCODE-equivalent comparison for public mouse liver circadian factor ChIP-seq. No tested condition reproduced both the deposited peak counts and the peak sets.

- **[Which model holds the seat, and what to do when it does not](https://evoclock.github.io/fieldnotes/notes/seat-benchmarking.html)**  
  <sub>Note · evaluation methodology · 9 August 2026</sub>  
  A leaderboard averages over the wrong axis. What matters is which model wins which seat, on what evidence, and which rung of the intervention ladder a failure points at.

- **[6.6W versus 35W, and a desk-scale PUE argument](https://evoclock.github.io/fieldnotes/notes/watts-per-token.html)**  
  <sub>Note · running the hardware · 9 August 2026</sub>  
  Sustained eval workloads are watts-bound on a desk-scale box, and the fan moving air through a hot chassis is a bigger share of that than it looks.

- **[Building a 4B Local Implementer: technical report](https://evoclock.github.io/fieldnotes/publications/technical-report.html)**  
  <sub>Technical report · 27 July 2026</sub>  
  Training regime, paired evaluation across fifteen HumanEval+ runs, and what the numbers do and do not support.

- **[A reasoning manual helped a small model catch the trap](https://evoclock.github.io/fieldnotes/evals/fable-run5-granite.html)**  
  <sub>Operating manual · run 5 · 10 July 2026</sub>  
  On granite-4.0-h-small-FP8 the manual raised the catch rate from 8/24 to 16/24, while a same-length placebo did nothing. Small n, stated plainly.

- **[The prompt is not the model](https://evoclock.github.io/fieldnotes/evals/cruxeval-o-ab-184.html)**  
  <sub>CRUXEval-O · A/B · 10 July 2026</sub>  
  Seven models over 184 output-prediction problems. The headline change is meaningless on its own, the effect is bimodal, and the real signal is the floor.

- **[The gate opened, and the manual still moved nothing](https://evoclock.github.io/fieldnotes/evals/screen_eval_run4.html)**  
  <sub>Capability screen · run 4 · 8 July 2026</sub>  
  A weaker base model and a harder trap gave the manual room to show a capability effect. It did not.

- **[Seven local models on output prediction](https://evoclock.github.io/fieldnotes/evals/cruxeval-o-results.html)**  
  <sub>CRUXEval-O · reviewer seat · 8 July 2026</sub>  
  100 Python problems, graded strictly at Pass@1 and reported together with its prompt, infrastructure and harness failures.

- **[The manual moved only the labels](https://evoclock.github.io/fieldnotes/evals/screen_eval.html)**  
  <sub>Capability screen · run 3 · 7 July 2026</sub>  
  Three arms, three tiers and twenty-seven agents, with a sham arm so a real capability effect would have had room to appear.

- **[It changed how the work was shown, not what was caught](https://evoclock.github.io/fieldnotes/evals/trap_eval.html)**  
  <sub>Trap battery · A/B · 7 July 2026</sub>  
  Nine traps, model held constant, one arm reading the operating manual and one not.

</details>

<details>
<summary><strong>Computational biology</strong> (1)</summary>

Circadian genomics, phenome classification, and disease modelling.

<img src="assets/Yamagane-origami-removebg-preview.png" alt="" width="58" align="right">

- **[Circadian ChIP-seq reproducibility audit](https://evoclock.github.io/fieldnotes/compbio/circadian-chipseq-audit.html)**  
  <sub>Reproducibility audit · 9 August 2026</sub>  
  A method reconstruction, sensitivity analysis and local ENCODE-equivalent comparison for public mouse liver circadian factor ChIP-seq. No tested condition reproduced both the deposited peak counts and the peak sets.

</details>
