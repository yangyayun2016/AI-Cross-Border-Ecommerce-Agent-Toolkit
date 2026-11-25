# 定价算术骨架

本页不提供 Amazon 佣金、FBA、VAT 或订阅费。这些数字待后续盈亏模板，而且要能指到 Seller Central 费率表的日期。

体积重、体积和「箱重/365」不在这里重复，见 [`Templates/amazon/product_master_data.md`](./amazon/product_master_data.md)。

## 调用方填入

| 项 | 值 | 说明 |
|---|---|---|
| 货币 | `{USD/EUR/GBP…}` | 只是标签 |
| 售价 | `{ }` | 调用方 |
| 到岸成本 | `{ }` | 含采购与头程时请拆开写，不要混成一个无法追溯的数 |
| 佣金 % | `{ }` | 显式传入。空着就不能算 |
| 配送费 | `{ }` | 单件金额，不是百分比预设 |
| 退货预留 % | `{ }` | 未填则脚本按 0，并声明这不是平台费率 |
| 广告预留 % | `{ }` | 同上 |
| 税 % | `{ }` | 同上。欧洲 VAT 不要在这里写死 |
| 目标净利 % | `{ }` | 经营假设，不是平台规则。不填则不算目标价 |

## 脚本

```bash
python Agents/02_Product_Strategy_Agent/scripts/sku_pricing.py calc \
  --cost <到岸成本> --price <售价> --commission <已核对的佣金百分比>
```

`--platform amazon_us` 或 `amazon_eu` 只表示「该站点预设未核实」。不带 `--commission` 时脚本会退出，而不是使用某个历史百分比。

广告侧同一套显式费率：

```bash
python Agents/06_Advertising_Optimization_Agent/scripts/ad_metrics.py calc \
  --price <售价> --product-cost <成本> --commission <百分比> --cvr <转化率> --target-acos <目标>
```

输出是算术结果，不是定价决定。`decision_approved` 仍由人填写。
