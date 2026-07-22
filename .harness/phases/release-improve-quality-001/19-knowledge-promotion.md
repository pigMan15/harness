# 知识沉淀草稿

## 来源

- RunId: `release-improve-quality-001`
- Intent: `DEPLOYMENT`
- Risk: `MEDIUM`
- Phase dir: `.harness/phases/release-improve-quality-001`
- 原始 PRD / context-pack: 本次为发布流程，无独立 PRD；主要输入来自 release run 的 intake、pre-mortem、预发布部署、接口测试和证据文件。

## 候选知识

| 类型 | 标题 | 相对 PRD 的新增点 | 证据 | 建议位置 |
| --- | --- | --- | --- | --- |
| pitfall | PowerShell 上传 URL 需要使用 `${uploadUrl}` 拼接查询参数 | 发布过程中发现 `"$uploadUrl?name=..."` 会被解析成错误变量名，导致 Release 资产上传失败 | `17-interface-test.md` 记录了失败和修正；最终上传命令成功返回资产大小与下载地址 | `.harness/knowledge/release-pitfalls.md` |
| pattern | 无 `gh` 时可用 Git Credential Manager 凭据调用 GitHub REST API | 本机已能 HTTPS push，但无 `gh` 和环境 token；使用 `git credential fill` 仅在内存中获取凭据完成 Release 创建和资产上传 | `15-evidence.json` 记录 Release 创建与资产上传成功 | `.harness/knowledge/release-patterns.md` |
| rule | 发布证据提交不应移动发布 tag | Release tag 应指向发布源码提交；发布后补齐 harness 证据可作为后续 main 提交保留审计记录 | `16-prerelease-deployment.md` 和 `18-acceptance-report.md` 记录 tag、commit 与证据关系 | `.harness/rules/deployment.md` |

## 不建议沉淀的内容

- 一次性命令的完整输出：只对本次 run 有审计价值，已保存在 `15-evidence.json`。
- GitHub API rate limit 的匿名查询失败：属于当前网络环境偶发现象，不足以形成稳定规则。
- 发布说明逐条内容：属于本版本 Release notes，不是长期工程知识。

## 待用户确认

- 是否将“无 `gh` 时复用 Git Credential Manager 调 GitHub API”的模式提升为正式发布规则。
- 是否要求后续发布必须在干净 Windows 环境下载 Release 资产后再标记验收完成。
