"""
Hand-authored Wave 1 enrichment content (enrichment_prompt_v3.md Section 11).
The classification-expert role (normally an LLM call) is filled in by this
session directly; enrichment_harness.py supplies the mechanical parts
(rate lookup, history building, search_text, validation, checksumming).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import (
    load_master, build_history, build_search_text, validate, finalize, write_jsonl
)

MASTER = load_master()

CH63_HEADINGS = ["HSN_6301", "HSN_6302", "HSN_6303", "HSN_6304", "HSN_6305", "HSN_6306", "HSN_6307", "HSN_6310"]
CH33_HEADINGS = ["HSN_3301", "HSN_3302", "HSN_3303", "HSN_3304", "HSN_3305", "HSN_3306", "HSN_3307"]
MASK_CANDIDATES = CH63_HEADINGS + CH33_HEADINGS + ["HSN_63079091", "HSN_90200000", "HSN_33049990"]

WATER_CANDIDATES = ["HSN_2201", "HSN_2202"]

ACCOUNTING_CANDIDATES = [
    "SAC_998211", "SAC_998212", "SAC_998213", "SAC_998214", "SAC_998215", "SAC_998216",
    "SAC_998221", "SAC_998222", "SAC_998223", "SAC_998224", "SAC_998231", "SAC_998232", "SAC_998240",
]

CH19_HEADINGS = ["HSN_1901", "HSN_1902", "HSN_1903", "HSN_1904", "HSN_1905"]
CH20_HEADINGS = ["HSN_2001", "HSN_2002", "HSN_2003", "HSN_2004", "HSN_2005", "HSN_2007", "HSN_2008", "HSN_2009"]
CH21_HEADINGS = ["HSN_2101", "HSN_2102", "HSN_2103", "HSN_2104", "HSN_2106"]
NAMKEEN_CANDIDATES = (
    CH19_HEADINGS + CH20_HEADINGS + CH21_HEADINGS
    + ["HSN_21069020", "HSN_21069099", "HSN_2201", "HSN_2202"]
)

UNRESOLVED_CAVEAT = "No GST rate could be matched to this code from the notification schedules. Consult a tax professional."
LOW_CONF_CAVEAT = "This rate was matched with low confidence at the heading level — verify against Notification 9/2025 before invoicing."

RECORDS = []  # list of (id, candidates, title, ai_dict, enrichment_status, rate_overrides)


def add(mid, candidates, title, ai, status="complete", exceptions=None, caveat=None):
    RECORDS.append((mid, candidates, title, ai, status, exceptions or [], caveat))


def build_record(mid, candidates, title, ai, status, exceptions, caveat):
    m = MASTER[mid]
    tax = m["tax"]
    meta = m.get("metadata", {})
    conf = meta.get("rate_confidence") or "unresolved"
    if caveat is None:
        if conf == "unresolved":
            caveat = UNRESOLVED_CAVEAT
        elif meta.get("rate_scope") == "chapter" or conf == "low":
            caveat = LOW_CONF_CAVEAT
    rate = {
        "gst_rate": tax.get("gst_rate"),
        "cess": tax.get("cess"),
        "effective_from": tax.get("effective_from"),
        "notification_no": tax.get("notification_no"),
        "rate_confidence": conf,
        "rate_scope": meta.get("rate_scope"),
        "rate_caveat": caveat,
        "exceptions": exceptions,
        "history": build_history(meta.get("superseded_rates")),
    }
    rec = {
        "id": mid,
        "code": m["code"],
        "entity_type": m["entity_type"],
        "title": title,
        "rate": rate,
        "ai": ai,
        "search_text": build_search_text(ai),
        "enrichment_status": status,
        "ai_checksum": "PENDING_CHECKSUM",
    }
    return rec, candidates


# =====================================================================
# WATER CLUSTER (HSN_2201, HSN_2202) — High confidence demo
# =====================================================================

add(
    "HSN_2201", WATER_CANDIDATES,
    "Mineral and aerated waters, not containing added sugar or flavoured; ice and snow",
    {
        "synonyms": ["packaged drinking water", "mineral water", "bottled water", "soda water", "club soda", "plain soda", "ice cubes"],
        "market_terms": ["PET bottled water", "20 litre water jar", "mineral water brand", "soda bottling"],
        "hindi_transliterated": ["pani ki bottle", "soda"],
        "examples": ["1 litre sealed bottle of packaged drinking water", "20-litre water jar for office cooler", "plain soda water bottle sold at a kirana store"],
        "attributes": {
            "material": ["water", "natural mineral water"],
            "use": ["drinking", "refilling water dispensers"],
            "form": ["bottled", "packaged", "jar"],
            "industry": ["beverages", "packaged water", "fmcg"],
        },
        "clarification_questions": [
            {"question": "Does the water have added sugar or flavouring?", "attribute": "form",
             "options": ["No, plain/unflavoured", "Yes, sweetened or flavoured"], "disambiguates_from": ["HSN_2202"]},
        ],
        "exclusion_notes": [
            {"excluded_code": "HSN_2202", "reason": "2202 covers water with added sugar, flavouring, or other non-alcoholic beverages — 2201 is only for plain or naturally mineral water"},
        ],
        "classification_confidence": {
            "level": "High",
            "rationale": "Plain bottled or mineral water maps uniquely to 2201; the only real fork is whether sugar or flavour has been added.",
            "ambiguity_triggers": ["flavoured water", "sweetened", "soft drink", "cola"],
        },
        "plain_rationale": "HSN 2201 covers plain drinking water and natural or artificial mineral water sold in bottles, jars, or cans, along with ice and snow — with no added sugar or flavouring. If you package or sell plain packaged drinking water, mineral water, or soda water, this is your code and GST is a flat 5%. The moment sugar or flavour (like a cola or fruit-flavoured drink) is added, the product moves to HSN 2202 instead, which carries a much higher rate, so keep plain and flavoured stock billed separately.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 22, Heading 2201 — waters, not containing added sugar or flavoured. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2202", WATER_CANDIDATES,
    "Waters, including mineral and aerated waters, containing added sugar or flavouring, and other non-alcoholic beverages",
    {
        "synonyms": ["soft drink", "cold drink", "aerated water", "flavoured water", "carbonated soft drink", "fizzy drink"],
        "market_terms": ["aerated beverage", "carbonated soft drink (CSD)", "flavoured beverage", "bottled soft drink"],
        "hindi_transliterated": ["thanda"],
        "examples": ["chilled cola bottle sold at a shop", "flavoured soda can", "fruit-flavoured aerated drink"],
        "attributes": {
            "material": ["carbonated water", "added sugar", "flavouring"],
            "use": ["drinking", "refreshment"],
            "form": ["bottled", "canned"],
            "industry": ["beverages", "fmcg"],
        },
        "clarification_questions": [],
        "exclusion_notes": [
            {"excluded_code": "HSN_2201", "reason": "2201 is for plain or unflavoured mineral/aerated water with no added sugar — use 2202 only once sugar or flavour is added"},
        ],
        "classification_confidence": {
            "level": "High",
            "rationale": "Sweetened or flavoured aerated drinks map uniquely to 2202 once sugar/flavour is confirmed present.",
            "ambiguity_triggers": ["plain water", "unflavoured", "mineral water only"],
        },
        "plain_rationale": "HSN 2202 covers water and other beverages with added sugar, sweetener, or flavour — this includes carbonated soft drinks, colas, and flavoured aerated water, but excludes fruit and vegetable juices, which fall under heading 2009. The GST rate here is a flat 40%, much higher than the 5% on plain bottled water under 2201, so billing the two under the same code is a common and costly MSME mistake.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 22, Heading 2202 — waters and other non-alcoholic beverages containing added sugar or flavouring. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

# =====================================================================
# ACCOUNTING SERVICES CLUSTER (SAC 998221-998224) — High confidence demo
# =====================================================================

_ARBITRAL_EXC = [{"gst_rate": 0.0, "condition": "Services by an arbitral tribunal to a non-business or small-turnover recipient: exempt"}]

add(
    "SAC_998222", ACCOUNTING_CANDIDATES,
    "Accounting and bookkeeping services",
    {
        "synonyms": ["accounting services", "bookkeeping", "book-keeping services", "accounts maintenance", "financial accounting"],
        "market_terms": ["accounting outsourcing", "monthly accounts", "Tally services", "books writing", "ledger maintenance"],
        "hindi_transliterated": ["hisab kitab", "khata lekhan"],
        "examples": ["maintaining purchase and sales ledgers for a trading firm", "preparing monthly profit and loss statements for a shop", "writing day-books and ledgers on Tally for a small manufacturer"],
        "attributes": {
            "material": [],
            "use": ["financial reporting", "statutory compliance"],
            "form": ["professional service", "outsourced service"],
            "industry": ["accounting", "professional services", "finance"],
        },
        "clarification_questions": [],
        "exclusion_notes": [
            {"excluded_code": "SAC_998221", "reason": "998221 is financial auditing (independently verifying the books) — 998222 is for preparing and maintaining the books, not auditing them"},
            {"excluded_code": "SAC_998231", "reason": "998231 is corporate tax consulting/return filing — use 998222 only for the underlying bookkeeping work, not tax advisory"},
        ],
        "classification_confidence": {
            "level": "High",
            "rationale": "Accounting and bookkeeping is a well-defined, singly-mapped service; the risk is conflating it with auditing or tax filing, both billed separately.",
            "ambiguity_triggers": ["audit", "statutory audit", "GST return filing", "tax planning"],
        },
        "plain_rationale": "SAC 998222 covers financial accounting and bookkeeping — maintaining a business's day-books, ledgers and financial records. If you provide or buy plain accounting or bookkeeping services, this is the code, and GST is 18%. It does not cover auditing those books (that's 998221) or tax return preparation and planning (that's under the 99823 tax-consultancy group) — bill those separately even if the same firm provides all three.",
        "regulatory_citation": "Scheme of Classification of Services, annexure to Notification 11/2017-Central Tax (Rate), SAC 998222 (Accounting and bookkeeping services), heading 9982, w.e.f. 01-07-2017.",
    },
    exceptions=_ARBITRAL_EXC,
)

add(
    "SAC_998221", ACCOUNTING_CANDIDATES,
    "Financial auditing services",
    {
        "synonyms": ["financial audit", "statutory audit", "auditing services", "account auditing", "tax audit"],
        "market_terms": ["statutory audit engagement", "independent financial audit", "CA audit services", "annual audit"],
        "hindi_transliterated": ["lekha pariksha"],
        "examples": ["annual statutory audit of a private limited company's accounts", "independent audit of a trust's financial statements", "tax audit report preparation under the Income Tax Act"],
        "attributes": {
            "material": [],
            "use": ["statutory compliance", "assurance"],
            "form": ["professional service"],
            "industry": ["accounting", "professional services", "finance"],
        },
        "clarification_questions": [],
        "exclusion_notes": [
            {"excluded_code": "SAC_998222", "reason": "998222 is bookkeeping/accounting (preparing the books) — 998221 is independently examining and certifying books already prepared"},
        ],
        "classification_confidence": {
            "level": "High",
            "rationale": "Financial/statutory auditing is a distinctly regulated service that maps uniquely to 998221.",
            "ambiguity_triggers": ["bookkeeping", "write the accounts", "maintain ledgers"],
        },
        "plain_rationale": "SAC 998221 covers financial auditing — independently examining a business's accounts and issuing an audit opinion or report, as done by a Chartered Accountant for statutory or tax audits. GST is 18%. This is different from bookkeeping (998222), which is the ongoing work of preparing and maintaining the accounts that get audited — a firm doing both should bill them under their respective codes.",
        "regulatory_citation": "Scheme of Classification of Services, annexure to Notification 11/2017-Central Tax (Rate), SAC 998221 (Financial auditing services), heading 9982, w.e.f. 01-07-2017.",
    },
    exceptions=_ARBITRAL_EXC,
)

add(
    "SAC_998223", ACCOUNTING_CANDIDATES,
    "Payroll services",
    {
        "synonyms": ["payroll processing", "payroll management", "salary processing", "payroll outsourcing"],
        "market_terms": ["payroll outsourcing services", "monthly payroll run", "salary and PF processing", "payslip generation"],
        "hindi_transliterated": [],
        "examples": ["processing monthly salaries and payslips for a 50-employee firm", "calculating PF and ESI deductions for staff payroll", "managing salary disbursement for a retail chain"],
        "attributes": {
            "material": [],
            "use": ["payroll processing", "statutory compliance"],
            "form": ["outsourced service"],
            "industry": ["accounting", "hr services", "professional services"],
        },
        "clarification_questions": [],
        "exclusion_notes": [
            {"excluded_code": "SAC_998222", "reason": "998222 is general bookkeeping — 998223 is specifically for running payroll (salary, PF, ESI processing), even when done by the same accounting firm"},
        ],
        "classification_confidence": {
            "level": "High",
            "rationale": "Payroll processing is a distinct, well-understood service that maps uniquely to 998223.",
            "ambiguity_triggers": ["bookkeeping", "HR recruitment", "accounting"],
        },
        "plain_rationale": "SAC 998223 covers payroll services — calculating and processing employee salaries, PF, ESI and related statutory deductions on a business's behalf. GST is 18%. Many accounting firms bundle this with bookkeeping, but for invoicing purposes payroll work should be billed under 998223, separate from general accounting (998222).",
        "regulatory_citation": "Scheme of Classification of Services, annexure to Notification 11/2017-Central Tax (Rate), SAC 998223 (Payroll services), heading 9982, w.e.f. 01-07-2017.",
    },
    exceptions=_ARBITRAL_EXC,
)

add(
    "SAC_998224", ACCOUNTING_CANDIDATES,
    "Other similar services n.e.c",
    {
        "synonyms": ["miscellaneous accounting service", "other bookkeeping-related service"],
        "market_terms": ["accounting-adjacent service n.e.c."],
        "hindi_transliterated": [],
        "examples": ["a professional accounting task that does not fit auditing, bookkeeping, or payroll specifically"],
        "attributes": {
            "material": [],
            "use": [],
            "form": [],
            "industry": ["accounting", "professional services"],
        },
        "clarification_questions": [],
        "exclusion_notes": [
            {"excluded_code": "SAC_998222", "reason": "998222 is the specific accounting/bookkeeping code — use 998224 only when the service genuinely doesn't fit 998221-998223"},
        ],
        "classification_confidence": {
            "level": "Low",
            "rationale": "Residual 'other' bucket for accounting-group services that don't fit auditing, bookkeeping, or payroll; cannot be matched from a plain description alone.",
            "ambiguity_triggers": [],
        },
        "plain_rationale": "SAC 998224 is a residual code for accounting-group services that don't specifically fit auditing (998221), bookkeeping (998222), or payroll (998223). Because it's a catch-all, correctly using it usually needs a professional's judgement on what the service actually is — check the more specific codes first.",
        "regulatory_citation": "Scheme of Classification of Services, annexure to Notification 11/2017-Central Tax (Rate), SAC 998224 (Other similar services n.e.c.), heading 9982, w.e.f. 01-07-2017.",
    },
    status="partial",
    exceptions=_ARBITRAL_EXC,
)

# =====================================================================
# MASK CLUSTER (3-way ambiguity demo): Ch63 textile, Ch90 breathing
# appliances, Ch33 cosmetic — 18 records
# =====================================================================

add(
    "HSN_6301", MASK_CANDIDATES, "Blankets and travelling rugs",
    {
        "synonyms": ["blanket", "travelling rug", "woollen blanket", "fleece blanket"],
        "market_terms": ["textile blanket", "hosiery blanket", "rug manufacturing"],
        "hindi_transliterated": ["kambal"],
        "examples": ["woollen blanket sold in winter season", "fleece travel rug for cars"],
        "attributes": {"material": ["wool", "fleece", "cotton", "synthetic fibre"], "use": ["bedding", "travel"], "form": ["made-up textile article"], "industry": ["textiles", "home furnishings"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Blankets and travelling rugs map cleanly and uniquely to 6301.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 6301 covers blankets and travelling rugs — woollen, fleece, cotton or synthetic. If you manufacture or sell blankets, this is your code. The GST rate for this heading could not be resolved from the notification schedules in our data, so confirm the current rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6301 — blankets and travelling rugs.",
    },
)

add(
    "HSN_6302", MASK_CANDIDATES, "Bed linen, table linen, toilet linen and kitchen linen",
    {
        "synonyms": ["bed sheet", "table linen", "kitchen towel", "toilet linen", "bedsheet set"],
        "market_terms": ["home furnishing textiles", "linen manufacturing", "hospitality linen"],
        "hindi_transliterated": ["chaddar"],
        "examples": ["cotton bedsheet set for retail sale", "kitchen towel pack", "hotel table linen"],
        "attributes": {"material": ["cotton", "linen", "polyester blend"], "use": ["bedding", "kitchen", "hospitality"], "form": ["made-up textile article"], "industry": ["textiles", "home furnishings", "hospitality"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Bed/table/kitchen linen maps cleanly to 6302.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 6302 covers bed linen, table linen, toilet linen and kitchen linen made from any textile material — bedsheets, pillow covers, table cloths, kitchen towels and similar household or hospitality linen. The GST rate for this heading could not be resolved from the notification schedules in our data; confirm the current rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6302 — bed linen, table linen, toilet linen and kitchen linen.",
    },
)

add(
    "HSN_6303", MASK_CANDIDATES, "Curtains and interior blinds; curtain or bed valances",
    {
        "synonyms": ["curtain", "window curtain", "interior blind", "door curtain", "bed valance"],
        "market_terms": ["curtain fabric stitching", "home décor textiles", "window furnishing"],
        "hindi_transliterated": ["parda"],
        "examples": ["stitched cotton window curtains", "roller blind for home interiors"],
        "attributes": {"material": ["cotton", "polyester", "synthetic fabric"], "use": ["home décor", "window covering"], "form": ["made-up textile article"], "industry": ["textiles", "home furnishings", "interior décor"]},
        "clarification_questions": [],
        "exclusion_notes": [{"excluded_code": "HSN_6304", "reason": "6304 is for other furnishing articles like cushion covers and bedspreads — 6303 is specifically curtains, blinds and valances"}],
        "classification_confidence": {"level": "High", "rationale": "Curtains and blinds map clearly to 6303; the only common mix-up is with other furnishing articles.", "ambiguity_triggers": ["cushion cover", "bedspread", "furnishing"]},
        "plain_rationale": "HSN 6303 covers curtains, drapes, interior blinds, and curtain or bed valances made of textile fabric. If you make or sell window curtains or fabric blinds, this is your code. The GST rate for this heading could not be resolved from the notification schedules in our data; confirm the current rate with your CA before invoicing. Related furnishing items like cushion covers fall under 6304 instead.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6303 — curtains, interior blinds, and curtain or bed valances.",
    },
)

add(
    "HSN_6304", MASK_CANDIDATES, "Other furnishing articles, excluding those of heading 94.04",
    {
        "synonyms": ["cushion cover", "bedspread", "sofa cover", "furnishing article", "table runner"],
        "market_terms": ["home furnishing textiles", "upholstery covers", "decorative textile items"],
        "hindi_transliterated": ["gaddi cover"],
        "examples": ["printed cushion covers sold in a set", "cotton bedspread for double bed", "sofa cover set"],
        "attributes": {"material": ["cotton", "polyester", "velvet"], "use": ["home décor", "upholstery"], "form": ["made-up textile article"], "industry": ["textiles", "home furnishings"]},
        "clarification_questions": [],
        "exclusion_notes": [{"excluded_code": "HSN_6303", "reason": "6303 is specifically curtains, blinds and valances — 6304 is other furnishing articles like cushion covers and bedspreads"}],
        "classification_confidence": {"level": "High", "rationale": "Furnishing articles like cushion covers and bedspreads map clearly to 6304.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 6304 covers other furnishing articles made of textile material — cushion covers, bedspreads, sofa covers, table runners and similar decorative home textiles — excluding mattress supports and bedding of heading 9404. The GST rate for this heading could not be resolved from the notification schedules in our data; confirm the current rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6304 — other furnishing articles, excluding those of heading 94.04.",
    },
)

add(
    "HSN_6305", MASK_CANDIDATES, "Sacks and bags of a kind used for the packing of goods",
    {
        "synonyms": ["gunny bag", "packing sack", "jute bag", "woven sack", "cement bag"],
        "market_terms": ["PP woven sacks", "bulk packaging bags", "jute packaging"],
        "hindi_transliterated": ["bora", "thaila"],
        "examples": ["jute gunny bags for grain packing", "woven polypropylene cement bags", "bulk rice packing sacks"],
        "attributes": {"material": ["jute", "polypropylene", "cotton"], "use": ["packing", "bulk storage"], "form": ["sack", "bag"], "industry": ["textiles", "packaging", "agriculture"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Sacks and bags used for packing goods map uniquely to 6305 regardless of material.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 6305 covers sacks and bags of textile material used for packing goods — jute gunny bags, woven polypropylene (PP) sacks, and similar bulk packaging. If you manufacture or trade in packing sacks for grain, cement, sugar or similar bulk goods, this is your code. GST is 18%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6305 — sacks and bags used for packing goods. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_6306", MASK_CANDIDATES, "Tarpaulins, awnings and sunblinds; tents; sails for boats, sailboards or landcraft; camping goods",
    {
        "synonyms": ["tarpaulin", "tent", "awning", "sunblind", "camping tent", "canopy"],
        "market_terms": ["waterproof tarpaulin sheet", "event tent rental stock", "PVC tarpaulin manufacturing"],
        "hindi_transliterated": ["tirpal"],
        "examples": ["waterproof tarpaulin sheet for truck covering", "camping tent for outdoor use", "cloth awning for a shop front"],
        "attributes": {"material": ["canvas", "PVC-coated fabric", "polyester"], "use": ["outdoor covering", "camping", "shelter"], "form": ["made-up textile article"], "industry": ["textiles", "outdoor equipment", "construction"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Tarpaulins, tents, awnings and camping goods map clearly to 6306.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 6306 covers tarpaulins, awnings, sunblinds, tents (including temporary canopies), sails, and camping goods made of textile material. If you make or sell tarpaulin sheets, tents, or fabric awnings, this is your code. The GST rate for this heading could not be resolved from the notification schedules in our data; confirm the current rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6306 — tarpaulins, awnings, tents, sails and camping goods.",
    },
)

add(
    "HSN_6307", MASK_CANDIDATES, "Other made up articles, including dress patterns",
    {
        "synonyms": ["made-up textile article", "dress pattern", "textile face mask", "cleaning cloth", "mop cloth"],
        "market_terms": ["other made-up textiles", "miscellaneous textile articles", "unclassified textile item trade"],
        "hindi_transliterated": [],
        "examples": ["printed dress pattern sold to tailors", "cotton cleaning or mop cloths sold in bulk", "made-up textile item not covered by any more specific heading in this chapter"],
        "attributes": {"material": ["cotton", "synthetic fabric", "mixed textile"], "use": ["miscellaneous"], "form": ["made-up textile article"], "industry": ["textiles"]},
        "clarification_questions": [
            {"question": "What specific item is it — a mask, a dress pattern, or a cleaning cloth?", "attribute": "use",
             "options": ["Face mask", "Dress pattern", "Cleaning cloth", "Other made-up item"], "disambiguates_from": ["HSN_63079091"]},
        ],
        "exclusion_notes": [{"excluded_code": "HSN_63079091", "reason": "63079091 is the specific sub-code for textile face masks — use it instead of the general 6307 heading when the product is specifically a mask"}],
        "classification_confidence": {
            "level": "Low",
            "rationale": "6307 is a residual 'other made up articles' heading covering many unrelated products (dress patterns, cleaning cloths, face masks); the plain description alone doesn't pin down which sub-item applies.",
            "ambiguity_triggers": ["mask", "dress pattern", "cleaning cloth", "rag"],
        },
        "plain_rationale": "HSN 6307 is a broad 'other made up textile articles' heading covering items like dress patterns, cleaning cloths, and textile face masks that don't have their own dedicated heading elsewhere in Chapter 63. Because it's a catch-all, the exact 8-digit code depends on the specific item — for instance, textile face masks have their own sub-code, 63079091. The GST rate for the general heading could not be resolved from the notification schedules in our data; confirm the current rate for your specific product with your CA.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6307 — other made up articles, including dress patterns.",
    },
)

add(
    "HSN_63079091", MASK_CANDIDATES,
    "Textile face masks, without a replaceable filter or mechanical parts, including surgical masks",
    {
        "synonyms": ["face mask", "cloth mask", "cotton mask", "surgical mask", "fabric mask", "reusable face mask"],
        "market_terms": ["non-woven face mask (fabric)", "PPE textile mask", "3-ply cloth mask"],
        "hindi_transliterated": [],
        "examples": ["3-ply cotton face mask sold in packs of 50", "reusable washable cloth face mask", "disposable surgical-style textile mask without a replaceable filter"],
        "attributes": {"material": ["cotton", "non-woven fabric", "cloth"], "use": ["personal protection", "hygiene"], "form": ["textile", "disposable", "reusable"], "industry": ["textiles", "healthcare supplies", "ppe"]},
        "clarification_questions": [
            {"question": "Does the mask have a replaceable filter cartridge or mechanical parts (like a valve)?", "attribute": "form",
             "options": ["No, plain fabric mask", "Yes, has a filter/valve or mechanical part"], "disambiguates_from": ["HSN_90200000"]},
            {"question": "Is it a cloth/fabric mask or a preparation applied to skin (like a clay or sheet face mask)?", "attribute": "form",
             "options": ["Fabric mask worn on the face", "Cosmetic skin-care preparation"], "disambiguates_from": ["HSN_33049990"]},
        ],
        "exclusion_notes": [
            {"excluded_code": "HSN_90200000", "reason": "90200000 covers respirators/gas masks with mechanical parts or replaceable filters — 63079091 is for plain textile masks without those parts"},
            {"excluded_code": "HSN_33049990", "reason": "33049990 covers cosmetic skin-care 'face masks' (creams, clay or sheet masks) — 63079091 is a fabric mask worn over the mouth and nose, not a skincare product"},
        ],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "The word 'mask' is genuinely 3-way ambiguous between a textile mask, a mechanical respirator, and a cosmetic skin preparation; once fabric-without-filter is confirmed, 63079091 is the right code.",
            "ambiguity_triggers": ["gas mask", "respirator", "filter", "valve", "face pack", "skin mask", "clay mask"],
        },
        "plain_rationale": "HSN 63079091 covers textile face masks made of fabric, without a replaceable filter or mechanical parts — ordinary cotton and surgical-style masks. If you make or sell cloth or non-woven fabric masks, this is your code. Watch for two look-alikes: masks with a filter cartridge or valve fall under HSN 9020 instead, and cosmetic 'face masks' applied to skin fall under HSN 3304. No resolved GST rate was found for this code in the notification schedules, so confirm the rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6307, tariff item 6307 90 91 — textile face masks without a replaceable filter or mechanical parts, including surgical masks.",
    },
)

add(
    "HSN_6310", MASK_CANDIDATES, "Used or new rags, scrap twine, cordage, rope and cables, of textile materials",
    {
        "synonyms": ["textile rags", "scrap twine", "waste cordage", "worn rope"],
        "market_terms": ["textile waste trade", "rag recycling", "scrap rope"],
        "hindi_transliterated": ["chindi", "purana kapda"],
        "examples": ["bundle of used cotton rags sold to a recycler", "worn-out rope and cordage scrap"],
        "attributes": {"material": ["textile waste", "rope", "twine"], "use": ["recycling", "industrial wiping"], "form": ["scrap", "rags"], "industry": ["textiles", "recycling", "waste trade"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Textile rags and rope/twine scrap map clearly to 6310.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 6310 covers used or new rags, scrap twine, cordage, rope and cables, and worn-out textile articles — essentially textile waste and scrap sold for recycling or industrial wiping. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 63, Heading 6310 — used or new rags and scrap textile cordage. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_3301", MASK_CANDIDATES, "Essential oils, resinoids and related aromatic extracts",
    {
        "synonyms": ["essential oil", "aromatic oil", "resinoid", "mentha oil", "peppermint oil"],
        "market_terms": ["essential oil manufacturing", "aromatherapy oil trade", "mentha/peppermint oil export"],
        "hindi_transliterated": ["itra", "sugandhit tel"],
        "examples": ["mentha (peppermint) oil sold in bulk drums", "lavender essential oil for aromatherapy", "citronella oil for industrial use"],
        "attributes": {"material": ["plant extract", "volatile oil"], "use": ["perfumery", "aromatherapy", "flavouring", "industrial raw material"], "form": ["liquid", "concentrate"], "industry": ["chemicals", "perfumery", "essential oils"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Essential oils and resinoids map clearly to 3301 by their physical/chemical nature.", "ambiguity_triggers": ["perfume", "finished fragrance"]},
        "plain_rationale": "HSN 3301 covers essential oils, resinoids, extracted oleoresins and related aromatic concentrates in their raw or semi-processed form — like mentha oil, lavender oil or citronella oil sold in bulk. It does not cover finished perfumes (that's 3303). Most goods in this heading actually attract 18% GST rather than the 5% shown as the general heading rate, so check the specific exception that applies to your product before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3301 — essential oils, resinoids and related aromatic extracts. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
    exceptions=[
        {"gst_rate": 18.0, "condition": "Menthol, mentha/peppermint oil and related mint-derivative products (not from natural menthol)"},
        {"gst_rate": 18.0, "condition": "Essential oils, resinoids, and concentrated aqueous distillates generally attract 18%, not the 5% default"},
    ],
)

add(
    "HSN_3302", MASK_CANDIDATES, "Mixtures of odoriferous substances used as industrial raw materials",
    {
        "synonyms": ["odoriferous mixture", "fragrance compound", "flavour concentrate", "beverage flavouring base"],
        "market_terms": ["fragrance compounding", "flavour house raw material", "industrial fragrance mixture"],
        "hindi_transliterated": ["khushbu"],
        "examples": ["fragrance compound sold to a soap manufacturer", "flavour base used in a beverage factory"],
        "attributes": {"material": ["odoriferous substance blend"], "use": ["industrial raw material", "beverage flavouring"], "form": ["mixture", "concentrate"], "industry": ["chemicals", "fmcg raw materials", "beverages"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Odoriferous mixtures used as industrial/beverage raw material map to 3302 by definition; the rate carries more uncertainty than the code.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 3302 covers mixtures of odoriferous (fragrance/flavour) substances used as raw material in industries like soap, cosmetics or beverage manufacturing — not finished perfumes or foods. GST is 18%, but this was matched with low confidence at the heading level rather than a rule written specifically for this heading, so confirm it with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3302 — mixtures of odoriferous substances used as industrial raw materials. Rate per Notification 9/2025-Integrated Tax (Rate).",
    },
)

add(
    "HSN_3303", MASK_CANDIDATES, "Perfumes and toilet waters",
    {
        "synonyms": ["perfume", "toilet water", "eau de toilette", "fragrance spray", "cologne"],
        "market_terms": ["fragrance retail", "perfume brand", "EDT/EDP bottling"],
        "hindi_transliterated": ["itra", "khushboo"],
        "examples": ["branded perfume bottle sold in retail", "eau de toilette spray", "attar/itra in a small vial"],
        "attributes": {"material": ["alcohol-based fragrance", "essential oil blend"], "use": ["personal fragrance"], "form": ["spray", "bottled liquid"], "industry": ["cosmetics", "perfumery", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Finished perfumes and toilet waters map clearly to 3303.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 3303 covers finished perfumes and toilet waters — the fragrance products people actually spray or dab on, as opposed to the raw essential oils and fragrance mixtures used to make them (3301, 3302). GST is 18%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3303 — perfumes and toilet waters. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_3304", MASK_CANDIDATES, "Beauty, make-up and skin-care preparations, including sunscreen; manicure or pedicure preparations",
    {
        "synonyms": ["face cream", "skin care product", "makeup preparation", "sunscreen", "manicure preparation", "cosmetic face mask"],
        "market_terms": ["beauty product retail", "skin-care preparation", "cosmetics FMCG"],
        "hindi_transliterated": ["bindi", "kajal"],
        "examples": ["face cream sold in retail packaging", "sunscreen lotion for daily use", "clay or sheet face mask for skincare", "bindi and kumkum packets"],
        "attributes": {"material": ["cream", "lotion", "powder", "gel"], "use": ["skin care", "makeup", "sun protection"], "form": ["cream", "lotion", "powder", "sheet"], "industry": ["cosmetics", "beauty", "fmcg"]},
        "clarification_questions": [
            {"question": "Is it kajal, kumkum, bindi, sindur, alta, talcum powder or face powder specifically?", "attribute": "use",
             "options": ["Yes, one of these specific items", "No, a general beauty/skin-care product"], "disambiguates_from": []},
        ],
        "exclusion_notes": [{"excluded_code": "HSN_33049990", "reason": "33049990 is the specific 'other' sub-code under 3304 used for skin preparations like cosmetic face masks that aren't separately listed (kajal, powders, creams have their own sub-codes)"}],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "3304 is broad (make-up, skin-care, sun-care, manicure); the exact sub-item and whether it falls in the lower-taxed carve-out (kajal, bindi, talcum, face powder) needs the specific product name.",
            "ambiguity_triggers": ["kajal", "bindi", "kumkum", "talcum", "face powder"],
        },
        "plain_rationale": "HSN 3304 covers beauty and make-up preparations and skin-care products other than medicines — face creams, sunscreens, manicure preparations, and cosmetic 'face masks' like clay or sheet masks used for skincare. The base GST rate is 5%, but most products in this heading actually attract 18%; only kajal, kumkum, bindi, sindur, alta, talcum powder and face powder keep the 5% rate. Check which bucket your specific product falls into before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3304 — beauty, make-up and skin-care preparations. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
    exceptions=[{"gst_rate": 18.0, "condition": "Beauty/skin-care preparations other than kajal, kumkum, bindi, sindur, alta, talcum powder and face powder"}],
)

add(
    "HSN_33049990", MASK_CANDIDATES, "Other",
    {
        "synonyms": ["cosmetic face mask", "clay face mask", "sheet mask", "skin-care mask (other/unlisted)"],
        "market_terms": ["skincare face mask retail", "beauty face mask packaging", "cosmetic 'other' skin preparation"],
        "hindi_transliterated": [],
        "examples": ["clay-based face mask sold in a jar", "single-use sheet face mask sachet"],
        "attributes": {"material": ["clay", "gel", "sheet"], "use": ["skin care"], "form": ["cream", "sheet", "gel"], "industry": ["cosmetics", "beauty", "fmcg"]},
        "clarification_questions": [],
        "exclusion_notes": [{"excluded_code": "HSN_63079091", "reason": "63079091 is a fabric mask worn over the mouth and nose for protection — 33049990 is a cosmetic skin-care preparation, not something worn as protective gear"}],
        "classification_confidence": {
            "level": "Low",
            "rationale": "This is a residual 'Other: Other' sub-code under skin-care preparations (3304); it exists because clay/sheet/gel cosmetic face masks have no dedicated tariff line of their own, so the plain description alone under-determines the exact fit.",
            "ambiguity_triggers": ["face mask (protective)", "gas mask", "respirator"],
        },
        "plain_rationale": "HSN 33049990 is a residual 'Other' sub-code that sits under skin-care preparations (heading 3304) and is where cosmetic face masks — clay masks, sheet masks, gel masks used as a beauty treatment — are classified, because they don't have a dedicated tariff line of their own. This is not the same as a protective face mask worn over the mouth and nose (that's HSN 63079091). GST is 5% under the base rate, though most items in this broader heading actually sit at 18% except a short named list — confirm with your CA which bucket applies.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3304, subheading 3304 99 — other beauty/skin-care preparations not separately specified. Rate per Notification 9/2025-Integrated Tax (Rate).",
    },
    status="partial",
    exceptions=[{"gst_rate": 18.0, "condition": "Beauty/skin-care preparations other than kajal, kumkum, bindi, sindur, alta, talcum powder and face powder"}],
)

add(
    "HSN_3305", MASK_CANDIDATES, "Preparations for use on the hair",
    {
        "synonyms": ["hair oil", "shampoo", "hair care preparation", "mehendi paste", "hair conditioner"],
        "market_terms": ["hair care FMCG", "haircare retail", "salon hair products"],
        "hindi_transliterated": ["tel", "mehendi"],
        "examples": ["coconut hair oil bottle", "shampoo sachet", "mehendi paste cone for henna application"],
        "attributes": {"material": ["oil", "cream", "paste"], "use": ["hair care"], "form": ["liquid", "paste", "gel"], "industry": ["cosmetics", "fmcg", "haircare"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Hair-care preparations map clearly to 3305; the main nuance is which specific items keep the 5% rate.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 3305 covers preparations used on the hair — shampoos, hair oils, conditioners, and mehendi (henna) paste in cones. The base GST rate is 5%, but this specifically applies only to mehendi paste in cones, hair oil, and shampoo; other hair preparations in this heading attract 18%.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3305 — preparations for use on the hair. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
    exceptions=[{"gst_rate": 18.0, "condition": "Hair preparations other than mehendi paste in cones, hair oil, and shampoo"}],
)

add(
    "HSN_3306", MASK_CANDIDATES, "Preparations for oral or dental hygiene, including denture fixatives and dental floss",
    {
        "synonyms": ["toothpaste", "mouthwash", "dental floss", "denture fixative", "tooth powder"],
        "market_terms": ["oral care FMCG", "dental hygiene product retail", "toothpaste manufacturing"],
        "hindi_transliterated": ["manjan"],
        "examples": ["toothpaste tube sold in retail", "dental floss pack", "denture fixative paste"],
        "attributes": {"material": ["paste", "powder", "liquid"], "use": ["oral hygiene", "dental care"], "form": ["tube", "floss", "powder"], "industry": ["fmcg", "dental care", "personal care"]},
        "clarification_questions": [
            {"question": "Is the product toothpaste, or another oral/dental hygiene item (floss, mouthwash, denture fixative)?", "attribute": "use",
             "options": ["Toothpaste", "Other oral/dental hygiene item"], "disambiguates_from": []},
        ],
        "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Oral and dental hygiene preparations map clearly to 3306; the open question is the rate split between toothpaste and other items in the heading, not the code itself.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 3306 covers preparations for oral or dental hygiene — toothpaste, mouthwash, denture fixative pastes and powders, and retail-packaged dental floss. The code is clear, but the GST rate is not: toothpaste attracts 5% while other oral hygiene preparations in this heading attract 18% under Notification 9/2025, and our data could not resolve which applies without knowing your specific product. Confirm with your CA which of the two rates fits your item before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3306 — preparations for oral or dental hygiene. Rate per Notification 9/2025-Integrated Tax (Rate) (rate depends on specific product).",
    },
    caveat="No single GST rate could be matched to this heading — toothpaste attracts 5% while other oral/dental hygiene preparations attract 18% under Notification 9/2025. Consult a tax professional to confirm which applies to your specific product.",
)

add(
    "HSN_3307", MASK_CANDIDATES, "Shaving preparations, personal deodorants, bath preparations and depilatories; room deodorisers",
    {
        "synonyms": ["shaving cream", "deodorant", "aftershave", "bath preparation", "room freshener"],
        "market_terms": ["personal care FMCG", "grooming products retail", "room deodoriser"],
        "hindi_transliterated": [],
        "examples": ["deodorant spray can", "aftershave lotion bottle", "room freshener spray"],
        "attributes": {"material": ["cream", "spray", "liquid"], "use": ["personal grooming", "room fragrance"], "form": ["spray", "cream", "lotion"], "industry": ["cosmetics", "personal care", "fmcg"]},
        "clarification_questions": [],
        "exclusion_notes": [{"excluded_code": "HSN_3303", "reason": "3303 is finished perfumes and toilet waters — 3307 is grooming preparations like shaving cream, deodorants and bath products, not fragrance-first products"}],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "3307 bundles several distinct personal-care and room-fragrance products; the source rate exception text was truncated, so the exact list of items still qualifying for 5% is not fully known from this record alone.",
            "ambiguity_triggers": ["perfume", "essential oil", "skin cream"],
        },
        "plain_rationale": "HSN 3307 covers pre-shave, shaving and after-shave preparations, personal deodorants, bath preparations, depilatories and similar grooming products, plus room deodorisers. The base rate shown is 5%, but most items in this heading attract 18%; shaving cream is confirmed to keep the lower rate, though our source text for the full exception list was cut off, so confirm the exact list with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 33, Heading 3307 — shaving/grooming preparations, deodorants and room deodorisers. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
    exceptions=[{"gst_rate": 18.0, "condition": "Grooming/toilet preparations other than shaving cream (full carve-out list truncated in source notification text)"}],
)

add(
    "HSN_90200000", MASK_CANDIDATES,
    "Breathing appliances and gas masks, excluding masks with no mechanical parts or replaceable filter",
    {
        "synonyms": ["gas mask", "respirator", "breathing apparatus", "industrial respirator mask", "respirator with valve"],
        "market_terms": ["industrial safety respirator", "PPE breathing apparatus", "gas mask with filter cartridge"],
        "hindi_transliterated": [],
        "examples": ["industrial respirator mask with replaceable filter cartridge", "gas mask used in chemical handling", "respirator with an exhalation valve"],
        "attributes": {"material": ["rubber", "plastic", "filter cartridge"], "use": ["industrial safety", "chemical protection", "breathing protection"], "form": ["mechanical device", "reusable equipment"], "industry": ["industrial safety", "ppe", "healthcare"]},
        "clarification_questions": [
            {"question": "Does the mask have a replaceable filter cartridge or a mechanical valve?", "attribute": "form",
             "options": ["Yes", "No, it's a plain fabric mask"], "disambiguates_from": ["HSN_63079091"]},
        ],
        "exclusion_notes": [{"excluded_code": "HSN_63079091", "reason": "63079091 is a plain textile mask with no filter or mechanical parts — 9020 is specifically for masks/respirators that do have a replaceable filter or mechanical parts (e.g. a valve)"}],
        "classification_confidence": {
            "level": "High",
            "rationale": "A mask with a mechanical part or replaceable filter cartridge maps clearly to 9020, distinct from a plain fabric mask.",
            "ambiguity_triggers": ["cloth mask", "surgical mask", "fabric mask"],
        },
        "plain_rationale": "HSN 9020 (tariff item 9020 00 00) covers gas masks and other breathing appliances that have mechanical parts or a replaceable filter — industrial respirators and similar protective equipment. It specifically excludes plain protective masks that have neither mechanical parts nor a replaceable filter; those simpler fabric masks fall under HSN 63079091 instead. GST is 5%, but this was matched with low confidence at the heading level rather than a rule written specifically for this item, so confirm it with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 90, Heading 9020, tariff item 9020 00 00 — other breathing appliances and gas masks. Rate per Notification 9/2025-Integrated Tax (Rate).",
    },
)

# =====================================================================
# NAMKEEN / FOOD-PREPARATION CLUSTER (all Ch19-21 headings) — 18 records
# =====================================================================

add(
    "HSN_1901", NAMKEEN_CANDIDATES, "Malt extract; food preparations of flour, groats, meal, starch or malt extract, not elsewhere specified",
    {
        "synonyms": ["malt extract", "baby food preparation", "cereal-based food mix", "milk food preparation"],
        "market_terms": ["infant nutrition base", "malted food drink mix", "bakery raw material"],
        "hindi_transliterated": [],
        "examples": ["malted milk food drink powder", "cereal-based baby food mix"],
        "attributes": {"material": ["malt", "flour", "milk solids"], "use": ["nutrition", "bakery raw material"], "form": ["powder", "extract"], "industry": ["food processing", "fmcg", "bakery"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Malt extract and flour/milk-based food preparations not covered elsewhere map to 1901 by definition.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 1901 covers malt extract and food preparations made from flour, groats, meal, starch or malt extract (with little or no cocoa) that aren't covered by a more specific heading — this includes many infant/baby food mixes and malted food-drink powders. GST is 5%, but this was matched with low confidence at the heading level, so confirm the rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 19, Heading 1901 — malt extract and flour/milk-based food preparations. Rate per Notification 9/2025-Integrated Tax (Rate).",
    },
)

add(
    "HSN_1902", NAMKEEN_CANDIDATES, "Pasta, whether or not cooked or stuffed, and couscous",
    {
        "synonyms": ["pasta", "macaroni", "noodles", "spaghetti", "instant noodles"],
        "market_terms": ["dry pasta manufacturing", "instant noodle brand", "semolina pasta"],
        "hindi_transliterated": ["seviyan"],
        "examples": ["packet of dry spaghetti", "instant noodle cup", "vermicelli/seviyan pack"],
        "attributes": {"material": ["semolina", "wheat flour"], "use": ["cooking", "instant food"], "form": ["dried", "instant", "fresh"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Pasta and couscous in any prepared form map clearly to 1902.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 1902 covers pasta in all forms — dried, fresh, stuffed or instant — including spaghetti, macaroni, noodles and vermicelli/seviyan, as well as couscous. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 19, Heading 1902 — pasta and couscous. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_1903", NAMKEEN_CANDIDATES, "Tapioca and substitutes therefor prepared from starch, in the form of flakes, grains, pearls, siftings or similar forms",
    {
        "synonyms": ["tapioca", "sabudana", "sago", "tapioca pearls"],
        "market_terms": ["sabudana packaging", "tapioca starch product", "sago manufacturing"],
        "hindi_transliterated": ["sabudana"],
        "examples": ["sabudana (sago pearls) packet sold for fasting food", "tapioca flakes"],
        "attributes": {"material": ["starch", "tapioca"], "use": ["cooking", "fasting food"], "form": ["pearls", "flakes", "grains"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Sabudana/sago and other starch-based tapioca substitutes map clearly to 1903.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 1903 covers tapioca and its substitutes prepared from starch, in the form of flakes, grains, pearls, siftings or similar shapes — this is the code for sabudana (sago pearls), a common fasting-food ingredient in India. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 19, Heading 1903 — tapioca and substitutes prepared from starch. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_1904", NAMKEEN_CANDIDATES,
    "Prepared foods obtained by the swelling or roasting of cereals; cereals otherwise prepared, not elsewhere specified",
    {
        "synonyms": ["corn flakes", "puffed rice", "muri", "extruded snack", "roasted cereal snack", "corn puffs"],
        "market_terms": ["breakfast cereal", "extruded corn snack", "ready-to-eat cereal"],
        "hindi_transliterated": ["muri", "chira", "khoi", "murki"],
        "examples": ["packet of corn flakes", "muri (puffed rice) sold loose", "extruded corn curls made by roasting/swelling cereal"],
        "attributes": {"material": ["corn", "rice", "wheat", "other cereals"], "use": ["breakfast food", "snacking"], "form": ["flakes", "puffed", "extruded"], "industry": ["food processing", "fmcg", "snacks"]},
        "clarification_questions": [
            {"question": "Is the snack made by swelling/roasting/extruding cereal grains (like corn flakes or corn puffs), or is it a fried/seasoned savoury mixture (like namkeen or bhujia)?", "attribute": "form",
             "options": ["Swelled/roasted/extruded cereal snack", "Fried or seasoned savoury mixture"], "disambiguates_from": ["HSN_2106"]},
        ],
        "exclusion_notes": [{"excluded_code": "HSN_2106", "reason": "2106 covers fried or seasoned savoury food mixtures like namkeen and bhujia not made by swelling/roasting cereal — 1904 is specifically for cereal products prepared by swelling, roasting or pre-cooking (like corn flakes and puffed rice)"}],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "Many Indian extruded/puffed snacks sit right at the boundary between 1904 (cereals prepared by swelling/roasting) and 2106 (other food preparations); the production method decides which heading applies.",
            "ambiguity_triggers": ["namkeen", "bhujia", "fried snack", "savoury mixture", "sev"],
        },
        "plain_rationale": "HSN 1904 covers prepared foods made by swelling or roasting cereals — corn flakes are the classic example — plus pre-cooked or otherwise prepared cereal grains and flakes not covered elsewhere. It also covers puffed rice (muri), flattened rice (chira) and parched rice/paddy (khoi, murki) at 5%. Extruded cereal snacks like corn puffs generally belong here too. If your snack is instead a fried, seasoned savoury mixture — typical namkeen or bhujia — that's usually classified under HSN 2106 instead, so the production method of your product matters here.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 19, Heading 1904 — prepared foods from swelling/roasting of cereals. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
    exceptions=[{"gst_rate": 5.0, "condition": "Corn flakes, bulgur wheat and cereal-flake preparations, and puffed/flattened/parched rice (muri, chira, khoi, murki) — all at 5%"}],
)

add(
    "HSN_1905", NAMKEEN_CANDIDATES, "Bread, pastry, cakes, biscuits and other bakers' wares; communion wafers and similar products",
    {
        "synonyms": ["bread", "biscuit", "cake", "pastry", "rusk"],
        "market_terms": ["bakery products", "packaged biscuits", "bakery wholesale"],
        "hindi_transliterated": [],
        "examples": ["packet of glucose biscuits", "sliced bread loaf", "rusk pack"],
        "attributes": {"material": ["flour", "sugar", "yeast"], "use": ["bakery", "snacking"], "form": ["baked good"], "industry": ["food processing", "bakery", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Baked bread, biscuits, cakes and pastry map clearly to 1905.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 1905 covers bread, pastry, cakes, biscuits and other baked goods, whether or not they contain cocoa, plus items like communion wafers and rice paper. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 19, Heading 1905 — bread, pastry, cakes, biscuits and bakers' wares. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2001", NAMKEEN_CANDIDATES, "Vegetables, fruit, nuts and other edible parts of plants, prepared or preserved by vinegar or acetic acid",
    {
        "synonyms": ["pickle", "vinegar pickle", "preserved vegetable", "achar"],
        "market_terms": ["pickle manufacturing", "vinegar-preserved food", "condiment retail"],
        "hindi_transliterated": ["achar"],
        "examples": ["mango pickle in vinegar", "pickled onions jar"],
        "attributes": {"material": ["vegetables", "fruit", "vinegar"], "use": ["condiment", "preserved food"], "form": ["jarred", "bottled"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Vinegar/acetic-acid preserved vegetables and fruit map clearly to 2001.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2001 covers vegetables, fruit, nuts and other edible plant parts preserved specifically using vinegar or acetic acid — classic vinegar pickles (achar). GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2001 — vegetables/fruit prepared or preserved by vinegar or acetic acid. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2002", NAMKEEN_CANDIDATES, "Tomatoes prepared or preserved otherwise than by vinegar or acetic acid",
    {
        "synonyms": ["tomato puree", "tomato paste", "canned tomato", "tomato ketchup base"],
        "market_terms": ["tomato processing", "canned tomato product", "tomato paste manufacturing"],
        "hindi_transliterated": [],
        "examples": ["canned whole peeled tomatoes", "tomato puree tin"],
        "attributes": {"material": ["tomato"], "use": ["cooking ingredient", "food processing input"], "form": ["canned", "puree", "paste"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Prepared/preserved tomatoes map clearly to 2002.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2002 covers tomatoes prepared or preserved other than by vinegar or acetic acid — canned tomatoes, tomato puree and tomato paste. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2002 — prepared or preserved tomatoes. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2003", NAMKEEN_CANDIDATES, "Mushrooms and truffles, prepared or preserved otherwise than by vinegar or acetic acid",
    {
        "synonyms": ["canned mushroom", "preserved mushroom", "truffle preparation", "mushroom in brine"],
        "market_terms": ["mushroom processing", "canned mushroom retail", "brined mushroom supply"],
        "hindi_transliterated": ["khumb"],
        "examples": ["canned button mushrooms", "preserved mushroom in brine"],
        "attributes": {"material": ["mushroom", "truffle"], "use": ["cooking ingredient"], "form": ["canned", "preserved"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Prepared/preserved mushrooms and truffles map clearly to 2003.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2003 covers mushrooms and truffles prepared or preserved otherwise than by vinegar or acetic acid — typically canned or brined mushrooms. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2003 — prepared or preserved mushrooms and truffles. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2004", NAMKEEN_CANDIDATES, "Other vegetables prepared or preserved otherwise than by vinegar or acetic acid, frozen",
    {
        "synonyms": ["frozen vegetable", "frozen mixed veg", "frozen peas", "frozen corn"],
        "market_terms": ["frozen vegetable processing", "IQF vegetables", "frozen food retail"],
        "hindi_transliterated": [],
        "examples": ["frozen green peas packet", "frozen mixed vegetable pack"],
        "attributes": {"material": ["vegetables"], "use": ["cooking ingredient"], "form": ["frozen"], "industry": ["food processing", "frozen foods", "fmcg"]},
        "clarification_questions": [
            {"question": "Is the vegetable frozen or not frozen?", "attribute": "form", "options": ["Frozen", "Not frozen (canned/preserved)"], "disambiguates_from": ["HSN_2005"]},
        ],
        "exclusion_notes": [{"excluded_code": "HSN_2005", "reason": "2005 is the same category of prepared/preserved vegetables but not frozen — 2004 is specifically the frozen form"}],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "This heading is defined purely by physical state (frozen); products that look identical when not frozen fall under the sibling heading 2005 instead.",
            "ambiguity_triggers": ["canned vegetable", "preserved vegetable (not frozen)"],
        },
        "plain_rationale": "HSN 2004 covers other vegetables (not covered by 2001-2003) prepared or preserved otherwise than by vinegar, specifically in frozen form — like frozen peas or frozen mixed vegetables. The identical product sold not frozen falls under HSN 2005 instead. GST is 5%, but this was matched with low confidence at the heading level, so confirm the rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2004 — other frozen prepared/preserved vegetables. Rate per Notification 9/2025-Integrated Tax (Rate).",
    },
)

add(
    "HSN_2005", NAMKEEN_CANDIDATES, "Other vegetables prepared or preserved otherwise than by vinegar or acetic acid, not frozen",
    {
        "synonyms": ["canned vegetable", "preserved vegetable mix", "bottled vegetable", "shelf-stable vegetable pack"],
        "market_terms": ["canned vegetable processing", "ambient shelf-stable vegetables", "bottled vegetable retail"],
        "hindi_transliterated": [],
        "examples": ["canned sweet corn (not frozen)", "bottled preserved vegetable mix"],
        "attributes": {"material": ["vegetables"], "use": ["cooking ingredient"], "form": ["canned", "bottled", "not frozen"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [],
        "exclusion_notes": [{"excluded_code": "HSN_2004", "reason": "2004 is the same category of prepared/preserved vegetables but frozen — 2005 is specifically the not-frozen form"}],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "Distinguished from its sibling heading purely by physical state (not frozen); needs that one attribute to confirm.",
            "ambiguity_triggers": ["frozen vegetable"],
        },
        "plain_rationale": "HSN 2005 covers other vegetables (not covered by 2001-2003) prepared or preserved otherwise than by vinegar, in not-frozen form — canned or bottled vegetables like sweet corn or mixed vegetables. The frozen version of the same product falls under HSN 2004 instead. GST is 5%, but this was matched with low confidence at the heading level, so confirm the rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2005 — other prepared/preserved vegetables, not frozen. Rate per Notification 9/2025-Integrated Tax (Rate).",
    },
)

add(
    "HSN_2007", NAMKEEN_CANDIDATES, "Jams, fruit jellies, marmalades, fruit or nut purée and fruit or nut pastes, obtained by cooking",
    {
        "synonyms": ["jam", "fruit jelly", "marmalade", "fruit puree", "fruit paste"],
        "market_terms": ["jam manufacturing", "fruit preserve retail", "marmalade brand"],
        "hindi_transliterated": [],
        "examples": ["mixed fruit jam jar", "orange marmalade bottle"],
        "attributes": {"material": ["fruit", "sugar"], "use": ["spread", "cooking ingredient"], "form": ["jam", "jelly", "paste"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Jams, jellies, marmalades and fruit pastes map clearly to 2007.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2007 covers jams, fruit jellies, marmalades, and fruit or nut purees and pastes made by cooking, with or without added sugar. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2007 — jams, jellies, marmalades and fruit pastes. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2008", NAMKEEN_CANDIDATES, "Fruit, nuts and other edible parts of plants, otherwise prepared or preserved, not elsewhere specified",
    {
        "synonyms": ["preserved fruit", "candied fruit", "roasted nuts (prepared)", "fruit in syrup"],
        "market_terms": ["preserved fruit processing", "candied fruit retail", "packaged roasted nuts"],
        "hindi_transliterated": [],
        "examples": ["canned fruit cocktail in syrup", "candied fruit peel", "roasted and salted preserved nuts"],
        "attributes": {"material": ["fruit", "nuts"], "use": ["snacking", "cooking ingredient"], "form": ["canned", "candied", "roasted"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [],
        "exclusion_notes": [{"excluded_code": "HSN_2106", "reason": "2106 covers general savoury food preparations like salted/spiced nut and namkeen mixtures — 2008 is for fruit/nuts preserved with sugar, spirit or similar preparation, not fried savoury snack mixtures"}],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "This is a broad 'not elsewhere specified' heading covering many different prepared fruit and nut products; the specific product name decides finer classification within it.",
            "ambiguity_triggers": ["namkeen nuts", "salted nuts snack mixture"],
        },
        "plain_rationale": "HSN 2008 covers fruit, nuts and other edible plant parts otherwise prepared or preserved — including added sugar, sweetening matter or spirit — that aren't covered by a more specific heading, such as canned fruit cocktail or candied fruit. Plain roasted or fried savoury nut/namkeen mixtures are usually classified under HSN 2106 instead, so check which preparation matches your product. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2008 — fruit/nuts otherwise prepared or preserved, not elsewhere specified. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2009", NAMKEEN_CANDIDATES, "Fruit or nut juices and vegetable juices, unfermented and not containing added spirit",
    {
        "synonyms": ["fruit juice", "fruit nectar", "vegetable juice", "coconut water (packaged)"],
        "market_terms": ["packaged fruit juice", "juice concentrate", "beverage juice manufacturing"],
        "hindi_transliterated": ["ras"],
        "examples": ["packaged mango juice tetra pack", "bottled coconut water", "vegetable juice blend"],
        "attributes": {"material": ["fruit", "vegetable", "juice concentrate"], "use": ["drinking"], "form": ["bottled", "tetra pack", "canned"], "industry": ["beverages", "fmcg"]},
        "clarification_questions": [
            {"question": "Does the drink contain real fruit/vegetable juice, or is it a flavoured/sweetened water-based drink with no juice content?", "attribute": "material",
             "options": ["Contains real fruit/vegetable juice", "Flavoured/sweetened water, no juice"], "disambiguates_from": ["HSN_2202"]},
        ],
        "exclusion_notes": [{"excluded_code": "HSN_2202", "reason": "2202 covers flavoured/sweetened water-based beverages with no real juice content — 2009 is specifically unfermented fruit, nut or vegetable juice"}],
        "classification_confidence": {
            "level": "High",
            "rationale": "Genuine fruit, nut or vegetable juice maps clearly to 2009; the common mix-up is with juice-flavoured but juice-free soft drinks under 2202.",
            "ambiguity_triggers": ["soft drink", "flavoured water", "juice drink (no real juice)"],
        },
        "plain_rationale": "HSN 2009 covers unfermented fruit, nut or vegetable juices — including grape must and coconut water — with or without added sugar, but without added spirit. If your product is a real fruit or vegetable juice, this is your code. Juice-flavoured but juice-free soft drinks belong under HSN 2202 instead. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 20, Heading 2009 — fruit, nut and vegetable juices. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2101", NAMKEEN_CANDIDATES,
    "Coffee, tea or mate extracts and preparations; roasted chicory and coffee substitutes",
    {
        "synonyms": ["instant coffee", "coffee extract", "tea extract", "chicory coffee substitute", "instant tea premix"],
        "market_terms": ["instant coffee manufacturing", "coffee premix", "chicory blend"],
        "hindi_transliterated": [],
        "examples": ["instant coffee powder jar", "3-in-1 tea premix sachet", "roasted chicory coffee substitute"],
        "attributes": {"material": ["coffee", "tea", "chicory"], "use": ["beverage preparation"], "form": ["powder", "extract", "granules"], "industry": ["food processing", "beverages", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Coffee/tea extracts and roasted chicory substitutes map clearly to 2101.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2101 covers extracts, essences and concentrates of coffee, tea or mate, preparations based on these, and roasted chicory and other roasted coffee substitutes — instant coffee, tea premixes and similar products. The GST rate for this heading could not be resolved from the notification schedules in our data; confirm the current rate with your CA before invoicing.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 21, Heading 2101 — coffee/tea/mate extracts and roasted coffee substitutes.",
    },
)

add(
    "HSN_2102", NAMKEEN_CANDIDATES, "Yeasts (active or inactive); other single-cell micro-organisms, dead; prepared baking powders",
    {
        "synonyms": ["yeast", "baking powder", "instant yeast", "active dry yeast"],
        "market_terms": ["bakery yeast supply", "baking powder manufacturing", "fermentation ingredient trade"],
        "hindi_transliterated": [],
        "examples": ["packet of active dry yeast for baking", "baking powder tin"],
        "attributes": {"material": ["yeast", "baking powder"], "use": ["baking", "fermentation"], "form": ["powder", "granules"], "industry": ["food processing", "bakery", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Yeast and prepared baking powder map clearly to 2102.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2102 covers yeasts (active or inactive), other dead single-cell micro-organisms, and prepared baking powders. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 21, Heading 2102 — yeasts and prepared baking powders. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2103", NAMKEEN_CANDIDATES, "Sauces and preparations therefor; mixed condiments and mixed seasonings; mustard flour and meal and prepared mustard",
    {
        "synonyms": ["sauce", "ketchup", "chutney", "mixed condiment", "mustard paste"],
        "market_terms": ["sauce manufacturing", "condiment retail", "ketchup brand"],
        "hindi_transliterated": ["chatni"],
        "examples": ["tomato ketchup bottle", "mixed pickle-style chutney jar", "mustard sauce"],
        "attributes": {"material": ["tomato", "spices", "mustard"], "use": ["condiment", "cooking ingredient"], "form": ["bottled", "jarred"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Sauces, condiments and prepared mustard map clearly to 2103.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2103 covers sauces and preparations for sauces, mixed condiments and seasonings, and mustard flour, meal and prepared mustard — ketchup, chutney and similar condiments. GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 21, Heading 2103 — sauces, condiments and prepared mustard. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2104", NAMKEEN_CANDIDATES, "Soups and broths and preparations therefor; homogenised composite food preparations",
    {
        "synonyms": ["soup", "broth", "instant soup mix", "baby food (homogenised)"],
        "market_terms": ["instant soup manufacturing", "packaged broth", "homogenised baby food"],
        "hindi_transliterated": [],
        "examples": ["instant soup packet", "canned broth", "homogenised baby food jar"],
        "attributes": {"material": ["vegetables", "meat", "cereal"], "use": ["cooking", "infant nutrition"], "form": ["powder", "canned", "jarred"], "industry": ["food processing", "fmcg"]},
        "clarification_questions": [], "exclusion_notes": [],
        "classification_confidence": {"level": "High", "rationale": "Soups, broths and homogenised composite food preparations map clearly to 2104.", "ambiguity_triggers": []},
        "plain_rationale": "HSN 2104 covers soups and broths and preparations for them, plus homogenised composite food preparations (used for infant food or dietetic purposes). GST is 5%, matched at the heading level.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 21, Heading 2104 — soups, broths and homogenised composite food preparations. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
)

add(
    "HSN_2106", NAMKEEN_CANDIDATES, "Food preparations not elsewhere specified or included",
    {
        "synonyms": ["namkeen", "bhujia", "savoury snack mixture", "farsan", "fried snack mix", "spiced nut mixture"],
        "market_terms": ["namkeen manufacturing", "savoury snack packaging", "farsan wholesale"],
        "hindi_transliterated": ["namkeen", "bhujia", "farsan", "chivda"],
        "examples": ["packet of aloo bhujia namkeen", "mixed farsan/chivda snack pack", "spiced roasted chana mixture"],
        "attributes": {"material": ["gram flour", "rice flakes", "lentils", "spices", "oil"], "use": ["snacking"], "form": ["fried", "roasted", "mixed"], "industry": ["food processing", "fmcg", "snacks"]},
        "clarification_questions": [
            {"question": "Is the snack a fried/seasoned savoury mixture (namkeen, bhujia, farsan), or is it made by swelling/roasting/extruding cereal grains (like corn flakes or corn puffs)?", "attribute": "form",
             "options": ["Fried/seasoned savoury mixture", "Swelled/roasted/extruded cereal snack"], "disambiguates_from": ["HSN_1904"]},
            {"question": "Is the product pan masala or a betel-nut preparation?", "attribute": "use",
             "options": ["No, a savoury food snack", "Yes, pan masala / supari preparation"], "disambiguates_from": ["HSN_21069020"]},
        ],
        "exclusion_notes": [
            {"excluded_code": "HSN_1904", "reason": "1904 is for cereal products prepared by swelling, roasting or extrusion (like corn flakes/puffs) — 2106 is for fried and seasoned savoury mixtures like namkeen and bhujia"},
            {"excluded_code": "HSN_21069020", "reason": "21069020 (pan masala) sits under the same 2106 heading but is taxed very differently (28% GST plus 60% compensation cess) — do not bill pan masala under the general namkeen/food-preparation code"},
        ],
        "classification_confidence": {
            "level": "Medium",
            "rationale": "Namkeen and similar savoury snack mixtures generally fall under this residual 'other food preparations' heading, but the boundary with cereal-based snacks classified under 1904 depends on how the product is made, and the same heading also contains the much-higher-taxed pan masala sub-code.",
            "ambiguity_triggers": ["corn flakes", "corn puffs", "pan masala", "supari", "betel nut"],
        },
        "plain_rationale": "HSN 2106 is the general 'food preparations not elsewhere specified' heading, and it's where most Indian savoury snacks — namkeen, bhujia, farsan, chivda — are classified. GST is 5% generally, but this heading also contains pan masala (21069020), taxed at a much higher 28% GST plus 60% cess — a different bucket that must not be billed under the general namkeen rate. Snacks made by swelling, roasting or extruding cereal grains (corn flakes, corn puffs) belong under HSN 1904 instead. Rates here varied historically by branding before being harmonised — see the rate history panel.",
        "regulatory_citation": "ITC(HS) 2022, Chapter 21, Heading 2106 — food preparations not elsewhere specified or included. Rate per Notification 9/2025-Integrated Tax (Rate), w.e.f. 22-09-2025.",
    },
    exceptions=[{"gst_rate": 5.0, "condition": "Applies to all food preparations not elsewhere specified, except pan masala"}],
)


def main():
    prepared = [build_record(*r) for r in RECORDS]

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
    total, new = write_jsonl(finalized)
    print(f"enriched.jsonl now has {total} records ({new} new from this run).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
