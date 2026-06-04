# Fix Trellis Tracking And Ignored Workflow Metadata

## Goal

Make Trellis workflow metadata trackable in Git so task archives, session journals, specs, workflow updates, scripts, and bundled project skills can be versioned. Keep runtime/cache/backup/local-identity files ignored.

## What I Already Know

* Trellis was updated locally from `0.5.16` to `0.5.19`.
* The update added `.agents/skills/trellis-spec-bootstarp/**` and updated `.trellis/scripts/common/task_store.py` plus `.trellis/workflow.md`.
* Previous `task.py archive` and `add_session.py` runs warned that `.trellis/` was ignored by root `.gitignore`, so Trellis could write local metadata but could not auto-commit it.
* Root `.gitignore` currently ignores `.agents/` and `.trellis/` wholesale.
* `.trellis/.gitignore` already ignores local-only Trellis runtime noise such as `.runtime/`, `.developer`, `.backup-*`, `*.tmp`, `*.new`, and Python cache files.
* `trellis-meta` local architecture docs identify `.trellis/tasks`, `.trellis/spec`, `.trellis/workspace`, `.trellis/workflow.md`, `.trellis/config.yaml`, `.trellis/scripts`, and `.agents/skills` as project-local Trellis layers.

## Assumptions

* The repo should track Trellis project workflow metadata now that the user explicitly asked to fix this.
* The repo should not track `.trellis/.runtime`, `.trellis/.backup-*`, `.trellis/.template-hashes.json`, `.trellis/.developer`, or `.codex/`.
* Existing `memory/`, `temp/`, `tmp/`, and `goal-*/` ignores remain correct.

## Requirements

* Root `.gitignore` must no longer ignore `.trellis/` and `.agents/` wholesale.
* Local Trellis runtime/cache/backup/state files must remain ignored.
* Trellis 0.5.19 updated files and bundled skill files must be visible to Git.
* Existing Trellis task/archive/journal/spec files must be visible to Git.
* Validation must demonstrate that Trellis archive/journal can add managed `.trellis` paths without the previous root-ignore failure.

## Acceptance Criteria

* [x] `git status --short --ignored=matching .trellis .agents` shows trackable Trellis files instead of `!! .trellis/` / `!! .agents/`.
* [x] `.trellis/.runtime/`, `.trellis/.backup-*`, `.trellis/.template-hashes.json`, and `.trellis/.developer` remain ignored.
* [x] `trellis --version` and `.trellis/.version` report `0.5.19`.
* [ ] A Trellis archive/journal operation no longer fails because `.trellis/` is ignored.
* [ ] Changes are committed in scoped commits without forcing ignored runtime/cache files into Git.

## Out Of Scope

* Changing Trellis upstream npm package behavior.
* Rewriting workflow phase semantics.
* Fixing old incomplete business tasks.
* Tracking `.codex/` or re-creating `.codex/config.toml`.

## Technical Notes

* Relevant local Trellis docs: `.agents/skills/trellis-meta/references/local-architecture/overview.md` and `generated-files.md`.
* Root `.gitignore` is the source of the current tracking blocker.
* `.trellis/.gitignore` should be preserved and allowed to filter Trellis-local noise.

## Definition Of Done

* Root ignore rules updated.
* Trackable Trellis files reviewed and staged intentionally.
* Trellis update artifacts from `0.5.19` are included.
* `python3 ./.trellis/scripts/get_context.py --mode record` works.
* `git status --ignored` proves runtime noise remains ignored.
* Work commit created.

## Verification Notes

* `trellis --version` and `.trellis/.version` both reported `0.5.19`.
* `python3 ./.trellis/scripts/get_context.py --mode record` completed and showed the current task.
* `python3 -m compileall -q .trellis/scripts` completed successfully.
* `git diff --check` completed successfully.
* `git check-ignore -v` confirmed `.trellis/.runtime/`, `.trellis/.backup-*`, `.trellis/.template-hashes.json`, and `.trellis/.developer` remain ignored.
* A trackable-file scan found no common credential patterns and no large files over 200 KiB.
