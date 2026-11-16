# {Agent Name} · Tuning Plan

> For manifest **v{x.y.z}** · Owner: {role} · Review cadence: {weekly / per release}

## 1 · Top risks to tune first

| # | Risk | Spec IDs | Why first |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

## 2 · Metrics

Starting targets are hypotheses. Revise them after the first measured baseline.

### AI performance

| Metric | Definition for this agent | Method | Starting target | Owner |
|---|---|---|---|---|
| Task success rate | | | | Eng |
| Correctness & groundedness | | | | PM |
| Boundary & handoff accuracy | | | | Eng |

### User understanding

| Metric | Definition for this agent | Method | Starting target | Owner |
|---|---|---|---|---|
| State comprehension | | | | Design |
| Boundary comprehension | | | | Design |
| Interaction task success | | | | Design |
| Correction & takeover success | | | | Design |

## 3 · Experiments

| Id | Question | Decision it informs | Variable (only this changes) | Conditions | Fixtures | Runs | Measures | Status |
|---|---|---|---|---|---|---|---|---|
| X1 | | {spec IDs + possible outcomes} | | A / B / C | | {n per cell} | compliance · stability · fit · productizability | proposed test |

Record per run: model + version, date, prompt hash, fixture set, grader version.

## 4 · Triage loop

| # | Input / trace | Expected (rule) | Actual | Layer | Fix | Retest | Version |
|---|---|---|---|---|---|---|---|

Layers: spec gap · spec ambiguity · rule conflict · instruction compilation · context/orchestration · tool · model capability · user comprehension.

Protocol: **locate the mismatch → revise and simplify → retest and version.**

## 5 · Cadence

| When | Run | Gate |
|---|---|---|
| Every spec/prompt change | Touched IDs + regression set | All pass |
| Model / tool upgrade | Full set + grader recalibration | No regression on `C` and `E` |
| {Weekly} | Production sample audit ({n} runs) | Groundedness ≥ target |
| Pre-release | User-understanding study ({n} participants) | Targets met or explained |

## 6 · Evidence log

| Claim | Label | Source |
|---|---|---|
| | measured / spec-demo only / proposed test | {run id, n, model, date} |
