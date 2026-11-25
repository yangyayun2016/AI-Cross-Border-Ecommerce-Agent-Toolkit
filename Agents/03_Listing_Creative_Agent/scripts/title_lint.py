#!/usr/bin/env python3
"""商品名称字符实测（Amazon）。只报长度，不把某一上限当成唯一官方规则。

  python title_lint.py "Title text" --forbidden "best,#1"

并排口径见 docs/02_Platform_Output_Spec.md。
默认建议：发布前按后台实时规则复核。
超过 75 或 200 都只记 INFO，不因此 FAIL。
FAIL 仅在命中调用方传入的禁用词，或同一词重复达到 3 次。
"""
import argparse
import json
import re
import sys

PROMO_WORDS = [
    "free shipping", "best seller", "sale", "discount", "% off",
    "免费", "促销", "特价", "全网第一",
]

EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF]")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def analyse(title, args):
    res = []
    t = title.strip()
    n = len(t)

    res.append(("INFO", "length", (
        f"{n} 字符（实测）。"
        "论坛公告口径：商品名称 75（含空格，媒体类除外的说法见公告）、"
        "Item Highlights 125；答复帖称两栏合计仍可到 200。"
        "资料内还有「一般 200」与「标题 <75 / 亮点 <125」。"
        "五点 255 仅为知识图实践口径。帮助页正文未在本仓库摘录。"
        "发布前按后台实时规则复核。本脚本不因超过其中任一数字而失败。"
    )))

    forbidden = args.forbidden or []
    if isinstance(forbidden, str):
        forbidden = [w.strip() for w in forbidden.split(",") if w.strip()]
    if args.forbidden_file:
        try:
            with open(args.forbidden_file, encoding="utf-8") as f:
                forbidden += [ln.strip() for ln in f if ln.strip()]
        except OSError as e:
            res.append(("WARN", "forbidden", f"禁用词文件读不了：{e}"))
    hits = [w for w in forbidden if w and w.lower() in t.lower()]
    if hits:
        res.append(("FAIL", "forbidden", f"命中禁用词：{'、'.join(hits)}"))
    elif forbidden:
        res.append(("PASS", "forbidden", f"0 命中（查了 {len(forbidden)} 个词）"))

    if args.keywords:
        kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
        missing = [k for k in kws if k.lower() not in t.lower()]
        if missing:
            res.append(("WARN", "keywords", f"未覆盖：{'、'.join(missing)}"))
        else:
            res.append(("PASS", "keywords", "调用方给出的词都出现了"))

    low = t.lower()
    promo_hits = [w for w in PROMO_WORDS if w in low]
    if promo_hits:
        res.append(("WARN", "promo", f"可能是促销或绝对化用语：{'、'.join(promo_hits)}"))

    if EMOJI_RE.search(t):
        res.append(("WARN", "emoji", "含表情符号。发布前按该类目规则复核"))

    words = re.findall(r"[A-Za-z0-9]+", t.lower())
    dup = [w for w in set(words) if words.count(w) >= 3 and len(w) > 2]
    if dup:
        res.append(("FAIL", "duplicates", f"同一词重复 ≥3 次：{'、'.join(dup)}"))

    if CJK_RE.search(t):
        res.append(("WARN", "locale", "含中文。美欧买家可见标题通常用站点语言，请确认这不是内部备注"))

    ok = not any(lv == "FAIL" for lv, _, _ in res)
    return dict(platform="amazon", chars=n, ok=ok, checks=res, preview=t[:40])


def main():
    ap = argparse.ArgumentParser(description="Amazon 商品名称字符实测（不设唯一官方上限）")
    ap.add_argument("title", nargs="?", help="标题文本；或用 --file")
    ap.add_argument("--file", help="一行一个标题")
    ap.add_argument("--platform", default="amazon", help="只接受 amazon")
    ap.add_argument("--forbidden", help="禁用词，逗号分隔")
    ap.add_argument("--forbidden-file", help="禁用词文件")
    ap.add_argument("--keywords", help="希望覆盖的词，逗号分隔")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.platform != "amazon":
        sys.exit("[INPUT_MISSING] 只支持 --platform amazon。其他站点规则已从本仓库移除。")

    titles = []
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                titles = [ln.strip() for ln in f if ln.strip()]
        except OSError as e:
            sys.exit(f"[ERROR] 读不了文件：{e}")
    elif args.title:
        titles = [args.title]
    else:
        sys.exit("[ERROR] 给标题文本或 --file")

    reports = [analyse(t, args) for t in titles]
    all_ok = all(r["ok"] for r in reports)
    if args.json:
        print(json.dumps(reports if len(reports) > 1 else reports[0],
                         ensure_ascii=False, indent=2))
    else:
        icon = {"PASS": "PASS", "WARN": "WARN", "FAIL": "FAIL", "INFO": "INFO"}
        for r in reports:
            print(f"\n[{r['platform']}] {r['chars']} 字符  "
                  f"{'通过' if r['ok'] else '未通过'}  「{r['preview']}」")
            for lv, name, detail in r["checks"]:
                print(f"  {icon[lv]:<4} {name:<12} {detail}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
