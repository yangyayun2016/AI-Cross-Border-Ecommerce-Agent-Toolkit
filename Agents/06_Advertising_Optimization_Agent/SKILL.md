---
name: advertising-optimization
description: >-
  用调用方显式费率计算广告盈亏线，并按导出表分级建议。
  不改广告后台。架构、日志和 eCPM 待后续 PR。
---

# 06 Advertising

## 底线

不编 CVR、ACOS、佣金。建议不是已经执行。人决定要不要改后台。

## 最小输入

- 售价、产品成本、佣金百分比
- 若做诊断：广告导出 CSV（曝光、点击、花费、订单）

## 顺序

```text
1. 没有佣金就停止，不要假设一个百分比
2. python scripts/ad_metrics.py
3. prompts 只转述脚本，并写明未覆盖 SP/SB/SD 架构
```
