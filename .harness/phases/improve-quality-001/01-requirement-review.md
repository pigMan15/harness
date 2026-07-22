# Requirement Review

## Goal

Improve Bridle's project quality in a focused way so the tool is more reliable for normal installation, harness validation, TUI run creation, and automated regression checks.

## Scope

- Add validation that detects drift between `state.required_nodes` and `workflow.route(state.intent, state.risk)`.
- Fix the TUI new-run flow so selected intent and risk are preserved when creating a run.
- Add package data configuration so `templates/` and `locales/` are included in standard package builds.
- Strengthen weak tests and add focused tests for the new validation and TUI new-run behavior.
- Repair clearly broken user-facing/package strings touched by this work where they affect runtime or packaging.

## Non-Goals

- Do not rewrite every README/template/prose file in this run.
- Do not redesign the entire gate engine beyond the state/workflow drift check.
- Do not add network-dependent release automation.
- Do not change public command names or route definitions except where needed for correctness.

## Acceptance Criteria

- [ ] Drift validation:
  - Verification: a test creates a mismatch between `state.required_nodes` and the workflow route and `Validator.validate()` reports a clear error.
- [ ] TUI intent/risk preservation:
  - Verification: a test proves `NewRunModal` returns run id, intent, and risk, and dashboard run creation uses those values instead of hard-coded `FEATURE/MEDIUM`.
- [ ] Package data:
  - Verification: `pyproject.toml` declares `harness_cli.templates` and `harness_cli.locales` package data or equivalent setuptools configuration.
- [ ] Test suite signal:
  - Verification: existing tautological/weak tests are replaced with assertions that can fail on regression.
- [ ] Local verification:
  - Verification: focused pytest command exits 0, or any inability to run is recorded with cause and waiver.

## Open Questions

- Full documentation mojibake repair is desirable but may be larger than this medium-risk improvement.
- The local environment lacks an installed `bridle` command and Python dependencies; verification may need the bundled Python plus dependency availability or recorded waiver.

## Risk Notes

- Adding strict route drift validation can surface existing historical runs as invalid if workflow routes changed after the run was created. The validation should compare active state to current route and produce a clear message; users may need a documented way to preserve historical snapshots.
- TUI changes touch Textual interaction boundaries, so tests should cover the data contract without requiring a full terminal UI session where possible.
