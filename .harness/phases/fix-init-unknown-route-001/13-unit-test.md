# 单元测试

- 命令：`python -m pytest tests/test_validate.py -q`
- 工作目录：`G:\Project\ai\harness\harness_cli`
- 退出码：0
- 结果：PASS
- 关键输出：`9 passed, 1 warning in 0.83s`

- 命令：`python -m pytest tests -q`
- 工作目录：`G:\Project\ai\harness\harness_cli`
- 退出码：0
- 结果：PASS
- 关键输出：`81 passed, 1 warning in 4.97s`

- 警告说明：pytest cache 写入 `.pytest_cache` 时出现权限警告，不影响测试断言和退出码。
