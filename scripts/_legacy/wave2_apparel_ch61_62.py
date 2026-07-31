"""
Wave 2, first batch: Chapter 61 (knitted apparel) + Chapter 62 (woven/not-knitted
apparel) heading-level records — 33 records. Same harness as Wave 1
(scripts/enrichment_harness.py); this file only supplies content.

Every heading in these two chapters shares the same rate shape in the master:
18% GST, matched only at chapter level (rate_confidence "low", rate_scope
"chapter") with one shared exception — apparel sold at <=Rs 2500/piece drops
to 5%. That shared shape is factored out below instead of repeated 33 times.
The real content difference between records is the knitted/not-knitted pairing
(6101<->6201, 6109 T-shirts vs 6206/6211, etc.) which mirrors the T-shirt
worked example in enrichment_prompt_v3.md Section 8.1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import load_master, validate, finalize, write_jsonl
from wave1_records import build_record  # reuse the same record assembler

MASTER = load_master()

CH61_HEADINGS = ["HSN_6101", "HSN_6102", "HSN_6103", "HSN_6104", "HSN_6105", "HSN_6106", "HSN_6107",
                  "HSN_6108", "HSN_6109", "HSN_6110", "HSN_6111", "HSN_6112", "HSN_6114", "HSN_6115",
                  "HSN_6116", "HSN_6117"]
CH62_HEADINGS = ["HSN_6201", "HSN_6202", "HSN_6203", "HSN_6204", "HSN_6205", "HSN_6206", "HSN_6207",
                  "HSN_6208", "HSN_6209", "HSN_6210", "HSN_6211", "HSN_6212", "HSN_6213", "HSN_6214",
                  "HSN_6215", "HSN_6216", "HSN_6217"]
APPAREL_CANDIDATES = CH61_HEADINGS + CH62_HEADINGS

CH61_CAVEAT = "Rate inferred from the Chapter 61 entry, not a rule written for this specific heading. Verify against Notification 9/2025 before invoicing."
CH62_CAVEAT = "Rate inferred from the Chapter 62 entry, not a rule written for this specific heading. Verify against Notification 9/2025 before invoicing."
KNIT_EXC = [{"gst_rate": 5.0, "condition": "Knitted/crocheted apparel and clothing accessories of sale value ≤ ₹2,500 per piece"}]
WOVEN_EXC = [{"gst_rate": 5.0, "condition": "Non-knitted apparel and clothing accessories of sale value ≤ ₹2,500 per piece"}]

RECORDS = []


def add(mid, candidates, title, ai, status="complete", exceptions=None, caveat=None):
    RECORDS.append((mid, candidates, title, ai, status, exceptions or [], caveat))


def add61(mid, title, ai, **kw):
    add(mid, APPAREL_CANDIDATES, title, ai, exceptions=KNIT_EXC, caveat=CH61_CAVEAT, **kw)


def add62(mid, title, ai, **kw):
    add(mid, APPAREL_CANDIDATES, title, ai, exceptions=WOVEN_EXC, caveat=CH62_CAVEAT, **kw)


# =====================================================================
# CHAPTER 61 — knitted or crocheted apparel
# =====================================================================

add61("HSN_6101", "Men's or boys' knitted overcoats, anoraks, wind-cheaters and similar articles", {
    "synonyms": ["men's winter jacket", "knitted overcoat", "windcheater", "anorak", "knitted men's jacket"],
    "market_terms": ["knitted outerwear", "men's winter RMG", "hosiery jacket"],
    "hindi_transliterated": ["jacket"],
    "examples": ["men's knitted winter jacket", "boys' fleece windcheater"],
    "attributes": {"material": ["knitted fabric", "fleece", "wool blend"], "use": ["winter wear", "outerwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6201"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6201", "reason": "6201 is the same garment type (men's/boys' overcoats, anoraks) but woven/not-knitted — 6101 is knitted or crocheted only"}, {"excluded_code": "HSN_6102", "reason": "6102 is the equivalent women's/girls' garment — 6101 is men's and boys' only"}],
    "classification_confidence": {"level": "Medium", "rationale": "Men's knitted outerwear is well-defined, but the knitted-vs-woven split decides between chapters 61 and 62.", "ambiguity_triggers": ["woven", "not knitted", "women's", "ladies"]},
    "plain_rationale": "HSN 6101 covers men's and boys' knitted or crocheted overcoats, anoraks, windcheaters and similar outerwear. If you make or sell knitted winter jackets for men/boys, this is your code. The identical woven (non-stretch) garment falls under HSN 6201 instead. GST is 18%, but this rate was inferred from the chapter-wide Chapter 61 entry rather than a rule written for this specific heading, so confirm it with your CA. Garments selling at ₹2,500 or less per piece attract 5% instead.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6101 — men's/boys' knitted overcoats and similar articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6102", "Women's or girls' knitted overcoats, anoraks, wind-cheaters and similar articles", {
    "synonyms": ["women's winter jacket", "knitted overcoat", "ladies windcheater", "knitted women's jacket"],
    "market_terms": ["knitted outerwear", "women's winter RMG", "hosiery jacket"],
    "hindi_transliterated": ["jacket"],
    "examples": ["women's knitted winter jacket", "girls' fleece windcheater"],
    "attributes": {"material": ["knitted fabric", "fleece", "wool blend"], "use": ["winter wear", "outerwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6202"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6202", "reason": "6202 is the same garment type but woven/not-knitted — 6102 is knitted or crocheted only"}, {"excluded_code": "HSN_6101", "reason": "6101 is the equivalent men's/boys' garment — 6102 is women's and girls' only"}],
    "classification_confidence": {"level": "Medium", "rationale": "Women's knitted outerwear is well-defined, but the knitted-vs-woven split decides between chapters 61 and 62.", "ambiguity_triggers": ["woven", "not knitted", "men's", "boys"]},
    "plain_rationale": "HSN 6102 covers women's and girls' knitted or crocheted overcoats, anoraks, windcheaters and similar outerwear. If you make or sell knitted winter jackets for women/girls, this is your code. The identical woven garment falls under HSN 6202 instead. GST is 18%, inferred from the chapter-wide Chapter 61 entry rather than a heading-specific rule, so confirm it with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6102 — women's/girls' knitted overcoats and similar articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6103", "Men's or boys' knitted suits, ensembles, jackets, blazers, trousers, overalls, breeches and shorts", {
    "synonyms": ["men's suit", "knitted blazer", "trousers", "track pants", "boys' shorts"],
    "market_terms": ["knitted formal wear", "men's hosiery bottoms", "knitted trousers RMG"],
    "hindi_transliterated": ["pant", "pyjama"],
    "examples": ["men's knitted jogger trousers", "boys' knitted shorts", "knitted blazer set"],
    "attributes": {"material": ["knitted fabric"], "use": ["formal wear", "casual wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6203"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6203", "reason": "6203 is the same garment category but woven/not-knitted"}, {"excluded_code": "HSN_6112", "reason": "6112 is specifically tracksuits, ski suits and swimwear — not general trousers/suits"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; knitted-vs-woven decides the chapter.", "ambiguity_triggers": ["woven", "not knitted", "tracksuit", "swimwear"]},
    "plain_rationale": "HSN 6103 covers men's and boys' knitted suits, blazers, trousers, overalls, breeches and shorts (not swimwear). If your product is knitted/stretch fabric, use this code; the woven equivalent is HSN 6203. GST is 18%, inferred from the chapter-wide entry, so confirm with your CA — garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6103 — men's/boys' knitted suits, trousers and similar. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6104", "Women's or girls' knitted suits, ensembles, dresses, skirts, trousers, overalls, breeches and shorts", {
    "synonyms": ["women's dress", "knitted skirt", "ladies trousers", "knitted ensemble", "girls' shorts"],
    "market_terms": ["knitted women's wear", "hosiery bottoms", "knitted dress RMG"],
    "hindi_transliterated": [],
    "examples": ["women's knitted dress", "girls' knitted skirt", "ladies' knitted trousers"],
    "attributes": {"material": ["knitted fabric"], "use": ["formal wear", "casual wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6204"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6204", "reason": "6204 is the same garment category but woven/not-knitted"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; knitted-vs-woven decides the chapter.", "ambiguity_triggers": ["woven", "not knitted"]},
    "plain_rationale": "HSN 6104 covers women's and girls' knitted suits, dresses, skirts, trousers, overalls, breeches and shorts (not swimwear). If your product is knitted/stretch fabric, use this code; the woven equivalent is HSN 6204. GST is 18%, inferred from the chapter-wide entry, so confirm with your CA — garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6104 — women's/girls' knitted suits, dresses and similar. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6105", "Men's or boys' knitted shirts", {
    "synonyms": ["knitted shirt", "polo shirt", "men's casual shirt", "boys' knit shirt"],
    "market_terms": ["knitted shirting", "polo/collar tee RMG", "hosiery shirts"],
    "hindi_transliterated": [],
    "examples": ["men's knitted polo shirt", "boys' knitted casual shirt"],
    "attributes": {"material": ["knitted fabric", "cotton", "pique"], "use": ["casual wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the shirt knitted (e.g. polo/collar tee) or woven (a formal button-down shirt)?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6205"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6205", "reason": "6205 is a woven men's/boys' shirt — 6105 is knitted only (e.g. polo shirts)"}, {"excluded_code": "HSN_6109", "reason": "6109 is T-shirts/singlets/vests without a collar or buttons — 6105 is shirts specifically"}],
    "classification_confidence": {"level": "Medium", "rationale": "Knitted collared shirts (polos) map to 6105; plain T-shirts belong under 6109 instead, and woven formal shirts under 6205.", "ambiguity_triggers": ["woven", "formal shirt", "t-shirt", "no collar"]},
    "plain_rationale": "HSN 6105 covers men's and boys' knitted shirts, typically polo or collared knit shirts. A plain collarless T-shirt or vest instead falls under HSN 6109, and a woven, non-stretch formal shirt falls under HSN 6205. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6105 — men's/boys' knitted shirts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6106", "Women's or girls' knitted blouses, shirts and shirt-blouses", {
    "synonyms": ["knitted blouse", "women's knit top", "shirt-blouse", "girls' knit shirt"],
    "market_terms": ["knitted womenswear tops", "hosiery blouse", "knit top RMG"],
    "hindi_transliterated": [],
    "examples": ["women's knitted blouse", "girls' knit shirt-blouse"],
    "attributes": {"material": ["knitted fabric"], "use": ["casual wear", "formal wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the blouse/shirt knitted (stretch) or woven (non-stretch)?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6206"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6206", "reason": "6206 covers the same garment category but woven, non-stretch fabric — 6106 is knitted or crocheted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment type is clear; the knitted-vs-woven fabric split decides the chapter.", "ambiguity_triggers": ["woven", "non-stretch"]},
    "plain_rationale": "HSN 6106 covers women's and girls' knitted blouses, shirts and shirt-blouses. If the fabric is knitted/stretchy, use this code; a woven equivalent falls under HSN 6206 instead. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6106 — women's/girls' knitted blouses and shirt-blouses. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6107", "Men's or boys' knitted underpants, briefs, nightshirts, pyjamas, bathrobes and dressing gowns", {
    "synonyms": ["men's underwear", "briefs", "pyjama set", "bathrobe", "nightshirt"],
    "market_terms": ["knitted innerwear", "men's hosiery underwear", "nightwear RMG"],
    "hindi_transliterated": ["pyjama", "jangiya"],
    "examples": ["men's cotton knitted briefs pack", "knitted pyjama set for men"],
    "attributes": {"material": ["knitted fabric", "cotton"], "use": ["innerwear", "nightwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6207"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6207", "reason": "6207 is the same garment category but woven/not-knitted"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; knitted-vs-woven decides the chapter.", "ambiguity_triggers": ["woven", "not knitted"]},
    "plain_rationale": "HSN 6107 covers men's and boys' knitted underwear, nightshirts, pyjamas, bathrobes and dressing gowns. If the fabric is knitted, use this code; the woven equivalent is HSN 6207. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6107 — men's/boys' knitted underwear and nightwear. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6108", "Women's or girls' knitted slips, petticoats, briefs, panties, nightdresses, negligees, bathrobes and dressing gowns", {
    "synonyms": ["women's underwear", "panties", "nightdress", "petticoat", "bathrobe"],
    "market_terms": ["knitted innerwear", "women's hosiery underwear", "nightwear RMG"],
    "hindi_transliterated": ["nighty"],
    "examples": ["women's cotton knitted panties pack", "knitted nightdress for women"],
    "attributes": {"material": ["knitted fabric", "cotton"], "use": ["innerwear", "nightwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6208"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6208", "reason": "6208 is the same garment category but woven/not-knitted"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; knitted-vs-woven decides the chapter.", "ambiguity_triggers": ["woven", "not knitted"]},
    "plain_rationale": "HSN 6108 covers women's and girls' knitted slips, petticoats, briefs, panties, nightdresses, negligees, bathrobes and dressing gowns. If the fabric is knitted, use this code; the woven equivalent is HSN 6208. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6108 — women's/girls' knitted underwear and nightwear. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6109", "T-shirts, singlets and other vests, knitted or crocheted", {
    "synonyms": ["T-shirt", "tee shirt", "round neck tee", "singlet", "knitted vest", "cotton tee"],
    "market_terms": ["knitted readymade garment", "knitted RMG", "hosiery vest", "jersey tops"],
    "hindi_transliterated": ["baniyan", "ganjee"],
    "examples": ["plain white cotton T-shirt sold at ₹150", "printed round-neck tee", "polyester sports vest"],
    "attributes": {"material": ["cotton", "polyester", "knitted fabric", "jersey"], "use": ["casual wear", "sportswear", "innerwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel", "hosiery"]},
    "clarification_questions": [{"question": "Is the fabric knitted (stretchy) or woven (non-stretch)?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6206", "HSN_6211"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6206", "reason": "6206 covers woven blouses/shirts — use 6109 only for knitted, stretchy T-shirts/vests"}, {"excluded_code": "HSN_6211", "reason": "6211 covers tracksuits and swimwear — 6109 is for plain T-shirts and vests"}, {"excluded_code": "HSN_6105", "reason": "6105 is a shirt (with collar/buttons) — 6109 is collarless T-shirts, singlets and vests"}],
    "classification_confidence": {"level": "Medium", "rationale": "T-shirt is a common term but the knitted-versus-woven distinction decides between chapters.", "ambiguity_triggers": ["shirt", "top", "blouse", "woven", "cotton shirt"]},
    "plain_rationale": "HSN 6109 covers T-shirts, vests and singlets made from knitted or crocheted fabric — plain or printed round-neck tees, polo-free casual tees, and sports vests. GST is 18%, inferred from the chapter-wide entry, but drops to 5% if the garment sells at ₹2,500 or less per piece — confirm the rate with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6109 — T-shirts, singlets and other vests, knitted or crocheted. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6110", "Jerseys, pullovers, cardigans, waistcoats and similar articles, knitted or crocheted", {
    "synonyms": ["sweater", "pullover", "cardigan", "jersey", "knitted waistcoat"],
    "market_terms": ["knitwear", "winter knitwear RMG", "sweater manufacturing"],
    "hindi_transliterated": ["sweater"],
    "examples": ["woollen pullover for winter", "knitted cardigan with buttons", "sleeveless knitted waistcoat"],
    "attributes": {"material": ["wool", "acrylic", "knitted fabric"], "use": ["winter wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel", "hosiery"]},
    "clarification_questions": [],
    "exclusion_notes": [{"excluded_code": "HSN_6101", "reason": "6101 is a knitted overcoat/jacket (outerwear) — 6110 is jerseys, pullovers, cardigans and waistcoats worn as mid-layers"}],
    "classification_confidence": {"level": "High", "rationale": "Sweaters, pullovers and cardigans are inherently knitted garments with no woven equivalent heading, so 6110 applies unambiguously.", "ambiguity_triggers": ["overcoat", "jacket"]},
    "plain_rationale": "HSN 6110 covers jerseys, pullovers, cardigans, waistcoats and similar knitted garments — sweaters and cardigans are almost always knitted, so there's no separate woven-fabric equivalent heading. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6110 — jerseys, pullovers, cardigans and waistcoats, knitted. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6111", "Babies' garments and clothing accessories, knitted or crocheted", {
    "synonyms": ["baby clothes", "infant garment", "knitted baby wear", "romper"],
    "market_terms": ["infant apparel RMG", "baby hosiery wear", "newborn clothing trade"],
    "hindi_transliterated": [],
    "examples": ["knitted baby romper", "infant knitted cap and mitten set"],
    "attributes": {"material": ["knitted fabric", "cotton"], "use": ["infant wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6209"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6209", "reason": "6209 is the same baby-garment category but woven/not-knitted"}],
    "classification_confidence": {"level": "Medium", "rationale": "Baby garments map clearly to this category; knitted-vs-woven decides the chapter.", "ambiguity_triggers": ["woven", "not knitted"]},
    "plain_rationale": "HSN 6111 covers babies' garments and clothing accessories made of knitted or crocheted fabric — rompers, knitted caps, mittens and similar infant wear. The woven equivalent is HSN 6209. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6111 — babies' knitted garments and clothing accessories. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6112", "Track suits, ski suits and swimwear, knitted or crocheted", {
    "synonyms": ["tracksuit", "swimwear", "swimsuit", "ski suit", "knitted sportswear"],
    "market_terms": ["athleisure RMG", "sportswear manufacturing", "swimwear brand"],
    "hindi_transliterated": [],
    "examples": ["knitted tracksuit set", "swimsuit for women", "kids' swimming costume"],
    "attributes": {"material": ["knitted fabric", "lycra/spandex blend"], "use": ["sportswear", "swimming"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel", "sportswear"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/non-stretch?", "attribute": "material", "options": ["Knitted", "Woven"], "disambiguates_from": ["HSN_6211"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6211", "reason": "6211 is the same category (tracksuits, ski suits, swimwear) but woven/not-knitted"}, {"excluded_code": "HSN_6109", "reason": "6109 is a plain T-shirt/vest — 6112 is specifically tracksuits, ski suits and swimwear"}],
    "classification_confidence": {"level": "Medium", "rationale": "Tracksuits and swimwear map clearly to this category; knitted-vs-woven decides the chapter.", "ambiguity_triggers": ["woven", "T-shirt"]},
    "plain_rationale": "HSN 6112 covers knitted track suits, ski suits and swimwear. If the fabric is knitted/stretch (typical for sportswear and swimwear), use this code; the woven equivalent is HSN 6211. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6112 — knitted track suits, ski suits and swimwear. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6114", "Other garments, knitted or crocheted", {
    "synonyms": ["knitted garment (other)", "specialty knitted clothing", "miscellaneous knitwear", "unclassified knitted garment"],
    "market_terms": ["knitted apparel (residual category)", "specialty knitwear trade", "custom knitted garment"],
    "hindi_transliterated": [],
    "examples": ["knitted costume garment not covered by a specific heading", "specialty knitted workwear"],
    "attributes": {"material": ["knitted fabric"], "use": ["specialty wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [],
    "exclusion_notes": [{"excluded_code": "HSN_6211", "reason": "6211 is the woven 'other garments' catch-all — 6114 is the knitted equivalent; use the specific heading (6101-6112) first if your garment fits one"}],
    "classification_confidence": {"level": "Low", "rationale": "This is a residual 'other' heading for knitted garments that don't fit any specific heading (6101-6112); the plain description alone doesn't confirm the fit.", "ambiguity_triggers": ["shirt", "trouser", "jacket", "T-shirt"]},
    "plain_rationale": "HSN 6114 is a residual heading for knitted or crocheted garments that don't fit any of the specific categories in this chapter (overcoats, suits, shirts, T-shirts, sweaters, etc.) — check those first. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6114 — other knitted or crocheted garments. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6115", "Panty hose, tights, stockings, socks and other hosiery, knitted or crocheted", {
    "synonyms": ["socks", "stockings", "tights", "panty hose", "compression stockings"],
    "market_terms": ["hosiery manufacturing", "sock RMG", "compression hosiery"],
    "hindi_transliterated": ["mojaa"],
    "examples": ["pair of cotton socks", "women's tights", "compression stockings for varicose veins"],
    "attributes": {"material": ["knitted fabric", "cotton", "nylon"], "use": ["legwear", "medical support"], "form": ["readymade garment"], "industry": ["textiles", "garments", "hosiery"]},
    "clarification_questions": [],
    "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Socks, stockings and tights are structurally always knitted; there is no woven equivalent heading, so 6115 applies unambiguously.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 6115 covers panty hose, tights, stockings, socks and other hosiery, including compression stockings, made of knitted or crocheted fabric — this category is inherently knitted, with no separate woven heading. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6115 — knitted hosiery: panty hose, tights, stockings and socks. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6116", "Gloves, mittens and mitts, knitted or crocheted", {
    "synonyms": ["knitted gloves", "mittens", "woollen gloves", "hand gloves"],
    "market_terms": ["knitted glove manufacturing", "winter gloves RMG", "hosiery gloves trade"],
    "hindi_transliterated": ["dastane"],
    "examples": ["woollen knitted gloves for winter", "kids' knitted mittens"],
    "attributes": {"material": ["knitted fabric", "wool"], "use": ["winter wear", "hand protection"], "form": ["readymade garment"], "industry": ["textiles", "garments", "hosiery"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/leather?", "attribute": "material", "options": ["Knitted", "Woven/leather/other"], "disambiguates_from": ["HSN_6216"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6216", "reason": "6216 is the same product but woven/not-knitted (or of other material) — 6116 is knitted or crocheted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "Gloves map clearly to this category; knitted-vs-not-knitted decides the chapter.", "ambiguity_triggers": ["woven", "leather"]},
    "plain_rationale": "HSN 6116 covers knitted or crocheted gloves, mittens and mitts. If the fabric is knitted, use this code; the not-knitted equivalent is HSN 6216. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6116 — knitted gloves, mittens and mitts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add61("HSN_6117", "Other made up clothing accessories, knitted or crocheted; knitted or crocheted parts of garments", {
    "synonyms": ["knitted scarf", "knitted headband", "clothing accessory (knitted)", "garment trim"],
    "market_terms": ["knitted accessory manufacturing", "garment parts/trims", "knit trim supply"],
    "hindi_transliterated": [],
    "examples": ["knitted headband or beanie", "knitted collar/cuff parts sold to garment makers"],
    "attributes": {"material": ["knitted fabric"], "use": ["accessory"], "form": ["readymade accessory", "garment part"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [],
    "exclusion_notes": [{"excluded_code": "HSN_6217", "reason": "6217 is the woven/not-knitted equivalent — 6117 is knitted or crocheted accessories and garment parts"}],
    "classification_confidence": {"level": "Medium", "rationale": "This is a residual accessories/parts heading; the specific item and its knitted construction both need confirming.", "ambiguity_triggers": ["woven", "scarf (woven)", "tie"]},
    "plain_rationale": "HSN 6117 covers other knitted or crocheted clothing accessories not covered elsewhere (like knitted headbands or beanies) and knitted parts of garments (collars, cuffs) sold separately to garment makers. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 61, Heading 6117 — other knitted clothing accessories and garment parts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

# =====================================================================
# CHAPTER 62 — apparel not knitted or crocheted (woven)
# =====================================================================

add62("HSN_6201", "Men's or boys' overcoats, car-coats, capes, cloaks, anoraks, wind-cheaters and similar articles, not knitted", {
    "synonyms": ["men's woven jacket", "overcoat", "windcheater (woven)", "raincoat"],
    "market_terms": ["woven outerwear", "men's winter woven RMG", "woven jacket trade"],
    "hindi_transliterated": [],
    "examples": ["men's woven winter overcoat", "woven raincoat/windcheater"],
    "attributes": {"material": ["woven fabric", "polyester", "cotton"], "use": ["winter wear", "outerwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6101"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6101", "reason": "6101 is the same garment type but knitted or crocheted — 6201 is woven/not-knitted only"}, {"excluded_code": "HSN_6202", "reason": "6202 is the equivalent women's/girls' garment"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; woven-vs-knitted decides the chapter.", "ambiguity_triggers": ["knitted", "stretchy"]},
    "plain_rationale": "HSN 6201 covers men's and boys' woven (not knitted) overcoats, anoraks, windcheaters and similar outerwear. The knitted equivalent is HSN 6101. GST is 18%, inferred from the chapter-wide Chapter 62 entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6201 — men's/boys' woven overcoats and similar articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6202", "Women's or girls' overcoats, car-coats, capes, cloaks, anoraks, wind-cheaters and similar articles, not knitted", {
    "synonyms": ["women's woven jacket", "overcoat", "ladies raincoat", "woven windcheater"],
    "market_terms": ["woven outerwear", "women's winter woven RMG", "woven jacket trade"],
    "hindi_transliterated": [],
    "examples": ["women's woven winter overcoat", "woven raincoat for girls"],
    "attributes": {"material": ["woven fabric", "polyester", "cotton"], "use": ["winter wear", "outerwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6102"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6102", "reason": "6102 is the same garment type but knitted or crocheted — 6202 is woven/not-knitted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; woven-vs-knitted decides the chapter.", "ambiguity_triggers": ["knitted", "stretchy"]},
    "plain_rationale": "HSN 6202 covers women's and girls' woven (not knitted) overcoats, anoraks, windcheaters and similar outerwear. The knitted equivalent is HSN 6102. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6202 — women's/girls' woven overcoats and similar articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6203", "Men's or boys' suits, ensembles, jackets, blazers, trousers, overalls, breeches and shorts, not knitted", {
    "synonyms": ["men's formal suit", "blazer", "woven trousers", "formal pant", "boys' shorts"],
    "market_terms": ["woven formal wear", "men's woven bottoms", "suiting fabric garments"],
    "hindi_transliterated": ["pant"],
    "examples": ["men's woven formal trousers", "boys' woven shorts", "suit-and-blazer set"],
    "attributes": {"material": ["woven fabric", "suiting cloth"], "use": ["formal wear", "casual wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6103"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6103", "reason": "6103 is the same garment category but knitted or crocheted — 6203 is woven/not-knitted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; woven-vs-knitted decides the chapter.", "ambiguity_triggers": ["knitted", "stretchy"]},
    "plain_rationale": "HSN 6203 covers men's and boys' woven suits, blazers, trousers, overalls, breeches and shorts (not swimwear). The knitted equivalent is HSN 6103. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6203 — men's/boys' woven suits, trousers and similar. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6204", "Women's or girls' suits, dresses, skirts, trousers, overalls and shorts, not knitted", {
    "synonyms": ["women's woven dress", "skirt", "woven trousers", "formal suit (women's)", "girls' shorts"],
    "market_terms": ["woven womenswear", "women's suiting garments", "formal dress RMG"],
    "hindi_transliterated": [],
    "examples": ["women's woven formal dress", "woven pleated skirt", "ladies' woven trousers"],
    "attributes": {"material": ["woven fabric"], "use": ["formal wear", "casual wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6104"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6104", "reason": "6104 is the same garment category but knitted or crocheted — 6204 is woven/not-knitted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; woven-vs-knitted decides the chapter.", "ambiguity_triggers": ["knitted", "stretchy"]},
    "plain_rationale": "HSN 6204 covers women's and girls' woven suits, dresses, skirts, trousers, overalls, breeches and shorts (not swimwear). The knitted equivalent is HSN 6104. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6204 — women's/girls' woven suits, dresses and similar. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6205", "Men's or boys' shirts, not knitted", {
    "synonyms": ["formal shirt", "woven shirt", "men's button-down shirt", "office shirt"],
    "market_terms": ["woven shirting", "formal shirt RMG", "corporate shirting fabric garments"],
    "hindi_transliterated": [],
    "examples": ["men's formal woven cotton shirt", "boys' woven checked shirt"],
    "attributes": {"material": ["woven fabric", "cotton", "poly-cotton"], "use": ["formal wear", "office wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the shirt woven/non-stretch (formal button-down) or knitted (polo)?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6105"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6105", "reason": "6105 is a knitted shirt (e.g. polo) — 6205 is a woven, non-stretch button-down shirt"}],
    "classification_confidence": {"level": "Medium", "rationale": "Formal woven shirts map clearly here; knitted polo-style shirts belong under 6105 instead.", "ambiguity_triggers": ["polo", "knitted", "T-shirt"]},
    "plain_rationale": "HSN 6205 covers men's and boys' woven, non-stretch shirts — the typical formal button-down office shirt. A knitted polo shirt instead falls under HSN 6105. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6205 — men's/boys' woven shirts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6206", "Women's or girls' blouses, shirts and shirt-blouses, not knitted", {
    "synonyms": ["woven blouse", "women's formal shirt", "shirt-blouse", "girls' woven top"],
    "market_terms": ["woven womenswear tops", "formal blouse RMG", "shirt-blouse trade"],
    "hindi_transliterated": [],
    "examples": ["women's woven formal blouse", "girls' woven shirt-blouse"],
    "attributes": {"material": ["woven fabric"], "use": ["formal wear", "casual wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6106", "HSN_6109"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6106", "reason": "6106 is the same garment category but knitted or crocheted — 6206 is woven/not-knitted only"}, {"excluded_code": "HSN_6109", "reason": "6109 is a knitted T-shirt/vest, not a woven blouse or shirt"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment type is clear; the woven-vs-knitted fabric split decides the chapter.", "ambiguity_triggers": ["knitted", "stretchy", "T-shirt"]},
    "plain_rationale": "HSN 6206 covers women's and girls' woven blouses, shirts and shirt-blouses. If the fabric is non-stretch/woven, use this code; the knitted equivalent is HSN 6106. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6206 — women's/girls' woven blouses and shirt-blouses. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6207", "Men's or boys' singlets, vests, underpants, briefs, nightshirts, pyjamas, bathrobes and dressing gowns, not knitted", {
    "synonyms": ["men's woven underwear", "woven briefs", "pyjama set (woven)", "bathrobe"],
    "market_terms": ["woven innerwear", "men's woven nightwear RMG", "woven underwear trade"],
    "hindi_transliterated": ["pyjama"],
    "examples": ["men's woven pyjama set", "woven bathrobe"],
    "attributes": {"material": ["woven fabric", "cotton"], "use": ["innerwear", "nightwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6107"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6107", "reason": "6107 is the same garment category but knitted or crocheted — 6207 is woven/not-knitted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; woven-vs-knitted decides the chapter.", "ambiguity_triggers": ["knitted"]},
    "plain_rationale": "HSN 6207 covers men's and boys' woven underwear, nightshirts, pyjamas, bathrobes and dressing gowns. The knitted equivalent is HSN 6107. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6207 — men's/boys' woven underwear and nightwear. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6208", "Women's or girls' slips, petticoats, panties, nightdresses, negligees and dressing gowns, not knitted", {
    "synonyms": ["women's woven underwear", "woven petticoat", "nightdress (woven)", "bathrobe"],
    "market_terms": ["woven innerwear", "women's woven nightwear RMG", "woven underwear trade"],
    "hindi_transliterated": ["nighty"],
    "examples": ["women's woven petticoat", "woven nightdress"],
    "attributes": {"material": ["woven fabric", "cotton"], "use": ["innerwear", "nightwear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6108"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6108", "reason": "6108 is the same garment category but knitted or crocheted — 6208 is woven/not-knitted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "The garment category is clear; woven-vs-knitted decides the chapter.", "ambiguity_triggers": ["knitted"]},
    "plain_rationale": "HSN 6208 covers women's and girls' woven underwear, nightdresses, negligees, bathrobes and dressing gowns. The knitted equivalent is HSN 6108. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6208 — women's/girls' woven underwear and nightwear. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6209", "Babies' garments and clothing accessories, not knitted", {
    "synonyms": ["baby clothes (woven)", "infant garment", "woven baby wear", "romper (woven)"],
    "market_terms": ["infant apparel RMG (woven)", "woven baby wear trade", "newborn clothing trade"],
    "hindi_transliterated": [],
    "examples": ["woven baby romper", "infant woven cap set"],
    "attributes": {"material": ["woven fabric", "cotton"], "use": ["infant wear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6111"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6111", "reason": "6111 is the same baby-garment category but knitted or crocheted — 6209 is woven/not-knitted only"}],
    "classification_confidence": {"level": "Medium", "rationale": "Baby garments map clearly to this category; woven-vs-knitted decides the chapter.", "ambiguity_triggers": ["knitted"]},
    "plain_rationale": "HSN 6209 covers babies' garments and clothing accessories made of woven (not knitted) fabric. The knitted equivalent is HSN 6111. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6209 — babies' woven garments and clothing accessories. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6210", "Garments made up of fabrics of heading 56.02, 56.03, 59.03, 59.06 or 59.07", {
    "synonyms": ["non-woven garment", "coated fabric garment", "rubberised raincoat", "PVC coat"],
    "market_terms": ["technical textile garment", "coated/laminated fabric apparel", "non-woven protective wear"],
    "hindi_transliterated": [],
    "examples": ["PVC-coated rain-cape", "rubberised protective coverall", "non-woven disposable coverall garment"],
    "attributes": {"material": ["non-woven fabric", "coated fabric", "laminated fabric"], "use": ["protective wear", "rainwear"], "form": ["readymade garment"], "industry": ["textiles", "industrial safety", "apparel"]},
    "clarification_questions": [],
    "exclusion_notes": [{"excluded_code": "HSN_6211", "reason": "6211 is ordinary woven fabric garments — 6210 is specifically for garments made of felt, non-woven, rubberised/coated, or impregnated/laminated fabric"}],
    "classification_confidence": {"level": "Medium", "rationale": "This heading is defined by the specific fabric type (felt, non-wovens, rubberised/coated, or impregnated textile fabrics), which needs to be confirmed against a plain garment description.", "ambiguity_triggers": ["plain cotton", "knitted", "ordinary woven fabric"]},
    "plain_rationale": "HSN 6210 covers garments made from special fabrics — felt, non-wovens, rubberised or plastic-coated textile fabric, or impregnated/laminated fabric — rather than ordinary woven or knitted cloth. Typical examples are PVC rain-capes and disposable non-woven coveralls. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6210 — garments of felt, non-woven, or coated/laminated fabrics. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6211", "Track suits, ski suits and swimwear; other garments, not knitted", {
    "synonyms": ["woven tracksuit", "woven swimwear", "ski suit", "woven costume/other garment"],
    "market_terms": ["woven athleisure", "woven sportswear RMG", "woven swimwear trade"],
    "hindi_transliterated": [],
    "examples": ["woven tracksuit set", "woven board shorts/swim trunks"],
    "attributes": {"material": ["woven fabric"], "use": ["sportswear", "swimming"], "form": ["readymade garment"], "industry": ["textiles", "garments", "apparel", "sportswear"]},
    "clarification_questions": [{"question": "Is the fabric woven/non-stretch or knitted/stretchy?", "attribute": "material", "options": ["Woven", "Knitted"], "disambiguates_from": ["HSN_6112"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6112", "reason": "6112 is the same category (tracksuits, ski suits, swimwear) but knitted or crocheted — 6211 is woven/not-knitted only"}, {"excluded_code": "HSN_6109", "reason": "6109 is a plain T-shirt/vest, not tracksuits or swimwear"}],
    "classification_confidence": {"level": "Medium", "rationale": "Tracksuits/swimwear map clearly to this category; woven-vs-knitted decides the chapter, and it also acts as a general 'other garments' catch-all for chapter 62.", "ambiguity_triggers": ["knitted"]},
    "plain_rationale": "HSN 6211 covers woven track suits, ski suits and swimwear, plus other woven garments not covered elsewhere in Chapter 62. The knitted equivalent (6112) applies if the fabric is stretchy/knitted instead. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Garments at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6211 — woven track suits, ski suits, swimwear and other garments. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6212", "Brassieres, girdles, corsets, braces, suspenders and garters, knitted or not", {
    "synonyms": ["bra", "brassiere", "girdle", "corset", "suspender belt"],
    "market_terms": ["shapewear manufacturing", "lingerie RMG", "foundation garments"],
    "hindi_transliterated": [],
    "examples": ["women's bra", "shapewear/girdle", "suspender belt"],
    "attributes": {"material": ["knitted or woven fabric", "elastic"], "use": ["innerwear", "shapewear"], "form": ["readymade garment"], "industry": ["textiles", "garments", "lingerie"]},
    "clarification_questions": [],
    "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "This single heading explicitly covers both knitted and woven construction, so there is no knit/woven ambiguity to resolve unlike most of this chapter.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 6212 covers brassieres, girdles, corsets, braces, suspenders, garters and similar shaping/support garments and their parts — unusually, this single code applies whether the item is knitted or woven, so there's no fabric-type split to worry about here. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6212 — brassieres, girdles, corsets and similar articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6213", "Handkerchiefs", {
    "synonyms": ["handkerchief", "hanky", "pocket square", "rumaal"],
    "market_terms": ["handkerchief manufacturing", "textile accessory trade", "hanky wholesale"],
    "hindi_transliterated": ["rumaal"],
    "examples": ["cotton handkerchief pack", "embroidered pocket square"],
    "attributes": {"material": ["cotton", "woven fabric"], "use": ["personal accessory"], "form": ["readymade accessory"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [],
    "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Handkerchiefs map uniquely to this single heading with no knit/woven split.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 6213 covers handkerchiefs of any textile material. If you make or sell handkerchiefs, this is your code. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6213 — handkerchiefs. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6214", "Shawls, scarves, mufflers, mantillas, veils and the like", {
    "synonyms": ["shawl", "scarf", "muffler", "stole", "veil"],
    "market_terms": ["shawl/scarf manufacturing", "stole trade", "winter accessory RMG"],
    "hindi_transliterated": ["dupatta", "chunni"],
    "examples": ["woollen shawl for winter", "printed cotton scarf", "muffler set"],
    "attributes": {"material": ["wool", "cotton", "silk"], "use": ["winter wear", "fashion accessory"], "form": ["readymade accessory"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [],
    "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Shawls, scarves and mufflers map uniquely to this single heading regardless of knit/woven construction.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 6214 covers shawls, scarves, mufflers, mantillas, veils and similar items of any textile material. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6214 — shawls, scarves, mufflers and veils. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6215", "Ties, bow ties and cravats", {
    "synonyms": ["necktie", "bow tie", "cravat", "silk tie"],
    "market_terms": ["necktie manufacturing", "formal accessory trade", "tie wholesale"],
    "hindi_transliterated": [],
    "examples": ["silk necktie", "bow tie for formal wear"],
    "attributes": {"material": ["silk", "polyester", "woven fabric"], "use": ["formal wear accessory"], "form": ["readymade accessory"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [],
    "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Ties, bow ties and cravats map uniquely to this single heading.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 6215 covers ties, bow ties and cravats of any textile material. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6215 — ties, bow ties and cravats. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6216", "Gloves, mittens and mitts, not knitted", {
    "synonyms": ["leather gloves", "woven gloves", "work gloves", "driving gloves"],
    "market_terms": ["woven/leather glove manufacturing", "industrial work gloves", "leather glove trade"],
    "hindi_transliterated": ["dastane"],
    "examples": ["leather work gloves", "woven fabric driving gloves"],
    "attributes": {"material": ["woven fabric", "leather"], "use": ["hand protection", "fashion accessory"], "form": ["readymade garment"], "industry": ["textiles", "garments", "industrial safety"]},
    "clarification_questions": [{"question": "Is the fabric knitted/stretchy or woven/leather/other?", "attribute": "material", "options": ["Knitted", "Woven/leather/other"], "disambiguates_from": ["HSN_6116"]}],
    "exclusion_notes": [{"excluded_code": "HSN_6116", "reason": "6116 is the same product but knitted or crocheted — 6216 is woven, leather, or other non-knitted material"}],
    "classification_confidence": {"level": "Medium", "rationale": "Gloves map clearly to this category; knitted-vs-not-knitted decides the chapter.", "ambiguity_triggers": ["knitted"]},
    "plain_rationale": "HSN 6216 covers gloves, mittens and mitts that are not knitted or crocheted — leather, woven fabric, or other materials. The knitted equivalent is HSN 6116. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6216 — gloves, mittens and mitts, not knitted. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add62("HSN_6217", "Other made up clothing accessories; parts of garments or of clothing accessories, not knitted", {
    "synonyms": ["clothing accessory (woven)", "garment trim/lining", "belt", "collar/cuff part"],
    "market_terms": ["garment accessory manufacturing", "trims and linings trade", "woven trim supply"],
    "hindi_transliterated": [],
    "examples": ["fabric belt sold as a clothing accessory", "collar and cuff parts sold to garment makers"],
    "attributes": {"material": ["woven fabric"], "use": ["accessory"], "form": ["readymade accessory", "garment part"], "industry": ["textiles", "garments", "apparel"]},
    "clarification_questions": [],
    "exclusion_notes": [{"excluded_code": "HSN_6117", "reason": "6117 is the knitted or crocheted equivalent — 6217 is woven/not-knitted accessories and garment parts"}, {"excluded_code": "HSN_6212", "reason": "6212 specifically covers braces, suspenders and garters — use 6212 instead of the general 6217 catch-all for those items"}],
    "classification_confidence": {"level": "Low", "rationale": "This is a residual 'other' accessories/parts heading; the specific item needs confirming since several more specific headings (6212, 6117) sit alongside it.", "ambiguity_triggers": ["brace", "suspender", "garter", "knitted"]},
    "plain_rationale": "HSN 6217 covers other woven clothing accessories not covered elsewhere (like fabric belts) and woven parts of garments (collars, cuffs, linings) sold separately. Braces, suspenders and garters have their own more specific code (6212); the knitted equivalent of this heading is 6117. GST is 18%, inferred from the chapter-wide entry — confirm with your CA. Items at ₹2,500 or less per piece attract 5%.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 62, Heading 6217 — other woven clothing accessories and garment parts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})


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
