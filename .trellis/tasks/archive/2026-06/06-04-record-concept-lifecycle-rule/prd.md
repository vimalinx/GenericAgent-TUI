# Record concept lifecycle rule in AGENTS

## Goal

Persist the user's instruction in the repository-level `AGENTS.md` so future agents treat purged concepts as removed from the active system ontology instead of adding local prohibition patches.

## What I already know

- The user asked to record the rule in "agent.md"; this repository has a root `AGENTS.md`.
- The rule comes from the recent schedule-control regression: retired vocabulary was kept alive by active prompts and normal tests.
- The desired behavior is deletion/schema/invariant-first, not special-case rejection.

## Assumptions

- Root `AGENTS.md` is the intended project instruction file.
- This is a small documentation/instruction update, not a runtime code change.

## Requirements

- Add a clear instruction section to `AGENTS.md`.
- Define concept lifecycle handling for `purged` concepts.
- State that purged concepts must not be mentioned in active runtime, prompts, docs, normal tests, user-facing errors, or flowcharts.
- Prefer positive schemas, deletion, ontology updates, generic unsupported-field handling, and invariant checks over local guards.
- Keep wording concise enough to be usable by future coding agents.

## Acceptance Criteria

- [ ] `AGENTS.md` contains a durable rule for purged concept cleanup.
- [ ] The rule explicitly blocks "remove by adding explicit rejection branch" behavior.
- [ ] The rule is written generally, not only for the recent schedule example.
- [ ] Working tree is verified and the change is committed.

## Out of Scope

- No runtime code changes.
- No tests required unless the edited instruction file has a validation path.

## Technical Notes

- Target file: `AGENTS.md`.
