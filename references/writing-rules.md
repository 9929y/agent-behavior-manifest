# Writing Rules for a Manifest

A manifest is read by three audiences at once: the model (as instructions), engineers (as a
contract), and reviewers (as a design). Every sentence must survive all three.

## Rule grammar

```
R{n}. **{Short name}.** {Condition}, {imperative action}. {Threshold / order / tie-breaker}. {Otherwise …}.
```

Examples:

- ❌ "Be careful with sources and prefer reliable ones."
- ✅ "R2. **Source order.** When sources disagree about a value, use the higher one: locked policy › user correction › account record › official documents › observed behavior › recommendations. When two official documents disagree, apply E1."

- ❌ "Pick the most relevant photos."
- ✅ "R6. **Board.** Rank photos by how many of their tags are among the direction's 5 most common tags, then by date, newest first. Put the top 9 on the board. With fewer than 6, leave the board empty and add `photos` to `missing`."

## Ten writing rules

1. **Imperative and addressed to the agent.** "Return…", "Never…", "Ask…", not "The system should ideally…".
2. **One behavior per rule.** If a rule has "and also", split it.
3. **Numbers, not adjectives.** Write "3 sentences", "up to 9", "at least 2 in 5", "within 20°". Write "exactly 3", never "short".
4. **Every selection is deterministic.** Give a ranking key, a count, and a tie-breaker. The same input gives the same output.
5. **Every conflict has a winner.** Give a precedence or an escalation. "Use judgment" is not a winner.
6. **Facts vs inference.** Say which fields may contain inference, and require evidence for facts. "Never state a name, price, date, or claim that is not in the evidence."
7. **Allow unknowns.** Missing data becomes `null`, an empty list, or `missing`, never a plausible guess. A field the agent can't fill is a valid outcome.
8. **"Never" comes with "instead".** "Never approve merges. Instead, state the risks and that the developer decides."
9. **Define every noun once** (in Terms) and use it identically everywhere. Don't use synonyms for defined terms.
10. **Owner-facing text has no process narration.** No scores, confidence numbers, evidence counts, or internal ids in what users read.

## Banned or suspect wording

These words hide an unwritten rule. The linter flags them. Replace each one or justify it.

`should` · `ideally` · `try to` · `attempt to` · `as needed` · `if possible` · `where appropriate` ·
`appropriate` · `reasonable` · `relevant` (without a criterion) · `properly` · `correctly` (without a check) ·
`best effort` · `when necessary` · `etc.` · `and so on` · `user-friendly` · `robust` · `seamless` ·
`smart` · `intelligent` · `high-quality` · `as much as possible` · `generally` · `usually` · `be careful`

"Should" is allowed only when quoting a user or a source.

## Prompt vs code vs orchestration

Not every rule belongs in the prompt. Put each rule in the layer that can actually enforce it, and
note the layer in the manifest where it isn't obvious.

| Belongs in **code** | Belongs in **orchestration** | Belongs in the **prompt** |
|---|---|---|
| Counting (sentences, emoji, items), thresholds, measurements | Routing events, preconditions, concurrency (`busy`) | Interpretation, classification of meaning |
| Permission and access checks | Retries, backoff, timeouts | Tone, wording, judgment within a rubric |
| Versioning, commits, atomic saves | Which context each step receives | How to phrase refusals and handoffs |
| Deduplication, hashing, caching | Fan-out, waiting on dependencies | Separating facts from inference in prose |
| Schema validation of outputs | Running Definition-of-Done checks before commit | Following compiled instructions |

**Code measures, model reads.** When a value can be measured (a colour hex, a sentence count, a
share of the frame), code measures it and the model uses the number. Never let the model invent
numbers it could have been given.

## Compiling intent into instructions

Users speak in labels ("warm", "short", "premium"). Models follow concrete instructions far more
reliably than abstract labels. When the agent produces instructions for another model, compile them:

| Label | Compiled instruction |
|---|---|
| short | "Write exactly 3 sentences." |
| warm | "Target tone: warm, plain, specific. Preferred phrases: … Avoid phrases: … Example lines: …" |
| clean composition | "Subject in the lower third; at least 40% negative space above it." |

Give each compiled instruction a **lock level** so the consumer knows how strictly to follow it:

| Lock | Meaning | Use for |
|---|---|---|
| `hard` | Must hold; output fails validation otherwise | Measurable limits (length, counts, required fields) |
| `soft` | Follow unless it conflicts with a hard rule or the task | Tone, phrasing, structure |
| `guidance` | Consider; low confidence or taste | Values inferred from little evidence |

Lower the lock level automatically when the underlying value has low confidence.

## Tables over prose

Use tables for anything with more than two parallel items: actors, tools, events, stores, policy,
failure modes, escalations. Tables make gaps visible: an empty cell is a missing decision.

## Typed contracts

Write output and event shapes as TypeScript-style types or JSON Schema. Name every enum value.
Comment the meaning of any field whose name is not self-evident.
