# Depth Calibration: Risk Sets the Depth

Spend effort on behavior design in proportion to what can go wrong. Score four dimensions, then
choose a level.

## Score

| Dimension | Question | 0 | 1 | 2 |
|---|---|---|---|---|
| **Consequence** | Can it send, modify, buy, delete, publish, or affect other people? | Read-only, advisory, private draft | Writes reversible state the user sees before it matters | Irreversible or external action, money, other people affected |
| **Ambiguity** | Are inputs incomplete or conflicting, or do they need interpretation? | Structured input, one right answer | Some interpretation, sources rarely conflict | Sparse, conflicting, or subjective inputs; several defensible answers |
| **Duration** | Does it span sessions, run async, or rely on long-term memory? | Single turn | Multi-step within one session | Cross-session, background or async, persistent memory |
| **Accountability** | After a failure, is approval, remediation, an audit, or a named owner needed? | Nobody needs to know | A team would want to know and fix it | Approval, audit trail, compliance, or customer-facing remediation |

## Map to the risk matrix

Use **Consequence** and **Ambiguity** as the axes. Duration and accountability push the result up.

|  | Low consequence (0–1) | High consequence (2) |
|---|---|---|
| **Low ambiguity (0–1)** | **Light brief:** Role / Output / Done | **Permissions & confirmation:** Actions / Constraints / Approval |
| **High ambiguity (2)** | **Rules & evidence:** Core Rules / Evidence / Failure | **Full ten + tests:** cross-system, long-running, high consequence |

## Choose the level

| Level | Rule | Sections |
|---|---|---|
| **1 · Brief** | Total ≤ 2 and consequence = 0 | Role · Core Rules · Human Escalation · Output Format |
| **2 · Workflow** | Any other case that doesn't meet Level 3 | Level 1 + Scope · Failure Modes · Definition of Done (+ Terms recommended) |
| **3 · Full** | Consequence = 2, **or** duration = 2, **or** total ≥ 6, **or** it hands work to or from other agents | All ten + Terms + a behavior test on every rule |

**Indirect consequence counts.** Score consequence by what happens downstream, not just by the
agent's own tools. An agent that only writes memory or context, where that context steers other
agents that publish, send, or spend, scores consequence 2.

Quadrant emphasis applies at any level. A Level 2 feature in the "permissions & confirmation"
quadrant still needs a real Constraints section with a confirmation flow. A Level 2 feature in the
"rules & evidence" quadrant needs source precedence and evidence rules in Core Rules.

**When in doubt, choose the higher level.** The cost of an extra section is a review hour. The cost
of a missing one is a production incident.

## Upgrade triggers

Re-run calibration when any of these happens. Each one usually moves the feature up a level:

- A write, send, purchase, delete, or publish tool is added, even behind a flag.
- Memory starts persisting across sessions, or another feature starts reading it.
- The agent starts consuming another agent's output, or producing input for one.
- The audience changes: internal to customer-facing, or single user to shared/team.
- A regulated domain enters (money, health, legal, minors, personal data).
- Autonomy increases: from suggest, to act with confirmation, to act then notify.

## Boundary review: the four questions

Answer these in writing at the end of every manifest, whatever the level:

| Section | Question |
|---|---|
| Scope | Could it accept a task it should not take? |
| Constraints | Could it perform an action it should not take? |
| Human Escalation | Does it know when it must stop and hand control back? |
| Definition of Done | How does the team know the task is really done, and not just that the agent says so? |

An answer of "the prompt says not to" is weak. Name the enforcing layer for each answer:
prompt, orchestration, code, permission system, or UI confirmation.

## Calibration record (put this at the top of the manifest)

```markdown
> **Level 3 · Full** (consequence 2, ambiguity 1, duration 2, accountability 2 = 7)
> Why: issues refunds to customers' payment methods, remembers past conversations, and finance audits every refund.
> Upgrade watch: auto-approval above the current limit would need a new review.
```
