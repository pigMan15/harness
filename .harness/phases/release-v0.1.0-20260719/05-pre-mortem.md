# 失败预演 — v0.1.0 GitHub Release

| 失败模式 | 原因 | 预防 | 发现 | 回滚 |
| --- | --- | --- | --- | --- |
| PyInstaller 构建失败 | 依赖缺失或 spec 配置错误 | 先运行 `pip install pyinstaller`，确认 bridle.spec 有效 | 构建命令返回非零退出码 | 修复依赖/spec 后重试 |
| 二进制无法启动 | 隐藏导入遗漏或 DLL 缺失 | 构建后立即执行 `bridle.exe --version` | 命令报错或崩溃 | 检查 hiddenimports，重新构建 |
| gh CLI 未安装 | 开发环境未安装 GitHub CLI | 检查 `gh --version`，若无则改用 Git + 手动上传 | Release 创建步骤失败 | 手动在 GitHub Web 创建 Release 并上传 |
| 上传网络失败 | 网络不稳定或 GitHub API 限流 | 重试机制，小文件优先 | curl/gh 返回网络错误 | 重试上传 |
| 版本号不一致 | tag/spec/pyproject.toml 版本不同步 | 构建前统一检查版本 | Release 描述与实际二进制版本不匹配 | 统一版本号后重新走流程 |
| dist 目录残留旧产物 | 上次构建的旧文件干扰 | 构建前 `make clean` 或手动删除 dist/ | 文件时间戳异常或大小不对 | 清理后重新构建 |

## 测试策略

- 构建后执行 `dist/bridle.exe --version` 验证二进制可运行
- 执行 `dist/bridle.exe status` 验证核心功能
- 执行 `dist/bridle.exe validate` 验证结构校验
- 检查文件大小合理（~15MB）

## 门禁预期

| 门禁 | 预期 | 说明 |
| --- | --- | --- |
| G7_PRERELEASE | PASS | 构建成功 + 二进制可运行 |
| G6_EVIDENCE | PASS | 证据文件记录所有命令和结果 |
| G8_ACCEPTANCE | PASS | 验收报告总结发布结果 |

## 回滚预期

- 如果 Release 创建失败：删除 draft release，修复问题后重试
- 如果二进制有问题：删除 Release assets，重新上传正确版本
- 最坏情况：删除 GitHub Release + tag，修复后重新发布

## 停止条件

- PyInstaller 构建连续失败 2 次
- 二进制验证连续失败 2 次
- GitHub Release 创建连续失败 2 次
- 任何不可恢复的环境问题（如 Python 环境损坏）
