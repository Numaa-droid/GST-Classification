"""
Wave 2, Chapter 39 (plastics and articles thereof) — 26 heading-level records.
Same harness as Wave 1/2 (scripts/enrichment_harness.py + wave1_records.build_record).

Unlike the apparel cluster, Chapter 39 rates are matched cleanly at heading
level (rate_confidence "medium", rate_scope "heading") for 25 of 26 headings,
so most records need no rate_caveat at all. 3926 is the exception — a residual
"other articles of plastics" bucket whose listed 5% base rate is misleading
(most goods in it actually attract 18%, only bangles/beads/feeding bottles
keep 5%), the same "inverted exception" pattern seen in Chapter 33 in Wave 1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import load_master, validate, finalize, write_jsonl
from wave1_records import build_record

MASTER = load_master()

CH39_HEADINGS = [f"HSN_39{n:02d}" for n in range(1, 27)]  # 3901-3926

RECORDS = []


def add(mid, title, ai, status="complete", exceptions=None, caveat=None):
    RECORDS.append((mid, CH39_HEADINGS, title, ai, status, exceptions or [], caveat))


add("HSN_3901", "Polymers of ethylene, in primary forms", {
    "synonyms": ["polyethylene", "PE granules", "HDPE", "LDPE", "polyethylene resin"],
    "market_terms": ["PE resin trade", "polymer raw material", "plastic granule supply"],
    "hindi_transliterated": [],
    "examples": ["HDPE granules for blow moulding", "LDPE resin for film manufacturing"],
    "attributes": {"material": ["polyethylene"], "use": ["raw material for plastic manufacturing"], "form": ["granules", "pellets", "powder"], "industry": ["plastics", "chemicals", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Polyethylene polymers in primary (granule/resin) form map uniquely to 3901 by chemical composition.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3901 covers polymers of ethylene (polyethylene, including HDPE and LDPE) in primary form — granules, pellets or powder raw resin, not yet converted into finished plastic articles. If you trade in or manufacture PE resin as raw material, this is your code. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3901 — polymers of ethylene, primary forms. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3902", "Polymers of propylene or of other olefins, in primary forms", {
    "synonyms": ["polypropylene", "PP granules", "PP resin", "propylene polymer"],
    "market_terms": ["PP resin trade", "polymer raw material supply", "olefin polymer trade"],
    "hindi_transliterated": [],
    "examples": ["PP granules for injection moulding", "polypropylene resin for woven sack manufacturing"],
    "attributes": {"material": ["polypropylene"], "use": ["raw material for plastic manufacturing"], "form": ["granules", "pellets"], "industry": ["plastics", "chemicals", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Polypropylene and other olefin polymers in primary form map uniquely to 3902.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3902 covers polymers of propylene and other olefins (like polypropylene, PP) in primary raw-resin form. If you trade in or manufacture PP granules/resin as raw material, this is your code. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3902 — polymers of propylene/olefins, primary forms. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3903", "Polymers of styrene, in primary forms", {
    "synonyms": ["polystyrene", "PS granules", "expandable polystyrene (EPS) beads", "styrene resin"],
    "market_terms": ["PS resin trade", "thermocol raw material", "polymer supply"],
    "hindi_transliterated": [],
    "examples": ["EPS beads for thermocol packaging", "polystyrene resin for injection moulding"],
    "attributes": {"material": ["polystyrene"], "use": ["raw material for plastic/thermocol manufacturing"], "form": ["granules", "beads"], "industry": ["plastics", "chemicals", "packaging"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Polystyrene polymers, including expandable EPS beads, map uniquely to 3903.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3903 covers polymers of styrene (polystyrene, including expandable EPS beads used to make thermocol) in primary raw-resin form. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3903 — polymers of styrene, primary forms. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3904", "Polymers of vinyl chloride or of other halogenated olefins, in primary forms", {
    "synonyms": ["PVC resin", "PVC granules", "vinyl chloride polymer", "PVC compound"],
    "market_terms": ["PVC resin trade", "pipe-grade PVC supply", "halogenated polymer trade"],
    "hindi_transliterated": [],
    "examples": ["PVC resin for pipe manufacturing", "PVC compound for cable insulation"],
    "attributes": {"material": ["PVC", "halogenated olefin polymer"], "use": ["raw material for plastic manufacturing"], "form": ["granules", "compound", "powder"], "industry": ["plastics", "chemicals", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "PVC and other halogenated-olefin polymers in primary form map uniquely to 3904.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3904 covers polymers of vinyl chloride (PVC) and other halogenated olefins in primary raw-resin form — the raw material used to make PVC pipes, cables and profiles. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3904 — polymers of vinyl chloride/halogenated olefins. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3905", "Polymers of vinyl acetate or of other vinyl esters, in primary forms; other vinyl polymers", {
    "synonyms": ["PVA resin", "vinyl acetate polymer", "polyvinyl alcohol", "vinyl ester polymer"],
    "market_terms": ["vinyl polymer trade", "adhesive raw material supply", "paint binder resin trade"],
    "hindi_transliterated": [],
    "examples": ["PVA resin for adhesive manufacturing", "vinyl acetate polymer for paint binders"],
    "attributes": {"material": ["vinyl acetate polymer", "PVA"], "use": ["raw material for adhesives/paints"], "form": ["resin", "emulsion", "powder"], "industry": ["plastics", "chemicals", "adhesives"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Vinyl acetate and other vinyl polymers in primary form map uniquely to 3905.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3905 covers polymers of vinyl acetate and other vinyl esters (like PVA) in primary form — used as raw material for adhesives, paints and coatings. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3905 — vinyl acetate/vinyl ester polymers. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3906", "Acrylic polymers in primary forms", {
    "synonyms": ["acrylic resin", "PMMA", "acrylic polymer", "polyacrylate"],
    "market_terms": ["acrylic resin trade", "polymer raw material supply", "PMMA sheet raw material"],
    "hindi_transliterated": [],
    "examples": ["acrylic sheet raw resin", "PMMA granules for signage manufacturing"],
    "attributes": {"material": ["acrylic polymer", "PMMA"], "use": ["raw material for plastic manufacturing"], "form": ["granules", "resin"], "industry": ["plastics", "chemicals", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Acrylic polymers in primary form map uniquely to 3906.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3906 covers acrylic polymers (like PMMA/acrylic resin) in primary form — raw material for acrylic sheets, paints and adhesives. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3906 — acrylic polymers, primary forms. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3907", "Polyacetals, other polyethers, epoxide resins, polycarbonates and other polyesters, in primary forms", {
    "synonyms": ["polycarbonate resin", "epoxy resin", "polyester resin", "PET resin"],
    "market_terms": ["engineering plastic resin trade", "epoxy raw material supply", "PET chip trade"],
    "hindi_transliterated": [],
    "examples": ["PET resin chips for bottle manufacturing", "epoxy resin for adhesives and coatings"],
    "attributes": {"material": ["polycarbonate", "epoxy resin", "PET"], "use": ["raw material for plastic/packaging manufacturing"], "form": ["resin", "chips", "granules"], "industry": ["plastics", "chemicals", "packaging"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Polyacetals, polyethers, epoxide resins, polycarbonates and polyesters in primary form map uniquely to 3907.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3907 covers polyacetals, polyethers, epoxide resins, polycarbonates and polyesters (including PET resin) in primary form. PET resin used for bottle-grade plastic falls here. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3907 — polyacetals, epoxide resins, polycarbonates, polyesters. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3908", "Polyamides in primary forms", {
    "synonyms": ["nylon resin", "polyamide granules", "nylon 6", "nylon 66"],
    "market_terms": ["nylon resin trade", "engineering plastic supply", "polyamide chip trade"],
    "hindi_transliterated": [],
    "examples": ["nylon 6 granules for yarn/fibre manufacturing", "polyamide resin for moulded parts"],
    "attributes": {"material": ["polyamide", "nylon"], "use": ["raw material for fibre/plastic manufacturing"], "form": ["granules", "chips"], "industry": ["plastics", "chemicals", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Polyamides (nylon) in primary form map uniquely to 3908.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3908 covers polyamides (nylon resins like Nylon 6 and Nylon 66) in primary form — raw material for synthetic fibre, yarn and moulded engineering parts. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3908 — polyamides, primary forms. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3909", "Amino-resins, phenolic resins and polyurethanes, in primary forms", {
    "synonyms": ["polyurethane resin", "phenolic resin", "melamine resin", "urea formaldehyde resin"],
    "market_terms": ["PU foam raw material", "adhesive resin trade", "laminate resin supply"],
    "hindi_transliterated": [],
    "examples": ["polyurethane (PU) resin for foam manufacturing", "phenolic resin for plywood adhesive"],
    "attributes": {"material": ["polyurethane", "phenolic resin", "melamine resin"], "use": ["raw material for foam/adhesive/laminate manufacturing"], "form": ["resin", "liquid", "powder"], "industry": ["plastics", "chemicals", "furniture", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Amino-resins, phenolic resins and polyurethanes in primary form map uniquely to 3909.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3909 covers amino-resins, phenolic resins and polyurethanes (PU) in primary form — raw material for foam, adhesives, laminates and plywood binders. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3909 — amino-resins, phenolic resins, polyurethanes. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3910", "Silicones in primary forms", {
    "synonyms": ["silicone resin", "silicone sealant raw material", "silicone rubber compound", "silicone elastomer"],
    "market_terms": ["silicone raw material trade", "sealant/adhesive supply", "mould-making resin trade"],
    "hindi_transliterated": [],
    "examples": ["silicone sealant raw compound", "silicone resin for mould-making"],
    "attributes": {"material": ["silicone"], "use": ["raw material for sealant/rubber manufacturing"], "form": ["resin", "compound", "liquid"], "industry": ["plastics", "chemicals", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Silicones in primary form map uniquely to 3910.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3910 covers silicones in primary form — the raw material for silicone sealants, rubber compounds and moulds. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3910 — silicones, primary forms. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3911", "Petroleum resins, coumarone-indene resins, polyterpenes, polysulphides, polysulphones and similar products", {
    "synonyms": ["petroleum resin", "coumarone-indene resin", "polyterpene resin", "polysulphide resin"],
    "market_terms": ["specialty resin trade", "adhesive/rubber raw material supply", "ink resin trade"],
    "hindi_transliterated": [],
    "examples": ["petroleum resin used in rubber and adhesive manufacturing", "polyterpene resin used in printing ink formulation"],
    "attributes": {"material": ["petroleum resin", "polyterpene"], "use": ["raw material for rubber/adhesive/ink manufacturing"], "form": ["resin"], "industry": ["plastics", "chemicals", "rubber"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "These specialty synthetic resins map uniquely to 3911 by chemical composition.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3911 covers petroleum resins, coumarone-indene resins, polyterpenes and similar specialty synthetic resins used as raw material in rubber, adhesive and ink manufacturing. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3911 — petroleum resins and similar specialty resins. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3912", "Cellulose and its chemical derivatives, not elsewhere specified, in primary forms", {
    "synonyms": ["cellulose acetate", "carboxymethyl cellulose (CMC)", "cellulose derivative resin", "cellulose nitrate"],
    "market_terms": ["cellulose derivative trade", "CMC raw material supply", "cellulose film raw material"],
    "hindi_transliterated": [],
    "examples": ["cellulose acetate flakes for film manufacturing", "CMC powder used as a thickening agent raw material"],
    "attributes": {"material": ["cellulose acetate", "CMC"], "use": ["raw material for film/thickener manufacturing"], "form": ["flakes", "powder"], "industry": ["plastics", "chemicals", "food processing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Cellulose derivatives not elsewhere specified map uniquely to 3912.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3912 covers cellulose and its chemical derivatives not elsewhere specified, in primary form — such as cellulose acetate and CMC (carboxymethyl cellulose), used as raw material in films, coatings and thickeners. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3912 — cellulose and chemical derivatives. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3913", "Natural polymers and modified natural polymers, in primary forms", {
    "synonyms": ["alginic acid", "modified natural polymer", "hardened protein resin", "natural biopolymer"],
    "market_terms": ["natural polymer trade", "specialty biopolymer supply", "food-grade thickener raw material"],
    "hindi_transliterated": [],
    "examples": ["alginic acid used in food/pharma thickening applications", "modified natural polymer raw material"],
    "attributes": {"material": ["natural polymer", "alginic acid"], "use": ["raw material for food/pharma/industrial applications"], "form": ["powder", "resin"], "industry": ["chemicals", "food processing", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Natural and modified natural polymers map uniquely to 3913 by definition.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3913 covers natural polymers (like alginic acid) and modified natural polymers (such as hardened proteins) in primary form, used as specialty raw materials in food, pharma and industrial applications. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3913 — natural and modified natural polymers. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3914", "Ion-exchangers based on polymers of headings 39.01 to 39.13, in primary forms", {
    "synonyms": ["ion exchange resin", "water softening resin", "deionising resin", "resin beads (water treatment)"],
    "market_terms": ["ion-exchange resin trade", "water treatment raw material", "RO plant resin supply"],
    "hindi_transliterated": [],
    "examples": ["ion-exchange resin for water softener manufacturing", "deionising resin for RO plants"],
    "attributes": {"material": ["ion-exchange resin"], "use": ["water treatment"], "form": ["resin", "beads"], "industry": ["chemicals", "water treatment", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Ion-exchange resins map uniquely to 3914.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3914 covers ion-exchange resins based on the polymers of headings 3901-3913, used in water softening and purification systems. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3914 — ion-exchangers based on polymers. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3915", "Waste, parings and scrap, of plastics", {
    "synonyms": ["plastic scrap", "plastic waste", "PET scrap", "plastic regrind"],
    "market_terms": ["plastic scrap trade", "recycled plastic raw material", "PET bottle scrap trade"],
    "hindi_transliterated": [],
    "examples": ["PET bottle scrap sold to a recycler", "mixed plastic waste for regrinding"],
    "attributes": {"material": ["plastic waste", "plastic scrap"], "use": ["recycling"], "form": ["scrap", "regrind", "flakes"], "industry": ["plastics", "recycling", "waste trade"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Plastic waste, parings and scrap map uniquely to 3915, distinct from finished plastic goods.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3915 covers waste, parings and scrap of plastics — offcuts, rejects and recovered plastic material sold for recycling, not finished goods. If you trade in plastic scrap or waste, this is your code. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3915 — waste, parings and scrap of plastics. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3916", "Monofilament, rods, sticks and profile shapes, of plastics", {
    "synonyms": ["plastic rod", "plastic monofilament", "plastic profile", "plastic stick"],
    "market_terms": ["plastic extrusion trade", "profile/rod manufacturing supply", "plastic raw stock trade"],
    "hindi_transliterated": [],
    "examples": ["plastic rods for machining components", "plastic profile strips for furniture edging"],
    "attributes": {"material": ["plastic (extruded)"], "use": ["raw stock for machining/fabrication"], "form": ["rod", "profile", "monofilament"], "industry": ["plastics", "manufacturing", "furniture"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Plastic monofilament, rods, sticks and profile shapes map uniquely to 3916.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3916 covers plastic monofilament, rods, sticks and profile shapes (over 1mm cross-section), whether surface-worked or not, but not otherwise worked. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3916 — plastic monofilament, rods and profile shapes. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3917", "Tubes, pipes and hoses, and fittings therefor, of plastics", {
    "synonyms": ["PVC pipe", "plastic pipe", "plastic hose", "pipe fitting (plastic)"],
    "market_terms": ["plastic pipe manufacturing", "PVC pipe & fitting trade", "irrigation pipe supply"],
    "hindi_transliterated": [],
    "examples": ["PVC water supply pipe", "plastic garden hose", "PVC elbow/joint fitting"],
    "attributes": {"material": ["PVC", "plastic"], "use": ["plumbing", "irrigation", "industrial piping"], "form": ["pipe", "hose", "fitting"], "industry": ["plastics", "construction", "agriculture"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Plastic tubes, pipes, hoses and their fittings map uniquely to 3917.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3917 covers plastic tubes, pipes and hoses, and their fittings (joints, elbows, flanges). If you make or sell PVC/plastic pipes and fittings for plumbing, irrigation or industrial use, this is your code. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3917 — plastic tubes, pipes, hoses and fittings. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3918", "Floor coverings and wall or ceiling coverings, of plastics", {
    "synonyms": ["vinyl flooring", "plastic floor covering", "PVC wall covering", "vinyl tile"],
    "market_terms": ["vinyl flooring trade", "plastic tile manufacturing", "interior décor material supply"],
    "hindi_transliterated": [],
    "examples": ["vinyl flooring roll for home use", "PVC wall covering sheet"],
    "attributes": {"material": ["PVC", "vinyl"], "use": ["flooring", "wall/ceiling covering"], "form": ["roll", "tile", "sheet"], "industry": ["plastics", "construction", "interior décor"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Plastic floor, wall and ceiling coverings map uniquely to 3918.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3918 covers floor, wall or ceiling coverings of plastics, in rolls or tile form, including self-adhesive types — vinyl flooring and PVC wall coverings. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3918 — plastic floor, wall and ceiling coverings. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3919", "Self-adhesive plates, sheets, film, foil, tape, strip and other flat shapes, of plastics", {
    "synonyms": ["adhesive tape", "plastic sticker sheet", "self-adhesive film", "BOPP tape"],
    "market_terms": ["packaging tape manufacturing", "self-adhesive film trade", "BOPP tape supply"],
    "hindi_transliterated": [],
    "examples": ["BOPP packing tape roll", "self-adhesive plastic label sheet"],
    "attributes": {"material": ["plastic film"], "use": ["packaging", "labelling"], "form": ["tape", "sheet", "roll"], "industry": ["plastics", "packaging"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Self-adhesive plastic flat shapes map uniquely to 3919.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3919 covers self-adhesive plates, sheets, film, foil, tape and strip of plastics — packing tape, adhesive labels and similar self-stick plastic products. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3919 — self-adhesive plastic sheets, film and tape. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3920", "Other plates, sheets, film, foil and strip of plastics, non-cellular and not reinforced, laminated or combined", {
    "synonyms": ["plastic sheet", "plastic film", "PVC sheet", "plastic foil"],
    "market_terms": ["plastic sheet/film manufacturing", "packaging film trade", "unsupported film supply"],
    "hindi_transliterated": [],
    "examples": ["plain plastic sheet for packaging", "PVC film roll"],
    "attributes": {"material": ["plastic (unsupported)"], "use": ["packaging", "general fabrication"], "form": ["sheet", "film", "foil"], "industry": ["plastics", "packaging"]},
    "clarification_questions": [{"question": "Is the sheet/film plain (not laminated, reinforced or combined with another material)?", "attribute": "form", "options": ["Plain plastic sheet/film", "Laminated/reinforced/combined"], "disambiguates_from": ["HSN_3921"]}],
    "exclusion_notes": [{"excluded_code": "HSN_3921", "reason": "3921 covers plastic sheet/film that is laminated, reinforced or combined with another material — 3920 is plain, non-cellular, unsupported plastic sheet/film"}],
    "classification_confidence": {"level": "Medium", "rationale": "The heading is defined by physical construction (plain, non-cellular, unsupported) versus the closely related 3921 (laminated/reinforced/cellular).", "ambiguity_triggers": ["laminated", "reinforced", "foam"]},
    "plain_rationale": "HSN 3920 covers plain plastic plates, sheets, film, foil and strip that are not cellular (foamed) and not laminated, reinforced or combined with another material. If your product is laminated or reinforced, it falls under HSN 3921 instead. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3920 — plain (unsupported) plastic sheet and film. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3921", "Other plates, sheets, film, foil and strip, of plastics (laminated, reinforced or cellular)", {
    "synonyms": ["laminated plastic sheet", "reinforced plastic film", "foam plastic sheet", "plastic laminate"],
    "market_terms": ["laminate manufacturing", "packaging laminate trade", "foam sheet supply"],
    "hindi_transliterated": [],
    "examples": ["laminated plastic packaging film", "foam plastic sheet for insulation"],
    "attributes": {"material": ["plastic (laminated/cellular)"], "use": ["packaging", "insulation"], "form": ["laminate", "foam sheet"], "industry": ["plastics", "packaging", "construction"]},
    "clarification_questions": [{"question": "Is the sheet/film laminated, reinforced, or cellular (foamed), or is it plain unsupported plastic?", "attribute": "form", "options": ["Laminated/reinforced/cellular", "Plain plastic sheet/film"], "disambiguates_from": ["HSN_3920"]}],
    "exclusion_notes": [{"excluded_code": "HSN_3920", "reason": "3920 is plain, non-cellular, unsupported plastic sheet/film — 3921 covers laminated, reinforced, or cellular (foamed) versions"}],
    "classification_confidence": {"level": "Medium", "rationale": "The heading is defined by physical construction (laminated/reinforced/cellular) versus the closely related plain-sheet heading 3920.", "ambiguity_triggers": ["plain sheet", "unsupported"]},
    "plain_rationale": "HSN 3921 covers plastic plates, sheets, film, foil and strip that are laminated, reinforced, or cellular (foamed) — as opposed to plain unsupported sheet under HSN 3920. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3921 — laminated/reinforced/cellular plastic sheet and film. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3922", "Baths, sinks, wash-basins, lavatory pans, seats and covers, flushing cisterns and similar sanitary ware, of plastics", {
    "synonyms": ["plastic toilet seat", "plastic wash basin", "plastic bathtub", "PVC cistern"],
    "market_terms": ["plastic sanitaryware manufacturing", "bathroom fitting trade", "sanitary fixture supply"],
    "hindi_transliterated": [],
    "examples": ["plastic toilet seat and cover", "PVC flushing cistern"],
    "attributes": {"material": ["plastic", "PVC"], "use": ["bathroom fittings"], "form": ["moulded sanitary ware"], "industry": ["plastics", "construction", "sanitaryware"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Plastic sanitary ware maps uniquely to 3922.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3922 covers baths, wash-basins, toilet seats and covers, flushing cisterns and similar sanitary ware made of plastic. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3922 — plastic sanitary ware. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3923", "Articles for the conveyance or packing of goods, of plastics; stoppers, lids, caps and other closures, of plastics", {
    "synonyms": ["plastic bottle", "plastic container", "plastic cap", "plastic packaging box", "plastic pouch"],
    "market_terms": ["plastic packaging manufacturing", "PET bottle supply", "closures & caps trade"],
    "hindi_transliterated": [],
    "examples": ["PET bottle for beverage packaging", "plastic screw cap/closure", "plastic storage container"],
    "attributes": {"material": ["plastic", "PET", "HDPE"], "use": ["packaging"], "form": ["bottle", "container", "cap", "pouch"], "industry": ["plastics", "packaging", "fmcg"]},
    "clarification_questions": [], "exclusion_notes": [{"excluded_code": "HSN_3924", "reason": "3924 is household tableware/kitchenware — 3923 is packaging articles (bottles, caps, containers) used to convey or pack goods for sale"}],
    "classification_confidence": {"level": "High", "rationale": "Plastic packaging articles and closures map clearly to 3923; the main risk is confusing them with household plastic goods under 3924.", "ambiguity_triggers": ["household", "tableware", "kitchenware"]},
    "plain_rationale": "HSN 3923 covers plastic articles used for conveying or packing goods — bottles, containers, jars, boxes, and closures like caps, lids and stoppers. If you manufacture or sell plastic packaging materials, this is your code. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3923 — plastic packing/conveyance articles and closures. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3924", "Tableware, kitchenware, other household articles and hygienic or toilet articles, of plastics", {
    "synonyms": ["plastic tableware", "plastic kitchenware", "plastic mug", "plastic bucket", "plastic storage box"],
    "market_terms": ["plastic houseware manufacturing", "kitchenware retail", "plastic bucket/mug trade"],
    "hindi_transliterated": [],
    "examples": ["plastic dinner plate set", "plastic bucket and mug", "plastic lunch box"],
    "attributes": {"material": ["plastic"], "use": ["household use", "kitchen use"], "form": ["tableware", "kitchenware", "storage container"], "industry": ["plastics", "houseware", "fmcg"]},
    "clarification_questions": [], "exclusion_notes": [{"excluded_code": "HSN_3923", "reason": "3923 is packaging articles (bottles, caps, containers used to pack goods) — 3924 is finished household tableware and kitchenware sold for direct use"}],
    "classification_confidence": {"level": "High", "rationale": "Household plastic tableware and kitchenware map clearly to 3924; the main risk is confusing them with packaging articles under 3923.", "ambiguity_triggers": ["packaging", "bottle", "container for goods"]},
    "plain_rationale": "HSN 3924 covers plastic tableware, kitchenware, other household articles, and hygienic or toilet articles — plates, mugs, buckets, storage boxes and similar everyday plastic household goods. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3924 — plastic tableware, kitchenware and household articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3925", "Builders' ware of plastics, not elsewhere specified or included", {
    "synonyms": ["plastic door/window frame", "plastic water tank", "PVC builders ware", "plastic gutter"],
    "market_terms": ["plastic building material trade", "PVC fitting for construction", "builders' hardware supply"],
    "hindi_transliterated": [],
    "examples": ["PVC window frame", "plastic overhead water storage tank"],
    "attributes": {"material": ["plastic", "PVC"], "use": ["construction", "building fittings"], "form": ["frame", "tank", "fitting"], "industry": ["plastics", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Plastic builders' ware not elsewhere specified maps clearly to 3925.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 3925 covers builders' ware of plastics not elsewhere specified — window and door frames, water storage tanks, gutters and similar plastic construction fittings. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3925 — builders' ware of plastics. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_3926", "Other articles of plastics and articles of other materials of headings 39.01 to 39.14", {
    "synonyms": ["plastic bangles", "plastic bead", "feeding bottle (plastic)", "misc plastic component", "plastic novelty item"],
    "market_terms": ["plastic component manufacturing", "plastic novelty item trade", "moulded plastic goods supply"],
    "hindi_transliterated": ["choodi"],
    "examples": ["plastic bangles sold in a set", "plastic baby feeding bottle", "miscellaneous moulded plastic component"],
    "attributes": {"material": ["plastic"], "use": ["miscellaneous"], "form": ["moulded article"], "industry": ["plastics", "manufacturing"]},
    "clarification_questions": [{"question": "Is the item plastic bangles, plastic beads, or a feeding bottle?", "attribute": "use", "options": ["Yes, one of these specific items", "No, a different plastic article"], "disambiguates_from": []}],
    "exclusion_notes": [{"excluded_code": "HSN_3923", "reason": "3923 is packaging articles (bottles, caps, containers) — 3926 is the residual 'other' bucket for plastic articles not covered by any more specific heading in this chapter"}],
    "classification_confidence": {"level": "Medium", "rationale": "This is a residual 'other articles of plastics' heading covering many unrelated products; the specific item decides which of two very different rates applies.", "ambiguity_triggers": ["packaging", "household article", "toy"]},
    "plain_rationale": "HSN 3926 is a residual 'other articles of plastics' heading covering items not classified elsewhere in this chapter — miscellaneous moulded plastic components and, specifically, plastic bangles, beads and feeding bottles. The base rate is 5%, but this specifically applies only to bangles, beads and feeding bottles — most other articles in this heading actually attract 18% instead. Check which bucket your product falls into before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 39, Heading 3926 — other articles of plastics. Rate per Notification 9/2025-Integrated Tax (Rate).",
}, exceptions=[{"gst_rate": 18.0, "condition": "Other plastic articles generally, except bangles, beads and feeding bottles (which keep the 5% rate)"}])


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
