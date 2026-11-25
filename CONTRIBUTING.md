# CONTRIBUTING

贡献要真实、脱敏、可复现。操作平台是 Amazon 美国站与欧洲站点。

## 可以贡献什么

| 类型 | 说明 |
|---|---|
| 经 Seller Central 或官方帮助页核对过的字段说明 | 附上 URL 与核对日期。对不上就标待核实 |
| 脱敏后的空表或案例 | 无店铺、无员工姓名、无真实成本与 ASIN 业务行 |
| Prompt | 保留合规守卫，缺字段必须报错 |
| 文档勘误 | 指出哪一句把实践口径写成了官方 |

## 不接受

| 内容 | 原因 |
|---|---|
| 刷单、刷评、补单、控评节奏、规避风控 | 见 [`docs/05_SOP_Gap_Register.md`](./docs/05_SOP_Gap_Register.md) |
| 没有来源的佣金、FBA、VAT、eCPM 公式 | 会变成假的官方预设 |
| 选品指南针或商机探测器的臆造字段词典 | 名称可以登记，字段要等资料 |
| 真实店铺、账号、买家、未授权品牌 | 隐私与商标 |
| 把空格占位写成亚马逊官方强制规则 | 那是实践口径 |

## 案例

1. 产品只保留能公开的类目描述，不写活 SKU。
2. 输入字段完整，输出能被下游模板接住。
3. 字符数、时长、价格来自脚本或可手算的式子。
4. 过 [`docs/04_Result_Checklist.md`](./docs/04_Result_Checklist.md)。
5. 定位用 [`docs/amazon/01_product_positioning.md`](./docs/amazon/01_product_positioning.md)。待补定义不要擅自补上。

## Prompt

遵循 [`docs/01_Prompt_Design_Guide.md`](./docs/01_Prompt_Design_Guide.md)。保留 `COMPLIANCE GUARD`。自检项必须是通过 / 不通过。

## 目录

```text
Agents/<NN>_<Name>_Agent/
├── README.md
├── prompts/
├── templates/
└── examples/          至少说明本模块示例是教学占位还是已核实
```

跨模块空表放 [`Templates/`](./Templates/)。Amazon 专用空表放 [`Templates/amazon/`](./Templates/amazon/)。方法论文档放 `docs/` 或 `docs/amazon/`。

## 提交说明

```text
feat: …
fix: …
docs: …
prompt: …
chore: …
```

提交前确认：没有违规步骤，没有未标注的假费率，没有真实商业数据，合规守卫还在。
