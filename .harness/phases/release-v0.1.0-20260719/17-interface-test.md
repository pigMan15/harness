# 接口测试 — bridle.exe v0.1.0

- **测试目标**：验证 PyInstaller 打包的 bridle.exe 二进制功能完整
- **二进制**：`harness_cli/dist/bridle.exe` (15MB, built 2026-07-19)
- **环境**：Windows 11 Pro, Python 3.13.6 (via PyInstaller bundle)

## 场景与结果

| # | 命令 | 预期 | 结果 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | `bridle --version` | 显示版本号和依赖信息 | `bridle v0.1.0 (harness schema: 1.0)` | PASS |
| 2 | `bridle status --json` | 输出合法 JSON，含 run_id/progress/gates | 完整 JSON，run_id=release-v0.1.0-20260719 | PASS |
| 3 | `bridle gates --json` | 输出 8 道门禁状态 | 8 gates，含 description/status/reason | PASS |
| 4 | `bridle list` | 列出所有历史 runs | 3 runs: local-initial, harness-tui-*, harness-light-o* | PASS |
| 5 | `bridle validate` | 结构校验通过 | "Harness validation passed" | PASS |

## 失败

无。

## 剩余风险

- TUI 模式 (`bridle` 无参数) 未在自动化中测试（需要交互式终端）
- `bridle new` / `bridle init` / `bridle save` 等写入命令未测试（避免污染当前 run）
- 跨平台兼容性未测试（仅 Windows）
