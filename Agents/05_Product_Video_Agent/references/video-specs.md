# 视频时长

`video_timing.py` 按调用方给定的目标秒数和语速估算。默认 2.5 词/秒只是脚本默认值，不是亚马逊官方口播标准，用 `--wps` 改。

不把 15 秒或 30 秒写成平台上限。官方视频规格待核实，待后续 PR。

```bash
python scripts/video_timing.py --script examples/narration_placeholder.txt --target 20 --wps 2.5
```

示例配音是英文教学句，不是广告成片。
