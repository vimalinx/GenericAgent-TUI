# Local Governance Paths For OMP Proposal Bridge

## Question

How should the next Oh My Pi fusion step connect OMP output to GenericAgent-TUI governed actions and memory approval without bypassing the Orchestrator?

## Local Evidence

- `src/ga_tui/ohmypi_provider.py` already supports OMP JSONL RPC, memory append prompt injection, memory candidate signals, and app-injected host tools.
- `src/ga_tui/app.py` now registers one read-only OMP host tool, `ga_tui_query`, through `ohmypi_tui_readonly_host_tool_definitions()` and `ohmypi_tui_query_host_tool_handler(state)`.
- `src/ga_tui/control_protocol.py` already maps current `memory_candidate` controls into `subagent_remember` controls.
- `src/ga_tui/app.py` already has `apply_tui_controls_from_text(state, text, source=..., default_target=...)`, which routes parsed controls through schedule, task, subagent, and session control handlers.
- `src/ga_tui/app.py` already has `queue_curated_memory_candidate(...)`, `build_memory_candidate(...)`, `append_memory_candidate_record(...)`, `queue_approval(...)`, approval inbox commands, artifact refs, agent mail, and traces for memory curation.
- `append_ohmypi_memory_candidate_signal(...)` currently stores OMP completion-derived memory candidate signals as `pending_signal` rows without approval ids. That is useful as a passive signal but is not yet the curated approval inbox loop.
- The backend spec requires OMP provider code to stay provider-local and not import `ga_tui.app`, curses, or mutable TUI `State`.

## Repo Constraints

- OMP must not mutate TUI ledgers or memory directly from provider code.
- GenericAgent-TUI should remain the Orchestrator and approval owner.
- Existing `ga-control.v2`, task ledger, approval, artifact, trace, and memory candidate stores should be reused.
- New OMP write-like behavior should be app-injected and auditable, similar to the read-only `ga_tui_query` bridge.
- Host URI schemes and arbitrary OMP host tools remain too broad for this step.

## Feasible Approaches

### Approach A: Add `ga_tui_propose`

Register a second app-owned OMP host tool that accepts bounded proposals:

- `proposal_type:"ga_control"` with a current `ga-control.v2` envelope or single `agenttask.v2` action.
- `proposal_type:"memory_candidate"` with target, statement, evidence ref, and optional task id.

The app-layer callback validates the proposal, runs it through existing TUI governance paths, and returns a structured result.

Pros:

- One auditable entry point for all OMP-to-TUI write-like intent.
- Reuses existing control parser and memory curator approval flow.
- Keeps provider protocol generic and provider-local.
- Fits the product goal: OMP can propose or initiate, TUI governs.

Cons:

- Needs careful validation to avoid accepting arbitrary retired controls or raw free-form text.
- Some allowed `ga-control.v2` actions may execute immediately if existing policy permits them.

### Approach B: Memory loop only

Only turn OMP memory candidate signals into curated approval inbox entries.

Pros:

- Smallest and safest.
- Directly closes the memory loop.

Cons:

- Does not advance OMP controlled actions.
- OMP still cannot use TUI governance as an action surface.

### Approach C: Direct action-specific host tools

Expose separate tools such as `task_update`, `delegate_create`, and `memory_candidate_create`.

Pros:

- Stronger per-tool schemas.
- Easier to document for model tool selection.

Cons:

- More surface area immediately.
- Duplicates logic already present in `ga-control.v2`.
- More likely to drift from the current control protocol.

## Recommendation

Use Approach A for the MVP. Add exactly one governed host tool, `ga_tui_propose`, with two proposal types:

- `ga_control`: current-schema controls only, executed through existing `apply_tui_controls_from_text()` so policy gates and ledger logic remain centralized.
- `memory_candidate`: routed to `queue_curated_memory_candidate()` so memory approval, artifact refs, agent mail, traces, duplicate/conflict checks, and approval inbox behavior remain centralized.

Keep direct long-term memory writes, host URI schemes, auto-approval, arbitrary OMP tool registration, and OMP internal subagent ledger mapping out of scope.
