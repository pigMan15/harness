# Command: harness-audit

目的：检查这套 harness 模板结构是否健康。

## 人工审计

1. 确认存在入口文件：`AGENTS.md` 或 `CLAUDE.md`。
2. 确认存在状态和 workflow。
3. 确认 workflow 引用的 agent 都存在。
4. 确认 workflow 引用的 gate 都存在。
5. 确认 agent 引用的 rule 都存在。
6. 确认 `state.phase_dir/` 存在。

## 自动审计

运行：

```powershell
./.harness/scripts/validate-harness.ps1
```

Windows 命令提示符:

```cmd
.\.harness\scripts\validate-harness.cmd
```

Linux/macOS/Git Bash:

```sh
./.harness/scripts/validate-harness.sh
```

