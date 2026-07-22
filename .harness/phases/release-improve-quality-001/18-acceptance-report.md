# 验收报告

## 范围

- 将 `bridle` CLI 发布为 `v0.1.1`。
- 将本地 `main` 分支合并结果推送到 GitHub 远端。
- 创建 GitHub Release 并上传 Windows CLI 产物。
- 补齐发布 run 的可审计证据。

## 变更

- 已创建提交：`1e88aea926ac2d0802afdcc86b3964eeb05ca881`，消息为 `chore: release bridle v0.1.1`。
- 已创建并推送 tag：`v0.1.1`。
- 已上传资产：`bridle-v0.1.1.exe`。
- Release 地址：https://github.com/pigMan15/harness/releases/tag/v0.1.1
- 下载地址：https://github.com/pigMan15/harness/releases/download/v0.1.1/bridle-v0.1.1.exe

## 验证

- `python -m pytest tests -q` 通过，结果为 `79 passed in 5.92s`。
- `python -m harness_cli.cli validate --json` 通过，`passed=true`。
- `python -m PyInstaller bridle.spec --clean --noconfirm` 通过。
- `bridle-v0.1.1.exe --version` 通过，输出 `bridle v0.1.1`。
- `bridle-v0.1.1.exe validate --json` 通过，`passed=true`。
- `bridle-v0.1.1.exe status --json` 通过，可读取当前 release run。
- `git push origin main` 通过。
- `git push origin v0.1.1` 通过。
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

- 未在干净 Windows 主机重新下载执行 Release 资产。
- 当前发布流程尚未自动化，后续建议引入专用 token 或 `gh` CLI 以减少手工 API 脚本。

## 结论

本次 `v0.1.1` 发布完成，可以对外使用。
