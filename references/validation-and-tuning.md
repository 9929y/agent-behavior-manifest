# Validate Outcomes and Tune the Spec

A manifest is a hypothesis about behavior. Validation tests it. Tuning changes the spec, or the
layer under it, when reality disagrees.

## 1 · Metrics: two families

Measure the system **and** the people using it. An agent that is correct but misunderstood still
fails.

### AI performance

| Metric | Definition | How to measure |
|---|---|---|
| **Task success rate** | Share of runs that reach the intended outcome with status `ok` and all `D` checks passing | Fixture runs + production sample; code-checked where possible |
| **Correctness & groundedness** | Share of stated facts and conclusions that are right **and** traceable to evidence | Claim-level audit: each claim → evidence id → verified |
| **Boundary & handoff accuracy** | Share of out-of-scope, constraint, and escalation cases handled exactly as the spec says (right refusal shape, right stop, complete handoff packet) | Boundary test set; precision **and** recall: over-refusal is a failure too |

### User understanding

| Metric | Definition | How to measure |
|---|---|---|
| **State comprehension** | Users correctly say what the agent is doing / did / didn't do | Post-task question or think-aloud ("What happened just now?") |
| **Boundary comprehension** | Users correctly predict what the agent can and cannot do | Prediction questions before tasks |
| **Interaction task success** | Users complete the end-to-end task that involves the agent | Usability test tasks |
| **Correction & takeover success** | Users fix a wrong result or take over a stopped run without help | Seeded-error tasks: give a wrong output and watch the recovery |

Set a **starting target, an owner, and a cadence** for each metric. Starting targets are guesses to
revise, not promises. Label them that way.

## 2 · Deriving behavior tests

### Coverage rules

| Spec item | Minimum tests |
|---|---|
| Each Core Rule `R` | 1 positive case. Add 1 tie or threshold edge if the rule selects or ranks |
| Each Constraint `C` | 1 direct case + 1 **adversarial** case (the user or injected content tries to override it) |
| Each out-of-scope item | 1 refusal case checking reason code + explanation + offer |
| Each Failure Mode `F` | 1 fault-injection case (make the tool fail, remove the input, …), checking the return and that **nothing was saved** |
| Each Escalation `E` | 1 case checking the stop + the handoff packet or decision |
| Each Done check `D` | Becomes a grader used by the cases above |
| Each Entry Point | 1 precondition-false case, and 1 concurrency case if the spec defines `busy` |

### Test case schema

```yaml
id: T-C2-adv
covers: [C2]
type: adversarial          # positive | edge | adversarial | refusal | fault | escalation | regression
setup: <state + fixtures>
input: <event + payload>
expect:
  status: rejected
  reason: out_of_scope
  must: ["explains the boundary in one sentence", "offers an in-scope alternative"]
  must_not: ["issues the refund", "mentions internal ids"]
grader: code | rubric | human
```

### Graders

| Use | When |
|---|---|
| **Code** | Status, schema, counts, enums, "nothing was saved", ids traceable to evidence |
| **Rubric (model-graded)** | Meaning: "explains the boundary", "tone matches", "separates facts from inference". Give the grader the rule text and pass/fail anchors |
| **Human** | New rubric calibration, high-consequence cases, user-understanding metrics |

Calibrate model graders against human labels on a small set before you trust them. Re-calibrate when
the model changes.

### Fixtures

Build named fixtures that vary **one** risk at a time: sparse input, conflicting sources, a noisy
majority vs an authoritative minority, adversarial content, missing permission, oversized input.
Reuse them across experiments so results stay comparable.

## 3 · Experiment design (for tuning decisions)

Use experiments to decide *how* a rule should be modeled, for example whether tone is a structured
control, a phrase bundle, or a persona.

1. **Question → decision.** Write down which manifest decision the result will change ("If B beats A on brand fit without hurting stability, tone becomes a phrase bundle with `soft` lock").
2. **One variable.** Vary only the condition under test. Keep the prompt skeleton, model, fixtures, and every other control fixed.
3. **Conditions.** A/B or A/B/C, named and versioned.
4. **Repeats.** Run each fixture × condition several times to see variance, not just the mean.
5. **Measure more than variation:** compliance, stability across runs, fit to the target, and *productizability* (can this become a field, a control, or an instruction?).
6. **Record** the model + version, date, prompt hash, fixture set, and grader version.
7. **Map back.** Each result ends as one of: becomes a `hard` control · becomes `soft` guidance · becomes an internal prompt strategy · dropped.

### Evidence labels

Every claim in a tuning plan or report carries one label:

| Label | Meaning |
|---|---|
| **measured** | An experiment ran. Cite the run, sample size, model, and date |
| **spec/demo only** | The rule or a scripted demo exists. Its reliability is not yet measured |
| **proposed test** | Designed, not run |

Never present a demo or a planned test as a result. Results transfer only to the same task, model,
and fixture family. Say so.

## 4 · Failure triage (Tune mode)

For each observed mismatch:

```markdown
| # | Input / trace | Expected (rule) | Actual | Layer | Fix | Retest |
```

### Layer classification

| Layer | Signature | Typical fix |
|---|---|---|
| **Spec gap** | No rule covers it | Add a rule, or route it to the catch-all failure |
| **Spec ambiguity** | Two readings of a rule are both defensible | Rewrite with numbers, an order, or a tie-breaker; add a term |
| **Rule conflict** | Two rules give different answers | Add precedence; delete the weaker duplicate |
| **Instruction compilation** | The rule is right, but the prompt doesn't carry it, or carries it as a label | Compile it into a concrete instruction; adjust the lock level |
| **Context / orchestration** | The agent never saw the data, or saw stale data | Fix the context assembly, the event routing, or freezing per job |
| **Tool** | A tool returned wrong, partial, or unexpected data | Fix the tool; add a failure row for its error mode |
| **Model capability** | Correct instructions and context, still wrong | Move to code (P9), split the step, change the model, or narrow the scope |
| **User comprehension** | The agent behaved to spec; the user misread it | Change the screen spec or copy, not the behavior spec |

### Spec update protocol

1. **Locate the mismatch.** Find the exact rule ID, or record that none exists.
2. **Revise and simplify.** Prefer rewriting or deleting over adding. Remove duplicates and conflicts you find on the way.
3. **Retest and version.** Rerun the failing case, the tests for every touched ID, and the regression set. Bump the version and log the change with its rule IDs, reason, evidence, and owner.

Watch for **rule bloat.** If the manifest grows every tuning round and never shrinks, rules are
patching symptoms. Look for the missing term or precedence underneath.

## 5 · Cadence

| When | Do |
|---|---|
| Before first release | Full test set; boundary set at 100% pass on `C` items; user-understanding test with 5 or more people |
| Each spec or prompt change | Tests for the touched IDs + the regression set |
| Model or tool upgrade | The full set + grader re-calibration |
| Weekly / per release | Production sample audit for groundedness and handoff accuracy; new failures feed the triage table |
| Quarterly | Drift audit (see `maintenance.md`); rule-bloat review |
