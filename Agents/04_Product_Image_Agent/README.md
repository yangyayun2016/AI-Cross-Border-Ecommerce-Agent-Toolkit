# 04 · 商品图

自动检查只覆盖 Amazon 主图规则卡里的像素项。设计需求表待后续 PR。

```bash
python scripts/check_main_image.py 图.png --platform amazon
```

`--fix` 会把近白拉成纯白并按规则卡重排主体占比。修复后的图仍要人看过，才能上传。

`tests/amazon_fail.png` 是一张用于观察失败报告的夹具，不是商品素材。
