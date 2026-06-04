# Smooth GenericAgent TUI Upstream Integration

## Goal

Make the standalone `GenericAgent-TUI` integrate with `/home/vimalinx/Programs/GenericAgent` in a way that survives upstream GenericAgent updates with minimal conflict. The user wants to know whether the local TUI conflicts with upstream, and wants future updates to be smooth.

## What I already know

* `GenericAgent-TUI` is a separate curses TUI package with its own console script `ga-tui`.
* `src/ga_tui/app.py` dynamically finds the GenericAgent root via `GENERICAGENT_ROOT`, `GA_ROOT`, nearby sibling paths, or `/home/vimalinx/Programs/GenericAgent`.
* The TUI imports runtime core APIs from the GenericAgent checkout: `agentmain.GenericAgent`, `frontends/continue_cmd.py`, and `frontends/session_names.py`.
* Upstream GenericAgent `origin/main` is 120 commits ahead of the local core checkout and includes large TUI updates in `frontends/tui_v3.py` and `frontends/tuiapp_v2.py`.
* The external `GenericAgent-TUI` source does not directly edit upstream `frontends/tui_v3.py` or `frontends/tuiapp_v2.py`.
* Current local GenericAgent changes that overlap upstream are mainly launcher/integration changes in `ga_cli/cli.py`, cwd behavior in `agentmain.py`/`ga.py`, and local `frontends/tuiapp_v2.py` patches.

## Assumptions

* The preferred long-term direction is to keep `GenericAgent-TUI` as an external package and avoid carrying large local patches inside GenericAgent core.
* It is acceptable to add small helper scripts/modules in this repo to reinstall or verify the external TUI hook after upstream updates.
* It is not acceptable to silently rewrite or discard the user's existing dirty changes in `/home/vimalinx/Programs/GenericAgent`.

## Requirements

* Provide a clear answer on conflict scope: external TUI vs upstream TUI code, launcher patch vs upstream core.
* Add a maintainable integration mechanism that makes `GenericAgent-TUI` runnable without modifying upstream TUI source files.
* Keep the integration boundary small, explicit, and re-runnable after GenericAgent updates.
* Prefer environment/config based discovery over hard-coded local-only paths where feasible.
* Add a smoke-check path that verifies the external TUI can resolve the GenericAgent root and import required core modules.
* Do not update or merge GenericAgent core in this task unless explicitly requested later.

## Acceptance Criteria

* [x] The repository has a documented or scripted integration path for launching external `GenericAgent-TUI` from a GenericAgent checkout.
* [x] The integration path does not require carrying changes in upstream `frontends/tuiapp_v2.py`.
* [x] There is a quick command to validate that the external TUI can find GenericAgent and import the core dependencies.
* [x] The implementation is resilient to future upstream updates: after a pull, the user can rerun one command or use `ga-tui` directly.
* [x] Existing behavior of `PYTHONPATH=src python -m ga_tui` and `ga-tui` remains intact.

## Completion Notes

* Added `src/ga_tui/integration.py` with root discovery, dependency/import validation, generated launcher shim creation, and CLI entrypoints.
* Added console scripts: `ga-tui-check`, `ga-tui-install-core-shim`, and `ga-tui-integration`.
* Moved `src/ga_tui/app.py` root discovery to the shared integration helper.
* Documented the low-conflict update path in `README.md`.
* Installed the package through `pipx` because the system Python is PEP 668 externally managed.
* Installed a generated sidecar shim at `/home/vimalinx/Programs/GenericAgent/frontends/tuiapp_curses.py`; this remains an untracked GenericAgent sidecar.

## Verification

* `PYTHONPATH=src python -m py_compile src/ga_tui/app.py src/ga_tui/integration.py`
* `ga-tui-check`
* `ga-tui --help`
* `ga-tui-integration doctor --root /home/vimalinx/Programs/GenericAgent`
* `python /home/vimalinx/Programs/GenericAgent/frontends/tuiapp_curses.py --help`
* `PYTHONPATH=src python -m ga_tui --help`
* `python scripts/check_policy_gates.py`
* `git diff --check`

## Definition of Done

* Relevant specs/guidelines read before coding.
* Code compiles with `python -m py_compile`.
* Smoke command validates integration without starting curses interactively.
* Documentation explains the recommended future update flow.
* No unrelated dirty files are reverted.

## Out of Scope

* Merging `/home/vimalinx/Programs/GenericAgent` with `origin/main`.
* Rewriting upstream `frontends/tui_v3.py` or `frontends/tuiapp_v2.py`.
* Publishing an upstream PR.
* Solving all future GenericAgent API compatibility changes.

## Technical Notes

* Main external TUI entrypoint: `src/ga_tui/app.py`.
* Current console script: `ga-tui = ga_tui.app:main` in `pyproject.toml`.
* Current local core launcher patch: `ga_cli/cli.py` adds `_external_tui()` and points `ga tui` at `GenericAgent-TUI/src/ga_tui/app.py`.
* Upstream core changed `frontends/continue_cmd.py`, but the private functions used by the external TUI still exist on `origin/main`.
* A low-conflict strategy is to keep external TUI launch as its own installed command and provide a small re-runnable hook/shim installer for people who still want `ga tui` to route to the external TUI.
