#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic GST calculator.

Pure stdlib. No floats anywhere - every money value is a `decimal.Decimal`
quantised with ROUND_HALF_UP. The same inputs always produce byte-identical
output, on any platform, in any Python 3.x.

What it decides, and on what authority
--------------------------------------
1. Is the supply intra-State/UT or inter-State?
       Same supplier and place-of-supply code  -> intra   (CGST + SGST/UTGST)
       Different codes                          -> inter   (IGST)
2. If intra, is the state half SGST or UTGST?
       This is the part most implementations get wrong. It is NOT
       "state -> SGST, union territory -> UTGST".

       The UTGST Act 2017 s.2(8) defines "Union territory" as Andaman and
       Nicobar Islands, Lakshadweep, Dadra and Nagar Haveli and Daman and Diu,
       Ladakh, Chandigarh and other territory - and *excludes* Delhi and
       Puducherry, which have their own legislatures and their own SGST Acts.
       Jammu & Kashmir likewise became a UT *with* legislature in Oct 2019 and
       levies SGST.

       So: 28 States + Delhi + Puducherry + J&K  -> SGST   (31 codes)
           the 5 UTs without legislature          -> UTGST  (+ Other Territory)

Rounding policy (stated, not implied)
-------------------------------------
- Each tax component is computed independently from the taxable value at its
  own rate, then quantised to 2 dp with ROUND_HALF_UP.
- CGST and SGST/UTGST are each computed at rate/2 - they are not derived by
  halving a rounded total.
- Consequence, surfaced as `split_residue`: for some values an intra-State
  total can differ from the inter-State total by 0.01, because two independent
  roundings are not the same as one. This is inherent to per-component
  rounding and is what accounting systems do; it is reported, never hidden.
- `--round-total` additionally rounds the invoice total to the nearest rupee
  per CGST Act s.170. Off by default.

Usage
-----
    python scripts/gst_calc.py --value 10000 --rate 18 --from 27 --to 27
    python scripts/gst_calc.py --value 11800 --rate 18 --from 27 --to 27 --inclusive
    python scripts/gst_calc.py --value 10000 --rate 18 --from 04 --to 04   # UTGST
    python scripts/gst_calc.py --code HSN_6109 --value 5000 --from 27 --to 24
    python scripts/gst_calc.py --selftest
    python scripts/gst_calc.py --list-states
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 28

MONEY = Decimal("0.01")
RUPEE = Decimal("1")

STATE = "state"                    # levies SGST
UT_LEG = "ut_with_legislature"     # has its own legislature -> levies SGST
UT_NOLEG = "ut_without_legislature"  # levies UTGST
DEPRECATED = "deprecated"
SPECIAL = "special"

# GST state codes = first two digits of a GSTIN.
STATE_CODES = {
    "01": ("Jammu and Kashmir", UT_LEG),
    "02": ("Himachal Pradesh", STATE),
    "03": ("Punjab", STATE),
    "04": ("Chandigarh", UT_NOLEG),
    "05": ("Uttarakhand", STATE),
    "06": ("Haryana", STATE),
    "07": ("Delhi", UT_LEG),
    "08": ("Rajasthan", STATE),
    "09": ("Uttar Pradesh", STATE),
    "10": ("Bihar", STATE),
    "11": ("Sikkim", STATE),
    "12": ("Arunachal Pradesh", STATE),
    "13": ("Nagaland", STATE),
    "14": ("Manipur", STATE),
    "15": ("Mizoram", STATE),
    "16": ("Tripura", STATE),
    "17": ("Meghalaya", STATE),
    "18": ("Assam", STATE),
    "19": ("West Bengal", STATE),
    "20": ("Jharkhand", STATE),
    "21": ("Odisha", STATE),
    "22": ("Chhattisgarh", STATE),
    "23": ("Madhya Pradesh", STATE),
    "24": ("Gujarat", STATE),
    "25": ("Daman and Diu (merged into 26 on 26-01-2020)", DEPRECATED),
    "26": ("Dadra and Nagar Haveli and Daman and Diu", UT_NOLEG),
    "27": ("Maharashtra", STATE),
    "28": ("Andhra Pradesh (pre-bifurcation; now 37)", DEPRECATED),
    "29": ("Karnataka", STATE),
    "30": ("Goa", STATE),
    "31": ("Lakshadweep", UT_NOLEG),
    "32": ("Kerala", STATE),
    "33": ("Tamil Nadu", STATE),
    "34": ("Puducherry", UT_LEG),
    "35": ("Andaman and Nicobar Islands", UT_NOLEG),
    "36": ("Telangana", STATE),
    "37": ("Andhra Pradesh", STATE),
    "38": ("Ladakh", UT_NOLEG),
    "97": ("Other Territory", UT_NOLEG),
    "99": ("Centre Jurisdiction", SPECIAL),
}


class GstError(ValueError):
    pass


# ---------------------------------------------------------------------------
# Jurisdiction rules
# ---------------------------------------------------------------------------

def normalise_code(code):
    c = str(code).strip()
    if c.isdigit() and len(c) == 1:
        c = "0" + c
    if len(c) > 2 and c[:2].isdigit():   # a full GSTIN was passed
        c = c[:2]
    if c not in STATE_CODES:
        raise GstError("unknown GST state code %r (expected one of %s)"
                       % (code, ", ".join(sorted(STATE_CODES))))
    kind = STATE_CODES[c][1]
    if kind == DEPRECATED:
        raise GstError("GST state code %s is deprecated: %s"
                       % (c, STATE_CODES[c][0]))
    return c


def state_tax_label(code):
    """SGST or UTGST for the given code. This is the rule most code gets wrong."""
    kind = STATE_CODES[normalise_code(code)][1]
    if kind == UT_NOLEG:
        return "UTGST"
    return "SGST"


def supply_type(supplier_code, pos_code):
    """'intra' -> CGST + SGST/UTGST ; 'inter' -> IGST."""
    return "intra" if normalise_code(supplier_code) == normalise_code(pos_code) else "inter"


# ---------------------------------------------------------------------------
# Money
# ---------------------------------------------------------------------------

def _dec(v, what):
    try:
        d = Decimal(str(v))
    except Exception:
        raise GstError("%s is not a number: %r" % (what, v))
    if d.is_nan() or d.is_infinite():
        raise GstError("%s is not finite: %r" % (what, v))
    return d


def q(d, exp=MONEY):
    return d.quantize(exp, rounding=ROUND_HALF_UP)


def compute(taxable_value, gst_rate, supplier_code, pos_code,
            cess_rate=0, inclusive=False, round_total=False):
    """Return a full, deterministic GST breakdown.

    taxable_value : amount. If `inclusive` it is treated as GST-inclusive and
                    the taxable value is back-calculated.
    gst_rate      : total GST percentage (e.g. 18 for 18%). May be None -> no tax.
    supplier_code : GST state code of the supplier
    pos_code      : GST state code of the place of supply
    """
    if gst_rate is None:
        raise GstError("gst_rate is None - this code has no resolved rate, so "
                       "no tax can be computed. Do not assume zero.")

    amount = _dec(taxable_value, "value")
    if amount < 0:
        raise GstError("value must not be negative")
    rate = _dec(gst_rate, "rate")
    if rate < 0:
        raise GstError("rate must not be negative")
    cess = _dec(cess_rate or 0, "cess_rate")

    sup = normalise_code(supplier_code)
    pos = normalise_code(pos_code)
    kind = supply_type(sup, pos)
    label = state_tax_label(pos)

    hundred = Decimal(100)
    if inclusive:
        # back out the taxable value; cess rides on the same base
        base = amount / (hundred + rate + cess) * hundred
        base = q(base)
    else:
        base = q(amount)

    half = rate / Decimal(2)

    if kind == "intra":
        cgst = q(base * half / hundred)
        sgst = q(base * half / hundred)
        igst = Decimal("0.00")
    else:
        cgst = Decimal("0.00")
        sgst = Decimal("0.00")
        igst = q(base * rate / hundred)

    cess_amt = q(base * cess / hundred) if cess else Decimal("0.00")
    tax_total = cgst + sgst + igst + cess_amt
    invoice_total = base + tax_total

    # what the other supply type would have produced, to expose the residue
    counterpart = q(base * rate / hundred) if kind == "intra" else \
        q(base * half / hundred) * 2
    residue = (cgst + sgst + igst) - counterpart

    if round_total:
        invoice_total = q(invoice_total, RUPEE)

    return {
        "taxable_value": base,
        "gst_rate": rate,
        "supply_type": kind,
        "supplier": {"code": sup, "name": STATE_CODES[sup][0],
                     "kind": STATE_CODES[sup][1]},
        "place_of_supply": {"code": pos, "name": STATE_CODES[pos][0],
                            "kind": STATE_CODES[pos][1]},
        "state_tax_label": label,
        "components": [
            {"tax": "CGST", "rate": half if kind == "intra" else Decimal(0), "amount": cgst},
            {"tax": label, "rate": half if kind == "intra" else Decimal(0), "amount": sgst},
            {"tax": "IGST", "rate": rate if kind == "inter" else Decimal(0), "amount": igst},
        ] + ([{"tax": "Cess", "rate": cess, "amount": cess_amt}] if cess else []),
        "cgst": cgst,
        "state_tax": sgst,
        "igst": igst,
        "cess": cess_amt,
        "tax_total": tax_total,
        "invoice_total": invoice_total,
        "split_residue": residue,
        "total_rounded_to_rupee": bool(round_total),
    }


def as_json(res):
    def conv(o):
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, list):
            return [conv(x) for x in o]
        return o
    return json.dumps(conv(res), ensure_ascii=False, indent=2)


def as_text(res):
    L = []
    L.append("Taxable value      %12s" % fmt(res["taxable_value"]))
    L.append("GST rate           %12s%%" % strip(res["gst_rate"]))
    L.append("Supplier           %s (%s)" % (res["supplier"]["name"], res["supplier"]["code"]))
    L.append("Place of supply    %s (%s)" % (res["place_of_supply"]["name"],
                                             res["place_of_supply"]["code"]))
    L.append("Supply type        %s" % (
        "Intra-State / Intra-UT" if res["supply_type"] == "intra" else "Inter-State"))
    L.append("")
    for c in res["components"]:
        if c["amount"] == 0 and c["tax"] != "Cess":
            continue
        L.append("  %-6s @ %5s%%   %12s" % (c["tax"], strip(c["rate"]), fmt(c["amount"])))
    L.append("  %-16s %12s" % ("Total tax", fmt(res["tax_total"])))
    L.append("  %-16s %12s" % ("Invoice total", fmt(res["invoice_total"])))
    if res["split_residue"] != 0:
        L.append("")
        L.append("  note: %s vs the other supply type differs by %s due to per-component"
                 % ("this split", fmt(res["split_residue"])))
        L.append("        rounding (two roundings vs one). Expected, not an error.")
    return "\n".join(L)


def fmt(d):
    return "{:,.2f}".format(d)


def strip(d):
    s = str(d.normalize()) if isinstance(d, Decimal) else str(d)
    return s if "E" not in s else format(d, "f")


# ---------------------------------------------------------------------------
# Self-test - the determinism guarantee, checkable
# ---------------------------------------------------------------------------

VECTORS = [
    # value,   rate, from, to,  incl,  expect cgst, state, igst, label
    ("10000",   18, "27", "27", False, "900.00", "900.00",   "0.00", "SGST"),
    ("10000",   18, "27", "24", False,   "0.00",   "0.00","1800.00", "SGST"),
    # the user's point: a UT without legislature levies UTGST, not SGST
    ("10000",   18, "04", "04", False, "900.00", "900.00",   "0.00", "UTGST"),
    ("10000",   18, "35", "35", False, "900.00", "900.00",   "0.00", "UTGST"),
    ("10000",   18, "38", "38", False, "900.00", "900.00",   "0.00", "UTGST"),
    # the subtlety: UTs *with* legislature levy SGST
    ("10000",   18, "07", "07", False, "900.00", "900.00",   "0.00", "SGST"),
    ("10000",   18, "34", "34", False, "900.00", "900.00",   "0.00", "SGST"),
    ("10000",   18, "01", "01", False, "900.00", "900.00",   "0.00", "SGST"),
    # UT to a different UT is still inter-State
    ("10000",   18, "04", "35", False,   "0.00",   "0.00","1800.00", "UTGST"),
    # 5% splits to 2.5 / 2.5 with no rounding loss
    ( "1000",    5, "29", "29", False,  "25.00",  "25.00",   "0.00", "SGST"),
    # 40% slab
    ( "1000",   40, "29", "29", False, "200.00", "200.00",   "0.00", "SGST"),
    # zero-rated / nil
    ( "1000",    0, "29", "29", False,   "0.00",   "0.00",   "0.00", "SGST"),
    # inclusive pricing backs out to a clean base
    ("11800",   18, "27", "27", True,  "900.00", "900.00",   "0.00", "SGST"),
    ( "1050",    5, "27", "24", True,    "0.00",   "0.00",  "50.00", "SGST"),
    # half-paise case - each component rounds independently
    ("333.33",   5, "27", "27", False,   "8.33",   "8.33",   "0.00", "SGST"),
]


def selftest():
    failures = []
    for i, (val, rate, frm, to, incl, e_c, e_s, e_i, e_lbl) in enumerate(VECTORS, 1):
        r = compute(val, rate, frm, to, inclusive=incl)
        got = (str(r["cgst"]), str(r["state_tax"]), str(r["igst"]), r["state_tax_label"])
        exp = (e_c, e_s, e_i, e_lbl)
        if got != exp:
            failures.append("  vector %d (%s @ %s%% %s->%s%s)\n    expected %s\n    got      %s"
                            % (i, val, rate, frm, to, " incl" if incl else "", exp, got))

    # determinism: same input, repeated, must be identical
    a = as_json(compute("7777.77", 18, "27", "27"))
    for _ in range(50):
        if as_json(compute("7777.77", 18, "27", "27")) != a:
            failures.append("  non-deterministic: repeated calls differ")
            break

    # every live code classifies to exactly one label
    for code, (name, kind) in sorted(STATE_CODES.items()):
        if kind in (DEPRECATED, SPECIAL):
            continue
        lbl = state_tax_label(code)
        if lbl not in ("SGST", "UTGST"):
            failures.append("  %s (%s) -> bad label %r" % (code, name, lbl))
        if kind == UT_NOLEG and lbl != "UTGST":
            failures.append("  %s (%s) is a UT without legislature but got %s" % (code, name, lbl))
        if kind in (STATE, UT_LEG) and lbl != "SGST":
            failures.append("  %s (%s) should levy SGST but got %s" % (code, name, lbl))

    # CGST + state tax must equal IGST-on-the-same-base within one paisa
    for v in ("1", "9.99", "100", "333.33", "99999.95"):
        for rt in (5, 18, 40):
            intra = compute(v, rt, "27", "27")
            inter = compute(v, rt, "27", "24")
            if abs(intra["tax_total"] - inter["tax_total"]) > Decimal("0.01"):
                failures.append("  %s @ %s%%: intra %s vs inter %s differ by more than 0.01"
                                % (v, rt, intra["tax_total"], inter["tax_total"]))

    # deprecated codes must be rejected, not silently accepted
    for bad in ("25", "28"):
        try:
            compute("100", 18, bad, bad)
            failures.append("  deprecated code %s was accepted" % bad)
        except GstError:
            pass

    # a null rate must raise, never be treated as zero
    try:
        compute("100", None, "27", "27")
        failures.append("  gst_rate=None was treated as computable")
    except GstError:
        pass

    n = len(VECTORS)
    if failures:
        print("SELFTEST FAILED (%d issue(s)) over %d vectors + invariants:" % (len(failures), n))
        for f in failures:
            print(f)
        return 1
    print("SELFTEST PASS")
    print("  %d rate vectors" % n)
    print("  %d state codes classified (SGST vs UTGST)"
          % sum(1 for _, k in STATE_CODES.values() if k in (STATE, UT_LEG, UT_NOLEG)))
    print("  determinism: 50 repeated calls byte-identical")
    print("  intra vs inter totals agree within 0.01 on 15 value/rate pairs")
    print("  deprecated codes 25 and 28 rejected; null rate rejected")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def lookup_rate(code):
    """Read a gst_rate straight out of the knowledge base. Never guesses."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "enriched_complete.jsonl")
    if not os.path.exists(path):
        raise GstError("enriched_complete.jsonl not found next to scripts/")
    want = code if "_" in code else None
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r["id"] == want or r["code"] == code:
                if r["rate"]["gst_rate"] is None:
                    raise GstError(
                        "%s (%s) has no resolved rate in the knowledge base "
                        "(rate_confidence=%s). Refusing to assume a rate."
                        % (r["id"], r["title"][:60], r["rate"]["rate_confidence"]))
                return r["rate"]["gst_rate"], r
    raise GstError("code %r not found in enriched_complete.jsonl" % code)


def main(argv=None):
    p = argparse.ArgumentParser(description="Deterministic GST calculator.")
    p.add_argument("--value", help="taxable value (or GST-inclusive value with --inclusive)")
    p.add_argument("--rate", help="total GST %% (omit if using --code)")
    p.add_argument("--code", help="HSN/SAC code or id; reads the rate from the knowledge base")
    p.add_argument("--from", dest="frm", help="supplier GST state code, e.g. 27")
    p.add_argument("--to", dest="to", help="place-of-supply GST state code")
    p.add_argument("--cess", default=0, help="cess %% (default 0)")
    p.add_argument("--inclusive", action="store_true", help="value already includes GST")
    p.add_argument("--round-total", action="store_true",
                   help="round the invoice total to the nearest rupee (CGST Act s.170)")
    p.add_argument("--json", action="store_true", help="emit JSON")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--list-states", action="store_true")
    a = p.parse_args(argv)

    if a.selftest:
        return selftest()

    if a.list_states:
        print("%-5s %-46s %s" % ("CODE", "NAME", "STATE HALF"))
        for c in sorted(STATE_CODES):
            name, kind = STATE_CODES[c]
            if kind == DEPRECATED:
                lbl = "— deprecated"
            elif kind == SPECIAL:
                lbl = "— special"
            else:
                lbl = state_tax_label(c)
            print("%-5s %-46s %s" % (c, name, lbl))
        return 0

    if not a.value or not a.frm or not a.to:
        p.error("--value, --from and --to are required (or use --selftest / --list-states)")

    src = None
    if a.code:
        rate, src = lookup_rate(a.code)
    elif a.rate is not None:
        rate = a.rate
    else:
        p.error("supply --rate or --code")

    res = compute(a.value, rate, a.frm, a.to, cess_rate=a.cess,
                  inclusive=a.inclusive, round_total=a.round_total)
    if a.json:
        print(as_json(res))
    else:
        if src:
            print("%s  %s" % (src["id"], src["title"]))
            print("rate source: %s (%s confidence)"
                  % (src["rate"]["rate_source"], src["rate"]["rate_confidence"]))
            print("")
        print(as_text(res))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GstError as e:
        sys.stderr.write("ERROR: %s\n" % e)
        sys.exit(1)
