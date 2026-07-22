# Implementation Plan

## Goal

Implement focused quality improvements for validation correctness, TUI run creation, packaging data, and regression tests.

## Assumptions

- The run remains `FEATURE/MEDIUM`.
- Dependencies may be unavailable in the current shell; failed verification must be recorded rather than treated as success.
- Full documentation mojibake repair is outside this run unless needed for touched files.

## Task List

1. Add route drift validation.
   - Files: `harness_cli/src/harness_cli/core/validate.py`, `harness_cli/tests/test_validate.py`
   - Test: focused pytest for validator drift detection.

2. Fix TUI new-run payload.
   - Files: `harness_cli/src/harness_cli/ui/widgets/new_run_modal.py`, `harness_cli/src/harness_cli/ui/dashboard.py`
   - Test: focused unit test for `NewRunRequest`/modal payload helper and dashboard creation helper if extracted.

3. Add package data metadata.
   - File: `harness_cli/pyproject.toml`
   - Test: static assertion in tests or metadata review that `templates` and `locales` are declared.

4. Strengthen weak tests.
   - Files: `harness_cli/tests/test_validate.py` and any new focused test file.
   - Test: replace tautological assertions with specific warning/error expectations.

5. Run verification.
   - Commands:
     - `python -m pytest tests/test_validate.py tests/test_workflow.py -q`
     - Add TUI-focused test file to command if created.
   - Record outcomes in `12-compile.md`, `13-unit-test.md`, and `15-evidence.json`.

## Verification Plan

- First run focused tests after adding test cases to confirm whether failures are meaningful.
- Implement minimal source changes.
- Run focused tests again.
- If dependencies are unavailable, record command, exit code, and missing dependency as WAIVED/BLOCKED according to verifier result.

## Rollback Plan

- Revert `validate.py` drift check and related tests if it is too strict for current migration needs.
- Revert modal payload changes if Textual callback compatibility breaks.
- Remove package-data section if setuptools rejects it.

## TDD Record

- New or selected tests:
  - Validator route drift test.
  - Strict-mode warning promotion test.
  - TUI new-run payload test.
  - Package-data metadata test.
- Initial failure:
  - To be recorded during verifier/development after tests are run.
- Implementation:
  - Pending development node.
- Focused result:
  - Pending verifier node.
- Expanded result:
  - Pending verifier node.
