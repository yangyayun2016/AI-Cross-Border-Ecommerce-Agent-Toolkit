# 07 · 评论

模型负责把每条评论归到调用方给出的类别，脚本负责计数。不代写买家评论，不教删评，不安排星级节奏。

Q&A 专项、跨站点星级换算待后续 PR。知识图里有相关标题，正文不在本批。

```bash
python scripts/review_stats.py --file examples/sample-reviews.csv \
  --fixable "误解,参数不符"
```

示例 CSV 是四行教学数据。
