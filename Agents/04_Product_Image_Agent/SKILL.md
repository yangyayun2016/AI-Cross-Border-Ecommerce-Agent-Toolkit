---
name: product-image
description: >-
  按仓库内的 Amazon 主图规则卡检查白底、尺寸和主体占比。
  阈值发布前复核。设计需求表待后续 PR。
---

# 04 Product Image

## 底线

主图不叠促销字。规则卡不是豁免。不生成带虚假认证或评价截图的画面。

## 最小输入

- `site`
- 一张主图，或一份「还没有图」的说明
- 产品真实外观（颜色、是否有配件）。没有就不许在提示词里添加

## 顺序

```text
1. 读 references/platform-amazon.md
2. 有图则跑 check_main_image.py --platform amazon
3. prompts 只规划画面，不把规则卡改写成其他平台
```

## 不要做

- 要求主图加卖点大字
- 编造 1600 与 2000 谁才是唯一官方尺寸
