# 证据模板

按这个结构创建 `state.phase_dir/15-evidence.json`。创建前必须读取 `.harness/state.json`，不要写入 `docs/superpowers`。

```json
{
  "run_id": "",
  "intent": "",
  "risk": "",
  "changed_files": [],
  "commands": [
    {
      "name": "",
      "command": "",
      "cwd": "",
      "exit_code": null,
      "result": "PASS"
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
  "waivers": [],
  "residual_risks": []
}
```

