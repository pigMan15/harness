# Development

- 修改文件：
  - `harness_cli/src/harness_cli/core/validate.py`
  - `harness_cli/tests/test_validate.py`
- 变更说明：
  - 在 active state route 校验中识别新项目初始化后的空闲占位状态：`intent=UNKNOWN`、`risk=UNKNOWN`、`required_nodes=[]`。
  - 对该初始状态跳过 workflow route 检查，避免 `bridle init` 完成后误报 `No workflow route for UNKNOWN/UNKNOWN`。
  - 保留其它无 route 组合的错误，例如 `UNKNOWN/LOW` 仍然报错。
- 测试补充：
  - 新增初始化占位状态通过校验的测试。
  - 新增非初始化未知组合仍报错的测试。
- 中文注释：
  - 未新增中文代码注释；仅在英文代码注释中说明模板占位状态，贴合现有源码风格。
