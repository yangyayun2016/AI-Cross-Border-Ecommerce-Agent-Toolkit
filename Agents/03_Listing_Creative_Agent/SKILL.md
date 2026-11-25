---
name: listing-creative
description: >-
  Amazon 商品文案的合规约束、字符实测和属性实践对照。
  不把某一年的字数上限写成唯一官方规则。文案包待后续 PR。
---

# 03 Listing Creative

## 底线

数字来自 `spec_table`。字符数来自 `title_lint.py`。空格占位不是官方政策。

## 最小输入

- `site` 与 `language`
- `spec_table`
- 若写买家可见句：`brand_authorized`（默认否）

## 顺序

```text
1. 读 docs/amazon/02_listing_attribute_practice.md 与 docs/02_Platform_Output_Spec.md
2. prompts/01 只做「还不能写的清单」，不输出完整文案包
3. 有标题草稿才跑 title_lint.py
4. prompts/03 做合规扫描
```

## 不要做

- 编写一套当官方用的标题五段公式
- 把五点 255 字写成已核实上限
- 教空格占位的变体写法
