#!/usr/bin/env python3
'Render the Fable Run 5 operating-manual report as self-contained HTML.'

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from statistics import mean

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARM_JSON = Path('/home/julen_gamboa/ai-models/fable/screen_run5_vllm_arm_X_granite-small.json')
DEFAULT_CALIB_JSON = Path('/home/julen_gamboa/ai-models/fable/screen_run5_vllm_calib_granite-small.json')
DEFAULT_OUTPUT = REPO_ROOT / 'reports' / 'output' / 'fable-run5-granite.html'
FULL_MODEL_NAME = 'granite-4.0-h-small-FP8'

PALETTE_CSS = '''
:root {
  --bg: #1a1816;
  --surface: #383431;
  --panel: #4a4540;
  --boost: #5c564f;
  --text: #ead1b5;
  --muted: #b09080;
  --primary: #79c39e;
  --secondary: #e77843;
  --accent: #ee9b69;
  --shadow: rgba(0, 0, 0, 0.35);
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.55;
}
body { padding: 42px 20px 56px; }
main { max-width: 1120px; margin: 0 auto; }
h1 { margin: 0 0 8px; color: var(--text); font-size: clamp(2.1rem, 5vw, 4.8rem); line-height: 0.98; letter-spacing: 0; }
h2 { margin: 34px 0 12px; color: var(--primary); font-size: 0.9rem; letter-spacing: 0.08em; text-transform: uppercase; }
h3 { margin: 0 0 8px; color: var(--text); font-size: 1.04rem; }
p { margin: 0 0 14px; }
code { color: var(--primary); font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.92em; }
.subtitle { margin: 0 0 22px; color: var(--muted); font-size: 0.94rem; }
.lede { margin: 22px 0 28px; max-width: 950px; color: var(--text); font-size: clamp(1.18rem, 2.2vw, 1.55rem); line-height: 1.38; }
.prose { max-width: 930px; }
.callout { margin: 24px 0; padding: 16px 18px; border: 1px solid var(--boost); border-left: 4px solid var(--primary); background: var(--surface); border-radius: 6px; box-shadow: 0 6px 20px var(--shadow); }
.callout.warn { border-left-color: var(--secondary); }
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 10px; margin: 22px 0 28px; }
.metric { background: var(--surface); border: 1px solid var(--boost); border-radius: 6px; padding: 12px 14px; }
.metric-label { display: block; color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }
.metric-value { display: block; margin-top: 4px; color: var(--text); font-size: 1.5rem; font-weight: 700; }
table { width: 100%; border-collapse: collapse; margin: 14px 0 24px; background: var(--surface); border: 1px solid var(--boost); border-radius: 6px; overflow: hidden; font-size: 0.92rem; }
th { background: var(--panel); color: var(--primary); padding: 10px 12px; text-align: left; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }
td { padding: 10px 12px; border-top: 1px solid var(--panel); vertical-align: top; }
.strong { color: var(--text); font-weight: 700; }
.pos { color: var(--primary); font-weight: 700; }
.neg { color: var(--secondary); font-weight: 700; }
.zero { color: var(--muted); font-weight: 700; }
.groups { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin: 18px 0 28px; }
.group { background: var(--surface); border: 1px solid var(--boost); border-radius: 6px; padding: 16px; }
.group.good { border-top: 4px solid var(--primary); }
.group.bad { border-top: 4px solid var(--secondary); }
.group.neutral { border-top: 4px solid var(--muted); }
.group-sub { color: var(--muted); font-size: 0.86rem; margin-bottom: 10px; }
.group ul { margin: 0; padding-left: 18px; }
.group li { margin: 8px 0; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 14px; margin-top: 14px; }
.card { background: var(--surface); border: 1px solid var(--boost); border-radius: 6px; overflow: hidden; box-shadow: 0 6px 18px var(--shadow); }
.card.open { grid-column: 1 / -1; }
.card-head { padding: 16px 18px; cursor: pointer; user-select: none; }
.card-title { color: var(--text); font-weight: 800; line-height: 1.25; }
.card-kicker { margin-top: 3px; color: var(--muted); font-size: 0.82rem; }
.card-stats { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.pill { display: inline-flex; align-items: center; min-height: 24px; border: 1px solid var(--boost); border-radius: 999px; padding: 2px 9px; color: var(--text); background: var(--panel); font-size: 0.82rem; font-variant-numeric: tabular-nums; }
.pill.good { color: var(--primary); }
.pill.bad { color: var(--secondary); }
.pill.warn { color: var(--accent); }
.card-toggle { margin-top: 12px; color: var(--muted); font-size: 0.86rem; font-weight: 700; }
.card-toggle::before { content: "▸ "; }
.card.open .card-toggle { color: var(--primary); }
.card.open .card-toggle::before { content: "▾ "; }
.card-body { display: none; overflow-x: auto; border-top: 1px solid var(--boost); }
.card.open .card-body { display: block; }
.card-body table { margin: 0; border: 0; border-radius: 0; }
.mono { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.84rem; word-break: break-word; }
.excerpt { max-width: 720px; }
.row-pass td:first-child { border-left: 3px solid var(--primary); }
.row-fail td:first-child { border-left: 3px solid var(--secondary); }
.generated { margin-top: 34px; color: var(--muted); font-size: 0.84rem; }
@media (max-width: 700px) { body { padding: 28px 12px 42px; } th, td { padding: 8px 9px; } .card.open { grid-column: auto; } }
'''


def pct(value: float) -> str:
    return f'{round(value * 100):.0f}%'


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def excerpt(text: str, limit: int = 280) -> str:
    compact = ' '.join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + '...'


def load_json(path: Path) -> dict:
    with path.open('r', encoding='utf-8') as fh:
        return json.load(fh)


def arm_rows_table(rows: list[dict]) -> str:
    out = []
    for row in rows:
        passed = bool(row['pass'])
        cls = 'row-pass' if passed else 'row-fail'
        result = 'PASS' if passed else 'FAIL'
        result_cls = 'pos' if passed else 'neg'
        out.append(
            f'<tr class="{cls}">'
            f'<td class="mono">{e(row["i"])}</td>'
            f'<td class="{result_cls}">{result}</td>'
            f'<td>{e(row.get("secs", ""))}s</td>'
            f'<td class="excerpt">{e(excerpt(row.get("answer", "")))}</td>'
            f'</tr>'
        )
    return ''.join(out)


def render_arm_card(name: str, data: dict) -> str:
    passed = data['pass']
    n = data['n']
    failed = n - passed
    rate = data['rate']
    avg_secs = mean(row.get('secs', 0.0) for row in data.get('rows', []))
    card_id = f'arm-{name}'
    return f'''
    <article class="card" id="{card_id}">
      <div class="card-head" onclick="toggleCard('{card_id}')">
        <div class="card-title">{e(name.title())}</div>
        <div class="card-kicker">n={n}, mean latency {avg_secs:.1f}s</div>
        <div class="card-stats">
          <span class="pill good">pass {passed}/{n}</span>
          <span class="pill bad">fail {failed}/{n}</span>
          <span class="pill warn">rate {pct(rate)}</span>
        </div>
        <div class="card-toggle">show sample evidence</div>
      </div>
      <div class="card-body">
        <table>
          <thead><tr><th>sample</th><th>grade</th><th>seconds</th><th>answer excerpt</th></tr></thead>
          <tbody>{arm_rows_table(data.get('rows', []))}</tbody>
        </table>
      </div>
    </article>
    '''


def calibration_table(calib: dict) -> str:
    rows = []
    labels = {
        'E': 'dropped cost / arithmetic check',
        'M': 'utilization or queueing sign-off',
        'H': 'Simpson-style aggregate trap',
        'X': '90-day retention storage slip',
    }
    for tier, data in calib.get('tiers', {}).items():
        fail = data['fail']
        n = data['n']
        rate = data['fail_rate']
        cls = 'pos' if tier == 'X' else ('neg' if rate in (0.0, 1.0) else 'zero')
        selected = 'selected' if tier == 'X' else 'not selected'
        rows.append(
            f'<tr><td class="mono">{e(tier)}</td><td>{e(labels.get(tier, ""))}</td>'
            f'<td>{fail}/{n}</td><td class="{cls}">{pct(rate)}</td><td>{selected}</td></tr>'
        )
    return ''.join(rows)


def render(arm: dict, calib: dict, arm_path: Path, calib_path: Path) -> str:
    arms = arm['arms']
    control = arms['control']
    sham = arms['sham']
    manual = arms['manual']
    manual_lift = manual['rate'] - control['rate']
    sham_delta = sham['rate'] - control['rate']
    generated = '2026-07-10'
    arm_cards = ''.join(render_arm_card(name, arms[name]) for name in ('control', 'sham', 'manual'))
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The manual moved outcomes, not just tone</title>
<style>{PALETTE_CSS}</style>
</head>
<body>
<main>
  <h1>The manual moved outcomes, not just tone</h1>
  <p class="subtitle">Fable operating-manual trap battery, Run 5 · {FULL_MODEL_NAME} · tier X · n=24 per arm · temperature 0.7</p>

  <p class="lede">The Fable-authored operating manual produced the first clean H1 signal in the series: manual 16/24, control 8/24, sham 7/24. The same-length placebo did nothing, which is the result the sham arm exists to test.</p>

  <section class="metric-grid" aria-label="Headline metrics">
    <div class="metric"><span class="metric-label">control</span><span class="metric-value">8/24</span></div>
    <div class="metric"><span class="metric-label">sham</span><span class="metric-value">7/24</span></div>
    <div class="metric"><span class="metric-label">manual</span><span class="metric-value">16/24</span></div>
    <div class="metric"><span class="metric-label">manual lift</span><span class="metric-value">+{manual_lift * 100:.0f}pp</span></div>
  </section>

  <section class="prose">
    <p>This run asks whether a reasoning operating manual authored by Fable changes a weaker model's actual answer on a single-turn trap. An operating manual here means a short set of reasoning-discipline procedures: re-derive a step by an independent route, run a disconfirming test, track provenance, and state the answer first. The outcome is not whether the model sounds careful. The outcome is whether it refuses to sign off and names the specific wrong step.</p>
    <p>The test has three arms. The control arm gets the worksheet and the sign-off question. The sham arm gets the same worksheet plus a same-length generic carefulness preamble with none of the manual's procedures. The manual arm gets the worksheet plus the actual Fable operating manual. The sham arm is the critical control because it separates content from priming, length, and careful-sounding language.</p>
  </section>

  <h2>Arm Results</h2>
  <table>
    <thead><tr><th>arm</th><th>pass</th><th>fail</th><th>rate</th><th>delta vs control</th><th>interpretation</th></tr></thead>
    <tbody>
      <tr><td class="strong">control</td><td>8/24</td><td>16/24</td><td>33%</td><td class="zero">baseline</td><td>Headroom exists: the model usually ships the bad worksheet.</td></tr>
      <tr><td class="strong">sham</td><td>7/24</td><td>17/24</td><td>29%</td><td class="zero">{sham_delta * 100:+.0f}pp</td><td>The placebo manual does not improve the result.</td></tr>
      <tr><td class="strong">manual</td><td>16/24</td><td>8/24</td><td class="pos">67%</td><td class="pos">+{manual_lift * 100:.0f}pp</td><td>The actual procedures lift the catch rate.</td></tr>
    </tbody>
  </table>

  <section class="groups">
    <div class="group good">
      <h3>H1: capability signal</h3>
      <div class="group-sub">Manual beats both control and sham by more than 15 percentage points.</div>
      <ul><li>Observed: manual 67%, control 33%, sham 29%.</li><li>The manual-control gap is about 34 percentage points.</li></ul>
    </div>
    <div class="group neutral">
      <h3>H2: priming</h3>
      <div class="group-sub">Would require sham and manual to rise together.</div>
      <ul><li>Not observed. Sham was slightly below control.</li><li>Length and careful tone were not enough.</li></ul>
    </div>
    <div class="group bad">
      <h3>H0: no effect</h3>
      <div class="group-sub">Would require all three arms to tie within noise.</div>
      <ul><li>Not observed. Manual is separated from both other arms.</li><li>The caveat is sample size, not direction.</li></ul>
    </div>
  </section>

  <h2>The Trap</h2>
  <section class="prose">
    <p>Tier X is a 90-day retention and cumulative-storage budgeting trap. The worksheet says 500 GB of new backup data arrives every day, backups are retained for 90 days, and cold storage costs $0.004 per GB-month. The buried error is using days in month, 30, where the retention period, 90, is the quantity that determines steady-state stored data. That understates the storage and cost by 3x.</p>
    <p>A response passes only if it does both parts: refuses to sign off and identifies the 30-day versus 90-day error with the needed correction. A vague request to double-check, or a sign-off with caveats, does not count.</p>
  </section>

  <h2>Calibration</h2>
  <section class="prose">
    <p>The run first calibrated traps control-only at n=16 per tier. The goal was a middle fail band, where the control model misses often enough for an intervention to help but not so often that every arm collapses. Tier X was selected because it produced 10/16 failures, a 62% fail rate.</p>
  </section>
  <table>
    <thead><tr><th>tier</th><th>trap family</th><th>control failures</th><th>fail rate</th><th>decision</th></tr></thead>
    <tbody>{calibration_table(calib)}</tbody>
  </table>

  <section class="callout">
    <p><strong>Why this run matters.</strong> Earlier runs did not have enough headroom: one saturated, and the Qwen3.6-35B-A3B-NVFP4 run redrew too cleanly to expose an effect. This run used {FULL_MODEL_NAME}, served locally as <code>granite-small</code>, because it is weak enough on these traps to make an outcome change measurable.</p>
  </section>

  <h2>Per-sample Evidence</h2>
  <section class="cards">{arm_cards}</section>

  <section class="callout warn">
    <p><strong>Caveat.</strong> This is a small n=24 per-arm result, so the right claim is H1 signal, not a final reliability estimate. The next run should measure cons@k, which means majority-vote consistency over repeated samples, and pass^k, which means whether all repeated samples pass. That separates point-estimate accuracy from stability.</p>
  </section>

  <p class="generated">Generated {generated} from <code>{e(arm_path)}</code> and <code>{e(calib_path)}</code>. Template style: <code>reports/templates/powerstation-report.html</code>.</p>
</main>
<script>
function toggleCard(id) {{
  document.getElementById(id).classList.toggle('open');
}}
</script>
</body>
</html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arm-json', type=Path, default=DEFAULT_ARM_JSON)
    parser.add_argument('--calib-json', type=Path, default=DEFAULT_CALIB_JSON)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    arm = load_json(args.arm_json)
    calib = load_json(args.calib_json)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(arm, calib, args.arm_json, args.calib_json), encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
