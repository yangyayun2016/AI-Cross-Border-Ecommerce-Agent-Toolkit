# AI Cross Border Ecommerce Agent Toolkit

**AI 跨境电商运营智能体工具箱** · 当前操作平台：**Amazon 美国站与欧洲站点**。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Status: PR1 Amazon](https://img.shields.io/badge/status-PR1%20Amazon%20US%2FEU-orange.svg)](./CHANGELOG.md)

把运营判断写成可复用的 Agent 入口：一份输入契约、一段不编数的脚本、一个人来点确认的闸门。

本批完成的是平台切换和第一批亚马逊运营材料。关键词、盈亏模板、补货、广告架构、VOC、视觉沟通表仍标着「待后续 PR」，没有用空泛步骤填上。

## 这批能直接打开的材料

| 材料 | 路径 |
|---|---|
| 运营五阶段 | [`docs/amazon/00_ops_framework.md`](./docs/amazon/00_ops_framework.md) |
| 定位词典 | [`docs/amazon/01_product_positioning.md`](./docs/amazon/01_product_positioning.md) |
| 后台属性（实践 / 官方分栏） | [`docs/amazon/02_listing_attribute_practice.md`](./docs/amazon/02_listing_attribute_practice.md) |
| 选品指南针、商机探测器（只登记名称） | [`docs/amazon/03_official_tools.md`](./docs/amazon/03_official_tools.md) |
| 知识图 10 层 82 节点标题 | [`docs/amazon/knowledge-map-index.md`](./docs/amazon/knowledge-map-index.md) |
| 主数据与立项空表 | [`Templates/amazon/`](./Templates/amazon/) |
| 差异登记 | [`docs/05_SOP_Gap_Register.md`](./docs/05_SOP_Gap_Register.md) |

## Agent

七个模块仍是一条链路的入口。深水区 SOP 还没写的，README 里会直接说。

| # | 模块 | 现在做什么 |
|---|---|---|
| 01 | [市场分析](./Agents/01_Market_Research_Agent/) | 解读调用方提供的表。集中度与价格带由脚本计算 |
| 02 | [产品策略](./Agents/02_Product_Strategy_Agent/) | 使用新的定位词典。费率必须显式传入，仓库不预设佣金 |
| 03 | [商品内容](./Agents/03_Listing_Creative_Agent/) | 属性实践 + 合规守卫 + 字符实测。文案包待后续 PR |
| 04 | [商品图](./Agents/04_Product_Image_Agent/) | Amazon 主图检查。设计需求表待后续 PR |
| 05 | [视频](./Agents/05_Product_Video_Agent/) | 按给定秒数算时长。官方规格待核实 |
| 06 | [广告](./Agents/06_Advertising_Optimization_Agent/) | 只算盈亏线，不改后台。架构与 eCPM 待后续 PR |
| 07 | [评论](./Agents/07_Review_Analysis_Agent/) | 归类计数。不代写、不删评。Q&A 待后续 PR |

```text
01 已有数据 → 02 定位与显式费率 → 03/04/05 草稿 → 人上架
→ 06/07 诊断导出数据 → 只改有证据的那一处 → 复测
```

## 怎么跑

不需要 API key。

```text
1. 打开对应 Agent 的 templates/，只填你能举证的字段
2. 系统 Prompt + 任务 Prompt + 填好的模板，交给模型
3. 有脚本的先跑脚本，再让模型解读脚本输出
4. 用 docs/04_Result_Checklist.md 自检
5. 发布前到 Seller Central 复核字数、类目属性和费率
```

## 设计原则

1. **不编数据。** 缺字段就停。官方没核对的费率、字段、字数上限写成待核实。
2. **人闸。** 上架、改价、开关广告、索赔由人执行。
3. **合规优先。** 见 [`docs/03_Compliance_Guard.md`](./docs/03_Compliance_Guard.md)。
4. **站点语言。** 买家可见文本用该站点语言，内部说明用中文。

## 目录

```text
docs/amazon/          运营框架与对照表
docs/00…05            架构、Prompt 规范、字段、合规、自检、差异登记
Templates/amazon/     去敏空表
Agents/               01–07
Examples/             只保留链路说明，不含旧站点案例正文
```

## 路线与贡献

路线图见 [`ROADMAP.md`](./ROADMAP.md)。贡献前读 [`CONTRIBUTING.md`](./CONTRIBUTING.md)。案例必须脱敏。

## Fork 与许可证

本仓库 fork 自 [heqiangdiao-wq/AI-Cross-Border-Ecommerce-Agent-Toolkit](https://github.com/heqiangdiao-wq/AI-Cross-Border-Ecommerce-Agent-Toolkit)。许可证为 MIT，版权声明保留在 [LICENSE](./LICENSE)（Copyright (c) 2026 AI Cross Border Ecommerce Agent Toolkit Contributors）。

此前版本的操作说明面向 Shopee 巴西站与 Mercado Livre。那些站点的规则、费率预设、关键词三榜和案例已从本 fork 删除。自本改写起，仓库教的是 Amazon 美国站与欧洲站点。

## 合规

工具箱只服务合法运营。大纲里的评论干预和订单干预没有写成步骤，登记见 [`docs/05_SOP_Gap_Register.md`](./docs/05_SOP_Gap_Register.md)。使用者自行承担违反平台规则的后果。
