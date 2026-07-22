# 接口测试

## 测试目标

验证 `v0.1.2` 打包产物可正常启动、报告正确版本、读取当前 harness 状态、执行结构校验，并确认 `bridle init` 新项目初始化不再误报 `UNKNOWN/UNKNOWN` route 错误。

## 场景

- 场景 1：用户运行 `bridle-v0.1.2.exe --version`，应输出 `bridle v0.1.2`。
- 场景 2：用户在仓库根目录运行 `bridle-v0.1.2.exe validate --json`，应得到 `passed=true`。
- 场景 3：用户在仓库根目录运行 `bridle-v0.1.2.exe status --json`，应能读取当前 release run。
- 场景 4：用户在全新空目录运行 `bridle-v0.1.2.exe --lang zh init --force` 后，再运行 `validate --json`，应通过且不再出现 `UNKNOWN/UNKNOWN` route 错误。

## 命令或请求

- `.\harness_cli\dist\bridle-v0.1.2.exe --version`
- `.\harness_cli\dist\bridle-v0.1.2.exe validate --json`
- `.\harness_cli\dist\bridle-v0.1.2.exe status --json`
- `G:\Project\ai\harness\harness_cli\dist\bridle-v0.1.2.exe --lang zh init --force`
- `G:\Project\ai\harness\harness_cli\dist\bridle-v0.1.2.exe --lang zh validate --json`

## 结果

- `--version` 通过，输出 `bridle v0.1.2`。
- `validate --json` 通过，输出 JSON 中 `passed=true`。
- `status --json` 通过，能够读取当前 `release-v0.1.2-20260723` run。
- 二进制在临时空目录执行 `init --force` 创建 87 个模板文件，随后 `validate --json` 返回 `passed=true`。

## 失败

- 首次使用 `harness_cli\dist\bridle-v0.1.2.exe --version` 时，PowerShell 将相对路径误解析为模块名，命令未启动；使用 `.\harness_cli\dist\bridle-v0.1.2.exe --version` 后通过。该失败不是 CLI 二进制行为失败。

## 剩余风险

- 仅在本机 Windows 环境完成下载前本地冒烟，尚未在另一台干净 Windows 主机下载 Release 资产后执行。
