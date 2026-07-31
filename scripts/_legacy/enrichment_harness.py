"""
Reusable harness for the GST enrichment pipeline described in enrichment_prompt_v5.md.

Provides the pieces the spec assumes an upstream/downstream pipeline already has:
  - load_master()          : id -> record index over merged 1.jsonl
  - build_history()        : metadata.superseded_rates -> rate.history (Section 6)
  - build_search_text()    : Section 6 search_text rule (includes attributes.sector)
  - default_rate_caveat()  : Section 4 composition-rule caveat text
  - derive_exemption_status(): Section 5 exemption_status derivation
  - build_rate()           : assembles a full v5 rate block from a master record
  - nic_rate()             : the fixed, always-null rate block for NIC records (Section 8.4)
  - validate()             : Section 10 assertions, adapted to also cross-check the master
  - finalize()             : computes the real ai_checksum (Section 6 checksum recipe)
  - write_jsonl()          : merge records into a target .jsonl file by id

This module has no content-authoring logic in it on purpose -- record content
(the actual "ai" and "rate" blocks) is produced by whoever plays the LLM role
(a human, this session, or a real model call) and handed to validate()/finalize().
"""
import json
import re
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MERGED_PATH = ROOT / "merged 1.jsonl"
ENRICHED_PATH = ROOT / "enriched.jsonl"

PUNCT_STRIP_RE = re.compile(r"[,.;:()]")
WS_RE = re.compile(r"\s+")

# Section 6 -- controlled enum for ai.attributes.sector. Exact strings, exact casing.
SECTORS = {
    "Food & Beverages", "Textiles & Apparel", "Engineering & Machinery",
    "Chemicals & Pharmaceuticals", "Plastics & Rubber", "Metals & Metal Products",
    "Wood, Paper & Packaging", "Construction & Building Materials",
    "Electronics & Electricals", "Automotive & Transport",
    "Agriculture & Live Animals", "Minerals & Energy",
    "Consumer Goods & Household", "Professional Services",
    "Financial & Business Services", "Transport & Logistics Services", "Other",
}

# Section 6 -- controlled enum for ai.clarification_questions[].attribute.
CLARIFICATION_ATTRS = {
    "material", "use", "form", "industry", "price", "branding", "origin", "retail_industrial",
}

# Section 5 -- the two notifications that make a record "exempt" rather than "unknown".
EXEMPT_NOTIFICATIONS = {"2/2017-Central Tax (Rate)", "12/2017-Central Tax (Rate)"}

UNRESOLVED_RATE_CAVEAT = (
    "No GST rate could be matched to this code from the notification schedules "
    "currently in the knowledge base. Consult a tax professional or check the CBIC portal directly."
)

NIC_RATE_CAVEAT = (
    "NIC is an activity classification for MCA and MSME registration and does not carry a GST rate. "
    "For tax rates, use the corresponding HSN code for the goods produced."
)


def load_master():
    """Return {id: record} for every row in merged 1.jsonl."""
    master = {}
    with open(MERGED_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            master[rec["id"]] = rec
    return master


def build_history(superseded_rates):
    """Section 6: metadata.superseded_rates -> rate.history."""
    if not superseded_rates:
        return []
    seen = set()
    pairs = []
    for date, rate in superseded_rates:
        key = (date, rate)
        if key in seen:
            continue
        seen.add(key)
        pairs.append({"effective_from": date, "gst_rate": rate})
    pairs.sort(key=lambda p: p["effective_from"])
    return pairs[-5:]


def default_rate_caveat(rate_confidence, rate_scope, heading=None, chapter=None, notification_no=None):
    """Section 4 composition rule: emit a caveat whenever rate_scope is 'chapter' or
    rate_confidence is low/unresolved. Returns None when no caveat is warranted.

    Chapter-scoped and heading-scoped-but-low-confidence are genuinely different situations
    (matched at the wrong granularity vs. matched at the right granularity with low certainty),
    so they get different wording rather than one template papering over both."""
    note = notification_no or "the applicable notification"
    if rate_confidence == "unresolved":
        return UNRESOLVED_RATE_CAVEAT
    if rate_scope == "chapter":
        chap = chapter or "?"
        head = heading or "?"
        return (
            f"This rate was matched from the Chapter {chap} entry as a whole, not a rule written "
            f"specifically for heading {head}. Confirm against Notification {note} before invoicing."
        )
    if rate_confidence == "low":
        return (
            f"This rate was matched with low confidence at the heading level — verify against "
            f"Notification {note} before invoicing."
        )
    return None


def derive_exemption_status(tax, rate_confidence):
    """Section 5: exempt only on a 0.0 rate or an exemption-notification reference;
    unknown whenever the rate itself is unresolved. Never inferred from the description."""
    if rate_confidence == "unresolved":
        return "unknown"
    gst_rate = tax.get("gst_rate")
    notification_no = tax.get("notification_no") or ""
    if gst_rate == 0.0 or notification_no in EXEMPT_NOTIFICATIONS:
        return "exempt"
    if gst_rate is not None and gst_rate > 0:
        return "taxable"
    return "unknown"


def build_rate(master_rec, exceptions=None, caveat=None, exemption_status=None, composition_note=None):
    """Assemble a full v5 rate block from a Source B master record. Any of caveat /
    exemption_status may be overridden by the caller for record-specific nuance;
    otherwise they're derived mechanically so authors don't have to repeat the logic."""
    tax = master_rec.get("tax", {})
    meta = master_rec.get("metadata", {})
    conf = meta.get("rate_confidence") or "unresolved"
    rate_scope = meta.get("rate_scope")
    hierarchy = master_rec.get("hierarchy", {})
    if caveat is None:
        caveat = default_rate_caveat(
            conf, rate_scope, hierarchy.get("heading"), hierarchy.get("chapter"), tax.get("notification_no")
        )
    if exemption_status is None:
        exemption_status = derive_exemption_status(tax, conf)
    return {
        "gst_rate": tax.get("gst_rate"),
        "cess": tax.get("cess"),
        "effective_from": tax.get("effective_from"),
        "notification_no": tax.get("notification_no"),
        "rate_confidence": conf,
        "rate_scope": rate_scope,
        "rate_caveat": caveat,
        "exemption_status": exemption_status,
        "composition_note": composition_note,
        "exceptions": exceptions or [],
        "history": build_history(meta.get("superseded_rates")),
    }


def nic_rate():
    """Section 8.4: NIC never carries a GST rate, ever."""
    return {
        "gst_rate": None,
        "cess": None,
        "effective_from": None,
        "notification_no": None,
        "rate_confidence": "unresolved",
        "rate_scope": None,
        "rate_caveat": NIC_RATE_CAVEAT,
        "exemption_status": "unknown",
        "composition_note": None,
        "exceptions": [],
        "history": [],
    }


def _tokenize(text):
    text = text.lower()
    text = PUNCT_STRIP_RE.sub(" ", text)
    return [t for t in WS_RE.split(text) if t]


def build_search_text(ai):
    """Section 6: concat synonyms+market_terms+hindi_transliterated+examples+all attribute
    values (including sector), lowercase, strip punctuation (keep intra-word hyphens),
    dedupe preserving order."""
    parts = []
    parts.extend(ai["synonyms"])
    parts.extend(ai["market_terms"])
    parts.extend(ai["hindi_transliterated"])
    parts.extend(ai["examples"])
    for group in ("material", "use", "form", "industry", "sector"):
        parts.extend(ai["attributes"].get(group, []))

    seen = set()
    tokens = []
    for part in parts:
        for tok in _tokenize(part):
            if tok not in seen:
                seen.add(tok)
                tokens.append(tok)
    return " ".join(tokens)


def validate(rec, candidates, master):
    """Section 10 assertions, plus the master cross-checks called out at the end of Section 10."""
    errs = []
    mid = rec["id"]
    r, ai = rec["rate"], rec["ai"]

    if mid not in master:
        errs.append("id not in master")
    if rec["code"] == "1111" and rec["entity_type"] == "HSN":
        errs.append("code 1111 (AKASH test artifact) must not be enriched")
    if rec["ai_checksum"] != "PENDING_CHECKSUM":
        errs.append("checksum must be PENDING_CHECKSUM before finalize()")

    # --- rate integrity (Section 4, 5, 9) ---
    if rec["entity_type"] == "NIC" and r["gst_rate"] is not None:
        errs.append("NIC record carries a GST rate")
    if r["rate_confidence"] == "unresolved" and r["gst_rate"] is not None:
        errs.append("unresolved rate has a value")
    if r["rate_scope"] == "chapter" and not r["rate_caveat"]:
        errs.append("chapter-scope rate missing caveat")
    if r["rate_confidence"] in ("low", "unresolved") and not r["rate_caveat"]:
        errs.append("low/unresolved rate_confidence missing caveat")
    if r["exemption_status"] not in ("exempt", "taxable", "unknown"):
        errs.append(f"bad exemption_status {r['exemption_status']!r}")
    if r["exemption_status"] == "exempt" and r["gst_rate"] not in (0.0, None):
        errs.append("exempt but non-zero rate")
    if r["rate_confidence"] == "unresolved" and r["exemption_status"] != "unknown":
        errs.append("unresolved rate must have unknown exemption_status")
    if rec["entity_type"] == "NIC" and r["composition_note"] is not None:
        errs.append("NIC record must not carry a composition_note")

    # --- controlled vocab (Section 6, 9) ---
    for s in ai["attributes"]["sector"]:
        if s not in SECTORS:
            errs.append(f"invented sector {s!r}")
    if not 1 <= len(ai["attributes"]["sector"]) <= 2:
        errs.append("sector must have 1-2 values")

    # --- no invented codes (Section 9) ---
    for note in ai["exclusion_notes"]:
        if note["excluded_code"] not in candidates:
            errs.append(f"invented code in exclusion_notes: {note['excluded_code']}")
    for q in ai["clarification_questions"]:
        if q["attribute"] not in CLARIFICATION_ATTRS:
            errs.append(f"bad clarification attribute {q['attribute']!r}")
        for c in q["disambiguates_from"]:
            if c not in candidates:
                errs.append(f"invented code in clarification_questions: {c}")

    # --- completeness (Section 6, 9) ---
    if rec["enrichment_status"] == "complete":
        if not 4 <= len(ai["synonyms"]) <= 8:
            errs.append(f"synonyms out of 4-8 range ({len(ai['synonyms'])})")
        if not 2 <= len(ai["examples"]) <= 4:
            errs.append(f"examples out of 2-4 range ({len(ai['examples'])})")
        if not 3 <= len(ai["market_terms"]) <= 6:
            errs.append(f"market_terms out of 3-6 range ({len(ai['market_terms'])})")
        if ai["classification_confidence"]["level"] in ("Medium", "Low") and not ai["exclusion_notes"]:
            errs.append("Medium/Low classification_confidence without exclusion note")

    if len(ai["attributes"].get("industry", [])) < 1:
        errs.append("industry attribute must have >=1 entry")
    if len(ai["hindi_transliterated"]) > 5:
        errs.append("hindi_transliterated exceeds 5")
    if len(ai["clarification_questions"]) > 3:
        errs.append("clarification_questions exceeds 3")
    if len(ai["exclusion_notes"]) > 3:
        errs.append("exclusion_notes exceeds 3")
    if ai["classification_confidence"]["level"] not in ("High", "Medium", "Low"):
        errs.append("bad classification_confidence.level")
    if len(rec["title"]) > 120:
        errs.append("title exceeds 120 chars")
    if len(ai["plain_rationale"]) > 600:
        errs.append("plain_rationale exceeds 600 chars")
    if len(ai["regulatory_citation"]) > 200:
        errs.append("regulatory_citation exceeds 200 chars")
    if r["composition_note"] is not None and len(r["composition_note"]) > 200:
        errs.append("composition_note exceeds 200 chars")

    # --- search_text hygiene (Section 6, 9) ---
    if any(ch in rec["search_text"] for ch in ",.;:()"):
        errs.append("punctuation in search_text")
    if rec["search_text"] != rec["search_text"].lower():
        errs.append("search_text not lowercase")

    # --- cross-checks against the master (end of Section 10) ---
    if mid in master:
        m = master[mid]
        master_rate = m.get("tax", {}).get("gst_rate")
        if r["gst_rate"] != master_rate and not (r["gst_rate"] is None and master_rate is None):
            errs.append(f"gst_rate {r['gst_rate']!r} != master {master_rate!r}")

        master_conf = m.get("metadata", {}).get("rate_confidence")
        expected_conf = master_conf if master_conf else "unresolved"
        if rec["entity_type"] != "NIC" and r["rate_confidence"] != expected_conf:
            errs.append(f"rate_confidence {r['rate_confidence']!r} != master {expected_conf!r}")

        master_history_pairs = {
            (d, rate) for d, rate in m.get("metadata", {}).get("superseded_rates", []) or []
        }
        for h in r["history"]:
            if (h["effective_from"], h["gst_rate"]) not in master_history_pairs:
                errs.append(f"history entry not in master superseded_rates: {h}")

    return errs


def finalize(rec):
    """Section 6 checksum recipe. Mutates and returns rec."""
    rec["ai_checksum"] = hashlib.sha256(
        json.dumps(rec["ai"], sort_keys=True, ensure_ascii=False,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return rec


def write_jsonl(records, path=ENRICHED_PATH):
    """Merge records into path by id: existing ids are replaced, order preserved
    (existing rows keep their position, new ids are appended at the end)."""
    existing = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    existing.append(json.loads(line))

    by_id = {r["id"]: r for r in existing}
    for rec in records:
        by_id[rec["id"]] = rec

    ordered = [by_id[r["id"]] for r in existing]
    seen = {r["id"] for r in existing}
    new_ids = []
    for rec in records:
        if rec["id"] not in seen:
            ordered.append(rec)
            seen.add(rec["id"])
            new_ids.append(rec["id"])

    with open(path, "w", encoding="utf-8") as f:
        for rec in ordered:
            f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")))
            f.write("\n")

    return len(ordered), len(new_ids)
