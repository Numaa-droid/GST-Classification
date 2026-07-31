#!/usr/bin/env python3
"""
Fill the remaining MVP content gaps on top of the v6 file.

Parts A-C add new records (Chapter 84, auto parts, SAC breadth); Part D applies
the manual demo seeds and the demo-path one-liners.

Inputs  : updat_enriched.jsonl (224, v6), quarantine.jsonl, merged 1.jsonl
Outputs : enriched_final.jsonl, demo_seed.json, gap_report.md

Rate values are only ever copied from `merged 1.jsonl` or taken from
demo_seed.json with a source_note. Nothing is invented. Everything mechanical
(split, history, search_text, checksum) is derived, never typed by hand.

Usage:  python scripts/gap_fill_v6.py
"""

from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gap_content as C  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IN_CUR = os.path.join(BASE, "updat_enriched.jsonl")
IN_QUAR = os.path.join(BASE, "quarantine.jsonl")
IN_MERGED = os.path.join(BASE, "merged 1.jsonl")

OUT_FINAL = os.path.join(BASE, "enriched_final.jsonl")
OUT_SEED = os.path.join(BASE, "demo_seed.json")
OUT_REPORT = os.path.join(BASE, "gap_report.md")

# Chapter 87 is added for the bolt test (8708/8714) and 48 to restore HSN_4819,
# which the gap spec's Part D2 one-liner list requires. Both were out of scope
# under the v6 patch; see the report for the rationale.
MVP_CHAPTERS = {
    "19", "20", "21", "28", "29", "33", "39", "61", "62", "73", "84",
    "22", "63", "90",
    "87", "48",
}
CHAPTERS_ADDED_HERE = {"87", "48"}

V6_SECTORS = {
    "Food & Beverages", "Textiles & Apparel", "Engineering & Machinery",
    "Chemicals & Pharmaceuticals", "Plastics & Rubber", "Metals & Metal Products",
    "Construction & Building Materials", "Professional Services",
    "Financial & Business Services", "Transport & Logistics Services",
    "IT & Software Services", "Repair & Maintenance Services", "Other",
}

# Records restored from quarantine were parked before the v6 patch ran, so they
# still carry v5 sector values and need the same remap applied.
SECTOR_REMAP = {
    "Agriculture & Live Animals":  "Food & Beverages",
    "Consumer Goods & Household":  "Other",
    "Minerals & Energy":           "Other",
    "Automotive & Transport":      "Engineering & Machinery",
    "Wood, Paper & Packaging":     "Other",
}

RATE_KEY_ORDER = [
    "gst_rate", "cgst", "sgst", "igst", "rate_source",
    "cess", "effective_from", "notification_no",
    "rate_confidence", "rate_scope", "rate_caveat",
    "exemption_status", "exceptions", "history",
]
AI_KEY_ORDER = [
    "synonyms", "market_terms", "hindi_transliterated", "examples", "attributes",
    "clarification_questions", "exclusion_notes", "classification_confidence",
    "plain_rationale", "one_line_rationale", "regulatory_citation",
]
TOP_KEY_ORDER = ["id", "code", "entity_type", "title", "rate", "ai",
                 "search_text", "enrichment_status", "ai_checksum"]
ATTR_ORDER = ["material", "use", "form", "industry", "sector"]

UNRESOLVED_CAVEAT = (
    "No GST rate could be matched to this code from the notification schedules "
    "currently in the knowledge base. Consult a tax professional or check the "
    "CBIC portal directly."
)
MAX_HISTORY = 3
ONE_LINER_MAX = 120


class GapError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Part D1 - manual demo seeds. Every entry carries a source_note.
# ---------------------------------------------------------------------------

DEMO_SEED = {
    "HSN_6307": {
        "gst_rate": 5.0,
        "effective_from": "2022-05-01",
        "notification_no": "1/2017-Central Tax (Rate), Schedule I entry 224",
        "rate_confidence": "medium",
        "rate_scope": "heading",
        "rate_source": "manual_seed",
        "source_note": (
            "Seeded from CGST ready reckoner 01.05.2022, Schedule I entry 224 - other made up "
            "textile articles, sale value not exceeding Rs 1000 per piece (2.5% CGST = 5% total). "
            "Figure supplied by the task specification. NOT independently verified against the "
            "CBIC portal: this build runs offline with no network access, so the notification "
            "text could not be re-read. The 2022 reckoner predates the 2025 rate revision and "
            "Notification 9/2025-Integrated Tax (Rate) was not cross-checked for this heading - "
            "confirm before any figure is relied on for invoicing."
        ),
    },
    "HSN_63079091": {
        "gst_rate": 5.0,
        "effective_from": "2022-05-01",
        "notification_no": "1/2017-Central Tax (Rate), Schedule I entry 224",
        "rate_confidence": "low",
        "rate_scope": "heading",
        "rate_source": "manual_seed",
        "source_note": (
            "Inherited from the seeded parent heading HSN_6307, of which 63079091 (textile face "
            "masks without a replaceable filter or mechanical parts) is a tariff item. No entry "
            "specific to 63079091 exists in the knowledge base, so the heading-level figure is "
            "applied and rate_scope is recorded as 'heading'. rate_confidence is deliberately "
            "set one step lower than the parent ('low') because the value is inherited rather "
            "than matched. Carries the same caveats as HSN_6307: supplied by the task "
            "specification, not independently verified offline, and predating the 2025 revision."
        ),
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_jsonl(path):
    if not os.path.exists(path):
        raise GapError("required input not found: %s" % path)
    out = []
    with io.open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError as e:
                raise GapError("%s line %d: %s" % (path, n, e))
    return out


def dump_line(o):
    return json.dumps(o, ensure_ascii=False, separators=(",", ":"))


def write_jsonl(path, recs):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in recs:
            fh.write(dump_line(r))
            fh.write("\n")


def write_text(path, text):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def ai_checksum(ai):
    return hashlib.sha256(json.dumps(ai, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def build_search_text(ai):
    """Reproduces the rule used by the existing 224 records: lowercase, split on
    whitespace and [,.;:()], dedupe preserving first-occurrence order, over
    synonyms + market_terms + hindi + examples + material/use/form/industry/sector.
    Verified to reproduce 218/224 existing values exactly (the 6 misses are
    records whose search_text predates the v6 sector remap)."""
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


def fmt_rate(v):
    return ("%d" % v) if float(v).is_integer() else ("%s" % v)


def order_rate(r):
    missing = [k for k in RATE_KEY_ORDER if k not in r]
    if missing:
        raise GapError("rate missing keys %s" % missing)
    extra = [k for k in r if k not in RATE_KEY_ORDER]
    if extra:
        raise GapError("rate has unexpected keys %s" % extra)
    return collections.OrderedDict((k, r[k]) for k in RATE_KEY_ORDER)


def order_ai(a):
    missing = [k for k in AI_KEY_ORDER if k not in a]
    if missing:
        raise GapError("ai missing keys %s" % missing)
    extra = [k for k in a if k not in AI_KEY_ORDER]
    if extra:
        raise GapError("ai has unexpected keys %s" % extra)
    out = collections.OrderedDict((k, a[k]) for k in AI_KEY_ORDER)
    out["attributes"] = collections.OrderedDict(
        (k, out["attributes"].get(k, [])) for k in ATTR_ORDER)
    return out


def order_top(r):
    return collections.OrderedDict((k, r[k]) for k in TOP_KEY_ORDER)


# ---------------------------------------------------------------------------
# Record construction
# ---------------------------------------------------------------------------

def build_rate_from_merged(m):
    """Copy the rate straight out of merged, then derive the split. No invention."""
    tax = m.get("tax", {}) or {}
    md = m.get("metadata", {}) or {}
    total = tax.get("gst_rate")
    scope = md.get("rate_scope")

    hist = [{"effective_from": a, "gst_rate": b} for a, b in (md.get("superseded_rates") or [])]
    hist = sorted(hist, key=lambda h: (h["effective_from"] is None, h["effective_from"] or ""))
    seen, ded = set(), []
    for h in hist:
        k = (h["effective_from"], h["gst_rate"])
        if k not in seen:
            seen.add(k)
            ded.append(h)
    hist = ded[-MAX_HISTORY:]

    exc = [{"gst_rate": e.get("gst_rate"), "condition": e.get("basis")}
           for e in (md.get("rate_exceptions") or [])]

    r = {
        "gst_rate": total,
        "cgst": None if total is None else total / 2,
        "sgst": None if total is None else total / 2,
        "igst": None if total is None else total,
        "rate_source": "none" if total is None else "merged",
        "cess": tax.get("cess"),
        "effective_from": tax.get("effective_from"),
        "notification_no": tax.get("notification_no"),
        "rate_confidence": md.get("rate_confidence") or "unresolved",
        "rate_scope": scope,
        "rate_caveat": UNRESOLVED_CAVEAT if total is None else None,
        "exemption_status": "unknown" if total is None else "taxable",
        "exceptions": exc,
        "history": hist,
    }
    return order_rate(r)


def compose_plain_rationale(kind, code, spec, rate):
    """Rate sentence is generated from the actual rate block, never typed by hand,
    so a rationale can never state a rate the record does not carry."""
    head = "%s %s covers %s." % (kind, code, spec["d"])
    total = rate["gst_rate"]
    if total is None:
        rate_sent = (" No GST rate for this code could be matched from the notification "
                     "schedules currently in the knowledge base; confirm with your CA "
                     "before invoicing.")
    else:
        where = {"heading": "matched at the heading level",
                 "chapter": "inferred from the chapter-wide entry",
                 "subheading": "matched at the subheading level",
                 "tariff_item": "matched at the tariff-item level"}.get(
                     rate["rate_scope"], "matched from the rate schedules")
        rate_sent = " GST is %s%%, %s." % (fmt_rate(total), where)
    tail = ""
    if spec.get("xn"):
        ex_code, ex_reason = spec["xn"][0]
        tail = " Note that %s" % ex_reason[0].lower() + ex_reason[1:] + "."
    if spec.get("extra"):
        tail += " " + spec["extra"]
    return head + rate_sent + tail


def build_record(kind, code, spec, m, chapter_label):
    ent = "HSN" if kind == "HSN" else "SAC"
    rid = "%s_%s" % (ent, code)
    rate = build_rate_from_merged(m)

    sec = spec.get("sec") or ([C.ENG] if ent == "HSN" else [C.PRO])
    for s in sec:
        if s not in V6_SECTORS:
            raise GapError("%s: sector %r outside v6 enum" % (rid, s))
    if not 1 <= len(sec) <= 2:
        raise GapError("%s: sector must have 1-2 values" % rid)

    cqs = []
    for q, attr, opts, dis in spec.get("cq", []):
        cqs.append(collections.OrderedDict([
            ("question", q), ("attribute", attr), ("options", list(opts)),
            ("disambiguates_from", list(dis)),
        ]))
    xns = [collections.OrderedDict([("excluded_code", c), ("reason", r)])
           for c, r in spec.get("xn", [])]

    ai = {
        "synonyms": list(spec.get("syn", [])),
        "market_terms": list(spec.get("mkt", [])),
        "hindi_transliterated": list(spec.get("hin", [])),
        "examples": list(spec.get("ex", [])),
        "attributes": {
            "material": list(spec.get("mat", [])),
            "use": list(spec.get("use", [])),
            "form": list(spec.get("frm", [])),
            "industry": list(spec.get("ind", [])),
            "sector": list(sec),
        },
        "clarification_questions": cqs,
        "exclusion_notes": xns,
        "classification_confidence": collections.OrderedDict([
            ("level", spec.get("lvl", "Medium")),
            ("rationale", spec.get("cr") or
             ("Heading description maps cleanly to the goods; the main risk is confusion with "
              "neighbouring headings in the same chapter.")),
            ("ambiguity_triggers", list(spec.get("amb", []))),
        ]),
        "plain_rationale": compose_plain_rationale(ent, code, spec, rate),
        "one_line_rationale": None,
        "regulatory_citation": None,
    }
    cite = "%s, %s, Heading %s - %s." % (
        "ITC(HS) 2022" if ent == "HSN" else "Scheme of Classification of Services (SAC)",
        chapter_label, code, spec["t"].rstrip("."))
    if rate["notification_no"]:
        cite += " Rate per Notification %s." % rate["notification_no"]
    ai["regulatory_citation"] = cite

    ai = order_ai(ai)
    rec = {
        "id": rid, "code": code, "entity_type": ent, "title": spec["t"],
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": spec.get("st", "complete"),
        "ai_checksum": ai_checksum(ai),
    }
    return order_top(rec)


# ---------------------------------------------------------------------------
# Validation (patch-spec validator, verbatim)
# ---------------------------------------------------------------------------

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
    if len(r["history"]) > MAX_HISTORY:
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


def validate_extra(rec, known_ids, check_search_text):
    errs = []
    r, ai = rec["rate"], rec["ai"]
    if r["gst_rate"] is not None and r["rate_source"] not in ("merged", "manual_seed"):
        errs.append("resolved rate with rate_source=%r" % r["rate_source"])
    if r["rate_source"] not in ("merged", "manual_seed", "none"):
        errs.append("rate_source %r outside enum" % r["rate_source"])
    if rec["ai_checksum"] != ai_checksum(ai):
        errs.append("ai_checksum stale")
    if list(r.keys()) != RATE_KEY_ORDER:
        errs.append("rate key order drifted")
    if list(ai.keys()) != AI_KEY_ORDER:
        errs.append("ai key order drifted")
    # Only enforced on records this script authors or touches. Six pre-existing
    # chapter-33 records have a search_text that predates the v6 sector remap;
    # they are reported rather than silently rewritten.
    if check_search_text and rec["search_text"] != build_search_text(ai):
        errs.append("search_text does not match the ai object")
    ol = ai["one_line_rationale"]
    if ol is not None and len(ol) > ONE_LINER_MAX:
        errs.append("one_line_rationale is %d chars (limit %d)" % (len(ol), ONE_LINER_MAX))
    # No invented codes. The spec allows a reference to a code that is real but not
    # yet enriched (the existing data already does this - HSN_2106 -> HSN_21069020),
    # so `known_ids` is the enriched set plus every real HSN/SAC code in the
    # reference tariff. A reference resolving to neither is a fabrication.
    for x in ai["exclusion_notes"]:
        if x["excluded_code"] not in known_ids:
            errs.append("exclusion_notes references non-existent code %s" % x["excluded_code"])
    for q in ai["clarification_questions"]:
        for d in q.get("disambiguates_from", []):
            if d not in known_ids:
                errs.append("disambiguates_from references non-existent code %s" % d)
    return errs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=IN_CUR)
    ap.add_argument("--outdir", default=BASE)
    args = ap.parse_args(argv)
    outdir = os.path.abspath(args.outdir)
    out_final = os.path.join(outdir, os.path.basename(OUT_FINAL))
    out_seed = os.path.join(outdir, os.path.basename(OUT_SEED))
    out_report = os.path.join(outdir, os.path.basename(OUT_REPORT))

    notes = []
    in_enriched = os.path.abspath(args.input)
    # updat_enriched.jsonl is a renamed enriched_v6.jsonl - accept either, and if
    # neither exists say which stage regenerates it rather than just "not found".
    if not os.path.exists(in_enriched) and args.input == IN_CUR:
        alt = os.path.join(BASE, "enriched_v6.jsonl")
        if os.path.exists(alt):
            in_enriched = alt
        else:
            raise GapError(
                "input not found: %s (nor enriched_v6.jsonl).\n"
                "  It is a build artifact, not a source file. Regenerate it with:\n"
                "      python scripts/patch_enriched_v5_to_v6.py\n"
                "  then re-run this script." % os.path.basename(IN_CUR))
    cur = read_jsonl(os.path.abspath(in_enriched))
    quar = read_jsonl(IN_QUAR)
    n_start = len(cur)
    by_id = {r["id"]: r for r in cur}
    quar_by_id = {r["id"]: r for r in quar}

    # ---- index merged for every code we need -------------------------------
    need = set()
    for c in C.CH84:
        need.add(("HSN", c))
    for c in C.CH87:
        need.add(("HSN", c))
    for c in C.SAC:
        need.add(("SAC", c))
    for r in cur:
        need.add((r["entity_type"], r["code"]))
    need.add(("HSN", "4819"))

    merged = {}
    real_codes = set()   # every real HSN/SAC code in the tariff, as an id string
    with io.open(IN_MERGED, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            m = json.loads(line)
            et, code = m.get("entity_type"), m.get("code")
            k = (et, code)
            if et in ("HSN", "SAC") and code:
                real_codes.add("%s_%s" % (et, code))
            if k in need and k not in merged:
                merged[k] = m
    missing = sorted(k for k in need if k not in merged)
    if missing:
        raise GapError("codes absent from merged reference: %r" % missing[:8])

    # ---- restore HSN_4819 from quarantine (Part D2 needs it) ---------------
    restored = []
    if "HSN_4819" not in by_id:
        src = quar_by_id.get("HSN_4819")
        if src is None:
            raise GapError("HSN_4819 is required by Part D2 but is in neither input")
        rec = copy.deepcopy(src)
        rec.pop("quarantine_reason", None)
        # bring the v5 shape up to v6
        rr = dict(rec["rate"])
        rr.pop("composition_note", None)
        total = rr["gst_rate"]
        rr["cgst"] = None if total is None else total / 2
        rr["sgst"] = None if total is None else total / 2
        rr["igst"] = None if total is None else total
        rr["rate_source"] = "none" if total is None else "merged"
        rr["history"] = rr.get("history") or []
        rec["rate"] = order_rate(rr)
        aa = dict(rec["ai"])
        aa.setdefault("one_line_rationale", None)
        # v5 sector values were never remapped on quarantined records
        attrs = dict(aa["attributes"])
        remapped, secs_before = [], list(attrs.get("sector", []))
        for s in secs_before:
            t = s if s in V6_SECTORS else SECTOR_REMAP.get(s, s)
            if t not in remapped:
                remapped.append(t)
        attrs["sector"] = remapped
        aa["attributes"] = attrs
        rec["ai"] = order_ai(aa)
        # regenerate search_text so it reflects the remapped sector
        rec["search_text"] = build_search_text(rec["ai"])
        rec["ai_checksum"] = ai_checksum(rec["ai"])
        rec = order_top(rec)
        cur.append(rec)
        by_id[rec["id"]] = rec
        restored.append("HSN_4819")
        notes.append(
            "`HSN_4819` (paper cartons, chapter 48) was restored from `quarantine.jsonl` and "
            "migrated to v6. Part D2 lists it in the packing-material demo path, but chapter 48 "
            "was out of MVP scope under the v6 patch, so it had been quarantined.")
        if secs_before != remapped:
            notes.append(
                "`HSN_4819`'s sector was still the v5 value %s and was remapped to %s on "
                "restore - quarantined records never went through the v6 Step 6 normalisation. "
                "Its `search_text` was regenerated to match."
                % (secs_before, remapped))

    # ---- Parts A/B/C: build new records ------------------------------------
    added = {"A": [], "B": [], "C": []}
    for code, spec in sorted(C.CH84.items()):
        rid = "HSN_" + code
        if rid in by_id:
            raise GapError("%s already exists; refusing to overwrite" % rid)
        rec = build_record("HSN", code, spec, merged[("HSN", code)], "Chapter 84")
        cur.append(rec)
        by_id[rid] = rec
        added["A"].append(rid)
    for code, spec in sorted(C.CH87.items()):
        rid = "HSN_" + code
        if rid in by_id:
            raise GapError("%s already exists" % rid)
        rec = build_record("HSN", code, spec, merged[("HSN", code)], "Chapter 87")
        cur.append(rec)
        by_id[rid] = rec
        added["B"].append(rid)
    for code, spec in sorted(C.SAC.items()):
        rid = "SAC_" + code
        if rid in by_id:
            raise GapError("%s already exists" % rid)
        rec = build_record("SAC", code, spec, merged[("SAC", code)], "Section 99")
        cur.append(rec)
        by_id[rid] = rec
        added["C"].append(rid)

    # Any newly built record that already existed in quarantine is a *replacement*,
    # not a creation - say so rather than letting the counts imply it was new.
    superseded = sorted(rid for grp in added.values() for rid in grp if rid in quar_by_id)
    if superseded:
        notes.append(
            "{IDS} was rebuilt from scratch by Part B rather than restored, because it was absent "
            "from the v6 input - the v6 patch had quarantined it as out-of-chapter. The new "
            "record therefore **supersedes** an earlier enrichment of the same id rather than "
            "filling an empty slot. The original's bolt-specific vocabulary (\"vehicle bolt\", "
            "\"chassis bolt\", \"automotive fastener\") and its caveat that the 5% rate applies "
            "to specified tractor parts while most vehicle parts attract 18% were both carried "
            "forward deliberately; the rebuild adds cross-references to HSN_8714 and HSN_8409 "
            "and a second clarification question."
            .replace("{IDS}", ", ".join("`%s`" % x for x in superseded)))

    # ---- Part B: the 7318 <-> 8708 cross-reference -------------------------
    bolt = {}
    r7318 = by_id["HSN_7318"]
    already = any(x["excluded_code"] == "HSN_8708" for x in r7318["ai"]["exclusion_notes"])
    bolt["7318_already_had_note"] = already
    if not already:
        r7318["ai"]["exclusion_notes"].append(collections.OrderedDict([
            ("excluded_code", "HSN_8708"),
            ("reason", "8708 covers the same physical bolt or nut when it is manufactured and "
                       "sold specifically as a motor vehicle part rather than generic hardware"),
        ]))
        r7318["ai"] = order_ai(dict(r7318["ai"]))
        r7318["search_text"] = build_search_text(r7318["ai"])
        r7318["ai_checksum"] = ai_checksum(r7318["ai"])
        bolt["7318_patched"] = True
    else:
        bolt["7318_patched"] = False
        notes.append(
            "Part B asks for `HSN_7318`'s `exclusion_notes` to be patched to reference "
            "`HSN_8708`. That note - and a matching clarification question - was already present "
            "from the original enrichment, so no edit was made and its checksum is unchanged. "
            "The cross-reference was verified in both directions rather than assumed.")
    bolt["7318_to_8708"] = any(x["excluded_code"] == "HSN_8708"
                               for x in r7318["ai"]["exclusion_notes"])
    bolt["8708_to_7318"] = any(x["excluded_code"] == "HSN_7318"
                               for x in by_id["HSN_8708"]["ai"]["exclusion_notes"])
    bolt["7318_cq"] = any("HSN_8708" in q.get("disambiguates_from", [])
                          for q in r7318["ai"]["clarification_questions"])
    bolt["8708_cq"] = any("HSN_7318" in q.get("disambiguates_from", [])
                          for q in by_id["HSN_8708"]["ai"]["clarification_questions"])

    # ---- Part D1: apply the demo seeds -------------------------------------
    seeded = []
    for rid, seed in DEMO_SEED.items():
        rec = by_id.get(rid)
        if rec is None:
            raise GapError("seed target %s not in the working set" % rid)
        if not seed.get("source_note"):
            raise GapError("%s: seed without a source_note" % rid)
        before = rec["rate"]["gst_rate"]
        if before is not None:
            raise GapError("%s already carries a rate (%s); refusing to overwrite it with a seed"
                           % (rid, before))
        r = dict(rec["rate"])
        total = seed["gst_rate"]
        r["gst_rate"] = total
        r["cgst"] = total / 2
        r["sgst"] = total / 2
        r["igst"] = total
        r["rate_source"] = "manual_seed"
        r["effective_from"] = seed["effective_from"]
        r["notification_no"] = seed["notification_no"]
        r["rate_confidence"] = seed["rate_confidence"]
        r["rate_scope"] = seed["rate_scope"]
        r["rate_caveat"] = None
        r["exemption_status"] = "taxable"
        rec["rate"] = order_rate(r)
        # keep the rationale honest about where the number came from
        pr = rec["ai"]["plain_rationale"]
        pr = pr.replace(
            "No GST rate for this exact code could be matched from the notification schedules; "
            "confirm with your CA before invoicing.", "").replace(
            "No GST rate could be matched to this code from the notification schedules currently "
            "in the knowledge base. Consult a tax professional or check the CBIC portal directly.",
            "").strip()
        pr = (pr + " GST is %s%%, seeded manually from %s; this figure was entered by hand rather "
                   "than matched from the rate schedules, so confirm it with your CA before "
                   "invoicing." % (fmt_rate(total), seed["notification_no"])).strip()
        rec["ai"]["plain_rationale"] = pr
        rec["ai"] = order_ai(dict(rec["ai"]))
        rec["search_text"] = build_search_text(rec["ai"])
        rec["ai_checksum"] = ai_checksum(rec["ai"])
        seeded.append(rid)

    # ---- Part D2: one-liners ----------------------------------------------
    wrote_ol, missing_ol = [], []
    for rid, text in C.ONE_LINERS.items():
        rec = by_id.get(rid)
        if rec is None:
            missing_ol.append(rid)
            continue
        if len(text) > ONE_LINER_MAX:
            raise GapError("%s: one_line_rationale is %d chars (limit %d)"
                           % (rid, len(text), ONE_LINER_MAX))
        rec["ai"]["one_line_rationale"] = text
        rec["ai"] = order_ai(dict(rec["ai"]))
        rec["ai_checksum"] = ai_checksum(rec["ai"])
        wrote_ol.append(rid)
    if missing_ol:
        raise GapError("one-liner targets missing from the working set: %r" % missing_ol)

    # ---- validate ----------------------------------------------------------
    known_ids = set(by_id) | real_codes
    # search_text is derived only from synonyms/market_terms/hindi/examples/attributes,
    # so it is enforced on records whose ai content this pass authored - not on ones
    # that merely received a one-liner or a rate seed, neither of which feeds it.
    authored = set(added["A"]) | set(added["B"]) | set(added["C"]) | set(restored)
    touched = authored | set(seeded) | set(wrote_ol)
    val_errs, extra_errs = [], []
    for rec in cur:
        for e in validate(rec):
            val_errs.append((rec["id"], e))
        for e in validate_extra(rec, known_ids, rec["id"] in authored):
            extra_errs.append((rec["id"], e))

    stale_st = [r["id"] for r in cur
                if r["id"] not in authored and r["search_text"] != build_search_text(r["ai"])]

    dup = [i for i, c in collections.Counter(r["id"] for r in cur).items() if c > 1]
    if dup:
        raise GapError("duplicate ids: %r" % dup[:5])

    # ---- rate drift (manual_seed exempted) ---------------------------------
    drift, skipped_seed, compared = [], 0, 0
    for rec in cur:
        if rec["rate"]["rate_source"] == "manual_seed":
            skipped_seed += 1
            continue
        m = merged.get((rec["entity_type"], rec["code"]))
        if m is None:
            continue
        compared += 1
        if rec["rate"]["gst_rate"] != m.get("tax", {}).get("gst_rate"):
            drift.append((rec["id"], "gst_rate", m.get("tax", {}).get("gst_rate"),
                          rec["rate"]["gst_rate"]))
        mc = m.get("metadata", {}).get("rate_confidence")
        rc = rec["rate"]["rate_confidence"]
        if rc != mc and not (mc is None and rc == "unresolved"):
            drift.append((rec["id"], "rate_confidence", mc, rc))

    if val_errs:
        for i, e in val_errs[:40]:
            sys.stderr.write("VALIDATION %s: %s\n" % (i, e))
        raise GapError("validation failed with %d error(s); nothing written" % len(val_errs))
    if extra_errs:
        for i, e in extra_errs[:40]:
            sys.stderr.write("EXTRA %s: %s\n" % (i, e))
        raise GapError("extra checks failed with %d error(s); nothing written" % len(extra_errs))
    if drift:
        for d in drift[:20]:
            sys.stderr.write("DRIFT %r\n" % (d,))
        raise GapError("rate drift detected on %d field(s); nothing written" % len(drift))

    # ---- report ------------------------------------------------------------
    ctx = dict(
        n_start=n_start, n_final=len(cur), added=added, restored=restored,
        seeded=seeded, wrote_ol=wrote_ol, bolt=bolt, notes=notes,
        compared=compared, skipped_seed=skipped_seed, touched=touched,
        authored=authored, stale_search_text=stale_st, n_real_codes=len(real_codes),
        records=cur, by_id=by_id, merged=merged,
    )
    report = build_report(ctx)

    write_jsonl(out_final, cur)
    write_text(out_seed, json.dumps(DEMO_SEED, ensure_ascii=False, indent=2) + "\n")
    write_text(out_report, report)

    print("start          : %d" % n_start)
    print("Part A ch84    : +%d" % len(added["A"]))
    print("Part B ch87    : +%d" % len(added["B"]))
    print("Part C SAC     : +%d" % len(added["C"]))
    print("restored       : +%d %s" % (len(restored), restored or ""))
    print("final          : %d -> %s" % (len(cur), os.path.basename(out_final)))
    print("seeded rates   : %d %s" % (len(seeded), seeded))
    print("one-liners     : %d" % len(wrote_ol))
    print("validation     : PASS (0 errors)")
    print("rate drift     : PASS (%d compared, %d manual_seed skipped)" % (compared, skipped_seed))
    print("bolt test      : 7318->8708 %s | 8708->7318 %s" %
          (bolt["7318_to_8708"], bolt["8708_to_7318"]))
    return 0


def build_report(ctx):
    L = []
    add = L.append
    recs = ctx["records"]
    by_id = ctx["by_id"]

    hsn = [r for r in recs if r["entity_type"] == "HSN"]
    sac = [r for r in recs if r["entity_type"] == "SAC"]
    per_ch = collections.Counter(r["code"][:2] for r in hsn)

    add("# Gap-fill report - `updat_enriched.jsonl` -> `enriched_final.jsonl`")
    add("")
    add("Project: IRIS-HACK-P-2026-001 - GST Classification Engine  ")
    add("Script: `scripts/gap_fill_v6.py` + `scripts/gap_content.py`")
    add("")

    add("## Headline")
    add("")
    add("| | |")
    add("|---|---|")
    add("| Starting records | %d |" % ctx["n_start"])
    add("| Part A - Chapter 84 | +%d |" % len(ctx["added"]["A"]))
    add("| Part B - auto parts | +%d |" % len(ctx["added"]["B"]))
    add("| Part C - SAC breadth | +%d |" % len(ctx["added"]["C"]))
    add("| Restored from quarantine | +%d |" % len(ctx["restored"]))
    add("| **Final total** | **%d** |" % ctx["n_final"])
    add("| Validation errors | 0 |")
    add("| Rate drift | 0 |")
    add("")

    add("## Count reconciliation")
    add("")
    add("The spec predicted ~350 (224 + 87 + 2 + 20 + 17). Actual is **%d**. Two reasons:" % ctx["n_final"])
    add("")
    add("- **Chapter 84 has 86 four-digit headings in the reference data, not 87.** "
        "Heading 8469 (typewriters) was deleted from the tariff, so the chapter runs "
        "8401-8487 with one gap. All 86 present headings were enriched.")
    add("- **The spec's own Part C arithmetic double-counts.** The summary table says "
        "\"~17\" but the code table lists **20** codes and the text says this \"brings SAC to "
        "32\" (12 + 20 = 32). The 20-code list was treated as authoritative.")
    add("")
    add("So: 224 + 86 + 2 + 20 + 1 restored = **%d**." % ctx["n_final"])
    add("")

    # Part A
    add("## Part A - Chapter 84")
    add("")
    a = [by_id[i] for i in ctx["added"]["A"]]
    withrate = [r for r in a if r["rate"]["gst_rate"] is not None]
    add("- Headings enriched: **%d** (8401-8487, 8469 absent from the tariff)" % len(a))
    add("- With a rate from `merged 1.jsonl`: **%d**" % len(withrate))
    add("- Left `unresolved` (no rate in the source): **%d** - %s"
        % (len(a) - len(withrate),
           ", ".join("`%s`" % r["id"] for r in a if r["rate"]["gst_rate"] is None)))
    add("")
    add("The spec expected 3 unresolved; the reference data has **2**. Neither was seeded - "
        "Part A explicitly says not to.")
    add("")
    add("Rate distribution: " + ", ".join(
        "%s%% = %d" % (fmt_rate(k), v) for k, v in sorted(
            collections.Counter(r["rate"]["gst_rate"] for r in withrate).items())))
    add("")
    abst = [r for r in a if r["enrichment_status"] == "abstained"]
    add("**Abstained (residual \"other\" headings):** %d - %s"
        % (len(abst), ", ".join("`%s`" % r["id"] for r in abst)))
    add("")
    add("These are catch-all headings (\"other engines and motors\", \"machines having "
        "individual functions n.e.s.\", \"other office machines\", \"machinery parts n.e.s.\"). "
        "A record only belongs in one after every named heading has been ruled out, which a "
        "plain-language query cannot establish. They carry full enrichment so search still "
        "reaches them, but `enrichment_status: \"abstained\"` flags that the classification "
        "needs human confirmation rather than being asserted.")
    add("")
    add("**Multi-sector assignments** (the spec's watch-list):")
    add("")
    add("| Heading | Sectors |")
    add("|---|---|")
    for r in a:
        if len(r["ai"]["attributes"]["sector"]) == 2:
            add("| `%s` %s | %s |" % (r["id"], r["title"][:44],
                                      " + ".join(r["ai"]["attributes"]["sector"])))
    add("")
    add("**Clarification questions** were written for the near-neighbour pairs the spec named:")
    add("")
    add("| Pair | Attribute | Question |")
    add("|---|---|---|")
    for rid in ("HSN_8413", "HSN_8407", "HSN_8481", "HSN_8484", "HSN_8414", "HSN_8408"):
        r = by_id.get(rid)
        if r and r["ai"]["clarification_questions"]:
            q = r["ai"]["clarification_questions"][0]
            add("| `%s` vs %s | `%s` | %s |" % (
                rid, ", ".join("`%s`" % x for x in q["disambiguates_from"]),
                q["attribute"], q["question"]))
    add("")

    # Part B
    add("## Part B - `HSN_8708` and the bolt test")
    add("")
    b = ctx["bolt"]
    add("| Check | Result |")
    add("|---|---|")
    add("| `HSN_8708` present | %s |" % ("yes" if "HSN_8708" in by_id else "**NO**"))
    add("| `HSN_8714` present | %s |" % ("yes" if "HSN_8714" in by_id else "**NO**"))
    add("| `HSN_7318` -> `HSN_8708` in `exclusion_notes` | %s |" % ("yes" if b["7318_to_8708"] else "**NO**"))
    add("| `HSN_8708` -> `HSN_7318` in `exclusion_notes` | %s |" % ("yes" if b["8708_to_7318"] else "**NO**"))
    add("| `HSN_7318` clarification question targets 8708 | %s |" % ("yes" if b["7318_cq"] else "**NO**"))
    add("| `HSN_8708` clarification question targets 7318 | %s |" % ("yes" if b["8708_cq"] else "**NO**"))
    add("")
    if b["7318_already_had_note"]:
        add("**`HSN_7318` needed no patch.** Part B asks for its `exclusion_notes` to be edited "
            "to add `HSN_8708`, but that note *and* a matching clarification question were "
            "already present from the original enrichment. The cross-reference was verified in "
            "both directions rather than assumed, and 7318's checksum is untouched.")
    else:
        add("`HSN_7318` was patched to add the `HSN_8708` exclusion note and its checksum recomputed.")
    add("")
    r8708 = by_id["HSN_8708"]
    r8714 = by_id["HSN_8714"]
    add("`HSN_8708` carries rate **%s%%** (`%s`, from merged). `HSN_8714` is **%s** - no rate "
        "exists for it anywhere in the reference data, so it was left unresolved rather than "
        "seeded or inferred from 8708."
        % (fmt_rate(r8708["rate"]["gst_rate"]), r8708["rate"]["rate_confidence"],
           "null" if r8714["rate"]["gst_rate"] is None else fmt_rate(r8714["rate"]["gst_rate"]) + "%"))
    add("")

    # Part C
    add("## Part C - SAC breadth")
    add("")
    sec_of = collections.Counter()
    for r in sac:
        for s in r["ai"]["attributes"]["sector"]:
            sec_of[s] += 1
    add("SAC total: **%d** (12 existing + %d added). Distinct sectors: **%d**."
        % (len(sac), len(ctx["added"]["C"]), len(sec_of)))
    add("")
    add("| Sector | SAC codes |")
    add("|---|---:|")
    for s, n in sorted(sec_of.items(), key=lambda kv: (-kv[1], kv[0])):
        add("| %s | %d |" % (s, n))
    add("")
    add("The clustering is fixed: before this pass all 12 SAC records sat in construction "
        "(9954x) and accounting (99822x) alone. IT, transport, legal, advertising, repair and "
        "job-work families are now represented.")
    add("")
    add("**Job-work codes** `SAC_998873` and `SAC_998877` sound like goods but are services. "
        "Both carry a `retail_industrial` clarification question separating \"I make and sell "
        "the product\" (goods, HSN) from \"I process material the customer supplies\" "
        "(service, SAC), with `disambiguates_from` pointing at the corresponding HSN headings.")
    add("")

    # Part D
    add("## Part D1 - Manual rate seeds")
    add("")
    add("| Record | Rate | Confidence | Scope | Source |")
    add("|---|---:|---|---|---|")
    for rid in ctx["seeded"]:
        r = by_id[rid]
        add("| `%s` | %s%% | %s | %s | `manual_seed` |" % (
            rid, fmt_rate(r["rate"]["gst_rate"]), r["rate"]["rate_confidence"],
            r["rate"]["rate_scope"]))
    add("")
    add("Both entries are written to `demo_seed.json` with a full `source_note`. Reproduced here:")
    add("")
    for rid, seed in DEMO_SEED.items():
        add("**`%s`** - %s" % (rid, seed["source_note"]))
        add("")
    add("> **Verification status - read this before the demo.** Part D1 says to \"verify the "
        "ready-reckoner values yourself before committing them\". This build runs offline with "
        "no network access, so **the CBIC notification could not be independently checked**. "
        "The `HSN_6307` figure is the one supplied in the task specification, recorded as such; "
        "`HSN_63079091` inherits it from its parent heading at one confidence step lower. "
        "Neither was cross-checked against Notification 9/2025, which the spec flags as a "
        "possible conflict. Both are marked `rate_source: \"manual_seed\"` so they are "
        "distinguishable from matched rates everywhere downstream, and both are excluded from "
        "the rate-drift check by design.")
    add("")

    add("### Mask test")
    add("")
    add("| Code | Title | Rate | Source |")
    add("|---|---|---:|---|")
    ok_mask = True
    for rid in ("HSN_63079091", "HSN_90200000", "HSN_3304"):
        r = by_id[rid]
        gr = r["rate"]["gst_rate"]
        if gr is None:
            ok_mask = False
        add("| `%s` | %s | %s | `%s` |" % (rid, r["title"][:52],
                                           "**null**" if gr is None else fmt_rate(gr) + "%",
                                           r["rate"]["rate_source"]))
    add("")
    add("**%s** - all three mask codes carry a rate." % ("PASS" if ok_mask else "FAIL"))
    add("")

    add("## Part D2 - One-line rationales")
    add("")
    written = [r for r in recs if r["ai"]["one_line_rationale"] is not None]
    add("Written: **%d**. Still null: **%d** of %d."
        % (len(written), ctx["n_final"] - len(written), ctx["n_final"]))
    add("")
    add("| Record | One-liner | Chars |")
    add("|---|---|---:|")
    for rid in C.ONE_LINERS:
        r = by_id[rid]
        add("| `%s` | %s | %d |" % (rid, r["ai"]["one_line_rationale"],
                                    len(r["ai"]["one_line_rationale"])))
    add("")
    add("All are within the 120-char limit and written as standalone sentences - none is a "
        "truncation of `plain_rationale`. The remaining records stay null by design; they are "
        "reachable by search but will not be on screen during the demo.")
    add("")

    # Coverage
    add("## Chapter coverage")
    add("")
    add("| Chapter | Records | Status |")
    add("|---|---:|---|")
    for ch in sorted(MVP_CHAPTERS):
        n = per_ch.get(ch, 0)
        tag = ""
        if ch in CHAPTERS_ADDED_HERE:
            tag = " (added this pass)"
        status = "**ZERO**" if n == 0 else ("thin" if n < 5 else ("light" if n < 10 else "ok"))
        add("| %s%s | %d | %s |" % (ch, tag, n, status))
    add("| SAC (all) | %d | ok |" % len(sac))
    add("| **Total** | **%d** | |" % ctx["n_final"])
    add("")
    zero = [ch for ch in sorted(MVP_CHAPTERS) if per_ch.get(ch, 0) == 0]
    if zero:
        add("**Chapters still at zero: %s.**" % ", ".join(zero))
    else:
        add("**No MVP chapter is at zero.** Chapter 84 went from 0 to %d this pass - it was the "
            "single largest gap in the set." % per_ch.get("84", 0))
    add("")

    # Scope change
    add("## Scope change - two chapters added to `MVP_CHAPTERS`")
    add("")
    add("The gap spec requires records the v6 scope rule excludes, so `MVP_CHAPTERS` was widened "
        "by two. Without this the spec's own instruction to run the patch validator with zero "
        "errors is unsatisfiable:")
    add("")
    add("| Chapter | Why it had to be added | Records |")
    add("|---|---|---:|")
    add("| 87 | Part B requires `HSN_8708` and `HSN_8714`; the bolt test is a named success "
        "criterion | %d |" % per_ch.get("87", 0))
    add("| 48 | Part D2 lists `HSN_4819` in the packing-material demo path | %d |" % per_ch.get("48", 0))
    add("")
    add("This resolves the contradiction flagged in the v6 patch report, where `HSN_8708` "
        "appeared on the demo path but was quarantined by the scope rule.")
    add("")

    # Validation
    add("## Validation and rate drift")
    add("")
    add("**Validator: PASS** - all %d records pass the patch spec's `validate()` with zero "
        "errors." % ctx["n_final"])
    add("")
    add("Additional checks, also all passing:")
    add("")
    add("- `rate_source` enum, and every resolved rate carrying `merged` or `manual_seed`")
    add("- `ai_checksum` matches the `ai` object on every record")
    add("- `rate` and `ai` key order identical to the existing 224")
    add("- `search_text` regenerates exactly from the `ai` object, on all %d records this pass "
        "authored" % len(ctx["authored"]))
    add("- every `one_line_rationale` within 120 chars")
    add("- **no invented codes**: every `excluded_code` and every `disambiguates_from` id "
        "resolves either to a record in the final set or to one of the %s real HSN/SAC codes "
        "in the reference tariff. Cross-references to real-but-not-yet-enriched codes are "
        "allowed (the existing data already does this, e.g. `HSN_2106` -> `HSN_21069020`); a "
        "reference to neither would be a fabrication and fails the build."
        % "{:,}".format(ctx["n_real_codes"]))
    add("")
    add("**Rate drift: PASS.** %d records compared against `merged 1.jsonl` on "
        "`(entity_type, code)`; zero differences in `gst_rate` or `rate_confidence`. "
        "%d `manual_seed` records were skipped, as the spec requires - they are expected to "
        "differ because merged has no rate for them at all."
        % (ctx["compared"], ctx["skipped_seed"]))
    add("")

    add("## Notes and deviations")
    add("")
    for n in ctx["notes"]:
        add("- %s" % n)
    add("- `enrichment_prompt_v6.md` is named as the enrichment prompt but is not present in the "
        "project. The existing 224 records were used as the style contract instead, which the "
        "spec's own rule (\"new records must match the existing 224 exactly\") makes the "
        "authoritative source anyway. Field shapes, key order and the `search_text` rule were "
        "reverse-engineered from them and verified.")
    add("- `HSN_SAC.xlsx` (`HSN_MSTR` / `SAC_MSTR`) is absent, so `merged 1.jsonl` was used as "
        "the code list and rate source. It contains all 86 Chapter 84 headings, both Chapter 87 "
        "codes and all 20 target SAC codes, so nothing was lost.")
    add("- The rate reference is `merged 1.jsonl` on disk, not `merged_1.jsonl`.")
    add("- **%d untouched record(s) have a `search_text` that no longer regenerates from their "
        "`ai` object**: %s. All are chapter-33 records whose `search_text` still contains the "
        "pre-v6 sector wording (\"consumer goods household\") because the v6 patch normalised "
        "`sector` but deliberately left `search_text` alone. Harmless - it only adds stale "
        "search tokens - and reported rather than silently rewritten, since rewriting them is a "
        "scope decision, not a gap-fill one."
        % (len(ctx["stale_search_text"]),
           ", ".join("`%s`" % x for x in ctx["stale_search_text"]) or "none"))
    add("- New-record `plain_rationale` text is composed from the record's own rate block rather "
        "than typed by hand, so a rationale can never state a rate the record does not carry.")
    add("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GapError as e:
        sys.stderr.write("\nGAP-FILL FAILED: %s\n" % e)
        sys.exit(1)
