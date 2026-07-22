# 接口测试

## 测试目标

验证 Release 产物 `bridle-v0.1.1.exe` 可作为 CLI 正常启动、报告版本、读取当前 harness 状态，并能执行项目结构校验。

## 场景

- 场景 1：用户下载 Windows CLI 后运行 `--version`，应输出当前发布版本。
- 场景 2：用户在仓库根目录运行 `validate --json`，应得到可解析 JSON，且 `passed` 为 `true`。
- 场景 3：用户在仓库根目录运行 `status --json`，应得到可解析 JSON，并能读取当前 run。

## 命令或请求

- `harness_cli\dist\bridle-v0.1.1.exe --version`
- `harness_cli\dist\bridle-v0.1.1.exe validate --json`
- `harness_cli\dist\bridle-v0.1.1.exe status --json`

## 结果

- `--version` 通过，输出 `bridle v0.1.1`。
- `validate --json` 通过，输出 JSON 中 `passed=true`。
- `status --json` 通过，能够读取当前 `release-improve-quality-001` run。
- Release 页面已存在，资产 `bridle-v0.1.1.exe` 上传成功，大小 33,552,543 bytes。

## 失败

无未解释失败。一次 Release API 上传脚本因 PowerShell URL 变量拼接错误未上传资产，随后使用 `${uploadUrl}` 修正并成功上传。

## 剩余风险

- 冒烟测试覆盖本地 Windows 环境，未在干净虚拟机或另一台 Windows 主机重新下载验证。
- GitHub Release 创建依赖当前 Git Credential Manager 凭据，后续自动化发布建议改用专用最小权限 token 或安装并配置 `gh`。
