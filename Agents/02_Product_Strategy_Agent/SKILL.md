---
name: product-strategy
description: >-
  Amazon 定位词典与显式费率下的定价算术。不预设佣金，不使用已退役的 SKU 四角色。
---

# 02 Product Strategy

## 底线

不编费率。不把待补定位写成已有定义。不代替人做 `decision_approved`。

## 最小输入

- `site`
- 定位候选（只能是词典中的名称，或「待补定义」）
- 若要算价格：售价、到岸成本、佣金百分比，以及货币标签

## 顺序

```text
1. 读 docs/amazon/01_product_positioning.md
2. prompts/01_product_decision.md
3. 需要算术时才跑 scripts/sku_pricing.py，费率来自命令行
4. prompts/02_pricing_and_sku.md 解读脚本输出
```

## 不要做

- 使用引流 / 高配 / 套装作为现行角色
- 把 `platform_fees.json` 里的空预设当成 0 佣金
- 写出 VC/DI/DF 的官方公式
