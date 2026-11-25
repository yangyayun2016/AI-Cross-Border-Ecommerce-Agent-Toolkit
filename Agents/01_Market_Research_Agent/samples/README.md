# 合成样本

`sample_category_synthetic.csv` 由 `scripts/make_sample.py` 用固定随机种子生成。金额和标题都是教学夹具，用来检查清洗和指标脚本。

不要把 `*.metrics.md` 里的数字写成某个 Amazon 类目的结论。

```bash
python ../scripts/make_sample.py
python ../scripts/normalize_export.py sample_category_synthetic.csv
python ../scripts/market_metrics.py sample_category_synthetic.normalized.json \
  --config-fields 功率,承重 --format md
```

报告会写到 `sample_category_synthetic.normalized.metrics.md`。

配置交叉需要标题里能解析出功率和承重。当前样本标题是英文夹具，若脚本认不出配置字段，报告会写未覆盖，这是预期，不要手填。
