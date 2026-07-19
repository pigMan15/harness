# 验收报告

## 完成范围

- 修复低中风险功能路径与“业务代码必须部署”硬规则之间的冲突。
- 增加 G1-G8 门禁的确定性回退节点和每门禁两次自动重试上限。
- 增加可选 `retry_counts` 状态，不要求迁移旧 run。
- 增强 PowerShell 和 Shell 现有校验入口，没有新增脚本。
- 保持 CMD 为 PowerShell 包装器，没有调整工程目录结构。

## 验证结论

- PowerShell 校验入口：PASS。
- CMD 校验入口：PASS。
- Shell 内嵌 Python 完整校验核心：PASS。
- 四类错误场景：PowerShell `4/4`、Shell Python 核心 `4/4` 均按预期阻断。
- 原生 Shell 包装器：因当前环境没有可用 Bash，记录 WAIVED。

## 剩余风险

需要在 Linux、macOS、Git Bash 或已配置 WSL 的环境中补跑一次 `validate-harness.sh`，确认 POSIX 包装部分。该限制不影响当前 Windows PowerShell 和 CMD 使用。

## 结论

本次轻量优化达到确认范围，没有新增项目上下文模板、目录、流程节点或脚本入口。
