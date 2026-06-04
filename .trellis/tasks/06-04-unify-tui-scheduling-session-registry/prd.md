# Unify TUI scheduling and session registry

## Goal

Make GenericAgent-TUI the owner of scheduling and sidebar session state so models do not bypass TUI governance through legacy GenericAgent scheduler files, and physical session archival does not make the TUI sidebar lose known history rows.

## What I already know

- The TUI prompt already describes `ScheduleCreate`, but the model read GenericAgent's `scheduled_task_sop.md` and followed the legacy `sche_tasks` / `reflect/scheduler.py` path.
- The TUI only exposes read-only query tools today. State-changing schedule creation is only a hidden text control block, so a model can drift to file/code tools after reading old SOPs.
- The TUI sidebar derives history from `model_responses*.txt` raw files, then decorates rows with `session_meta.json` and `session_names.json`.
- GenericAgent L4 archival can delete raw `model_responses*.txt` files without updating TUI metadata, so the sidebar loses rows even when display names and archived data still exist.
- Zip archives are not original `model_responses_*.txt` names, so this task should not blindly restore historical sessions.

## Requirements

- Add a TUI-owned schedule tool path for creating/listing schedules so "create a scheduled task" can call a TUI tool instead of inspecting legacy scheduler files.
- Keep `ga-control.v2` schedule actions as the protocol path, but make scheduled-task instructions explicit that TUI is the only active scheduler control plane.
- Prevent prompt/tool guidance from encouraging file/code inspection of external scheduler SOPs for schedule creation.
- Add a sidebar session-registry fallback that can show known sessions from TUI metadata even when the raw log path is missing due to physical archival.
- Mark missing-source rows with clear metadata so they do not pretend to be directly restorable raw sessions.
- Avoid destructive restoration or unzip operations in this task.
- Add regression coverage for the new schedule tool path and missing-source sidebar fallback.

## Acceptance Criteria

- [x] `schedule_create` creates a TUI schedule record through the same governed schedule registry as `ga-control.v2`.
- [x] `schedule_list` reports the TUI scheduled task registry without touching legacy scheduler files.
- [x] The active prompt tells the model schedule creation is TUI-owned and should not inspect or modify external scheduler files.
- [x] `load_history()` can keep a known session row visible from TUI metadata when its raw source file has disappeared.
- [x] Missing-source history rows are marked as archive-backed/missing-source and are not treated as normal raw restore candidates without a source file.
- [x] Policy gate checks pass.
- [x] No live history restoration or destructive filesystem change is performed.

## Completion Notes

- Committed tracked code changes through `ac0575a Refine schedule execution schema`.
- Schedule execution now has one current source of truth: `execution.mode:"tui_action"` for TUI-local reminders and `execution.mode:"agent_task"` for governed subagent work.
- `schedule.update` preserves the existing execution contract unless a new execution object is explicitly supplied, and trigger updates leave one current trigger source of truth.

## Out of Scope

- Do not unzip or restore historical sessions.
- Do not modify the sibling GenericAgent legacy scheduler in this task unless strictly needed for tests.
- Do not redesign the entire multi-provider session registry yet; implement the smallest durable bridge toward it.

## Technical Notes

- Main implementation target: `src/ga_tui/app.py`.
- Regression target: `scripts/check_policy_gates.py`.
- Spec target: `.trellis/spec/backend/agent-control-protocol.md`.
- Architecture baseline: `docs/agent-harness-architecture.md`.
