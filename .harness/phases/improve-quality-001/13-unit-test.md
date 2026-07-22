# 单元测试结果

## 依赖准备

- 命令：`C:\Users\15330\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -e .[dev]`
- 工作目录：`G:\Project\ai\harness\harness_cli`
- 退出码：0
- 结果：PASS
- 关键输出：成功安装 `bridle-cli` editable 包及 `pytest`、`textual`、`typer`、`jsonschema` 等 dev/runtime 依赖。

## 首次聚焦测试

- 命令：`python -m pytest tests\test_validate.py tests\test_tui_new_run.py -q`
- 工作目录：`G:\Project\ai\harness\harness_cli`
- 退出码：1
- 结果：FAIL
- 关键输出：`No module named pytest`。
- 后续动作：安装 dev 依赖后重跑。

## 聚焦测试

- 命令：`python -m pytest tests\test_validate.py tests\test_tui_new_run.py -q`
- 工作目录：`G:\Project\ai\harness\harness_cli`
- 退出码：0
- 结果：PASS
- 关键输出：`8 passed in 0.97s`。

## 全量测试

- 命令：`python -m pytest tests -q`
- 工作目录：`G:\Project\ai\harness\harness_cli`
- 退出码：0
- 结果：PASS
- 关键输出：`79 passed in 4.67s`。
