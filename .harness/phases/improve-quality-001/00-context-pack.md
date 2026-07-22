# Context Pack

## Task Source

- RunId: improve-quality-001
- PRD ID: none
- PRD path or wiki page: conversation request, "补充完善"
- Prototype/screenshots: none
- Initiator: user
- Time: 2026-07-22T21:24:00+08:00

## Requirement Summary

The user asked to improve the current project after a read-only audit identified several quality gaps. The project is Bridle, a Python CLI/TUI tool that initializes and manages `.harness/` workflows for AI-assisted coding. The improvement should focus on correctness, workflow integrity, installation reliability, and test strength. The work must preserve the user-selected `FEATURE/MEDIUM` intent/risk and proceed through the configured harness route. Acceptance should be observable through focused tests and recorded evidence.

## Related Domain Knowledge

| Knowledge Point | Summary | Source |
| --- | --- | --- |
| Harness workflow | `.harness/state.json` is the active run; `workflow.yaml` is the route source of truth. | AGENTS.md, .harness/workflow.yaml |
| Gate discipline | G3-G8 are verifier-owned; developer work must not mark them PASS. | AGENTS.md |
| Artifact discipline | All phase artifacts for this run must be written to `.harness/phases/improve-quality-001`. | .harness/rules/artifact-location.md |

## Related Historical Experience

| Type | Conclusion | Source |
| --- | --- | --- |
| pitfall | The previous active run was DONE but its `DEPLOYMENT/MEDIUM` required nodes drifted from the current workflow route by missing `KNOWLEDGE_PROMOTION`. | `.harness/state.json`, `.harness/workflow.yaml` audit |
| pitfall | Mojibake appears in user-facing docs, package metadata, locale JSON, and Python comments/docstrings. Some files may be syntactically invalid. | README.md, pyproject.toml, locales/zh.json, core/gates.py |
| case | TUI new-run modal exposes intent/risk controls but dashboard creation hard-codes `FEATURE/MEDIUM`. | `harness_cli/src/harness_cli/ui/dashboard.py`, `new_run_modal.py` |

## Relevant Code Anchors

- Module: `harness_cli/src/harness_cli/core/validate.py`
- Module: `harness_cli/src/harness_cli/core/workflow.py`
- Module: `harness_cli/src/harness_cli/core/gates.py`
- Module: `harness_cli/src/harness_cli/ui/dashboard.py`
- Module: `harness_cli/src/harness_cli/ui/widgets/new_run_modal.py`
- Configuration: `harness_cli/pyproject.toml`
- Tests: `harness_cli/tests/test_validate.py`, `harness_cli/tests/test_workflow.py`, `harness_cli/tests/test_gates.py`
- Locale/docs: `harness_cli/src/harness_cli/locales/zh.json`, `README.md`, `README_en.md`

## Invariants

- Do not change the run intent/risk chosen by the user.
- Do not bypass required nodes in `FEATURE/MEDIUM`.
- Preserve existing public CLI names and command behavior unless fixing a clear bug.
- Keep source changes scoped to the audited quality gaps.
- Do not mark G3-G8 gates outside verifier nodes.

## Questions To Confirm

- Whether to fully restore all Chinese prose across README/templates or limit this run to files required for package/runtime correctness.
- Whether package publication should target only PyInstaller or also normal wheel/sdist installation.

Working assumption: make focused fixes that improve runtime/install/test correctness and avoid a full documentation rewrite unless the file is directly affected.

## Risk Assessment

- Suggested Intent: FEATURE
- Suggested Risk: MEDIUM
- Risk reason: The changes touch validation behavior, TUI run creation, packaging metadata, and tests. They are not production incident fixes, but regressions could affect new users and workflow correctness.

## Knowledge Sources

- Obsidian: none
- LLM Wiki: none
- Harness run: improve-quality-001
- Code files: listed in relevant code anchors
