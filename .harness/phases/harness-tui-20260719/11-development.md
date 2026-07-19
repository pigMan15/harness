# 开发记录

## 代码统计

| 层 | 文件数 | 说明 |
|---|---|---|
| 项目骨架 | 8 | pyproject.toml + __init__.py x 6 + constants.py |
| core/ | 4 | state.py, workflow.py, gates.py, validate.py |
| commands/ | 9 | main.py + 8 个命令行子命令 |
| ui/ | 8 | console.py + dashboard.py + 5 widgets + app.py |
| templates/ | 1 (目录) | 内置 .harness/ 模板副本 (94 files) |
| tests/ | 6 | conftest.py + test_state/workflow/gates/validate/init.py |
| 构建 | 2 | bridle.spec (PyInstaller) + Makefile |
| **合计** | **38** | Python 源文件 + 构建配置 |

## 关键实现决策

1. **HarnessState.create_new()** — 工厂方法，不写磁盘，便于测试
2. **Validator 子校验拆分** — 每个 `_check_*` 方法独立，方便单独调用
3. **GateEvaluator.evaluate() 幂等** — 产物缺失时将已标记的 PASS 降级为 FAIL
4. **init_cmd 幂等** — 检测 `<!-- HARNESS-ENTRY:START -->` 标记，避免重复追加
5. **TUI 数据流** — `refresh_data()` → 各 `update_*()` 方法，单向数据流
6. **--json 标志** — status/gates/validate/list 四命令支持机器可读输出，CI 集成
7. **ASCII 安全输出** — 所有终端输出使用纯 ASCII 字符，避免 Windows GBK 编码错误

## 验证结果

### CLI 命令测试

```
bridle --version     ✅
bridle status        ✅ Panel + progress + nodes + gates
bridle status --json ✅ 合法 JSON
bridle validate      ✅ 通过，exit 0
bridle gates         ✅ 表格渲染
bridle gates --json  ✅ 合法 JSON
bridle list          ✅ Runs 表格
bridle save          ✅ 快照保存
bridle switch        ✅ Run 恢复
bridle new           ✅ 11 节点路由
bridle init --force  ✅ 94 模板文件 + AGENTS.md/CLAUDE.md
```

### 单元测试

```
54 passed, 0 failed in 3.65s

test_state.py    15 passed   (load/save/create/query/list/switch)
test_workflow.py 14 passed   (load/route/next/query)
test_gates.py    11 passed   (load/evaluate/bulk/health)
test_validate.py  5 passed   (valid/missing/strict/summary)
test_init.py      9 passed   (detect/append/replace/idempotent)
```

## 未实现（v0.2+）

- `harness watch` 文件监控
- TUI Artifact 面板 Markdown 预览
- Schema 迁移引擎
- 版本检查缓存持久化
- TUI Textual 组件测试（需要现代终端，Git Bash 不支持）

## 已知限制

- Windows GBK 终端下中文显示为乱码（gates.yaml 描述），`--json` 输出不受影响
- 模板目录包含开发 run 的历史 phases/ 数据（生产构建前需清理）
- `bridle` 命令不在 PATH 中（需配置 Windows Store Python stub 问题）
