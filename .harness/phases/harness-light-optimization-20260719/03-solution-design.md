# Harness 轻量优化设计

## 目标

在不增加目录、流程节点和脚本数量的前提下，让 workflow 的路由规则、失败恢复和结构校验形成一致且可验证的闭环。

## 方案选择

采用“保持结构，只优化行为”的方案。

未采用以下方案：

- 轻度重组目录：需要修改较多文件引用，收益有限。
- 拆分 Core 与 Extensions：更适合后续团队化发布，当前改造范围过大。

## 设计一：统一路由与硬规则

保留按 `intent + risk` 选择最小路径的机制。将“所有业务代码变更必须预发部署和接口测试”的笼统硬规则收窄为高风险或部署类任务要求，避免它与 `FEATURE / LOW、MEDIUM` 及 `prd-quick-feature` 冲突。

基础代码变更仍必须执行：

- 编译或等价静态检查。
- 聚焦单元测试，无法执行时记录豁免或阻塞。
- 证据采集。

预发部署和接口测试只由明确包含这些节点的路由强制要求。

## 设计二：确定性失败恢复

在 `workflow.yaml` 中增加门禁失败到流程节点的映射：

| 失败门禁 | 回退节点 |
| --- | --- |
| G1_REQUIREMENTS | REQUIREMENT_REVIEW |
| G2_DESIGN | SOLUTION_DESIGN |
| G3_COMPILE | DEVELOPMENT |
| G4_UNIT_TEST | DEVELOPMENT |
| G5_ATDD | DEVELOPMENT |
| G6_EVIDENCE | EVIDENCE_CAPTURE |
| G7_PRERELEASE | PRERELEASE_DEPLOYMENT |
| G8_ACCEPTANCE | ACCEPTANCE_REPORT |

默认最大自动重试次数设为 2。达到上限后状态改为 `BLOCKED`，记录失败原因并等待用户处理，防止反复修复和验证造成无效循环。

同步更新门禁运行手册，使文字规则与 workflow 保持一致。

## 设计三：增强现有校验入口

不新增脚本。继续保留 PowerShell、CMD、Shell 三个现有入口，并检查以下内容：

1. 必需文件存在。
2. `state.json` 是有效 JSON，且包含关键字段。
3. `phase_dir` 存在并位于 `.harness/phases/` 下。
4. workflow 路由引用的节点均已定义。
5. workflow 节点引用的角色文件均存在。
6. workflow 引用的门禁均在 `gates.yaml` 中定义。
7. 当前 state 的 `required_nodes` 和 `completed_nodes` 只引用有效节点。
8. `completed_nodes` 对应的必需产物存在。

CMD 继续作为 PowerShell 入口包装，避免维护第四套校验逻辑。PowerShell 和 Shell 实现相同的校验语义。

## 错误处理

- 校验发现问题时输出具体文件或节点名称并返回非零退出码。
- 不自动删除、移动或修复用户文件。
- 不因项目中存在 `docs/superpowers` 而失败。
- YAML 校验优先使用当前环境已有能力；不为模板增加新的第三方依赖。

## 验证方式

- 分别运行 PowerShell、CMD、Shell 校验入口；当前环境不能执行的入口明确记录限制。
- 构造最小临时副本验证无效节点、缺失角色、未知门禁和非法 `phase_dir` 能被阻止。
- 确认正常模板仍能通过校验。
- 检查三个入口不会修改项目源码或删除文件。

## 风险与控制

- 纯文本解析 YAML 可能存在边界限制：校验仅针对模板当前稳定结构，不尝试实现通用 YAML 解析器。
- 三个平台实现可能逐渐不一致：在文档中明确 PowerShell 和 Shell 的同一检查清单，CMD 只包装 PowerShell。
- 更严格的校验可能暴露现有状态问题：错误信息必须指出修复位置，不自动改写状态。

## 非目标

- 不重组现有目录。
- 不新增项目上下文文件。
- 不引入依赖安装。
- 不实现自动 Git 回滚。
- 不将所有任务强制升级为完整测试或部署流程。
