# 构建规则

目的：让构建验证可复现、可定位、可审计。

## 必须执行

1. 优先使用仓库已有的构建命令。
2. 如果没有文档化命令，先检查项目文件：
   - Node: `package.json`
   - Python: `pyproject.toml`, `setup.py`, `requirements.txt`
   - Java: `pom.xml`, `build.gradle`
   - .NET: `*.sln`, `*.csproj`
3. 如果仓库支持模块级构建，优先只构建受影响模块。
4. 将确切命令和结果记录到 `state.phase_dir/12-compile.md`。

## 避免

- 没有明确理由时，不要运行过宽、过慢或有破坏性的构建命令。
- 没看过日志，不要声称编译成功。
- “命令不可用”不是成功，必须记录为阻塞或豁免。

## 输出格式

```markdown
# 编译结果

- 命令：
- 工作目录：
- 退出码：
- 结果：PASS | FAIL | WAIVED | BLOCKED
- 关键输出：
- 后续动作：
```

