# 预发部署 — v0.1.0 GitHub Release

- **环境**：Windows 11 Pro (local dev), Python 3.13.6, PyInstaller 6.21.0
- **版本或 commit**：v0.1.0 (commit 7fb14fb)
- **命令**：
  ```bash
  cd harness_cli
  python -m PyInstaller bridle.spec --clean --noconfirm
  ```
- **结果**：构建成功，退出码 0
- **产物**：
  - `dist/bridle.exe` — 15MB 单文件（稳定命名，适合 PATH）
  - `dist/bridle-v0.1.0.exe` — 15MB 版本化文件（GitHub Release 用）
- **验证**：
  - `bridle.exe --version` → `bridle v0.1.0 (harness schema: 1.0)` ✓
  - `bridle.exe status` → 正确显示当前 run 状态 ✓
  - `bridle.exe validate` → 结构校验正常执行 ✓
- **回滚**：无需回滚（非生产部署，仅构建二进制）
- **冒烟/接口测试**：见 INTERFACE_TEST 节点
- **证据链接**：
  - 构建日志完整，无错误
  - PyInstaller warnings: `build/bridle/warn-bridle.txt`
