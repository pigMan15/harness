# 验收报告

## 范围

- 提交 `bridle init` 初始化校验修复。
- 发布 Bridle `v0.1.2` 补丁版本。
- 打包 Windows CLI 并上传到 GitHub Release。

## 变更

- 修复提交：`a17233b fix: allow initial unknown harness state validation`
- 发布提交：`0a465d9 chore: release bridle v0.1.2`
- 发布 tag：`v0.1.2`
- Release 地址：https://github.com/pigMan15/harness/releases/tag/v0.1.2
- CLI 下载地址：https://github.com/pigMan15/harness/releases/download/v0.1.2/bridle-v0.1.2.exe

## 验证

- `python -m pytest tests -q` 通过，结果为 `81 passed`。
- `python -m compileall src tests -q` 通过。
- `python -m harness_cli.cli validate --json` 通过，`passed=true`。
- 源码版 `bridle init --force` 在临时空目录通过。
- PyInstaller 打包通过。
- `bridle-v0.1.2.exe --version` 通过，输出 `bridle v0.1.2`。
- `bridle-v0.1.2.exe validate --json` 通过，`passed=true`。
- `bridle-v0.1.2.exe status --json` 通过。
- 二进制版 `bridle init --force` 在临时空目录通过。
- `main` 和 tag `v0.1.2` 已推送。
- GitHub Release 创建和资产上传通过。

## 门禁

- `G1_REQUIREMENTS`：`NOT_REQUIRED`
- `G2_DESIGN`：`PASS`
- `G3_COMPILE`：`NOT_REQUIRED`
- `G4_UNIT_TEST`：`NOT_REQUIRED`
- `G5_ATDD`：`NOT_REQUIRED`
- `G6_EVIDENCE`：`PASS`
- `G7_PRERELEASE`：`PASS`
- `G8_ACCEPTANCE`：`PASS`

## 剩余风险

- 未在另一台干净 Windows 主机下载 Release 资产后执行。
- Git 推送依赖本机用户代理 `127.0.0.1:7897`，未写入全局配置。

## 结论

`v0.1.2` 补丁版本已完成发布，可以替换 `v0.1.1` 使用。
