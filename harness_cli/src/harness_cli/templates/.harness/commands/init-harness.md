# Command: init-harness

目的：把通用 harness 适配到具体项目。

## 步骤

1. 识别项目类型和主要构建/测试命令。
2. 用确切项目命令更新 `.harness/rules/build.md`。
3. 如果项目不部署或不使用 worktree，更新 `.harness/workflow.yaml`。
4. 将项目特有安全约束加入 `.harness/rules/safety.md`。
5. 运行 `.harness/scripts/validate-harness.ps1`。

## 输出

写入 `state.phase_dir/init-harness.md`：

- 项目类型
- 构建命令
- 测试命令
- 部署命令，如有
- 已知约束

