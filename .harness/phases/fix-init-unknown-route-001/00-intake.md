# Intake

- 问题：用户在新目录执行 `bridle init` 后，初始化创建成功，但最终校验报错 `No workflow route for UNKNOWN/UNKNOWN [.harness/workflow.yaml]`。
- 影响：新项目刚初始化、尚未执行 `bridle new` 时，模板 state 使用 `UNKNOWN/UNKNOWN` 占位，这应是合法初始状态；当前校验把它误判为 route 错误。
- 范围：修复 active state route 校验逻辑，让 `UNKNOWN/UNKNOWN` 初始占位跳过 route drift 检查；其它无路由的真实 intent/risk 组合继续报错。
- 验收：
  - 初始化模板 state 可通过 `Validator.validate()`。
  - 真实无 route 组合仍会报告 `No workflow route`。
  - 现有 validate 相关测试通过。
