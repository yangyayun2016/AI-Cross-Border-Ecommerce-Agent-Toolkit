# 主图夹具

只保留 Amazon 规则卡的检查。

```bash
python ../scripts/check_main_image.py amazon_fail.png --platform amazon
```

这张图预期不能通过规则卡（用来看报告长什么样）。通过与否以你本机跑出的结果为准。

修复命令会写新文件，不覆盖原图：

```bash
python ../scripts/check_main_image.py amazon_fail.png --platform amazon --fix /tmp/amazon_main_fixed.png
```
