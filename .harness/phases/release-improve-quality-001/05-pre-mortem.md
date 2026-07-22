# 发布失败预演

| 失败模式 | 原因 | 预防 | 发现 | 回滚 |
| --- | --- | --- | --- | --- |
| 重复发布旧版本 | 本地已有 `v0.1.0`，源码仍显示 `0.1.0` | 发布前更新 `pyproject.toml` 和 `__version__` 到 `0.1.1` | `bridle --version` 冒烟测试 | 删除未推送 tag，恢复版本号 |
| PyInstaller 构建失败 | hidden import 或资源数据遗漏 | 使用现有 `bridle.spec`，构建后执行二进制冒烟 | PyInstaller 退出码非 0 或二进制启动失败 | 修复 spec 或回退提交 |
| Git push 失败 | 网络或认证不可用 | 推送前确认 remote，失败记录 BLOCKED | git push 退出码非 0 | 保留本地 tag/commit，待认证后重推 |
| GitHub Release 创建失败 | 缺少 `gh` 或 GitHub token | 检查 `gh`/token，可用则用 API 上传资产 | API/curl 退出码或 HTTP 状态失败 | 已推 tag 可手动创建 release |
| 发布资产不可用 | 上传失败或文件名错误 | 使用 `bridle-v0.1.1.exe` 固定资产名 | GitHub Release 页面/API 检查 | 重新上传资产或删除 draft release |

## 目标环境

- Git branch: `main`
- Remote: `origin` (`https://github.com/pigMan15/harness.git`)
- Release tag: `v0.1.1`
- Asset: `harness_cli/dist/bridle-v0.1.1.exe`

## 回滚路径

- 若未推送：重置/修改本地提交和 tag。
- 若已推送 tag 但未发布：删除远端 tag `v0.1.1`。
- 若已创建 GitHub Release：删除 release 或发布修复版 `v0.1.2`。
