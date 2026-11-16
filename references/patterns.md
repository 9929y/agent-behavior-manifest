# Reusable Behavior Patterns

These patterns were distilled from a production spec for a memory-owning agent: an agent that reads
messy user material, keeps a versioned profile, serves context to other generators, and learns from
user choices. Each pattern solves a problem that shows up again and again. Copy the structure and
rename the nouns.

| # | Pattern | Use when |
|---|---|---|
| P1 | Evidence-tagged fields | The agent states facts or keeps values users will trust |
| P2 | Allow unknowns | Inputs can be sparse |
| P3 | Source precedence ladder | More than one source can set the same value |
| P4 | Deterministic selection | The agent picks, ranks, or routes |
| P5 | Append-only versions + corrections in force | The agent maintains state over time |
| P6 | Single writer | Several agents or features touch the same store |
| P7 | Decisions channel | The agent must sometimes ask a person |
| P8 | Response taxonomy + atomic commit | Any agent with side effects |
| P9 | Code measures, model reads | Any value can be measured |
| P10 | Compiled context with lock levels | The agent feeds other models or agents |
| P11 | Signals become requests, not rewrites | Behavior should adapt to user choices or edits |
| P12 | Non-events list | The UI has many actions that look like triggers |
| P13 | Progress stages | The run is long enough to show progress |

---

## P1 · Evidence-tagged fields

Store every trusted value with its provenance instead of a bare value.

```ts
type Origin = 'locked' | 'user' | 'extracted' | 'derived' | 'recommended'
// locked       set by an authority above the user; read-only
// user         a correction by the user
// extracted    stated in the evidence (a quoted value, a measured value)
// derived      inferred from the evidence (a pattern or judgment)
// recommended  no evidence; a default or suggestion

interface Field<T> {
  value: T
  origin: Origin
  confidence: 'high' | 'medium' | 'low'
  evidence: string[]          // evidence ids; empty for 'recommended'
}
```

Confidence comes from a table, not a feeling. Use the first row that matches:

| Confidence | When |
|---|---|
| high | Origin `locked` or `user`; a value from an authoritative record; or ≥ 3 supporting evidence items |
| medium | 2 supporting evidence items |
| low | Everything else |

Then:
- List every `low` field path under `unconfirmed` in the output.
- Lower the lock level (P10) of instructions built from `low` fields.
- DoD check: every name, price, date, and claim appears in the evidence.

## P2 · Allow unknowns

Requiring a complete profile pushes the model to invent. Permit `null`, empty lists, and a `missing`
list, and treat them as valid results.

```
R5. Set `category` to null when no document states it. Never name a product from an image alone.
```

When the inputs are too thin for the main path, **route to a different path** (for example,
"recommend references instead of building a profile, and save nothing") instead of producing a weak
result that looks confirmed.

## P3 · Source precedence ladder

One line that settles most conflicts:

```
R2. When sources disagree about a value, use the higher one:
    locked values › user corrections › account record › official documents › observed behavior › linked pages › user picks › recommendations.
    List a value that a locked value overrides under `skipped` with reason `locked`.
```

Use *authority* to rank, not *frequency*. Ten campaign photos in purple don't override one brand
guideline that says green. Photos can still inform style. When two sources of **equal** rank
disagree, escalate (P7) instead of guessing.

## P4 · Deterministic selection

Every pick, rank, or route specifies a ranking key, a count or threshold, and a tie-breaker. Runs become
reproducible, testable, and explainable.

```
Rank by <key>, then by <key2>. Take the top <N>. With fewer than <M>, <fallback>.
Break ties by <earliest | newest | alphabetical | first in input order>.
```

## P5 · Append-only versions + corrections in force

- Each run that changes state saves a **new** version `v{n}`. Never edit a saved version.
- Copy unchanged values forward. List every changed value in `changes` with **one** reason from a fixed enum (`correction`, `new_evidence`, `removed_evidence`, `policy_change`, …).
- If nothing changed, save nothing and return the live version.
- A user correction is stored separately and **applied in every later run** until it is removed. A regeneration never silently drops it.
- "Stale" is computed (the inputs changed since the live version), not guessed.

## P6 · Single writer

Exactly one agent writes each store. The others **propose**: they send a typed change proposal
(target field, old/new value, scope, reason, evidence, and the version it was based on). The writer
validates it against locks, policy, and newer corrections, then commits or rejects it. A proposal
changes nothing by itself.

## P7 · Decisions channel

Instead of letting the agent ask ad-hoc questions, define a closed set of decision types it may
attach to an otherwise complete result:

```ts
type Decision =
  | { kind: 'conflict'; field: string; used: string; options: string[] }
  | { kind: 'unmapped_change'; change: string; options: string[] }
```

```
E1. Two documents state different values for one field, and the brand's own site states exactly one of them → use that value; no decision.
E2. Two documents disagree and the site states neither or both → use the most recently added; attach `conflict` with both options.
Ask the user questions only through these decisions.
```

This is **complete and flag**: the user gets a usable result plus a precise question, not a blocked
run. Keep **stop and ask** for cases where continuing would act on a guess.

## P8 · Response taxonomy + atomic commit

```ts
type Response =
  | { status: 'ok'; result: R; missing: string[]; unconfirmed: string[]; skipped: Skipped[]; decisions: Decision[] }
  | { status: 'blocked'; waiting_for: string; result: R }          // paused; resumes when the input arrives
  | { status: 'partial'; result: R; remaining: string[]; reason: string }
  | { status: 'failed'; stage: string | null; reason: string }
  | { status: 'rejected'; reason: 'out_of_scope' | 'precondition' | 'busy' }
```

- `rejected`: the run never started (scope, precondition, concurrency).
- `failed`: the run started and stopped. **Save nothing**, which means naming the write calls that must not happen.
- `ok` + `skipped`: a degraded success with itemized reasons (`unreadable`, `policy`, `locked`, …).
- Run the Definition-of-Done check **before** the commit call. A failed check means `failed` with the check as the reason.
- The catch-all row: "No rule covers the situation → stop, save nothing, return `failed`."

## P9 · Code measures, model reads

Split every perception task into **measured** fields (code: hashes, counts, colours, boxes, ratios)
and **read** fields (model: style, mood, composition category). Say which is which in the spec. Then
require: "Every number in the output comes from a measured field or a user correction." This removes
a whole class of hallucinated precision.

## P10 · Compiled context with lock levels

When the agent's memory is consumed by other models, don't hand them raw labels. Compile each rule
into one instruction with a lock level (`hard` / `soft` / `guidance`, see `writing-rules.md`). Per
consumer, include only the sections it needs:

| Consumer | Gets |
|---|---|
| text generator | facts, voice instructions, policy |
| image generator | facts, visual plan, palette, policy |
| campaign | both |

Some owner-facing values (for example, "vibe" words shown in a UI) are deliberately **never** sent to
generators. Generators get the concrete plan instead. Write that down as a rule.

## P11 · Signals become requests, not rewrites

To learn from user behavior without letting one click rewrite memory:

1. **Record** each choice as a signal: what was chosen, what was not, and what each option followed.
2. **Compare** it with the live value. Classify each compared field as `reinforce` (the chosen option matches the live value and an unchosen one doesn't), `diverge` (the reverse), or `no_signal`.
3. `reinforce` → add the signal as supporting evidence (it raises confidence). No user confirmation is needed. **The choice was the decision.**
4. `diverge` → count it in a *direction* (field + chosen value). At **N = 3** in one direction since the last version or the last dismissal, open a **request** the user can accept or dismiss.
5. Dismissing resets the count. Accepting applies the change as a user correction.
6. A signal is never evidence for anything else, never makes the profile stale, and never changes a value directly. Code makes every count and match.
7. Declare which fields a choice says **nothing** about (tone, facts, …). Never compare those.

The principle: **people decide what changes.** The agent only notices and asks.

## P12 · Non-events list

List the user actions that are *not* agent triggers, for example: "Board edits, palette edits,
approvals, restores, downloads, sharing changes, and single publishes are not events." This stops
both engineers and the model from wiring the agent to every click.

## P13 · Progress stages

For long runs, map each event to an ordered list of stage ids and say what work happens in each
stage. The UI's loading states (screen spec) bind to these ids, which keeps the behavior spec and the
screen spec in sync.

| Event | Stages |
|---|---|
| `onboarding.submit` | `read` → `analyze` → `compose` → `check` |
