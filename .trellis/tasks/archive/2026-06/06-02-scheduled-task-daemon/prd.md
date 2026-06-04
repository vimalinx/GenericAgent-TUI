# Implement Scheduled Task Daemon

## Goal

Implement real scheduled-task execution for GenericAgent-TUI. Existing schedule controls can register, update, enable, disable, and delete jobs, but registered jobs do not yet run. The TUI should become the top-level scheduler owner: it decides when a job is due, records an auditable run, dispatches the work through the governed `agenttask.v2` path, and prevents duplicate execution.

## Context

- `docs/runtime-provider-control-plane.md` defines the direction: TUI owns scheduled task registry and recurring dispatch through `agenttask.v2`.
- `src/ga_tui/app.py` already persists schedule records to `AGENT_SCHEDULES_PATH` and exposes `/schedules`.
- `scripts/check_policy_gates.py` already verifies schedule control registration, registry output, MCP resources, and runtime provider metadata.
- The project architecture baseline requires ledgers, approval gates, artifact refs, and auditable agent communication. Scheduled jobs must not bypass that.

## Requirements

- Add due-job evaluation for supported schedule triggers:
  - `at`: ISO-like absolute timestamp.
  - `interval`: simple recurring intervals such as `10m`, `2h`, `1d`, and plain seconds.
  - `cron`: basic five-field cron syntax for minute/hour/day/month/weekday.
  - `trigger`: preserve compatibility with existing records by treating recognizable `interval:` / `at:` / `cron:` strings as executable.
- Add a scheduler tick/daemon surface that can be called by the TUI and by tests without launching a separate long-running process.
- Dispatch due jobs through existing `agenttask.v2`/delegation code paths rather than direct backend prompt execution.
- Append auditable schedule-run records including run id, schedule id, due time, dispatch result, status, and error details.
- Prevent duplicate runs with an idempotency key and persisted last-run metadata.
- Respect disabled/deleted schedules and missing/invalid trigger definitions.
- Surface scheduler status in `/schedules` output so users can tell whether jobs are merely registered or actually runnable.
- Keep GenericAgent as the default provider, but preserve explicit provider metadata for future runtime adapters.

## Non-Goals

- Do not implement a systemd service or external daemon installer in this task.
- Do not add a full cron parser dependency.
- Do not bypass policy gates or auto-approve risky work.
- Do not implement provider-specific dispatch for Codex/Claude/OpenAI SDK yet.

## Acceptance Criteria

- Schedule records can be evaluated as due/not due deterministically in tests.
- A due enabled schedule creates a governed dispatch attempt using existing task/delegation machinery.
- The scheduler records successful, skipped, duplicate, invalid, and failed run outcomes.
- `/schedules` shows scheduler-run state and next actionable information.
- Regression tests cover due evaluation, duplicate prevention, disabled/deleted skip, and control-plane formatting.
- `python3 -m py_compile src/ga_tui/app.py src/ga_tui/runtime.py scripts/check_policy_gates.py` passes.
- `python3 scripts/check_policy_gates.py` passes.
- `python3 -m compileall -q src scripts` passes.
- `git diff --check` passes.
- `ga-tui-check --root /home/vimalinx/Programs/GenericAgent` passes when the sibling GenericAgent checkout exists.

## Architecture Baseline Impact

This change should move the system closer to `docs/agent-harness-architecture.md` by making scheduled work governed, ledgered, and auditable instead of passive registry metadata.

Remaining gaps expected after this task:

- No external service manager installer yet.
- No full cross-runtime scheduler dispatch for non-GenericAgent providers yet.
- Artifact references will depend on existing delegation output rather than a dedicated scheduler artifact store.
