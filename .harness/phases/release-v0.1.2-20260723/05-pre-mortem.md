# Pre-Mortem

## 失败模式

- 版本号只更新 `pyproject.toml`，未同步 `__version__`，导致二进制输出旧版本。
- 发布 tag 指向错误提交，导致 Release 源码不包含 init 修复。
- PyInstaller 打包成功但缺少模板或 locales，导致新目录初始化仍失败。
- GitHub Release 资产未上传或上传旧文件。
- 将未跟踪的 `presentations/` 目录误提交进发布提交。

## 测试策略

- 运行 `python -m pytest tests -q` 覆盖全部单元测试。
- 运行 `python -m harness_cli.cli validate --json` 校验当前仓库 harness。
- 在临时空目录执行 `python -m harness_cli.cli --lang zh init --force` 和 `validate --json` 做真实初始化冒烟。
- 打包后执行 `bridle-v0.1.2.exe --version`、`validate --json` 和临时空目录 init 冒烟。

## 门禁预期

- `G6_EVIDENCE`：发布证据完整后标记为 `PASS`。
- `G7_PRERELEASE`：本地构建、远端 push、Release 创建和 CLI 冒烟完成后标记为 `PASS`。
- `G8_ACCEPTANCE`：验收报告完成后标记为 `PASS`。
- `G1/G3/G4/G5` 对当前 deployment run 不直接要求，但构建与测试结果仍作为发布证据记录。

## 回滚预期

- 推送前：可追加修复提交或删除本地 tag。
- 推送 tag 后：可删除远端 tag `v0.1.2` 并重新发布。
- Release 创建后：可删除 Release 或发布 `v0.1.3` 修复版本。

## 停止条件

- 单元测试失败。
- 打包失败。
- 打包后 CLI 版本不是 `v0.1.2`。
- 真实 init 冒烟仍出现 `UNKNOWN/UNKNOWN` route 错误。
- GitHub Release 无法创建或资产无法上传。
