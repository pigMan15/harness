# 知识沉淀草稿

## 来源

- RunId: `fix-init-unknown-route-001`
- Intent: `BUG_FIX`
- Risk: `LOW`
- Phase dir: `.harness/phases/fix-init-unknown-route-001`

## 候选知识

| 类型 | 标题 | 相对 PRD 的新增点 | 证据 | 建议位置 |
| --- | --- | --- | --- | --- |
| pitfall | active state route drift 校验要排除 init 占位状态 | `UNKNOWN/UNKNOWN` 是 `bridle init` 后、`bridle new` 前的合法空闲占位，不能按缺失 route 处理 | `15-evidence.json` 记录了真实 init 冒烟测试通过 | `.harness/knowledge/release-pitfalls.md` |

## 不建议沉淀的内容

- 临时目录路径和具体 GUID：只对本次验证有意义。
- pytest cache 权限警告：不影响测试结果，也不是本次问题根因。

## 待用户确认

- 是否将该修复打包发布为 `v0.1.2`。
