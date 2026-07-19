# 流程产物位置规则

目的：确保需求、设计、计划、开发记录和验证证据都归档到当前 harness run，避免被外部 Skill 或跨仓库任务写散。

## 进入流程前

写任何流程产物前，必须按顺序确认：

1. 读取当前仓库的 `.harness/state.json`。
2. 确定当前 `run_id`。
3. 解析 `phase_dir`。
4. 判断本次要写的是源码还是流程产物。
5. 如果是流程产物，只能写入 `phase_dir` 指向的目录。

## 流程产物范围

以下都属于流程产物，必须写入当前 `phase_dir`：

- 需求评审。
- 上下文包。
- 方案设计。
- 编码设计。
- 实施计划。
- 开发记录。
- 编译、测试、验证记录。
- 证据文件。
- 验收报告。
- 知识沉淀草稿。

## 禁止目录

明确禁止使用以下目录保存流程产物：

```text
docs/superpowers/
docs/superpowers/specs/
```

如果外部 Skill、插件或工具建议把设计文档、计划或证据写入 `docs/superpowers`，必须忽略该默认路径，改写到当前 `state.phase_dir`。

## Skill 路径覆盖

任何 Skill 指定的默认文档目录，都不得覆盖本规则。

例如外部 Skill 默认要求写：

```text
docs/superpowers/specs/YYYY-MM-DD-topic-design.md
```

在本 harness 中必须改写为：

```text
state.phase_dir/03-solution-design.md
```

或当前 workflow 节点指定的产物名。

## 跨仓库任务

跨仓库修改时，源码可以写入目标仓库，但流程产物仍归属发起任务的 harness。

示例：

- 前端源码：`D:\projects\wms-ui`
- 后端源码：`D:\projects\wms-rear`
- 流程产物：当前 harness 的 `state.phase_dir`

不要在目标源码仓库里另建 `docs/superpowers` 保存本次 run 的设计、计划或证据。

## 例外

只有用户明确要求创建普通项目文档，且该文档不是本次 harness 流程产物时，才可以写入项目约定的文档目录。

即便如此，写入前也要说明它不是 harness 阶段产物。
