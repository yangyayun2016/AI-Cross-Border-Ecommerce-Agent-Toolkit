---
name: product-video
description: >-
  按调用方给定的秒数估算配音时长与字幕行长。不宣布 Amazon 官方视频上限。
---

# 05 Product Video

## 底线

时长以脚本为准。不在画面或字幕里承诺 `spec_table` 没有的参数。不写评价引导台词。

## 最小输入

- `site` 与 `language`
- 一行一句的配音稿
- `--target` 秒数（调用方的目标，不是平台上限）

## 顺序

```text
1. prompts/01 分镜，未知事实就留空
2. python scripts/video_timing.py --script 稿.txt --target <秒>
3. prompts/02 只把脚本结果写进制作说明
```
