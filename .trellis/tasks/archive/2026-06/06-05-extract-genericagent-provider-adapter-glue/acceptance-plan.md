# GenericAgent Provider Adapter Glue Acceptance Plan

## Purpose

This plan verifies that GenericAgent-specific runtime patching moves out of `app.py` without changing GenericAgent-TUI behavior.

## Module Boundary

`src/ga_tui/genericagent_provider.py` must own:

* `TUI_AGENT_CONTROL_HINT`
* `TUI_CONTROL_HINT_MARKER`
* `LEGACY_TUI_CONTROL_HINT_BLOCK_RE`
* `TUI_QUERY_TOOL_SCHEMAS`
* `TUI_SCHEDULE_TOOL_SCHEMAS`
* `TUI_TOOL_SCHEMAS`
* tool schema injection into `agentmain.TOOLS_SCHEMA`
* wrapping `agentmain.load_tool_schema()`
* patching `agentmain.GenericAgentHandler.do_*`
* binding `agent._ga_tui_state`
* `install_tui_control_hint()`
* `GenericAgentRuntimeAdapter`

The module must not import `ga_tui.app`, curses, or mutable TUI `State`. It must receive app-layer behavior through explicit configuration.

## Behavior Acceptance

* Repeated runtime installation does not duplicate tool schemas.
* GenericAgent schema reload re-appends TUI tool schemas exactly once.
* GenericAgent handler methods exist for all query and schedule tools.
* Handler methods return `StepOutcome(data, next_prompt:"\n")`.
* Missing bound state returns tool/query errors instead of guessing.
* Bound state calls reach the same `tui_tool_*` implementations as before.
* Control hint install removes old GenericAgent-TUI hint blocks and leaves one current hint block.
* `GenericAgentRuntimeAdapter.create_agent()` still creates a GenericAgent and sets `inc_out`.
* `GenericAgentRuntimeAdapter.prepare_agent()` still installs tools and control hint.
* `GenericAgentRuntimeAdapter.start_agent()` still starts `agent.run()` in a daemon thread.

## Cross-Layer Acceptance

* `new_agent()` remains behavior-compatible.
* Model switching still calls tool runtime and control hint installers after selecting a model.
* `install_interaction_hook()` still binds runtime state.
* Subagent runtime creation/preparation still receives TUI tools and hint.
* Query tools still see Secret Vault subagents when Secret Vault is unlocked.
* Schedule tools still use the TUI-owned scheduler registry and do not touch external scheduler files.

## Test Plan

Run:

```bash
python3 -m py_compile src/ga_tui/app.py src/ga_tui/genericagent_provider.py src/ga_tui/runtime.py src/ga_tui/control_protocol.py src/ga_tui/scheduler.py scripts/check_policy_gates.py
python3 scripts/check_policy_gates.py
python3 -m compileall -q src scripts
git diff --check
ga-tui-check --root /home/vimalinx/Programs/GenericAgent
```

`scripts/check_policy_gates.py` should add or preserve assertions for:

* provider module ownership and no reverse imports
* app compatibility re-exports
* tool schema idempotency
* handler method patching
* control hint replacement/deduplication
* schedule tool behavior

## Rollback Plan

If behavior regresses, restore GenericAgent provider glue to `app.py` from the pre-task state and remove provider-module imports. Do not use destructive git commands without approval.
