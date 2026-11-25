#!/usr/bin/env python3
"""SKU 定价算术脚本 —— 只算，不猜，不定价（定价决策由人）。

  python sku_pricing.py --list-platforms
  python sku_pricing.py calc --cost 18 --price 40 --commission 15 --currency USD

amazon_us / amazon_eu 在 platform_fees.json 里没有费率数字。
不传 --commission 时退出，不用历史默认佣金，也不把「待核实」当成 0。

未传入的退货、广告、税、附加，按 0 参与本次运算，输出会标明这不是平台费率。
不传 --target-margin 就不算目标价。

  广告前毛利 = 售价 − 到岸成本 − 售价×(佣金%+退货%+税%+附加%) − 按件固定费
  净利率     = (广告前毛利 − 售价×广告%) ÷ 售价
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

_CURRENCY_RE = re.compile(r"(?i)(BRL|R\$|USD|US\$|EUR|GBP|CNY|RMB|JPY|€|£|¥|元|\$)")
_CURRENCY_CODE = {
    "BRL": "BRL", "R$": "BRL",
    "USD": "USD", "US$": "USD", "$": "USD",
    "EUR": "EUR", "€": "EUR",
    "GBP": "GBP", "£": "GBP",
    "CNY": "CNY", "RMB": "CNY", "元": "CNY",
    "JPY": "JPY", "¥": "JPY",
}

PLATFORMS_FILE = Path(__file__).with_name("platform_fees.json")

def rates_ready(preset: dict | None) -> bool:
    """预设里有没有可以参与运算的佣金。待核实占位一律不算。"""
    if not preset:
        return False
    if preset.get("rates_included") is False or preset.get("status") == "待核实":
        return False
    return "commission_pct" in preset or bool(preset.get("commission_tiers"))


def load_platforms() -> dict:
    try:
        with open(PLATFORMS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except OSError as e:
        sys.exit(f"[ERROR] 读不到平台费率表 {PLATFORMS_FILE.name}：{e}")


def _tier_lookup(price: float, tiers: list, default: float) -> float:
    """tiers: [{"max": 79.99, "fee"/"pct": v}, ..., {"max": null, ...}]，按序首个命中。"""
    for t in tiers or []:
        mx = t.get("max")
        if mx is None or price <= float(mx):
            v = t.get("pct", t.get("fee", default))
            return float(v)
    return default


class FeeModel:
    """费率模型：显式 CLI 参数 > 平台预设 > 历史默认。佣金/固定费可随价格分档。"""

    def __init__(self, preset: dict | None = None, *, commission=None,
                 return_rate=None, ad=None, tax=None, target_margin=None,
                 extra_pct=None, fixed_fee=None):
        self.p = preset or {}
        self.o = dict(commission=commission, return_rate=return_rate, ad=ad,
                      tax=tax, target_margin=target_margin,
                      extra_pct=extra_pct, fixed_fee=fixed_fee)

    def _scalar(self, key: str, preset_key: str) -> float:
        if self.o[key] is not None:
            return float(self.o[key])
        if preset_key in self.p and self.p[preset_key] is not None and rates_ready(self.p):
            return float(self.p[preset_key])
        return 0.0

    def commission_pct(self, price: float) -> float:
        if self.o["commission"] is not None:
            return float(self.o["commission"])
        if rates_ready(self.p):
            if self.p.get("commission_tiers"):
                return _tier_lookup(price, self.p["commission_tiers"],
                                    float(self.p.get("commission_pct", 0)))
            return float(self.p["commission_pct"])
        sys.exit("[RATES_UNVERIFIED] 没有可使用的佣金。请在核对 Seller Central 后传入 --commission。"
                 "本仓库的站点预设不包含费率数字，也不会回退到历史默认值。")

    def fixed_fee(self, price: float) -> float:
        if self.o["fixed_fee"] is not None:
            return float(self.o["fixed_fee"])
        if rates_ready(self.p) and self.p.get("fixed_fee_tiers"):
            return _tier_lookup(price, self.p["fixed_fee_tiers"], 0.0)
        return 0.0

    def return_pct(self) -> float: return self._scalar("return_rate", "return_pct")
    def tax_pct(self) -> float:    return self._scalar("tax", "tax_pct")
    def extra_pct(self) -> float:  return self._scalar("extra_pct", "extra_pct")
    def ad_pct(self) -> float:     return self._scalar("ad", "ad_pct")
    def target_margin(self):
        if self.o["target_margin"] is not None:
            return float(self.o["target_margin"])
        if rates_ready(self.p) and self.p.get("target_margin_pct") is not None:
            return float(self.p["target_margin_pct"])
        return None

    def margin(self, price: float, cost: float, ad_pct: float | None = None) -> dict:
        ad = self.ad_pct() if ad_pct is None else ad_pct
        cp = self.commission_pct(price)
        ff = self.fixed_fee(price)
        pct = cp + self.return_pct() + self.tax_pct() + self.extra_pct()
        pre = price - cost - price * pct / 100 - ff
        net = pre - price * ad / 100
        return dict(pre_ad_margin=round(pre, 2),
                    pre_ad_rate=round(pre / price, 4) if price else 0,
                    net_margin=round(net, 2),
                    net_rate=round(net / price, 4) if price else 0,
                    commission_pct_applied=cp,
                    fixed_fee_applied=round(ff, 2))

    def _solve(self, cost: float, ad_pct: float, tm_pct: float) -> float | None:
        """盈亏/目标价：p = (cost + fixed_fee(p)) / (1 − Σpct(p)/100)，不动点迭代。"""
        p = max(cost, 1.0)
        for _ in range(12):
            pct = (self.commission_pct(p) + self.return_pct() + self.tax_pct()
                   + self.extra_pct() + ad_pct + tm_pct) / 100
            denom = 1 - pct
            if denom <= 0:
                return None
            p = (cost + self.fixed_fee(p)) / denom
        return round(p, 2)

    def break_even_price(self, cost: float) -> float | None:
        return self._solve(cost, 0.0, 0.0)

    def target_price(self, cost: float) -> float | None:
        tm = self.target_margin()
        if tm is None:
            return None
        return self._solve(cost, self.ad_pct(), tm)


def _model_from_args(args, plats: dict) -> FeeModel:
    preset = None
    if getattr(args, "platform", None):
        key = args.platform.strip()
        if key not in plats or key.startswith("_"):
            keys = "、".join(k for k in plats if not k.startswith("_"))
            sys.exit(f"[INPUT_MISSING] 未知平台 {args.platform!r}。可用：{keys}")
        preset = plats[key]
        if not rates_ready(preset) and getattr(args, "commission", None) is None:
            sys.exit("[RATES_UNVERIFIED] "
                     f"{key} 的费率待核实，文件里没有佣金数字。"
                     "请核对 Seller Central 后传入 --commission。不要把待核实当成 0 佣金。")
    if preset is None and getattr(args, "commission", None) is None:
        sys.exit("[INPUT_MISSING] 请传入 --commission。本仓库没有默认佣金。")
    return FeeModel(preset,
                    commission=getattr(args, "commission", None),
                    return_rate=getattr(args, "return_rate", None),
                    ad=getattr(args, "ad", None),
                    tax=getattr(args, "tax", None),
                    target_margin=getattr(args, "target_margin", None),
                    extra_pct=getattr(args, "extra_pct", None),
                    fixed_fee=getattr(args, "fixed_fee", None))


def cmd_calc(args, plats) -> int:
    fm = _model_from_args(args, plats)
    m = fm.margin(args.price, args.cost)
    be = fm.break_even_price(args.cost)
    tp = fm.target_price(args.cost)
    tm_pct = fm.target_margin()
    tm = (tm_pct / 100) if tm_pct is not None else None
    headroom = None
    if tm is not None:
        headroom = round((m["net_rate"] - tm) * args.price, 2) if m["net_rate"] > tm else 0
    out = dict(mode="calc", platform=getattr(args, "platform", None) or "custom",
               currency=getattr(args, "currency", None) or "未标明",
               rates_note="佣金及未单独说明的预留均来自本次参数；未传入的预留按 0，不是平台费率",
               price=args.price, cost=args.cost, **m,
               extra_pct_applied=fm.extra_pct(),
               break_even_price=be, target_price=tp,
               target_margin=tm_pct,
               coupon_headroom=headroom,
               break_even_roas=round(args.price / m["pre_ad_margin"], 2)
               if m["pre_ad_margin"] > 0 else None)
    if fm.ad_pct() > 0 and m["pre_ad_margin"] > 0:
        out["break_even_roas_at_this_ad"] = round(
            args.price / (args.price * fm.ad_pct() / 100), 2)
    # 平台月费/其它固定成本仅提示（不摊入单件）
    if fm.p.get("monthly_fee"):
        out["platform_monthly_fee"] = fm.p["monthly_fee"]
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if not getattr(args, "json", False):
        cur = out["currency"]
        tp_s = "未设目标净利" if tp is None else f"{tp:,.2f} {cur}"
        be_s = "无正的盈亏价" if be is None else f"{be:,.2f} {cur}"
        hd_s = "未设目标净利" if out["coupon_headroom"] is None else f"{out['coupon_headroom']:,.2f} {cur}"
        print(f"\n平台: {out['platform']} ｜ 货币标签 {cur} ｜ 佣金 {m['commission_pct_applied']}% ｜ "
              f"固定费 {m['fixed_fee_applied']:.2f} ｜ 附加 {fm.extra_pct()}% ｜ "
              f"退货 {fm.return_pct()}% ｜ 税 {fm.tax_pct()}% ｜ 广告 {fm.ad_pct()}%")
        print("未传入的预留按 0 参加运算，不是平台官方费率。")
        print(f"净利率 {m['net_rate']:.1%} ｜ 盈亏价 {be_s} ｜ 目标价 {tp_s} ｜ 券余量 {hd_s}")
        for note in fm.p.get("notes", [])[:3]:
            print(f"  ℹ️  {note}")
    return 0


def cmd_matrix(args, plats) -> int:
    try:
        with open(args.file, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        sys.exit(f"[ERROR] 读不了文件：{e}")
    if not rows:
        sys.exit("[ERROR] CSV 里没有数据行")
    header = list(rows[0].keys())
    low = [h.strip().lower() for h in header]

    def col(*cands):
        for c in cands:
            if c in low:
                return header[low.index(c)]
        return None

    c_name = col("角色", "名称", "sku", "role", "name") or header[0]
    c_price = col("售价", "价格", "price")
    c_cost = col("到岸成本", "成本", "cost")
    if not c_price or not c_cost:
        sys.exit(f"[ERROR] 认不出售价/成本列（表头：{header}）")

    fm = _model_from_args(args, plats)
    tm_pct = fm.target_margin()
    tm = (tm_pct / 100) if tm_pct is not None else None
    declared = _known_currency(getattr(args, "currency", None))
    if getattr(args, "currency", None) and declared is None:
        sys.exit("[INPUT_MISSING] --currency 请使用 USD、EUR、GBP、BRL、CNY 或 JPY。"
                 "本脚本只核对货币是否一致，不换汇。")
    results = []
    file_codes: set[str] = set()
    for r in rows:
        name = (r.get(c_name) or "?").strip()
        price, price_ccy = _money(r.get(c_price))
        cost, cost_ccy = _money(r.get(c_cost))
        row_ccy = _same_currency(price_ccy, cost_ccy, declared=declared, where=f"{name} 的")
        if row_ccy:
            if file_codes and row_ccy not in file_codes:
                sys.exit("[INPUT_MISSING] 表里出现了多种货币："
                         f"{'、'.join(sorted(file_codes | {row_ccy}))}。"
                         "请先换算成同一种货币，本脚本不换汇。")
            file_codes.add(row_ccy)
        if price <= 0 or cost <= 0:
            results.append(dict(sku=name, error="价格或成本非正数，跳过"))
            continue
        m = fm.margin(price, cost)
        if tm is None:
            vs, verdict, headroom = None, "未设目标净利", None
        else:
            headroom = round((m["net_rate"] - tm) * price, 2)
            vs = round(m["net_rate"] - tm, 4)
            verdict = ("不低于目标" if m["net_rate"] >= tm else
                       f"低于目标 {(tm - m['net_rate']) * 100:.1f} 个点")
            headroom = max(headroom, 0)
        results.append(dict(
            sku=name, price=price, cost=cost,
            pre_ad_margin=m["pre_ad_margin"], net_rate=m["net_rate"],
            commission_pct_applied=m["commission_pct_applied"],
            fixed_fee_applied=m["fixed_fee_applied"],
            vs_target=vs,
            verdict=verdict,
            coupon_headroom=headroom,
            break_even_price=fm.break_even_price(cost)))

    ladder = []
    sorted_skus = sorted([r for r in results if "price" in r], key=lambda x: x["price"])
    for a, b in zip(sorted_skus, sorted_skus[1:]):
        gap = b["price"] - a["price"]
        ladder.append(dict(frm=a["sku"], to=b["sku"], gap=round(gap, 2),
                           gap_pct=round(gap / a["price"], 4)))

    notes = []
    by_net = sorted([r for r in results if "net_rate" in r], key=lambda x: -x["net_rate"])
    if len(by_net) >= 2 and by_net[0]["price"] < by_net[-1]["price"]:
        notes.append("最高净利率不是最高价那一行。若不是有意设计，请核对成本。")
    if tm is not None:
        under = [r["sku"] for r in results if "net_rate" in r and r["net_rate"] < tm]
        if under:
            notes.append(f"低于调用方目标 {fm.target_margin():g}% 的行：{'、'.join(under)}")
    else:
        notes.append("未传 --target-margin，不做达标比较。")

    out = dict(mode="matrix", platform=getattr(args, "platform", None) or "custom",
               currency=getattr(args, "currency", None) or "未标明",
               target_margin=fm.target_margin(), skus=results,
               price_ladder=ladder, notes=notes)
    print(json.dumps(out, ensure_ascii=False, indent=2))

    if not args.json:
        plat_label = (fm.p.get("label") or out["platform"])
        goal = "未设" if fm.target_margin() is None else f"{fm.target_margin():g}%"
        print(f"\n平台: {plat_label} ｜ 货币标签 {out['currency']} ｜ 目标净利 {goal} ｜ "
              f"广告 {fm.ad_pct()}% ｜ 退货 {fm.return_pct()}% ｜ "
              f"税 {fm.tax_pct()}% ｜ 附加 {fm.extra_pct()}%\n"
              "未传入的预留按 0，不是平台费率。\n")
        print(f"{'SKU':<30}{'售价':>10}{'佣金%':>7}{'固定费':>8}{'净利率':>8}{'对目标':>9}{'券余量':>9}")
        for r in results:
            if "error" in r:
                print(f"{r['sku']:<30}  ⚠️ {r['error']}")
                continue
            if r["vs_target"] is None:
                mark = "—"
                vs_s = "—"
                hd_s = "—"
            else:
                mark = "不低于目标" if r["vs_target"] >= 0 else "低于目标"
                vs_s = f"{r['vs_target']:+.1%}"
                hd_s = f"{r['coupon_headroom']:,.2f}"
            print(f"{r['sku']:<30}{r['price']:>10,.2f}{r['commission_pct_applied']:>7g}"
                  f"{r['fixed_fee_applied']:>8,.2f}{r['net_rate']:>8.1%}"
                  f"{vs_s:>9}{hd_s:>9} {mark}")
        print()
        for l in ladder:
            print(f"  阶梯 {l['frm']} → {l['to']}：差 {l['gap']:,.2f}（{l['gap_pct']:.0%}）")
        for n in notes:
            print(f"  ℹ️  {n}")
        for note in fm.p.get("notes", [])[:2]:
            print(f"  📌 {note}")
    return 0


def cmd_list_platforms(plats) -> int:
    print(f"{'key':<16}{'状态':<10}{'含费率数字':<12}说明")
    print("-" * 72)
    for k, v in plats.items():
        if k.startswith("_"):
            continue
        included = "否" if v.get("rates_included") is False or not rates_ready(v) else "是"
        print(f"{k:<16}{v.get('status', '-'):<10}{included:<12}{v.get('label', k)}")
    note = plats.get("_meta", {}).get("note", "")
    print("\n" + note)
    print("显式参数（--commission 等）永远优先；待核实预设不能当成 0 佣金。")
    return 0


def _currency_codes(raw: str) -> set[str]:
    return {_CURRENCY_CODE.get(tok.upper(), _CURRENCY_CODE.get(tok, tok))
            for tok in _CURRENCY_RE.findall(raw)}


def _known_currency(label: str | None) -> str | None:
    if not label:
        return None
    token = label.strip()
    if not token or token in ("未标明", "金额"):
        return None
    return _CURRENCY_CODE.get(token.upper(), _CURRENCY_CODE.get(token))


def _parse_plain_amount(s: str) -> float:
    """s 只剩数字和分隔符。整数部分为 0 时，逗号或点后面都是小数（0,125 / 0.125）。"""
    if not re.fullmatch(r"\d+(?:[.,]\d+)*", s):
        raise ValueError(s)
    if "," in s and "." in s:
        body = (s.replace(".", "").replace(",", ".")
                if s.rfind(",") > s.rfind(".") else s.replace(",", ""))
        return float(body)
    if "," not in s and "." not in s:
        return float(s)
    sep = "," if "," in s else "."
    head, *tails = s.split(sep)
    if not all(part.isdigit() for part in tails):
        raise ValueError(s)
    if len(tails) == 1 and int(head) == 0:
        return float(f"0.{tails[0]}")
    if len(tails) == 1 and len(tails[0]) in (1, 2):
        return float(f"{int(head)}.{tails[0]}")
    if all(len(part) == 3 for part in tails):
        return float(head + "".join(tails))
    if (len(tails) > 1 and all(len(part) == 3 for part in tails[:-1])
            and len(tails[-1]) in (1, 2)):
        return float(head + "".join(tails[:-1]) + "." + tails[-1])
    raise ValueError(s)


def _money(v, default=0.0):
    """返回 (金额, 货币代码或 None)。空单元格金额为 default。不换汇。"""
    if v is None:
        return default, None
    raw = str(v).strip()
    if raw in ("", "-", "—", "暂无", "N/A", "nan"):
        return default, None
    codes = _currency_codes(raw)
    if len(codes) > 1:
        sys.exit(f"[INPUT_MISSING] 同一格里有多种货币 {sorted(codes)}：{raw!r}。请先换算成一种货币。")
    neg = raw.lstrip().startswith(("-", "−"))
    s = _CURRENCY_RE.sub("", raw).replace("%", "")
    s = re.sub(r"\s+", "", s).lstrip("+-−")
    if s in ("", "-", "—"):
        return default, (next(iter(codes)) if codes else None)
    try:
        value = _parse_plain_amount(s)
    except ValueError:
        sys.exit(f"[INPUT_MISSING] 无法把金额解析成数字：{raw!r}")
    return ((-value if neg else value), (next(iter(codes)) if codes else None))


def _same_currency(*codes, declared=None, where=""):
    explicit = {c for c in codes if c}
    if declared and explicit and explicit != {declared}:
        sys.exit("[INPUT_MISSING] "
                 f"{where}单元格货币是 {'、'.join(sorted(explicit))}，"
                 f"声明的货币是 {declared}。请先换算成同一种货币，本脚本不换汇。")
    if len(explicit) > 1:
        sys.exit("[INPUT_MISSING] "
                 f"{where}出现了多种货币：{'、'.join(sorted(explicit))}。"
                 "请先换算成同一种货币，本脚本不换汇。")
    return next(iter(explicit), None) if len(explicit) == 1 else declared


def _num(v, default=0.0, kind="dec"):
    """金额或计数。空单元格用 default。写了但不是数字则退出，不当成 0。"""
    if kind == "int":
        if v is None:
            return default
        raw = str(v).strip()
        if raw in ("", "-", "—", "暂无", "N/A", "nan"):
            return default
        neg = raw.lstrip().startswith(("-", "−"))
        digits = "".join(ch for ch in raw if ch.isdigit())
        if not digits:
            sys.exit(f"[INPUT_MISSING] 无法把计数字段解析成整数：{raw!r}")
        return (-1 if neg else 1) * int(digits)
    value, _code = _money(v, default)
    return value


def _add_common(p):
    p.add_argument("--platform", help="站点键（--list-platforms）。当前预设不含费率数字")
    p.add_argument("--currency", default=None, help="货币标签，只用于打印，不换算")
    p.add_argument("--commission", type=float, default=None, help="佣金 %%。必填，除非预设里真有数字")
    p.add_argument("--return", dest="return_rate", type=float, default=None, help="退货预留 %%。不传则本次按 0")
    p.add_argument("--ad", type=float, default=None, help="广告预留占售价 %%。不传则本次按 0")
    p.add_argument("--tax", type=float, default=None, help="税 %%。不传则本次按 0，不是 VAT 规定")
    p.add_argument("--extra-pct", type=float, default=None, help="其他附加 %%。不传则本次按 0")
    p.add_argument("--fixed-fee", type=float, default=None, help="按件固定费（金额）。不传则本次按 0")
    p.add_argument("--target-margin", type=float, default=None, help="目标净利 %%。不传则不算目标价")


def main():
    plats = load_platforms()
    ap = argparse.ArgumentParser(description="SKU 定价算术（只算不定价）")
    ap.add_argument("--list-platforms", action="store_true", help="列出全部平台费率预设")
    sub = ap.add_subparsers(dest="cmd")

    c = sub.add_parser("calc", help="单 SKU：净利率 / 盈亏价 / 目标价 / 优惠券余量")
    _add_common(c)
    c.add_argument("--cost", type=float, required=True, help="到岸成本（调用方货币）")
    c.add_argument("--price", type=float, required=True, help="售价（调用方货币）")
    c.add_argument("--json", action="store_true", help="仅输出 JSON")

    m = sub.add_parser("matrix", help="多 SKU 矩阵：读 CSV 出净利率表 + 价格阶梯 + 券余量")
    _add_common(m)
    m.add_argument("--file", required=True)
    m.add_argument("--json", action="store_true")

    args = ap.parse_args()
    if args.list_platforms:
        sys.exit(cmd_list_platforms(plats))
    if not args.cmd:
        ap.print_help()
        sys.exit(2)
    sys.exit(cmd_calc(args, plats) if args.cmd == "calc" else cmd_matrix(args, plats))


if __name__ == "__main__":
    main()
