# 06 · 广告算术

脚本根据调用方给出的售价、成本、佣金和导出的广告表，计算盈亏线并给建议分级。它不登录广告后台，不改预算。

SP / SB / SD 的架构、命名、批量上传、新品 45 天安排、eCPM、自然单占比，待后续 PR。知识图里这些只是标题，见 [`docs/amazon/knowledge-map-index.md`](../../docs/amazon/knowledge-map-index.md)。

```bash
python scripts/ad_metrics.py calc --price 40 --product-cost 18 --commission 15 \
  --cvr 10 --target-acos 25 --currency USD
```

这里的 15 和 25 是命令形状，不是官方费率或官方目标。

曝光充分性门槛 `--min-impressions` 默认 1000，是脚本的数据量开关，不是平台冷启动规则。
