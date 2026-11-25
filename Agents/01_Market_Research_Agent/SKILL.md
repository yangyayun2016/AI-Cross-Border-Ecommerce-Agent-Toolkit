---
name: market-research
description: >-
  解读调用方提供的 Amazon 类目表：标准化、集中度、价格带、配置交叉。
  不编造搜索量、BSR 或官方工具字段。
---

# 01 Market Research

## 底线

不编数据。脚本算指标。商机探测器和选品指南针的字段待补，不要现编。

## 最小输入

- 站点（US 或具体欧洲站）
- 一张至少含价格和销量（或销售额）的表
- 公司是否有供应与售后能力的说明（没有就停在前置判断）

## 顺序

```text
1. prompts/01_category_precheck.md
   不通过则停止
2. python scripts/normalize_export.py <表>
3. python scripts/market_metrics.py <normalized.json>
4. prompts/02_market_analysis.md 只解读脚本输出
```

## 不要做

- 用印象填写 CR、HHI 或价格带
- 把合成样本 `samples/` 说成某类目的真实市场份额
- 展开 12 闸或 42 维的评分细则
