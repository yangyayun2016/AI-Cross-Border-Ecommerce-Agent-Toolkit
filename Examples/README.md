# 示例库

这里只保留链路说明。旧的长案例（含其他站点的标题、葡语口播和费率演算）已删除，避免被当成现行做法。

| 顺序 | 看哪里 |
|---|---|
| 1 | [`docs/amazon/00_ops_framework.md`](../docs/amazon/00_ops_framework.md) |
| 2 | 各 Agent 的 `examples/README.md`：教学占位与脚本怎么跑 |
| 3 | [`docs/04_Result_Checklist.md`](../docs/04_Result_Checklist.md) |

## 闭环（仍然有效的纪律）

```text
有导出表 → 脚本出数 → 模型只解读 → 人改一处 → 用同一指标复测
```

没有复测导出，就不要写「已经改善」。一次只改脚本指出的那一类问题。

合成样本与占位 CSV 的数字都不是市场结论。
