# Dispatcher Decision

- Intent: FEATURE
- Risk: MEDIUM
- Current node before dispatch: INTAKE
- Next node: INTAKE
- Next role: dispatcher
- Required artifact: 00-intake.md
- Artifact directory: .harness/phases/improve-quality-001
- Reason: The user requested quality improvements for the project and explicitly specified `FEATURE/MEDIUM` via `bridle new improve-quality-001 --intent FEATURE --risk MEDIUM`. The bridle executable and plain Python command were unavailable in the current environment, so the run was initialized with the same state semantics.

## Scope Captured

Improve the project based on the read-only audit:

- Restore broken UTF-8/mojibake text where it affects package metadata, user-facing docs, locale JSON, and importable Python source.
- Add validation for drift between `state.required_nodes` and `workflow.route(intent, risk)`.
- Make TUI new-run intent/risk selections actually drive the created run.
- Strengthen weak tests and add coverage for the new validation and TUI behavior.
- Add package data configuration so templates/locales are present in installed wheels.

## Constraints

- Preserve the user-selected intent/risk.
- Do not skip required workflow nodes.
- Keep all phase artifacts in `.harness/phases/improve-quality-001`.
- G3-G8 gates must be marked only during verifier nodes.
