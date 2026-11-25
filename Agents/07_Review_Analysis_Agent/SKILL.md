---
name: review-analysis
description: >-
  对调用方导出的 Amazon 评论做归类计数。不代写评价，不删评。
  Q&A 与星级换算待后续 PR。
---

# 07 Review Analysis

## 底线

分类可以讨论，计数必须跑 `review_stats.py`。不输出评价模板。

## 最小输入

- 含 `rating` 的 CSV
- 若要算占比：差评行上的 `category` 列（类别名由本次分析定义，不假装是官方枚举）

## 顺序

```text
1. prompts/01 拟定类别，但数字留空
2. 人把类别填回 CSV 后跑 review_stats.py
3. prompts/02 只根据脚本谈「说明是否没写清」，不谈如何改评
```
