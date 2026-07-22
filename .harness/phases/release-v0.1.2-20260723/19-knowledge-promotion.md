# 知识沉淀草稿

## 来源

- RunId: `release-v0.1.2-20260723`
- Intent: `DEPLOYMENT`
- Risk: `MEDIUM`
- Phase dir: `.harness/phases/release-v0.1.2-20260723`

## 候选知识

| 类型 | 标题 | 相对 PRD 的新增点 | 证据 | 建议位置 |
| --- | --- | --- | --- | --- |
| pitfall | `bridle init` 后的 `UNKNOWN/UNKNOWN` 是合法占位状态 | route drift 校验不能把 init 后、new 前的空闲状态当作错误 | `15-evidence.json` 记录源码版和二进制版 init 冒烟通过 | `.harness/knowledge/release-pitfalls.md` |
| pitfall | Windows Git 可能不使用系统用户代理 | 本机 PowerShell 可访问 GitHub，但 Git 直连失败；临时通过 `-c http.proxy=http://127.0.0.1:7897` 推送成功 | `15-evidence.json` 记录 Git 代理推送命令 | `.harness/knowledge/release-pitfalls.md` |

## 不建议沉淀的内容

- 临时冒烟目录路径：只对本次验证有审计价值。
- GitHub API 尝试创建的未引用 commit object：没有更新远端 ref，不影响最终发布路径。

## 待用户确认

- 是否将 Git 代理配置作为本机发布环境的固定配置。
