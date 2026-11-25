# 02 · 产品策略

两件事：

1. 用 [`docs/amazon/01_product_positioning.md`](../../docs/amazon/01_product_positioning.md) 标注定位。未定义的类型保持「待补定义」。
2. 在调用方**显式传入**佣金等费率时，用脚本算净利、盈亏价。仓库不内置 Amazon 官方费率。

`decision_approved` 只能由人改成 yes。模型不决定上架。

旧的 SKU 四角色（引流 / 主推 / 高配 / 套装）已退役，只在定位词典里作为对照被提到，不在本模块继续使用。

## 用法

```bash
python scripts/sku_pricing.py --list-platforms
python scripts/sku_pricing.py calc --cost 20 --price 40 --commission 15 --currency USD
```

`--commission 15` 是命令示例里的**调用方数字**，不是本仓库认定的美国站佣金。不传 `--commission` 时，即使写了 `--platform amazon_us`，脚本也会退出。

美欧 SC / VC / DI / DF 的完整模板待后续 PR。

## 示例

`examples/sample-skus.csv` 的金额是教学占位，用来看矩阵命令的列是否认得出。不要把它当成定价方案。
