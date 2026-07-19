# 编译与静态检查结果

- 工作目录：`C:\Users\pig\Documents\调研1`
- 结果：`PASS`

## JSON 解析

- 命令：PowerShell `ConvertFrom-Json` 解析 `.harness/state.schema.json` 和 `.harness/state.json`
- 退出结果：成功
- 关键输出：`JSON_PARSE=PASS`

## PowerShell 校验入口

- 命令：`.\.harness\scripts\validate-harness.ps1`
- 退出码：`0`
- 关键输出：`Harness validation passed.`

## CMD 校验入口

- 命令：`.\.harness\scripts\validate-harness.cmd`
- 退出码：`0`
- 关键输出：`Harness validation passed.`

## Shell 校验核心

- 命令：从 `validate-harness.sh` 提取内嵌 Python，使用 Python 3.14 对当前工程执行完整校验
- 退出码：`0`
- 关键输出：`Harness validation passed.`

## Shell 包装器限制

- 命令：`bash --version`
- 退出码：`1`
- 结果：`WAIVED`
- 原因：当前机器的 bash 指向未安装发行版的 WSL，无法原生执行 Shell 包装器。
