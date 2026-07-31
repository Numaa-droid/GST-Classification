"""
Golden dataset builder for enrichment_prompt_v5.md.

Builds a small, hand-vetted, fully v5-schema-compliant reference set covering:
  - the three ambiguity terms judges are told to type (v5 Section 11): mask, bolt,
    packing material -- plus their full candidate sibling sets
  - the four worked examples from v5 Section 8

Two of those worked examples (HSN "0409" and SAC "99541") turned out to differ from
the prompt's own illustrative numbers once checked against the real merged 1.jsonl:
  - There is no 4-digit HSN_0409 entity in the source at all -- honey's heading has
    only one 8-digit tariff item, so the real id is HSN_04090000, and it DOES have a
    Source B rate match (5%, low confidence) rather than being unresolved as the v5
    example illustrates.
  - SAC_99541 (the group heading) carries a real matched rate (18%, medium confidence,
    inherited from the 9954 heading level) rather than being unresolved/rateless as
    the v5 example illustrates.
Hard rule #2 (no invented rates, ever) means the real data wins; this file follows
merged 1.jsonl, not the prompt's illustrative text, for both.

Upgrades 21 records already produced under the v3 schema (in enriched.jsonl) by adding
the v5-only fields (sector, exemption_status, composition_note) and rebuilding
search_text/checksum; authors 5 new records from scratch (HSN_8708, HSN_4819,
HSN_04090000, SAC_99541, NIC_14101). Writes everything to a separate golden_dataset.jsonl
-- enriched.jsonl is left untouched.
"""
import sys
import json
import copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import (
    load_master, build_rate, nic_rate, build_search_text, validate, finalize, write_jsonl, ROOT
)

MASTER = load_master()
OLD_ENRICHED_PATH = ROOT / "enriched.jsonl"
GOLDEN_PATH = ROOT / "golden_dataset.jsonl"


def load_old_records():
    old = {}
    with open(OLD_ENRICHED_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            old[rec["id"]] = rec
    return old


OLD = load_old_records()

# ---------------------------------------------------------------- candidate sets
MASK_CANDIDATES = [
    "HSN_6301", "HSN_6302", "HSN_6303", "HSN_6304", "HSN_6305", "HSN_6306", "HSN_6307", "HSN_6310",
    "HSN_63079091",
    "HSN_3301", "HSN_3302", "HSN_3303", "HSN_3304", "HSN_3305", "HSN_3306", "HSN_3307", "HSN_33049990",
    "HSN_90200000",
]
BOLT_CANDIDATES = ["HSN_7318", "HSN_8708"]
PACKING_CANDIDATES = ["HSN_3923", "HSN_4819", "HSN_3924"]
TSHIRT_CANDIDATES = ["HSN_6109", "HSN_6206", "HSN_6211", "HSN_6105"]
HONEY_CANDIDATES = ["HSN_04090000"]
CONSTRUCTION_CANDIDATES = ["SAC_99541", "SAC_995411", "SAC_995412", "SAC_995413", "SAC_9954"]
GARMENT_MFG_CANDIDATES = ["NIC_14101", "NIC_46411", "NIC_13921"]

CANDIDATES_BY_ID = {}
for _id in MASK_CANDIDATES:
    CANDIDATES_BY_ID[_id] = MASK_CANDIDATES
CANDIDATES_BY_ID["HSN_7318"] = BOLT_CANDIDATES
CANDIDATES_BY_ID["HSN_8708"] = BOLT_CANDIDATES
CANDIDATES_BY_ID["HSN_3923"] = PACKING_CANDIDATES
CANDIDATES_BY_ID["HSN_4819"] = PACKING_CANDIDATES
CANDIDATES_BY_ID["HSN_6109"] = TSHIRT_CANDIDATES
CANDIDATES_BY_ID["HSN_04090000"] = HONEY_CANDIDATES
CANDIDATES_BY_ID["SAC_99541"] = CONSTRUCTION_CANDIDATES
CANDIDATES_BY_ID["NIC_14101"] = GARMENT_MFG_CANDIDATES

# ------------------------------------------- Section 6 controlled sector, per upgraded id
SECTORS_BY_ID = {
    "HSN_6301": ["Textiles & Apparel"],
    "HSN_6302": ["Textiles & Apparel"],
    "HSN_6303": ["Textiles & Apparel"],
    "HSN_6304": ["Textiles & Apparel"],
    "HSN_6305": ["Textiles & Apparel"],
    "HSN_6306": ["Textiles & Apparel", "Construction & Building Materials"],
    "HSN_6307": ["Textiles & Apparel"],
    "HSN_63079091": ["Textiles & Apparel"],
    "HSN_6310": ["Textiles & Apparel"],
    "HSN_3301": ["Chemicals & Pharmaceuticals"],
    "HSN_3302": ["Chemicals & Pharmaceuticals"],
    "HSN_3303": ["Consumer Goods & Household"],
    "HSN_3304": ["Consumer Goods & Household"],
    "HSN_33049990": ["Consumer Goods & Household"],
    "HSN_3305": ["Consumer Goods & Household"],
    "HSN_3306": ["Consumer Goods & Household"],
    "HSN_3307": ["Consumer Goods & Household"],
    "HSN_90200000": ["Engineering & Machinery"],
    "HSN_6109": ["Textiles & Apparel"],
    "HSN_3923": ["Plastics & Rubber"],
    "HSN_7318": ["Metals & Metal Products", "Engineering & Machinery"],
}

GOODS_COMPOSITION_NOTE = (
    "Small manufacturers and traders under the composition scheme pay a flat "
    "turnover-based GST rate instead of this rate — check eligibility with your CA."
)


# ---------------------------------------------------------------- cross-link patches
def patch_7318(ai):
    """7318 (generic fasteners) needs to point at the new 8708 (vehicle-part) sibling
    now that the golden set covers the 'bolt' demo term end to end."""
    ai["clarification_questions"].append({
        "question": "Is this a generic hardware fastener, or a part sold specifically for a motor vehicle?",
        "attribute": "use",
        "options": ["Generic hardware fastener", "Motor vehicle spare part"],
        "disambiguates_from": ["HSN_8708"],
    })
    ai["exclusion_notes"].append({
        "excluded_code": "HSN_8708",
        "reason": "8708 covers the same physical bolt/nut when it is manufactured and sold specifically as a motor vehicle part or accessory, not as generic hardware",
    })
    ai["classification_confidence"] = {
        "level": "Medium",
        "rationale": "A generic bolt maps clearly to 7318, but the identical item sold as a branded vehicle spare part is classified under 8708 instead — the deciding factor is how it's sold, not its shape.",
        "ambiguity_triggers": ["car part", "vehicle part", "spare part", "OEM", "automotive"],
    }
    ai["plain_rationale"] = (
        ai["plain_rationale"]
        + " If the same bolt is manufactured and sold specifically as a motor vehicle spare part rather than generic hardware, it belongs under HSN 8708 instead."
    )


def patch_3923(ai):
    """3923 (plastic packing) needs to point at the new 4819 (paper packing) sibling
    now that the golden set covers the 'packing material' demo term end to end."""
    ai["clarification_questions"].append({
        "question": "Is the packing material made of plastic, or of paper/paperboard?",
        "attribute": "material",
        "options": ["Plastic", "Paper / paperboard"],
        "disambiguates_from": ["HSN_4819"],
    })
    ai["exclusion_notes"].append({
        "excluded_code": "HSN_4819",
        "reason": "4819 covers the same kind of packing/conveyance article (cartons, boxes, bags) but made of paper or paperboard rather than plastic",
    })
    ai["classification_confidence"] = {
        "level": "Medium",
        "rationale": "Packaging articles map clearly to 3923 once the material is known to be plastic, but 'packing material' alone is genuinely split between this heading and the paper/paperboard equivalent, 4819.",
        "ambiguity_triggers": ["paper box", "cardboard box", "carton", "paperboard"],
    }
    ai["plain_rationale"] = (
        ai["plain_rationale"]
        + " The paper/paperboard equivalent — cardboard cartons and boxes — falls under HSN 4819 instead."
    )


PATCHES = {"HSN_7318": patch_7318, "HSN_3923": patch_3923}


def upgrade(rec_id):
    """Take a v3-schema record already in enriched.jsonl and lift it to v5: add sector,
    exemption_status (derived) and composition_note, reusing the master for the rate
    block so the numbers stay mechanically correct rather than copy-pasted."""
    old = OLD[rec_id]
    m = MASTER[rec_id]
    ai = copy.deepcopy(old["ai"])
    ai["attributes"]["sector"] = SECTORS_BY_ID[rec_id]
    if rec_id in PATCHES:
        PATCHES[rec_id](ai)

    rate = build_rate(
        m,
        exceptions=old["rate"]["exceptions"],
        caveat=old["rate"]["rate_caveat"],
        composition_note=GOODS_COMPOSITION_NOTE,
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
    return rec, CANDIDATES_BY_ID[rec_id]


UPGRADE_IDS = list(SECTORS_BY_ID)

# ======================================================================== new records
NEW_RECORDS = []  # list of (id, candidates, record_dict_builder)


def r_hsn_8708():
    m = MASTER["HSN_8708"]
    rate = build_rate(
        m,
        exceptions=[{
            "gst_rate": 18.0,
            "condition": "Parts/accessories of motor vehicles (headings 8701-8705) other than specified tractor parts",
        }],
        composition_note=(
            "Small auto-component manufacturers and traders under the composition scheme pay a flat "
            "turnover-based GST rate instead of this rate — check eligibility with your CA."
        ),
    )
    ai = {
        "synonyms": ["vehicle bolt", "car part bolt", "automotive fastener", "chassis bolt", "engine mounting bolt", "OEM vehicle part"],
        "market_terms": ["automotive spare parts trade", "OEM auto components", "vehicle parts wholesale"],
        "hindi_transliterated": ["gaadi ka part"],
        "examples": [
            "chassis mounting bolt sold as a branded car spare part",
            "engine bracket bolt supplied as an OEM automotive component",
        ],
        "attributes": {
            "material": ["steel", "iron", "alloy"],
            "use": ["automotive repair", "vehicle assembly"],
            "form": ["bolt", "fastener", "vehicle part"],
            "industry": ["automotive", "auto components", "vehicle parts"],
            "sector": ["Automotive & Transport"],
        },
        "clarification_questions": [{
            "question": "Is the bolt a generic hardware fastener, or a part made specifically for a motor vehicle?",
            "attribute": "use",
            "options": ["Generic hardware fastener", "Vehicle-specific spare part"],
            "disambiguates_from": ["HSN_7318"],
        }],
        "exclusion_notes": [{
            "excluded_code": "HSN_7318",
            "reason": "7318 is the generic heading for iron/steel screws, bolts and nuts sold as hardware — use 8708 only when the bolt is manufactured and sold specifically as a motor vehicle part or accessory",
        }],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "A bolt sold as a branded motor-vehicle spare part is classified here rather than under the generic fastener heading (7318) — the deciding factor is how the product is sold, not its physical shape.",
            "ambiguity_triggers": ["nut", "screw", "hardware", "generic fastener", "washer"],
        },
        "plain_rationale": (
            "HSN 8708 covers parts and accessories made specifically for motor vehicles of headings 8701 to "
            "8705 — including ordinary-looking bolts, brackets and fasteners once they're manufactured and sold "
            "as a vehicle part rather than as generic hardware. The 5% rate shown here matches specified tractor "
            "parts; most other motor-vehicle parts (cars, two-wheelers, commercial vehicles) attract 18% instead "
            "— confirm which bucket your specific part falls into before invoicing."
        ),
        "regulatory_citation": "ITC(HS) 2022, Chapter 87, Heading 8708 — parts and accessories of motor vehicles of headings 8701 to 8705. Rate per Notification 9/2025-Integrated Tax (Rate).",
    }
    rec = {
        "id": "HSN_8708", "code": m["code"], "entity_type": "HSN",
        "title": "Parts and accessories of motor vehicles of headings 8701 to 8705",
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    return rec, BOLT_CANDIDATES


def r_hsn_4819():
    m = MASTER["HSN_4819"]
    rate = build_rate(m, composition_note=(
        "Small packaging manufacturers and traders under the composition scheme pay a flat "
        "turnover-based GST rate instead of this rate — check eligibility with your CA."
    ))
    ai = {
        "synonyms": ["cardboard box", "paper carton", "packing box", "corrugated box", "paperboard container", "carton box"],
        "market_terms": ["corrugated packaging trade", "carton box manufacturing", "paperboard packaging supply"],
        "hindi_transliterated": ["dabba"],
        "examples": [
            "corrugated cardboard shipping box",
            "paperboard carton for retail packaging",
            "paper courier box used by an e-commerce seller",
        ],
        "attributes": {
            "material": ["paper", "paperboard", "corrugated board", "cellulose"],
            "use": ["packing", "shipping", "retail packaging"],
            "form": ["box", "carton", "case", "bag"],
            "industry": ["paper & packaging", "printing & packaging"],
            "sector": ["Wood, Paper & Packaging"],
        },
        "clarification_questions": [{
            "question": "Is the packing material made of paper/paperboard, or of plastic?",
            "attribute": "material",
            "options": ["Paper / paperboard", "Plastic"],
            "disambiguates_from": ["HSN_3923"],
        }],
        "exclusion_notes": [{
            "excluded_code": "HSN_3923",
            "reason": "3923 covers the same kind of packing/conveyance article (bottles, containers, bags) but made of plastics rather than paper or paperboard",
        }],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "Once the material is confirmed as paper/paperboard, this heading is clear — but 'packing material' as a plain-language term is genuinely split between this heading and its plastic equivalent, 3923.",
            "ambiguity_triggers": ["plastic", "poly bag", "pouch", "PET"],
        },
        "plain_rationale": (
            "HSN 4819 covers cartons, boxes, cases, bags and similar packing containers made of paper, "
            "paperboard or cellulose fibre — including corrugated shipping boxes and retail cartons — plus "
            "box files and letter trays of the kind used in offices. GST is 18%, but this was matched with low "
            "confidence at the heading level rather than a rule written specifically for this item, so confirm "
            "it with your CA before invoicing. The plastic equivalent of the same packing containers falls "
            "under HSN 3923 instead."
        ),
        "regulatory_citation": "ITC(HS) 2022, Chapter 48, Heading 4819 — paper/paperboard packing containers, box files and letter trays. Rate per Notification 9/2025-Integrated Tax (Rate).",
    }
    rec = {
        "id": "HSN_4819", "code": m["code"], "entity_type": "HSN",
        "title": "Cartons, boxes and other packing containers, and box files/letter trays, of paper or paperboard",
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    return rec, PACKING_CANDIDATES


def r_hsn_honey():
    m = MASTER["HSN_04090000"]
    rate = build_rate(m, composition_note=(
        "Small honey traders and processors under the composition scheme pay a flat "
        "turnover-based GST rate instead of this rate — check eligibility with your CA."
    ))
    ai = {
        "synonyms": ["natural honey", "raw honey", "pure honey", "unprocessed honey"],
        "market_terms": ["natural honey bulk trade", "raw honey wholesale", "honey export trade"],
        "hindi_transliterated": ["shahad"],
        "examples": [
            "raw forest honey sold loose by weight",
            "natural honey in a plain unbranded jar",
            "branded honey jar sold in a supermarket",
        ],
        "attributes": {
            "material": ["honey"],
            "use": ["food", "edible"],
            "form": ["raw", "natural", "unprocessed"],
            "industry": ["food processing", "agriculture", "apiculture"],
            "sector": ["Food & Beverages", "Agriculture & Live Animals"],
        },
        "clarification_questions": [{
            "question": "Is the honey sold in a branded, sealed unit container, or loose/unbranded?",
            "attribute": "branding",
            "options": ["Branded, sealed container", "Unbranded / loose"],
            "disambiguates_from": [],
        }],
        "exclusion_notes": [],
        "classification_confidence": {
            "level": "High",
            "rationale": "Natural honey maps uniquely to this heading regardless of branding or packaging.",
            "ambiguity_triggers": ["processed honey", "flavoured honey", "honey-based syrup"],
        },
        "plain_rationale": (
            "HSN 04090000 covers natural honey — the raw product as it comes from the hive, whether sold loose "
            "or in a sealed retail jar. GST is 5%, matched at the heading level but with low confidence, so "
            "confirm the current rate with your CA before invoicing. Branded, sealed packs and loose, unbranded "
            "honey are taxed the same way at this heading."
        ),
        "regulatory_citation": "ITC(HS) 2022, Chapter 4, Heading 0409, tariff item 0409 00 00 — natural honey. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    }
    rec = {
        "id": "HSN_04090000", "code": m["code"], "entity_type": "HSN",
        "title": "Natural honey",
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    return rec, HONEY_CANDIDATES


def r_sac_construction():
    m = MASTER["SAC_99541"]
    rate = build_rate(
        m,
        exceptions=[
            {"gst_rate": 1.5, "condition": "Affordable residential apartment construction under RREP/REP schemes commencing on/after 1 April 2019"},
            {"gst_rate": 0.0, "condition": "Pure labour contracts for construction of a single residential unit outside a residential complex"},
        ],
        composition_note=None,  # works-contract/construction services are not a clean composition-scheme fit -- don't guess
    )
    ai = {
        "synonyms": ["building construction", "construction services", "building work", "civil construction"],
        "market_terms": ["civil construction services group", "works contract services", "building contractor services"],
        "hindi_transliterated": ["nirman seva"],
        "examples": [
            "group heading covering all building-construction sub-services",
            "a contractor invoicing for residential building construction",
        ],
        "attributes": {
            "material": [],
            "use": ["construction"],
            "form": ["group heading"],
            "industry": ["construction", "real estate", "works contract"],
            "sector": ["Construction & Building Materials"],
        },
        "clarification_questions": [{
            "question": "What kind of building are you constructing?",
            "attribute": "use",
            "options": ["Residential (dwelling)", "Other residential (hostel, shelter, etc.)", "Industrial", "Not sure"],
            "disambiguates_from": ["SAC_995411", "SAC_995412", "SAC_995413"],
        }],
        "exclusion_notes": [{
            "excluded_code": "SAC_995411",
            "reason": "995411 is the specific 6-digit code for construction of dwelling/residential buildings — use this group heading (99541) for browsing only, not for the actual invoice",
        }],
        "classification_confidence": {
            "level": "Low",
            "rationale": "Group-level heading covering several 6-digit sub-codes; a specific sub-code is needed for the actual invoice even though this group heading does carry an inherited rate.",
            "ambiguity_triggers": [],
        },
        "plain_rationale": (
            "SAC 99541 is a group heading for building construction services, organising the more specific "
            "6-digit codes beneath it (residential, other residential, industrial). It inherits an 18% rate "
            "from the parent Construction Services heading (9954), but that entry also carries major carve-outs "
            "still on the 2017 service-rate regime: affordable residential apartments under RREP/REP schemes "
            "drop to 1.5%, and pure labour contracts for a single residential unit are exempt. Pick the specific "
            "6-digit sub-code matching your project type for the actual invoice."
        ),
        "regulatory_citation": "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC group 99541 — Construction services of buildings.",
    }
    rec = {
        "id": "SAC_99541", "code": m["code"], "entity_type": "SAC",
        "title": "Construction services of buildings",
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    return rec, CONSTRUCTION_CANDIDATES


def r_nic_garments():
    ai = {
        "synonyms": ["garment manufacturing", "clothing manufacturing", "apparel making", "readymade garment unit", "tailoring unit"],
        "market_terms": ["RMG manufacturing", "apparel production", "garment factory", "CMT unit"],
        "hindi_transliterated": ["kapda silai"],
        "examples": [
            "a small unit stitching cotton shirts for wholesale",
            "a factory producing readymade kurtas",
            "a job-work tailoring unit making school uniforms",
        ],
        "attributes": {
            "material": ["cotton", "polyester", "knitted fabric", "woven fabric"],
            "use": ["manufacturing", "production"],
            "form": ["factory", "manufacturing unit"],
            "industry": ["textiles", "garments", "apparel", "manufacturing"],
            "sector": ["Textiles & Apparel"],
        },
        "clarification_questions": [{
            "question": "Do you manufacture the garments, or only trade in them?",
            "attribute": "retail_industrial",
            "options": ["Manufacture", "Trade / resell", "Both"],
            "disambiguates_from": ["NIC_46411"],
        }],
        "exclusion_notes": [
            {"excluded_code": "NIC_46411", "reason": "46411 is wholesale trade of textiles — use 14101 only if you actually manufacture the garments"},
            {"excluded_code": "NIC_13921", "reason": "13921 covers made-up textile articles like curtains and bed linen, not wearable garments"},
        ],
        "classification_confidence": {
            "level": "High",
            "rationale": "Garment manufacturing maps cleanly to 14101; the main risk is confusing manufacturing with trading.",
            "ambiguity_triggers": ["trading", "wholesale", "retail", "reselling", "job work"],
        },
        "plain_rationale": (
            "NIC 14101 is the activity code for manufacturing textile garments and clothing accessories. You "
            "use it when registering with MCA or on the MSME (Udyam) portal — it describes what your business "
            "does, not what you sell. If you only buy and resell garments without making them, you need a "
            "wholesale or retail trade code instead. NIC codes carry no GST rate; for tax, use the HSN code of "
            "the garments you produce."
        ),
        "regulatory_citation": "National Industrial Classification 2008 (MoSPI), Division 14, Class 1410, Sub-class 14101.",
    }
    rec = {
        "id": "NIC_14101", "code": "14101", "entity_type": "NIC",
        "title": "Manufacture of all types of textile garments and clothing accessories",
        "rate": nic_rate(), "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    return rec, GARMENT_MFG_CANDIDATES


NEW_BUILDERS = [r_hsn_8708, r_hsn_4819, r_hsn_honey, r_sac_construction, r_nic_garments]


def main():
    prepared = [upgrade(rid) for rid in UPGRADE_IDS]
    prepared += [builder() for builder in NEW_BUILDERS]

    all_errors = {}
    for rec, candidates in prepared:
        errs = validate(rec, candidates, MASTER)
        if errs:
            all_errors[rec["id"]] = errs

    if all_errors:
        print(f"VALIDATION FAILED for {len(all_errors)} record(s):")
        for rid, errs in all_errors.items():
            print(f"  {rid}:")
            for e in errs:
                print(f"    - {e}")
        return 1

    print(f"All {len(prepared)} records passed validation.")
    finalized = [finalize(rec) for rec, _ in prepared]
    total, new = write_jsonl(finalized, path=GOLDEN_PATH)
    print(f"{GOLDEN_PATH.name} now has {total} records ({new} new from this run).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
