# AI Slop Cleanup

## Goal

Run a bounded anti-slop cleanup pass on GenericAgent-TUI that preserves current behavior, removes low-signal cleanup candidates, and improves maintainability without broad rewrites.

## What I Already Know

* User invoked `$ai-slop-cleaner`, so the requested workflow is regression-tests-first cleanup/refactor rather than feature work.
* Repository is a Python curses TUI and local agent harness control plane for GenericAgent.
* `ga-tui` integration currently passes: the TUI discovers `/home/vimalinx/Programs/GenericAgent` and imports `agentmain` / `continue_cmd`.
* `src/ga_tui/app.py` is still the central monolith at roughly 21k lines.
* Recent commits have already extracted `scheduler`, `control_protocol`, `runtime`, and `genericagent_provider` seams from `app.py`.
* The active architecture baseline is `docs/agent-harness-architecture.md`: strong Orchestrator, restricted subagents, ledgers, artifacts, single-writer, approval gates, auditable communication, memory hydration, recovery/eval/trace, and A2A/MCP compatibility.
* The active executable backend spec is `.trellis/spec/backend/agent-control-protocol.md`.
* Current dirty state before this task included an untracked Trellis planning task: `.trellis/tasks/06-06-merge-model-commands-provider-tabs/`.
* This task added only its own Trellis task directory so far.

## Assumptions

* Preserve external behavior and CLI entry points unless the user explicitly chooses a larger cleanup scope.
* Prefer small, reversible cleanup in one coherent area over a broad project-wide rewrite.
* Treat fallback-like code as evidence to classify first, not as automatic deletion.
* Do not modify unrelated untracked Trellis task state.

## Open Questions

* None.

## Requirements

* Lock behavior with targeted existing or new regression checks before cleanup edits.
* Build an explicit cleanup plan before touching business code.
* Search the selected scope for fallback-like signals, classify each finding, and resolve or defer explicitly.
* Execute cleanup smell-by-smell, starting with safest/highest-signal changes.
* Keep changes bounded to the model/provider management slice in `src/ga_tui/app.py` unless a test requires a small adjacent update.
* Compare any harness behavior changes against `docs/agent-harness-architecture.md` before claiming completion.

## Acceptance Criteria

* [x] Cleanup scope is explicitly chosen and recorded.
* [x] Behavior lock is documented before cleanup edits.
* [x] Fallback-like findings in scope are inventoried and classified.
* [x] Cleanup plan lists concrete smells and pass order.
* [x] Relevant regression checks pass after each meaningful pass.
* [x] Final report includes changed files, simplifications, fallback review, checks run, remaining risks, and architecture-baseline direction.

## Definition of Done

* Tests added or updated where behavior is not already locked.
* `scripts/check_policy_gates.py` passes when relevant to the selected scope.
* Python compile checks pass for modified modules.
* `git diff --check` passes.
* `ga-tui-check --root /home/vimalinx/Programs/GenericAgent` passes when GenericAgent checkout is available.
* Specs or notes are updated only if this cleanup discovers a reusable convention or invariant.

## Candidate Approaches

### Approach A: Provider/runtime seam cleanup (Recommended)

Clean the recently extracted runtime-provider seam and adjacent `app.py` compatibility glue. Likely scope: `src/ga_tui/runtime.py`, `src/ga_tui/genericagent_provider.py`, `src/ga_tui/scheduler.py`, and only directly necessary `app.py` re-export or delegation lines.

Pros: aligned with recent extraction direction, bounded, testable with existing policy gates, lower risk.

Cons: does not directly shrink the largest `app.py` sections beyond adjacent glue.

### Approach B: One `app.py` monolith slice

Pick one coherent `app.py` slice such as model manager, approvals panel, secret vault helpers, or subagent runtime control and clean/extract it.

Pros: attacks the biggest maintainability problem.

Cons: higher regression risk because curses UI, runtime state, and GenericAgent integration are tightly coupled.

Decision: selected by user on 2026-06-10. The pass will focus on one coherent `src/ga_tui/app.py` slice, chosen after code inspection and behavior-lock review.

## Selected Scope

Model/provider management slice in `src/ga_tui/app.py`, centered on:

* `model_form_fields`
* `choice_values_for_field`
* `cycle_value`
* `draw_model_form`
* `run_model_form`
* `default_entry_index`
* `save_default_model`
* `probe_and_merge_models`
* `open_model_manager`
* `open_llm_provider_adder`

This slice is selected because `open_model_manager` is one of the largest remaining `app.py` functions, it has repeated save/reload/message branches, it is adjacent to recent provider/runtime extraction work, and existing policy gates already cover model orchestration, model defaults, provider metadata, and manager helper behavior.

User confirmed this scope on 2026-06-10.

## Behavior Lock

Baseline checks run before cleanup edits:

* `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/ga_tui/app.py src/ga_tui/runtime.py src/ga_tui/genericagent_provider.py src/ga_tui/scheduler.py scripts/check_policy_gates.py` — PASS
* `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_policy_gates.py` — PASS

## Cleanup Plan

Fallback-like code resolution gate:

* Inventory only this selected slice before editing.
* Preserve grounded UI/IO fail-safe handling such as curses modal cancellation, validation failures, probe failures, and reload failures.
* Treat silent or duplicated error-handling branches as cleanup candidates only if behavior remains explicit and covered.

Pass 1: Dead code deletion

* Remove only unreachable or unused local variables/branches inside the selected slice if proven by inspection and tests.

Pass 2: Duplicate removal

* Consolidate repeated save/reload/recent-model refresh/message patterns in `open_model_manager`.
* Avoid new speculative abstraction; helper extraction must directly reduce repeated branches.

Pass 3: Naming/error handling cleanup

* Clarify helper names and return messages where existing code is ambiguous.
* Preserve user-facing Chinese copy unless it is duplicated or misleading.

Pass 4: Test reinforcement

* Add or extend narrow checks in `scripts/check_policy_gates.py` only if the cleanup introduces a helper or touches behavior not already covered.

## Fallback Findings

Initial selected-scope classification:

* Curses modal cancellation and `KeyboardInterrupt` / `curses.error` handling: grounded UI fail-safe fallback, preserve.
* Model probe failure branches: grounded external-provider failure path, preserve explicit messages.
* Save/reload branches repeated after add/edit/delete/probe/default changes: duplication, cleanup candidate.
* Numeric validation in `run_model_form`: grounded input-validation failure path, preserve behavior.
* Default provider/template fallback from configured providers to built-in providers is outside this selected slice unless an adjacent helper call requires inspection.

### Approach C: Audit-only slop map

Do not change business code yet. Produce a ranked cleanup inventory with fallback classifications, test gaps, and recommended next Trellis tasks.

Pros: safest and useful for planning.

Cons: does not remove slop in this pass.

## Out of Scope

* Broad rewrite of the TUI.
* Changing the current `ga-control.v2` protocol semantics without explicit requirement.
* Changing GenericAgent core code.
* Modifying unrelated active Trellis tasks.
* Pushing to remote.

## Technical Notes

* Initial fallback-like inventory found many broad signals, especially `except Exception`, `pass`, compatibility shims, defaults, temporary/session handling, and scheduler skip paths. These need scope-bounded classification before any deletion.
* `scripts/check_policy_gates.py` is the main regression gate for protocol/provider/scheduler behavior.
* Existing docs identify `GenericAgent` as default runtime provider while keeping future providers additive.
* Current backend spec files are uneven: `agent-control-protocol.md` is active, while several generic backend guidelines remain placeholders.

## Completion Notes

Changed files:

* `src/ga_tui/app.py` — added `save_model_manager_entries()` and reused it across model add/edit/delete/probe flows to remove repeated save-and-reload branches.
* `scripts/check_policy_gates.py` — added a regression check for the helper's success and save-failure behavior.

Fallback review:

* Preserved grounded UI fail-safe paths for modal cancellation, curses errors, probe failures, validation errors, and reload failures.
* Classified repeated save/reload fallback handling as duplication and replaced it with a single helper.
* No ambiguous architectural fallback required `$ralplan` escalation.

Quality gates run:

* `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile src/ga_tui/app.py src/ga_tui/runtime.py src/ga_tui/genericagent_provider.py src/ga_tui/scheduler.py scripts/check_policy_gates.py` — PASS
* `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_policy_gates.py` — PASS
* `PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q src scripts` — PASS
* `git diff --check` — PASS
* `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m ga_tui.integration doctor --root /home/vimalinx/Programs/GenericAgent` — PASS

Spec update decision:

* No `.trellis/spec/` update needed. This cleanup introduced no new command/API signature, storage contract, provider boundary, or cross-layer behavior.

Architecture baseline direction:

* Moves slightly closer to the baseline by reducing duplicated model-provider control-plane glue in `app.py` while preserving the existing GenericAgent provider/runtime governance path.
