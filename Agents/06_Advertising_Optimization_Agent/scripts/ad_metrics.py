#!/usr/bin/env python3
"""广告盈亏线算术 —— 只算，不猜，不执行。

  python ad_metrics.py calc --price 40 --product-cost 18 --commission 15 --cvr 10 --target-acos 25
  python ad_metrics.py diagnose --file ../examples/sample-ad-report.csv \
      --price 40 --product-cost 18 --commission 15 --target-acos 25

佣金必须显式传入。amazon_us / amazon_eu 预设没有数字，不能当成 0。
--cvr 的单位是百分数（10 表示 10%）。
--target-acos 是调用方目标，不是官方基准。诊断命令不设默认目标。
--min-impressions 默认 1000，只是数据量开关，不是平台冷启动规则。

  广告前贡献 = 售价 − 产品成本 − 头程 − 尾程 − 售价×(佣金%+退货%+税%+附加%) − 按件固定费
  盈亏线 ACoS = 广告前贡献 ÷ 售价
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

# 与 02 模块共用同一份平台费率预设（单一事实来源）
PLATFORM_FEES = (Path(__file__).resolve().parents[2]
                 / "02_Product_Strategy_Agent" / "scripts" / "platform_fees.json")


def _tier_lookup(price, tiers, default=0.0):
    for t in tiers or []:
        mx = t.get("max")
        if mx is None or price <= float(mx):
            return float(t.get("pct", t.get("fee", default)))
    return default


def _rates_ready(preset) -> bool:
    if not preset:
        return False
    if preset.get("rates_included") is False or preset.get("status") == "待核实":
        return False
    return "commission_pct" in preset or bool(preset.get("commission_tiers"))


def _resolve_fees(args):
    """显式参数优先。待核实预设不能当成 0 佣金。"""
    preset = None
    if getattr(args, "platform", None):
        try:
            plats = json.loads(PLATFORM_FEES.read_text(encoding="utf-8"))
        except OSError:
            sys.exit(f"[ERROR] 读不到平台费率表：{PLATFORM_FEES}")
        key = args.platform.strip()
        if key not in plats or key.startswith("_"):
            keys = "、".join(k for k in plats if not k.startswith("_"))
            sys.exit(f"[INPUT_MISSING] 未知平台 {args.platform!r}。可用：{keys}")
        preset = plats[key]

    if args.commission is not None:
        comm = float(args.commission)
    elif _rates_ready(preset):
        if "commission_pct" in preset:
            comm = float(preset["commission_pct"])
        else:
            comm = _tier_lookup(args.price, preset.get("commission_tiers"))
    else:
        sys.exit("[RATES_UNVERIFIED] 请传入 --commission。站点预设没有已核实费率，不能按 0 佣金计算。")

    def scalar(flag, pkey):
        if flag is not None:
            return float(flag)
        if _rates_ready(preset) and preset and pkey in preset and preset[pkey] is not None:
            return float(preset[pkey])
        return 0.0

    if getattr(args, "fixed_fee", None) is not None:
        ff = float(args.fixed_fee)
    elif _rates_ready(preset) and preset and preset.get("fixed_fee_tiers"):
        ff = _tier_lookup(args.price, preset["fixed_fee_tiers"])
    else:
        ff = 0.0

    label = (preset or {}).get("label", getattr(args, "platform", None) or "custom")
    return comm, scalar(args.return_rate, "return_pct"), scalar(args.tax, "tax_pct"), \
        scalar(getattr(args, "extra_pct", None), "extra_pct"), ff, label

# 列名自动映射（中 / 英 / 葡）
COLUMN_MAP = {
    "name":    ["广告名称", "广告组", "计划名称", "campaign", "name", "ad_group"],
    "impressions": ["曝光量", "曝光", "展示量", "impressions", "imps"],
    "clicks":  ["点击量", "点击数", "点击", "clicks"],
    "spend":   ["花费", "消耗", "花费金额", "spend", "cost"],
    "orders":  ["订单数", "订单", "成交订单", "orders", "conversions"],
    "gmv":     ["销售额", "成交金额", "广告销售额", "gmv", "sales"],
}


def _currency_codes(raw: str) -> set[str]:
    return {_CURRENCY_CODE.get(tok.upper(), _CURRENCY_CODE.get(tok, tok))
            for tok in _CURRENCY_RE.findall(raw)}


def _parse_plain_amount(s: str) -> float:
    """整数部分为 0 时，后面全部是小数（0,125 / 0.125），不当成千分位。"""
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
    """返回 (金额, 货币代码或 None)。不换汇。空单元格用 default。"""
    if v is None:
        return default, None
    raw = str(v).strip()
    if raw in ("", "-", "—", "暂无", "N/A", "nan", "NaN"):
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
        sys.exit(f"[INPUT_MISSING] 无法把金额解析成数字：{raw!r}。空着可以，写了就必须是金额。")
    return ((-value if neg else value), (next(iter(codes)) if codes else None))


def _num(v, default=0.0, kind="dec"):
    """金额或计数。空单元格用 default。写了但不是数字则退出，不当成 0。"""
    if kind == "int":
        if v is None:
            return default
        raw = str(v).strip()
        if raw in ("", "-", "—", "暂无", "N/A", "nan", "NaN"):
            return default
        neg = raw.lstrip().startswith(("-", "−"))
        digits = "".join(ch for ch in re.sub(r"\s+", "", raw) if ch.isdigit())
        if not digits:
            sys.exit(f"[INPUT_MISSING] 无法把计数字段解析成整数：{raw!r}")
        return (-1 if neg else 1) * int(digits)
    value, _code = _money(v, default)
    return value


def _pick(header, kind):
    low = [h.strip().lower() for h in header]
    for cand in COLUMN_MAP[kind]:
        if cand.lower() in low:
            return header[low.index(cand.lower())]
    return None


def cost_model(args):
    price = args.price
    comm, ret, tax, extra, ff, plat_label = _resolve_fees(args)
    contrib = (price - args.product_cost - args.first_leg - args.shipping
               - price * (comm + ret + tax + extra) / 100 - ff)
    be_acos = contrib / price if price else 0
    return dict(price=price, platform=plat_label,
                commission_pct_applied=comm, fixed_fee_applied=round(ff, 2),
                extra_pct_applied=extra,
                pre_ad_contribution=round(contrib, 2),
                break_even_acos=round(be_acos, 4),
                break_even_roas=round(1 / be_acos, 2) if be_acos > 0 else None)


def cmd_calc(args):
    m = cost_model(args)
    out = dict(mode="calc", **m)
    if args.target_acos:
        ta = args.target_acos / 100
        out["target_acos"] = args.target_acos
        out["target_roas"] = round(1 / ta, 2)
        if args.cvr:
            out["affordable_cpc"] = round(m["price"] * (args.cvr / 100) * ta, 2)
            out["affordable_cpc_note"] = "售价 × 转化率 × 目标ACoS —— 出价高于它即亏损加速"
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def _grade(row, m, args, be_roas, target_roas):
    """确定性分级：P0 止血 / P1 改善 / P2 放量 / INFO 数据不足。返回 (级别, 动作列表)。"""
    acts = []
    name = row["name"]
    imp, clk, spend, orders = row["impressions"], row["clicks"], row["spend"], row["orders"]
    gmv = row["gmv"] if row["gmv"] else orders * m["price"]
    ctr = clk / imp if imp else 0
    cvr = orders / clk if clk else 0
    cpc = spend / clk if clk else 0
    roas = gmv / spend if spend else None
    affordable_cpc = m["price"] * cvr * (args.target_acos / 100) if cvr else None

    # 0) 数据充分性 —— 数据不足一律不动（攒数据，过早上手段=噪声驱动）
    if imp < args.min_impressions:
        return "INFO", [f"曝光 {imp:,.0f} < {args.min_impressions:,}，数据不足，本轮不动，继续攒数据"], dict(
            ctr=ctr, cvr=cvr, cpc=cpc, roas=roas, affordable_cpc=affordable_cpc, gmv=gmv)
    if not spend:
        return "INFO", ["无花费，本轮不动"], dict(ctr=ctr, cvr=cvr, cpc=cpc, roas=roas,
                                                affordable_cpc=affordable_cpc, gmv=gmv)

    def cpc_line():
        if affordable_cpc is None:
            return f"当前 CPC {cpc:.2f}。这次算不出可承受 CPC（转化率为 0 或盈亏线非正）。"
        return (f"按本次费率，可承受 CPC 约 {affordable_cpc:.2f}，当前 {cpc:.2f}。"
                "是否改出价由人决定，脚本不改后台。")

    if orders == 0 and clk >= 30:
        acts.append(f"点击 {clk:,.0f} 且订单为 0。建议人核对页面与价格。")
        acts.append(cpc_line())
        return "P0", acts, dict(ctr=ctr, cvr=cvr, cpc=cpc, roas=roas,
                                affordable_cpc=affordable_cpc, gmv=gmv)

    if roas is None or be_roas is None:
        return "INFO", ["花费或盈亏线不足，无法分级"], dict(
            ctr=ctr, cvr=cvr, cpc=cpc, roas=roas,
            affordable_cpc=affordable_cpc, gmv=gmv)
    if roas < 0.5 * be_roas:
        acts.append(f"ROAS {roas:.2f} 低于盈亏线 {be_roas:.2f} 的一半。建议人先看是否止血。")
        acts.append(cpc_line())
    elif roas < be_roas:
        acts.append(f"ROAS {roas:.2f} 低于盈亏线 {be_roas:.2f}。")
        acts.append(cpc_line())
    elif target_roas is not None and roas < target_roas:
        acts.append(f"ROAS {roas:.2f} 在盈亏线与调用方目标 {target_roas:.2f} 之间。")
        acts.append("脚本不建议自动加预算。")
    else:
        acts.append(f"ROAS {roas:.2f} 不低于调用方目标 {target_roas:.2f}。是否放量由人决定。")
        acts.append("脚本不给出加预算的幅度。")

    acts.append("本轮建议只处理上面这一条。没有写进建议的部分保持不动。")
    return ("P0" if roas < 0.5 * be_roas else
            "P2" if target_roas is not None and roas >= target_roas else "P1"), acts, dict(
        ctr=ctr, cvr=cvr, cpc=cpc, roas=roas, affordable_cpc=affordable_cpc, gmv=gmv)


def cmd_diagnose(args):
    m = cost_model(args)
    be_roas = m["break_even_roas"]
    target_roas = 1 / (args.target_acos / 100) if args.target_acos else be_roas * 1.5

    try:
        with open(args.file, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except OSError as e:
        sys.exit(f"[ERROR] 读不了文件：{e}")
    if not rows:
        sys.exit("[ERROR] CSV 里没有数据行")

    header = list(rows[0].keys())
    col = {k: _pick(header, k) for k in COLUMN_MAP}
    missing = [k for k, v in col.items() if v is None and k != "gmv"]
    if missing:
        sys.exit(f"[ERROR] 认不出这些列（可用映射见 references/metrics.md）：{missing}")

    results, totals = [], dict(spend=0.0, gmv=0.0, orders=0.0, clicks=0.0, impressions=0.0)
    file_codes: set[str] = set()
    for r in rows:
        name = (r.get(col["name"]) or "?").strip()
        spend, spend_ccy = _money(r.get(col["spend"]))
        gmv, gmv_ccy = _money(r.get(col["gmv"])) if col["gmv"] else (0.0, None)
        codes = {c for c in (spend_ccy, gmv_ccy) if c}
        if len(codes) > 1 or (file_codes and codes and codes != file_codes):
            sys.exit("[INPUT_MISSING] "
                     f"{name} 的花费和销售额不是同一种货币："
                     f"{'、'.join(sorted(file_codes | codes))}。"
                     "请先换算，本脚本不换汇。")
        file_codes |= codes
        row = dict(name=name,
                   impressions=_num(r.get(col["impressions"]), kind="int"),
                   clicks=_num(r.get(col["clicks"]), kind="int"),
                   spend=spend,
                   orders=_num(r.get(col["orders"]), kind="int"),
                   gmv=gmv)
        grade, acts, met = _grade(row, m, args, be_roas, target_roas)
        results.append(dict(campaign=row["name"], grade=grade,
                            impressions=row["impressions"], clicks=row["clicks"],
                            spend=round(row["spend"], 2), orders=row["orders"],
                            **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in met.items()},
                            actions=acts))
        for k in totals:
            totals[k] += row[k] if k != "gmv" else (row["gmv"] or row["orders"] * m["price"])

    total_roas = totals["gmv"] / totals["spend"] if totals["spend"] else None
    out = dict(mode="diagnose", cost_model=m, target_acos=args.target_acos,
               target_roas=target_roas, total=dict(
                   campaigns=len(results), **{k: round(v, 2) for k, v in totals.items()},
                   roas=round(total_roas, 2) if total_roas else None,
                   net_contribution=round(m["pre_ad_contribution"] / m["price"] * totals["gmv"] - totals["spend"], 2)),
               campaigns=sorted(results, key=lambda x: (x["grade"], -(x["roas"] or 0))))
    print(json.dumps(out, ensure_ascii=False, indent=2))

    if not args.json:
        icon = {"P0": "🔴", "P1": "🟡", "P2": "🟢", "INFO": "⚪"}
        print(f"\n盈亏线 ROAS {be_roas} ｜ 目标 ROAS {target_roas} ｜ "
              f"整体 ROAS {out['total']['roas']} ｜ 整体净贡献 {out['total']['net_contribution']}\n")
        for c in out["campaigns"]:
            print(f"{icon[c['grade']]} [{c['grade']}] {c['campaign']}  "
                  f"ROAS {c['roas'] if c['roas'] else '-'}  花费 {c['spend']}  订单 {c['orders']:g}")
            for a in c["actions"]:
                print(f"     · {a}")
            print()
    return 0


def main():
    ap = argparse.ArgumentParser(description="广告决策层算术脚本（只算不执行）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("calc", help="由成本结构算盈亏线 / 可承受 CPC")
    c.add_argument("--price", type=float, required=True, help="售价")
    c.add_argument("--product-cost", type=float, required=True)
    c.add_argument("--shipping", type=float, default=0, help="尾程，金额")
    c.add_argument("--first-leg", type=float, default=0, help="头程，金额")
    c.add_argument("--platform", help="站点键。当前预设不含费率")
    c.add_argument("--commission", type=float, default=None, help="佣金 %%，必填")
    c.add_argument("--return", dest="return_rate", type=float, default=None, help="退货预留 %%")
    c.add_argument("--tax", type=float, default=None, help="税 %%。不传则本次按 0")
    c.add_argument("--extra-pct", type=float, default=None, help="其他附加 %%")
    c.add_argument("--fixed-fee", type=float, default=None, help="按件固定费")
    c.add_argument("--target-acos", type=float, help="调用方的目标 ACoS %%")
    c.add_argument("--cvr", type=float, help="转化率 %%，10 表示 10%%")

    d = sub.add_parser("diagnose", help="读广告导出 CSV → 指标 + P0/P1/P2 分级动作")
    d.add_argument("--file", required=True)
    d.add_argument("--price", type=float, required=True)
    d.add_argument("--product-cost", type=float, required=True)
    d.add_argument("--shipping", type=float, default=0)
    d.add_argument("--first-leg", type=float, default=0)
    d.add_argument("--platform", help="站点键。当前预设不含费率")
    d.add_argument("--commission", type=float, default=None, help="佣金 %%，必填")
    d.add_argument("--return", dest="return_rate", type=float, default=None)
    d.add_argument("--tax", type=float, default=None)
    d.add_argument("--extra-pct", type=float, default=None)
    d.add_argument("--fixed-fee", type=float, default=None)
    d.add_argument("--target-acos", type=float, required=True, help="调用方的目标 ACoS %%")
    d.add_argument("--min-impressions", type=int, default=1000,
                   help="数据量开关，默认 1000。不是平台官方规则")
    d.add_argument("--json", action="store_true")

    args = ap.parse_args()
    sys.exit(cmd_calc(args) if args.cmd == "calc" else cmd_diagnose(args))


if __name__ == "__main__":
    main()
