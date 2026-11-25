# 01 · 市场分析

解读**调用方已经导出的表**。集中度、价格分箱和配置交叉由 `scripts/market_metrics.py` 计算。模型不心算，也不把缺失的搜索量补成一个数。

亚马逊侧的 ABA、品牌分析、商机探测器、选品指南针，目前只登记名称，字段词典待补。见 [`docs/amazon/03_official_tools.md`](../../docs/amazon/03_official_tools.md)。

## 输入 / 输出

| 输入 | 输出 |
|---|---|
| 含价格、销量或销售额、卖家、品牌的表 | 标准化 JSON + 指标报告 |
| 站点、类目假设、公司能不能做的说明 | 前置判断：继续或停止 |

样本是合成数据，用来检查脚本，不是市场结论。见 `samples/README.md`。

## 用法

```bash
python scripts/normalize_export.py ../samples/sample_category_synthetic.csv
python scripts/market_metrics.py ../samples/sample_category_synthetic.normalized.json \
  --config-fields 功率,承重 --format md
```

列名对不上时用 `--mapping`。不要为了跑通去改业务数字。

## 限制

- 不爬取前台，不登录卖家后台
- 不把知识图里的「类目准入 12 闸」「BOSM 42 维」展开成字段清单（标题见知识图索引，正文待后续 PR）
- 前置判断不通过时，不写下游定位
