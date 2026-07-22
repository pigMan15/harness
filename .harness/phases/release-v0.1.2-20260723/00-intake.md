# Intake

- 目标：发布 Bridle `v0.1.2` 补丁版本。
- 背景：`v0.1.1` 的 `bridle init` 在新项目初始化后会误报 `No workflow route for UNKNOWN/UNKNOWN`，源码修复已提交为 `a17233b`。
- 范围：
  - 将 CLI 版本号从 `0.1.1` 升级到 `0.1.2`。
  - 运行测试、结构校验和打包。
  - 创建 Git tag `v0.1.2`。
  - 推送 `main` 和 tag。
  - 创建 GitHub Release 并上传 Windows CLI 资产。
- 不包含：
  - 不发布或提交 `presentations/` 目录中的演示 PPT。
  - 不扩大修复范围到模板 schema 差异。
- 验收：
  - 单元测试通过。
  - `bridle init` 真实冒烟通过。
  - PyInstaller 产物可输出 `bridle v0.1.2`。
  - GitHub Release `v0.1.2` 存在并包含 `bridle-v0.1.2.exe`。
