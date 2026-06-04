# Refine Scheduler Dispatch Result Contract

## Goal

Replace scheduler dispatch status inference from localized UI strings with a structured dispatch result contract. Scheduled agent work should still enter the existing governed `start_subagent_task()` path, but `dispatch_schedule_run()` must classify run status from explicit fields instead of parsing Chinese/English message text.

## What I Already Know

* The user wants to continue with the prioritized follow-up work after active ontology cleanup.
* `dispatch_schedule_run()` currently calls `start_subagent_task()` and then classifies the returned string through `schedule_dispatch_status()`.
* `schedule_dispatch_status()` currently checks phrases such as approval text, queued text, startup text, and failure words.
* `start_subagent_task()` is used by many UI and approval flows and currently returns user-facing strings; those strings should remain compatible.
* Schedule execution must continue to go through task ledger, policy gates, single-writer locks, agent mail, checkpoints, and traces.
* Existing tests cover due schedule dispatch, duplicate tick behavior, approval-required paths, and task-ledger creation.

## Assumptions

* The smallest safe change is to add a structured helper around subagent dispatch rather than changing all existing `start_subagent_task()` callers.
* `start_subagent_task()` should keep returning text for existing UI and command paths.
* The scheduler can determine `task_id` from ledger deltas and subagent state, but status should come from structured dispatch output.

## Requirements

* Add a typed/structured result for subagent dispatch with at least `status`, `message`, `task_id`, `approval_id`, and `error` fields.
* Scheduler agent-task dispatch must use the structured result instead of `schedule_dispatch_status()`.
* Remove or stop using localized string parsing for scheduler status classification.
* Preserve existing user-facing strings from `start_subagent_task()` for non-scheduler callers.
* Preserve schedule-run audit shape and existing statuses: `dispatched`, `queued`, `approval_required`, `failed`, and `rejected`.
* Tests must exercise at least normal dispatch and approval-required dispatch through scheduler without relying on localized status text parsing.

## Acceptance Criteria

* [x] `dispatch_schedule_run()` obtains scheduler status from structured dispatch fields.
* [x] `schedule_dispatch_status()` is removed or no longer used.
* [x] Normal due agent-task schedules still write `starting` then `dispatched` run rows and include `task_id`.
* [x] Risky scheduled work records `approval_required` and approval metadata without being classified through text matching.
* [x] Existing direct callers of `start_subagent_task()` keep receiving the same user-facing string style.
* [x] Project validation commands pass.

## Implementation Notes

* Added `SubagentDispatchResult` and `start_subagent_task_structured()` as a machine-readable wrapper around existing subagent dispatch.
* `dispatch_schedule_run()` now writes final schedule-run status from structured dispatch fields.
* Removed `schedule_dispatch_status()` localized text classification.
* Added scheduler approval-required coverage that asserts matching `task_id` and `approval_id`.
* Validation passed: `python3 -m py_compile src/ga_tui/app.py src/ga_tui/compat_legacy.py scripts/check_policy_gates.py`, `python3 scripts/check_policy_gates.py`, `python3 -m compileall -q src scripts`, `git diff --check`, and `ga-tui-check --root /home/vimalinx/Programs/GenericAgent`.

## Out Of Scope

* Full scheduler module extraction into `scheduler.py`.
* Scheduler overlap/concurrency policy.
* Full pytest migration.
* Changing Secret Vault subagent task return strings, except if needed for structured scheduler status.

## Technical Notes

* Relevant source: `src/ga_tui/app.py`.
* Relevant tests: `scripts/check_policy_gates.py`.
* Relevant spec: `.trellis/spec/backend/agent-control-protocol.md`, scheduled task scenario.

## Definition Of Done

* Tests updated for structured scheduler dispatch.
* `python3 -m py_compile src/ga_tui/app.py src/ga_tui/compat_legacy.py scripts/check_policy_gates.py` passes.
* `python3 scripts/check_policy_gates.py` passes.
* `python3 -m compileall -q src scripts` passes.
* `git diff --check` passes.
* `ga-tui-check --root /home/vimalinx/Programs/GenericAgent` passes.
* `docs/agent-harness-architecture.md` comparison is reported before close-out.
