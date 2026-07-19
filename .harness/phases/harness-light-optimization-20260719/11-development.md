# 开发记录

## 修改范围

- `.harness/workflow.yaml`：收窄部署硬规则，增加门禁失败回退映射和每门禁两次自动重试上限。
- `.harness/state.schema.json`：增加可选 `retry_counts` 字段，旧 run 无需迁移。
- `.harness/agents/dispatcher.md`：增加失败回退和超过重试上限后的阻塞规则。
- `.harness/agents/verifier.md`：增加重试次数维护规则。
- `.harness/evals/runbook.md`：增加确定性门禁回退表。
- `.harness/scripts/validate-harness.ps1`：增加路径边界、节点、角色、门禁、状态和已完成产物检查。
- `.harness/scripts/validate-harness.sh`：同步核心检查；没有 Python 3 时明确降级。

`.harness/scripts/validate-harness.cmd` 未修改，继续透传 PowerShell 的输出和退出码。

## 编码思想

- workflow 是流程和恢复策略的唯一事实来源。
- dispatcher 只负责路由，verifier 只负责验证和状态记录。
- 校验器只读，不自动修改、移动或删除工程文件。
- 只解析模板当前稳定的 YAML 结构，不实现通用 YAML 解析器。
- 不增加第三方依赖，不增加脚本或目录。

## 兼容性

- PowerShell 脚本保留 UTF-8 BOM，确保 Windows PowerShell 5 能正确读取中文注释。
- 运行时错误信息使用 ASCII，降低不同终端编码导致的解析风险。
- Shell 完整检查使用 Python 3 标准库；缺失 Python 3 时仅运行基础检查并明确提示降级。

## 剩余限制

当前 Windows 环境的 `bash` 指向未安装发行版的 WSL，无法原生执行 `validate-harness.sh`。Shell 内嵌 Python 核心已单独执行，包装器本身保留跨平台验证风险。
