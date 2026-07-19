# 编码设计确认

## 推荐编码思想

采用“配置为事实来源、校验器只读验证、失败关闭”的实现风格：

- `workflow.yaml` 描述路由和恢复策略，不把规则散落到脚本。
- dispatcher 负责路由，verifier 负责记录验证结果，保持角色边界。
- 校验器只读取文件并返回退出码，不自动修复、移动或删除内容。
- 使用小型提取函数解析模板的稳定 YAML 结构，不手写通用 YAML 解析器。
- 不引入第三方依赖，不新增脚本。

## 模块边界

- 流程语义：`.harness/workflow.yaml`
- 状态契约：`.harness/state.schema.json`
- 执行角色：`.harness/agents/dispatcher.md`、`.harness/agents/verifier.md`
- 操作说明：`.harness/evals/runbook.md`
- 确定性检查：`.harness/scripts/validate-harness.ps1`、`.harness/scripts/validate-harness.sh`
- CMD 入口：保持现状，只透传 PowerShell 退出码

## 兼容策略

- `retry_counts` 是可选字段，旧 run 不需要迁移。
- 不要求删除项目已有的 `docs/superpowers`。
- 保留当前命令和目录名称，已有使用方式不变。
- Shell 缺少 Python 3 时明确降级为基础校验。

## 中文注释策略

脚本中的复杂解析和路径边界判断添加必要中文注释；简单赋值和显而易见的循环不增加注释，避免注释噪声。

## 需要确认

确认按以上模块边界实施，并在当前会话内逐项执行和验证。
