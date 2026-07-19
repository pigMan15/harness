# 学习沉淀规则

目的：把重复失败转成持久规则。

## 三级经验

1. `lesson`：一次观察到的失败。
2. `pattern`：在不同任务中重复出现的失败。
3. `instinct`：确认后加入默认 harness 行为的规则。

## 必须执行

当失败重复出现时，在 `state.phase_dir/learn-YYYYMMDD-topic.md` 写学习记录。

格式：

```markdown
# 学习记录

- 等级：lesson | pattern | instinct-candidate
- 触发条件：
- 失败现象：
- 根因：
- 新规则：
- 应写入位置：
- 人工确认：
```

只有在用户明确确认后，才能将规则提升为 `instinct`。

