# Development Record

## Changed Files

- `harness_cli/src/harness_cli/core/validate.py`
  - Rewrote the validator module into clean ASCII text to remove mojibake from active code.
  - Added active state route-drift validation via `_check_required_nodes_route`.
  - Preserved existing required-file, schema, workflow, phase path, gate definition, and artifact checks.
- `harness_cli/src/harness_cli/ui/widgets/new_run_modal.py`
  - Added `NewRunRequest` payload with `run_id`, `intent`, and `risk`.
  - Included `NA` as a TUI risk option.
  - Changed create action to dismiss with the full request payload.
- `harness_cli/src/harness_cli/ui/dashboard.py`
  - Added `create_state_for_new_run()` helper.
  - Updated new-run callback to use selected intent/risk instead of hard-coded `FEATURE/MEDIUM`.
- `harness_cli/pyproject.toml`
  - Replaced mojibake in package description with ASCII text.
  - Added setuptools package-data entries for `locales/*.json` and `templates/**/*`.
- `harness_cli/tests/conftest.py`
  - Made the fixture write the minimal workflow/gates/schema explicitly after copying templates.
- `harness_cli/tests/test_validate.py`
  - Replaced tautological strict-mode assertion with a warning-promotion check.
  - Added route-drift validation test.
  - Added package-data static test.
- `harness_cli/tests/test_tui_new_run.py`
  - Added focused test that selected TUI intent/risk drive new run state.

## Coding Notes

- The implementation keeps module boundaries unchanged.
- The validator drift check is limited to the active `state.json` validation path.
- The TUI helper is intentionally small so behavior can be tested without launching a full Textual app.

## Comments

- Added one short comment in `validate.py` explaining why active state must align with the workflow route.
- Added concise docstrings for `NewRunRequest` and `create_state_for_new_run`.

## Local Developer Precheck

- Command: `python -m py_compile` using bundled Codex Python.
- Files: changed source and test Python files.
- Result: exit code 0.

## Handoff

Implementation is complete. Route to verifier for compile and unit-test gates.
