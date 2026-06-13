# Fix OMP Final Text Fallback

## Goal

Make the GA-TUI Oh My Pi runtime adapter usable under real RPC event variants by surfacing final assistant text even when OMP sends the visible answer only on terminal message frames instead of streaming it through `text_delta` events.

## Requirements

- Keep the current working streaming path unchanged: `message_update` frames with `assistantMessageEvent.type:"text_delta"` still emit `next` queue items and one final `done` queue item containing the accumulated buffer.
- Add a final-text fallback for OMP terminal frames that carry assistant message content without prior streamed deltas.
- Extract visible text from OMP message payloads shaped like `message.content:[{"type":"text","text":"..."}]`.
- Avoid duplicate final text when streamed deltas already populated the active buffer.
- Preserve terminal error behavior: `stopReason:"error"`, `errorMessage`, and `errorStatus` must still surface visible `[Oh My Pi] ...` done text.
- Preserve provider boundaries: `ohmypi_provider.py` owns only RPC/process/env/event mapping and must not import `app.py`, curses, or mutable TUI `State`.
- Do not modify system OMP config under `~/.omp/agent`.

## Acceptance Criteria

- [x] A real GA-TUI adapter smoke through `agent_runtime_registry().default().put_task(...)` returns non-empty Chinese text and uses `ohmypi`.
- [x] System `/home/vimalinx/.omp/agent/config.yml` hash remains unchanged across the smoke.
- [x] A fake RPC process that sends `message_end.message.content` text and no `text_delta` produces `{"done":"测试成功。","source":"ohmypi"}`.
- [x] Existing fake RPC streaming and terminal error tests continue to pass.
- [x] Required project checks pass: `py_compile`, `scripts/check_policy_gates.py`, `compileall`, `git diff --check`, and `ga-tui-check --root /home/vimalinx/Programs/GenericAgent`.

## Definition of Done

- Tests added or updated for the fallback behavior.
- Runtime adapter remains narrow and provider-local.
- Specs are updated if the final-message fallback contract was not already explicit.
- Work is committed before archival.

## Technical Approach

Add a small helper in `src/ga_tui/ohmypi_provider.py` to extract visible text from OMP message-like payloads. On `message_end`, store or finish with that text only when the active buffer is empty and no error text exists. On `turn_end` or `agent_end`, finish with the existing buffer, or with terminal-frame final text when available. Add regression coverage to `scripts/check_policy_gates.py`.

## Decision

Context: Real smoke with current OMP streamed correctly, but a protocol-compatible terminal-frame-only response currently maps to an empty `done` item.

Decision: Treat terminal-frame assistant text as a fallback output source, subordinate to streamed deltas and terminal errors.

Consequences: The TUI remains compatible with both streaming and final-only OMP event shapes without moving rendering or TUI state concerns into the provider.

## Out of Scope

- No changes to OMP itself.
- No changes to model setup UI beyond the already isolated runtime settings.
- No new writable host tools or direct memory writes.
- No modification of the user's system OMP installation or config.

## Technical Notes

- Real adapter smoke on 2026-06-13 selected `runtime_provider ohmypi`, used `/home/vimalinx/Programs/GenericAgent/memory/agent_harness/runtime/ohmypi/agent`, returned `测试成功。`, and kept the system OMP config hash unchanged.
- Failing reproduction before the fix: fake RPC sent `message_end.message.content:[{"type":"text","text":"测试成功。"}]` and then `turn_end`; the queue emitted `{"done":"","source":"ohmypi"}`.
- Relevant code: `src/ga_tui/ohmypi_provider.py`.
- Relevant tests: `scripts/check_policy_gates.py`.
- Relevant spec: `.trellis/spec/backend/agent-control-protocol.md`.
