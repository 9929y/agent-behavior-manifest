# Agent Behavior Manifest

**An agent skill for turning any PRD or feature spec into a reviewable, testable contract for how an AI agent behaves, with derived behavior tests and a tuning plan.**

> Screen design specifies what the user sees.
> Behavior design specifies how the AI system acts.

AI features fail in ways screens never show. An agent accepts a task it shouldn't. It acts without
confirmation, invents a fact to fill a gap, keeps going when it should stop, or reports a partial
job as done. This skill makes those behaviors explicit before they ship, at a depth that matches
the feature's risk.

## What it produces

| File | Answers |
|---|---|
| `BEHAVIOR_MANIFEST.md` | How must the agent behave? Ten sections, stable rule IDs, risk-calibrated depth |
| `BEHAVIOR_TESTS.md` | How do we prove it? Every rule, constraint, failure mode, and escalation has a test; every hard boundary has an adversarial test |
| `TUNING_PLAN.md` | How do we measure it and change it safely? Metrics, single-variable experiments, a failure-triage loop, and versioning |

## The ten sections

| # | Section | Question |
|---|---|---|
| 01 | Role | What does it work as, and who is it accountable to? |
| 02 | Scope | Which tasks does it accept, and which does it refuse? |
| 03 | Entry Points | When does it start, and what context does it need? |
| 04 | Core Rules | In what order does it judge, and who wins a conflict? |
| 05 | Memory | What must it remember, for how long, and who can change it? |
| 06 | Constraints | What is always forbidden, and what needs confirmation? |
| 07 | Failure Modes | How can it fail, and how does the user notice and recover? |
| 08 | Human Escalation | When must it stop and hand the decision back? |
| 09 | Output Format | How do people understand the result, and how do downstream systems use it? |
| 10 | Definition of Done | How do we confirm it is really done, and not just that the system says so? |

## Risk sets the depth

|  | Low consequence | High consequence |
|---|---|---|
| **Low ambiguity** | Light brief: Role / Output / Done | Permissions & confirmation |
| **High ambiguity** | Rules & evidence | Full ten + behavior tests |

- **Level 1 · Brief:** low-risk prototype. Role, Core Rules, Human Escalation, Output Format.
- **Level 2 · Workflow:** embedded in a real workflow. Level 1 + Scope, Failure Modes, Definition of Done.
- **Level 3 · Full:** direct actions or long-running tasks. All ten sections + behavior tests on every rule.

## Three modes

- **Create:** PRD → manifest + tests + tuning plan + open decisions, grouped by owner (PM / Design / Eng).
- **Review:** existing agent spec or system prompt → section map, lint, what is already strong, gap report by risk → revised manifest (short specs) or proposed patches (long or strong specs), Boundary review, and the behavior tests it most lacks.
- **Tune:** manifest + observed failures → triage (which rule, which layer) → spec diff → retest plan.

## Install

**Claude Code** (personal):

```bash
git clone https://github.com/9929y/agent-behavior-manifest ~/.claude/skills/agent-behavior-manifest
```

Project-scoped: clone into `.claude/skills/agent-behavior-manifest` in your repo.

Other agents that read `SKILL.md`-style skills: copy the folder into that tool's skills directory.

## Use

```
Use agent-behavior-manifest on docs/prd/smart-replies.md
```

```
Review our agents/support/system_prompt.md against the behavior manifest framework
```

```
Here are 12 failed transcripts from the refund assistant. Tune the manifest.
```

Lint a manifest at any time:

```bash
python3 scripts/lint_manifest.py BEHAVIOR_MANIFEST.md --tests BEHAVIOR_TESTS.md
```

The linter checks the sections required for the declared level, unique `R/C/F/E/D` IDs,
leftover template placeholders, vague wording ("should", "appropriate", "try to"…), the catch-all
failure row, a `partial` status, unresolved decision markers, and rule-to-test coverage, including an
adversarial test for every hard constraint. It uses only the Python standard library.

## Structure

```
SKILL.md                         workflow the agent follows
references/
  framework.md                   the ten sections: what each must answer, good vs typical failures
  depth-calibration.md           four-dimension risk score → Level 1/2/3, upgrade triggers, boundary review
  prd-extraction.md              PRD → manifest mapping, hidden-rule cues, gap question bank
  writing-rules.md               rule grammar, banned wording, prompt vs code vs orchestration, lock levels
  patterns.md                    13 reusable behavior patterns from a production agent spec
  validation-and-tuning.md       metrics, test derivation, experiment design, failure triage
  maintenance.md                 ownership, versioning, changelog, drift audits
templates/
  behavior-manifest.md           Level 2–3
  behavior-manifest-lite.md      Level 1
  behavior-tests.md
  tuning-plan.md
scripts/
  lint_manifest.py
examples/
  refund-assistant/              fictional PRD → Level 3 manifest, tests, tuning plan
```

## Where the ideas come from

- **The reusable patterns** (evidence-tagged fields, source precedence, decisions channel, "code measures, model reads", lock levels, signals become requests, single writer) are distilled from writing and testing the behavior spec for a production brand-memory agent.
- **The experiment and evidence-label practice** comes from prompt and model testing on the same project: change one variable at a time, and never present a planned test as a result.

## License

MIT. See [LICENSE](LICENSE).
