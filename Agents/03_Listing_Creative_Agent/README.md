# 03 · 商品内容

本批交付三件事：合规守卫、字符实测、把人指向属性实践分栏。

关键词打标、标题公式的完整套用、五点、Search Terms、A+ 文案包，待后续 PR。不要用一套通用标题公式冒充已核实的 Amazon 规则。

字符数的并排口径在 [`docs/02_Platform_Output_Spec.md`](../../docs/02_Platform_Output_Spec.md)。脚本不因为超过 75 或 200 而失败。

## 用法

```bash
python scripts/title_lint.py "buyer-facing title" --forbidden "best,#1"
```

参数一致性：

```bash
python scripts/spec_consistency.py --title "..." --specs examples/spec_table.csv
```

`examples/spec_table.csv` 是教学占位，不是某个在售商品。
