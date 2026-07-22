# Acceptance Report

## Scope Summary

本次 run 按 `FEATURE/MEDIUM` 完成了聚焦质量改进：

- 为 active `state.json` 增加 `required_nodes` 与 `workflow.route(intent, risk)` 的漂移校验。
- 修复 TUI 新建 run 时忽略用户选择的 intent/risk 的问题。
- 为标准 setuptools 安装声明 `locales` 和 `templates` 包数据。
- 替换无效测试断言，并新增 route drift、package-data、TUI 新建 run 行为测试。
- 将 `validate.py` 和 `pyproject.toml` 中与本次改动相关的 mojibake 影响点改为稳定 ASCII 文本。

## Changed Files

- `harness_cli/src/harness_cli/core/validate.py`
- `harness_cli/src/harness_cli/ui/widgets/new_run_modal.py`
- `harness_cli/src/harness_cli/ui/dashboard.py`
- `harness_cli/pyproject.toml`
- `harness_cli/tests/conftest.py`
- `harness_cli/tests/test_validate.py`
- `harness_cli/tests/test_tui_new_run.py`

## Verification Summary

- 编译静态检查：PASS
  - `python -m py_compile ...`
- 聚焦测试：PASS
  - `8 passed in 0.97s`
- 全量测试：PASS
  - `79 passed in 4.67s`
- Harness 结构校验：PASS
  - `passed=true`

## Gates

- G1_REQUIREMENTS: PASS
- G2_DESIGN: PASS
- G3_COMPILE: PASS
- G4_UNIT_TEST: PASS
- G5_ATDD: NOT_REQUIRED
- G6_EVIDENCE: PASS
- G7_PRERELEASE: NOT_REQUIRED
- G8_ACCEPTANCE: PASS

## Waivers

- G5_ATDD：当前 `FEATURE/MEDIUM` 路由不要求 ATDD，且变更由聚焦测试和全量单元测试覆盖。
- G7_PRERELEASE：当前 `FEATURE/MEDIUM` 路由不要求预发布部署。

## Residual Risks

- 未单独执行 wheel/sdist 构建烟测；本次通过 pyproject 静态测试验证 package-data 配置。
- TUI 行为通过 helper 级单元测试验证，未启动完整 Textual 交互会话。

## Acceptance Decision

通过。实现范围与验收标准一致，相关验证均已记录在 `15-evidence.json`。
