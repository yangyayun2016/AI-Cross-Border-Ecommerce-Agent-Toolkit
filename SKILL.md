---
name: sop-ecom-toolkit
description: >-
  跨境电商运营 AI 工具箱总入口（Amazon 美国站与欧洲站点）。
  覆盖市场调研、产品定位与显式费率下的定价算术、Listing 合规与属性实践、
  Amazon 主图检查、视频时长、广告盈亏线、评论计数，以及诊断后的小步回流。
  当用户要看类目、对定位、算给定费率下的价格、核对属性、查主图、
  算视频时长、算广告盈亏线或归类评论时使用。
  不用于代操作卖家后台、刷单刷评、或在没有官方出处时编造费率与字段词典。
allowed-tools:
  - Bash(python *)
  - Read
  - Write
metadata:
  version: 0.5.0-pr1
  category: e-commerce/operations
  license: MIT
---

# AI Cross Border Ecommerce Agent Toolkit（总入口）

先看路由表，再打开子模块的 `SKILL.md`。子模块写着「待后续 PR」的部分，不要用通用电商常识补成一份假 SOP。

## 三条底线

1. **不编数据。** 缺字段输出 `[INPUT_MISSING]`。指标走 `scripts/`。费率和工具字段没有核实来源就标待核实。
2. **合规优先。** 见 `docs/03_Compliance_Guard.md` 与 `docs/05_SOP_Gap_Register.md`。不写刷单、刷评步骤。
3. **买家可见文本使用该 Amazon 站点的语言**，内部备注用中文。数字必须能回到 `spec_table` 或脚本输出。

## 路由

| 用户要做的事 | 打开 |
|---|---|
| 阶段顺序、发货前到推广前期 | [docs/amazon/00_ops_framework.md](docs/amazon/00_ops_framework.md) |
| 战略款 / 主推款，或其他定位是不是待补 | [docs/amazon/01_product_positioning.md](docs/amazon/01_product_positioning.md) |
| 后台属性、空格占位算不算官方 | [docs/amazon/02_listing_attribute_practice.md](docs/amazon/02_listing_attribute_practice.md) |
| 选品指南针、商机探测器叫什么 | [docs/amazon/03_official_tools.md](docs/amazon/03_official_tools.md) |
| 解读一张已导出的类目表 | [Agents/01_Market_Research_Agent/SKILL.md](Agents/01_Market_Research_Agent/SKILL.md) |
| 定位落地、用显式费率做算术 | [Agents/02_Product_Strategy_Agent/SKILL.md](Agents/02_Product_Strategy_Agent/SKILL.md) |
| 属性核对、标题字符实测、合规扫描 | [Agents/03_Listing_Creative_Agent/SKILL.md](Agents/03_Listing_Creative_Agent/SKILL.md) |
| 主图是否接近既有 Amazon 规则卡 | [Agents/04_Product_Image_Agent/SKILL.md](Agents/04_Product_Image_Agent/SKILL.md) |
| 视频时长 | [Agents/05_Product_Video_Agent/SKILL.md](Agents/05_Product_Video_Agent/SKILL.md) |
| 广告盈亏线（不改后台） | [Agents/06_Advertising_Optimization_Agent/SKILL.md](Agents/06_Advertising_Optimization_Agent/SKILL.md) |
| 评论归类计数 | [Agents/07_Review_Analysis_Agent/SKILL.md](Agents/07_Review_Analysis_Agent/SKILL.md) |

```text
01 → 02 → 03/04/05 → 人上架 → 06/07 → 只改有证据的一处 → 复测
```

## 执行顺序

```text
1. 打开子模块 SKILL.md
2. 按最小输入要数据。没有导出表就停
3. 跑 scripts/
4. 按 prompts/ 产出，并跑自检
5. 提醒：发布前到 Seller Central 复核
```

## 已知限制

- 不代操作后台
- 不采集数据
- 不渲染最终图片或成片
- 关键词文案包、盈亏模板、广告架构、eCPM、VOC、两个官方工具的字段词典：待后续 PR
