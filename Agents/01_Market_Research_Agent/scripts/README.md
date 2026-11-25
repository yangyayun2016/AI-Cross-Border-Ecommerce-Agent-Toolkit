# 脚本

合成样本不是市场数据。

```bash
python make_sample.py
python normalize_export.py ../samples/sample_category_synthetic.csv
python market_metrics.py ../samples/sample_category_synthetic.normalized.json \
  --config-fields 功率,承重 --format md
```

`normalize_export.py` 只做列名对齐和数字清洗。它不认识商机探测器或选品指南针的字段。对不上的列用 `--mapping` 指向一份 JSON。

`market_metrics.py` 计算集中度、价格分箱和配置交叉。解读留给 Agent，脚本不写结论。
