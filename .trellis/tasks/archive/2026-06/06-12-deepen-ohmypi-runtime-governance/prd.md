# Deepen Oh My Pi Runtime Governance

## Goal

Continue the Oh My Pi / GenericAgent-TUI fusion after the first runtime-memory bridge. The next useful step is to let OMP see selected TUI governance state through a bounded, read-only RPC bridge while keeping GenericAgent-TUI as the Orchestrator and policy owner.

## What I Already Know

- User direction: continue fusing OMP and GenericAgent-TUI after the first experiment branch made OMP the default runtime and injected GA/TUI memory.
- Previous task `06-12-fuse-ohmypi-runtime-ga-memory` completed startup memory injection and post-run memory candidate signaling.
- Current branch is `experiment/ohmypi-runtime-memory`; working tree was clean before this task started.
- OMP is installed at `/home/vimalinx/.bun/bin/omp`, resolves to `/home/vimalinx/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent/src/cli.ts`, and reports version `15.10.8`.
- OMP CLI supports `--mode rpc`, `--mode rpc-ui`, `omp acp`, `--append-system-prompt`, `--no-tools`, `--tools=<list>`, `--approval-mode`, `--session-dir`, `--continue`, and `--resume`.
- OMP RPC supports `set_host_tools`, `host_tool_call`, `host_tool_result`, `set_host_uri_schemes`, and `host_uri_request` frames in local source.
- GenericAgent-TUI already has read-only query surfaces for `agent_list`, `task_list`, `approval_list`, `artifact_list`, and `capability_list`.
- The provider module must remain provider-local and must not import `ga_tui.app`, curses, or mutable TUI state.

## Assumptions

- This is still an experiment branch; we should keep changes reversible.
- The safest deeper fusion is read-only TUI governance visibility inside OMP, not immediate write capability.
- Host URI schemes and writable host tools should remain disabled until the read-only host tool bridge is proven.
- OMP internal subagents should remain provider-owned for this task; mapping them into first-class TUI subagents is a later step.

## Research References

- [`research/omp-rpc-governance-bridge.md`](research/omp-rpc-governance-bridge.md) - local source evidence for OMP RPC host tools, host URI schemes, extension UI, and safe MVP boundary.
- `.trellis/tasks/archive/2026-06/06-12-fuse-ohmypi-runtime-ga-memory/prd.md` - previous accepted bridge scope and out-of-scope list.
- `docs/runtime-provider-control-plane.md` - TUI owns governance; runtime providers are bounded execution.
- `.trellis/spec/backend/agent-control-protocol.md` - executable OMP provider contract.

## Requirements

- Add a provider-local RPC host tool bridge in `src/ga_tui/ohmypi_provider.py`.
- The bridge must register only TUI-owned read-only tools with OMP via `set_host_tools`.
- Initial host tool registration must happen after OMP emits `ready` and before/around the first prompt without blocking normal startup indefinitely.
- Host tool calls from OMP must be correlated by RPC frame `id` and answered with `host_tool_result`.
- Host tool results must be JSON-safe, bounded, and secret-safe.
- Host tool failures must answer OMP with `isError:true` and a textual error result instead of crashing the provider.
- Host tool cancellation frames must be handled safely, even if the TUI callback has already completed or never started.
- The provider metadata must distinguish read-only TUI host tools from unrestricted OMP host tools.
- The existing OMP queue mapping, memory injection, memory candidate signaling, missing-binary handling, and abort handling must keep working.

## Acceptance Criteria

- [x] `OhMyPiRpcAgent` can send a `set_host_tools` RPC command with at least one read-only TUI host tool definition.
- [x] A fake OMP `host_tool_call` frame receives a valid `host_tool_result` frame.
- [x] Unknown or failing host tool calls receive `host_tool_result` with `isError:true`.
- [x] Host tool definitions and call handling live in `ohmypi_provider.py`; TUI state callbacks are injected from `app.py`.
- [x] Provider metadata advertises `tui_readonly_host_tools` without enabling unrestricted `host_tools`.
- [x] `scripts/check_policy_gates.py` covers registration, success, error, cancellation, and provider boundary invariants.
- [x] `python3 -m py_compile src/ga_tui/app.py src/ga_tui/ohmypi_provider.py src/ga_tui/runtime.py scripts/check_policy_gates.py` passes.
- [x] `python3 scripts/check_policy_gates.py` passes.
- [x] `python3 -m compileall -q src scripts` passes.
- [x] `git diff --check` passes.
- [x] Architecture baseline comparison shows the task moves toward auditable Orchestrator-owned context instead of unconstrained runtime tools.

## Definition Of Done

- PRD and research are persisted under this task.
- Relevant Trellis backend specs are loaded before implementation.
- Implementation is covered by policy-gate checks.
- Runtime behavior is smoke-tested with fake RPC process frames, not real model calls.
- Changes are committed on `experiment/ohmypi-runtime-memory`.

## Out Of Scope

- Enabling arbitrary OMP built-in write tools through the TUI.
- Registering writable host URI schemes.
- Auto-approving OMP extension UI requests.
- Mapping OMP internal subagents into TUI task/subagent ledgers.
- Refactoring the full runtime API into a provider-neutral work-order API.
- Modifying or vendoring Oh My Pi source.

## Technical Approach

Recommended MVP: read-only TUI host tools.

- Add provider types for host tool definitions, host tool call frames, and callback results.
- Pass a host tool configuration/callback into `OhMyPiRuntimeAdapter` from `app.py`.
- After the OMP RPC process is ready, send `{"type":"set_host_tools","tools":[...]}`.
- When OMP emits `{"type":"host_tool_call",...}`, run the injected callback and send `{"type":"host_tool_result","id":...,"result":{"content":[{"type":"text","text":"<bounded json>"}]}}`.
- Keep all callbacks read-only and app-owned, for example a single `ga_tui_query` tool with an `endpoint` enum for runtime/capabilities/tasks/approvals/artifacts.

## Decision

Chosen direction: **Approach A: read-only TUI host tools**.

The user selected the recommended scope. This gives OMP access to GA/TUI orchestration context without bypassing approvals or creating write conflicts.

Alternative approaches:

- **Approach B: host URI schemes** - expose `ga-tui://tasks`, `ga-tui://approvals`, and similar resources to OMP. This aligns with OMP internal URL routing but introduces read/write scheme design and more protocol surface.
- **Approach C: provider-neutral work-order refactor** - clean architecture but too broad for a single continuation step.

## Technical Notes

- `src/ga_tui/ohmypi_provider.py` currently answers extension UI prompts conservatively and ignores host tool/URI frames.
- OMP local source files inspected:
  - `/home/vimalinx/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent/src/modes/rpc/rpc-mode.ts`
  - `/home/vimalinx/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent/src/modes/rpc/rpc-types.ts`
  - `/home/vimalinx/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent/src/modes/rpc/host-tools.ts`
  - `/home/vimalinx/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent/src/modes/rpc/host-uris.ts`
- Broad searches under `~/.omp/agent/sessions` can surface raw OMP session logs and should not be used as governance input or prompt material.

## Implementation Notes

- Added provider-local `RpcHostToolDefinition` support and bounded `host_tool_result` serialization in `src/ga_tui/ohmypi_provider.py`.
- Registered one app-owned `ga_tui_query` host tool that exposes read-only runtime, capability, agent, task, approval, and artifact metadata from `src/ga_tui/app.py`.
- Kept provider metadata explicit: unrestricted `host_tools:false`, read-only TUI bridge `tui_readonly_host_tools:true`.
- Updated `.trellis/spec/backend/agent-control-protocol.md` so this contract is now the source of truth.

## Verification

- `python3 -m py_compile src/ga_tui/app.py src/ga_tui/ohmypi_provider.py src/ga_tui/runtime.py scripts/check_policy_gates.py`
- `python3 scripts/check_policy_gates.py`
- `python3 -m compileall -q src scripts`
- `git diff --check`
- `ga-tui-check --root /home/vimalinx/Programs/GenericAgent`

## Architecture Baseline Comparison

This moves the system closer to `docs/agent-harness-architecture.md`: OMP remains a bounded runtime worker, while GenericAgent-TUI owns the Orchestrator context, policy metadata, task ledger, approval metadata, artifact refs, and memory governance. The bridge exposes read-only context through a single auditable host tool instead of enabling runtime-owned writes or free-form agent chatter.

Remaining gaps stay intentionally out of scope: writable action tools, host URI resource schemes, TUI approval mutation, OMP internal subagent-to-ledger mapping, checkpoint/eval trace expansion, and provider-neutral work-order refactoring.
