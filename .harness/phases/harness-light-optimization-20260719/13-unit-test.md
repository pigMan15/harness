# 聚焦验证结果

- 结果：`PASS`
- 测试对象：PowerShell 校验器和 Shell 内嵌 Python 校验核心

## 负向场景

| 场景 | PowerShell | Shell Python 核心 |
| --- | --- | --- |
| workflow 引用未知节点 | 按预期退出 1 | 按预期退出 1 |
| node 引用缺失角色 | 按预期退出 1 | 按预期退出 1 |
| node 引用未知门禁 | 按预期退出 1 | 按预期退出 1 |
| `phase_dir` 路径越界 | 按预期退出 1 | 按预期退出 1 |

汇总：

- `PS_NEGATIVE=4/4`
- `SHELL_PY_NEGATIVE=4/4`

所有测试均在 `%TEMP%` 下的固定测试目录执行；删除前验证目标位于系统临时目录内，没有删除工作区文件。
