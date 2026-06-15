# GA-TUI OMP Bridge Plugin

Project-managed Oh My Pi plugin for consuming GA-TUI-owned context and submitting governed memory proposals.

## Use Without Mutating System OMP

```bash
GA_TUI_REPO=/home/vimalinx/Programs/GenericAgent-TUI \
  omp --tool /home/vimalinx/Programs/GenericAgent-TUI/integrations/omp-ga-tui-plugin/tools/index.ts
```

This loads the GA-TUI bridge tools for that OMP process without linking the
plugin into the user's global OMP plugin store.

## Optional Persistent Link

Only run this if you explicitly want OMP to remember the plugin link:

```bash
omp plugin link /home/vimalinx/Programs/GenericAgent-TUI/integrations/omp-ga-tui-plugin
```

## Tools

- `ga_tui_context_get`: read a GA-TUI context pack and artifact ref.
- `ga_tui_memory_candidate_submit`: submit a memory candidate through GA-TUI validation and human approval.

The plugin does not write GA-TUI memory, approvals, schedules, or ledgers directly. It calls `ga_tui.agent_bridge`, and GA-TUI remains the source of truth.
