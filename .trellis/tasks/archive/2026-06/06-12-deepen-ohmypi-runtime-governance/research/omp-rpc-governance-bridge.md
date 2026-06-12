# OMP RPC Governance Bridge Research

## Question

What is the next safe integration seam after making OMP the default runtime and injecting GA/TUI memory?

## Local Evidence

- `omp --help` reports version `15.10.8` and supports `--mode rpc`, `--mode rpc-ui`, `omp acp`, `--append-system-prompt`, `--no-tools`, `--tools=<list>`, `--approval-mode`, `--session-dir`, `--continue`, and `--resume`.
- `/home/vimalinx/.bun/bin/omp` resolves to `/home/vimalinx/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent/src/cli.ts`.
- `src/modes/rpc/rpc-types.ts` defines `set_host_tools`, `set_host_uri_schemes`, `host_tool_call`, `host_tool_result`, `host_tool_update`, `host_uri_request`, and `host_uri_result`.
- `src/modes/rpc/rpc-mode.ts` creates `RpcHostToolBridge` and `RpcHostUriBridge`, handles `set_host_tools`, and emits host tool calls to the RPC host.
- `src/modes/rpc/host-tools.ts` shows that host tool calls are correlated by a generated frame `id`, include `toolName` and `arguments`, and expect `host_tool_result` with an `AgentToolResult`-shaped `content` array.
- `src/modes/rpc/host-uris.ts` shows host URI schemes can be writable and register process-global internal URL handlers, which is a larger governance surface.
- RPC extension UI supports `confirm`, `select`, `input`, `editor`, `notify`, `setStatus`, `setWidget`, `setTitle`, `set_editor_text`, and `open_url`. The current GA/TUI provider already denies interactive prompts conservatively.

## Repo Constraints

- `ohmypi_provider.py` must not import `ga_tui.app`, curses, or mutable TUI `State`.
- GenericAgent-TUI owns policy gates, ledgers, approvals, artifacts, and memory governance.
- Existing TUI query tools already expose read-only state for agents, tasks, approvals, artifacts, and capabilities.
- The first OMP fusion task intentionally left host tools, host URI schemes, and OMP subagent ledger mapping out of scope.

## Feasible Approaches

### Approach A: Read-only TUI host tools

Register one or more RPC host tools that OMP can call to inspect bounded TUI governance state.

Pros:

- Gives OMP useful GA/TUI orchestration context during execution.
- Keeps TUI as host and policy owner.
- Uses OMP's supported RPC protocol without patching OMP.
- Testable with fake RPC frames.

Cons:

- Requires careful JSON bounding and secret hygiene.
- Does not yet expose artifact contents or writable actions.

### Approach B: Read-only host URI schemes

Register `ga-tui://...` resource schemes so OMP's read tool can resolve TUI resources.

Pros:

- Resource-like model fits artifact refs and memory refs.
- Could become the cleanest bridge for `ga-tui://tasks/<id>` and `ga-tui://approvals`.

Cons:

- Host URI bridge has writable flags and process-global router behavior.
- Larger contract to design before first safe integration.

### Approach C: Provider-neutral work-order refactor

Replace GenericAgent-shaped runtime hot paths before exposing more OMP-specific behavior.

Pros:

- Architecturally clean.

Cons:

- Too broad for the next continuation step.
- Does not validate OMP's practical runtime benefits quickly.

## Recommendation

Implement Approach A first. Register read-only TUI host tools and answer OMP `host_tool_call` frames from injected app-layer callbacks. Keep writable host URI schemes, approval mutation, direct memory writes, and OMP subagent ledger mapping out of scope.
