# Maintain the Spec

A behavior manifest is a living contract. It must stay reviewable, testable, and versioned **with
the implementation**, in the same repository and through the same review process.

## Who owns the contract

| Owner | Owns | Signs off on |
|---|---|---|
| **PM** | User outcomes and risk investment | Role, Scope, the calibration level, success metrics, which `[DECISION NEEDED]` items are product decisions |
| **Design** | Control, feedback, recovery | Human Escalation, the human-facing parts of Output Format, failure states, user-understanding metrics, the progress-to-screen mapping |
| **Engineering** | Capability, permissions, acceptance | Entry Points, Memory, Constraints enforcement layers, Failure Modes, Definition of Done graders, the test harness |

Every section has exactly one owning role. Changes need that owner's review.

## Versioning

- Keep the manifest next to the code it governs (for example `agents/<name>/BEHAVIOR_MANIFEST.md`).
- Give it a semver header: **major** = a new or removed capability, a changed constraint, or a changed output contract. **Minor** = new rules, failure rows, or escalations. **Patch** = wording that doesn't change behavior.
- A pull request that changes agent behavior changes the manifest in the same PR, and the other way round.
- Tests reference rule IDs. A PR that changes `R7` must touch or rerun the tests that cover `R7`.

## Changelog

```markdown
## 1.3.0 · 2026-11-16
- R7 (changed): tie-breaker is now newest-first. Reason: T-R7-edge failed on duplicate timestamps. Evidence: triage #12. Owner: Eng.
- F9 (added): payment provider timeout → `failed`, save nothing. Reason: incident 2026-11-10. Owner: Eng.
- C3 (unchanged), E2 (wording only).
```

Rule IDs are never reused. A deleted rule keeps its ID in the changelog as *removed*.

## Change triggers

Review the manifest when:
- Any upgrade trigger in `depth-calibration.md` fires.
- A model, tool, or data source changes.
- The triage table finds a *spec gap*, *ambiguity*, or *conflict*.
- A user-understanding metric drops (the behavior may be right while the explanation is wrong).

## Drift audit (quarterly)

1. **Spec → code:** for every `C` item, confirm the enforcing layer still exists (permission, validator, confirmation UI).
2. **Code → spec:** list the tools, events, and stores in code. Anything not in the manifest is undocumented behavior.
3. **Tests → spec:** every `R/C/F/E` ID has a live test. Remove tests for removed IDs.
4. **Prompt → spec:** the compiled prompt still carries each rule that belongs in the prompt, word for word or explicitly compiled.
5. **Bloat check:** count the rules against last quarter. Merge or delete where you can.

## Deprecating behavior

Mark a rule `deprecated in X.Y`, keep it for one release with a test asserting the new behavior,
then remove it. Never silently change what an output field means. Add a new field instead.
