# 证据模板

按这个结构创建 `state.phase_dir/15-evidence.json`。创建前必须读取 `.harness/state.json`，不要写入 `docs/superpowers`。

**语言要求：所有描述性字段（residual_risks、waivers、command name、result 等）必须使用中文填写。**

```json
{
  "run_id": "",
  "intent": "",
  "risk": "",
  "changed_files": [],
  "commands": [
    {
      "name": "构建命令",
      "command": "",
      "cwd": "",
      "exit_code": null,
      "result": "构建成功，退出码 0"
    }
  ],
  "gates": {
    "G1_REQUIREMENTS": "PASS",
    "G2_DESIGN": "PASS",
    "G3_COMPILE": "PASS",
    "G4_UNIT_TEST": "PASS",
    "G5_ATDD": "NOT_REQUIRED",
    "G6_EVIDENCE": "PASS",
    "G7_PRERELEASE": "NOT_REQUIRED",
    "G8_ACCEPTANCE": "PASS"
  },
  "artifacts": [],
  "waivers": [
    {"scope": "G5_ATDD", "reason": "纯前端项目，无集成测试框架"}
  ],
  "residual_risks": [
    "跨浏览器兼容性未穷举测试（仅覆盖 Chrome）",
    "移动端键盘输入行为可能与桌面端不一致",
    "屏幕阅读器无障碍测试未执行",
    "超大数字可能溢出显示布局"
  ]
}
```

