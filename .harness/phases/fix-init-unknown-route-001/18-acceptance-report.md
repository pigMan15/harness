# 验收报告

## 范围

- 修复 `bridle init` 在新项目初始化后把模板占位状态 `UNKNOWN/UNKNOWN` 误判为 workflow route 缺失的问题。
- 保留 active state 与 workflow route 的漂移校验能力。

## 变更

- `Validator._check_required_nodes_route()` 现在允许 `intent=UNKNOWN`、`risk=UNKNOWN`、`required_nodes=[]` 的初始空闲状态。
- 新增测试覆盖初始化占位状态通过校验。
- 新增测试覆盖非初始化未知组合仍然报错。

## 验证

- `python -m pytest tests/test_validate.py -q` 通过：`9 passed`。
- `python -m pytest tests -q` 通过：`81 passed`。
- `python -m compileall src tests -q` 通过。
- 临时空目录执行 `python -m harness_cli.cli --lang zh init --force` 后，最终校验通过。
- 仓库根目录执行 `python -m harness_cli.cli validate --json` 通过。

## 剩余风险

- 当前修复还未打包成新的 exe；用户已下载的 `v0.1.1` 二进制需要补丁发布后才能获得修复。
- 本次没有修改模板 schema 的 `next_role` 差异，避免扩大修复范围。

## 结论

本次初始化校验误报已在源码中修复，满足验收条件。
