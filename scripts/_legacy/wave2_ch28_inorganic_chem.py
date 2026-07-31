"""
Wave 2, Chapter 28 (inorganic chemicals; compounds of precious/rare-earth/
radioactive elements) — 48 heading-level records. Same harness as prior waves.

42 of 48 headings share one shape: rate_confidence "low", rate_scope
"chapter", and an identical exception string ("All inorganic chemicals
[other than those specified in notification No.10/2025-Central Tax (Rate)
...]" at 18%). That shared shape is factored into add28() below. The
remaining 6 headings (2807, 2808, 2809, 2814, 2845, 2853) are resolved
cleanly at heading level (medium confidence, no exception) and use plain
add() instead — these are presumably the items actually listed in
Notification 10/2025 that keep the 5% rate.

This chapter is overwhelmingly B2B industrial/specialty chemical trade with
little natural-language ambiguity per compound (each name is chemically
distinct), so records here are intentionally leaner than the consumer-goods
clusters in Wave 1 — 4 synonyms rather than 8, no clarification questions
where the compound name alone is unambiguous.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import load_master, validate, finalize, write_jsonl
from wave1_records import build_record

MASTER = load_master()

CH28_HEADINGS = (
    [f"HSN_28{n:02d}" for n in range(1, 38)]  # 2801-2837
    + [f"HSN_28{n:02d}" for n in range(39, 47)]  # 2839-2846
    + ["HSN_2849", "HSN_2852", "HSN_2853"]
)

CH28_CAVEAT = "Rate inferred from the Chapter 28 entry, not a rule written for this specific heading. Most inorganic chemicals attract 18% except those specifically listed in Notification 10/2025-Central Tax (Rate); verify against that notification before invoicing."
CH28_EXC = [{"gst_rate": 18.0, "condition": "All inorganic chemicals except those specifically listed in Notification 10/2025-Central Tax (Rate) or other schedules of Notification 9/2025"}]

RECORDS = []


def add(mid, title, ai, status="complete", exceptions=None, caveat=None):
    RECORDS.append((mid, CH28_HEADINGS, title, ai, status, exceptions or [], caveat))


def add28(mid, title, ai, **kw):
    add(mid, title, ai, exceptions=CH28_EXC, caveat=CH28_CAVEAT, **kw)


add28("HSN_2801", "Fluorine, chlorine, bromine and iodine", {
    "synonyms": ["chlorine gas", "liquid chlorine", "bromine", "iodine (elemental)"],
    "market_terms": ["halogen gas trade", "industrial chlorine supply", "water treatment chemical trade"],
    "hindi_transliterated": [], "examples": ["liquid chlorine for water treatment", "industrial bromine for chemical synthesis"],
    "attributes": {"material": ["halogen element"], "use": ["water treatment", "chemical synthesis", "disinfection"], "form": ["gas", "liquid"], "industry": ["chemicals", "water treatment"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Each halogen element (fluorine, chlorine, bromine, iodine) is chemically distinct and maps uniquely to 2801.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2801 covers the elemental halogens — fluorine, chlorine, bromine and iodine — commonly traded as industrial gases or liquids for water treatment and chemical manufacturing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2801 — fluorine, chlorine, bromine and iodine. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2802", "Sulphur, sublimed or precipitated; colloidal sulphur", {
    "synonyms": ["sublimed sulphur", "precipitated sulphur", "colloidal sulphur", "flowers of sulphur"],
    "market_terms": ["sulphur trade", "agricultural sulphur supply", "rubber vulcanising agent trade"],
    "hindi_transliterated": ["gandhak"], "examples": ["sublimed sulphur for agricultural fungicide use", "precipitated sulphur for rubber vulcanisation"],
    "attributes": {"material": ["sulphur"], "use": ["agriculture", "rubber manufacturing"], "form": ["powder"], "industry": ["chemicals", "agriculture", "rubber"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Processed sulphur (sublimed, precipitated, colloidal) maps uniquely to 2802.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2802 covers processed sulphur — sublimed, precipitated or colloidal forms — used in agriculture (fungicides) and rubber vulcanisation.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2802 — sublimed/precipitated/colloidal sulphur. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2803", "Carbon (carbon blacks and other forms of carbon not elsewhere specified)", {
    "synonyms": ["carbon black", "activated carbon", "industrial carbon", "amorphous carbon"],
    "market_terms": ["carbon black trade", "tyre/rubber pigment supply", "activated carbon supply"],
    "hindi_transliterated": [], "examples": ["carbon black used as a rubber/tyre pigment and reinforcing filler", "activated carbon for water/air filtration"],
    "attributes": {"material": ["carbon"], "use": ["rubber manufacturing", "filtration", "pigment"], "form": ["powder", "granules"], "industry": ["chemicals", "rubber", "water treatment"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Carbon black and other non-elsewhere-specified carbon forms map uniquely to 2803.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2803 covers carbon black and other forms of carbon not elsewhere specified — used as a rubber/tyre reinforcing pigment and, in activated form, as a filtration medium.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2803 — carbon (carbon blacks and other forms). Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2804", "Hydrogen, rare gases and other non-metals", {
    "synonyms": ["hydrogen gas", "helium", "argon", "industrial nitrogen"],
    "market_terms": ["industrial gas trade", "welding gas supply", "cylinder gas trade"],
    "hindi_transliterated": [], "examples": ["compressed hydrogen gas for industrial use", "argon gas for welding"],
    "attributes": {"material": ["hydrogen", "rare gas"], "use": ["welding", "industrial processing"], "form": ["compressed gas"], "industry": ["chemicals", "industrial gases", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Hydrogen, rare gases (helium, argon, neon etc.) and other non-metal elements map uniquely to 2804.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2804 covers hydrogen, rare gases (like helium and argon) and other elemental non-metals, typically traded as compressed industrial gas.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2804 — hydrogen, rare gases and other non-metals. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2805", "Alkali or alkaline-earth metals; rare-earth metals, scandium and yttrium; mercury", {
    "synonyms": ["sodium metal", "calcium metal", "mercury (elemental)", "rare-earth metal"],
    "market_terms": ["industrial metal trade", "specialty metal supply", "laboratory reagent trade"],
    "hindi_transliterated": ["paara"], "examples": ["metallic sodium for chemical synthesis", "elemental mercury for laboratory/industrial use"],
    "attributes": {"material": ["alkali metal", "alkaline-earth metal", "mercury"], "use": ["chemical synthesis", "laboratory/industrial use"], "form": ["metal", "liquid metal"], "industry": ["chemicals", "specialty metals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Elemental alkali/alkaline-earth/rare-earth metals and mercury map uniquely to 2805.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2805 covers elemental alkali metals (like sodium), alkaline-earth metals (like calcium), rare-earth metals, scandium, yttrium, and elemental mercury.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2805 — alkali/alkaline-earth/rare-earth metals; mercury. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2806", "Hydrogen chloride (hydrochloric acid); chlorosulphuric acid", {
    "synonyms": ["hydrochloric acid", "muriatic acid", "HCl", "chlorosulphuric acid"],
    "market_terms": ["industrial acid trade", "water treatment chemical supply", "metal pickling chemical trade"],
    "hindi_transliterated": [], "examples": ["hydrochloric acid for industrial cleaning/metal pickling", "muriatic acid for pH correction in pools/construction"],
    "attributes": {"material": ["hydrochloric acid"], "use": ["industrial cleaning", "pH correction", "metal treatment"], "form": ["liquid"], "industry": ["chemicals", "construction", "water treatment"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Hydrochloric acid and chlorosulphuric acid map uniquely to 2806.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2806 covers hydrogen chloride (hydrochloric/muriatic acid) and chlorosulphuric acid, widely used for industrial cleaning, metal pickling and pH correction.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2806 — hydrochloric acid and chlorosulphuric acid. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_2807", "Sulphuric acid; oleum", {
    "synonyms": ["sulphuric acid", "oleum", "battery acid", "H2SO4"],
    "market_terms": ["industrial acid trade", "battery acid supply", "fertiliser chemical trade"],
    "hindi_transliterated": [], "examples": ["sulphuric acid for lead-acid battery manufacturing", "oleum for chemical/fertiliser processing"],
    "attributes": {"material": ["sulphuric acid"], "use": ["battery manufacturing", "fertiliser production", "chemical processing"], "form": ["liquid"], "industry": ["chemicals", "automotive", "fertilisers"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sulphuric acid and oleum map uniquely to 2807, cleanly resolved at heading level.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2807 covers sulphuric acid and oleum (fuming sulphuric acid) — key industrial acids used in battery manufacturing, fertiliser production and chemical processing. GST is 5%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2807 — sulphuric acid; oleum. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_2808", "Nitric acid; sulphonitric acids", {
    "synonyms": ["nitric acid", "sulphonitric acid", "HNO3", "aqua fortis"],
    "market_terms": ["industrial acid trade", "fertiliser chemical trade", "explosives raw material trade"],
    "hindi_transliterated": [], "examples": ["nitric acid for fertiliser manufacturing", "nitric acid used in metal etching/refining"],
    "attributes": {"material": ["nitric acid"], "use": ["fertiliser production", "metal treatment"], "form": ["liquid"], "industry": ["chemicals", "fertilisers", "metal processing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Nitric acid and sulphonitric acids map uniquely to 2808, cleanly resolved at heading level.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2808 covers nitric acid and sulphonitric acids, used in fertiliser manufacturing and metal etching/refining. GST is 5%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2808 — nitric acid; sulphonitric acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_2809", "Diphosphorus pentaoxide; phosphoric acid; polyphosphoric acids", {
    "synonyms": ["phosphoric acid", "polyphosphoric acid", "diphosphorus pentaoxide", "orthophosphoric acid"],
    "market_terms": ["fertiliser chemical trade", "food-grade phosphoric acid supply", "industrial acid trade"],
    "hindi_transliterated": [], "examples": ["phosphoric acid for fertiliser production", "food-grade phosphoric acid used as a soft-drink acidulant"],
    "attributes": {"material": ["phosphoric acid"], "use": ["fertiliser production", "food processing"], "form": ["liquid"], "industry": ["chemicals", "fertilisers", "food processing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Phosphoric acid and related phosphorus oxyacids map uniquely to 2809, cleanly resolved at heading level.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2809 covers diphosphorus pentaoxide, phosphoric acid and polyphosphoric acids, used in fertiliser manufacturing and (food-grade) as a soft-drink acidulant. GST is 5%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2809 — phosphoric acid and related compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2810", "Oxides of boron; boric acids", {
    "synonyms": ["boric acid", "boric oxide", "boron trioxide", "orthoboric acid"],
    "market_terms": ["industrial chemical trade", "boric acid supply", "glass raw material trade"],
    "hindi_transliterated": [], "examples": ["boric acid for antiseptic/industrial use", "boron oxide for glass manufacturing"],
    "attributes": {"material": ["boron oxide", "boric acid"], "use": ["glass manufacturing", "industrial/antiseptic use"], "form": ["powder", "crystal"], "industry": ["chemicals", "glass"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Boron oxides and boric acids map uniquely to 2810.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2810 covers oxides of boron and boric acids, used in glass manufacturing and industrial/antiseptic applications.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2810 — boron oxides; boric acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2811", "Other inorganic acids and other inorganic oxygen compounds of non-metals", {
    "synonyms": ["silicic acid", "selenious acid", "other inorganic acid", "non-metal oxyacid"],
    "market_terms": ["specialty inorganic chemical trade", "industrial acid supply", "laboratory chemical trade"],
    "hindi_transliterated": [], "examples": ["silicic acid used in industrial silica gel manufacturing", "selenious acid used in specialty chemical synthesis"],
    "attributes": {"material": ["inorganic acid"], "use": ["specialty chemical manufacturing"], "form": ["liquid", "powder"], "industry": ["chemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "This is a specific, chemically-defined residual heading for non-metal oxyacids not covered by the named acid headings above.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2811 covers other inorganic acids and inorganic oxygen compounds of non-metals not covered by the named acid headings (sulphuric, nitric, phosphoric) elsewhere in this chapter.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2811 — other inorganic acids/oxygen compounds of non-metals. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2812", "Halides and halide oxides of non-metals", {
    "synonyms": ["phosphorus trichloride", "sulphur hexafluoride", "silicon tetrachloride", "non-metal halide"],
    "market_terms": ["specialty chemical trade", "industrial halide supply", "semiconductor gas trade"],
    "hindi_transliterated": [], "examples": ["phosphorus trichloride used in chemical synthesis", "sulphur hexafluoride (SF6) used as an electrical insulating gas"],
    "attributes": {"material": ["non-metal halide"], "use": ["chemical synthesis", "electrical insulation", "semiconductor processing"], "form": ["gas", "liquid"], "industry": ["chemicals", "electronics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Halides and halide oxides of non-metals map uniquely to 2812.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2812 covers halides and halide oxides of non-metals — specialty chemicals like phosphorus trichloride and sulphur hexafluoride, used in chemical synthesis and electronics.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2812 — halides/halide oxides of non-metals. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2813", "Sulphides of non-metals; commercial phosphorus trisulphide", {
    "synonyms": ["carbon disulphide", "phosphorus trisulphide", "diphosphorus pentasulphide", "non-metal sulphide"],
    "market_terms": ["specialty chemical trade", "industrial sulphide supply", "match manufacturing raw material trade"],
    "hindi_transliterated": [], "examples": ["carbon disulphide used in rayon/viscose fibre manufacturing", "phosphorus trisulphide used in match-head manufacturing"],
    "attributes": {"material": ["non-metal sulphide"], "use": ["fibre manufacturing", "match manufacturing"], "form": ["liquid", "solid"], "industry": ["chemicals", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sulphides of non-metals and commercial phosphorus trisulphide map uniquely to 2813.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2813 covers sulphides of non-metals, including commercial phosphorus trisulphide — used in viscose/rayon fibre production and match manufacturing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2813 — sulphides of non-metals. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_2814", "Ammonia, anhydrous or in aqueous solution", {
    "synonyms": ["ammonia", "liquid ammonia", "aqueous ammonia", "anhydrous ammonia"],
    "market_terms": ["fertiliser raw material trade", "industrial ammonia supply", "refrigerant gas trade"],
    "hindi_transliterated": [], "examples": ["anhydrous ammonia for fertiliser manufacturing", "aqueous ammonia (ammonia solution) for industrial cleaning"],
    "attributes": {"material": ["ammonia"], "use": ["fertiliser production", "industrial cleaning", "refrigeration"], "form": ["gas", "liquid solution"], "industry": ["chemicals", "fertilisers"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Ammonia (anhydrous or aqueous) maps uniquely to 2814, cleanly resolved at heading level.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2814 covers ammonia, whether anhydrous (pure gas/liquid) or as an aqueous solution — a key fertiliser raw material also used in industrial cleaning and refrigeration. GST is 5%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2814 — ammonia. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2815", "Sodium hydroxide (caustic soda); potassium hydroxide (caustic potash); peroxides of sodium or potassium", {
    "synonyms": ["caustic soda", "sodium hydroxide", "caustic potash", "NaOH"],
    "market_terms": ["soap/detergent raw material trade", "caustic soda supply", "industrial alkali trade"],
    "hindi_transliterated": [], "examples": ["caustic soda flakes for soap manufacturing", "sodium hydroxide solution for industrial cleaning"],
    "attributes": {"material": ["caustic soda", "caustic potash"], "use": ["soap/detergent manufacturing", "industrial cleaning", "pH control"], "form": ["flakes", "solution", "pellets"], "industry": ["chemicals", "soap/detergent manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Caustic soda and caustic potash map uniquely to 2815.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2815 covers caustic soda (sodium hydroxide), caustic potash (potassium hydroxide), and their peroxides — a widely used industrial alkali, especially for soap and detergent manufacturing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2815 — caustic soda/potash and their peroxides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2816", "Hydroxide and peroxide of magnesium; oxides, hydroxides and peroxides of strontium or barium", {
    "synonyms": ["magnesium hydroxide", "milk of magnesia raw material", "barium oxide", "strontium oxide"],
    "market_terms": ["specialty inorganic chemical trade", "pharma raw material trade", "industrial oxide supply"],
    "hindi_transliterated": [], "examples": ["magnesium hydroxide used as an antacid raw material", "barium oxide for industrial use"],
    "attributes": {"material": ["magnesium hydroxide", "barium/strontium compounds"], "use": ["pharma raw material", "industrial use"], "form": ["powder"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "These specific magnesium/strontium/barium compounds map uniquely to 2816.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2816 covers magnesium hydroxide/peroxide and the oxides, hydroxides and peroxides of strontium or barium — magnesium hydroxide is a common antacid raw material.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2816 — magnesium/strontium/barium hydroxides and peroxides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2817", "Zinc oxide; zinc peroxide", {
    "synonyms": ["zinc oxide", "zinc white", "zinc peroxide", "ZnO"],
    "market_terms": ["paint/rubber pigment trade", "cosmetic raw material trade", "pharma raw material trade"],
    "hindi_transliterated": [], "examples": ["zinc oxide powder for rubber/tyre manufacturing", "zinc oxide for sunscreen/cosmetic formulation"],
    "attributes": {"material": ["zinc oxide"], "use": ["rubber manufacturing", "cosmetics", "pharmaceuticals"], "form": ["powder"], "industry": ["chemicals", "rubber", "cosmetics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Zinc oxide and zinc peroxide map uniquely to 2817.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2817 covers zinc oxide and zinc peroxide — widely used as a rubber/tyre additive, a cosmetic sunscreen ingredient, and a pharmaceutical raw material.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2817 — zinc oxide; zinc peroxide. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2818", "Artificial corundum; aluminium oxide; aluminium hydroxide", {
    "synonyms": ["aluminium oxide", "alumina", "artificial corundum", "aluminium hydroxide"],
    "market_terms": ["abrasive raw material trade", "refractory material trade", "ceramic raw material trade"],
    "hindi_transliterated": [], "examples": ["alumina powder for abrasive/grinding wheel manufacturing", "aluminium hydroxide used as a flame-retardant filler"],
    "attributes": {"material": ["aluminium oxide", "aluminium hydroxide"], "use": ["abrasives", "refractories", "ceramics"], "form": ["powder"], "industry": ["chemicals", "abrasives", "ceramics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Artificial corundum, aluminium oxide and aluminium hydroxide map uniquely to 2818.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2818 covers artificial corundum, aluminium oxide (alumina) and aluminium hydroxide — key raw materials for abrasives, refractories and ceramics.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2818 — artificial corundum; aluminium oxide/hydroxide. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2819", "Chromium oxides and hydroxides", {
    "synonyms": ["chromium oxide", "chromic oxide", "chrome green pigment", "Cr2O3"],
    "market_terms": ["pigment raw material trade", "industrial chemical trade", "electroplating chemical trade"],
    "hindi_transliterated": [], "examples": ["chromium oxide green pigment for paints/ceramics", "chromium oxide used in metal plating/tanning"],
    "attributes": {"material": ["chromium oxide"], "use": ["pigments", "electroplating", "tanning"], "form": ["powder"], "industry": ["chemicals", "pigments", "metal finishing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Chromium oxides and hydroxides map uniquely to 2819.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2819 covers chromium oxides and hydroxides — used as a green pigment in paints/ceramics and in electroplating and leather tanning.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2819 — chromium oxides and hydroxides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2820", "Manganese oxides", {
    "synonyms": ["manganese dioxide", "manganese oxide", "MnO2", "battery-grade manganese oxide"],
    "market_terms": ["battery raw material trade", "ceramic/glass raw material trade", "industrial oxide supply"],
    "hindi_transliterated": [], "examples": ["manganese dioxide for dry-cell battery manufacturing", "manganese oxide used in ceramic glazing"],
    "attributes": {"material": ["manganese oxide"], "use": ["battery manufacturing", "ceramics"], "form": ["powder"], "industry": ["chemicals", "batteries", "ceramics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Manganese oxides map uniquely to 2820.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2820 covers manganese oxides, including manganese dioxide (MnO2) — a key raw material for dry-cell battery manufacturing and ceramic glazing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2820 — manganese oxides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2821", "Iron oxides and hydroxides; earth colours containing 70% or more combined iron (as Fe2O3)", {
    "synonyms": ["iron oxide pigment", "red oxide", "yellow oxide", "ochre"],
    "market_terms": ["pigment raw material trade", "paint industry chemical supply", "construction colour pigment trade"],
    "hindi_transliterated": [], "examples": ["red iron oxide pigment for paint manufacturing", "yellow iron oxide for construction colour mixing"],
    "attributes": {"material": ["iron oxide"], "use": ["pigments", "construction colouring"], "form": ["powder"], "industry": ["chemicals", "paints", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Iron oxide pigments and iron-rich earth colours map uniquely to 2821.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2821 covers iron oxides and hydroxides, and earth colours with 70% or more combined iron content — the red, yellow and brown pigments widely used in paints and construction colour mixing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2821 — iron oxides, hydroxides and earth colours. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2822", "Cobalt oxides and hydroxides; commercial cobalt oxides", {
    "synonyms": ["cobalt oxide", "cobalt hydroxide", "commercial cobalt oxide", "cobalt blue pigment raw material"],
    "market_terms": ["ceramic pigment raw material trade", "battery raw material trade", "specialty chemical supply"],
    "hindi_transliterated": [], "examples": ["cobalt oxide used in ceramic glaze/pigment manufacturing", "cobalt oxide used in battery cathode manufacturing"],
    "attributes": {"material": ["cobalt oxide"], "use": ["ceramics", "battery manufacturing"], "form": ["powder"], "industry": ["chemicals", "ceramics", "batteries"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Cobalt oxides and hydroxides map uniquely to 2822.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2822 covers cobalt oxides and hydroxides, including commercial cobalt oxide — used in ceramic pigments (cobalt blue) and battery cathode manufacturing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2822 — cobalt oxides and hydroxides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2823", "Titanium oxides", {
    "synonyms": ["titanium dioxide", "TiO2", "titanium white pigment", "rutile pigment"],
    "market_terms": ["paint pigment raw material trade", "plastics/coatings pigment supply", "cosmetic raw material trade"],
    "hindi_transliterated": [], "examples": ["titanium dioxide (TiO2) for paint manufacturing", "titanium dioxide used as a whitening pigment in plastics"],
    "attributes": {"material": ["titanium dioxide"], "use": ["paints", "plastics", "cosmetics"], "form": ["powder"], "industry": ["chemicals", "paints", "cosmetics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Titanium oxides map uniquely to 2823.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2823 covers titanium oxides, chiefly titanium dioxide (TiO2) — the world's most widely used white pigment, in paints, plastics and cosmetics.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2823 — titanium oxides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2824", "Lead oxides; red lead and orange lead", {
    "synonyms": ["lead oxide", "red lead", "litharge", "orange lead"],
    "market_terms": ["lead-acid battery raw material trade", "glass/ceramic raw material trade", "anti-corrosive pigment supply"],
    "hindi_transliterated": [], "examples": ["litharge (lead monoxide) for lead-acid battery manufacturing", "red lead used as an anti-corrosive primer pigment"],
    "attributes": {"material": ["lead oxide"], "use": ["battery manufacturing", "anti-corrosive coatings"], "form": ["powder"], "industry": ["chemicals", "batteries", "paints"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Lead oxides, red lead and orange lead map uniquely to 2824.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2824 covers lead oxides, including red lead and orange lead — key raw materials for lead-acid battery manufacturing and anti-corrosive primer pigments.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2824 — lead oxides; red lead; orange lead. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2825", "Hydrazine, hydroxylamine and their salts; other inorganic bases and metal oxides", {
    "synonyms": ["hydrazine", "hydroxylamine", "metal hydroxide (misc)", "nickel oxide"],
    "market_terms": ["specialty chemical trade", "industrial oxidiser/reducer supply", "propellant chemical trade"],
    "hindi_transliterated": [], "examples": ["hydrazine used as an industrial reducing agent/rocket propellant component", "nickel oxide used in ceramic/battery applications"],
    "attributes": {"material": ["hydrazine", "metal oxide"], "use": ["specialty chemical manufacturing"], "form": ["liquid", "powder"], "industry": ["chemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Hydrazine, hydroxylamine and other metal oxides/hydroxides not covered by more specific headings map to 2825.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2825 covers hydrazine and hydroxylamine and their salts, plus other inorganic bases and metal oxides/hydroxides/peroxides not covered by more specific headings elsewhere in this chapter.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2825 — hydrazine/hydroxylamine and other metal oxides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2826", "Fluorides; fluorosilicates, fluoroaluminates and other complex fluorine salts", {
    "synonyms": ["sodium fluoride", "fluorosilicate", "cryolite", "complex fluorine salt"],
    "market_terms": ["specialty chemical trade", "water fluoridation chemical supply", "aluminium smelting chemical trade"],
    "hindi_transliterated": [], "examples": ["sodium fluoride used in water fluoridation/toothpaste manufacturing", "cryolite used in aluminium smelting"],
    "attributes": {"material": ["fluoride salt"], "use": ["water treatment", "aluminium smelting"], "form": ["powder", "crystal"], "industry": ["chemicals", "aluminium industry"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Fluorides and complex fluorine salts map uniquely to 2826.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2826 covers fluorides, fluorosilicates, fluoroaluminates and other complex fluorine salts — used in water fluoridation, toothpaste manufacturing and aluminium smelting.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2826 — fluorides and complex fluorine salts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2827", "Chlorides, chloride oxides and chloride hydroxides; bromides and bromide oxides; iodides and iodide oxides", {
    "synonyms": ["calcium chloride", "ammonium chloride", "ferric chloride", "potassium iodide"],
    "market_terms": ["industrial salt/chemical trade", "water treatment chemical supply", "de-icing chemical trade"],
    "hindi_transliterated": [], "examples": ["calcium chloride used for de-icing and as a desiccant", "ferric chloride used in water/wastewater treatment"],
    "attributes": {"material": ["metal halide salt"], "use": ["water treatment", "de-icing", "industrial processing"], "form": ["powder", "solution"], "industry": ["chemicals", "water treatment"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Chlorides, bromides, iodides and their oxides map uniquely to 2827.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2827 covers chlorides, bromides, iodides and their oxide/hydroxide forms — common industrial salts like calcium chloride and ferric chloride used in water treatment and de-icing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2827 — chlorides, bromides and iodides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2828", "Hypochlorites; commercial calcium hypochlorite; chlorites; hypobromites", {
    "synonyms": ["bleaching powder", "calcium hypochlorite", "sodium hypochlorite (solid form)", "chlorite"],
    "market_terms": ["bleaching powder trade", "water disinfection chemical supply", "textile bleaching chemical trade"],
    "hindi_transliterated": ["bleaching powder"], "examples": ["calcium hypochlorite (bleaching powder) for water disinfection", "bleaching powder used in textile/paper processing"],
    "attributes": {"material": ["hypochlorite"], "use": ["water disinfection", "textile bleaching"], "form": ["powder"], "industry": ["chemicals", "water treatment", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Hypochlorites, including commercial bleaching powder, map uniquely to 2828.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2828 covers hypochlorites, commercial calcium hypochlorite (bleaching powder), chlorites and hypobromites — widely used for water disinfection and textile bleaching.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2828 — hypochlorites and bleaching powder. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2829", "Chlorates and perchlorates; bromates and perbromates; iodates and periodates", {
    "synonyms": ["potassium chlorate", "sodium chlorate", "perchlorate", "iodate"],
    "market_terms": ["specialty chemical trade", "match/fireworks raw material trade", "herbicide raw material trade"],
    "hindi_transliterated": [], "examples": ["potassium chlorate used in match-head/fireworks manufacturing", "sodium chlorate used as a herbicide raw material"],
    "attributes": {"material": ["chlorate/perchlorate salt"], "use": ["match/fireworks manufacturing", "herbicide production"], "form": ["powder", "crystal"], "industry": ["chemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Chlorates, perchlorates, bromates and iodates map uniquely to 2829.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2829 covers chlorates, perchlorates, bromates, perbromates, iodates and periodates — used in match/fireworks manufacturing and as herbicide raw material.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2829 — chlorates, perchlorates, bromates and iodates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2830", "Sulphides; polysulphides, whether or not chemically defined", {
    "synonyms": ["sodium sulphide", "calcium polysulphide", "metal sulphide", "unhairing chemical (sulphide)"],
    "market_terms": ["leather tanning chemical trade", "industrial chemical supply", "agrochemical raw material trade"],
    "hindi_transliterated": [], "examples": ["sodium sulphide used in leather tanning (unhairing agent)", "calcium polysulphide used as an agricultural fungicide"],
    "attributes": {"material": ["metal sulphide"], "use": ["leather tanning", "agriculture"], "form": ["powder", "liquid"], "industry": ["chemicals", "leather", "agriculture"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sulphides and polysulphides map uniquely to 2830.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2830 covers sulphides and polysulphides — sodium sulphide is a key leather-tanning unhairing agent, while calcium polysulphide is used as an agricultural fungicide.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2830 — sulphides and polysulphides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2831", "Dithionites and sulphoxylates", {
    "synonyms": ["sodium dithionite", "sodium hydrosulphite", "sulphoxylate", "reducing agent (dithionite)"],
    "market_terms": ["textile bleaching chemical trade", "dye industry chemical supply", "paper bleaching chemical trade"],
    "hindi_transliterated": [], "examples": ["sodium hydrosulphite used as a textile/paper bleaching agent", "sodium dithionite used in vat-dye reduction"],
    "attributes": {"material": ["dithionite", "sulphoxylate"], "use": ["textile bleaching/dyeing"], "form": ["powder"], "industry": ["chemicals", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Dithionites and sulphoxylates map uniquely to 2831.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2831 covers dithionites and sulphoxylates — reducing agents like sodium hydrosulphite, widely used in textile/paper bleaching and vat-dye reduction.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2831 — dithionites and sulphoxylates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2832", "Sulphites; thiosulphates", {
    "synonyms": ["sodium sulphite", "sodium thiosulphate", "hypo (photography chemical)", "dechlorination chemical"],
    "market_terms": ["photography chemical trade", "food preservative raw material trade", "water treatment chemical supply"],
    "hindi_transliterated": [], "examples": ["sodium thiosulphate (hypo) used in photographic fixing", "sodium sulphite used as a food preservative/antioxidant"],
    "attributes": {"material": ["sulphite", "thiosulphate"], "use": ["photography", "food preservation", "water dechlorination"], "form": ["powder"], "industry": ["chemicals", "food processing", "water treatment"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sulphites and thiosulphates map uniquely to 2832.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2832 covers sulphites and thiosulphates — sodium thiosulphate ('hypo') is used in photographic fixing and water dechlorination, while sodium sulphite is a common food preservative.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2832 — sulphites and thiosulphates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2833", "Sulphates; alums; peroxosulphates (persulphates)", {
    "synonyms": ["alum", "aluminium sulphate", "copper sulphate", "magnesium sulphate"],
    "market_terms": ["water treatment chemical trade", "agricultural chemical supply", "industrial sulphate trade"],
    "hindi_transliterated": ["phitkari"], "examples": ["alum (aluminium sulphate) used in water purification", "copper sulphate used as an agricultural fungicide"],
    "attributes": {"material": ["sulphate salt", "alum"], "use": ["water treatment", "agriculture"], "form": ["powder", "crystal"], "industry": ["chemicals", "water treatment", "agriculture"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sulphates, alums and peroxosulphates map uniquely to 2833.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2833 covers sulphates, alums and peroxosulphates — alum is a common water-purification coagulant, and copper sulphate is a widely used agricultural fungicide.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2833 — sulphates and alums. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2834", "Nitrites; nitrates", {
    "synonyms": ["sodium nitrate", "potassium nitrate", "nitrite salt", "saltpetre"],
    "market_terms": ["fertiliser raw material trade", "food preservative raw material trade", "industrial oxidiser supply"],
    "hindi_transliterated": [], "examples": ["potassium nitrate (saltpetre) used in fertiliser manufacturing", "sodium nitrite used as a food preservative"],
    "attributes": {"material": ["nitrate salt", "nitrite salt"], "use": ["fertiliser production", "food preservation"], "form": ["powder", "crystal"], "industry": ["chemicals", "fertilisers", "food processing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Nitrites and nitrates map uniquely to 2834.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2834 covers nitrites and nitrates — potassium nitrate (saltpetre) is a key fertiliser raw material, and sodium nitrite is a common food preservative.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2834 — nitrites and nitrates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2835", "Phosphinates, phosphonates and phosphates; polyphosphates", {
    "synonyms": ["sodium tripolyphosphate (STPP)", "calcium phosphate", "phosphate salt", "polyphosphate"],
    "market_terms": ["detergent raw material trade", "fertiliser raw material trade", "food additive raw material trade"],
    "hindi_transliterated": [], "examples": ["STPP used as a detergent builder", "calcium phosphate used in fertiliser/food additive manufacturing"],
    "attributes": {"material": ["phosphate salt"], "use": ["detergent manufacturing", "fertiliser production", "food additives"], "form": ["powder"], "industry": ["chemicals", "detergents", "fertilisers"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Phosphinates, phosphonates, phosphates and polyphosphates map uniquely to 2835.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2835 covers phosphinates, phosphonates, phosphates and polyphosphates — sodium tripolyphosphate (STPP) is a common detergent builder, and calcium phosphate is used in fertilisers and food additives.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2835 — phosphates and polyphosphates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2836", "Carbonates; peroxocarbonates (percarbonates); commercial ammonium carbonate", {
    "synonyms": ["sodium carbonate", "washing soda", "baking soda (sodium bicarbonate)", "calcium carbonate"],
    "market_terms": ["soda ash trade", "detergent raw material trade", "food/pharma raw material trade"],
    "hindi_transliterated": ["soda"], "examples": ["sodium carbonate (soda ash/washing soda) for detergent/glass manufacturing", "sodium bicarbonate (baking soda) for food/pharma use"],
    "attributes": {"material": ["carbonate salt"], "use": ["detergent manufacturing", "glass manufacturing", "food/pharma"], "form": ["powder"], "industry": ["chemicals", "detergents", "glass", "food processing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Carbonates, percarbonates and commercial ammonium carbonate map uniquely to 2836.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2836 covers carbonates and percarbonates — sodium carbonate (soda ash/washing soda) is a key raw material for detergent and glass manufacturing, and sodium bicarbonate (baking soda) is used across food and pharma.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2836 — carbonates and percarbonates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2837", "Cyanides, cyanide oxides and complex cyanides", {
    "synonyms": ["sodium cyanide", "potassium cyanide", "complex cyanide salt", "cyanide salt"],
    "market_terms": ["mining chemical trade", "electroplating chemical supply", "metal extraction chemical trade"],
    "hindi_transliterated": [], "examples": ["sodium cyanide used in gold ore extraction (mining)", "potassium cyanide used in electroplating"],
    "attributes": {"material": ["cyanide salt"], "use": ["mining", "electroplating"], "form": ["powder", "solution"], "industry": ["chemicals", "mining", "metal finishing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Cyanides, cyanide oxides and complex cyanides map uniquely to 2837.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2837 covers cyanides, cyanide oxides and complex cyanides — heavily regulated industrial chemicals used in gold ore extraction (mining) and electroplating.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2837 — cyanides and complex cyanides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2839", "Silicates; commercial alkali metal silicates", {
    "synonyms": ["sodium silicate", "water glass", "potassium silicate", "silicate solution"],
    "market_terms": ["detergent raw material trade", "adhesive raw material trade", "foundry chemical supply"],
    "hindi_transliterated": [], "examples": ["sodium silicate (water glass) used as a detergent builder/adhesive", "sodium silicate used in foundry sand binding"],
    "attributes": {"material": ["silicate"], "use": ["detergent manufacturing", "adhesives", "foundry"], "form": ["solution", "powder"], "industry": ["chemicals", "detergents", "foundry"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Silicates and commercial alkali metal silicates map uniquely to 2839.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2839 covers silicates, including commercial alkali metal silicates like sodium silicate (water glass) — used as a detergent builder, adhesive, and foundry sand binder.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2839 — silicates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2840", "Borates; peroxoborates (perborates)", {
    "synonyms": ["borax", "sodium borate", "sodium perborate", "boron salt"],
    "market_terms": ["detergent bleach raw material trade", "glass/ceramic raw material trade", "cosmetic raw material trade"],
    "hindi_transliterated": ["suhaga"], "examples": ["borax used in glass/ceramic manufacturing and as a cleaning agent", "sodium perborate used as a detergent bleaching agent"],
    "attributes": {"material": ["borate", "perborate"], "use": ["detergent manufacturing", "glass/ceramics"], "form": ["powder", "crystal"], "industry": ["chemicals", "detergents", "glass"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Borates and perborates map uniquely to 2840.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2840 covers borates and perborates — borax is used in glass/ceramic manufacturing and cleaning, while sodium perborate is a common detergent bleaching agent.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2840 — borates and perborates. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2841", "Salts of oxometallic or peroxometallic acids", {
    "synonyms": ["sodium dichromate", "potassium permanganate", "chromate salt", "oxometallic salt"],
    "market_terms": ["water treatment chemical trade", "tanning/dye chemical supply", "metal plating chemical trade"],
    "hindi_transliterated": [], "examples": ["potassium permanganate used for water treatment/disinfection", "sodium dichromate used in leather tanning/chrome plating"],
    "attributes": {"material": ["oxometallic salt"], "use": ["water treatment", "leather tanning", "metal plating"], "form": ["powder", "crystal"], "industry": ["chemicals", "water treatment", "leather"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Salts of oxometallic/peroxometallic acids map uniquely to 2841.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2841 covers salts of oxometallic or peroxometallic acids — potassium permanganate is a common water-treatment/disinfection chemical, and sodium dichromate is used in tanning and chrome plating.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2841 — salts of oxometallic/peroxometallic acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2842", "Other salts of inorganic acids or peroxoacids (including aluminosilicates), other than azides", {
    "synonyms": ["zeolite", "aluminosilicate salt", "molecular sieve material", "other inorganic salt"],
    "market_terms": ["detergent builder raw material trade", "catalyst raw material trade", "water softener raw material trade"],
    "hindi_transliterated": [], "examples": ["synthetic zeolite used as a detergent builder", "aluminosilicate used as an industrial catalyst/molecular sieve"],
    "attributes": {"material": ["aluminosilicate", "inorganic salt"], "use": ["detergent manufacturing", "industrial catalysis"], "form": ["powder"], "industry": ["chemicals", "detergents"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Other inorganic acid salts, including aluminosilicates like zeolite, map uniquely to 2842.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2842 covers other salts of inorganic acids or peroxoacids, including aluminosilicates like synthetic zeolite — used as detergent builders and industrial catalysts/molecular sieves.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2842 — other inorganic acid salts (incl. aluminosilicates). Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2843", "Colloidal precious metals; inorganic or organic compounds of precious metals; amalgams of precious metals", {
    "synonyms": ["colloidal silver", "silver nitrate", "gold compound (precious metal)", "precious metal salt"],
    "market_terms": ["photography/pharma chemical trade", "precious metal chemical supply", "diagnostics reagent trade"],
    "hindi_transliterated": [], "examples": ["silver nitrate used in photographic film/pharma manufacturing", "colloidal gold used in diagnostic test kits"],
    "attributes": {"material": ["precious metal compound"], "use": ["photography", "pharmaceuticals", "diagnostics"], "form": ["solution", "compound"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Colloidal precious metals and their compounds/amalgams map uniquely to 2843.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2843 covers colloidal precious metals and their inorganic/organic compounds and amalgams — silver nitrate is used in photographic and pharma manufacturing, and colloidal gold in diagnostic test kits.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2843 — precious metal compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2844", "Radioactive chemical elements and radioactive isotopes and their compounds; mixtures", {
    "synonyms": ["radioactive isotope", "enriched uranium (compound)", "radioisotope compound", "fissile material compound"],
    "market_terms": ["nuclear/medical isotope trade", "specialty radioactive material supply", "licensed nuclear material trade"],
    "hindi_transliterated": [], "examples": ["radioisotope compound used in nuclear medicine/diagnostics", "enriched uranium compound used in nuclear fuel"],
    "attributes": {"material": ["radioactive element", "radioisotope"], "use": ["nuclear medicine", "nuclear fuel", "research"], "form": ["compound"], "industry": ["nuclear energy", "healthcare/diagnostics"]},
    "clarification_questions": [], "exclusion_notes": [{"excluded_code": "HSN_2845", "reason": "2845 is stable (non-radioactive) isotopes and their compounds — 2844 is specifically radioactive elements and isotopes"}],
    "classification_confidence": {"level": "Low", "rationale": "This heading covers licensed, heavily regulated nuclear materials; plain-language MSME retail search rarely applies here, and the specific isotope/compound requires specialist regulatory classification.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2844 covers radioactive chemical elements and isotopes and their compounds — a heavily regulated category (nuclear fuel materials, medical radioisotopes) traded only under specific government licensing, not typical open MSME retail.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2844 — radioactive elements and isotopes. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_2845", "Isotopes other than those of heading 28.44; compounds of such isotopes", {
    "synonyms": ["stable isotope", "deuterium", "heavy water", "isotope compound"],
    "market_terms": ["specialty isotope trade", "research/industrial isotope supply", "nuclear reactor material trade"],
    "hindi_transliterated": [], "examples": ["heavy water (deuterium oxide) used in nuclear reactors/research", "stable isotope compound used in scientific research"],
    "attributes": {"material": ["stable isotope"], "use": ["research", "industrial/nuclear applications"], "form": ["compound", "liquid"], "industry": ["chemicals", "research", "nuclear energy"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Non-radioactive (stable) isotopes and their compounds map uniquely to 2845, cleanly resolved at heading level.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2845 covers stable isotopes (other than the radioactive ones in 2844) and their compounds — heavy water (deuterium oxide) is the best-known example, used in nuclear reactors and scientific research. GST is 5%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2845 — stable isotopes and their compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2846", "Compounds, inorganic or organic, of rare-earth metals, of yttrium or of scandium or of mixtures of these metals", {
    "synonyms": ["rare-earth compound", "cerium compound", "lanthanum compound", "yttrium compound"],
    "market_terms": ["specialty/electronics raw material trade", "magnet/catalyst raw material supply", "glass polishing compound trade"],
    "hindi_transliterated": [], "examples": ["cerium oxide used in glass polishing", "rare-earth compound used in permanent magnet manufacturing"],
    "attributes": {"material": ["rare-earth compound"], "use": ["electronics", "magnets", "catalysts", "glass polishing"], "form": ["powder", "compound"], "industry": ["chemicals", "electronics", "specialty materials"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Rare-earth, yttrium and scandium compounds map uniquely to 2846.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2846 covers inorganic or organic compounds of rare-earth metals, yttrium or scandium — used in permanent magnets, catalysts, glass polishing and electronics.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2846 — rare-earth/yttrium/scandium compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2849", "Carbides, whether or not chemically defined", {
    "synonyms": ["calcium carbide", "silicon carbide", "tungsten carbide", "carborundum"],
    "market_terms": ["welding/cutting gas raw material trade", "abrasive raw material trade", "cutting tool raw material supply"],
    "hindi_transliterated": [], "examples": ["calcium carbide used to generate acetylene gas for welding/cutting", "silicon carbide (carborundum) used as an industrial abrasive"],
    "attributes": {"material": ["carbide"], "use": ["welding/cutting", "abrasives", "cutting tools"], "form": ["lump", "powder"], "industry": ["chemicals", "welding", "abrasives"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Carbides (calcium, silicon, tungsten and others) map uniquely to 2849.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2849 covers carbides — calcium carbide generates acetylene gas for welding/cutting, while silicon carbide (carborundum) and tungsten carbide are widely used as industrial abrasives and cutting-tool materials.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2849 — carbides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add28("HSN_2852", "Inorganic or organic compounds of mercury, excluding amalgams", {
    "synonyms": ["mercury compound", "mercuric chloride", "mercury salt", "mercuric oxide"],
    "market_terms": ["specialty chemical trade", "laboratory reagent supply", "regulated toxic chemical trade"],
    "hindi_transliterated": [], "examples": ["mercury compound used in specialty chemical synthesis", "mercuric chloride used as a laboratory reagent"],
    "attributes": {"material": ["mercury compound"], "use": ["specialty chemical synthesis", "laboratory reagent"], "form": ["powder", "solution"], "industry": ["chemicals", "laboratories"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Mercury compounds (excluding amalgams, which sit under 2805) map uniquely to 2852.", "ambiguity_triggers": ["amalgam"]},
    "plain_rationale": "HSN 2852 covers inorganic or organic compounds of mercury, excluding amalgams (which are classified under 2805 instead) — used in specialty chemical synthesis and laboratory reagents. This is a tightly regulated category due to mercury's toxicity.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2852 — mercury compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_2853", "Phosphides (excl. ferrophosphorus); other inorganic compounds; liquid air; distilled water; amalgams", {
    "synonyms": ["aluminium phosphide", "distilled water (industrial)", "liquid air", "zinc phosphide"],
    "market_terms": ["fumigant chemical trade", "laboratory/industrial water supply", "cryogenic gas trade"],
    "hindi_transliterated": [], "examples": ["aluminium phosphide used as a grain fumigant pesticide", "distilled water for laboratory/battery use"],
    "attributes": {"material": ["phosphide", "distilled water", "liquid air"], "use": ["pest control (fumigant)", "laboratory/industrial use"], "form": ["tablet", "liquid", "gas"], "industry": ["chemicals", "agriculture", "laboratories"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "This residual heading (phosphides, distilled water, liquid air, amalgams not covered elsewhere) is cleanly resolved at heading level.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2853 covers phosphides (except ferrophosphorus), other miscellaneous inorganic compounds including distilled/conductivity water, liquid air, and amalgams not classified under precious/mercury headings — aluminium phosphide grain fumigant tablets are a common example. GST is 5%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 28, Heading 2853 — phosphides and other inorganic compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
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
