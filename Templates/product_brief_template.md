# 产品简报（模块间契约）

缺了必填项就停，不要猜。金额和费率不是本模板的默认值。

## 必填

| 字段 | 说明 |
|---|---|
| `marketplace` | `amazon` |
| `site` | `US` 或具体欧洲站（DE / UK / FR / IT / ES 等） |
| `language` | 买家可见文本的语言。必须与 `site` 一致 |
| `product_name` | 内部中文名可以有，但要和买家可见名称分开 |
| `positioning` | 只填 [`docs/amazon/01_product_positioning.md`](../docs/amazon/01_product_positioning.md) 里的类型。未定义的类型写「待补定义」 |
| `spec_table` | 参数名与数值。没有的参数不要出现在下游文案里 |
| `decision_approved` | 只能由人填写 `yes`。模型不得改成 yes |

## 选填

| 字段 | 说明 |
|---|---|
| `sku` / `asin` | 没有就留空。不要编 ASIN |
| `brand_authorized` | 没有授权记录就当否 |
| `forbidden_terms` | 额外禁用词 |
| `cost` / `price` | 调用方自己的数，标明货币 |
| `fee_notes` | 若参加了定价算术，写明佣金等是谁传入的、核对日期。仓库不提供官方百分比 |

## 阻塞

`decision_approved` 不是 `yes` 时，03/04/05 只能出草稿，并在文首写「未批准，不可上架」。
