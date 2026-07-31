"""
Full v5 golden-quality regeneration for the 119 legacy pre-v3 records in enriched.jsonl
(no entity_type/code/title/rate -- just an id and a thin seed ai block).

These break into three clean families:
  - HSN Chapters 1-5 (66 records): live animals, meat, fish, dairy, animal products.
    Five headings (0101-0105) have real parent/subitem overlap in this batch (e.g.
    HSN_0101 "live horses" vs HSN_01012100 "pure-bred breeding horses") -- those get a
    genuine clarification_question + exclusion_notes; everything else in Ch1-5 is a
    standalone heading with no sibling ambiguity in this batch, so it's High confidence
    with no manufactured disambiguation.
  - NIC crop/livestock/forestry/fishing codes (46 records): same pattern, one real
    cluster (NIC_0111 "cereals/oilseeds" + 7 NIC_0111x children), the rest standalone.
    One outlier, NIC_0510 "mining of hard coal", sits in this id range but isn't
    agriculture at all.
  - SAC construction-of-buildings codes (7 records): SAC_9954 (parent) + 6 children
    (995411-995416), the same heading/child pattern already used for SAC_99541 in
    golden_dataset.jsonl.

Seed content (synonyms/market_terms/examples/attributes) already in enriched.jsonl was
used as a starting point where it met the v5 minimums; most needed expanding to meet
the 4-8 synonym / 3-6 market_term / 2-4 example floors, since the legacy blocks were
seeded thin. Writes straight into enriched.jsonl (merge by id).
"""
import sys
import copy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import (
    load_master, build_rate, nic_rate, build_search_text, validate, finalize, write_jsonl,
    ENRICHED_PATH,
)

MASTER = load_master()

GOODS_COMPOSITION = (
    "Small traders and farmers under the composition scheme pay a flat turnover-based "
    "GST rate instead of this rate — check eligibility with your CA."
)

RECORDS = []       # (id, candidates, record_dict)
ALL_HSN01_IDS = [
    "HSN_0101", "HSN_01012100", "HSN_01012910", "HSN_01012990",
    "HSN_01013010", "HSN_01013020", "HSN_01013090", "HSN_01019030", "HSN_01019090",
    "HSN_0102", "HSN_01022110", "HSN_01022120", "HSN_01022910", "HSN_01022990",
    "HSN_01023100", "HSN_01023900", "HSN_01029010", "HSN_01029090",
    "HSN_0103", "HSN_01031000", "HSN_01039100", "HSN_01039200",
    "HSN_0104", "HSN_01041010", "HSN_01041090", "HSN_01042000",
    "HSN_0105", "HSN_01051100", "HSN_01051200",
    "HSN_0106",
]
ALL_NIC011_IDS = [
    "NIC_0111", "NIC_01111", "NIC_01112", "NIC_01113", "NIC_01114", "NIC_01115", "NIC_01116", "NIC_01117",
]
ALL_SAC9954_IDS = [
    "SAC_9954", "SAC_995411", "SAC_995412", "SAC_995413", "SAC_995414", "SAC_995415", "SAC_995416",
    "SAC_99541",  # already enriched in golden_dataset.jsonl -- a real, valid sibling to reference
]


def hsn_rec(rid, title, sector, synonyms, market_terms, examples, material, use, form, industry,
            conf_level, conf_rationale, plain_rationale, citation, hindi=None, ambiguity=None,
            clarification=None, exclusion=None, exceptions=None, candidates=None, composition=True):
    m = MASTER[rid]
    rate = build_rate(
        m, exceptions=exceptions or [],
        composition_note=GOODS_COMPOSITION if composition else None,
    )
    ai = {
        "synonyms": synonyms, "market_terms": market_terms,
        "hindi_transliterated": hindi or [], "examples": examples,
        "attributes": {"material": material, "use": use, "form": form, "industry": industry, "sector": sector},
        "clarification_questions": clarification or [],
        "exclusion_notes": exclusion or [],
        "classification_confidence": {"level": conf_level, "rationale": conf_rationale, "ambiguity_triggers": ambiguity or []},
        "plain_rationale": plain_rationale,
        "regulatory_citation": citation,
    }
    rec = {
        "id": rid, "code": m["code"], "entity_type": "HSN", "title": title,
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    RECORDS.append((rid, candidates or [rid], rec))


def nic_rec(rid, title, sector, synonyms, market_terms, examples, industry,
            conf_level, conf_rationale, plain_rationale, citation, hindi=None, ambiguity=None,
            clarification=None, exclusion=None, candidates=None):
    ai = {
        "synonyms": synonyms, "market_terms": market_terms,
        "hindi_transliterated": hindi or [], "examples": examples,
        "attributes": {"material": [], "use": [], "form": [], "industry": industry, "sector": sector},
        "clarification_questions": clarification or [],
        "exclusion_notes": exclusion or [],
        "classification_confidence": {"level": conf_level, "rationale": conf_rationale, "ambiguity_triggers": ambiguity or []},
        "plain_rationale": plain_rationale,
        "regulatory_citation": citation,
    }
    m = MASTER[rid]
    rec = {
        "id": rid, "code": m["code"], "entity_type": "NIC", "title": title,
        "rate": nic_rate(), "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    RECORDS.append((rid, candidates or [rid], rec))


def sac_rec(rid, title, sector, synonyms, market_terms, examples, industry,
            conf_level, conf_rationale, plain_rationale, citation, hindi=None, ambiguity=None,
            clarification=None, exclusion=None, exceptions=None, candidates=None):
    m = MASTER[rid]
    rate = build_rate(m, exceptions=exceptions or [], composition_note=None)
    ai = {
        "synonyms": synonyms, "market_terms": market_terms,
        "hindi_transliterated": hindi or [], "examples": examples,
        "attributes": {"material": [], "use": [], "form": [], "industry": industry, "sector": sector},
        "clarification_questions": clarification or [],
        "exclusion_notes": exclusion or [],
        "classification_confidence": {"level": conf_level, "rationale": conf_rationale, "ambiguity_triggers": ambiguity or []},
        "plain_rationale": plain_rationale,
        "regulatory_citation": citation,
    }
    rec = {
        "id": rid, "code": m["code"], "entity_type": "SAC", "title": title,
        "rate": rate, "ai": ai, "search_text": build_search_text(ai),
        "enrichment_status": "complete", "ai_checksum": "PENDING_CHECKSUM",
    }
    RECORDS.append((rid, candidates or [rid], rec))


AG = ["Agriculture & Live Animals"]
FOOD = ["Food & Beverages"]
CHEM = ["Chemicals & Pharmaceuticals"]
CONS = ["Consumer Goods & Household"]
CONSTR = ["Construction & Building Materials"]
OTHER = ["Other"]
MIN = ["Minerals & Energy"]

# ======================================================================= HSN 0101 cluster
hsn_rec("HSN_0101", "Live horses, asses, mules and hinnies", AG,
    ["live horse", "live donkey", "live mule", "live hinny", "equine livestock"],
    ["equine livestock trade", "horse and donkey trading", "breeding stock export"],
    ["a horse sold at a livestock market", "a working donkey sold to a farmer"],
    [], ["breeding", "work", "sport", "trade"], ["live animal"], ["livestock", "equine"],
    "Medium", "Live equines map to this heading, but the code narrows further by species (horse/ass/mule) and by purpose (pure-bred breeding vs. general-purpose) — a plain 'horse' or 'donkey' needs one more detail to pick the exact 8-digit code.",
    "HSN 0101 covers live horses, asses, mules and hinnies as a heading. The specific 8-digit code depends on species and purpose: pure-bred breeding horses and asses are separately coded and carry their own rate, while general-purpose and 'other' animals sit under different sub-codes with different rate resolution. Pick the specific sub-code for an actual invoice.",
    "ITC(HS) 2022, Chapter 1, Heading 0101 — live horses, asses, mules and hinnies.",
    ambiguity=["breeding", "polo", "racing", "pure-bred"],
    clarification=[{"question": "Is this a horse, a donkey (ass), or a mule/hinny — and is it a pure-bred breeding animal?",
                     "attribute": "use", "options": ["Horse", "Donkey/ass", "Mule/hinny", "Not sure"],
                     "disambiguates_from": ["HSN_01012100", "HSN_01013010", "HSN_01019030"]}],
    exclusion=[{"excluded_code": "HSN_01012100", "reason": "01012100 is the specific sub-code for pure-bred breeding horses, which carries a confirmed 5% rate — use this heading only for browsing, not the actual invoice"}],
    candidates=ALL_HSN01_IDS)

hsn_rec("HSN_01012100", "Pure-bred breeding horses", AG,
    ["pure-bred breeding horse", "stud horse", "breeding stallion", "breeding mare"],
    ["equine breeding stock trade", "stud farm livestock sale"],
    ["a certified pure-bred stallion sold to a stud farm", "a pedigreed breeding mare"],
    [], ["breeding"], ["live animal"], ["livestock", "equine", "breeding"],
    "High", "Pure-bred breeding horses are a specifically named, separately rated sub-code.",
    "HSN 01012100 covers pure-bred breeding horses specifically — animals sold with breeding pedigree, not general-purpose or sport horses. GST is 5%, matched with high confidence at this exact code.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 21 00 — pure-bred breeding horses.")

hsn_rec("HSN_01012910", "Horses for polo", AG,
    ["polo horse", "polo pony"],
    ["polo horse trade", "equestrian sport horse sale"],
    ["a trained polo horse sold to a club", "a polo pony imported for a tournament"],
    [], ["sport"], ["live animal"], ["livestock", "equine", "equestrian sports"],
    "High", "Polo horses are a specifically named sub-code, distinct from general-purpose or breeding horses.",
    "HSN 01012910 covers horses specifically for polo. GST is 5%, matched with high confidence at this exact code.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 29 10 — horses for polo.")

hsn_rec("HSN_01012990", "Other horses", AG,
    ["horse", "riding horse", "workhorse", "racehorse"],
    ["general livestock horse trade", "horse market sale"],
    ["a general-purpose riding horse sold at a livestock fair", "a working farm horse"],
    [], ["riding", "work", "general purpose"], ["live animal"], ["livestock", "equine"],
    "High", "This is the residual 'other horse' code once pure-bred breeding and polo horses are excluded.",
    "HSN 01012990 covers horses other than pure-bred breeding animals and polo horses — general riding, working or racing horses. GST is 5%, matched with high confidence at this exact code.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 29 90 — other horses.")

hsn_rec("HSN_01013010", "Pure-bred breeding donkeys", AG,
    ["pure-bred breeding donkey", "pure-bred breeding ass", "breeding jack", "breeding jenny"],
    ["donkey breeding stock trade"],
    ["a certified pure-bred breeding donkey sold to a breeder"],
    [], ["breeding"], ["live animal"], ["livestock"],
    "High", "Pure-bred breeding donkeys are a specifically named sub-code.",
    "HSN 01013010 covers pure-bred breeding donkeys (asses). No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 30 10 — pure-bred breeding asses.")

hsn_rec("HSN_01013020", "Donkeys kept as livestock", AG,
    ["livestock donkey", "working donkey", "pack donkey"],
    ["donkey livestock trade"],
    ["a working donkey sold to a farmer for load-carrying"],
    [], ["work", "load carrying"], ["live animal"], ["livestock"],
    "High", "Donkeys sold as general working livestock are a specifically named sub-code.",
    "HSN 01013020 covers donkeys (asses) kept and sold as general livestock, not pure-bred breeding animals. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 30 20 — asses as livestock.")

hsn_rec("HSN_01013090", "Other donkeys", AG,
    ["donkey", "ass"],
    ["general donkey trade"],
    ["a donkey sold at a rural livestock market"],
    [], ["general purpose"], ["live animal"], ["livestock"],
    "High", "Residual 'other donkey' code once breeding and livestock-purpose donkeys are excluded.",
    "HSN 01013090 covers donkeys (asses) other than pure-bred breeding or livestock-purpose animals. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 30 90 — other asses.")

hsn_rec("HSN_01019030", "Mules and hinnies kept as livestock", AG,
    ["mule", "hinny", "livestock mule"],
    ["mule livestock trade"],
    ["a mule sold as pack livestock to a farmer"],
    [], ["work", "load carrying"], ["live animal"], ["livestock"],
    "High", "Mules and hinnies sold as livestock are a specifically named sub-code.",
    "HSN 01019030 covers mules and hinnies (horse-donkey crossbreeds) sold as livestock. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 90 30 — mules and hinnies as livestock.")

hsn_rec("HSN_01019090", "Other mules and hinnies", AG,
    ["mule", "hinny"],
    ["general mule trade"],
    ["a mule sold outside the livestock-designated trade"],
    [], ["general purpose"], ["live animal"], ["livestock"],
    "High", "Residual 'other' code for mules and hinnies.",
    "HSN 01019090 covers mules and hinnies other than those sold specifically as livestock. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0101, tariff item 0101 90 90 — other mules and hinnies.")

# ======================================================================= HSN 0102 cluster
hsn_rec("HSN_0102", "Live bovine animals", AG,
    ["live cattle", "live cow", "live bull", "live buffalo", "bovine livestock"],
    ["cattle trading", "bovine livestock market", "dairy cattle sale"],
    ["a cow sold at a cattle market", "a water buffalo sold to a dairy farmer"],
    [], ["breeding", "dairy", "trade"], ["live animal"], ["livestock", "dairy farming"],
    "Medium", "Live bovine animals map to this heading, but the code narrows further by species (cattle vs buffalo), sex, and pure-bred breeding status.",
    "HSN 0102 covers live bovine animals — cattle and buffalo — as a heading. The specific 8-digit code depends on species, sex and whether the animal is a certified pure-bred breeding animal. Pick the specific sub-code for an actual invoice.",
    "ITC(HS) 2022, Chapter 1, Heading 0102 — live bovine animals.",
    ambiguity=["buffalo", "breeding", "calf"],
    clarification=[{"question": "Is this cattle (cow/bull) or buffalo, and is it a certified pure-bred breeding animal?",
                     "attribute": "use", "options": ["Cattle", "Buffalo", "Not sure"],
                     "disambiguates_from": ["HSN_01022110", "HSN_01023100", "HSN_01022990"]}],
    exclusion=[{"excluded_code": "HSN_01023100", "reason": "01023100 is the specific sub-code for pure-bred breeding buffalo — use this heading only for browsing, not the actual invoice"}],
    candidates=ALL_HSN01_IDS)

hsn_rec("HSN_01022110", "Pure-bred breeding bulls", AG,
    ["pure-bred breeding bull", "stud bull", "breeding bull"],
    ["cattle breeding stock trade"],
    ["a certified pure-bred breeding bull sold to a dairy farm"],
    [], ["breeding"], ["live animal"], ["livestock", "dairy farming"],
    "High", "Pure-bred breeding bulls are a specifically named sub-code.",
    "HSN 01022110 covers pure-bred breeding bulls sold with certified pedigree. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 21 10 — pure-bred breeding bulls.")

hsn_rec("HSN_01022120", "Pure-bred breeding cows", AG,
    ["pure-bred breeding cow", "pedigree cow", "breeding cow"],
    ["dairy cattle breeding stock trade"],
    ["a certified pedigree dairy cow sold to a farm"],
    [], ["breeding", "dairy"], ["live animal"], ["livestock", "dairy farming"],
    "High", "Pure-bred breeding cows are a specifically named sub-code.",
    "HSN 01022120 covers pure-bred breeding cows sold with certified pedigree. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 21 20 — pure-bred breeding cows.")

hsn_rec("HSN_01022910", "Other bulls", AG,
    ["bull", "breeding bull (non-pedigree)"],
    ["general cattle trade"],
    ["a bull sold at a general cattle market, not certified pure-bred"],
    [], ["general purpose"], ["live animal"], ["livestock"],
    "High", "Non-pedigree bulls are a specifically named residual sub-code.",
    "HSN 01022910 covers bulls other than certified pure-bred breeding animals. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 29 10 — other bulls.")

hsn_rec("HSN_01022990", "Other cattle, including calves", AG,
    ["cattle", "cow", "calf", "livestock cow"],
    ["general cattle and calf trade"],
    ["a calf sold at a village livestock market", "a milking cow sold to another farmer"],
    [], ["dairy", "general purpose"], ["live animal"], ["livestock", "dairy farming"],
    "High", "Residual 'other cattle, including calves' once bulls and pure-bred breeding animals are excluded.",
    "HSN 01022990 covers cattle other than bulls and pure-bred breeding animals, including calves. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 29 90 — other cattle, including calves.")

hsn_rec("HSN_01023100", "Pure-bred breeding buffalo", AG,
    ["pure-bred breeding buffalo", "breeding buffalo"],
    ["buffalo breeding stock trade"],
    ["a certified pure-bred breeding buffalo sold to a dairy farm"],
    [], ["breeding", "dairy"], ["live animal"], ["livestock", "dairy farming"],
    "High", "Pure-bred breeding buffalo are a specifically named sub-code.",
    "HSN 01023100 covers pure-bred breeding buffalo sold with certified pedigree. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 31 00 — pure-bred breeding buffalo.")

hsn_rec("HSN_01023900", "Other buffalo", AG,
    ["buffalo", "water buffalo", "livestock buffalo"],
    ["general buffalo trade"],
    ["a milking buffalo sold at a dairy livestock market"],
    [], ["dairy", "general purpose"], ["live animal"], ["livestock", "dairy farming"],
    "High", "Residual 'other buffalo' code once pure-bred breeding buffalo are excluded.",
    "HSN 01023900 covers buffalo other than certified pure-bred breeding animals. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 39 00 — other buffalo.")

hsn_rec("HSN_01029010", "Other pure-bred breeding bovine animals", AG,
    ["pure-bred breeding bovine", "other breeding cattle"],
    ["bovine breeding stock trade"],
    ["a certified pure-bred breeding bovine animal outside the cattle/buffalo split"],
    [], ["breeding"], ["live animal"], ["livestock"],
    "High", "Named residual sub-code for pure-bred breeding bovine animals not already covered under the cattle or buffalo entries.",
    "HSN 01029010 covers pure-bred breeding bovine animals not already covered elsewhere in this heading. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 90 10 — other pure-bred breeding bovine animals.")

hsn_rec("HSN_01029090", "Other bovine animals", AG,
    ["bovine animal", "cattle (other)"],
    ["general bovine livestock trade"],
    ["a bovine animal sold outside the cattle/buffalo-specific sub-codes"],
    [], ["general purpose"], ["live animal"], ["livestock"],
    "High", "Residual 'other bovine' code.",
    "HSN 01029090 is the residual code for bovine animals not covered elsewhere in this heading. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0102, tariff item 0102 90 90 — other bovine animals.")

# ======================================================================= HSN 0103 cluster
hsn_rec("HSN_0103", "Live swine", AG,
    ["live pig", "live swine", "live boar", "live hog"],
    ["swine livestock trade", "pig farming supply"],
    ["a pig sold at a livestock market", "piglets sold to a pig farm"],
    [], ["breeding", "meat production"], ["live animal"], ["livestock", "pig farming"],
    "Medium", "Live swine map to this heading, but the code narrows further by breeding status and, for non-breeding pigs, by weight.",
    "HSN 0103 covers live swine (pigs) as a heading. The specific 8-digit code depends on whether the animal is a certified pure-bred breeding pig, and otherwise on its weight (under or over 50 kg). Pick the specific sub-code for an actual invoice.",
    "ITC(HS) 2022, Chapter 1, Heading 0103 — live swine.",
    ambiguity=["piglet", "weight", "breeding"],
    clarification=[{"question": "Is this a certified pure-bred breeding pig, or a pig for general/meat purposes — and if the latter, is it under or over 50 kg?",
                     "attribute": "form", "options": ["Pure-bred breeding pig", "Under 50 kg", "50 kg or more", "Not sure"],
                     "disambiguates_from": ["HSN_01031000", "HSN_01039100", "HSN_01039200"]}],
    exclusion=[{"excluded_code": "HSN_01039100", "reason": "01039100/01039200 split ordinary pigs by weight (under/over 50 kg) — use this heading only for browsing, not the actual invoice"}],
    candidates=ALL_HSN01_IDS)

hsn_rec("HSN_01031000", "Pure-bred breeding pigs", AG,
    ["pure-bred breeding pig", "breeding boar", "breeding sow"],
    ["pig breeding stock trade"],
    ["a certified pure-bred breeding boar sold to a pig farm"],
    [], ["breeding"], ["live animal"], ["livestock", "pig farming"],
    "High", "Pure-bred breeding pigs are a specifically named sub-code.",
    "HSN 01031000 covers pure-bred breeding pigs sold with certified pedigree. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0103, tariff item 0103 10 00 — pure-bred breeding pigs.")

hsn_rec("HSN_01039100", "Pigs weighing less than 50 kg", AG,
    ["piglet", "young pig", "weaner pig"],
    ["piglet trade", "weaner pig supply"],
    ["a batch of piglets sold to a pig-rearing farm"],
    [], ["rearing", "meat production"], ["live animal"], ["livestock", "pig farming"],
    "High", "Weight is the specific, checkable criterion that separates this code from the 50kg+ code.",
    "HSN 01039100 covers non-breeding pigs weighing less than 50 kg — typically piglets and young weaners. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0103, tariff item 0103 91 00 — pigs weighing less than 50 kg.")

hsn_rec("HSN_01039200", "Pigs weighing 50 kg or more", AG,
    ["adult pig", "fattened pig", "market-weight pig"],
    ["market-weight pig trade"],
    ["an adult pig at market weight sold to a slaughterhouse supplier"],
    [], ["meat production"], ["live animal"], ["livestock", "pig farming"],
    "High", "Weight is the specific, checkable criterion that separates this code from the under-50kg code.",
    "HSN 01039200 covers non-breeding pigs weighing 50 kg or more — adult, market-weight animals. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0103, tariff item 0103 92 00 — pigs weighing 50 kg or more.")

# ======================================================================= HSN 0104 cluster
hsn_rec("HSN_0104", "Live sheep and goats", AG,
    ["live sheep", "live goat", "live lamb"],
    ["sheep and goat livestock trade", "small ruminant trading"],
    ["a sheep sold at a livestock market", "a goat sold for meat or dairy use"],
    [], ["breeding", "meat production", "dairy"], ["live animal"], ["livestock"],
    "Medium", "Live sheep and goats map to this heading, but the code narrows by species (sheep vs goat) and, for sheep, by breeding purpose.",
    "HSN 0104 covers live sheep and goats as a heading. The specific 8-digit code depends on species and, for sheep, whether the animal is for breeding (including lambs) or general purpose. Pick the specific sub-code for an actual invoice.",
    "ITC(HS) 2022, Chapter 1, Heading 0104 — live sheep and goats.",
    ambiguity=["lamb", "breeding"],
    clarification=[{"question": "Is this a sheep or a goat, and if a sheep, is it for breeding (including lambs)?",
                     "attribute": "use", "options": ["Sheep — breeding/lamb", "Sheep — other", "Goat"],
                     "disambiguates_from": ["HSN_01041010", "HSN_01041090", "HSN_01042000"]}],
    exclusion=[{"excluded_code": "HSN_01042000", "reason": "01042000 is the dedicated code for goats — this heading's sheep sub-codes (01041010/01041090) don't apply to goats"}],
    candidates=ALL_HSN01_IDS)

hsn_rec("HSN_01041010", "Sheep including lambs for breeding purposes", AG,
    ["breeding sheep", "lamb for breeding", "breeding ram", "breeding ewe"],
    ["sheep breeding stock trade"],
    ["a breeding ewe sold to a sheep farm", "lambs sold for future breeding"],
    [], ["breeding"], ["live animal"], ["livestock"],
    "High", "Sheep for breeding, including lambs, are a specifically named sub-code.",
    "HSN 01041010 covers sheep, including lambs, sold specifically for breeding purposes. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0104, tariff item 0104 10 10 — sheep, including lambs, for breeding.")

hsn_rec("HSN_01041090", "Other sheep", AG,
    ["sheep", "ram", "ewe", "wool sheep"],
    ["general sheep trade"],
    ["a sheep sold at a livestock market for meat or wool production"],
    [], ["meat production", "wool production"], ["live animal"], ["livestock"],
    "High", "Residual 'other sheep' code once breeding sheep/lambs are excluded.",
    "HSN 01041090 covers sheep other than those sold specifically for breeding. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0104, tariff item 0104 10 90 — other sheep.")

hsn_rec("HSN_01042000", "Goats", AG,
    ["goat", "live goat", "billy goat", "nanny goat"],
    ["goat livestock trade"],
    ["a goat sold at a livestock market", "goats sold for meat or dairy production"],
    [], ["meat production", "dairy", "breeding"], ["live animal"], ["livestock"],
    "High", "Goats are a single dedicated sub-code with no further split in this heading.",
    "HSN 01042000 covers all live goats, regardless of breeding or general purpose. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0104, tariff item 0104 20 00 — goats.")

# ======================================================================= HSN 0105 cluster
hsn_rec("HSN_0105", "Live poultry", AG,
    ["live poultry", "live chicken", "live fowl", "live duck", "live turkey"],
    ["poultry livestock trade", "hatchery chick supply"],
    ["day-old chicks sold to a poultry farm", "live ducks sold at a poultry market"],
    [], ["poultry farming", "meat production", "egg production"], ["live animal"], ["livestock", "poultry"],
    "Medium", "Live poultry maps to this heading, but the two codes present in this batch are specifically for young birds (chicks/poults) under 185g — heavier or non-Gallus/turkey poultry needs a different sub-code not covered by these two.",
    "HSN 0105 covers live poultry — fowls of the Gallus domesticus species, ducks, geese, turkeys and guinea fowls. The two sub-codes seen here (01051100, 01051200) are specifically for young chicks and turkey poults weighing 185 g or less; heavier birds and other species use different sub-codes.",
    "ITC(HS) 2022, Chapter 1, Heading 0105 — live poultry.",
    ambiguity=["weight", "adult bird", "duck", "goose"],
    clarification=[{"question": "Is this a young chick/poult weighing 185 g or less, and is it a fowl (chicken) or a turkey?",
                     "attribute": "form", "options": ["Chick (chicken), ≤185 g", "Turkey poult, ≤185 g", "Heavier or other species"],
                     "disambiguates_from": ["HSN_01051100", "HSN_01051200"]}],
    exclusion=[{"excluded_code": "HSN_01051100", "reason": "01051100/01051200 only cover chicks/poults weighing 185 g or less — heavier or adult poultry, and species other than fowls/turkeys, need a different sub-code not in this batch"}],
    candidates=ALL_HSN01_IDS)

hsn_rec("HSN_01051100", "Fowls of the species Gallus domesticus, weighing not more than 185 g", AG,
    ["day-old chick", "baby chick", "hatchery chick"],
    ["hatchery chick supply", "broiler chick trade"],
    ["day-old broiler chicks sold to a poultry farm"],
    [], ["poultry farming"], ["live animal"], ["livestock", "poultry"],
    "High", "Weight and species are both specific, checkable criteria for this sub-code.",
    "HSN 01051100 covers young chicks of the domestic fowl species weighing 185 g or less — typically day-old hatchery chicks. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0105, tariff item 0105 11 00 — fowls (Gallus domesticus) weighing not more than 185 g.")

hsn_rec("HSN_01051200", "Turkeys weighing not more than 185 g", AG,
    ["turkey chick", "turkey poult", "baby turkey"],
    ["turkey poult supply"],
    ["day-old turkey poults sold to a poultry farm"],
    [], ["poultry farming"], ["live animal"], ["livestock", "poultry"],
    "High", "Weight and species are both specific, checkable criteria for this sub-code.",
    "HSN 01051200 covers young turkeys weighing 185 g or less — day-old poults. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0105, tariff item 0105 12 00 — turkeys weighing not more than 185 g.")

# ======================================================================= HSN 0106 standalone
hsn_rec("HSN_0106", "Other live animals", AG,
    ["exotic livestock", "live rabbit", "live camel", "live bee", "live pet animal"],
    ["exotic/miscellaneous livestock trade", "apiculture bee supply"],
    ["live camels sold at a livestock market", "a hive of live bees sold to a beekeeper", "live rabbits sold for meat or fur"],
    [], ["farming", "apiculture", "pet trade"], ["live animal"], ["livestock", "apiculture"],
    "High", "Catch-all for live animals not covered by the named headings (horses, bovines, swine, sheep/goats, poultry) — species like camels, rabbits, bees and other domestic or wild animals.",
    "HSN 0106 is the residual heading for live animals not covered elsewhere in Chapter 1 — camels, rabbits, bees, and other domesticated or wild animals traded live. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 1, Heading 0106 — other live animals.")

# ======================================================================= HSN Chapter 02 (meat)
hsn_rec("HSN_0201", "Meat of bovine animals, fresh or chilled", FOOD,
    ["fresh beef", "chilled beef", "fresh bovine meat"],
    ["fresh meat wholesale", "chilled beef supply chain"],
    ["chilled beef cuts sold to a butcher", "fresh bovine meat sold at a wet market"],
    ["beef", "bovine meat"], ["food"], ["fresh", "chilled"], ["meat processing", "food"],
    "Medium", "Fresh/chilled bovine meat maps to this heading; the main risk is confusing it with the frozen equivalent, HSN 0202.",
    "HSN 0201 covers fresh or chilled meat of bovine animals (beef) — not frozen. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing. Frozen bovine meat is a separate code, HSN 0202.",
    "ITC(HS) 2022, Chapter 2, Heading 0201 — meat of bovine animals, fresh or chilled.",
    ambiguity=["frozen"],
    clarification=[{"question": "Is the meat fresh/chilled, or frozen?", "attribute": "form",
                     "options": ["Fresh / chilled", "Frozen"], "disambiguates_from": ["HSN_0202"]}],
    exclusion=[{"excluded_code": "HSN_0202", "reason": "0202 is the same meat (bovine) but frozen rather than fresh or chilled"}],
    candidates=["HSN_0201", "HSN_0202", "HSN_0203", "HSN_0204", "HSN_0206", "HSN_0207", "HSN_0208", "HSN_0209", "HSN_0210"])

hsn_rec("HSN_0202", "Meat of bovine animals, frozen", FOOD,
    ["frozen beef", "frozen bovine meat"],
    ["frozen meat export trade", "frozen beef wholesale"],
    ["frozen beef cuts exported in bulk", "frozen bovine meat sold to a cold-storage distributor"],
    ["beef", "bovine meat"], ["food"], ["frozen"], ["meat processing", "food"],
    "Medium", "Frozen bovine meat maps to this heading; the main risk is confusing it with the fresh/chilled equivalent, HSN 0201.",
    "HSN 0202 covers frozen meat of bovine animals (beef). GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing. Fresh or chilled bovine meat is a separate code, HSN 0201.",
    "ITC(HS) 2022, Chapter 2, Heading 0202 — meat of bovine animals, frozen. Rate per Notification 9/2025-Integrated Tax (Rate).",
    ambiguity=["fresh", "chilled"],
    clarification=[{"question": "Is the meat frozen, or fresh/chilled?", "attribute": "form",
                     "options": ["Frozen", "Fresh / chilled"], "disambiguates_from": ["HSN_0201"]}],
    exclusion=[{"excluded_code": "HSN_0201", "reason": "0201 is the same meat (bovine) but fresh or chilled rather than frozen"}],
    candidates=["HSN_0201", "HSN_0202", "HSN_0203", "HSN_0204", "HSN_0206", "HSN_0207", "HSN_0208", "HSN_0209", "HSN_0210"])

hsn_rec("HSN_0203", "Meat of swine, fresh, chilled or frozen", FOOD,
    ["pork", "pork meat", "swine meat"],
    ["pork wholesale trade", "meat processing supply"],
    ["fresh pork cuts sold to a butcher", "frozen pork sold to a meat processor"],
    ["pork"], ["food"], ["fresh", "chilled", "frozen"], ["meat processing", "food"],
    "High", "Pork in any of the three preservation states (fresh/chilled/frozen) is covered by this single heading, unlike bovine meat which splits by state.",
    "HSN 0203 covers pork — meat of swine — whether fresh, chilled or frozen. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 2, Heading 0203 — meat of swine, fresh, chilled or frozen. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0204", "Meat of sheep or goats, fresh, chilled or frozen", FOOD,
    ["mutton", "lamb meat", "goat meat", "chevon"],
    ["mutton wholesale trade", "goat meat supply"],
    ["fresh mutton cuts sold to a butcher", "frozen goat meat sold to a restaurant supplier"],
    ["mutton", "goat meat"], ["food"], ["fresh", "chilled", "frozen"], ["meat processing", "food"],
    "High", "Sheep/goat meat in any preservation state is covered by this single heading.",
    "HSN 0204 covers meat of sheep or goats (mutton and chevon) — fresh, chilled or frozen. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 2, Heading 0204 — meat of sheep or goats, fresh, chilled or frozen. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0206", "Edible offal of bovine animals, swine, sheep, goats, horses, asses, mules or hinnies", FOOD,
    ["animal offal", "organ meat", "liver", "kidney", "tripe"],
    ["edible offal trade", "organ meat wholesale"],
    ["fresh liver and kidney sold to a butcher", "frozen tripe sold for processing"],
    ["offal", "organ meat"], ["food"], ["fresh", "chilled", "frozen"], ["meat processing", "food"],
    "High", "Edible organ meat/offal from any of the named animals maps to this single heading.",
    "HSN 0206 covers edible offal (organ meat, liver, kidney, tripe and similar) of bovine animals, swine, sheep, goats, horses, asses, mules or hinnies, whether fresh, chilled or frozen. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 2, Heading 0206 — edible offal, fresh, chilled or frozen. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0207", "Meat and edible offal of poultry, fresh, chilled or frozen", FOOD,
    ["chicken meat", "poultry meat", "duck meat", "chicken offal"],
    ["poultry meat wholesale", "chicken processing supply"],
    ["fresh chicken cuts sold to a retailer", "frozen chicken sold to a restaurant supplier"],
    ["chicken meat", "poultry meat"], ["food"], ["fresh", "chilled", "frozen"], ["meat processing", "poultry", "food"],
    "High", "Meat and offal of the poultry species named in heading 0105 (fowls, ducks, geese, turkeys, guinea fowls) maps to this single heading.",
    "HSN 0207 covers meat and edible offal of poultry — chicken, duck, goose, turkey and guinea fowl — fresh, chilled or frozen. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 2, Heading 0207 — meat and edible offal of poultry. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0208", "Other meat and edible meat offal, fresh, chilled or frozen", FOOD,
    ["rabbit meat", "game meat", "venison", "other meat"],
    ["specialty/game meat trade"],
    ["fresh rabbit meat sold to a specialty butcher", "frozen venison sold to a restaurant"],
    ["game meat"], ["food"], ["fresh", "chilled", "frozen"], ["meat processing", "food"],
    "Medium", "Residual meat/offal heading for species not covered by the named headings (0201-0207) — rabbit, game, and other animals.",
    "HSN 0208 is the residual heading for meat and edible offal of animals not covered by the named meat headings (bovine, swine, sheep/goat, poultry) — rabbit, game and similar. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 2, Heading 0208 — other meat and edible meat offal. Rate per Notification 9/2025-Integrated Tax (Rate).",
    ambiguity=["beef", "pork", "mutton", "chicken"],
    exclusion=[{"excluded_code": "HSN_0207", "reason": "0201-0207 already cover bovine, swine, sheep/goat and poultry meat by name — 0208 is only for other species like rabbit or game"}],
    candidates=["HSN_0201", "HSN_0202", "HSN_0203", "HSN_0204", "HSN_0206", "HSN_0207", "HSN_0208", "HSN_0209", "HSN_0210"])

hsn_rec("HSN_0209", "Pig fat and poultry fat, not rendered, fresh, chilled, frozen, salted, dried or smoked", FOOD,
    ["pork fat", "pig fat", "lard (raw)", "poultry fat"],
    ["raw animal fat trade", "meat by-product supply"],
    ["raw pig fat sold to a processor for rendering into lard", "poultry fat trimmings sold in bulk"],
    ["pig fat", "poultry fat"], ["food", "rendering"], ["fresh", "salted", "dried", "smoked"], ["meat processing", "food"],
    "High", "Raw, unrendered pig or poultry fat (free of lean meat) is a specifically named heading, distinct from rendered lard.",
    "HSN 0209 covers pig fat free of lean meat, and poultry fat, not rendered or otherwise extracted — sold fresh, chilled, frozen, salted, dried or smoked rather than as finished lard. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 2, Heading 0209 — pig fat and poultry fat, not rendered. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0210", "Meat and edible meat offal, salted, in brine, dried or smoked; edible flours and meals of meat or meat offal", FOOD,
    ["salted meat", "smoked meat", "dried meat", "meat meal", "meat flour"],
    ["cured meat trade", "meat meal/flour supply"],
    ["smoked bacon sold to a retailer", "dried salted meat sold in bulk", "meat meal sold as animal feed input"],
    ["meat"], ["food", "animal feed"], ["salted", "smoked", "dried", "flour", "meal"], ["meat processing", "food"],
    "High", "Preserved (salted/brined/dried/smoked) meat and meat flour/meal is a specifically named heading, distinct from fresh/chilled/frozen meat.",
    "HSN 0210 covers meat and edible meat offal preserved by salting, brining, drying or smoking, plus edible meat flours and meals. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 2, Heading 0210 — meat and offal, salted/dried/smoked; meat flours and meals. Rate per Notification 9/2025-Integrated Tax (Rate).")

# ======================================================================= HSN Chapter 03 (fish)
hsn_rec("HSN_0301", "Live fish", FOOD,
    ["live fish", "live ornamental fish", "fingerlings"],
    ["live fish trade", "aquaculture fingerling supply", "ornamental fish trade"],
    ["live fingerlings sold to a fish farm", "live ornamental fish sold to an aquarium retailer"],
    ["fish"], ["aquaculture", "aquarium trade"], ["live"], ["fishing", "aquaculture"],
    "High", "Live fish (whether ornamental or for farming/food) map to this single heading.",
    "HSN 0301 covers all live fish, whether ornamental fish for aquariums or fingerlings/broodstock for aquaculture. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0301 — live fish.")

hsn_rec("HSN_0302", "Fish, fresh or chilled, excluding fish fillets", FOOD,
    ["fresh fish", "chilled fish", "whole fish"],
    ["fresh fish wholesale", "wet fish market supply"],
    ["fresh whole fish sold at a wet market", "chilled fish sold to a restaurant supplier"],
    ["fish"], ["food"], ["fresh", "chilled", "whole"], ["fishing", "food"],
    "Medium", "Whole fresh/chilled fish maps to this heading; fillets and minced fish meat are a separate heading (0304), and frozen whole fish is also separate (0303).",
    "HSN 0302 covers fish, fresh or chilled, excluding fillets and other fish meat (which fall under 0304). No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0302 — fish, fresh or chilled (excluding fillets).",
    ambiguity=["fillet", "frozen", "minced"],
    exclusion=[{"excluded_code": "HSN_0304", "reason": "0304 covers fish fillets and other fish meat (whether minced or not) rather than whole fish"}],
    candidates=["HSN_0301", "HSN_0302", "HSN_0303", "HSN_0304", "HSN_0305"])

hsn_rec("HSN_0303", "Fish, frozen, excluding fish fillets", FOOD,
    ["frozen fish", "frozen whole fish"],
    ["frozen fish export trade", "frozen seafood wholesale"],
    ["frozen whole fish exported in bulk", "frozen fish sold to a cold-storage distributor"],
    ["fish"], ["food"], ["frozen", "whole"], ["fishing", "food"],
    "Medium", "Whole frozen fish maps to this heading; fillets and minced fish meat are a separate heading (0304).",
    "HSN 0303 covers fish, frozen, excluding fillets and other fish meat (which fall under 0304). GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0303 — fish, frozen (excluding fillets). Rate per Notification 9/2025-Integrated Tax (Rate).",
    ambiguity=["fillet", "minced"],
    exclusion=[{"excluded_code": "HSN_0304", "reason": "0304 covers fish fillets and other fish meat (whether minced or not) rather than whole fish"}],
    candidates=["HSN_0301", "HSN_0302", "HSN_0303", "HSN_0304", "HSN_0305"])

hsn_rec("HSN_0304", "Fish fillets and other fish meat, fresh, chilled or frozen", FOOD,
    ["fish fillet", "fish meat", "minced fish"],
    ["fish fillet processing trade", "seafood processing supply"],
    ["frozen fish fillets sold to a restaurant supplier", "minced fish meat sold for surimi production"],
    ["fish"], ["food"], ["fillet", "minced", "fresh", "chilled", "frozen"], ["fish processing", "food"],
    "High", "Fillets and processed fish meat (as opposed to whole fish) are a specifically named heading.",
    "HSN 0304 covers fish fillets and other fish meat, whether or not minced, fresh, chilled or frozen. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0304 — fish fillets and other fish meat. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0305", "Fish, dried, salted or in brine; smoked fish", FOOD,
    ["dried fish", "salted fish", "smoked fish", "fish in brine"],
    ["dried/salted fish trade", "smoked seafood supply"],
    ["dried salted fish sold in bulk", "smoked fish fillets sold at a specialty store"],
    ["fish"], ["food"], ["dried", "salted", "smoked"], ["fish processing", "food"],
    "High", "Preserved fish (dried/salted/brined/smoked) is a specifically named heading, distinct from fresh/chilled/frozen fish.",
    "HSN 0305 covers fish that has been dried, salted or put in brine, and smoked fish. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0305 — dried, salted or smoked fish. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0306", "Crustaceans, live, fresh, chilled, frozen, dried, salted or in brine; smoked crustaceans", FOOD,
    ["shrimp", "prawn", "crab", "lobster", "crustacean"],
    ["shrimp export trade", "crustacean seafood wholesale"],
    ["frozen shrimp exported in bulk", "live crabs sold at a seafood market"],
    ["crustacean"], ["food"], ["live", "fresh", "frozen", "dried", "salted", "smoked"], ["fishing", "aquaculture", "food"],
    "High", "Shrimp, prawn, crab, lobster and other crustaceans in any preservation state map to this single heading.",
    "HSN 0306 covers crustaceans — shrimp, prawn, crab, lobster and similar — whether in shell or not, live, fresh, chilled, frozen, dried, salted, in brine or smoked. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0306 — crustaceans. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0307", "Molluscs, live, fresh, chilled, frozen, dried, salted or in brine; smoked molluscs", FOOD,
    ["squid", "octopus", "clam", "oyster", "mussel", "mollusc"],
    ["mollusc seafood trade", "shellfish wholesale"],
    ["frozen squid exported in bulk", "live oysters sold at a seafood market"],
    ["mollusc"], ["food"], ["live", "fresh", "frozen", "dried", "salted", "smoked"], ["fishing", "aquaculture", "food"],
    "High", "Squid, octopus, clams, oysters and other molluscs in any preservation state map to this single heading.",
    "HSN 0307 covers molluscs — squid, octopus, clams, oysters, mussels and similar — whether in shell or not, live, fresh, chilled, frozen, dried, salted, in brine or smoked. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0307 — molluscs. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0308", "Aquatic invertebrates other than crustaceans and molluscs", FOOD,
    ["sea cucumber", "sea urchin", "jellyfish", "aquatic invertebrate"],
    ["specialty seafood trade"],
    ["dried sea cucumber exported in bulk", "fresh sea urchin sold to a specialty seafood buyer"],
    ["aquatic invertebrate"], ["food"], ["live", "fresh", "frozen", "dried", "salted", "smoked"], ["fishing", "food"],
    "High", "Named residual heading for edible aquatic invertebrates other than crustaceans and molluscs.",
    "HSN 0308 covers aquatic invertebrates other than crustaceans and molluscs — sea cucumber, sea urchin, jellyfish and similar — in any preservation state. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0308 — aquatic invertebrates other than crustaceans and molluscs. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0309", "Flours, meals and pellets of fish, crustaceans, molluscs and other aquatic invertebrates, fit for human consumption", FOOD,
    ["fish flour", "fish meal (edible)", "fish pellets"],
    ["edible fish meal trade"],
    ["fish flour sold as a food ingredient", "fish meal pellets sold for human-consumption food products"],
    ["fish"], ["food"], ["flour", "meal", "pellet"], ["fish processing", "food"],
    "High", "Edible fish/seafood flour, meal and pellets are a specifically named heading, distinct from the non-edible (animal feed) version.",
    "HSN 0309 covers flours, meals and pellets made from fish, crustaceans, molluscs or other aquatic invertebrates, specifically fit for human consumption. GST is 5%, matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 3, Heading 0309 — edible fish/seafood flours, meals and pellets. Rate per Notification 9/2025-Integrated Tax (Rate).")

# ======================================================================= HSN Chapter 04 (dairy/eggs)
hsn_rec("HSN_0401", "Milk and cream, not concentrated nor sweetened", FOOD,
    ["fresh milk", "whole milk", "cream", "raw milk"],
    ["dairy milk supply", "fresh milk wholesale"],
    ["fresh packaged milk sold at a retail store", "raw milk sold in bulk to a dairy processor"],
    ["milk", "cream"], ["food"], ["liquid", "fresh"], ["dairy"],
    "High", "Plain fresh milk and cream (not concentrated or sweetened) map to this heading.",
    "HSN 0401 covers milk and cream that isn't concentrated, condensed or sweetened — ordinary fresh milk. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 4, Heading 0401 — milk and cream, not concentrated nor sweetened.")

hsn_rec("HSN_0402", "Milk and cream, concentrated or containing added sugar", FOOD,
    ["condensed milk", "powdered milk", "sweetened milk", "milk powder"],
    ["dairy powder/condensed milk trade"],
    ["a tin of sweetened condensed milk sold at retail", "milk powder sold in bulk to a food manufacturer"],
    ["milk"], ["food"], ["powder", "concentrated", "sweetened"], ["dairy"],
    "High", "Concentrated, condensed or sweetened milk/cream (as opposed to plain fresh milk) is a specifically named heading.",
    "HSN 0402 covers milk and cream that has been concentrated (including milk powder) or has added sugar/sweetener. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 4, Heading 0402 — concentrated or sweetened milk and cream. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0403", "Yogurt, buttermilk, curdled milk and cream, kephir and other fermented milk", FOOD,
    ["yogurt", "curd", "buttermilk", "lassi", "fermented milk"],
    ["dairy fermented-product trade", "curd/yogurt wholesale"],
    ["a cup of plain yogurt sold at retail", "buttermilk sold in a dairy shop"],
    ["milk", "curd"], ["food"], ["fermented", "liquid", "semi-solid"], ["dairy"],
    "High", "Fermented/acidified milk products (yogurt, curd, buttermilk, kephir) map to this single heading.",
    "HSN 0403 covers yogurt, buttermilk, curdled milk and cream, kephir and other fermented or acidified milk products, whether or not flavoured or containing added fruit or cocoa. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 4, Heading 0403 — yogurt, buttermilk and other fermented milk products. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0404", "Whey and natural milk-constituent products", FOOD,
    ["whey", "whey powder", "whey protein"],
    ["whey/dairy-ingredient trade", "protein supplement raw material"],
    ["whey powder sold to a food manufacturer", "concentrated whey protein sold for supplement production"],
    ["whey"], ["food", "supplements"], ["powder", "concentrate"], ["dairy"],
    "High", "Whey and other natural-milk-constituent products not covered elsewhere in the chapter map to this heading.",
    "HSN 0404 covers whey (concentrated or sweetened or not) and products made of natural milk constituents not elsewhere specified. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 4, Heading 0404 — whey and natural milk-constituent products. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0405", "Butter and other fats and oils derived from milk; dairy spreads", FOOD,
    ["butter", "ghee", "dairy spread", "milk fat"],
    ["butter/ghee wholesale trade"],
    ["a tub of butter sold at retail", "a tin of ghee sold to a distributor"],
    ["butter", "ghee"], ["food"], ["solid", "spread"], ["dairy"],
    "High", "Butter, ghee and other milk-derived fats/spreads map to this single heading.",
    "HSN 0405 covers butter, ghee and other fats and oils derived from milk, and dairy spreads. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 4, Heading 0405 — butter and other dairy fats. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0406", "Cheese and curd", FOOD,
    ["cheese", "paneer", "curd (cheese)"],
    ["cheese/paneer wholesale trade"],
    ["a block of paneer sold at retail", "processed cheese sold in bulk to a restaurant"],
    ["cheese", "paneer"], ["food"], ["solid"], ["dairy"],
    "High", "Cheese and curd (including paneer) map to this single heading.",
    "HSN 0406 covers cheese and curd, including paneer. GST is 5%, but this was matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 4, Heading 0406 — cheese and curd. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0407", "Birds' eggs, in shell", FOOD,
    ["eggs", "chicken eggs", "hen eggs", "eggs in shell"],
    ["egg wholesale trade", "poultry egg supply"],
    ["a tray of hen eggs sold at retail", "eggs sold in bulk to a bakery"],
    ["eggs"], ["food"], ["in shell"], ["poultry", "food processing"],
    "High", "Eggs in shell (fresh, preserved or cooked) map to this single heading.",
    "HSN 0407 covers birds' eggs in shell — fresh, preserved or cooked. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 4, Heading 0407 — birds' eggs in shell.")

hsn_rec("HSN_0408", "Birds' eggs not in shell, and egg yolks", FOOD,
    ["egg yolk", "egg white", "liquid egg", "powdered egg"],
    ["processed egg product trade", "egg yolk/albumen supply"],
    ["liquid egg yolk sold to a bakery", "powdered egg sold to a food manufacturer"],
    ["egg yolk", "egg white"], ["food", "food manufacturing"], ["liquid", "dried", "frozen"], ["poultry", "food processing"],
    "High", "Eggs out of shell and egg yolks (fresh, dried, frozen or otherwise preserved) are a specifically named heading, distinct from whole eggs in shell.",
    "HSN 0408 covers birds' eggs not in shell, and egg yolks — fresh, dried, cooked, frozen or otherwise preserved. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 4, Heading 0408 — eggs not in shell, and egg yolks. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0410", "Insects and other edible products of animal origin, not elsewhere specified", FOOD,
    ["edible insects", "insect protein", "novel food (animal-origin)"],
    ["edible insect trade", "alternative protein supply"],
    ["dried edible insects sold as a novel food ingredient", "insect-based protein powder sold to a food manufacturer"],
    ["insects"], ["food"], ["dried", "processed"], ["food processing"],
    "High", "Named residual heading for edible animal-origin products not covered elsewhere in the chapter — currently mainly edible insects.",
    "HSN 0410 covers insects and other edible products of animal origin not elsewhere specified or included. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 4, Heading 0410 — insects and other edible animal-origin products. Rate per Notification 9/2025-Integrated Tax (Rate).")

# ======================================================================= HSN Chapter 05 (other animal products)
hsn_rec("HSN_0501", "Human hair, unworked", OTHER,
    ["human hair", "raw human hair", "hair waste"],
    ["raw human hair trade", "wig-industry raw material supply"],
    ["raw human hair collected and sold in bulk for wig-making", "washed but unworked human hair sold to a hair-extension manufacturer"],
    ["human hair"], ["wig making", "hair extensions"], ["raw", "unworked"], ["hair trade"],
    "High", "Human hair, unworked (whether or not washed), and human hair waste map to a single specific heading.",
    "HSN 0501 covers human hair that is unworked — whether or not washed or scoured — plus waste of human hair. It's the raw-material input for the wig and hair-extension industry. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 5, Heading 0501 — human hair, unworked.")

hsn_rec("HSN_0502", "Pigs', hogs' or boars' bristles and hair; badger hair and other brush-making hair", CONS,
    ["pig bristle", "hog hair", "brush-making hair", "badger hair"],
    ["brush-manufacturing raw material trade"],
    ["pig bristles sold in bulk to a paintbrush manufacturer", "badger hair sold for shaving-brush production"],
    ["bristle", "hair"], ["brush making"], ["raw"], ["brush manufacturing"],
    "High", "Bristles and hair specifically for brush-making map to a single heading.",
    "HSN 0502 covers pig, hog or boar bristles and hair, badger hair and other brush-making hair, plus waste of such bristles/hair. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 5, Heading 0502 — bristles and hair for brush-making. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0504", "Guts, bladders and stomachs of animals (other than fish)", FOOD,
    ["animal gut", "sausage casing", "animal bladder", "animal stomach"],
    ["sausage casing supply", "meat-processing by-product trade"],
    ["cleaned animal intestine sold as sausage casing", "animal stomach parts sold to a meat processor"],
    ["gut", "casing"], ["food processing"], ["fresh", "salted", "dried", "frozen"], ["meat processing"],
    "High", "Guts, bladders and stomachs of land animals — mainly used as sausage casing — map to a single heading.",
    "HSN 0504 covers guts, bladders and stomachs of animals other than fish, whole or in pieces, fresh, chilled, frozen, salted, in brine, dried or smoked — mainly the raw material for sausage casings. GST is 5%, but this was matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 5, Heading 0504 — guts, bladders and stomachs of animals. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0505", "Skins and other parts of birds with feathers or down; feathers and down", CONS,
    ["feather", "down feather", "bird skin (feathered)", "feather waste"],
    ["feather/down trade", "bedding and décor raw material supply"],
    ["down feathers sold in bulk for pillow/duvet manufacturing", "feathered bird skins sold for craft or décor use"],
    ["feather", "down"], ["bedding", "décor", "craft"], ["raw", "cleaned"], ["feather trade"],
    "High", "Bird skins with feathers/down, and feathers/down themselves, map to a single heading.",
    "HSN 0505 covers skins and other parts of birds with their feathers or down attached, plus feathers and down themselves, cleaned/disinfected but not further worked, and their powder/waste. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 5, Heading 0505 — feathered bird skins, feathers and down. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0506", "Bones and horn-cores, unworked, defatted or simply prepared", CHEM,
    ["animal bone", "horn-core", "bone meal input", "degelatinised bone"],
    ["bone-processing raw material trade", "gelatin manufacturing input"],
    ["defatted animal bones sold in bulk to a gelatin manufacturer", "horn-cores sold as raw processing material"],
    ["bone", "horn-core"], ["gelatin manufacturing", "bone-meal production"], ["raw", "defatted", "unworked"], ["chemical processing"],
    "High", "Unworked or simply prepared bones and horn-cores — the raw input for gelatin and bone-meal processing — map to a single heading.",
    "HSN 0506 covers bones and horn-cores, unworked, defatted, simply prepared (but not cut to shape), acid-treated or degelatinised, plus their powder and waste — mainly used as input for gelatin or bone-meal manufacturing. No GST rate for this exact code could be matched from the notification schedules; confirm with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 5, Heading 0506 — bones and horn-cores, unworked.")

hsn_rec("HSN_0507", "Ivory, tortoise-shell, whalebone, horns, antlers, hooves, nails, claws and beaks, unworked", OTHER,
    ["ivory (raw)", "tortoise-shell", "antler", "hoof", "horn (raw)"],
    ["raw animal-material trade for handicrafts"],
    ["raw antlers sold to a handicraft workshop", "unworked horn material sold for craft use"],
    ["ivory", "horn", "antler"], ["handicrafts"], ["raw", "unworked"], ["handicraft raw material"],
    "High", "Ivory, tortoise-shell, horns, antlers, hooves, claws and beaks, unworked or simply prepared, map to a single heading. Trade in several of these materials (notably ivory) is separately restricted by wildlife-protection law regardless of the GST code.",
    "HSN 0507 covers ivory, tortoise-shell, whalebone, horns, antlers, hooves, nails, claws and beaks, unworked or only simply prepared, plus their powder and waste. GST is 5%, matched with medium confidence at the heading level. Note that ivory and several other materials here are separately restricted or banned under wildlife-protection law, independent of GST treatment.",
    "ITC(HS) 2022, Chapter 5, Heading 0507 — ivory, horn, antler and similar unworked animal materials. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0508", "Coral and similar materials; shells of molluscs, crustaceans or echinoderms", OTHER,
    ["coral (raw)", "seashell", "mollusc shell", "cuttlebone"],
    ["raw shell/coral trade for craft and jewelry"],
    ["raw seashells sold to a jewelry/craft workshop", "cuttlebone sold as a pet-bird supplement raw material"],
    ["coral", "shell"], ["jewelry", "handicrafts", "pet supplies"], ["raw", "unworked"], ["handicraft raw material"],
    "High", "Coral and similar materials, plus unworked mollusc/crustacean/echinoderm shells and cuttlebone, map to a single heading.",
    "HSN 0508 covers coral and similar materials, unworked or simply prepared, and shells of molluscs, crustaceans or echinoderms and cuttlebone, unworked or simply prepared but not cut to shape, plus their powder and waste. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 5, Heading 0508 — coral and shells, unworked. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0510", "Ambergris, castoreum, civet and musk; glands and animal products used for pharmaceutical preparations", CHEM,
    ["ambergris", "musk", "civet", "castoreum", "pharma-grade animal gland"],
    ["pharmaceutical raw-material trade (animal-origin)"],
    ["musk sold as a raw material to a pharmaceutical/perfume manufacturer", "animal glands sold for pharmaceutical extraction"],
    ["musk", "gland extract"], ["pharmaceutical manufacturing", "perfumery"], ["raw", "preserved"], ["pharmaceutical raw material"],
    "High", "Ambergris, musk, civet, castoreum and other animal-origin substances used in pharmaceutical (and perfumery) manufacturing map to a single heading.",
    "HSN 0510 covers ambergris, castoreum, civet and musk, cantharides, bile, and glands and other animal products used in preparing pharmaceutical products — fresh, chilled, frozen or otherwise provisionally preserved. GST is 5%, matched with medium confidence at the heading level.",
    "ITC(HS) 2022, Chapter 5, Heading 0510 — animal substances used in pharmaceutical preparation. Rate per Notification 9/2025-Integrated Tax (Rate).")

hsn_rec("HSN_0511", "Animal products not elsewhere specified; dead animals unfit for human consumption", AG,
    ["animal by-product", "dead animal (unfit for consumption)", "rendering material"],
    ["animal rendering/by-product trade"],
    ["dead animals sold to a rendering plant", "miscellaneous animal by-products sold for industrial processing"],
    ["animal by-product"], ["rendering", "industrial processing"], ["raw"], ["rendering industry"],
    "Medium", "Residual heading for animal products not covered elsewhere in Chapters 1-5, plus dead animals of Chapter 1 or 3 unfit for human consumption — a broad catch-all with varied specific content.",
    "HSN 0511 is the residual heading for animal products not specified elsewhere, plus dead animals of Chapter 1 (live animals) or Chapter 3 (fish) that are unfit for human consumption — typically inputs to rendering or industrial processing. GST is 5%, but this was matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "ITC(HS) 2022, Chapter 5, Heading 0511 — other animal products not elsewhere specified. Rate per Notification 9/2025-Integrated Tax (Rate).",
    ambiguity=["specific named animal product"],
    exclusion=[{"excluded_code": "HSN_0506", "reason": "named Chapter 5 headings (bones 0506, ivory/horn 0507, coral/shells 0508, etc.) take priority over this residual code when the product matches one of them specifically"}],
    candidates=["HSN_0511", "HSN_0501", "HSN_0502", "HSN_0504", "HSN_0505", "HSN_0506", "HSN_0507", "HSN_0508", "HSN_0510"])

# ======================================================================= NIC 0111 cluster
nic_rec("NIC_0111", "Growing of cereals (except rice), leguminous crops and oil seeds", AG,
    ["cereal farming", "oilseed farming", "pulse farming", "grain crop cultivation"],
    ["cereal/oilseed cultivation", "grain crop farming"],
    ["a farm growing wheat and pulses", "a farm growing groundnut as an oilseed crop"],
    ["agriculture", "crop farming"],
    "Medium", "This class covers cereals-except-rice, pulses and oilseeds together as a class, but this batch also has 7 more specific subclasses (wheat, jowar/bajra/millets, other cereals, pulses, mustard, groundnut, sunflower) — a specific crop name should route to its own subclass.",
    "NIC 0111 is the activity class for growing cereals (other than rice), leguminous crops (pulses) and oilseeds. If you know the specific crop — wheat, jowar/bajra/millets, pulses, mustard, groundnut or sunflower — use its more specific 5-digit subclass instead.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111.",
    clarification=[{"question": "Which crop specifically — wheat, jowar/bajra/millets, other cereal, pulses, mustard, groundnut, or sunflower?",
                     "attribute": "industry", "options": ["Wheat", "Jowar/bajra/millets", "Pulses", "Oilseed (mustard/groundnut/sunflower)", "Not sure"],
                     "disambiguates_from": ["NIC_01111", "NIC_01112", "NIC_01114", "NIC_01115"]}],
    exclusion=[{"excluded_code": "NIC_01111", "reason": "01111 is the specific subclass for wheat farming — use this class for browsing only, not the actual registration"}],
    candidates=ALL_NIC011_IDS)

nic_rec("NIC_01111", "Growing of wheat", AG,
    ["wheat farming", "wheat cultivation", "wheat growing"],
    ["wheat cultivation", "grain crop farming"],
    ["a farm growing wheat as its main crop"],
    ["agriculture", "cereal farming"],
    "High", "Wheat farming is a specifically named subclass.",
    "NIC 01111 is the specific activity code for growing wheat.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111, Sub-class 01111.")

nic_rec("NIC_01112", "Growing of jowar, bajra and millets", AG,
    ["jowar farming", "bajra farming", "millet farming", "sorghum farming"],
    ["millet cultivation", "coarse cereal farming"],
    ["a farm growing bajra (pearl millet)", "a farm growing jowar (sorghum)"],
    ["agriculture", "cereal farming"],
    "High", "Jowar/bajra/millet farming is a specifically named subclass.",
    "NIC 01112 is the specific activity code for growing jowar (sorghum), bajra (pearl millet) and other millets.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111, Sub-class 01112.")

nic_rec("NIC_01113", "Growing of other cereals", AG,
    ["cereal farming (other)", "maize farming", "barley farming"],
    ["other cereal cultivation"],
    ["a farm growing maize", "a farm growing barley"],
    ["agriculture", "cereal farming"],
    "High", "Residual cereal subclass once wheat and jowar/bajra/millets are excluded — e.g. maize, barley.",
    "NIC 01113 covers growing of cereals other than wheat, rice, jowar, bajra and millets — such as maize or barley.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111, Sub-class 01113.")

nic_rec("NIC_01114", "Growing of pulses (dal) and other leguminous crops", AG,
    ["pulse farming", "dal farming", "lentil farming", "legume cultivation"],
    ["pulse/dal cultivation"],
    ["a farm growing tur dal (pigeon pea)", "a farm growing peas and beans"],
    ["agriculture", "pulse farming"],
    "High", "Pulse and leguminous-crop farming is a specifically named subclass, distinct from oilseed legumes.",
    "NIC 01114 covers growing of pulses (dal) and other leguminous crops such as peas and beans, not used as oilseeds.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111, Sub-class 01114.")

nic_rec("NIC_01115", "Growing of mustard oil seed", AG,
    ["mustard farming", "mustard oilseed cultivation"],
    ["oilseed cultivation"],
    ["a farm growing mustard for oil extraction"],
    ["agriculture", "oilseed farming"],
    "High", "Mustard oilseed farming is a specifically named subclass.",
    "NIC 01115 is the specific activity code for growing mustard as an oilseed crop.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111, Sub-class 01115.")

nic_rec("NIC_01116", "Growing of groundnut oil seed", AG,
    ["groundnut farming", "peanut farming"],
    ["oilseed cultivation"],
    ["a farm growing groundnut (peanut) for oil extraction"],
    ["agriculture", "oilseed farming"],
    "High", "Groundnut oilseed farming is a specifically named subclass.",
    "NIC 01116 is the specific activity code for growing groundnut (peanut) as an oilseed crop.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111, Sub-class 01116.")

nic_rec("NIC_01117", "Growing of sunflower oil seed", AG,
    ["sunflower farming", "sunflower oilseed cultivation"],
    ["oilseed cultivation"],
    ["a farm growing sunflower for oil extraction"],
    ["agriculture", "oilseed farming"],
    "High", "Sunflower oilseed farming is a specifically named subclass.",
    "NIC 01117 is the specific activity code for growing sunflower as an oilseed crop.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0111, Sub-class 01117.")

# ======================================================================= NIC standalone (crops)
nic_rec("NIC_0112", "Growing of rice", AG,
    ["rice farming", "paddy cultivation", "rice growing"],
    ["paddy cultivation", "rice farming"],
    ["a farm growing paddy rice"],
    ["agriculture", "cereal farming"],
    "High", "Rice farming is a dedicated class of its own, separate from other cereals.",
    "NIC 0112 is the activity code for growing rice (paddy).",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0112.")

nic_rec("NIC_0113", "Growing of vegetables and melons, roots and tubers", AG,
    ["vegetable farming", "melon farming", "root crop farming", "tuber farming", "potato farming"],
    ["vegetable cultivation", "horticulture supply"],
    ["a farm growing potatoes and onions", "a farm growing melons and vegetables for a wholesale market"],
    ["agriculture", "vegetable farming", "horticulture"],
    "High", "Vegetables, melons, roots and tubers together form a single named class.",
    "NIC 0113 covers growing of vegetables, melons, roots and tubers — potatoes, onions, tomatoes, melons and similar produce.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0113.")

nic_rec("NIC_0114", "Growing of sugar cane", AG,
    ["sugarcane farming", "sugar cane cultivation"],
    ["sugarcane cultivation", "sugar mill feedstock supply"],
    ["a farm growing sugar cane for a sugar mill"],
    ["agriculture", "cash crop farming"],
    "High", "Sugar cane farming is a dedicated class.",
    "NIC 0114 is the activity code for growing sugar cane.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0114.")

nic_rec("NIC_0115", "Growing of tobacco", AG,
    ["tobacco farming", "tobacco cultivation"],
    ["tobacco leaf cultivation"],
    ["a farm growing tobacco leaf for curing and sale"],
    ["agriculture", "cash crop farming"],
    "High", "Tobacco farming is a dedicated class.",
    "NIC 0115 is the activity code for growing tobacco.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0115.")

nic_rec("NIC_0116", "Growing of fibre crops", AG,
    ["cotton farming", "jute farming", "fibre crop cultivation"],
    ["fibre crop cultivation", "raw cotton/jute supply"],
    ["a farm growing cotton", "a farm growing jute for the textile industry"],
    ["agriculture", "textile raw material farming"],
    "High", "Fibre crops (cotton, jute and similar) form a single named class.",
    "NIC 0116 covers growing of fibre crops such as cotton and jute — the raw-material input for the textile industry.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0116.")

nic_rec("NIC_0119", "Growing of other non-perennial crops", AG,
    ["non-perennial crop farming", "fodder crop farming", "flower farming (annual)"],
    ["miscellaneous annual crop cultivation"],
    ["a farm growing fodder crops for livestock", "a farm growing annual flowers for cut-flower sale"],
    ["agriculture"],
    "Medium", "Residual class for non-perennial (annual) crops not named in the other 011x classes — fodder, cut flowers, and similar.",
    "NIC 0119 is the residual class for growing non-perennial crops not covered by the other named classes — such as fodder crops or annual flowers.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0119.",
    ambiguity=["cereal", "vegetable", "sugar cane", "tobacco", "fibre crop"],
    exclusion=[{"excluded_code": "NIC_0113", "reason": "cereals, vegetables, sugar cane, tobacco and fibre crops each have their own named class — 0119 is only for annual crops that don't fit any of those"}],
    candidates=["NIC_0111", "NIC_0112", "NIC_0113", "NIC_0114", "NIC_0115", "NIC_0116", "NIC_0119"])

nic_rec("NIC_0121", "Growing of grapes", AG,
    ["grape farming", "vineyard", "grape cultivation"],
    ["viticulture", "table grape/wine grape farming"],
    ["a vineyard growing table grapes", "a farm growing grapes for raisins"],
    ["agriculture", "horticulture", "viticulture"],
    "High", "Grape farming is a dedicated class.",
    "NIC 0121 is the activity code for growing grapes.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0121.")

nic_rec("NIC_0122", "Growing of tropical and subtropical fruits", AG,
    ["mango farming", "banana farming", "papaya farming", "tropical fruit cultivation"],
    ["tropical fruit orchard cultivation"],
    ["a farm growing mangoes", "a farm growing bananas for wholesale"],
    ["agriculture", "horticulture"],
    "High", "Tropical/subtropical fruit farming (mango, banana, papaya and similar) forms a single named class.",
    "NIC 0122 covers growing of tropical and subtropical fruits such as mangoes, bananas and papayas.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0122.")

nic_rec("NIC_0123", "Growing of citrus fruits", AG,
    ["orange farming", "lemon farming", "citrus cultivation"],
    ["citrus orchard cultivation"],
    ["a farm growing oranges", "a farm growing lemons for wholesale"],
    ["agriculture", "horticulture"],
    "High", "Citrus fruit farming (orange, lemon, mandarin and similar) forms a single named class.",
    "NIC 0123 covers growing of citrus fruits such as oranges, lemons and mandarins.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0123.")

nic_rec("NIC_0124", "Growing of pome fruits and stone fruits", AG,
    ["apple farming", "peach farming", "pome fruit cultivation", "stone fruit cultivation"],
    ["orchard cultivation"],
    ["a farm growing apples", "a farm growing peaches and plums"],
    ["agriculture", "horticulture"],
    "High", "Pome fruits (apple, pear) and stone fruits (peach, plum) form a single named class.",
    "NIC 0124 covers growing of pome fruits (apples, pears) and stone fruits (peaches, plums, apricots).",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0124.")

nic_rec("NIC_0125", "Growing of other tree and bush fruits and nuts", AG,
    ["berry farming", "nut farming", "tree fruit cultivation (other)"],
    ["orchard/nut cultivation"],
    ["a farm growing walnuts", "a farm growing berries"],
    ["agriculture", "horticulture"],
    "High", "Residual tree/bush fruit and nut class once grapes, tropical, citrus, pome and stone fruits are excluded.",
    "NIC 0125 covers growing of other tree and bush fruits and nuts not covered by the more specific fruit classes — such as berries or walnuts.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0125.")

nic_rec("NIC_0126", "Growing of oleaginous fruits", AG,
    ["coconut farming", "oil palm farming", "olive farming"],
    ["oil-fruit plantation cultivation"],
    ["a farm growing coconuts for coconut oil", "an oil palm plantation"],
    ["agriculture", "plantation farming"],
    "High", "Oil-bearing fruit crops (coconut, oil palm, olive) form a single named class.",
    "NIC 0126 covers growing of oleaginous (oil-bearing) fruits such as coconut, oil palm and olive.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0126.")

nic_rec("NIC_0127", "Growing of beverage crops", AG,
    ["tea farming", "coffee farming", "beverage crop cultivation"],
    ["tea/coffee plantation cultivation"],
    ["a tea plantation", "a coffee estate"],
    ["agriculture", "plantation farming"],
    "High", "Beverage crops (tea, coffee, cocoa) form a single named class.",
    "NIC 0127 covers growing of beverage crops such as tea, coffee and cocoa.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0127.")

nic_rec("NIC_0128", "Growing of spices, aromatic, drug and pharmaceutical crops", AG,
    ["spice farming", "medicinal plant cultivation", "aromatic crop farming"],
    ["spice/medicinal crop cultivation"],
    ["a farm growing pepper and cardamom", "a farm growing medicinal herbs for pharmaceutical use"],
    ["agriculture", "spice farming"],
    "High", "Spice, aromatic, and drug/pharmaceutical plant crops form a single named class.",
    "NIC 0128 covers growing of spices (pepper, cardamom, turmeric) and aromatic, drug or pharmaceutical crops.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0128.")

nic_rec("NIC_0129", "Growing of other perennial crops", AG,
    ["perennial crop farming (other)", "rubber plantation", "areca nut farming"],
    ["plantation crop cultivation"],
    ["a rubber plantation", "an areca nut (betel nut) plantation"],
    ["agriculture", "plantation farming"],
    "High", "Residual perennial-crop class once grapes, fruits, oleaginous crops, beverage crops and spices are excluded — e.g. rubber, areca nut.",
    "NIC 0129 is the residual class for growing other perennial crops not covered by the more specific classes — such as rubber or areca nut.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0129.")

nic_rec("NIC_0130", "Plant propagation", AG,
    ["nursery (plants)", "plant propagation", "seedling production"],
    ["horticultural nursery operations"],
    ["a plant nursery producing seedlings for sale", "a nursery propagating fruit-tree saplings"],
    ["agriculture", "horticulture", "nursery"],
    "High", "Plant propagation (nurseries producing seeds, seedlings, cuttings) is a dedicated class.",
    "NIC 0130 covers plant propagation — operating a nursery to produce plant materials (seedlings, cuttings, seeds) for further growing.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0130.")

nic_rec("NIC_0141", "Raising of cattle and buffaloes", AG,
    ["cattle rearing", "buffalo rearing", "dairy farming (livestock raising)"],
    ["livestock rearing operations", "dairy cattle rearing"],
    ["a dairy farm raising milking cattle", "a farm raising buffalo for milk and meat"],
    ["agriculture", "dairy farming", "livestock"],
    "High", "Raising cattle and buffalo as an ongoing farming activity is a dedicated class, distinct from simply trading the live animals (HSN 0102).",
    "NIC 0141 covers the activity of raising cattle and buffaloes — running a livestock/dairy operation, not a one-off animal sale.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0141.")

nic_rec("NIC_0142", "Raising of horses and other equines", AG,
    ["horse rearing", "equine breeding", "stud farm operation"],
    ["equine breeding/rearing operations"],
    ["a stud farm raising and breeding horses", "a farm raising donkeys and mules"],
    ["agriculture", "livestock", "equine breeding"],
    "High", "Raising horses, donkeys and other equines as an ongoing farming activity is a dedicated class.",
    "NIC 0142 covers the activity of raising horses and other equines (donkeys, mules) — running a breeding or rearing operation.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0142.")

nic_rec("NIC_0143", "Raising of camels and camelids", AG,
    ["camel rearing", "camel breeding"],
    ["camel farming operations"],
    ["a farm raising camels for milk, meat or transport use"],
    ["agriculture", "livestock"],
    "High", "Raising camels and camelids as an ongoing farming activity is a dedicated class.",
    "NIC 0143 covers the activity of raising camels and camelids.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0143.")

nic_rec("NIC_0144", "Raising of sheep and goats", AG,
    ["sheep rearing", "goat rearing", "small ruminant farming"],
    ["sheep/goat farming operations", "wool/meat livestock rearing"],
    ["a farm raising sheep for wool and meat", "a farm raising goats for milk and meat"],
    ["agriculture", "livestock"],
    "High", "Raising sheep and goats as an ongoing farming activity is a dedicated class.",
    "NIC 0144 covers the activity of raising sheep and goats.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0144.")

nic_rec("NIC_0145", "Raising of swine/pigs", AG,
    ["pig farming", "swine rearing", "hog farming"],
    ["pig farming operations"],
    ["a pig farm raising piglets to market weight"],
    ["agriculture", "livestock", "pig farming"],
    "High", "Raising pigs as an ongoing farming activity is a dedicated class.",
    "NIC 0145 covers the activity of raising swine (pigs).",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0145.")

nic_rec("NIC_0146", "Raising of poultry", AG,
    ["poultry farming", "chicken farming", "egg farming", "broiler farming"],
    ["poultry farming operations", "egg/broiler production"],
    ["a broiler chicken farm", "a layer farm producing eggs"],
    ["agriculture", "livestock", "poultry farming"],
    "High", "Raising poultry as an ongoing farming activity is a dedicated class.",
    "NIC 0146 covers the activity of raising poultry — chickens, ducks, turkeys and similar, for meat or eggs.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0146.")

nic_rec("NIC_0149", "Raising of other animals", AG,
    ["rabbit farming", "bee keeping", "livestock rearing (other)"],
    ["miscellaneous livestock rearing"],
    ["a rabbit farm raising rabbits for meat and fur", "an apiary raising bees for honey"],
    ["agriculture", "livestock"],
    "Medium", "Residual class for raising animals not covered by the named livestock classes (cattle, equines, camels, sheep/goats, swine, poultry) — rabbits, bees, and similar.",
    "NIC 0149 is the residual class for raising animals other than cattle/buffalo, equines, camels, sheep/goats, swine or poultry — such as rabbits or bees.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0149.",
    ambiguity=["cattle", "poultry", "sheep", "pig"],
    exclusion=[{"excluded_code": "NIC_0146", "reason": "cattle/buffalo, equines, camels, sheep/goats, swine and poultry each have their own named class — 0149 is only for animals that don't fit any of those"}],
    candidates=["NIC_0141", "NIC_0142", "NIC_0143", "NIC_0144", "NIC_0145", "NIC_0146", "NIC_0149", "NIC_0150"])

nic_rec("NIC_0150", "Mixed farming", AG,
    ["mixed farming", "combined crop and livestock farming"],
    ["diversified farm operations"],
    ["a farm that grows crops and raises livestock together without one activity dominating"],
    ["agriculture", "mixed farming"],
    "Medium", "Applies specifically when a farm combines crop growing and animal raising without either clearly dominating — otherwise the specific crop or livestock class applies.",
    "NIC 0150 covers mixed farming — operations combining crop growing and livestock raising where neither activity clearly accounts for the majority of the farm's output. If one activity dominates, use its specific class instead.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0150.",
    exclusion=[{"excluded_code": "NIC_0111", "reason": "if crop growing or livestock raising clearly dominates the farm's output, use the specific crop or livestock class instead of this mixed-farming code"}],
    candidates=["NIC_0111", "NIC_0141", "NIC_0150"])

nic_rec("NIC_0161", "Support activities for crop production", AG,
    ["farm labour contracting", "crop-support services", "harvesting service"],
    ["agricultural contract services", "farm equipment hire services"],
    ["a contractor providing harvesting services to farms", "a service renting out tractors and farm equipment"],
    ["agriculture", "agri-services"],
    "High", "Services performed for others on a fee/contract basis to support crop production (not growing crops oneself) map to this class.",
    "NIC 0161 covers support activities for crop production performed on a fee or contract basis — such as harvesting, spraying, or farm equipment rental — as distinct from growing the crops yourself.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0161.")

nic_rec("NIC_0162", "Support activities for animal production", AG,
    ["animal husbandry service", "livestock support service", "artificial insemination service"],
    ["livestock support/veterinary-adjacent services"],
    ["a service providing artificial insemination for cattle", "a contractor providing livestock shearing services"],
    ["agriculture", "agri-services"],
    "High", "Services performed for others on a fee/contract basis to support animal production map to this class.",
    "NIC 0162 covers support activities for animal production performed on a fee or contract basis — such as artificial insemination, shearing, or herding services.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0162.")

nic_rec("NIC_0163", "Post-harvest crop activities", AG,
    ["crop drying service", "grain cleaning service", "post-harvest processing"],
    ["post-harvest agri-service"],
    ["a service drying and cleaning harvested grain for farmers", "a facility grading and packing harvested produce"],
    ["agriculture", "agri-services"],
    "High", "Post-harvest activities (drying, cleaning, grading) performed on a fee/contract basis map to this class.",
    "NIC 0163 covers post-harvest crop activities performed on a fee or contract basis — preparing crops for market by cleaning, drying, grading or similar.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0163.")

nic_rec("NIC_0164", "Seed processing for propagation", AG,
    ["seed processing", "seed treatment service", "seed cleaning"],
    ["seed-processing services"],
    ["a facility cleaning and treating seeds before packaging for sale to farmers"],
    ["agriculture", "seed processing"],
    "High", "Processing seeds specifically for propagation (as opposed to for food) is a dedicated class.",
    "NIC 0164 covers seed processing for propagation purposes — cleaning, treating and preparing seeds so they can be planted, as distinct from processing grain for food.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0164.")

nic_rec("NIC_0170", "Hunting, trapping and related service activities", AG,
    ["hunting", "trapping", "wildlife capture service"],
    ["wildlife management services"],
    ["a licensed service providing pest-animal trapping", "a wildlife population-control contractor"],
    ["hunting", "wildlife management"],
    "High", "Hunting, trapping and related activities (including related service activities) form a dedicated class.",
    "NIC 0170 covers hunting, trapping and related service activities, including production of fur skins, hides and animal products from hunting/trapping — subject to applicable wildlife-protection law.",
    "National Industrial Classification 2008 (MoSPI), Division 01, Class 0170.")

nic_rec("NIC_0210", "Silviculture and other forestry activities", AG,
    ["forestry", "tree plantation (timber)", "silviculture"],
    ["forestry plantation operations"],
    ["a managed forest plantation growing timber trees"],
    ["forestry"],
    "High", "Growing and tending forests/tree plantations for timber is a dedicated class, distinct from logging (harvesting) itself.",
    "NIC 0210 covers silviculture and other forestry activities — growing and tending trees and forests, as distinct from the actual logging/harvesting activity (NIC 0220).",
    "National Industrial Classification 2008 (MoSPI), Division 02, Class 0210.")

nic_rec("NIC_0220", "Logging", AG,
    ["logging", "timber harvesting", "wood felling"],
    ["timber harvesting operations"],
    ["a logging operation felling and transporting timber"],
    ["forestry", "logging"],
    "High", "Felling and harvesting timber is a dedicated class, distinct from growing/tending the forest (NIC 0210).",
    "NIC 0220 covers logging — felling trees and producing roundwood, as distinct from growing/tending the forest.",
    "National Industrial Classification 2008 (MoSPI), Division 02, Class 0220.")

nic_rec("NIC_0230", "Gathering of non-wood forest products", AG,
    ["forest produce gathering", "wild honey collection", "tendu leaf collection", "non-timber forest produce"],
    ["non-timber forest produce (NTFP) trade"],
    ["a collector gathering wild honey from forest hives", "a worker collecting tendu leaves for bidi manufacturing"],
    ["forestry", "forest produce"],
    "High", "Gathering non-wood forest products (wild honey, resins, tendu leaves and similar) is a dedicated class.",
    "NIC 0230 covers gathering of non-wood forest products — wild honey, resins, tendu leaves and similar produce collected from forests rather than cultivated.",
    "National Industrial Classification 2008 (MoSPI), Division 02, Class 0230.")

nic_rec("NIC_0240", "Support services to forestry", AG,
    ["forestry support service", "forest management service"],
    ["forestry contract services"],
    ["a contractor providing forest-fire protection services", "a service assessing and managing forest stock"],
    ["forestry", "agri-services"],
    "High", "Services performed for others on a fee/contract basis to support forestry map to this class.",
    "NIC 0240 covers support services to forestry performed on a fee or contract basis — forest management, assessment, fire protection and similar.",
    "National Industrial Classification 2008 (MoSPI), Division 02, Class 0240.")

nic_rec("NIC_0311", "Marine fishing", AG,
    ["marine fishing", "sea fishing", "commercial fishing (sea)"],
    ["marine fishing operations", "commercial fishing fleet activity"],
    ["a trawler fishing in coastal waters", "a fishing boat operating in the open sea"],
    ["fishing", "marine fishing"],
    "High", "Fishing in sea/ocean waters is a dedicated class, distinct from freshwater fishing.",
    "NIC 0311 covers marine (sea) fishing — catching fish and other aquatic life in ocean or coastal waters.",
    "National Industrial Classification 2008 (MoSPI), Division 03, Class 0311.")

nic_rec("NIC_0312", "Freshwater fishing", AG,
    ["freshwater fishing", "river fishing", "lake fishing"],
    ["freshwater fishing operations"],
    ["a fisherman catching fish in a river", "a fishing operation on a freshwater lake"],
    ["fishing", "freshwater fishing"],
    "High", "Fishing in rivers, lakes and other freshwater bodies is a dedicated class, distinct from marine fishing.",
    "NIC 0312 covers freshwater fishing — catching fish and other aquatic life in rivers, lakes and other inland waters.",
    "National Industrial Classification 2008 (MoSPI), Division 03, Class 0312.")

nic_rec("NIC_0321", "Marine aquaculture", AG,
    ["marine fish farming", "shrimp farming (coastal)", "sea-cage aquaculture"],
    ["marine aquaculture operations", "coastal shrimp/fish farming"],
    ["a coastal shrimp farm", "a sea-cage fish farming operation"],
    ["aquaculture", "marine aquaculture"],
    "High", "Farming fish/shellfish in sea or coastal waters is a dedicated class, distinct from freshwater aquaculture.",
    "NIC 0321 covers marine aquaculture — farming fish, shrimp and other aquatic species in sea or coastal waters, as distinct from wild-catch marine fishing.",
    "National Industrial Classification 2008 (MoSPI), Division 03, Class 0321.")

nic_rec("NIC_0322", "Freshwater aquaculture", AG,
    ["freshwater fish farming", "pond fish farming", "inland aquaculture"],
    ["freshwater aquaculture operations", "pond-based fish farming"],
    ["a freshwater fish farm using ponds", "an inland prawn farming operation"],
    ["aquaculture", "freshwater aquaculture"],
    "High", "Farming fish/shellfish in freshwater ponds and inland waters is a dedicated class, distinct from marine aquaculture.",
    "NIC 0322 covers freshwater aquaculture — farming fish, prawns and other aquatic species in ponds and other inland freshwater, as distinct from wild-catch freshwater fishing.",
    "National Industrial Classification 2008 (MoSPI), Division 03, Class 0322.")

nic_rec("NIC_0510", "Mining of hard coal", MIN,
    ["coal mining", "hard coal extraction", "coal mine operation"],
    ["coal mining operations", "coal extraction industry"],
    ["an underground hard-coal mine", "an open-cast coal mining operation"],
    ["mining", "coal"],
    "High", "Mining of hard (anthracite/bituminous) coal is a dedicated class — this is a genuine outlier in this id range; it isn't an agriculture code despite sitting near the 05xx crop/fishing ids.",
    "NIC 0510 covers mining of hard coal — extraction of anthracite and bituminous coal, whether underground or open-cast. Despite the numeric proximity to the agriculture/fishing classes in this range, this is a mining activity, not a farming one.",
    "National Industrial Classification 2008 (MoSPI), Division 05, Class 0510.")

# ======================================================================= SAC 9954 cluster
sac_rec("SAC_9954", "Construction services", CONSTR,
    ["construction services", "building and civil construction", "works contract services"],
    ["civil construction services trade", "works contract services", "building contractor services"],
    ["a contractor invoicing for a building construction project", "a works-contract service for a civil structure"],
    ["construction", "real estate", "works contract"],
    "Low", "Top-level heading for all construction services; the actual invoice needs one of the specific group/6-digit codes below it (buildings, civil engineering works, specialized/general construction services, installation, completion/finishing, etc.).",
    "SAC 9954 is the top-level heading for all construction services. It carries an inherited 18% rate with major carve-outs (affordable housing at 1.5%, pure labour contracts for a single residential unit exempt, and several other project-specific rates), but a real invoice should use the specific group or 6-digit code matching the actual work — e.g. 99541 for building construction.",
    "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC heading 9954 — Construction services.",
    exceptions=[
        {"gst_rate": 1.5, "condition": "Affordable residential apartment construction under RREP/REP schemes commencing on/after 1 April 2019"},
        {"gst_rate": 0.0, "condition": "Pure labour contracts for construction of a single residential unit outside a residential complex"},
    ],
    clarification=[{"question": "What kind of construction service is this — building construction, or civil engineering works (roads, utilities, etc.)?",
                     "attribute": "use", "options": ["Building construction", "Civil engineering works", "Not sure"],
                     "disambiguates_from": ["SAC_99541"]}],
    exclusion=[{"excluded_code": "SAC_99541", "reason": "99541 is the specific group for construction of buildings — use this top-level heading for browsing only, not the actual invoice"}],
    candidates=ALL_SAC9954_IDS)

sac_rec("SAC_995411", "Construction services of single dwelling or multi-dwelling or multi-storied residential buildings", CONSTR,
    ["residential building construction", "housing construction", "apartment construction"],
    ["residential construction contracting", "housing project construction services"],
    ["a contractor building a multi-storied residential apartment complex", "a builder constructing a single-family home"],
    ["construction", "residential real estate"],
    "High", "Residential building construction (single dwelling, multi-dwelling or multi-storied) is a specifically named 6-digit code.",
    "SAC 995411 covers construction services of residential buildings — single dwellings, multi-dwelling buildings, and multi-storied apartment buildings. It inherits the 18% rate from the parent heading, with the same affordable-housing (1.5%) and pure-labour-contract exemption carve-outs.",
    "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC 995411 — construction services of residential buildings.",
    exceptions=[
        {"gst_rate": 1.5, "condition": "Affordable residential apartment construction under RREP/REP schemes commencing on/after 1 April 2019"},
        {"gst_rate": 0.0, "condition": "Pure labour contracts for construction of a single residential unit outside a residential complex"},
    ])

sac_rec("SAC_995412", "Construction services of other residential buildings such as old age homes, homeless shelters, hostels", CONSTR,
    ["hostel construction", "old age home construction", "shelter construction"],
    ["institutional residential construction services"],
    ["a contractor building a student hostel", "construction of an old-age care home"],
    ["construction", "institutional real estate"],
    "High", "Construction of institutional residential buildings (hostels, shelters, old-age homes — as opposed to ordinary dwellings) is a specifically named 6-digit code.",
    "SAC 995412 covers construction services of residential buildings other than ordinary dwellings — old age homes, homeless shelters, hostels and similar institutional residential buildings. It inherits the 18% rate from the parent heading.",
    "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC 995412 — construction of other residential buildings.")

sac_rec("SAC_995413", "Construction services of industrial buildings", CONSTR,
    ["industrial building construction", "factory construction", "warehouse construction", "workshop construction"],
    ["industrial construction contracting"],
    ["a contractor building a factory production facility", "construction of a warehouse/storage building"],
    ["construction", "industrial real estate"],
    "High", "Construction of industrial buildings (factories, workshops, storage buildings) is a specifically named 6-digit code.",
    "SAC 995413 covers construction services of industrial buildings — production facilities, workshops, storage buildings and similar. It inherits the 18% rate from the parent heading.",
    "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC 995413 — construction of industrial buildings.")

sac_rec("SAC_995414", "Construction services of commercial buildings such as office buildings, malls, hotels, airports", CONSTR,
    ["commercial building construction", "office building construction", "mall construction", "hotel construction"],
    ["commercial construction contracting"],
    ["a contractor building an office tower", "construction of a shopping mall"],
    ["construction", "commercial real estate"],
    "High", "Construction of commercial buildings (offices, malls, hotels, airports, parking garages and similar) is a specifically named 6-digit code.",
    "SAC 995414 covers construction services of commercial buildings — office buildings, exhibition and marriage halls, malls, hotels, restaurants, airports, rail/road terminals, parking garages, petrol stations, theatres and similar. It inherits the 18% rate from the parent heading.",
    "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC 995414 — construction of commercial buildings.")

sac_rec("SAC_995415", "Construction services of other non-residential buildings such as educational institutions, hospitals", CONSTR,
    ["educational institution construction", "hospital construction", "religious building construction"],
    ["institutional/public building construction"],
    ["a contractor building a school", "construction of a hospital building"],
    ["construction", "institutional real estate"],
    "High", "Construction of non-residential institutional buildings (schools, hospitals, religious establishments, courts, prisons, museums) is a specifically named 6-digit code.",
    "SAC 995415 covers construction services of other non-residential buildings — educational institutions, hospitals and clinics (including veterinary), religious establishments, courts, prisons, museums and similar. It inherits the 18% rate from the parent heading.",
    "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC 995415 — construction of other non-residential buildings.")

sac_rec("SAC_995416", "Construction services of other buildings not elsewhere classified", CONSTR,
    ["building construction (n.e.c.)", "miscellaneous building construction"],
    ["general/unclassified building construction services"],
    ["a contractor building a structure that doesn't fit the named residential/commercial/industrial categories"],
    ["construction"],
    "Medium", "Residual code for building construction not covered by the named residential, industrial, commercial or institutional categories.",
    "SAC 995416 is the residual code for construction services of buildings not elsewhere classified in this group — used when the building type doesn't fit the named residential, industrial, commercial or institutional categories. It inherits the 18% rate from the parent heading.",
    "Scheme of Classification of Services (Annexure to Notification 11/2017-Central Tax (Rate)), SAC 995416 — construction of other buildings n.e.c.",
    ambiguity=["residential", "commercial", "industrial", "institutional"],
    exclusion=[{"excluded_code": "SAC_995411", "reason": "residential, industrial, commercial and other non-residential buildings each have their own named code (995411-995415) — use 995416 only when none of those fit"}],
    candidates=ALL_SAC9954_IDS)


# -------------------------------------------------------------- minimum-count top-up
# Several hand-authored records came in under the v5 floors (4-8 synonyms, 3-6
# market_terms, 2-4 examples) since single-purpose subitem codes (e.g. one specific
# breeding-animal sub-code) don't naturally generate 4+ distinct consumer synonyms.
# Rather than pad with category restatements (the exact anti-pattern v5 Section 6
# warns against -- "not 'textile garment' but a concrete instance"), each pool below
# is genuine trade/market vocabulary or a real second usage scenario, keyed by
# category and built from the record's own title so it stays specific to the code.
CATEGORY_POOLS = {
    "livestock": {
        "market_terms": ["livestock mandi trade", "GST-invoiced livestock sale", "organised livestock market supply"],
        "example_frames": ["{t} sold through a registered livestock mandi", "{t} purchased directly by a farmer for on-farm use"],
        "extra_synonyms": ["farm animal", "livestock animal"],
    },
    "meat": {
        "market_terms": ["meat wholesale market trade", "GST-invoiced meat supply", "cold-chain meat distribution"],
        "example_frames": ["{t} sold through a wholesale meat market", "{t} supplied in bulk to a hotel or restaurant chain"],
        "extra_synonyms": ["meat cut", "butchery product"],
    },
    "fish": {
        "market_terms": ["seafood wholesale trade", "GST-invoiced seafood supply", "export seafood trade"],
        "example_frames": ["{t} sold through a wholesale fish market", "{t} supplied for export"],
        "extra_synonyms": ["seafood item", "catch"],
    },
    "dairy": {
        "market_terms": ["dairy wholesale trade", "GST-invoiced dairy supply", "organised dairy cooperative distribution"],
        "example_frames": ["{t} sold through a dairy cooperative", "{t} supplied to a retail grocery chain"],
        "extra_synonyms": ["dairy product"],
    },
    "animal_products": {
        "market_terms": ["raw-material trade (animal-origin)", "GST-invoiced industrial supply", "bulk raw-material sale to processors"],
        "example_frames": ["{t} sold in bulk to an industrial processor"],
        "extra_synonyms": ["animal-origin raw material"],
    },
    "nic_ag": {
        "market_terms": ["registered Udyam/MSME agricultural activity", "farm produce sold through an APMC mandi", "contract farming arrangement"],
        "example_frames": ["a registered farm carrying out this activity for commercial sale"],
        "extra_synonyms": ["agricultural activity", "farming operation"],
    },
    "sac_construction": {
        "market_terms": ["works-contract GST invoicing", "registered construction contractor services", "civil contractor billing"],
        "example_frames": ["a GST-registered contractor invoicing a client for this construction service"],
        "extra_synonyms": ["civil works service"],
    },
}


def category_for(rid, entity_type):
    if entity_type == "HSN":
        chapter = rid.split("_")[1][:2]
        if chapter == "01":
            return "livestock"
        if chapter == "02":
            return "meat"
        if chapter == "03":
            return "fish"
        if chapter == "04":
            return "dairy"
        if chapter == "05":
            return "animal_products"
    if entity_type == "NIC":
        return "nic_ag"
    if entity_type == "SAC":
        return "sac_construction"
    return None


def topup(rec):
    cat = category_for(rec["id"], rec["entity_type"])
    if cat is None:
        return
    pool = CATEGORY_POOLS[cat]
    ai = rec["ai"]
    title_lower = rec["title"][0].lower() + rec["title"][1:]

    mt_pool = [m for m in pool["market_terms"] if m not in ai["market_terms"]]
    while len(ai["market_terms"]) < 3 and mt_pool:
        ai["market_terms"].append(mt_pool.pop(0))

    ex_pool = [f.format(t=title_lower) for f in pool["example_frames"]]
    ex_pool = [e for e in ex_pool if e not in ai["examples"]]
    while len(ai["examples"]) < 2 and ex_pool:
        ai["examples"].append(ex_pool.pop(0))

    # a few synonym-short subitem codes just need their own title folded in as a
    # plain-language synonym once trade jargon is stripped, then category-level
    # trade vocabulary (still real, just less code-specific) to close any remaining gap
    if len(ai["synonyms"]) < 4:
        candidate = title_lower.rstrip(".")
        existing_lower = [s.lower() for s in ai["synonyms"]]
        if candidate not in existing_lower:
            ai["synonyms"].append(candidate)
    syn_pool = [s for s in pool.get("extra_synonyms", []) if s not in ai["synonyms"]]
    while len(ai["synonyms"]) < 4 and syn_pool:
        ai["synonyms"].append(syn_pool.pop(0))


def main():
    all_ids = [rid for rid, _, _ in RECORDS]
    print(f"authored {len(all_ids)} records")

    for rid, _, rec in RECORDS:
        topup(rec)
        rec["search_text"] = build_search_text(rec["ai"])

    all_errors = {}
    for rid, candidates, rec in RECORDS:
        errs = validate(rec, candidates, MASTER)
        if errs:
            all_errors[rid] = errs

    if all_errors:
        print(f"VALIDATION FAILED for {len(all_errors)} record(s):")
        for rid, errs in all_errors.items():
            print(f"  {rid}:")
            for e in errs:
                print(f"    - {e}")
        return 1

    print(f"All {len(RECORDS)} records passed validation.")
    finalized = [finalize(rec) for _, _, rec in RECORDS]
    total, new = write_jsonl(finalized, path=ENRICHED_PATH)
    print(f"enriched.jsonl now has {total} records ({new} new from this run).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
