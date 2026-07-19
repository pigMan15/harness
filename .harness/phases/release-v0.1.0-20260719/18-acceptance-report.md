# 验收报告 — v0.1.0 GitHub Release

## 范围

- 构建 `bridle.exe` 单文件二进制（PyInstaller）
- 创建版本化副本 `bridle-v0.1.0.exe`
- 接口测试验证二进制功能完整
- 准备 GitHub Release 发布

## 变更

| 文件 | 说明 |
| --- | --- |
| `harness_cli/dist/bridle.exe` | 重新构建的 15MB 单文件二进制 |
| `harness_cli/dist/bridle-v0.1.0.exe` | 版本化副本，用于 GitHub Release 上传 |

无源码变更。

## 验证总结

| 门禁 | 状态 | 说明 |
| --- | --- | --- |
| G1-G5 | NOT_REQUIRED | DEPLOYMENT/MEDIUM 路由不要求 |
| G6_EVIDENCE | PASS | 15-evidence.json 完整，含命令/结果/豁免/风险 |
| G7_PRERELEASE | PASS | 构建成功 + 5 项接口测试全部通过 |
| G8_ACCEPTANCE | PASS | 本报告总结所有验证结果 |

### 接口测试结果（5/5 PASS）

1. `--version` → v0.1.0 ✓
2. `status --json` → 合法 JSON ✓
3. `gates --json` → 8 道门禁 ✓
4. `list` → 历史 runs ✓
5. `validate` → 结构校验通过 ✓

## 剩余风险

1. **gh CLI 未安装** — 无法从命令行创建 GitHub Release，需通过 GitHub Web UI 手动上传 `bridle-v0.1.0.exe`，或安装 gh CLI 后执行：
   ```bash
   gh release create v0.1.0 --title "Bridle v0.1.0" --notes "AI Coding Harness CLI & TUI 首个发布版本" harness_cli/dist/bridle-v0.1.0.exe
   ```
2. TUI 模式仅手动验证
3. 仅 Windows 构建，无 macOS/Linux 交叉编译

## 发布步骤（待执行）

由于 `gh` CLI 不可用，建议：
1. 打开 https://github.com/<org>/<repo>/releases/new?tag=v0.1.0
2. Title: `Bridle v0.1.0 — AI Coding Harness CLI`
3. 上传 `harness_cli/dist/bridle-v0.1.0.exe`
4. 发布 Release
