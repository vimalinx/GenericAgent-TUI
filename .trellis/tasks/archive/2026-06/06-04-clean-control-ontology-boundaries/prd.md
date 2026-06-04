# Clean Active Control Ontology And Boundaries

## Goal

Remove retired control-protocol vocabulary from the active GenericAgent-TUI ontology so the main model only sees the positive `ga-control.v2` / `agenttask.v2` contract. The immediate priority is to stop legacy concepts from surviving as prompt text, parser aliases, ordinary tests, or active spec examples.

## What I Already Know

* The user identified the project direction as correct but risky because the control plane has grown large and old concepts are still present in active paths.
* `AGENTS.md` defines concept lifecycle rules: purged concepts should disappear from active system ontology, not remain as "do not use this" branches.
* `src/ga_tui/app.py` currently includes retired protocol vocabulary in `TUI_AGENT_CONTROL_HINT`.
* `src/ga_tui/app.py` currently maps current `ga-control.v2` actions into internal subagent/task execution actions and also still exposes legacy action names in active parser/control constants.
* `scripts/check_policy_gates.py` currently asserts several active prompt strings and includes normal legacy behavior tests.
* `.trellis/spec/backend/agent-control-protocol.md` currently documents legacy bad cases and legacy stripping as part of the active protocol spec.

## Assumptions

* The first shippable slice should prioritize concept cleanup over a large `app.py` module split.
* Historical compatibility may be retained only as clearly quarantined code, not as model-facing prompt guidance or current executable protocol.
* Tests should prefer positive schema behavior and active-prompt absence over assertions that lock exact prompt wording.

## Requirements

* Active prompt text must describe only the current positive protocol and must not mention retired protocol tokens.
* Active parser/schema handling must accept `ga-control.v2` / `agenttask.v2` dotted actions and reject non-current action names through generic unknown-action handling.
* Compatibility handling for historical hidden tags, if retained, must be isolated in a clearly named quarantine module and not dispatch runtime actions.
* Ordinary policy-gate tests must stop asserting exact prompt phrases where behavior or absence checks are more appropriate.
* The backend control-protocol spec must be updated so the active source of truth is positive schema/invariant language, not retired-concept examples.

## Acceptance Criteria

* [x] `TUI_AGENT_CONTROL_HINT` contains current `ga-control.v2` guidance without retired protocol vocabulary.
* [x] Active control extraction does not dispatch retired action names.
* [x] Any historical tag stripping is quarantined and only removes display/history artifacts.
* [x] Policy-gate tests include an active prompt absence check for retired protocol vocabulary.
* [x] Backend control-protocol spec no longer enumerates retired protocol tokens in active contract examples.
* [x] Project validation commands pass.

## Implementation Notes

* Added `src/ga_tui/compat_legacy.py` as a quarantine for historical persisted markup stripping and restored-session matching.
* Updated control extraction to accept only exact current dotted action names from `ga-control.v2` / `agenttask.v2`.
* Removed retired protocol vocabulary from the active control hint.
* Updated policy-gate tests to check current prompt/doc absence and to avoid exact schedule prose assertions.
* Validation passed: `python3 -m py_compile src/ga_tui/app.py src/ga_tui/compat_legacy.py scripts/check_policy_gates.py`, `python3 scripts/check_policy_gates.py`, `python3 -m compileall -q src scripts`, `git diff --check`, and `ga-tui-check --root /home/vimalinx/Programs/GenericAgent`.

## Out Of Scope

* Full `app.py` architectural split into `state.py`, `scheduler.py`, `control/`, `runtime/`, and related packages.
* Scheduler typed-dispatch-result refactor.
* Migration of all `scripts/check_policy_gates.py` coverage into pytest modules.
* Runtime provider adapter extraction.

## Technical Notes

* Relevant spec: `.trellis/spec/backend/agent-control-protocol.md`.
* Relevant guide index: `.trellis/spec/backend/index.md`.
* Relevant source surfaces found so far: `src/ga_tui/app.py`, `scripts/check_policy_gates.py`, `docs/runtime-provider-control-plane.md`, `README.md`.
* Current main-loop scheduler tick is present in `src/ga_tui/app.py`, but scheduler behavior is not part of this cleanup slice.

## Definition Of Done

* Tests added/updated for positive control schema and prompt absence.
* `python3 -m py_compile src/ga_tui/app.py scripts/check_policy_gates.py` passes.
* `python3 scripts/check_policy_gates.py` passes.
* `python3 -m compileall -q src scripts` passes.
* `git diff --check` passes.
* `docs/agent-harness-architecture.md` comparison is reported before close-out.
