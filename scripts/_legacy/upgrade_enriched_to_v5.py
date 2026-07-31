"""
Bulk v5 upgrade for the well-formed v3-schema records already in enriched.jsonl.

Scope: the 216 records that have entity_type/code/title/rate (HSN + SAC), built by the
wave1/wave2 scripts across a small, known set of chapters. Of those, 21 have already
been hand-upgraded and vetted individually in golden_dataset.jsonl (mask/bolt/packing/
worked-example candidates) -- this script reuses that content verbatim for those ids
and mechanically upgrades the remaining ~195 by chapter.

Sector assignment is chapter-level, not per-record: every chapter covered here maps
cleanly onto exactly one Section 6 sector with no internal split (Ch 19-22 food
preparations, Ch 28-29 chemicals, Ch 39 plastics, Ch 61-62 apparel, Ch 73 iron/steel
articles, SAC 998xxx accounting services), so there's no ambiguity to guess at record
by record. Chapter 33/63/3923/6109/7318/90-series are excluded here because
golden_dataset.jsonl already covers all of them individually (see chapter counts in
enriched.jsonl: 33->8, 63->9, 90->1, and the single 3923/6109/7318 records -- all
fully accounted for by the golden set).

Does NOT touch the ~120 legacy pre-v3 records (no entity_type/code/rate/title) --
those need full regeneration, not a field-level upgrade, and are handled separately.
"""
import sys
import json
import copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import (
    load_master, build_rate, build_search_text, validate, finalize, write_jsonl, ROOT, ENRICHED_PATH
)

MASTER = load_master()
GOLDEN_PATH = ROOT / "golden_dataset.jsonl"

CHAPTER_SECTOR = {
    "19": ["Food & Beverages"],
    "20": ["Food & Beverages"],
    "21": ["Food & Beverages"],
    "22": ["Food & Beverages"],
    "28": ["Chemicals & Pharmaceuticals"],
    "29": ["Chemicals & Pharmaceuticals"],
    "39": ["Plastics & Rubber"],
    "61": ["Textiles & Apparel"],
    "62": ["Textiles & Apparel"],
    "73": ["Metals & Metal Products"],
}
SAC_PREFIX_SECTOR = {
    "998": ["Professional Services"],
}

GOODS_COMPOSITION_NOTE = (
    "Small manufacturers and traders under the composition scheme pay a flat "
    "turnover-based GST rate instead of this rate — check eligibility with your CA."
)


def load_jsonl(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec["id"]] = rec
    return out


def sector_for(rec):
    if rec["entity_type"] == "HSN":
        chapter = rec["code"][:2]
        return CHAPTER_SECTOR.get(chapter)
    if rec["entity_type"] == "SAC":
        prefix = rec["code"][:3]
        return SAC_PREFIX_SECTOR.get(prefix)
    return None


def upgrade(rec_id, old, group_ids):
    m = MASTER[rec_id]
    sector = sector_for(old)
    if sector is None:
        return None  # not one of the chapters this pass covers

    ai = copy.deepcopy(old["ai"])
    ai["attributes"]["sector"] = sector
    composition_note = None if old["entity_type"] == "SAC" else GOODS_COMPOSITION_NOTE

    rate = build_rate(
        m,
        exceptions=old["rate"].get("exceptions", []),
        caveat=old["rate"].get("rate_caveat"),
        composition_note=composition_note,
    )
    rec = {
        "id": rec_id,
        "code": old["code"],
        "entity_type": old["entity_type"],
        "title": old["title"],
        "rate": rate,
        "ai": ai,
        "search_text": build_search_text(ai),
        "enrichment_status": old["enrichment_status"],
        "ai_checksum": "PENDING_CHECKSUM",
    }
    return rec, group_ids


def main():
    old_records = load_jsonl(ENRICHED_PATH)
    golden_records = load_jsonl(GOLDEN_PATH)

    well_formed = {
        rid: r for rid, r in old_records.items()
        if r.get("entity_type") in ("HSN", "SAC") and "rate" in r
    }

    # Cross-references aren't confined to one chapter (e.g. 61xx knitted garments are
    # routinely cross-referenced against their 62xx woven counterparts, and the 19-22
    # food chapters cross-reference each other too), so use the full well-formed set as
    # the candidate pool rather than a strict per-chapter grouping.
    # a couple of existing exclusion_notes/clarification_questions reference real
    # sibling codes (SAC_998231, HSN_21069020) that exist in the master but aren't
    # separately enriched yet -- legitimate references, not invented ones.
    all_ids = list(well_formed.keys()) + ["SAC_998231", "HSN_21069020"]

    prepared = []
    skipped_already_golden = 0
    skipped_out_of_scope = 0

    for rid, old in well_formed.items():
        if rid in golden_records:
            skipped_already_golden += 1
            continue
        result = upgrade(rid, old, all_ids)
        if result is None:
            skipped_out_of_scope += 1
            continue
        prepared.append(result)

    print(f"well-formed v3 records: {len(well_formed)}")
    print(f"  already covered by golden_dataset.jsonl (skipped): {skipped_already_golden}")
    print(f"  out of this pass's chapter scope (skipped): {skipped_out_of_scope}")
    print(f"  upgrading: {len(prepared)}")

    all_errors = {}
    for rec, candidates in prepared:
        errs = validate(rec, candidates, MASTER)
        if errs:
            all_errors[rec["id"]] = errs

    if all_errors:
        print(f"\nVALIDATION FAILED for {len(all_errors)} record(s):")
        for rid, errs in list(all_errors.items())[:20]:
            print(f"  {rid}:")
            for e in errs:
                print(f"    - {e}")
        if len(all_errors) > 20:
            print(f"  ... and {len(all_errors) - 20} more")
        return 1

    print(f"\nAll {len(prepared)} upgraded records passed validation.")
    finalized = [finalize(rec) for rec, _ in prepared]

    # merge the upgraded batch, then also fold in the golden set (adds the 5 brand-new
    # ids and re-confirms the 21 already-upgraded ones) so enriched.jsonl ends up fully v5
    total, new = write_jsonl(finalized, path=ENRICHED_PATH)
    print(f"enriched.jsonl now has {total} records ({new} new from the bulk upgrade).")
    golden_list = list(golden_records.values())
    total2, new2 = write_jsonl(golden_list, path=ENRICHED_PATH)
    print(f"enriched.jsonl now has {total2} records ({new2} new from folding in the golden set).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
