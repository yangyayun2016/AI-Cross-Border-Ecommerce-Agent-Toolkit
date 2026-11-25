# 02 · 平台输出字段规范

操作平台：**Amazon 美国站与欧洲站点**。其他市场的字段表已从本仓库移除。

所有硬指标以 Seller Central **当时、该类目、该站点**的规则为准。下面凡是没能读到帮助页正文的，官方列写「待核实」。检查清单的默认建议只有一句：**发布前按后台实时规则复核。**

## 1. 商品名称、Item Highlights、要点

三套数字并排。它们来源不同，本仓库不选边当成唯一官方上限。

| 口径 | 商品名称 | 额外亮点 | 五点 / 要点 | 来源与分级 |
|---|---|---|---|---|
| 帮助页入口 | 待核实（正文本次未读到） | 待核实 | 待核实 | 商品名称：<https://sellercentral.amazon.com/help/hub/reference/external/GYTR6SYGFA5E3EQC> ；要点：<https://sellercentral.amazon.com/help/hub/reference/external/GX5L8BF8GLMML6CX> |
| Seller Central 论坛公告（2026） | 除媒体类外，2026-07-27 起公告要求不超过 75 个字符（含空格） | Item Highlights 125 个字符（含空格） | 论坛答复未给出五点上限 | 公告帖：<https://sellercentral.amazon.com/seller-forums/discussions/t/145b6d0f-999c-4555-896c-c694bda2e470> ；后续答复称重要信息合计仍可到 200，拆成名称 75 + 亮点 125：<https://sellercentral.amazon.com/seller-forums/discussions/t/302aaac6-6f2b-4d86-bcd2-36fe24f0e6cd> 。帖内还有「不足 75 才显示亮点」与「用满 75 仍显示」两种说法，**以后台为准** |
| 内部大纲 · 文案节 | 一般 200 字符内 | 未单列 | 痛点—方案，先写总结短语；前 3 点权重更高。此为写作建议，不是字数上限 | 资料口径，不是帮助页 |
| 内部大纲 · 完成度清单 | 标题长度 < 75；标题以品牌名开头 | 商品亮点 < 125 | 5 条及以上要点 | 资料口径，与文案节的 200 互相冲突 |
| 知识图节点标题旁的实践阈值 | 主标题 ≤ 75 | 亮点 ≤ 125 | 五点 ≤ 255 字符（注明 3P） | **实践口径**。节点正文未入库。255 未与帮助页核对，官方列仍为待核实 |
| 后台 Search Terms | — | — | 大纲写约 250 字符、可更少、不重复已用词、可全小写、半角空格分隔、不放品牌名 / ASIN / 无关词 | **待核实**。不在本批写成填写手册 |

欧洲站点语言不同，字符统计按该语言的字符数，不按字节。媒体类是否例外，只见于上述论坛公告，欧洲站是否同一天生效，待核实。

`Agents/03` 的 `title_lint.py` 只报告实测字符数，并打印本表，**不会**因为超过 75 或 200 就判失败。

## 2. 主图

既有规则卡（发布前复核，不在本批改数字）：[`Agents/04_Product_Image_Agent/references/platform-amazon.md`](../Agents/04_Product_Image_Agent/references/platform-amazon.md)。

大纲完成度清单另有这些**资料口径**，未逐条对上帮助页：8 张及以上图片；主图可缩放；建议 1600×1600。与规则卡里的 1000 / 2000 并排保留，发布前看后台。

## 3. 视频

不把「30 秒」「16:9」写成官方上限。调用方用 `video_timing.py --target` 传入自己的时长目标。官方规格待核实，待后续 PR。

## 4. 详情与 A+

长描述、A+、品牌故事的展示差异，大纲只提到「前后展示不同、可以继续埋词」。模块顺序与字符上限待后续 PR。属性填写的实践对照见 [`docs/amazon/02_listing_attribute_practice.md`](./amazon/02_listing_attribute_practice.md)。

## 5. 语言

买家可见文本使用**该站点的语言**（美国站英语；欧洲站按 DE / FR / IT / ES / UK 等实际站点）。内部备注用中文。不要先写中文再整段机翻后直接上架。缺站点字段则停止，不要猜语言。
