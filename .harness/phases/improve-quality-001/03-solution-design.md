# Solution Design

## Current Context

Bridle is split into core workflow/state/validation modules, Typer commands, and a Textual TUI. Existing tests cover core models but some assertions are too loose to catch regressions. The active audit found three correctness-oriented gaps:

- `Validator` does not compare active `state.required_nodes` with the route derived from `workflow.yaml`.
- `NewRunModal` exposes intent/risk selections, but `HarnessApp.action_new_run()` ignores them and creates `FEATURE/MEDIUM`.
- Standard package installs do not explicitly include `templates/` and `locales/`, while PyInstaller does.

## Recommended Approach

Make the smallest behavior-preserving changes:

- Extend `Validator._check_state_json()` or a focused helper to load workflow and compare `required_nodes` with `workflow.route(intent, risk)`.
- Keep historical drift behavior explicit: report an error for the active state because `state.json` is the current source of truth; snapshots remain data files unless switched active.
- Change `NewRunModal` to return a structured value containing `run_id`, `intent`, and `risk`.
- Update `HarnessApp.action_new_run()` to create the state using the selected intent/risk and route.
- Add setuptools package-data configuration for templates and locales.
- Replace the tautological strict-mode test and add focused tests for drift and modal payload creation.

## Affected Files / Modules

- `harness_cli/src/harness_cli/core/validate.py`
- `harness_cli/src/harness_cli/ui/dashboard.py`
- `harness_cli/src/harness_cli/ui/widgets/new_run_modal.py`
- `harness_cli/pyproject.toml`
- `harness_cli/tests/test_validate.py`
- Optional focused TUI/widget test file under `harness_cli/tests/`

## Data Flow

```text
state.json intent/risk
  -> Workflow.route(intent, risk)
  -> Validator compares route to state.required_nodes
  -> ValidationReport error on mismatch

NewRunModal selections
  -> NewRunRequest(run_id, intent, risk)
  -> HarnessState.create_new(...)
  -> state.required_nodes = workflow.route(intent, risk)
```

## Compatibility

- CLI command names and arguments remain unchanged.
- Existing route definitions remain unchanged.
- The modal return type changes internally; no public CLI API depends on it.
- Validation becomes stricter for active states that drift from current workflow.

## Rollback

- Revert `validate.py` route-drift check if it blocks legitimate workflow migration.
- Revert TUI modal return type and dashboard creation path if Textual integration breaks.
- Remove package-data config if packaging backend behavior conflicts, though this is unlikely.

## Rejected Alternatives

- Full gate engine redesign: broader than needed for this run.
- Full mojibake restoration across all documentation/templates: valuable, but too large and hard to verify safely in the current medium-risk scope.
- Running dependency installation automatically: not required for design and may need network access.

## Failure Premortem

| Failure mode | Cause | Prevention | Detection | Rollback |
| --- | --- | --- | --- | --- |
| Valid historical run is reported invalid | Workflow route changed after run creation | Limit check to active `state.json` validation and use clear error text | Drift test and manual validation output | Remove or soften drift check |
| TUI new run crashes | Modal callback receives unexpected payload shape | Use a dataclass/NamedTuple-like payload and tests | Focused widget/dashboard tests | Revert callback handling |
| Package build still misses data | setuptools glob pattern wrong | Use recursive package-data patterns | Package metadata review or wheel smoke test | Adjust pyproject package-data |
| Tests pass but behavior wrong | Tests inspect implementation instead of behavior | Test observable report errors and modal payload | Focused pytest | Add stronger behavioral assertions |
