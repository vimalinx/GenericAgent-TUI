# OMP Governed Actions And Memory Approval Loop

## Goal

After making Oh My Pi the default runtime and giving it read-only access to GenericAgent-TUI governance context, add a bounded way for OMP to propose governed TUI actions and curated memory candidates. The product goal is to make OMP useful as an agent runtime while keeping GenericAgent-TUI as the Orchestrator, policy owner, task ledger owner, artifact owner, and long-term memory approval owner.

## What I Already Know

- User direction: proceed with the recommended next step from the product roadmap: **OMP controlled actions + memory approval loop**.
- Previous work on this branch made OMP the default runtime, injected GA/TUI memory through `--append-system-prompt`, stored OMP memory candidate signals, and added read-only `ga_tui_query` host tools.
- Current branch is `experiment/ohmypi-runtime-memory`.
- Working tree was clean before this task was created.
- `ga-control.v2` is the current executable action protocol.
- Existing code already maps `memory_candidate` controls to subagent memory candidate behavior.
- Existing code already has curated memory candidate approval paths: candidate building, rejection, artifact refs, approval inbox, agent mail, traces, duplicate/conflict metadata, and approval commands.
- Provider code must remain provider-local and must not import `ga_tui.app`, curses, or mutable TUI `State`.

## Assumptions

- OMP should be allowed to propose governed actions, not bypass TUI policy gates.
- The first implementation should add one app-owned proposal bridge instead of many action-specific host tools.
- Existing `ga-control.v2` and memory candidate approval paths should be reused rather than duplicated.
- Direct long-term memory writes remain forbidden; all memory writes remain human-approved.

## Research References

- [`research/local-governance-paths.md`](research/local-governance-paths.md) - local code evidence for current `ga-control.v2`, OMP host tools, and memory approval paths.

## Requirements

- Add one app-injected OMP host tool for governed proposals, tentatively `ga_tui_propose`.
- Keep the existing read-only `ga_tui_query` host tool unchanged.
- The provider module should only handle generic OMP RPC host tool frames and must not know TUI state.
- The proposal host tool must support a memory candidate path that routes through `queue_curated_memory_candidate(...)`.
- The proposal host tool must support a current-schema action path that routes through existing `ga-control.v2` parsing/execution.
- Action proposals should execute through existing TUI policy gates rather than creating a separate universal approval layer.
- Proposal results must be JSON-safe, bounded, and include enough audit refs or result lines for OMP to continue.
- Unknown proposal types, missing required fields, invalid targets, parse errors, and callback failures must return structured error results, not crash the OMP stdout reader.
- Provider metadata must distinguish read-only host tools from governed proposal host tools and still keep unrestricted `host_tools:false`.
- Policy-gate tests must cover registration, success, error paths, and provider boundary invariants.

## Acceptance Criteria

- [x] OMP receives both `ga_tui_query` and `ga_tui_propose` host tool definitions through `set_host_tools`.
- [x] A fake OMP `ga_tui_propose` memory candidate call creates a governed memory candidate approval path through existing TUI functions.
- [x] A fake OMP `ga_tui_propose` current-schema control call routes through `apply_tui_controls_from_text(...)` and returns control result lines.
- [x] Invalid proposal calls return error payloads without crashing the provider.
- [x] Provider metadata advertises governed proposal host tools without enabling unrestricted `host_tools`.
- [x] `scripts/check_policy_gates.py` covers the proposal bridge and existing OMP runtime tests still pass.
- [x] `python3 -m py_compile src/ga_tui/app.py src/ga_tui/ohmypi_provider.py src/ga_tui/runtime.py scripts/check_policy_gates.py` passes.
- [x] `python3 scripts/check_policy_gates.py` passes.
- [x] `python3 -m compileall -q src scripts` passes.
- [x] `git diff --check` passes.
- [x] Architecture baseline comparison shows the change keeps OMP as a bounded runtime while GA/TUI owns orchestration, approval, ledgers, artifacts, and memory governance.

## Definition Of Done

- PRD and local research are persisted under this task.
- MVP scope is confirmed with the user.
- Relevant Trellis backend specs are loaded before implementation.
- Implementation is covered by policy-gate checks.
- Runtime behavior is smoke-tested with fake RPC process frames, not real model calls.
- Changes are committed on `experiment/ohmypi-runtime-memory`.

## Out Of Scope

- Arbitrary OMP host tools.
- Writable host URI schemes.
- Auto-approving OMP extension UI requests.
- Direct long-term memory writes.
- Mapping OMP internal subagents into first-class TUI subagent ledgers.
- Refactoring the full runtime API into a provider-neutral work-order API.
- Modifying or vendoring Oh My Pi source.

## Technical Approach

Recommended MVP: add one governed proposal host tool.

- Keep OMP RPC protocol handling inside `src/ga_tui/ohmypi_provider.py`.
- Keep TUI state callbacks inside `src/ga_tui/app.py`.
- Add `ga_tui_propose` alongside `ga_tui_query` in the app-injected OMP host tool definitions.
- For memory proposals, resolve a target subagent and call `queue_curated_memory_candidate(...)`.
- For action proposals, accept current-schema control payloads only and call `apply_tui_controls_from_text(...)`.
- Return a JSON-safe `ga-tui.proposal.v1` response with `status`, `kind`, result lines, and relevant ids/refs where available.

## Decision

Chosen MVP: **walk OMP action proposals through existing TUI gates**.

Context: OMP needs to become useful as an execution runtime without becoming a second Orchestrator. GenericAgent-TUI already has `ga-control.v2`, policy gates, task ledgers, approval queues, and memory curation.

Decision: `ga_tui_propose` accepts current-schema action proposals and routes them through `apply_tui_controls_from_text(...)`; risky operations are handled by existing policy gates. Memory proposals route through `queue_curated_memory_candidate(...)`.

Consequences: The product feels like OMP can act inside the harness, but all execution remains centralized in existing TUI governance paths. A future stricter mode can stage all OMP action proposals first, but that is out of scope for this MVP.

## Expansion Sweep

- Future evolution: this can become a provider-neutral proposal API for Codex/Claude/OMP runtimes, but this task keeps it OMP-specific and app-injected.
- Related scenarios: the proposal bridge should stay consistent with `ga-control.v2`, `/approvals`, memory candidate artifacts, task ledger traces, and runtime registry metadata.
- Failure and edge cases: invalid proposal schemas, missing state, ambiguous target subagents, parse errors, rejected memory candidates, policy-required approvals, and callback exceptions must all return structured errors/results.

## Open Questions

- None for MVP after user selected "walk existing gates".

## Technical Notes

- Local code inspected:
  - `src/ga_tui/ohmypi_provider.py`
  - `src/ga_tui/app.py`
  - `src/ga_tui/control_protocol.py`
  - `scripts/check_policy_gates.py`
  - `.trellis/spec/backend/agent-control-protocol.md`
- Memory signal path today: OMP completion text can create `pending_signal` memory candidate rows, but those rows do not yet become curated approval inbox entries.
- Existing curated memory candidate path already writes artifacts, approvals, agent mail, and traces.

## Implementation Summary

- Added app-owned `ga_tui_propose` alongside read-only `ga_tui_query` through `ohmypi_tui_host_tool_definitions()`.
- Kept `src/ga_tui/ohmypi_provider.py` generic: it still only registers app-injected tool definitions and dispatches RPC host tool frames.
- Added `ga-tui.proposal.v1` result payloads for `ga_control` and `memory_candidate` proposal results/errors.
- Routed `ga_control` proposals through current-schema `ga-control.v2` / `agenttask.v2` validation and `apply_tui_controls_from_text(..., source="agent:ohmypi_host_tool")`.
- Routed `memory_candidate` proposals through `queue_curated_memory_candidate(...)`, preserving Memory Curator artifacts, approval rows, traces, and human approval gates.
- Updated OMP provider metadata with `tui_governed_proposal_tools:true`, `tool_permissions:"tui_readonly_and_governed_proposal_tools_only"`, `memory_write:"candidate_only"`, and kept `host_tools:false`.
- Updated `.trellis/spec/backend/agent-control-protocol.md` to make the proposal bridge an executable backend contract.

## Verification

- `python3 -m py_compile src/ga_tui/app.py src/ga_tui/ohmypi_provider.py src/ga_tui/runtime.py scripts/check_policy_gates.py` passed.
- `python3 scripts/check_policy_gates.py` passed.
- `python3 -m compileall -q src scripts` passed.
- `git diff --check` passed.
- `ga-tui-check --root /home/vimalinx/Programs/GenericAgent` passed.

## Architecture Baseline Comparison

This moves the harness closer to `docs/agent-harness-architecture.md`: OMP can now initiate useful work, but GenericAgent-TUI remains the strong Orchestrator, policy owner, ledger owner, artifact owner, and memory approval owner. The implementation preserves restricted runtime behavior, explicit ledgers, artifact refs/provenance, human approval gates, and auditable protocol payloads.

Remaining gap: OMP internal tasks/subagents are still provider-owned and not mapped into first-class shared TUI ledgers. That remains intentionally out of scope for this MVP.
