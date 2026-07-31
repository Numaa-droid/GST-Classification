#!/usr/bin/env python3
"""
Build a self-contained HTML browser for enriched_complete.jsonl.

The data is embedded directly in the page, so the file opens by double-click
with no server (a fetch() of a local .jsonl is blocked by CORS on file://).

Usage:  python scripts/build_browser.py
Output: gst_browser.html
"""

from __future__ import annotations

import collections
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gst_calc as GC  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_RECORDS = os.path.join(BASE, "enriched_complete.jsonl")
IN_MERGED = os.path.join(BASE, "merged 1.jsonl")
IN_BLOCKLIST = os.path.join(BASE, "artifact_blocklist.json")
OUT_HTML = os.path.join(BASE, "gst_browser.html")

# Chapter titles are pulled from the reference data where possible; these fill
# the gaps and give shorter, plainer labels than the tariff's own wording.
CHAPTER_LABELS = {
    "19": "Cereal, flour & bakery preparations",
    "20": "Preparations of vegetables & fruit",
    "21": "Miscellaneous edible preparations",
    "22": "Beverages, spirits & vinegar",
    "28": "Inorganic chemicals",
    "29": "Organic chemicals",
    "33": "Cosmetics, perfumery & toiletries",
    "39": "Plastics & articles thereof",
    "48": "Paper, paperboard & cartons",
    "61": "Apparel — knitted or crocheted",
    "62": "Apparel — not knitted",
    "63": "Other made-up textile articles",
    "73": "Articles of iron or steel",
    "84": "Machinery & mechanical appliances",
    "87": "Vehicles & vehicle parts",
    "90": "Optical, medical & precision instruments",
}
PRD_CHAPTERS = {"19", "20", "21", "28", "29", "33", "39", "61", "62", "73", "84"}


def read_jsonl(path):
    out = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main():
    if not os.path.exists(IN_RECORDS):
        sys.stderr.write("missing %s\n" % IN_RECORDS)
        return 1
    records = read_jsonl(IN_RECORDS)

    blocked = {}
    if os.path.exists(IN_BLOCKLIST):
        blocked = json.load(io.open(IN_BLOCKLIST, encoding="utf-8")).get("blocked_codes", {})

    # real 4-digit headings per chapter, for the coverage meter
    real = collections.Counter()
    if os.path.exists(IN_MERGED):
        with io.open(IN_MERGED, "r", encoding="utf-8") as fh:
            seen = set()
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                m = json.loads(line)
                c = m.get("code") or ""
                if m.get("entity_type") == "HSN" and len(c) == 4 and c not in seen:
                    seen.add(c)
                    real[c[:2]] += 1
    for r in records:
        if r["entity_type"] == "HSN" and len(r["code"]) == 4:
            pass  # counted below against the union

    chapters = {}
    for r in records:
        if r["entity_type"] != "HSN":
            continue
        ch = r["code"][:2]
        chapters.setdefault(ch, {"code": ch, "n": 0, "n4": 0})
        chapters[ch]["n"] += 1
        if len(r["code"]) == 4:
            chapters[ch]["n4"] += 1
    for ch, d in chapters.items():
        d["label"] = CHAPTER_LABELS.get(ch, "Chapter " + ch)
        d["prd"] = ch in PRD_CHAPTERS
        d["real"] = max(real.get(ch, 0), d["n4"])

    # Jurisdiction table + cross-implementation test vectors. The page recomputes
    # every vector in JS on load; if the JS ever disagrees with this Python it
    # says so on screen instead of quietly returning a wrong tax.
    states = [{"code": c, "name": n, "kind": k, "label": (
                  "—" if k in (GC.DEPRECATED, GC.SPECIAL) else GC.state_tax_label(c))}
              for c, (n, k) in sorted(GC.STATE_CODES.items())]

    live = [c for c, (n, k) in sorted(GC.STATE_CODES.items())
            if k in (GC.STATE, GC.UT_LEG, GC.UT_NOLEG)]
    vectors = []
    values = ["1", "9.99", "100", "333.33", "1000", "4999.5", "10000", "99999.95", "123456.78"]
    rates = [0, 5, 18, 40]
    for i, v in enumerate(values):
        for rt in rates:
            for j in range(4):
                frm = live[(i * 7 + j * 5) % len(live)]
                to = live[(i * 3 + j * 11) % len(live)]
                for incl in (False, True):
                    if incl and rt == 0:
                        continue
                    r = GC.compute(v, rt, frm, to, inclusive=incl)
                    vectors.append({
                        "v": v, "r": rt, "f": frm, "t": to, "i": 1 if incl else 0,
                        "base": str(r["taxable_value"]), "c": str(r["cgst"]),
                        "s": str(r["state_tax"]), "g": str(r["igst"]),
                        "lbl": r["state_tax_label"], "tot": str(r["invoice_total"]),
                    })

    meta = {
        "states": states,
        "vectors": vectors,
        "generated_from": os.path.basename(IN_RECORDS),
        "total": len(records),
        "hsn": sum(1 for r in records if r["entity_type"] == "HSN"),
        "sac": sum(1 for r in records if r["entity_type"] == "SAC"),
        "with_rate": sum(1 for r in records if r["rate"]["gst_rate"] is not None),
        "no_rate": sum(1 for r in records if r["rate"]["gst_rate"] is None),
        "seeded": sum(1 for r in records if r["rate"]["rate_source"] == "manual_seed"),
        "chapters": sorted(chapters.values(), key=lambda d: d["code"]),
        "blocked": blocked,
    }

    payload = json.dumps({"meta": meta, "records": records},
                         ensure_ascii=False, separators=(",", ":"))
    # never let the data terminate the script element
    payload = payload.replace("</", "<\\/")

    html = PAGE.replace("/*__DATA__*/", payload)
    with io.open(OUT_HTML, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)

    kb = os.path.getsize(OUT_HTML) / 1024.0
    print("records embedded : %d (%d HSN, %d SAC)" % (meta["total"], meta["hsn"], meta["sac"]))
    print("chapters         : %d" % len(meta["chapters"]))
    print("blocklist codes  : %d" % len(blocked))
    print("written          : %s (%.0f KB)" % (os.path.basename(OUT_HTML), kb))
    return 0


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GST Classification — Knowledge Base Browser</title>
<style>
:root{
  color-scheme: light;
  --surface-1:#fcfcfb; --page:#f9f9f7; --raised:#ffffff;
  --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e1e0d9; --axis:#c3c2b7; --ring:rgba(11,11,11,0.10);
  --accent:#2a78d6; --accent-soft:#cde2fb;
  --good:#0ca30c; --warning:#fab219; --serious:#ec835a; --critical:#d03b3b;
  --seq-1:#cde2fb; --seq-4:#3987e5; --seq-6:#184f95;
  --radius:10px;
}
@media (prefers-color-scheme: dark){
  :root:where(:not([data-theme="light"])){
    color-scheme: dark;
    --surface-1:#1a1a19; --page:#0d0d0d; --raised:#222221;
    --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --ring:rgba(255,255,255,0.10);
    --accent:#3987e5; --accent-soft:#184f95;
    --seq-1:#184f95; --seq-4:#3987e5; --seq-6:#9ec5f4;
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --surface-1:#1a1a19; --page:#0d0d0d; --raised:#222221;
  --ink:#ffffff; --ink-2:#c3c2b7; --muted:#898781;
  --grid:#2c2c2a; --axis:#383835; --ring:rgba(255,255,255,0.10);
  --accent:#3987e5; --accent-soft:#184f95;
  --seq-1:#184f95; --seq-4:#3987e5; --seq-6:#9ec5f4;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--page); color:var(--ink);
  font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;
  -webkit-font-smoothing:antialiased;
}
button{font:inherit;color:inherit}
kbd{font:11px/1 ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--grid);
    border-radius:4px;padding:2px 5px;color:var(--ink-2)}

/* ---------- header ---------- */
header{
  position:sticky;top:0;z-index:20;background:var(--surface-1);
  border-bottom:1px solid var(--grid);padding:14px 20px;
}
.hrow{display:flex;align-items:center;gap:16px;flex-wrap:wrap}
h1{font-size:16px;margin:0;font-weight:650;letter-spacing:-0.01em}
h1 span{color:var(--muted);font-weight:400}
.tiles{display:flex;gap:18px;margin-left:auto;flex-wrap:wrap}
.tile{display:flex;flex-direction:column;gap:1px}
.tile b{font-size:19px;font-weight:650;line-height:1.1}
.tile span{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.themebtn{background:none;border:1px solid var(--ring);border-radius:8px;
  padding:6px 10px;cursor:pointer;color:var(--ink-2);font-size:12px}
.themebtn:hover{background:var(--grid)}

/* ---------- layout ---------- */
.app{display:grid;grid-template-columns:250px 340px 1fr;gap:0;
     height:calc(100vh - 66px);min-height:0}
.col{min-height:0;overflow-y:auto;border-right:1px solid var(--grid)}
.col:last-child{border-right:0}
.rail{background:var(--surface-1);padding:10px}
.list{background:var(--page)}
.detail{background:var(--page);padding:20px 24px 60px}

/* ---------- chapter rail ---------- */
.railhead{font-size:11px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--muted);padding:8px 8px 6px;font-weight:600}
.chap{display:block;width:100%;text-align:left;background:none;border:0;
  padding:8px 9px;border-radius:8px;cursor:pointer;margin-bottom:1px}
.chap:hover{background:var(--grid)}
.chap[aria-current="true"]{background:var(--accent-soft)}
:root[data-theme="dark"] .chap[aria-current="true"],
@media (prefers-color-scheme:dark){}
.chap .top{display:flex;align-items:baseline;gap:8px}
.chap .num{font-weight:650;font-variant-numeric:tabular-nums;min-width:22px}
.chap .nm{font-size:12.5px;color:var(--ink-2);flex:1;line-height:1.3}
.chap .ct{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.chap[aria-current="true"] .nm,.chap[aria-current="true"] .ct{color:var(--ink)}
.meter{height:3px;border-radius:2px;background:var(--grid);margin-top:5px;overflow:hidden}
.meter i{display:block;height:100%;background:var(--seq-4);border-radius:2px}
.prdtag{font-size:9px;letter-spacing:.06em;color:var(--muted);border:1px solid var(--ring);
  border-radius:4px;padding:0 3px;text-transform:uppercase}

/* ---------- record list ---------- */
.search{position:sticky;top:0;background:var(--page);padding:10px;
  border-bottom:1px solid var(--grid);z-index:5}
.search input{width:100%;padding:9px 11px;border-radius:8px;border:1px solid var(--ring);
  background:var(--surface-1);color:var(--ink);font:inherit}
.search input:focus{outline:2px solid var(--accent);outline-offset:-1px}
.filters{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
.chipbtn{border:1px solid var(--ring);background:var(--surface-1);border-radius:999px;
  padding:4px 10px;font-size:11.5px;cursor:pointer;color:var(--ink-2)}
.chipbtn[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.listcount{padding:8px 12px;font-size:11px;color:var(--muted);
  text-transform:uppercase;letter-spacing:.04em}
.rec{display:block;width:100%;text-align:left;background:none;border:0;
  border-bottom:1px solid var(--grid);padding:11px 12px;cursor:pointer}
.rec:hover{background:var(--surface-1)}
.rec[aria-current="true"]{background:var(--surface-1);
  box-shadow:inset 3px 0 0 var(--accent)}
.rec .r1{display:flex;align-items:center;gap:8px}
.rec code{font:600 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--accent)}
.rec .t{font-size:13px;margin-top:3px;color:var(--ink);line-height:1.35}
.rec .r2{display:flex;gap:6px;margin-top:6px;align-items:center;flex-wrap:wrap}

/* ---------- status chips (icon + label, never colour alone) ---------- */
.st{display:inline-flex;align-items:center;gap:4px;font-size:11px;font-weight:550;
  border-radius:999px;padding:2px 8px;border:1px solid var(--ring);
  background:var(--surface-1);color:var(--ink-2);white-space:nowrap}
.st .dot{width:7px;height:7px;border-radius:50%;flex:none}
.st.good .dot{background:var(--good)}
.st.warn .dot{background:var(--warning)}
.st.sers .dot{background:var(--serious)}
.st.crit .dot{background:var(--critical)}
.st.mute .dot{background:var(--muted)}
.rate-pill{font-weight:650;font-variant-numeric:tabular-nums;
  background:var(--accent-soft);border-color:transparent;color:var(--ink)}

/* ---------- detail ---------- */
.empty{color:var(--muted);padding:60px 20px;text-align:center;font-size:14px}
.dhead{border-bottom:1px solid var(--grid);padding-bottom:14px;margin-bottom:18px}
.dhead .bc{font-size:11.5px;color:var(--muted);margin-bottom:6px}
.dhead h2{margin:0 0 8px;font-size:19px;line-height:1.3;font-weight:650;letter-spacing:-0.01em}
.dhead .idline{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.dhead code{font:650 14px/1 ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--accent)}
.oneliner{margin-top:10px;padding:9px 12px;background:var(--accent-soft);
  border-radius:8px;font-size:13px;color:var(--ink)}
section{margin-bottom:22px}
h3{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
  margin:0 0 9px;font-weight:650}
.card{background:var(--surface-1);border:1px solid var(--grid);border-radius:var(--radius);
  padding:14px 16px}

/* rate block */
.ratetop{display:flex;align-items:flex-end;gap:20px;flex-wrap:wrap}
.bigrate{font-size:34px;font-weight:650;line-height:1;letter-spacing:-0.02em;
  font-variant-numeric:tabular-nums}
.bigrate.none{font-size:17px;color:var(--muted);font-weight:550}
.split{display:flex;gap:10px;flex-wrap:wrap}
.sp{border:1px solid var(--grid);border-radius:8px;padding:7px 12px;min-width:88px;
  background:var(--raised)}
.sp b{display:block;font-size:16px;font-variant-numeric:tabular-nums;font-weight:650}
.sp span{font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.sp.intra{border-color:var(--accent)}
.splitnote{font-size:11.5px;color:var(--muted);margin-top:8px}
.kv{display:grid;grid-template-columns:auto 1fr;gap:5px 14px;margin-top:14px;
  padding-top:12px;border-top:1px solid var(--grid);font-size:12.5px}
.kv dt{color:var(--muted)}
.kv dd{margin:0;color:var(--ink-2);word-break:break-word}
.caveat{margin-top:12px;padding:10px 12px;border-radius:8px;font-size:12.5px;
  background:var(--page);border:1px solid var(--ring);color:var(--ink-2)}
.caveat b{color:var(--ink)}

/* chips */
.chips{display:flex;flex-wrap:wrap;gap:5px}
.chip{background:var(--surface-1);border:1px solid var(--grid);border-radius:6px;
  padding:3px 8px;font-size:12px;color:var(--ink-2)}
.chip.hi{border-color:var(--accent);color:var(--ink)}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.sub{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;
  margin-bottom:6px;font-weight:600}
ul.plain{margin:0;padding-left:17px}
ul.plain li{margin-bottom:4px;color:var(--ink-2)}
.qa{border:1px solid var(--grid);border-radius:8px;padding:11px 13px;
  margin-bottom:8px;background:var(--surface-1)}
.qa .q{font-weight:550;margin-bottom:7px}
.qa .opts{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:7px}
.qa .opt{border:1px solid var(--axis);border-radius:999px;padding:3px 10px;font-size:12px}
.qa .meta{font-size:11.5px;color:var(--muted)}
.xn{border-left:2px solid var(--serious);padding:2px 0 2px 11px;margin-bottom:10px}
.xn .code{font:600 12px/1 ui-monospace,SFMono-Regular,Menlo,monospace}
.xn .reason{font-size:12.5px;color:var(--ink-2);margin-top:4px}
a.jump{color:var(--accent);text-decoration:none;border-bottom:1px dotted var(--accent);
  cursor:pointer}
a.jump:hover{border-bottom-style:solid}
table.ex{width:100%;border-collapse:collapse;font-size:12.5px}
table.ex th{text-align:left;font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;
  color:var(--muted);border-bottom:1px solid var(--grid);padding:0 10px 6px 0;font-weight:600}
table.ex td{padding:7px 10px 7px 0;border-bottom:1px solid var(--grid);
  vertical-align:top;color:var(--ink-2)}
table.ex td.r{font-variant-numeric:tabular-nums;font-weight:600;color:var(--ink);
  white-space:nowrap}
.scroller{overflow-x:auto}
/* calculator */
.calcgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.calcgrid label{display:block}
.calcin{width:100%;padding:8px 10px;border-radius:8px;border:1px solid var(--ring);
  background:var(--raised);color:var(--ink);font:inherit;font-variant-numeric:tabular-nums}
.calcin:focus{outline:2px solid var(--accent);outline-offset:-1px}
.inclrow{display:flex;align-items:center;gap:7px;margin-top:11px;font-size:12.5px;
  color:var(--ink-2);cursor:pointer}
.supplybadge{display:flex;align-items:center;gap:10px;flex-wrap:wrap;
  margin:15px 0 10px;padding-top:13px;border-top:1px solid var(--grid)}
table.calctable{width:100%;border-collapse:collapse;font-size:13px}
table.calctable td{padding:6px 0;border-bottom:1px solid var(--grid);color:var(--ink-2)}
table.calctable td.r{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink);
  white-space:nowrap}
table.calctable tr.tax td{color:var(--ink)}
table.calctable tr.sum td{font-weight:600;color:var(--ink)}
table.calctable tr.grand td{font-weight:700;font-size:15px;color:var(--ink);
  border-bottom:0;padding-top:9px}
.vfy{font-size:11px;color:var(--muted);padding:6px 9px;border-top:1px solid var(--grid)}
.vfy.bad{color:#fff;background:var(--critical);border-radius:6px;padding:8px 10px;
  font-weight:600}
details.raw{margin-top:6px}
details.raw summary{cursor:pointer;font-size:12px;color:var(--muted);
  list-style:none;padding:6px 0}
details.raw summary::-webkit-details-marker{display:none}
details.raw summary:before{content:"▸ ";color:var(--muted)}
details.raw[open] summary:before{content:"▾ "}
pre{margin:0;padding:13px;background:var(--surface-1);border:1px solid var(--grid);
  border-radius:8px;overflow-x:auto;font:11.5px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;
  color:var(--ink-2)}

@media (max-width:1100px){
  .app{grid-template-columns:210px 1fr;height:auto}
  .detail{display:none;grid-column:1/-1}
  body.showdetail .rail,body.showdetail .list{display:none}
  body.showdetail .detail{display:block}
}
@media (max-width:640px){
  .app{grid-template-columns:1fr}
  .tiles{gap:12px}
  .tile b{font-size:16px}
}
.backbtn{display:none;margin-bottom:12px;background:var(--surface-1);
  border:1px solid var(--ring);border-radius:8px;padding:7px 12px;cursor:pointer}
@media (max-width:1100px){.backbtn{display:inline-block}}
</style>
</head>
<body>

<header>
  <div class="hrow">
    <h1>GST Classification <span>· knowledge base browser</span></h1>
    <div class="tiles" id="tiles"></div>
    <button class="themebtn" id="theme" type="button">Theme</button>
  </div>
</header>

<div class="app">
  <nav class="col rail" id="rail"></nav>
  <div class="col list">
    <div class="search">
      <input id="q" type="search" placeholder="Search code, title, synonym, example…" autocomplete="off">
      <div class="filters" id="filters">
        <button class="chipbtn" data-f="all" aria-pressed="true" type="button">All</button>
        <button class="chipbtn" data-f="hsn" aria-pressed="false" type="button">Goods (HSN)</button>
        <button class="chipbtn" data-f="sac" aria-pressed="false" type="button">Services (SAC)</button>
        <button class="chipbtn" data-f="norate" aria-pressed="false" type="button">No rate</button>
        <button class="chipbtn" data-f="seed" aria-pressed="false" type="button">Hand-seeded</button>
      </div>
    </div>
    <div class="listcount" id="count"></div>
    <div id="reclist"></div>
  </div>
  <main class="col detail" id="detail"></main>
</div>

<script id="data" type="application/json">/*__DATA__*/</script>
<script>
(function(){
"use strict";
var DB      = JSON.parse(document.getElementById("data").textContent);
var META    = DB.meta, RECS = DB.records;
var byId    = {}; RECS.forEach(function(r){ byId[r.id] = r; });
var state   = { chapter:"ALL", filter:"all", q:"" };

/* ==================================================================
   Deterministic GST calculation — integer paise only, never a float.
   Mirrors scripts/gst_calc.py. Verified against Python-generated
   vectors at load time (see selfCheck below).
   ================================================================== */
var STATES={}; (META.states||[]).forEach(function(s){ STATES[s.code]=s; });

function toPaise(str){                     /* "1234.5" -> 123450 */
  var s=String(str).trim().replace(/,/g,"");
  if(!/^\d+(\.\d*)?$/.test(s)) return null;
  var p=s.split("."), r=p[0], f=(p[1]||"")+"00";
  /* round half up at the 3rd decimal, matching Decimal.quantize */
  var whole=parseInt(r,10), cents=parseInt(f.slice(0,2),10);
  var next=parseInt(f.charAt(2)||"0",10);
  var v=whole*100+cents; if(next>=5) v+=1;
  return v;
}
function divHalfUp(num,den){               /* exact, non-negative */
  var q=Math.floor(num/den), rem=num-q*den;
  return (rem*2>=den)?q+1:q;
}
function money(paise){
  var neg=paise<0; paise=Math.abs(paise);
  var r=Math.floor(paise/100), c=paise%100;
  return (neg?"-":"")+r.toLocaleString("en-IN")+"."+(c<10?"0":"")+c;
}
function stateLabel(code){
  var s=STATES[code];
  return (s && s.kind==="ut_without_legislature") ? "UTGST" : "SGST";
}
function calcGst(valueStr, ratePct, fromCode, toCode, inclusive, cessPct){
  var base=toPaise(valueStr); if(base===null) return null;
  var rateH=Math.round(Number(ratePct)*100);      /* 18 -> 1800, 2.5 -> 250 */
  var cessH=Math.round(Number(cessPct||0)*100);
  if(!(rateH>=0)||!(cessH>=0)) return null;
  if(inclusive) base=divHalfUp(base*10000,10000+rateH+cessH);

  var intra = (fromCode===toCode);
  var half  = rateH/2;                            /* always integral: rateH is *100 */
  var cgst=0,sgst=0,igst=0;
  if(intra){ cgst=divHalfUp(base*half,10000); sgst=cgst; }
  else     { igst=divHalfUp(base*rateH,10000); }
  var cess = cessH? divHalfUp(base*cessH,10000) : 0;
  var tax=cgst+sgst+igst+cess;
  return { base:base, cgst:cgst, sgst:sgst, igst:igst, cess:cess,
           tax:tax, total:base+tax, intra:intra,
           label:stateLabel(toCode), halfPct:(half/100), ratePct:Number(ratePct) };
}

/* the guarantee, checked rather than asserted */
function selfCheck(){
  var vs=META.vectors||[], bad=[];
  vs.forEach(function(v){
    var r=calcGst(v.v, v.r, v.f, v.t, !!v.i, 0);
    if(!r){ bad.push(v); return; }
    if(money(r.base)!==addCommas(v.base) || money(r.cgst)!==addCommas(v.c) ||
       money(r.sgst)!==addCommas(v.s)    || money(r.igst)!==addCommas(v.g) ||
       r.label!==v.lbl                   || money(r.total)!==addCommas(v.tot)){
      bad.push(v);
    }
  });
  return {total:vs.length, bad:bad};
}
function addCommas(numStr){                /* "1800.00" -> "1,800.00" (en-IN) */
  var p=String(numStr).split("."), n=parseInt(p[0],10);
  return n.toLocaleString("en-IN")+"."+(p[1]||"00");
}

function el(t,a,kids){
  var n=document.createElement(t); a=a||{};
  for(var k in a){ if(k==="class") n.className=a[k];
    else if(k==="html") n.innerHTML=a[k];
    else if(k==="text") n.textContent=a[k];
    else if(k.slice(0,2)==="on") n.addEventListener(k.slice(2),a[k]);
    else n.setAttribute(k,a[k]); }
  (kids||[]).forEach(function(c){ if(c) n.appendChild(c); });
  return n;
}
function esc(s){ return String(s==null?"":s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
function pct(v){ return (Math.round(v*10)/10)+"%"; }
function fmtRate(v){ return v==null?null:(Number.isInteger(v)?v:v)+"%"; }

/* ---------- status mapping: colour ALWAYS paired with a label ---------- */
function rateStatus(r){
  if(r.rate.gst_rate==null) return {cls:"crit", label:"No rate available"};
  var c=r.rate.rate_confidence;
  if(c==="high")   return {cls:"good", label:"High confidence"};
  if(c==="medium") return {cls:"warn", label:"Medium confidence"};
  if(c==="low")    return {cls:"sers", label:"Low confidence"};
  return {cls:"mute", label:c||"unknown"};
}
function sourceLabel(s){
  return s==="merged" ? "From rate schedule"
       : s==="manual_seed" ? "Hand-entered — verify"
       : "No source";
}
function chip(cls,label){
  return el("span",{class:"st "+cls},[el("span",{class:"dot"}),
         el("span",{text:label})]);
}

/* ---------- header tiles ---------- */
(function tiles(){
  var host=document.getElementById("tiles");
  [["Records",META.total],["Goods",META.hsn],["Services",META.sac],
   ["With a rate",META.with_rate],["No rate",META.no_rate]]
  .forEach(function(t){
    host.appendChild(el("div",{class:"tile"},[
      el("b",{text:String(t[1])}), el("span",{text:t[0]})]));
  });
})();

/* ---------- chapter rail ---------- */
function buildRail(){
  var rail=document.getElementById("rail"); rail.innerHTML="";
  var maxN=Math.max.apply(null,META.chapters.map(function(c){return c.n;}));

  rail.appendChild(el("div",{class:"railhead",text:"Browse"}));
  rail.appendChild(chapBtn({code:"ALL",label:"All records",n:META.total,real:0},maxN));
  rail.appendChild(chapBtn({code:"SAC",label:"Services (SAC)",n:META.sac,real:0},maxN));

  rail.appendChild(el("div",{class:"railhead",text:"HSN chapters (goods)"}));
  META.chapters.forEach(function(c){ rail.appendChild(chapBtn(c,maxN)); });

  if(META.blocked && Object.keys(META.blocked).length){
    rail.appendChild(el("div",{class:"railhead",text:"Excluded"}));
    var n=Object.keys(META.blocked).length;
    rail.appendChild(el("div",{class:"chap"},[
      el("div",{class:"top"},[
        el("span",{class:"nm",text:n+" blocked artifact codes"})]),
      el("div",{class:"splitnote",style:"font-size:11px;margin-top:2px",
        text:"Not real headings — never indexed"})]));
  }
}
function chapBtn(c,maxN){
  var cur = state.chapter===c.code;
  var kids=[el("div",{class:"top"},[
    c.code.length===2?el("span",{class:"num",text:c.code}):null,
    el("span",{class:"nm",text:c.label}),
    c.prd?el("span",{class:"prdtag",text:"PRD"}):null,
    el("span",{class:"ct",text:String(c.n)})])];
  if(c.code.length===2){
    kids.push(el("div",{class:"meter"},[
      el("i",{style:"width:"+Math.max(4,(c.n/maxN)*100)+"%"})]));
  }
  return el("button",{class:"chap","aria-current":cur?"true":"false",type:"button",
    onclick:function(){ state.chapter=c.code; buildRail(); renderList(); }},kids);
}

/* ---------- list ---------- */
function matches(r){
  if(state.chapter==="SAC"){ if(r.entity_type!=="SAC") return false; }
  else if(state.chapter!=="ALL"){
    if(r.entity_type!=="HSN"||r.code.slice(0,2)!==state.chapter) return false;
  }
  var f=state.filter;
  if(f==="hsn"    && r.entity_type!=="HSN") return false;
  if(f==="sac"    && r.entity_type!=="SAC") return false;
  if(f==="norate" && r.rate.gst_rate!=null) return false;
  if(f==="seed"   && r.rate.rate_source!=="manual_seed") return false;
  var q=state.q.trim().toLowerCase();
  if(!q) return true;
  return (r.code+" "+r.title+" "+r.search_text).toLowerCase().indexOf(q)>=0;
}
function renderList(){
  var host=document.getElementById("reclist"); host.innerHTML="";
  var hits=RECS.filter(matches);
  document.getElementById("count").textContent =
    hits.length+" record"+(hits.length===1?"":"s");
  if(!hits.length){
    host.appendChild(el("div",{class:"empty",text:"Nothing matches that filter."}));
    return;
  }
  hits.slice(0,600).forEach(function(r){
    var s=rateStatus(r);
    host.appendChild(el("button",{class:"rec",type:"button",
      "aria-current": (window.__cur===r.id)?"true":"false",
      onclick:function(){ show(r.id); }},[
      el("div",{class:"r1"},[el("code",{text:r.code}),
        el("span",{class:"st mute",style:"padding:1px 6px",text:r.entity_type})]),
      el("div",{class:"t",text:r.title}),
      el("div",{class:"r2"},[
        r.rate.gst_rate!=null
          ? el("span",{class:"st rate-pill",text:fmtRate(r.rate.gst_rate)+" GST"})
          : null,
        chip(s.cls,s.label)])
    ]));
  });
  if(hits.length>600){
    host.appendChild(el("div",{class:"listcount",
      text:"showing first 600 — narrow the search to see the rest"}));
  }
  var sel=host.querySelector('[aria-current="true"]');
  if(sel && sel.scrollIntoView) sel.scrollIntoView({block:"nearest"});
}

/* ---------- detail ---------- */
function show(id,skipHash){
  var r=byId[id]; if(!r){ renderEmpty(); return; }
  window.__cur=id; renderList();
  if(!skipHash && location.hash.slice(1)!==id){
    history.replaceState(null,"","#"+id);
  }
  var d=document.getElementById("detail");
  document.body.classList.add("showdetail");
  d.innerHTML=""; d.scrollTop=0;
  d.appendChild(el("button",{class:"backbtn",type:"button",text:"← Back to list",
    onclick:function(){ document.body.classList.remove("showdetail"); }}));

  var chLabel = r.entity_type==="HSN"
    ? ("Chapter "+r.code.slice(0,2)+" · "+chapterName(r.code.slice(0,2)))
    : "Services (SAC)";

  /* header */
  var head=el("div",{class:"dhead"},[
    el("div",{class:"bc",text:chLabel}),
    el("h2",{text:r.title}),
    el("div",{class:"idline"},[
      el("code",{text:r.code}),
      el("span",{class:"st mute",text:r.entity_type}),
      el("span",{class:"st mute",text:"Classification: "+
        r.ai.classification_confidence.level}),
      r.enrichment_status!=="complete"
        ? chip("warn","Status: "+r.enrichment_status) : null
    ])
  ]);
  if(r.ai.one_line_rationale){
    head.appendChild(el("div",{class:"oneliner",text:r.ai.one_line_rationale}));
  }
  d.appendChild(head);

  /* --- rate --- */
  var rt=r.rate, s=rateStatus(r);
  var rateCard=el("div",{class:"card"});
  var top=el("div",{class:"ratetop"});
  if(rt.gst_rate==null){
    top.appendChild(el("div",{class:"bigrate none",text:"Rate unavailable"}));
  }else{
    top.appendChild(el("div",{class:"bigrate",text:fmtRate(rt.gst_rate)}));
    top.appendChild(el("div",{class:"split"},[
      el("div",{class:"sp intra"},[el("b",{text:fmtRate(rt.cgst)}),
        el("span",{text:"CGST"})]),
      el("div",{class:"sp intra"},[el("b",{text:fmtRate(rt.sgst)}),
        el("span",{text:"SGST / UTGST"})]),
      el("div",{class:"sp"},[el("b",{text:fmtRate(rt.igst)}),
        el("span",{text:"IGST"})])
    ]));
  }
  rateCard.appendChild(top);
  rateCard.appendChild(el("div",{class:"r2",style:"display:flex;gap:6px;margin-top:12px;flex-wrap:wrap"},[
    chip(s.cls,s.label),
    chip(rt.rate_source==="manual_seed"?"warn":"mute",sourceLabel(rt.rate_source)),
    rt.rate_scope?el("span",{class:"st mute",text:"Matched at: "+rt.rate_scope}):null
  ]));
  if(rt.gst_rate!=null){
    rateCard.appendChild(el("div",{class:"splitnote",
      text:"Same state or UT → CGST + the state half. Different state or UT → IGST. "
         +"Both add up to "+fmtRate(rt.gst_rate)+". The state half is SGST in a State "
         +"or in Delhi / Puducherry / J&K, and UTGST in the other Union Territories — "
         +"pick a place of supply below to resolve it."}));
  }
  var kv=el("dl",{class:"kv"});
  [["Effective from",rt.effective_from],["Notification",rt.notification_no],
   ["Cess",rt.cess],["Exemption status",rt.exemption_status]]
   .forEach(function(p){ if(p[1]!=null&&p[1]!==""){
     kv.appendChild(el("dt",{text:p[0]})); kv.appendChild(el("dd",{text:String(p[1])})); }});
  if(kv.children.length) rateCard.appendChild(kv);
  if(rt.rate_caveat){
    rateCard.appendChild(el("div",{class:"caveat"},[
      el("b",{text:"Caveat: "}), el("span",{text:rt.rate_caveat})]));
  }
  d.appendChild(el("section",{},[el("h3",{text:"GST rate"}),rateCard]));

  /* --- calculator --- */
  if(rt.gst_rate!=null) d.appendChild(calculator(rt.gst_rate));

  /* --- exceptions --- */
  if(rt.exceptions&&rt.exceptions.length){
    var tb=el("tbody");
    rt.exceptions.forEach(function(x){
      tb.appendChild(el("tr",{},[
        el("td",{class:"r",text:x.gst_rate==null?"—":fmtRate(x.gst_rate)}),
        el("td",{text:x.condition||""})]));
    });
    d.appendChild(el("section",{},[
      el("h3",{text:"Rate exceptions ("+rt.exceptions.length+")"}),
      el("div",{class:"card"},[
        el("div",{class:"splitnote",style:"margin:0 0 10px",
          text:"These cases are taxed differently from the headline rate above. "
             + "If your product matches one, the headline rate does not apply to you."}),
        el("div",{class:"scroller"},[
          el("table",{class:"ex"},[
            el("thead",{},[el("tr",{},[el("th",{text:"Rate"}),el("th",{text:"When it applies"})])]),
            tb])])])]));
  }

  /* --- history --- */
  if(rt.history&&rt.history.length){
    var hb=el("tbody");
    rt.history.forEach(function(h){
      hb.appendChild(el("tr",{},[
        el("td",{text:h.effective_from||"—"}),
        el("td",{class:"r",text:h.gst_rate==null?"—":fmtRate(h.gst_rate)})]));
    });
    d.appendChild(el("section",{},[el("h3",{text:"Earlier rates"}),
      el("div",{class:"card"},[el("table",{class:"ex"},[
        el("thead",{},[el("tr",{},[el("th",{text:"Effective from"}),el("th",{text:"Rate"})])]),
        hb])])]));
  }

  /* --- why this code --- */
  var why=el("div",{class:"card"},[
    el("div",{style:"font-size:13.5px;line-height:1.6",text:r.ai.plain_rationale})]);
  var cc=r.ai.classification_confidence;
  why.appendChild(el("div",{class:"kv",style:"display:block"},[
    el("div",{class:"sub",style:"margin-top:4px",
      text:"Why confidence is "+cc.level}),
    el("div",{style:"font-size:12.5px;color:var(--ink-2)",text:cc.rationale})]));
  if(cc.ambiguity_triggers&&cc.ambiguity_triggers.length){
    why.appendChild(el("div",{style:"margin-top:12px"},[
      el("div",{class:"sub",text:"Words that make this ambiguous"}),
      el("div",{class:"chips"},cc.ambiguity_triggers.map(function(t){
        return el("span",{class:"chip",text:t}); }))]));
  }
  d.appendChild(el("section",{},[el("h3",{text:"Why this code"}),why]));

  /* --- clarifying questions --- */
  if(r.ai.clarification_questions.length){
    var box=el("div",{});
    r.ai.clarification_questions.forEach(function(q){
      var meta=el("div",{class:"meta"});
      meta.appendChild(document.createTextNode("Tells apart from: "));
      (q.disambiguates_from||[]).forEach(function(x,i){
        if(i) meta.appendChild(document.createTextNode(", "));
        meta.appendChild(linkTo(x));
      });
      meta.appendChild(document.createTextNode("  ·  attribute: "+q.attribute));
      box.appendChild(el("div",{class:"qa"},[
        el("div",{class:"q",text:q.question}),
        el("div",{class:"opts"},(q.options||[]).map(function(o){
          return el("span",{class:"opt",text:o}); })),
        meta]));
    });
    d.appendChild(el("section",{},[
      el("h3",{text:"Questions that narrow it down"}),box]));
  }

  /* --- exclusions --- */
  if(r.ai.exclusion_notes.length){
    var xb=el("div",{});
    r.ai.exclusion_notes.forEach(function(x){
      xb.appendChild(el("div",{class:"xn"},[
        el("div",{class:"code"},[document.createTextNode("Not "),linkTo(x.excluded_code)]),
        el("div",{class:"reason",text:x.reason})]));
    });
    d.appendChild(el("section",{},[
      el("h3",{text:"Easily confused with"}),el("div",{class:"card"},[xb])]));
  }

  /* --- vocabulary --- */
  var a=r.ai.attributes;
  var vocab=[["Also called",r.ai.synonyms],["Trade terms",r.ai.market_terms],
             ["Hindi / local",r.ai.hindi_transliterated],
             ["Material",a.material],["Use",a.use],["Form",a.form],
             ["Industry",a.industry],["Sector",a.sector]]
            .filter(function(p){ return p[1]&&p[1].length; });
  if(vocab.length){
    d.appendChild(el("section",{},[el("h3",{text:"How people describe it"}),
      el("div",{class:"card"},[el("div",{class:"grid2"},vocab.map(function(p){
        return el("div",{},[el("div",{class:"sub",text:p[0]}),
          el("div",{class:"chips"},p[1].map(function(v){
            return el("span",{class:"chip"+(p[0]==="Sector"?" hi":""),text:v}); }))]);
      }))])]));
  }
  if(r.ai.examples.length){
    d.appendChild(el("section",{},[el("h3",{text:"Real examples"}),
      el("div",{class:"card"},[el("ul",{class:"plain"},
        r.ai.examples.map(function(x){ return el("li",{text:x}); }))])]));
  }

  /* --- citation + raw --- */
  d.appendChild(el("section",{},[el("h3",{text:"Source"}),
    el("div",{class:"card"},[
      el("div",{style:"font-size:12.5px;color:var(--ink-2)",
        text:r.ai.regulatory_citation||"—"}),
      el("details",{class:"raw"},[
        el("summary",{text:"Raw record (JSON)"}),
        el("pre",{text:JSON.stringify(r,null,2)})])])]));
}
/* ---------- the calculator panel ---------- */
var CALC={amount:"10000", from:"27", to:"27", incl:false};
function stateSelect(which){
  var sel=el("select",{class:"calcin",onchange:function(){
    CALC[which]=this.value; redrawCalc(); }});
  (META.states||[]).forEach(function(s){
    if(s.kind==="deprecated"||s.kind==="special") return;
    var tag = s.kind==="ut_without_legislature" ? "  · UTGST"
            : s.kind==="ut_with_legislature"    ? "  · UT, SGST" : "";
    var o=el("option",{value:s.code,text:s.code+"  "+s.name+tag});
    if(CALC[which]===s.code) o.selected=true;
    sel.appendChild(o);
  });
  return sel;
}
function calculator(rate){
  var out=el("div",{id:"calcout"});
  var amt=el("input",{class:"calcin",type:"text",inputmode:"decimal",
    value:CALC.amount,oninput:function(){ CALC.amount=this.value; redrawCalc(); }});
  var inc=el("input",{type:"checkbox",onchange:function(){
    CALC.incl=this.checked; redrawCalc(); }});
  if(CALC.incl) inc.checked=true;

  window.__rate=rate;
  var card=el("div",{class:"card"},[
    el("div",{class:"calcgrid"},[
      el("label",{},[el("span",{class:"sub",text:"Amount (₹)"}),amt]),
      el("label",{},[el("span",{class:"sub",text:"Supplier is in"}),stateSelect("from")]),
      el("label",{},[el("span",{class:"sub",text:"Place of supply"}),stateSelect("to")])
    ]),
    el("label",{class:"inclrow"},[inc,
      el("span",{text:"Amount already includes GST"})]),
    out
  ]);
  setTimeout(redrawCalc,0);
  return el("section",{},[el("h3",{text:"Calculate this tax"}),card]);
}
function redrawCalc(){
  var out=document.getElementById("calcout"); if(!out) return;
  out.innerHTML="";
  var r=calcGst(CALC.amount, window.__rate, CALC.from, CALC.to, CALC.incl, 0);
  if(!r){ out.appendChild(el("div",{class:"splitnote",
    text:"Enter a number, e.g. 10000 or 4999.50."})); return; }

  var rows=[["Taxable value",money(r.base),""]];
  if(r.intra){
    rows.push(["CGST @ "+r.halfPct+"%",money(r.cgst),"tax"]);
    rows.push([r.label+" @ "+r.halfPct+"%",money(r.sgst),"tax"]);
  }else{
    rows.push(["IGST @ "+r.ratePct+"%",money(r.igst),"tax"]);
  }
  rows.push(["Total tax",money(r.tax),"sum"]);
  rows.push(["Invoice total",money(r.total),"grand"]);

  var tb=el("tbody");
  rows.forEach(function(x){
    tb.appendChild(el("tr",{class:x[2]},[
      el("td",{text:x[0]}),el("td",{class:"r",text:"₹ "+x[1]})]));
  });
  out.appendChild(el("div",{class:"supplybadge"},[
    chip(r.intra?"good":"warn",
      r.intra ? "Intra-State / Intra-UT → CGST + "+r.label
              : "Inter-State → IGST"),
    el("span",{class:"splitnote",style:"margin:0",
      text: r.intra
        ? (STATES[CALC.to]||{}).name+" levies "+r.label
        : "Supplier and place of supply are in different states/UTs"})
  ]));
  out.appendChild(el("table",{class:"calctable"},[tb]));
}

function chapterName(c){
  var m=META.chapters.filter(function(x){return x.code===c;})[0];
  return m?m.label:"—";
}

/* ---------- empty state doubles as the legend ---------- */
function renderEmpty(){
  var d=document.getElementById("detail"); d.innerHTML="";
  var legend=[["good","High confidence","rate matched directly to this code"],
              ["warn","Medium confidence","rate matched, but at a broader level"],
              ["sers","Low confidence","rate inferred — check before invoicing"],
              ["crit","No rate available","nothing matched; not a zero rate"]];
  var rows=el("div",{style:"display:grid;gap:9px;margin-top:4px"});
  legend.forEach(function(l){
    rows.appendChild(el("div",{style:"display:flex;gap:10px;align-items:center"},[
      chip(l[0],l[1]),
      el("span",{style:"font-size:12.5px;color:var(--ink-2)",text:l[2]})]));
  });
  d.appendChild(el("div",{style:"max-width:520px;margin:40px auto 0"},[
    el("h3",{text:"How to read this"}),
    el("div",{class:"card"},[
      el("div",{style:"font-size:13.5px;margin-bottom:14px",
        text:"Pick a chapter on the left, then a record — its full classification "
           + "response appears here: the GST rate and its CGST/SGST/IGST split, why "
           + "the code was chosen, what it is easily confused with, and the questions "
           + "that tell those apart."}),
      el("div",{class:"sub",text:"Rate confidence"}), rows,
      el("div",{class:"splitnote",style:"margin-top:14px",
        text:"Colour is never the only signal — every chip is labelled. "
           + Object.keys(META.blocked||{}).length
           + " known artifact codes are excluded from this set entirely."})])]));
}
function linkTo(id){
  if(byId[id]) return el("a",{class:"jump",text:id,title:byId[id].title,
    onclick:function(e){ e.preventDefault(); state.chapter="ALL"; state.q="";
      document.getElementById("q").value=""; buildRail(); show(id); }});
  return el("span",{text:id+" (not in this set)"});
}

/* ---------- wiring ---------- */
document.getElementById("q").addEventListener("input",function(e){
  state.q=e.target.value; renderList(); });
document.getElementById("filters").addEventListener("click",function(e){
  var b=e.target.closest("[data-f]"); if(!b) return;
  state.filter=b.getAttribute("data-f");
  [].forEach.call(this.querySelectorAll("[data-f]"),function(x){
    x.setAttribute("aria-pressed", x===b ? "true":"false"); });
  renderList();
});
document.getElementById("theme").addEventListener("click",function(){
  var cur=document.documentElement.getAttribute("data-theme");
  var next = cur==="dark" ? "light" : cur==="light" ? "dark"
    : (matchMedia("(prefers-color-scheme: dark)").matches ? "light":"dark");
  document.documentElement.setAttribute("data-theme",next);
});
window.addEventListener("hashchange",function(){
  var id=decodeURIComponent(location.hash.slice(1));
  if(id && byId[id]) show(id,true);
});

buildRail(); renderList();

/* prove the in-page calculator agrees with scripts/gst_calc.py */
(function(){
  var c=selfCheck(), rail=document.getElementById("rail");
  var n=el("div",{class:"vfy"+(c.bad.length?" bad":"")});
  if(c.bad.length){
    n.textContent="CALCULATOR MISMATCH: "+c.bad.length+" of "+c.total
      +" checks disagree with gst_calc.py — do not trust these figures.";
    console.error("GST calculator vector mismatches:",c.bad.slice(0,10));
  }else{
    n.textContent="Calculator verified: "+c.total
      +" cases match scripts/gst_calc.py exactly.";
  }
  rail.appendChild(n);
})();

var initial=decodeURIComponent(location.hash.slice(1));
if(initial && byId[initial]) show(initial,true); else renderEmpty();
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
