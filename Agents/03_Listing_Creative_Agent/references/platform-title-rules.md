# 标题规则卡

本卡不设单一官方上限。

| 要做的事 | 做法 |
|---|---|
| 数字符 | `title_lint.py`，按 Unicode 字符而不是字节 |
| 对照口径 | [`docs/02_Platform_Output_Spec.md`](../../../docs/02_Platform_Output_Spec.md) |
| 默认建议 | 发布前按后台实时规则复核 |
| 失败条件 | 仅当命中调用方给出的禁用词。超长只 INFO，不 FAIL |

禁止：未授权品牌、绝对化用语、把促销语塞进商品名称。
