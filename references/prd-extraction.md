# From PRD to Manifest

PRDs describe outcomes and screens. A manifest describes behavior. The job is to translate the
first into the second without inventing product decisions along the way.

## Intake sheet

Fill this in before drafting. Every row carries a source tag.

| Item | What to capture | Tag |
|---|---|---|
| Feature & goal | One sentence: what changes for whom | `[SRC: §]` |
| Actors | Every human role and system that triggers, reads, or changes anything | |
| Triggers | Every way a run starts (UI action, event, schedule, another agent) | |
| Actions | Every verb the AI performs. Mark side effects: **R** read · **W** reversible write · **X** external or irreversible | |
| Data in | Sources, their reliability, who owns them | |
| Data out | Outputs, their readers (person / code / other agent) | |
| Persistence | What is remembered across runs | |
| Success metrics | As written in the PRD | |
| Non-goals | As written in the PRD | |
| Edge cases | Any the PRD mentions | |
| Open questions | Anything the PRD defers | |

## Mapping table

| PRD content | Becomes |
|---|---|
| Problem statement, target user, "the AI will…" | **Role**: identity, who it serves, authority |
| Non-goals, out of scope, future work, "v2" | **Scope**: outside-scope list |
| Integrations, APIs, data sources | **Scope**: tools table, with limits |
| User stories, flows, "when the user clicks…" | **Entry Points**: events, preconditions, required inputs |
| "Smart", "automatic", "relevant", "best", "personalized", ranking, matching | **Core Rules**: criteria, order, thresholds, tie-breakers |
| "Learns", "remembers", "gets better over time", history, profile | **Memory**: stores, provenance, write path, retention + optional **Learning loop** |
| Compliance, legal, brand, safety, permissions, "must never" | **Constraints**: hard boundaries + confirmation flows + policy table |
| Error states, empty states, offline, timeouts | **Failure Modes** |
| Approval flows, "the user reviews", admin, support handoff | **Human Escalation** |
| Screens that render AI output, API consumers, exports | **Output Format**: typed contract + example |
| Success metrics, acceptance criteria, QA notes | **Definition of Done** + **Tuning plan** metrics |
| Loading states, progress UI | **Progress & state** extension |

## Extraction cues

Hidden behavior lives in specific words. When you see one, write the rule it implies, or a
`[DECISION NEEDED]`.

| Cue in PRD | Hidden question |
|---|---|
| "automatically" | Without confirmation? What is the undo? Who is notified? |
| "smart" / "intelligent" / "AI-powered" | By what criterion? In what order? What threshold? |
| "relevant" / "best" / "top" | Ranked how? How many? How do ties break? |
| "learns" / "adapts" | From which signal? After how many? Who approves the change? |
| "personalized" | From what stored data? Can the user see and correct it? |
| "suggests" vs "applies" | Which one? This decides the level |
| "summarizes" / "extracts" | What if the source is silent? (Allow unknowns, never fill in) |
| "handles errors gracefully" | Which errors? What does the user see? What is retried? |
| "on behalf of" | Whose permissions? What does it do when they are missing? |
| "in real time" | What runs while another run is in progress? |
| "users can override" | Does the override persist? Does it beat future inferences? |

## Gap question bank

Ask the owner only the questions whose answers change behavior. Group them by owner.

**PM: outcomes and risk investment**
- What is the worst acceptable outcome of a wrong answer? Of a wrong action?
- Which success metric wins when it conflicts with safety or cost?
- Which adjacent request will users make most often that we refuse?

**Design: control, feedback, recovery**
- How does the user see what the agent did, what it skipped, and why?
- How does the user correct a result, and does the correction persist?
- What does the user see on partial, blocked, and failed runs?

**Engineering: capability, permissions, acceptance**
- What can each tool actually do, compared with what the scope allows?
- What is enforced in code rather than in the prompt?
- What is the commit boundary, the point after which side effects can't be undone?

## Never

- Never turn an `[ASSUMPTION]` into a rule without marking it.
- Never copy the PRD's adjectives into a rule ("relevant", "high-quality"). Translate them or flag them.
- Never let the manifest grow scope the PRD doesn't have. Put extra ideas in an "Out of scope (candidates)" note.
