# Refund Assistant · Tuning Plan

> For manifest **v0.1.0** · Owner: Support Product Lead (PM) · Review cadence: weekly until launch, then per release
> Nothing in this plan has been measured. Every result below is a **proposed test** until a run id is logged in §6.

## 1 · Top risks to tune first

| # | Risk | Spec IDs | Why first |
|---|---|---|---|
| 1 | A wrong or ineligible Auto-refund: wrong Order line, wrong amount, duplicate, or over the limit | R3, R5, R7, R8, C1, C6, C7, D1–D6 | Money leaves the business and cannot be recalled; the PRD sets error rate < 0.5% `[SRC: §7]` |
| 2 | Photo judgment is model-only: fake or misread damage is refunded, or real damage is over-escalated | R6, E3 | The one judgment on the money path that code cannot check |
| 3 | Over-escalation misses the 60% target: only `damaged` has an auto path, the Abuse threshold is unset, and C7 adds a step | R4, R9, C7, E2, E4 | The PRD's main outcome `[SRC: §7]` depends on three open decisions |

## 2 · Metrics

Starting targets are hypotheses. Revise them after the first measured baseline.

### AI performance

| Metric | Definition for this agent | Method | Starting target | Owner |
|---|---|---|---|---|
| Task success rate | Share of Runs whose Outcome matches the labelled expected Outcome with every D check for that Outcome passing | Fixture suite (BEHAVIOR_TESTS.md), 5 runs per case; weekly sample of 200 production Runs | ≥ 95% fixtures; ≥ 90% sample | Eng |
| Correctness & groundedness | (a) Refund error rate: refunds with a wrong amount or to an ineligible line; (b) share of facts in `customer_message` that match a tool result (D10) | (a) Monthly reconciliation of audit records against `policy.check` replays, with Finance; (b) claim-level audit of the weekly sample | (a) < 0.5% `[SRC: §7]`; (b) 100% | PM |
| Boundary & handoff accuracy | Share of out-of-scope, constraint, and escalation cases handled exactly as specified; precision and recall both count | Regression set + labelled production escalations; Handoff packet completeness (D7) by code | 100% on `C` tests; ≥ 95% escalation precision and recall; 100% packet completeness | Eng |
| Resolution without a human | Share of refund conversations with Outcome `refunded`, `declined`, or `status_reported`. Counting `declined` as resolved is an `[ASSUMPTION]` | Production analytics | 60% `[SRC: §7]` | PM |

### User understanding

| Metric | Definition for this agent | Method | Starting target | Owner |
|---|---|---|---|---|
| State comprehension | After the Run, the Customer can say whether money was refunded, how much, and to where, or that a person will review it | Post-task question in a moderated test, 8 participants | ≥ 90% correct | Design |
| Boundary comprehension | Before the task, the Customer predicts that exchanges and store credit are not handled and that large refunds go to a person | Prediction questions, same study | ≥ 80% correct | Design |
| Interaction task success | Customer completes a damaged-item refund end to end without help | Usability task, same study; CSAT on assistant-handled conversations in production | ≥ 90% task success; CSAT ≥ 4.3 `[SRC: §7]` | Design |
| Correction & takeover success | (a) Customer catches a seeded wrong Order at the confirmation step; (b) a support agent resolves an escalated Case without asking the Customer to repeat anything `[SRC: §4]` | (a) Seeded-error task; (b) 20 Cases reviewed by support agents | (a) ≥ 80%; (b) ≥ 90% | Design |

## 3 · Experiments

| Id | Question | Decision it informs | Variable (only this changes) | Conditions | Fixtures | Runs | Measures | Status |
|---|---|---|---|---|---|---|---|---|
| X1 | Can the model's photo read gate an Auto-refund? | R6, E3. If A reaches ≥ 98% precision on "shows damage to the ordered item" against human labels, keep R6; if only B does, adopt the rubric; otherwise every damage photo goes to E3 | Photo-judgment instruction | A: R6 text only · B: R6 + a 4-category damage rubric | 200 labelled photos: 100 damaged, 60 undamaged, 40 wrong item | 3 per photo per condition | precision · recall · stability across runs · productizability | proposed test |
| X2 | Does compiling "friendly, empathetic" into counts beat the label? | R11. If B matches or beats A on the tone rubric with higher compliance, keep R11 with counts enforced in code | Tone instruction | A: "friendly, empathetic" · B: R11 compiled rules | FX-base, FX-late-window, FX-frequent, 10 transcripts each | 5 per transcript per condition | count compliance · tone rubric · no-blame rubric · stability | proposed test |
| X3 | Does the confirmation step (C7) prevent wrong refunds at an acceptable cost? | The Design decision on C7. Keep C7 if A catches ≥ 80% of seeded wrong Orders and adds ≤ 20 s median | Confirmation step | A: confirm, then refund · B: refund, then notify (test payments only) | Seeded wrong-Order task | 8 participants per condition | wrong refunds caught · time to complete · state comprehension | proposed test |
| X4 | What Abuse threshold keeps known abuse out without blocking normal Customers? | The PM decision on R9 and E2 | Threshold N in 90 days | N = 2 · 3 · 5 | 6 months of historical refunds, with support-labelled abuse cases | 1 replay per condition (deterministic) | share of requests escalated · share of labelled abuse caught | proposed test |

Record per run: model + version, date, prompt hash, fixture set, grader version. X4 is an offline data replay and needs no model.

Results transfer only to the same model, prompt, and fixture family. Rerun X1 and X2 on any model upgrade.

## 4 · Triage loop

| # | Input / trace | Expected (rule) | Actual | Layer | Fix | Retest | Version |
|---|---|---|---|---|---|---|---|

No mismatches observed yet. The first rows will come from the pre-release fixture run.

Layers: spec gap · spec ambiguity · rule conflict · instruction compilation · context/orchestration · tool · model capability · user comprehension.

Protocol: **locate the mismatch → revise and simplify → retest and version.** For this agent, route these to code before the prompt: amounts, day counts, the limit, the Refund count, and duplicate checks (manifest §04 R5, R7, R8, R9; §06 C1, C6).

## 5 · Cadence

| When | Run | Gate |
|---|---|---|
| Every spec or prompt change | Tests for touched IDs + regression set | All pass |
| Model or tool upgrade | Full set + rubric recalibration + X1 and X2 | No regression on `C` and `E` tests |
| Weekly | Production sample audit, 200 Runs | Groundedness 100%; escalation precision and recall ≥ 95% |
| Monthly | Finance reconciliation of audit records | Refund error rate < 0.5% |
| Pre-release | User-understanding study, 8 participants; X3 | Targets met or explained |

## 6 · Evidence log

| Claim | Label | Source |
|---|---|---|
| Auto-refunds cannot exceed $50.00 per Order | spec/demo only | Manifest C1; code check not yet built or tested |
| Refund error rate is below 0.5% | proposed test | §2 reconciliation; no run yet |
| The model judges damage photos reliably enough to refund | proposed test | X1 |
| Compiled tone rules beat the "friendly, empathetic" label | proposed test | X2 |
| The confirmation step catches wrong-Order refunds | proposed test | X3 |
| 60% resolution without a human is reachable with only a `damaged` auto path | proposed test | Production analytics after launch; depends on the R4 decision |
| Customers understand when a person will review their refund | proposed test | §2 user-understanding study |
