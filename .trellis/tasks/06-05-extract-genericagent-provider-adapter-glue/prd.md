# Extract GenericAgent Provider Adapter Glue

## Goal

Move GenericAgent-specific runtime glue out of `src/ga_tui/app.py` into a focused provider adapter module so the main TUI file no longer owns GenericAgent monkey patches, GenericAgent tool handler injection, GenericAgent tool schema injection, or GenericAgent control-hint installation.

## What I Already Know

* `src/ga_tui/app.py` still defines the active `TUI_AGENT_CONTROL_HINT`, query/schedule tool schemas, `install_tui_query_tool_schema()`, `wrap_agentmain_tool_schema_loader()`, `tui_query_tool_outcome()`, `install_tui_query_handler_methods()`, `install_tui_query_runtime()`, `install_tui_control_hint()`, and `GenericAgentRuntimeAdapter`.
* Those functions directly patch `agentmain.load_tool_schema()` and `agentmain.GenericAgentHandler`.
* Runtime state is exposed to GenericAgent handlers through `agent._ga_tui_state`.
* The previous tasks extracted current control-protocol helpers to `src/ga_tui/control_protocol.py` and scheduler helpers to `src/ga_tui/scheduler.py`.
* `src/ga_tui/runtime.py` already defines provider abstractions and the GenericAgent provider spec, but not the GenericAgent-specific patch/install runtime.
* Regression coverage for these paths lives in `scripts/check_policy_gates.py`: tool schema idempotency, handler method presence, `StepOutcome(next_prompt:"\n")`, state-bound tool calls, control hint replacement/deduplication, and prompt vocabulary checks.

## Assumptions

* This is a provider-adapter glue extraction, not a full query-tool extraction.
* TUI query implementation functions may remain in `app.py` for this task because they depend on `State`, subagents, ledgers, approvals, artifacts, Secret Vault, gateway registry, and scheduler registry.
* The provider adapter module may receive app-layer callbacks and objects through explicit runtime configuration.
* The new module must not import `src.ga_tui.app`, curses UI code, or mutable `State`.
* Existing public names under `ga_tui.app` should remain available by import/re-export for compatibility with tests and external callers.
* No active prompt vocabulary should be changed except for moving ownership; this task should not reword the control protocol.

## Requirements

* Add a focused module, tentatively `src/ga_tui/genericagent_provider.py`, that owns GenericAgent-specific runtime glue.
* Move the GenericAgent control hint text and marker, query/schedule tool schemas, tool schema wrapping, handler method patching, `_ga_tui_state` binding, control hint installer, and `GenericAgentRuntimeAdapter` into that module.
* Keep `app.py` responsible for actual TUI state query implementations such as `tui_tool_agent_list()`, `tui_tool_schedule_create()`, and `tui_tool_schedule_list()`.
* Configure the provider adapter from `app.py` with `agentmain`, `GenericAgent`, `StepOutcome`, a state type/checker, and the tool handler map.
* Keep `agent_runtime_registry()` behavior compatible and still register the GenericAgent adapter as the default provider.
* Keep tool schema installation idempotent and resilient to GenericAgent schema reloads.
* Keep `GenericAgentHandler.do_*` patching idempotent.
* Keep control hint installation deduplicated and still replacing old GenericAgent-TUI hint blocks.
* Add regression coverage that the moved runtime glue is owned by `ga_tui.genericagent_provider` and the new module has no reverse import into `app.py`.

## Acceptance Criteria

* [x] `src/ga_tui/genericagent_provider.py` exists and imports without importing curses, mutable `State`, or `ga_tui.app`.
* [x] GenericAgent-specific monkey patching and `GenericAgentRuntimeAdapter` are no longer locally defined in `app.py`.
* [x] `app.py` re-exports compatibility names for `TUI_AGENT_CONTROL_HINT`, `TUI_QUERY_TOOL_SCHEMAS`, `TUI_SCHEDULE_TOOL_SCHEMAS`, `install_tui_query_runtime()`, `install_tui_control_hint()`, and `GenericAgentRuntimeAdapter`.
* [x] Query and schedule tools still install exactly once and re-install after GenericAgent `load_tool_schema()` reloads.
* [x] `GenericAgentHandler` still exposes `do_agent_list`, `do_agent_get`, `do_agent_match`, `do_task_list`, `do_task_get`, `do_approval_list`, `do_artifact_list`, `do_capability_list`, `do_schedule_create`, and `do_schedule_list`.
* [x] Handler methods still return `StepOutcome` with `next_prompt:"\n"`.
* [x] Runtime state binding through `agent._ga_tui_state` still works.
* [x] Control hint installation still deduplicates and replaces previous hint blocks.
* [x] `new_agent()`, model switching, subagent agent preparation, and interaction hook setup still call the provider-adapter installers through compatibility names.
* [x] Existing policy-gate tests pass.
* [x] Architecture baseline comparison shows movement toward a provider-adapter control-plane boundary.

## Definition Of Done

* Trellis specs are loaded before code edits.
* The provider extraction is behavior-preserving.
* Relevant Trellis spec is updated with the provider-adapter module boundary.
* Verification passes: `py_compile`, `scripts/check_policy_gates.py`, `compileall`, `git diff --check`, and `ga-tui-check`.
* Work is committed and the task can be finished with `trellis-finish-work`.

## Out Of Scope

* Rewriting query tool behavior or response schemas.
* Moving all TUI query implementations out of `app.py`.
* Changing `ga-control.v2` prompt wording.
* Replacing GenericAgent with another runtime provider.
* Creating a `runtime/` package that conflicts with existing `runtime.py`.
* Splitting Secret Vault, task ledger, gateway, or scheduler implementation further in this task.

## Technical Notes

* Candidate new module: `src/ga_tui/genericagent_provider.py`.
* Candidate app-layer provider config: `agentmain`, `GenericAgent`, `StepOutcome`, `is_state`, and a `tool_handlers` map.
* Current tool schema constants and hint text are GenericAgent-facing prompt/tool contracts, so moving them to the provider module matches the adapter boundary.
* TUI-local tool implementations remain app-layer callbacks to avoid importing `State` or ledger modules into the provider module.

## Completion Notes

* Added `src/ga_tui/genericagent_provider.py` as the source of truth for GenericAgent control hint text, query/schedule tool schemas, schema loader wrapping, `GenericAgentHandler` method patching, `_ga_tui_state` binding, control hint installation, and `GenericAgentRuntimeAdapter`.
* Updated `src/ga_tui/app.py` to import/re-export provider names for compatibility and configure the provider with `agentmain`, `GenericAgent`, `StepOutcome`, the `State` predicate, and app-owned `tui_tool_*` callbacks.
* Kept actual TUI query and schedule tool behavior in `app.py`, preserving ownership of mutable `State`, ledgers, approvals, artifacts, Secret Vault access, gateway capability data, and scheduler registry reads/writes.
* Updated `scripts/check_policy_gates.py` to assert provider-module ownership, app compatibility re-exports, no reverse provider import into `app.py`, and no local duplicate GenericAgent glue definitions in `app.py`.
* Updated `.trellis/spec/backend/agent-control-protocol.md` with the GenericAgent provider adapter boundary contract.

## Verification

* `python3 -m py_compile src/ga_tui/app.py src/ga_tui/genericagent_provider.py src/ga_tui/runtime.py src/ga_tui/control_protocol.py src/ga_tui/scheduler.py scripts/check_policy_gates.py`
* `python3 scripts/check_policy_gates.py`
* `python3 -m compileall -q src scripts`
* `git diff --check`
* `ga-tui-check --root /home/vimalinx/Programs/GenericAgent`
* Provider import probe confirmed `ga_tui.genericagent_provider` imports without loading `ga_tui.app`, and `app.py` re-exports/configures provider names after import.

## Architecture Baseline Comparison

This change moves the system closer to `docs/agent-harness-architecture.md`: GenericAgent is now a concrete runtime provider adapter rather than a patching layer embedded in the TUI composition file, while the TUI remains the strong Orchestrator/control plane that owns state, ledgers, approvals, artifacts, scheduler governance, and tool behavior. Remaining gaps are unchanged: `app.py` still owns many app-layer concerns and the next cleanup should keep extracting app-owned domains behind explicit boundaries without moving mutable `State` into provider modules.
