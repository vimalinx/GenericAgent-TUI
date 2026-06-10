# Merge model commands and provider tabs

## Goal

Unify the current `/llm`, `/model`, and `/models` model-management surfaces into one user-facing `/model` command. The unified model panel should keep current-session model switching and full model/provider management in one place, and present models grouped by provider/category using a tabbed layout similar to the supplied terminal screenshot.

## What I Already Know

* The user wants `/llm` and `/model` merged, with only one visible `model` command remaining.
* The user wants provider-based grouping/tabs for model selection, visually similar to the screenshot showing provider templates on the left and details on the right.
* Current `COMMANDS` exposes `/llm`, `/model`, and `/models`.
* Current `/llm` opens `open_llm_provider_adder(..., manage_configs=True)` for model configuration, provider add/edit, model extraction, validation, and default model management.
* Current `/model` and `/models` open `open_model_manager(..., manage_configs=False)` for current-session model switching.
* `draw_model_manager` currently renders a flat list of configured model entries, with mode-specific help text.
* The add/edit provider form already has provider categories and category switching (`provider_categories`, `provider_indices_for_category`, `first_provider_in_category`), so the new model panel can reuse existing category concepts instead of inventing a separate taxonomy.
* Existing smoke checks cover model switching, default model saving, recent model tracking, subagent default model assignment, model extraction, and `/llm`/`/model` help text.

## Assumptions

* `/model` should become the primary and only visible command in help/README/command completion.
* The unified `/model` panel should expose management actions directly rather than requiring a separate `/llm` mode.
* Existing model config storage in `mykey.py` should remain compatible.
* Provider tabs should be derived from configured entries and known provider templates, not from external network lookup.
* Existing keybindings should be preserved where practical: `Enter` switches current session, `d` sets default, `u` jumps recent, `a` adds provider/API, `e` edits, `p` extracts models, `t` tests selected model, `v` validates all, `x` deletes, `r` reloads, `Esc` exits.

## Open Questions

* None.

## Requirements

* There is one visible model command: `/model`.
* `/model` opens a unified model panel with both current-session switching and model configuration actions.
* `/llm` and `/models` no longer appear as primary commands in help/README/command completion.
* `/llm` and `/models` remain hidden backwards-compatible aliases that open the unified `/model` panel.
* The model panel groups configured model entries by provider/category with tab-like navigation.
* The model panel should still show current session model, default new-session model, and recent models.
* The model panel should still support adding/editing provider/API configs using the existing provider template form.
* The model panel should still support model extraction from a provider config and merging returned models without duplicates.
* The model panel should still support testing one model and validating all models.
* The model panel should still support setting the selected model as current-session model and default new-session model.
* Existing subagent model management must keep working.
* Existing architecture direction remains unchanged: model routing is subordinate to TUI governance and runtime provider metadata.

## Acceptance Criteria

* [x] `COMMANDS` shows `/model` as the single visible model command.
* [x] `/model` help text explains the unified panel and mentions configuration, switching, recent, default, extraction, validation, add/edit/delete.
* [x] `/llm` and `/models` remain hidden compatible aliases for the unified `/model` panel.
* [x] The unified model panel renders provider/category tabs and filters the model list to the selected provider/category.
* [x] The model panel supports switching tabs/categories from the keyboard.
* [x] Add/edit/provider-template flow still works and returns to the unified panel.
* [x] Existing model switching/default/recent/subagent model behavior is preserved.
* [x] `scripts/check_policy_gates.py` is updated for the new command behavior and passes.
* [x] `PYTHONPATH=src python -m ga_tui.integration doctor` passes.
* [x] `python -m py_compile src/ga_tui/app.py src/ga_tui/integration.py` passes.
* [x] README model command docs are updated.

## Definition Of Done

* Tests or smoke checks are updated for the changed command surface and panel behavior.
* Syntax checks and project smoke checks pass.
* Docs are updated where the command list changes.
* The implementation is compared against `docs/agent-harness-architecture.md` before finish.
* Rollback is straightforward: revert changes to command routing, model panel rendering/navigation, docs, and smoke checks.

## Out Of Scope

* Replacing GenericAgent model config storage.
* Adding a new runtime provider.
* Changing actual LLM request behavior.
* Redesigning subagent settings beyond preserving existing default-model behavior.
* Adding network discovery beyond the existing model extraction/probe path.

## Technical Notes

* Likely primary file: `src/ga_tui/app.py`.
* Current command declarations: `src/ga_tui/app.py` around `COMMANDS`.
* Current model manager render loop: `draw_model_manager` and `open_model_manager`.
* Current add/edit provider/API form: `draw_model_form` and `run_model_form`.
* Current command routing: help path in `submit`, key handling path in `handle_key`.
* Current docs: `README.md` model command section.
* Current smoke checks: `scripts/check_policy_gates.py` model-related assertions.
* Architecture references: `docs/agent-harness-architecture.md`, `docs/runtime-provider-control-plane.md`.
* Compatibility decision: `/llm` and `/models` are hidden aliases, not visible commands. This keeps one visible model command while preserving old command muscle memory.
