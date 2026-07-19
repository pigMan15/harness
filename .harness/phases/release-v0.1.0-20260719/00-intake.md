# Dispatcher 决策 — INTAKE

- **意图**：DEPLOYMENT（打包发布）
- **风险**：MEDIUM
- **当前节点**：INTAKE
- **下一节点**：PRE_MORTEM
- **下一角色**：quality-guardian
- **必需产物**：05-pre-mortem.md
- **必需规则/上下文**：quality-guardian 角色文件
- **原因**：用户要求打包并发布到 GitHub Release。v0.1.0 tag 已存在，需构建二进制并创建 GitHub Release。按 DEPLOYMENT/MEDIUM 路由：INTAKE → PRE_MORTEM → PRERELEASE_DEPLOYMENT → INTERFACE_TEST → EVIDENCE_CAPTURE → ACCEPTANCE_REPORT。

## 任务摘要

- **目标**：构建 bridle.exe 单文件二进制，创建 GitHub Release v0.1.0 并上传产物
- **当前版本**：v0.1.0（tag 已存在，pyproject.toml version=0.1.0）
- **构建工具**：PyInstaller（bridle.spec）
- **产物**：`harness_cli/dist/bridle.exe`（~15MB 单文件）
- **前置条件**：
  - bridle.spec 已配置 ✓
  - dist/bridle.exe 已存在 ✓
  - 代码已 commit ✓
  - gh CLI 未安装 — 需要通过其他方式创建 Release
