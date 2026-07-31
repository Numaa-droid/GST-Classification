#!/usr/bin/env python3
"""
Close the final coverage gap: add the 6 genuinely-missing headings and build the
artifact blocklist.

Inputs  : enriched_final.jsonl (333, v6), merged 1.jsonl
Outputs : enriched_complete.jsonl, artifact_blocklist.json, coverage_report.md

The 6 new records are emitted with a null rate exactly as the spec mandates.
See INHERIT_TARIFF_ITEM_RATES below - the spec's premise that none of them has a
rate in the reference data does not hold for 4 of the 6, and this flag is the
single switch that changes the behaviour.

Usage:  python scripts/close_gap_v6.py
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import close_gap_content as G  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_FINAL = os.path.join(BASE, "enriched_final.jsonl")
IN_MERGED = os.path.join(BASE, "merged 1.jsonl")

OUT_COMPLETE = os.path.join(BASE, "enriched_complete.jsonl")
OUT_BLOCKLIST = os.path.join(BASE, "artifact_blocklist.json")
OUT_REPORT = os.path.join(BASE, "coverage_report.md")

# The spec states none of the 6 has a rate in merged, and its Hard Rules require
# all 6 to be emitted unresolved. That is what this script does by default.
# The premise is however only true of the *4-digit* codes: 4 of the 6 carry a
# rate at their 6- or 8-digit tariff-item form (see the report). Flip this to
# True to inherit those rates instead of emitting null.
INHERIT_TARIFF_ITEM_RATES = False

# 11 PRD chapters + demo exceptions + 87/48, which the spec explicitly confirms
# must be present (bolt test and packing-material test).
MVP_CHAPTERS = {
    "19", "20", "21", "28", "29", "33", "39", "61", "62", "73", "84",
    "22", "63", "90", "87", "48",
}
PRD_CHAPTERS = ["19", "20", "21", "28", "29", "33", "39", "61", "62", "73", "84"]

V6_SECTORS = {
    "Food & Beverages", "Textiles & Apparel", "Engineering & Machinery",
    "Chemicals & Pharmaceuticals", "Plastics & Rubber", "Metals & Metal Products",
    "Construction & Building Materials", "Professional Services",
    "Financial & Business Services", "Transport & Logistics Services",
    "IT & Software Services", "Repair & Maintenance Services", "Other",
}

RATE_KEY_ORDER = ["gst_rate", "cgst", "sgst", "igst", "rate_source", "cess",
                  "effective_from", "notification_no", "rate_confidence", "rate_scope",
                  "rate_caveat", "exemption_status", "exceptions", "history"]
AI_KEY_ORDER = ["synonyms", "market_terms", "hindi_transliterated", "examples", "attributes",
                "clarification_questions", "exclusion_notes", "classification_confidence",
                "plain_rationale", "one_line_rationale", "regulatory_citation"]
TOP_KEY_ORDER = ["id", "code", "entity_type", "title", "rate", "ai",
                 "search_text", "enrichment_status", "ai_checksum"]
ATTR_ORDER = ["material", "use", "form", "industry", "sector"]

UNRESOLVED_CAVEAT = (
    "No GST rate could be matched to this code from the notification schedules currently in "
    "the knowledge base. Consult a tax professional or check the CBIC portal directly.")

# Part C - hardcoded artifact list, verbatim from the spec.
BLOCKED_HARDCODED = collections.OrderedDict([
    ("1111", "Placeholder row - description is literally 'AKASH test'"),
    ("2031", "Chapter 02 artifact - 0203.1 (fresh/chilled swine meat), leading zero stripped"),
    ("2032", "Chapter 02 artifact - 0203.2 (frozen swine meat)"),
    ("2042", "Chapter 02 artifact - 0204.2 (sheep meat, fresh/chilled)"),
    ("2044", "Chapter 02 artifact - 0204.4 (sheep meat, frozen)"),
    ("2062", "Chapter 02 artifact - 0206.2 (bovine offal, frozen)"),
    ("2064", "Chapter 02 artifact - 0206.4 (swine offal, frozen)"),
    ("2071", "Chapter 02 artifact - 0207.1 (fowls, Gallus domesticus)"),
    ("2072", "Chapter 02 artifact - 0207.2 (turkeys)"),
    ("2073", "Chapter 02 artifact - 0207.3 (ducks, geese, guinea fowls)"),
    ("2075", "Chapter 02 artifact - 0207.5 (geese)"),
    ("2109", "Chapter 02 artifact - 0210.9 (meat flours and meals)"),
    ("2851", "Empty placeholder - description is '-'"),
])

# candidate_codes the spec supplies; cross-references may not go outside these.
CANDIDATES = {
    "2006": {"2001", "2002", "2003", "2004", "2005", "2007", "2008", "2009"},
    "2105": {"2101", "2102", "2103", "2104", "2106"},
}
CHEM_CANDIDATE_CHAPTER = "28"


class CloseError(RuntimeError):
    pass


def read_jsonl(p):
    if not os.path.exists(p):
        raise CloseError("required input not found: %s" % p)
    out = []
    with io.open(p, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError as e:
                raise CloseError("%s line %d: %s" % (p, n, e))
    return out


def dump_line(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def write_jsonl(p, recs):
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        for r in recs:
            fh.write(dump_line(r) + "\n")


def write_text(p, t):
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(t)


def ai_checksum(ai):
    return hashlib.sha256(json.dumps(ai, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def build_search_text(ai):
    parts = (list(ai["synonyms"]) + list(ai["market_terms"]) +
             list(ai["hindi_transliterated"]) + list(ai["examples"]))
    for k in ATTR_ORDER:
        parts += list(ai["attributes"].get(k, []))
    toks, seen = [], set()
    for p in parts:
        for t in re.sub(r"[,.;:()]", " ", str(p).lower()).split():
            if t not in seen:
                seen.add(t)
                toks.append(t)
    return " ".join(toks)


def order(d, keys, what):
    miss = [k for k in keys if k not in d]
    extra = [k for k in d if k not in keys]
    if miss or extra:
        raise CloseError("%s: missing=%s unexpected=%s" % (what, miss, extra))
    return collections.OrderedDict((k, d[k]) for k in keys)


def null_rate():
    """Exactly the block the spec mandates for all 6."""
    return order({
        "gst_rate": None, "cgst": None, "sgst": None, "igst": None,
        "rate_source": "none", "cess": None, "effective_from": None,
        "notification_no": None, "rate_confidence": "unresolved", "rate_scope": None,
        "rate_caveat": UNRESOLVED_CAVEAT, "exemption_status": "unknown",
        "exceptions": [], "history": [],
    }, RATE_KEY_ORDER, "rate")


def inherited_rate(m):
    tax, md = m.get("tax", {}) or {}, m.get("metadata", {}) or {}
    total = tax.get("gst_rate")
    if total is None:
        return null_rate()
    return order({
        "gst_rate": total, "cgst": total / 2, "sgst": total / 2, "igst": total,
        "rate_source": "merged", "cess": tax.get("cess"),
        "effective_from": tax.get("effective_from"),
        "notification_no": tax.get("notification_no"),
        "rate_confidence": md.get("rate_confidence") or "unresolved",
        "rate_scope": "heading",
        "rate_caveat": ("Rate inherited from the tariff-item entry %s; no entry exists for the "
                        "4-digit heading itself." % m.get("code")),
        "exemption_status": "taxable", "exceptions": [], "history": [],
    }, RATE_KEY_ORDER, "rate")


def build_record(code, spec, rate, allowed_refs):
    rid = "HSN_" + code
    sec = spec["sec"]
    for s in sec:
        if s not in V6_SECTORS:
            raise CloseError("%s: sector %r outside enum" % (rid, s))
    if not 1 <= len(sec) <= 2:
        raise CloseError("%s: sector must have 1-2 values" % rid)

    cqs = []
    for q, attr, opts, dis in spec.get("cq", []):
        for d in dis:
            if d not in allowed_refs:
                raise CloseError("%s: disambiguates_from %s outside candidate_codes" % (rid, d))
        cqs.append(collections.OrderedDict([
            ("question", q), ("attribute", attr), ("options", list(opts)),
            ("disambiguates_from", list(dis))]))
    xns = []
    for c, reason in spec.get("xn", []):
        if c not in allowed_refs:
            raise CloseError("%s: excluded_code %s outside candidate_codes" % (rid, c))
        xns.append(collections.OrderedDict([("excluded_code", c), ("reason", reason)]))

    if rate["gst_rate"] is None:
        rate_sent = (" No GST rate for this code could be matched from the notification "
                     "schedules currently in the knowledge base; confirm with your CA before "
                     "invoicing.")
    else:
        v = rate["gst_rate"]
        rate_sent = (" GST is %s%%, inherited from the tariff-item entry rather than matched to "
                     "the heading itself." % (("%d" % v) if float(v).is_integer() else v))
    tail = ""
    if spec.get("xn"):
        _, reason = spec["xn"][0]
        tail = " Note that %s%s." % (reason[0].lower(), reason[1:])

    ai = {
        "synonyms": list(spec.get("syn", [])),
        "market_terms": list(spec.get("mkt", [])),
        "hindi_transliterated": list(spec.get("hin", [])),
        "examples": list(spec.get("ex", [])),
        "attributes": collections.OrderedDict([
            ("material", list(spec.get("mat", []))),
            ("use", list(spec.get("use", []))),
            ("form", list(spec.get("frm", []))),
            ("industry", list(spec.get("ind", []))),
            ("sector", list(sec)),
        ]),
        "clarification_questions": cqs,
        "exclusion_notes": xns,
        # classification_confidence is deliberately independent of rate status.
        "classification_confidence": collections.OrderedDict([
            ("level", spec["lvl"]),
            ("rationale", spec["cr"]),
            ("ambiguity_triggers", list(spec.get("amb", []))),
        ]),
        "plain_rationale": "HSN %s covers %s.%s%s" % (code, spec["d"], rate_sent, tail),
        "one_line_rationale": None,
        "regulatory_citation": "ITC(HS) 2022, Chapter %s, Heading %s - %s." % (
            code[:2], code, spec["t"].rstrip(".")),
    }
    ai = order(ai, AI_KEY_ORDER, "ai")
    rec = {
        "id": rid, "code": code, "entity_type": "HSN", "title": spec["t"],
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": ai_checksum(ai),
    }
    return order(rec, TOP_KEY_ORDER, "record")


def validate(rec):
    errs = []
    r, ai = rec["rate"], rec["ai"]
    if rec["entity_type"] not in ("HSN", "SAC"):
        errs.append("NIC/unknown entity_type survived quarantine")
    if rec["code"] == "1111":
        errs.append("code 1111 (AKASH test artifact) present")
    if rec["entity_type"] == "HSN" and rec["code"][:2] not in MVP_CHAPTERS:
        errs.append("chapter %s out of scope" % rec["code"][:2])
    if r["gst_rate"] is None:
        if any(r[k] is not None for k in ("cgst", "sgst", "igst")):
            errs.append("null gst_rate but non-null split")
        if r["rate_source"] != "none":
            errs.append("null rate must have rate_source=none")
    else:
        if r["igst"] != r["gst_rate"]:
            errs.append("igst must equal gst_rate")
        if r["cgst"] != r["gst_rate"] / 2 or r["sgst"] != r["gst_rate"] / 2:
            errs.append("cgst/sgst must each be exactly half of gst_rate")
    if "composition_note" in r:
        errs.append("composition_note not removed")
    if r["rate_confidence"] == "unresolved" and r["gst_rate"] is not None:
        errs.append("unresolved rate carries a value")
    if r["rate_scope"] == "chapter" and not r["rate_caveat"]:
        errs.append("chapter-scope rate missing caveat")
    if len(r["history"]) > 3:
        errs.append("history exceeds 3 entries")
    secs = ai["attributes"].get("sector", [])
    if not 1 <= len(secs) <= 2:
        errs.append("sector must have 1-2 values")
    for s in secs:
        if s not in V6_SECTORS:
            errs.append("sector %r outside enum" % s)
    if "one_line_rationale" not in ai:
        errs.append("one_line_rationale key missing")
    return errs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=IN_FINAL)
    ap.add_argument("--outdir", default=BASE)
    args = ap.parse_args(argv)
    outdir = os.path.abspath(args.outdir)
    src = os.path.abspath(args.input)
    out_complete = os.path.join(outdir, os.path.basename(OUT_COMPLETE))
    if src == out_complete:
        raise CloseError("refusing to overwrite the input file")
    if not os.path.exists(src) and args.input == IN_FINAL:
        raise CloseError(
            "input not found: %s\n"
            "  It is a build artifact, not a source file. Regenerate it with:\n"
            "      python scripts/gap_fill_v6.py\n"
            "  then re-run this script." % os.path.basename(IN_FINAL))

    recs = read_jsonl(src)
    by_id = {r["id"]: r for r in recs}
    n_start = len(recs)

    # ---- Part C first: verify no blocklisted code is already present --------
    present_blocked = [c for c in BLOCKED_HARDCODED if ("HSN_" + c) in by_id]
    if present_blocked:
        raise CloseError("blocklisted codes already in the input: %r" % present_blocked)
    also_by_code = [r["id"] for r in recs if r["code"] in BLOCKED_HARDCODED]
    if also_by_code:
        raise CloseError("blocklisted codes present by code: %r" % also_by_code)

    # ---- index merged -------------------------------------------------------
    h4, tariff_forms, real_codes = {}, collections.defaultdict(list), set()
    for line in io.open(IN_MERGED, "r", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        m = json.loads(line)
        et, c = m.get("entity_type"), m.get("code") or ""
        if et not in ("HSN", "SAC") or not c:
            continue
        real_codes.add("%s_%s" % (et, c))
        if et != "HSN":
            continue
        if len(c) == 4:
            h4.setdefault(c, m)
        if len(c) >= 6:
            tariff_forms[c[:4]].append(m)

    # ---- the spec's premise check ------------------------------------------
    rate_evidence = {}
    for code in G.GAP6:
        in_h4 = code in h4
        best = None
        for m in sorted(tariff_forms.get(code, []), key=lambda x: len(x["code"])):
            if m.get("tax", {}).get("gst_rate") is not None:
                best = m
                break
        rate_evidence[code] = {
            "four_digit_in_merged": in_h4,
            "tariff_item": None if best is None else best["code"],
            "tariff_rate": None if best is None else best["tax"]["gst_rate"],
            "tariff_conf": None if best is None else best.get("metadata", {}).get("rate_confidence"),
        }

    # ---- Part A: build the 6 -----------------------------------------------
    added = []
    for code in sorted(G.GAP6):
        rid = "HSN_" + code
        if rid in by_id:
            raise CloseError("%s already exists; refusing to overwrite" % rid)
        if code in BLOCKED_HARDCODED:
            raise CloseError("%s is blocklisted and must never be enriched" % rid)
        spec = G.GAP6[code]
        if code in CANDIDATES:
            allowed = {"HSN_" + c for c in CANDIDATES[code]}
        else:
            allowed = {r["id"] for r in recs
                       if r["entity_type"] == "HSN" and r["code"][:2] == CHEM_CANDIDATE_CHAPTER}
        ev = rate_evidence[code]
        if INHERIT_TARIFF_ITEM_RATES and ev["tariff_item"]:
            rate = inherited_rate(next(m for m in tariff_forms[code]
                                       if m["code"] == ev["tariff_item"]))
        else:
            rate = null_rate()
        rec = build_record(code, spec, rate, allowed)
        recs.append(rec)
        by_id[rid] = rec
        added.append(rid)

    # ---- Part C: artifact scan ---------------------------------------------
    # The spec's rule keys on HSN_MSTR's ALL-CAPS heading convention. That file is
    # absent; merged does not use that convention (1020 of 1113 headings are
    # mostly lowercase), so running the rule here yields ~90 false positives.
    # Instead the scan is run and its unusability measured, and reported as such.
    scan_stats = {"headings": len(h4), "allcaps": 0, "mostly_lower": 0}
    naive_hits = []
    for c, m in sorted(h4.items()):
        t = (m.get("title") or "").split(" > ")[-1].strip()
        letters = [ch for ch in t if ch.isalpha()]
        if not letters:
            naive_hits.append(c)
            continue
        ratio = sum(1 for ch in letters if ch.isupper()) / len(letters)
        if ratio > 0.9:
            scan_stats["allcaps"] += 1
        if ratio < 0.3:
            scan_stats["mostly_lower"] += 1
            if len(t) < 28:
                naive_hits.append(c)
    scan_detected = []  # nothing defensible found in the available source

    blocklist = collections.OrderedDict()
    blocklist["blocked_codes"] = collections.OrderedDict(BLOCKED_HARDCODED)
    blocklist["_meta"] = collections.OrderedDict([
        ("purpose", "Codes that exist in HSN_MSTR but are not real HSN headings. Never index, "
                    "enrich, or return these."),
        ("hardcoded_count", len(BLOCKED_HARDCODED)),
        ("scan_detected_count", len(scan_detected)),
        ("scan_detected", scan_detected),
        ("scan_status", "NOT RUN - source unavailable"),
        ("scan_note", "The spec's detection rule keys on HSN_MSTR's ALL-CAPS heading convention. "
                      "HSN_SAC.xlsx is not present in the project. The rule was trialled against "
                      "the substitute source (merged 1.jsonl) and is not transferable: only %d of "
                      "%d headings there are ALL-CAPS while %d are mostly lowercase, so the rule "
                      "flags %d ordinary headings such as 'Live bovine animals.' as artifacts. "
                      "No scan-detected additions are claimed. Re-run against HSN_MSTR when it is "
                      "available."
         % (scan_stats["allcaps"], scan_stats["headings"], scan_stats["mostly_lower"],
            len(naive_hits))),
        ("verified_absent_from_output", True),
        ("verified_absent_from_merged", sorted(c for c in BLOCKED_HARDCODED
                                               if ("HSN_" + c) not in real_codes)),
    ])

    # ---- Part D: validate ---------------------------------------------------
    val_errs = []
    for r in recs:
        for e in validate(r):
            val_errs.append((r["id"], e))
    dup = [i for i, n in collections.Counter(r["id"] for r in recs).items() if n > 1]
    if dup:
        raise CloseError("duplicate ids: %r" % dup[:5])

    leaked = [r["id"] for r in recs if r["code"] in BLOCKED_HARDCODED]
    if leaked:
        raise CloseError("blocklisted code present in output: %r" % leaked)

    # cross-reference integrity
    known = set(by_id) | real_codes
    ref_errs = []
    for r in recs:
        for x in r["ai"]["exclusion_notes"]:
            if x["excluded_code"] not in known:
                ref_errs.append((r["id"], x["excluded_code"]))
        for q in r["ai"]["clarification_questions"]:
            for d in q.get("disambiguates_from", []):
                if d not in known:
                    ref_errs.append((r["id"], d))
    ck_errs = [r["id"] for r in recs if r["ai_checksum"] != ai_checksum(r["ai"])]

    # ---- rate drift ---------------------------------------------------------
    mindex = {}
    for line in io.open(IN_MERGED, "r", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        m = json.loads(line)
        if m.get("entity_type") in ("HSN", "SAC"):
            mindex.setdefault((m["entity_type"], m.get("code")), m)
    drift, skipped, compared = [], 0, 0
    for r in recs:
        if r["rate"]["rate_source"] == "manual_seed":
            skipped += 1
            continue
        m = mindex.get((r["entity_type"], r["code"]))
        if m is None:
            continue
        compared += 1
        if r["rate"]["gst_rate"] != m.get("tax", {}).get("gst_rate"):
            drift.append((r["id"], m.get("tax", {}).get("gst_rate"), r["rate"]["gst_rate"]))

    if val_errs:
        for i, e in val_errs[:40]:
            sys.stderr.write("VALIDATION %s: %s\n" % (i, e))
        raise CloseError("validation failed with %d error(s); nothing written" % len(val_errs))
    if ref_errs:
        for i, e in ref_errs[:20]:
            sys.stderr.write("REF %s -> %s\n" % (i, e))
        raise CloseError("%d invented cross-reference(s); nothing written" % len(ref_errs))
    if ck_errs:
        raise CloseError("%d stale checksum(s); nothing written" % len(ck_errs))
    if drift:
        for d in drift[:20]:
            sys.stderr.write("DRIFT %r\n" % (d,))
        raise CloseError("rate drift on %d record(s); nothing written" % len(drift))

    ctx = dict(n_start=n_start, recs=recs, by_id=by_id, added=added, h4=h4,
               rate_evidence=rate_evidence, blocklist=blocklist, scan_stats=scan_stats,
               naive_hits=naive_hits, compared=compared, skipped=skipped)
    report = build_report(ctx)

    write_jsonl(out_complete, recs)
    write_text(os.path.join(outdir, os.path.basename(OUT_BLOCKLIST)),
               json.dumps(blocklist, ensure_ascii=False, indent=2) + "\n")
    write_text(os.path.join(outdir, os.path.basename(OUT_REPORT)), report)

    print("start        : %d" % n_start)
    print("added        : +%d %s" % (len(added), [a.replace("HSN_", "") for a in added]))
    print("final        : %d -> %s" % (len(recs), os.path.basename(out_complete)))
    print("blocklist    : %d codes -> %s" % (len(BLOCKED_HARDCODED),
                                             os.path.basename(OUT_BLOCKLIST)))
    print("validation   : PASS (0 errors)")
    print("rate drift   : PASS (%d compared, %d manual_seed skipped)" % (compared, skipped))
    print("blocked leak : PASS (none present)")
    print("rates emitted: all 6 null (INHERIT_TARIFF_ITEM_RATES=%s)" % INHERIT_TARIFF_ITEM_RATES)
    return 0


def build_report(ctx):
    L, add = [], None
    L = []
    add = L.append
    recs, by_id, h4 = ctx["recs"], ctx["by_id"], ctx["h4"]
    hsn = [r for r in recs if r["entity_type"] == "HSN"]
    sac = [r for r in recs if r["entity_type"] == "SAC"]

    add("# Coverage report - `enriched_final.jsonl` -> `enriched_complete.jsonl`")
    add("")
    add("Project: IRIS-HACK-P-2026-001 - GST Classification Engine  ")
    add("Script: `scripts/close_gap_v6.py` + `scripts/close_gap_content.py`")
    add("")
    add("## Headline")
    add("")
    add("| | |")
    add("|---|---|")
    add("| Starting records | %d |" % ctx["n_start"])
    add("| Added (Part A) | +%d |" % len(ctx["added"]))
    add("| **Final total** | **%d** |" % len(recs))
    add("| Validator errors | 0 |")
    add("| Rate drift | 0 |")
    add("| Blocklisted codes in output | 0 |")
    add("")

    # --- the premise problem, up front
    add("## Read first - the spec's rate premise does not hold")
    add("")
    add("Part A states: *\"None of these 6 has a rate in `merged_1.jsonl`.\"* That is true of the "
        "**4-digit** codes - none of the six exists as a 4-digit heading in the reference data. "
        "But **4 of the 6 carry a rate at their 6- or 8-digit tariff-item form**:")
    add("")
    add("| Code | 4-digit in merged | Tariff item | Rate there | Confidence | Emitted as |")
    add("|---|---|---|---:|---|---|")
    for code in sorted(G.GAP6):
        e = ctx["rate_evidence"][code]
        add("| `%s` | %s | %s | %s | %s | **null** |" % (
            code, "yes" if e["four_digit_in_merged"] else "no",
            "`%s`" % e["tariff_item"] if e["tariff_item"] else "-",
            "%g%%" % e["tariff_rate"] if e["tariff_rate"] is not None else "-",
            e["tariff_conf"] or "-"))
    add("")
    add("**All 6 were emitted `null` anyway**, because the spec's Hard Rules say so three times "
        "over (\"Do not seed rates for these\", \"All 6 new records are `unresolved` with "
        "`gst_rate: null`. No seeding.\"). An explicit instruction was followed rather than "
        "quietly overridden - but you should know what it costs:")
    add("")
    add("- **`2105` (ice cream) is the one that hurts.** The spec calls it \"the one that "
        "matters\" and a real MSME product. Its tariff item `21050000` carries **5% at `high` "
        "confidence** - the highest-confidence rate evidence available for any of the six. It "
        "will nonetheless display \"rate unavailable\".")
    add("- Two of the six (`2838`, `2848`) are genuinely absent from the reference data in every "
        "form, so `null` is unarguably correct for them.")
    add("")
    add("**One caution against flipping this blindly.** The reference file also holds two "
        "conflicting `GST_RATE` rows for `21050000`, at 18% and 5%. Ice cream has historically "
        "been taxed at 18%, so the `high`-confidence 5% on the master record may itself be a "
        "data problem. Emitting `null` is arguably the safer of two imperfect options - which is "
        "a defence of the spec's outcome, not of its stated reason.")
    add("")
    add("To change the behaviour, set `INHERIT_TARIFF_ITEM_RATES = True` in "
        "`scripts/close_gap_v6.py` and re-run. It is a single flag; nothing else needs editing.")
    add("")

    # --- Part A
    add("## Part A - The 6 added headings")
    add("")
    add("| Code | Title | Sector | Confidence | Rate status |")
    add("|---|---|---|---|---|")
    for rid in ctx["added"]:
        r = by_id[rid]
        add("| `%s` | %s | %s | %s | `%s` / `%s` |" % (
            r["code"], r["title"][:56], ", ".join(r["ai"]["attributes"]["sector"]),
            r["ai"]["classification_confidence"]["level"],
            r["rate"]["rate_confidence"], r["rate"]["rate_source"]))
    add("")
    add("`classification_confidence` is independent of rate status, as the spec requires: "
        "`2105` is **High** confidence on classification while its rate is `unresolved`. The "
        "missing rate did not drag the classification score down on any of the six.")
    add("")
    r2105 = by_id["HSN_2105"]
    q = r2105["ai"]["clarification_questions"][0]
    add("**`2105` boundary question** (required by the spec, separating it from `2106`):")
    add("")
    add("> %s" % q["question"])
    add(">")
    add("> attribute `%s` - options: %s - disambiguates from %s"
        % (q["attribute"], " / ".join(q["options"]),
           ", ".join("`%s`" % d for d in q["disambiguates_from"])))
    add("")
    r2006 = by_id["HSN_2006"]
    add("**`2006` exclusion notes** (required against `2007` and `2008`): %s"
        % ", ".join("`%s`" % x["excluded_code"] for x in r2006["ai"]["exclusion_notes"]))
    add("")
    add("All cross-references were validated against the spec's `candidate_codes` lists at build "
        "time - a reference outside the supplied candidates fails the build.")
    add("")

    # --- Part B
    add("## Part B - `2851` skipped")
    add("")
    add("Not enriched. Its `HSN_MSTR` description is a single hyphen, so any record would have "
        "been fabricated. It is in the blocklist instead. Confirmed absent from the output and "
        "from the reference data in every form.")
    add("")

    # --- Part C
    add("## Part C - Artifact blocklist")
    add("")
    add("`artifact_blocklist.json` holds **%d** codes." % len(BLOCKED_HARDCODED))
    add("")
    add("| Code | Reason |")
    add("|---|---|")
    for c, why in BLOCKED_HARDCODED.items():
        add("| `%s` | %s |" % (c, why))
    add("")
    add("**Verified:** none of the %d appears in `enriched_complete.jsonl`, checked by both id "
        "and raw code. The build fails loudly if one ever does. All %d are also absent from the "
        "reference data entirely, which corroborates that they are an export artifact of "
        "`HSN_MSTR` rather than real headings."
        % (len(BLOCKED_HARDCODED),
           len(ctx["blocklist"]["_meta"]["verified_absent_from_merged"])))
    add("")
    add("### Systematic scan - NOT RUN, and why")
    add("")
    add("The spec asks to scan every 4-digit code in `HSN_MSTR` and flag descriptions that are "
        "lowercase fragments rather than ALL-CAPS heading text. **`HSN_SAC.xlsx` is not present "
        "in the project**, so that scan cannot be run against its intended source.")
    add("")
    add("The rule was trialled against the substitute source to see whether it transfers. "
        "It does not:")
    add("")
    add("| | |")
    add("|---|---:|")
    add("| 4-digit headings available | %d |" % ctx["scan_stats"]["headings"])
    add("| ALL-CAPS (>90%% upper) | %d |" % ctx["scan_stats"]["allcaps"])
    add("| Mostly lowercase (<30%% upper) | %d |" % ctx["scan_stats"]["mostly_lower"])
    add("| Codes the rule would flag | %d |" % len(ctx["naive_hits"]))
    add("")
    add("The reference file does not use the ALL-CAPS convention the rule depends on, so it "
        "flags ordinary headings - `0102 Live bovine animals.`, `1006 Rice.`, `2524 Asbestos.` - "
        "as artifacts. Reporting those as scan-detected additions would be worse than reporting "
        "nothing.")
    add("")
    add("**No scan-detected additions are claimed.** `artifact_blocklist.json` records "
        "`scan_status: \"NOT RUN - source unavailable\"` so the gap is visible to whatever reads "
        "it. Re-run against `HSN_MSTR` when the workbook is available; the spec's warning that "
        "\"there may be more in chapters we haven't audited\" remains unaddressed and is the "
        "main open risk from this task.")
    add("")
    add("### Wiring it in")
    add("")
    add("The blocklist is data, not enforcement. Whatever loads the knowledge base must skip "
        "these codes at index time. Minimal integration:")
    add("")
    add("```python")
    add("import json")
    add("BLOCKED = set(json.load(open('artifact_blocklist.json'))['blocked_codes'])")
    add("records = [r for r in records if r['code'] not in BLOCKED]")
    add("```")
    add("")

    # --- coverage
    add("## Coverage - PRD chapters against real headings")
    add("")
    add("Denominator is 4-digit headings present in the reference data, with blocklisted "
        "artifacts excluded. Artifacts never entered the count because they are absent from that "
        "source to begin with.")
    add("")
    add("| Chapter | Enriched | Real headings | Coverage |")
    add("|---|---:|---:|---:|")
    tot_e = tot_r = 0
    rows = []
    for ch in PRD_CHAPTERS:
        real = {c for c in h4 if c[:2] == ch} | {r["code"] for r in hsn
                                                 if r["code"][:2] == ch and len(r["code"]) == 4}
        real -= set(BLOCKED_HARDCODED)
        enr = {r["code"] for r in hsn if r["code"][:2] == ch and len(r["code"]) == 4} & real
        tot_e += len(enr)
        tot_r += len(real)
        pct = 100.0 * len(enr) / len(real) if real else 100.0
        rows.append((ch, len(enr), len(real), pct))
        add("| %s | %d | %d | %s |" % (ch, len(enr), len(real),
                                       "**%.1f%%**" % pct if pct < 95 else "%.1f%%" % pct))
    add("| **All 11** | **%d** | **%d** | **%.1f%%** |" % (tot_e, tot_r, 100.0*tot_e/tot_r))
    add("")
    below = [r for r in rows if r[3] < 95.0]
    if below:
        add("**Below 95%%:** %s" % ", ".join("chapter %s (%.1f%%)" % (r[0], r[3]) for r in below))
    else:
        add("**All 11 PRD chapters are at 100%% of the real headings available in the reference "
            "data.** Every 4-digit heading the source knows about in these chapters is enriched.")
    add("")
    add("> **Caveat on the denominator.** The spec cites 306 real headings and 93%% coverage. "
        "That count comes from `HSN_MSTR`, which is absent. The reference data available here "
        "holds %d headings across the 11 chapters. The 6 added codes are real headings the "
        "reference data does not carry as 4-digit entries at all - which is precisely why they "
        "were missing. So the figure above (%d/%d) is measured against the only denominator that "
        "can be verified offline, and is **not** directly comparable to the spec's 306. Against "
        "the spec's own denominator the result would be %d/306 = %.1f%%, which clears the 95%% "
        "bar - but that arithmetic rests on the spec's count, not on anything checkable here."
        % (tot_r - len(ctx["added"]), tot_e, tot_r, tot_e, 100.0*tot_e/306))
    add("")

    # --- SAC unchanged
    secs = collections.Counter(s for r in sac for s in r["ai"]["attributes"]["sector"])
    add("## SAC - unchanged, as expected")
    add("")
    add("SAC records: **%d** across **%d** sectors. This task touched no SAC record."
        % (len(sac), len(secs)))
    add("")
    add("| Sector | Codes |")
    add("|---|---:|")
    for s, n in sorted(secs.items(), key=lambda kv: (-kv[1], kv[0])):
        add("| %s | %d |" % (s, n))
    add("")

    # --- validation
    add("## Validation and rate drift")
    add("")
    add("**Validator: PASS** - all %d records, zero errors, using `MVP_CHAPTERS` including "
        "`\"87\"` and `\"48\"` as the spec instructs. Those three records (`8708`, `8714`, "
        "`4819`) are deliberately in scope and produce no errors." % len(recs))
    add("")
    add("Also passing:")
    add("")
    add("- `ai_checksum` matches the `ai` object on all %d records" % len(recs))
    add("- every cross-reference resolves to a real code; the 6 new records' references were "
        "additionally constrained to the spec's `candidate_codes` at build time")
    add("- no blocklisted code present, checked by id and by raw code")
    add("- the 6 new records carry `gst_rate: null`, `rate_source: \"none\"`, "
        "`rate_confidence: \"unresolved\"`, `exemption_status: \"unknown\"`, empty `exceptions` "
        "and `history`, and the standard unresolved caveat")
    add("")
    add("**Rate drift: PASS.** %d records compared against the reference data on "
        "`(entity_type, code)`; zero differences. %d `manual_seed` records skipped as required. "
        "The 6 new records do not participate - their 4-digit codes are absent from the source, "
        "so there is nothing to drift against." % (ctx["compared"], ctx["skipped"]))
    add("")

    add("## Notes")
    add("")
    add("- `HSN_SAC.xlsx` and `enrichment_prompt_v6.md` are both absent. Titles for the 6 new "
        "records were taken from the spec's own table; enrichment style was matched to the "
        "existing 333 records, which the schema rule makes authoritative anyway.")
    add("- The reference file is `merged 1.jsonl` on disk, not `merged_1.jsonl`.")
    add("- The 6 new records carry `one_line_rationale: null`. None is on the demo path, and the "
        "gap-fill task set that policy.")
    add("- Re-running this script produces a byte-identical `enriched_complete.jsonl`; re-running "
        "it against its own output fails loudly rather than double-applying.")
    add("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CloseError as e:
        sys.stderr.write("\nCLOSE-GAP FAILED: %s\n" % e)
        sys.exit(1)
