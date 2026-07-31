"""
Wave 2, Chapter 29 (organic chemicals) — 41 heading-level records. Same
harness as prior waves. Every heading in this chapter shares one shape:
rate_confidence "low", rate_scope "chapter", and an identical exception
("All organic chemicals other than gibberellic acid" at 18%) — factored
into add29() below.

This chapter is pure B2B industrial/pharma/specialty chemistry, organised
by functional group rather than product identity, so it has essentially no
natural-language classification ambiguity per heading (each functional
group is chemically distinct). Records are intentionally lean (4 synonyms,
named well-known example compounds per class) rather than padded.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import load_master, validate, finalize, write_jsonl
from wave1_records import build_record

MASTER = load_master()

CH29_HEADINGS = [f"HSN_29{n:02d}" for n in range(1, 40)] + ["HSN_2941", "HSN_2942"]  # 2901-2939, 2941-2942

CH29_CAVEAT = "Rate inferred from the Chapter 29 entry, not a rule written for this specific heading. Most organic chemicals attract 18% except gibberellic acid; verify against Notification 9/2025 before invoicing."
CH29_EXC = [{"gst_rate": 18.0, "condition": "All organic chemicals except gibberellic acid, which keeps the 5% rate"}]

RECORDS = []


def add29(mid, title, ai, status="complete", exclusion_notes=None):
    if exclusion_notes is not None:
        ai["exclusion_notes"] = exclusion_notes
    RECORDS.append((mid, CH29_HEADINGS, title, ai, status, CH29_EXC, CH29_CAVEAT))


add29("HSN_2901", "Acyclic hydrocarbons", {
    "synonyms": ["ethylene (chemical)", "propylene (chemical)", "butane", "acyclic hydrocarbon"],
    "market_terms": ["petrochemical feedstock trade", "LPG/hydrocarbon raw material supply", "polymer feedstock trade"],
    "hindi_transliterated": [], "examples": ["ethylene gas used as a petrochemical/polymer feedstock", "butane used as an LPG component"],
    "attributes": {"material": ["hydrocarbon"], "use": ["petrochemical feedstock"], "form": ["gas", "liquid"], "industry": ["chemicals", "petrochemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Acyclic (open-chain) hydrocarbons map uniquely to 2901 by chemical structure.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2901 covers acyclic (open-chain) hydrocarbons — ethylene, propylene, butane and similar petrochemical feedstocks used as raw material for plastics and fuels.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2901 — acyclic hydrocarbons. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2902", "Cyclic hydrocarbons", {
    "synonyms": ["benzene", "toluene", "xylene", "cyclic hydrocarbon"],
    "market_terms": ["petrochemical feedstock trade", "solvent raw material supply", "aromatic hydrocarbon trade"],
    "hindi_transliterated": [], "examples": ["benzene used as an industrial solvent/petrochemical feedstock", "toluene used as a paint/adhesive solvent"],
    "attributes": {"material": ["hydrocarbon"], "use": ["solvent", "petrochemical feedstock"], "form": ["liquid"], "industry": ["chemicals", "petrochemicals", "paints"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Cyclic (ring-structure) hydrocarbons like benzene and toluene map uniquely to 2902.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2902 covers cyclic hydrocarbons — benzene, toluene and xylene are the classic aromatic examples, widely used as industrial solvents and petrochemical feedstock.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2902 — cyclic hydrocarbons. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2903", "Halogenated derivatives of hydrocarbons", {
    "synonyms": ["chloroform", "carbon tetrachloride", "dichloromethane", "halogenated solvent"],
    "market_terms": ["industrial solvent trade", "refrigerant raw material supply", "pesticide intermediate trade"],
    "hindi_transliterated": [], "examples": ["dichloromethane used as an industrial paint-stripping solvent", "chloroform used in pharmaceutical/chemical synthesis"],
    "attributes": {"material": ["halogenated hydrocarbon"], "use": ["solvent", "chemical synthesis"], "form": ["liquid"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Halogenated hydrocarbon derivatives map uniquely to 2903.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2903 covers halogenated derivatives of hydrocarbons — chlorinated solvents like dichloromethane and chloroform, used in industrial cleaning and pharmaceutical synthesis.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2903 — halogenated hydrocarbon derivatives. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2904", "Sulphonated, nitrated or nitrosated derivatives of hydrocarbons", {
    "synonyms": ["trinitrotoluene (TNT)", "sulphonated hydrocarbon", "nitro compound", "detergent intermediate (sulphonate)"],
    "market_terms": ["explosives raw material trade", "specialty chemical trade", "detergent intermediate trade"],
    "hindi_transliterated": [], "examples": ["TNT used in explosives/mining blasting agent manufacturing", "sulphonated hydrocarbon used as a detergent intermediate"],
    "attributes": {"material": ["sulphonated/nitrated hydrocarbon"], "use": ["explosives", "detergent manufacturing"], "form": ["solid", "liquid"], "industry": ["chemicals", "mining", "detergents"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sulphonated, nitrated or nitrosated hydrocarbon derivatives map uniquely to 2904.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2904 covers sulphonated, nitrated or nitrosated hydrocarbon derivatives — TNT is the best-known nitro compound, while sulphonated hydrocarbons are used as detergent intermediates. This is a tightly regulated category.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2904 — sulphonated/nitrated hydrocarbon derivatives. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2905", "Acyclic alcohols and their halogenated, sulphonated, nitrated or nitrosated derivatives", {
    "synonyms": ["ethanol", "methanol", "isopropyl alcohol (IPA)", "glycerol"],
    "market_terms": ["industrial alcohol trade", "solvent raw material supply", "sanitiser raw material trade"],
    "hindi_transliterated": [], "examples": ["isopropyl alcohol (IPA) used in hand sanitiser manufacturing", "methanol used as an industrial solvent/fuel additive"],
    "attributes": {"material": ["acyclic alcohol"], "use": ["solvent", "sanitiser/disinfectant manufacturing"], "form": ["liquid"], "industry": ["chemicals", "personal care", "fuel"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Acyclic (open-chain) alcohols like ethanol, methanol and IPA map uniquely to 2905.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2905 covers acyclic alcohols — ethanol, methanol, isopropyl alcohol (IPA) and glycerol are common examples, used across solvents, sanitisers and fuel additives.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2905 — acyclic alcohols. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2906", "Cyclic alcohols and their halogenated, sulphonated, nitrated or nitrosated derivatives", {
    "synonyms": ["cyclohexanol", "menthol", "terpene alcohol", "cyclic alcohol"],
    "market_terms": ["fragrance/flavour raw material trade", "specialty chemical trade", "nylon raw material trade"],
    "hindi_transliterated": [], "examples": ["menthol used in flavouring and pharmaceutical formulations", "cyclohexanol used as a nylon manufacturing raw material"],
    "attributes": {"material": ["cyclic alcohol"], "use": ["flavouring", "pharmaceuticals", "fibre manufacturing"], "form": ["liquid", "crystal"], "industry": ["chemicals", "food/flavour", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Cyclic (ring-structure) alcohols like menthol and cyclohexanol map uniquely to 2906.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2906 covers cyclic alcohols — menthol is the best-known example (flavouring, pharma), while cyclohexanol is a nylon manufacturing raw material.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2906 — cyclic alcohols. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2907", "Phenols; phenol-alcohols", {
    "synonyms": ["phenol", "cresol", "carbolic acid", "phenol-alcohol"],
    "market_terms": ["resin raw material trade", "disinfectant raw material supply", "specialty chemical trade"],
    "hindi_transliterated": [], "examples": ["phenol used in phenolic resin manufacturing", "cresol used as a disinfectant raw material"],
    "attributes": {"material": ["phenol"], "use": ["resin manufacturing", "disinfectants"], "form": ["solid", "liquid"], "industry": ["chemicals", "plastics/resins"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Phenols and phenol-alcohols map uniquely to 2907.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2907 covers phenols and phenol-alcohols — phenol (carbolic acid) is a key raw material for phenolic resins, and cresol is used in disinfectant manufacturing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2907 — phenols and phenol-alcohols. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2908", "Halogenated, sulphonated, nitrated or nitrosated derivatives of phenols or phenol-alcohols", {
    "synonyms": ["chlorophenol", "nitrophenol", "picric acid", "halogenated phenol"],
    "market_terms": ["specialty chemical trade", "pesticide intermediate trade", "wood preservative raw material trade"],
    "hindi_transliterated": [], "examples": ["chlorophenol used as a pesticide/wood preservative intermediate", "picric acid used in chemical synthesis"],
    "attributes": {"material": ["halogenated phenol"], "use": ["pesticide manufacturing", "chemical synthesis"], "form": ["solid", "liquid"], "industry": ["chemicals", "agrochemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Halogenated, sulphonated, nitrated or nitrosated phenol derivatives map uniquely to 2908.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2908 covers halogenated, sulphonated, nitrated or nitrosated derivatives of phenols — used as pesticide/wood preservative intermediates and in chemical synthesis.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2908 — halogenated/nitrated phenol derivatives. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2909", "Ethers, ether-alcohols, ether-phenols, alcohol peroxides, ether peroxides and related peroxides", {
    "synonyms": ["diethyl ether", "ethylene glycol ether", "MTBE", "ether compound"],
    "market_terms": ["solvent raw material trade", "fuel additive trade", "specialty chemical trade"],
    "hindi_transliterated": [], "examples": ["diethyl ether used as a laboratory/industrial solvent", "MTBE used as a petrol fuel additive"],
    "attributes": {"material": ["ether"], "use": ["solvent", "fuel additive"], "form": ["liquid"], "industry": ["chemicals", "fuel/energy"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Ethers, ether-alcohols, ether-phenols and related peroxides map uniquely to 2909.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2909 covers ethers, ether-alcohols, ether-phenols and related peroxide compounds — diethyl ether is a common laboratory solvent, and MTBE is used as a petrol additive.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2909 — ethers and ether-alcohols. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2910", "Epoxides, epoxyalcohols, epoxyphenols and epoxyethers, with a three-membered ring", {
    "synonyms": ["epichlorohydrin", "ethylene oxide", "propylene oxide", "epoxide compound"],
    "market_terms": ["epoxy resin raw material trade", "specialty chemical trade", "sterilisation gas trade"],
    "hindi_transliterated": [], "examples": ["epichlorohydrin used in epoxy resin manufacturing", "ethylene oxide used for medical device sterilisation and chemical synthesis"],
    "attributes": {"material": ["epoxide"], "use": ["resin manufacturing", "sterilisation"], "form": ["liquid", "gas"], "industry": ["chemicals", "plastics/resins", "healthcare"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Three-membered-ring epoxides map uniquely to 2910.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2910 covers epoxides with a three-membered ring — epichlorohydrin is the key epoxy resin raw material, and ethylene oxide is widely used for sterilisation and chemical synthesis.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2910 — epoxides (three-membered ring). Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2911", "Acetals and hemiacetals, and their halogenated/sulphonated/nitrated derivatives", {
    "synonyms": ["acetal compound", "hemiacetal compound", "formaldehyde acetal", "cyclic acetal"],
    "market_terms": ["specialty chemical trade", "fragrance raw material trade", "flavour compound trade"],
    "hindi_transliterated": [], "examples": ["acetal compound used in fragrance/flavour formulation", "hemiacetal intermediate used in specialty chemical synthesis"],
    "attributes": {"material": ["acetal", "hemiacetal"], "use": ["fragrance/flavour", "chemical synthesis"], "form": ["liquid"], "industry": ["chemicals", "food/flavour"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Acetals and hemiacetals map uniquely to 2911.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2911 covers acetals and hemiacetals and their halogenated/sulphonated/nitrated derivatives — used in fragrance formulation and as specialty chemical intermediates.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2911 — acetals and hemiacetals. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2912", "Aldehydes; cyclic polymers of aldehydes; paraformaldehyde", {
    "synonyms": ["formaldehyde", "acetaldehyde", "paraformaldehyde", "vanillin"],
    "market_terms": ["resin raw material trade", "disinfectant raw material supply", "flavour/fragrance raw material trade"],
    "hindi_transliterated": [], "examples": ["formaldehyde used in resin and disinfectant manufacturing", "vanillin used as a flavouring agent"],
    "attributes": {"material": ["aldehyde"], "use": ["resin manufacturing", "flavouring"], "form": ["liquid", "solid"], "industry": ["chemicals", "food/flavour"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Aldehydes and their cyclic polymers map uniquely to 2912.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2912 covers aldehydes, cyclic aldehyde polymers and paraformaldehyde — formaldehyde is a key resin/disinfectant raw material, and vanillin is a widely used flavouring agent.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2912 — aldehydes and paraformaldehyde. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2913", "Halogenated, sulphonated, nitrated or nitrosated derivatives of products of heading 29.12", {
    "synonyms": ["chloral", "aldehyde derivative (halogenated)", "halogenated aldehyde compound", "chloral hydrate"],
    "market_terms": ["specialty chemical trade", "pesticide intermediate trade", "pharmaceutical intermediate trade"],
    "hindi_transliterated": [], "examples": ["chloral used as a chemical intermediate in industrial synthesis", "halogenated aldehyde derivative used in specialty organic synthesis"],
    "attributes": {"material": ["halogenated aldehyde"], "use": ["chemical synthesis"], "form": ["liquid"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Halogenated/nitrated derivatives of aldehydes map uniquely to 2913, distinct from the parent aldehydes under 2912.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2913 covers halogenated, sulphonated, nitrated or nitrosated derivatives of the aldehydes classified under heading 2912 — chloral is a well-known example, used in chemical synthesis.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2913 — halogenated aldehyde derivatives. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2914", "Ketones and quinones, and their halogenated, sulphonated, nitrated or nitrosated derivatives", {
    "synonyms": ["acetone", "methyl ethyl ketone (MEK)", "cyclohexanone", "quinone"],
    "market_terms": ["industrial solvent trade", "nylon raw material supply", "paint/coating solvent trade"],
    "hindi_transliterated": [], "examples": ["acetone used as an industrial and nail-polish-remover solvent", "MEK used as a paint and adhesive solvent"],
    "attributes": {"material": ["ketone"], "use": ["solvent", "fibre manufacturing"], "form": ["liquid"], "industry": ["chemicals", "paints", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Ketones and quinones like acetone and MEK map uniquely to 2914.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2914 covers ketones and quinones — acetone and MEK are everyday industrial solvents, while cyclohexanone is a nylon manufacturing raw material.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2914 — ketones and quinones. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2915", "Saturated acyclic monocarboxylic acids and their anhydrides, halides, peroxides and peroxyacids", {
    "synonyms": ["acetic acid", "formic acid", "propionic acid", "glacial acetic acid"],
    "market_terms": ["food/industrial acid trade", "preservative raw material supply", "textile chemical trade"],
    "hindi_transliterated": [], "examples": ["acetic acid (glacial) used in industrial and food-grade vinegar production", "formic acid used in leather tanning/textile processing"],
    "attributes": {"material": ["carboxylic acid"], "use": ["food processing", "leather tanning", "textiles"], "form": ["liquid"], "industry": ["chemicals", "food processing", "leather"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Saturated acyclic monocarboxylic acids like acetic and formic acid map uniquely to 2915.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2915 covers saturated acyclic monocarboxylic acids — acetic acid (used to make vinegar) and formic acid (used in leather tanning) are the most common examples.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2915 — saturated acyclic monocarboxylic acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2916", "Unsaturated acyclic monocarboxylic acids, cyclic monocarboxylic acids, and their derivatives", {
    "synonyms": ["acrylic acid", "benzoic acid", "sorbic acid", "unsaturated carboxylic acid"],
    "market_terms": ["preservative raw material trade", "polymer raw material supply", "specialty chemical trade"],
    "hindi_transliterated": [], "examples": ["acrylic acid used as a raw material for superabsorbent polymers/paints", "benzoic acid used as a food preservative raw material"],
    "attributes": {"material": ["carboxylic acid"], "use": ["polymer manufacturing", "food preservation"], "form": ["liquid", "solid"], "industry": ["chemicals", "food processing", "plastics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Unsaturated and cyclic monocarboxylic acids like acrylic and benzoic acid map uniquely to 2916.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2916 covers unsaturated acyclic and cyclic monocarboxylic acids — acrylic acid (superabsorbent polymers, paints) and benzoic acid (food preservative) are key examples.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2916 — unsaturated/cyclic monocarboxylic acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2917", "Polycarboxylic acids, their anhydrides, halides, peroxides and peroxyacids", {
    "synonyms": ["phthalic anhydride", "adipic acid", "maleic anhydride", "polycarboxylic acid"],
    "market_terms": ["plasticiser raw material trade", "polyester raw material supply", "nylon raw material trade"],
    "hindi_transliterated": [], "examples": ["phthalic anhydride used in plasticiser/PVC manufacturing", "adipic acid used in nylon manufacturing"],
    "attributes": {"material": ["polycarboxylic acid"], "use": ["plastics/plasticiser manufacturing", "fibre manufacturing"], "form": ["solid", "liquid"], "industry": ["chemicals", "plastics", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Polycarboxylic acids like phthalic anhydride and adipic acid map uniquely to 2917.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2917 covers polycarboxylic acids and their anhydrides/halides/peroxides — phthalic anhydride (plasticisers, PVC) and adipic acid (nylon) are the key industrial examples.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2917 — polycarboxylic acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2918", "Carboxylic acids with additional oxygen function, and their derivatives", {
    "synonyms": ["citric acid", "lactic acid", "salicylic acid", "tartaric acid"],
    "market_terms": ["food acidulant raw material trade", "pharma raw material supply", "cosmetic raw material trade"],
    "hindi_transliterated": [], "examples": ["citric acid used as a food/beverage acidulant", "salicylic acid used in pharma and cosmetic (acne treatment) formulations"],
    "attributes": {"material": ["carboxylic acid (oxygen-function)"], "use": ["food processing", "pharmaceuticals", "cosmetics"], "form": ["powder", "crystal"], "industry": ["chemicals", "food processing", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Carboxylic acids with additional oxygen function, like citric and salicylic acid, map uniquely to 2918.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2918 covers carboxylic acids with additional oxygen function — citric acid (food acidulant) and salicylic acid (pharma/cosmetics) are everyday examples.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2918 — oxygen-function carboxylic acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2919", "Phosphoric esters and their salts, including lactophosphates", {
    "synonyms": ["tributyl phosphate", "phosphate ester", "lactophosphate", "flame retardant phosphate ester"],
    "market_terms": ["plasticiser raw material trade", "flame retardant raw material trade", "extraction solvent trade"],
    "hindi_transliterated": [], "examples": ["phosphate ester used as a plasticiser/flame retardant raw material", "tributyl phosphate used as an industrial extraction solvent"],
    "attributes": {"material": ["phosphate ester"], "use": ["plasticiser manufacturing", "flame retardant manufacturing"], "form": ["liquid"], "industry": ["chemicals", "plastics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Phosphoric esters and their salts map uniquely to 2919.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2919 covers phosphoric esters and their salts, including lactophosphates — used as plasticiser and flame-retardant raw material, and as industrial extraction solvents.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2919 — phosphoric esters. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2920", "Esters of other inorganic acids of non-metals (excluding hydrogen halide esters) and their salts", {
    "synonyms": ["dimethyl sulphate", "sulphate ester", "nitrite/nitrate ester", "inorganic ester compound"],
    "market_terms": ["specialty chemical trade", "pharmaceutical intermediate trade", "methylating agent trade"],
    "hindi_transliterated": [], "examples": ["dimethyl sulphate used as a methylating agent in chemical synthesis", "inorganic ester compound used in specialty organic synthesis"],
    "attributes": {"material": ["inorganic acid ester"], "use": ["chemical synthesis"], "form": ["liquid"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Esters of inorganic acids of non-metals (excluding hydrogen halides) map uniquely to 2920.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2920 covers esters of other inorganic acids of non-metals (excluding hydrogen halide esters) and their salts — dimethyl sulphate is a widely used methylating agent in chemical synthesis.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2920 — esters of inorganic non-metal acids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2921", "Amine-function compounds", {
    "synonyms": ["aniline", "ethylenediamine", "triethanolamine", "amine compound"],
    "market_terms": ["dye/pigment raw material trade", "surfactant raw material supply", "rubber chemical trade"],
    "hindi_transliterated": [], "examples": ["aniline used in dye and rubber chemical manufacturing", "triethanolamine used in surfactant/cosmetic formulation"],
    "attributes": {"material": ["amine"], "use": ["dye manufacturing", "surfactant manufacturing"], "form": ["liquid"], "industry": ["chemicals", "textiles", "cosmetics"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Amine-function compounds like aniline and triethanolamine map uniquely to 2921.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2921 covers amine-function compounds — aniline is a key dye/rubber chemical raw material, and triethanolamine is used in surfactant and cosmetic formulation.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2921 — amine-function compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2922", "Oxygen-function amino-compounds", {
    "synonyms": ["glutamic acid (industrial)", "amino alcohol", "monosodium glutamate precursor", "amino-oxygen compound"],
    "market_terms": ["food additive raw material trade", "pharma intermediate trade", "amino compound supply"],
    "hindi_transliterated": [], "examples": ["amino alcohol compound used as a pharmaceutical intermediate", "glutamic acid derivative used in food additive (MSG) manufacturing"],
    "attributes": {"material": ["amino compound"], "use": ["food additive manufacturing", "pharmaceutical manufacturing"], "form": ["powder", "liquid"], "industry": ["chemicals", "food processing", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Oxygen-function amino-compounds like glutamic acid derivatives map uniquely to 2922.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2922 covers oxygen-function amino-compounds — glutamic acid derivatives (used to make MSG) and amino alcohols (pharmaceutical intermediates) are key examples.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2922 — oxygen-function amino-compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2923", "Quaternary ammonium salts and hydroxides; lecithins and other phosphoaminolipids", {
    "synonyms": ["lecithin", "quaternary ammonium compound", "cationic surfactant (quat)", "choline chloride"],
    "market_terms": ["surfactant raw material trade", "food/pharma additive supply", "disinfectant raw material trade"],
    "hindi_transliterated": [], "examples": ["lecithin used as a food emulsifier", "quaternary ammonium compound used in fabric softener/disinfectant manufacturing"],
    "attributes": {"material": ["quaternary ammonium salt", "lecithin"], "use": ["food additive", "surfactant manufacturing", "disinfection"], "form": ["liquid", "powder"], "industry": ["chemicals", "food processing", "personal care"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Quaternary ammonium salts and lecithins map uniquely to 2923.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2923 covers quaternary ammonium salts and hydroxides, and lecithins and other phosphoaminolipids — lecithin is a common food emulsifier, and quaternary ammonium compounds are used in fabric softeners and disinfectants.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2923 — quaternary ammonium salts; lecithins. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2924", "Carboxyamide-function compounds; amide-function compounds of carbonic acid", {
    "synonyms": ["acetamide", "paracetamol intermediate", "amide compound", "urea derivative (amide)"],
    "market_terms": ["pharma intermediate trade", "agrochemical raw material trade", "specialty chemical trade"],
    "hindi_transliterated": [], "examples": ["amide compound used as a pharmaceutical intermediate", "acetamide used in industrial chemical synthesis"],
    "attributes": {"material": ["amide"], "use": ["pharmaceutical manufacturing", "agrochemical manufacturing"], "form": ["powder", "liquid"], "industry": ["chemicals", "pharmaceuticals", "agrochemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Carboxyamide-function compounds map uniquely to 2924.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2924 covers carboxyamide-function compounds and amide-function compounds of carbonic acid — widely used as pharmaceutical and agrochemical intermediates.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2924 — carboxyamide-function compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2925", "Carboxyimide-function compounds (including saccharin and its salts) and imine-function compounds", {
    "synonyms": ["saccharin", "imide compound", "imine compound", "sweetener raw material"],
    "market_terms": ["artificial sweetener raw material trade", "pharma intermediate trade", "polymer raw material trade"],
    "hindi_transliterated": [], "examples": ["saccharin used as an artificial sweetener", "imide compound used in pharmaceutical/polymer synthesis"],
    "attributes": {"material": ["imide", "imine"], "use": ["food sweetener manufacturing", "pharmaceutical manufacturing"], "form": ["powder"], "industry": ["chemicals", "food processing", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Carboxyimide- and imine-function compounds, including saccharin, map uniquely to 2925.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2925 covers carboxyimide-function compounds (including the artificial sweetener saccharin and its salts) and imine-function compounds.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2925 — carboxyimide/imine compounds (incl. saccharin). Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2926", "Nitrile-function compounds", {
    "synonyms": ["acrylonitrile", "acetonitrile", "nitrile compound", "ABS plastic raw material"],
    "market_terms": ["acrylic fibre raw material trade", "solvent raw material supply", "plastics raw material trade"],
    "hindi_transliterated": [], "examples": ["acrylonitrile used as a raw material for acrylic fibre/ABS plastic manufacturing", "acetonitrile used as an industrial/laboratory solvent"],
    "attributes": {"material": ["nitrile"], "use": ["fibre/plastic manufacturing", "solvent"], "form": ["liquid"], "industry": ["chemicals", "plastics", "textiles"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Nitrile-function compounds like acrylonitrile map uniquely to 2926.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2926 covers nitrile-function compounds — acrylonitrile is the raw material for acrylic fibre and ABS plastic, while acetonitrile is a common industrial solvent.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2926 — nitrile-function compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2927", "Diazo-, azo- or azoxy-compounds", {
    "synonyms": ["azo dye intermediate", "diazo compound", "azo compound", "textile dye intermediate"],
    "market_terms": ["dye/pigment raw material trade", "textile chemical trade", "industrial colourant trade"],
    "hindi_transliterated": [], "examples": ["azo compound used as a dye/pigment intermediate for textiles", "diazo compound used in industrial dye manufacturing"],
    "attributes": {"material": ["azo compound"], "use": ["dye/pigment manufacturing"], "form": ["powder"], "industry": ["chemicals", "textiles", "dyes"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Diazo-, azo- and azoxy-compounds map uniquely to 2927.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2927 covers diazo-, azo- and azoxy-compounds — the core intermediates for azo dyes, one of the most widely used textile dye classes.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2927 — diazo/azo/azoxy compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2928", "Organic derivatives of hydrazine or of hydroxylamine", {
    "synonyms": ["phenylhydrazine", "hydrazine derivative (organic)", "hydroxylamine derivative", "pesticide intermediate (hydrazine)"],
    "market_terms": ["pharma intermediate trade", "agrochemical raw material trade", "specialty chemical trade"],
    "hindi_transliterated": [], "examples": ["organic hydrazine derivative used as a pharmaceutical/agrochemical intermediate", "phenylhydrazine used in chemical synthesis"],
    "attributes": {"material": ["organic hydrazine/hydroxylamine derivative"], "use": ["pharmaceutical manufacturing", "agrochemical manufacturing"], "form": ["liquid", "powder"], "industry": ["chemicals", "pharmaceuticals", "agrochemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Organic derivatives of hydrazine or hydroxylamine map uniquely to 2928.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2928 covers organic derivatives of hydrazine or hydroxylamine — used as pharmaceutical and agrochemical intermediates.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2928 — organic hydrazine/hydroxylamine derivatives. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2929", "Compounds with other nitrogen function", {
    "synonyms": ["isocyanate", "toluene diisocyanate (TDI)", "polyurethane raw material (isocyanate)", "nitrogen-function compound"],
    "market_terms": ["polyurethane raw material trade", "specialty chemical trade", "coating raw material trade"],
    "hindi_transliterated": [], "examples": ["toluene diisocyanate (TDI) used as a polyurethane foam raw material", "isocyanate compound used in coating manufacturing"],
    "attributes": {"material": ["isocyanate"], "use": ["polyurethane manufacturing", "coating manufacturing"], "form": ["liquid"], "industry": ["chemicals", "plastics/foams", "coatings"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Compounds with other nitrogen function, chiefly isocyanates like TDI, map uniquely to 2929.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2929 covers compounds with other nitrogen function — toluene diisocyanate (TDI) is the key raw material for polyurethane foam manufacturing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2929 — other nitrogen-function compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2930", "Organo-sulphur compounds", {
    "synonyms": ["thiourea", "mercaptan", "dithiocarbamate", "organo-sulphur compound"],
    "market_terms": ["rubber chemical trade", "agrochemical raw material trade", "pharma intermediate trade"],
    "hindi_transliterated": [], "examples": ["dithiocarbamate used as a rubber vulcanisation accelerator/fungicide", "thiourea used in chemical synthesis"],
    "attributes": {"material": ["organo-sulphur compound"], "use": ["rubber manufacturing", "agrochemical manufacturing"], "form": ["powder", "liquid"], "industry": ["chemicals", "rubber", "agrochemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Organo-sulphur compounds like thiourea and dithiocarbamate map uniquely to 2930.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2930 covers organo-sulphur compounds — dithiocarbamates are widely used as rubber vulcanisation accelerators and agricultural fungicides.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2930 — organo-sulphur compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2931", "Other organo-inorganic compounds", {
    "synonyms": ["organosilicon compound", "organophosphorus compound", "organometallic compound", "silane coupling agent"],
    "market_terms": ["specialty chemical trade", "silicone raw material trade", "agrochemical intermediate trade"],
    "hindi_transliterated": [], "examples": ["organosilicon compound used in silicone/sealant manufacturing", "organophosphorus compound used as a pesticide/flame retardant intermediate"],
    "attributes": {"material": ["organo-inorganic compound"], "use": ["silicone manufacturing", "agrochemical manufacturing"], "form": ["liquid"], "industry": ["chemicals", "construction", "agrochemicals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Other organo-inorganic compounds (organosilicon, organophosphorus, organometallic) map to this residual heading 2931.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2931 covers other organo-inorganic compounds not classified elsewhere — organosilicon compounds (silicone/sealant raw material) and organophosphorus compounds (pesticide/flame-retardant intermediates) are common examples.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2931 — other organo-inorganic compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2932", "Heterocyclic compounds with oxygen hetero-atom(s) only", {
    "synonyms": ["furan", "tetrahydrofuran (THF)", "coumarin", "oxygen heterocyclic compound"],
    "market_terms": ["solvent raw material trade", "fragrance/flavour raw material supply", "specialty chemical trade"],
    "hindi_transliterated": [], "examples": ["tetrahydrofuran (THF) used as an industrial solvent", "coumarin used as a fragrance/flavour compound"],
    "attributes": {"material": ["oxygen heterocycle"], "use": ["solvent", "fragrance/flavour"], "form": ["liquid"], "industry": ["chemicals", "food/flavour"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Heterocyclic compounds with only oxygen hetero-atoms map uniquely to 2932.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2932 covers heterocyclic compounds with oxygen hetero-atoms only — THF is a widely used industrial solvent, and coumarin is a common fragrance/flavour compound.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2932 — oxygen-only heterocyclic compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2933", "Heterocyclic compounds with nitrogen hetero-atom(s) only", {
    "synonyms": ["caffeine", "pyridine", "imidazole", "pharmaceutical intermediate (nitrogen heterocycle)"],
    "market_terms": ["pharma raw material trade", "agrochemical intermediate trade", "beverage raw material trade"],
    "hindi_transliterated": [], "examples": ["caffeine (synthetic) used in pharma/beverage manufacturing", "pyridine used as an industrial solvent/pharma intermediate"],
    "attributes": {"material": ["nitrogen heterocycle"], "use": ["pharmaceutical manufacturing", "beverage manufacturing"], "form": ["powder", "liquid"], "industry": ["chemicals", "pharmaceuticals", "beverages"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Heterocyclic compounds with only nitrogen hetero-atoms, like caffeine and pyridine, map uniquely to 2933 — this is the largest and most pharma-relevant heading in the chapter.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2933 covers heterocyclic compounds with nitrogen hetero-atoms only — this very broad class includes caffeine and pyridine, and underlies most synthetic pharmaceutical active ingredients.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2933 — nitrogen-only heterocyclic compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2934", "Nucleic acids and their salts; other heterocyclic compounds", {
    "synonyms": ["nucleic acid", "biotech raw material", "other heterocyclic compound", "DNA/RNA component (industrial)"],
    "market_terms": ["pharma/biotech raw material trade", "research chemical supply", "specialty chemical trade"],
    "hindi_transliterated": [], "examples": ["nucleic acid derivative used in pharmaceutical/biotech manufacturing", "heterocyclic compound used as a pharmaceutical intermediate"],
    "attributes": {"material": ["nucleic acid", "heterocyclic compound"], "use": ["biotech/pharmaceutical manufacturing"], "form": ["powder", "solution"], "industry": ["chemicals", "biotechnology", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Nucleic acids and heterocyclic compounds not covered by 2932/2933 map to 2934.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2934 covers nucleic acids and their salts, plus other heterocyclic compounds not classified under 2932 or 2933 — used in biotech and pharmaceutical manufacturing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2934 — nucleic acids and other heterocyclic compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2935", "Sulphonamides", {
    "synonyms": ["sulphonamide", "sulfa drug intermediate", "sulphanilamide", "antimicrobial raw material"],
    "market_terms": ["pharma raw material trade", "antibacterial drug intermediate trade", "bulk drug API trade"],
    "hindi_transliterated": [], "examples": ["sulphonamide compound used as a pharmaceutical (antibacterial) raw material", "sulphanilamide used in sulfa-drug manufacturing"],
    "attributes": {"material": ["sulphonamide"], "use": ["pharmaceutical manufacturing"], "form": ["powder"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sulphonamides map uniquely to 2935.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2935 covers sulphonamides — the chemical class behind sulfa antibacterial drugs.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2935 — sulphonamides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2936", "Provitamins and vitamins, natural or synthetic, and their derivatives used primarily as vitamins", {
    "synonyms": ["vitamin C (ascorbic acid)", "vitamin premix", "vitamin B complex", "synthetic vitamin"],
    "market_terms": ["pharma/nutraceutical raw material trade", "food fortification raw material trade", "animal feed additive trade"],
    "hindi_transliterated": [], "examples": ["ascorbic acid (vitamin C) used in pharma/food fortification", "vitamin premix used in animal feed manufacturing"],
    "attributes": {"material": ["vitamin"], "use": ["food fortification", "pharmaceutical manufacturing", "animal feed"], "form": ["powder"], "industry": ["chemicals", "pharmaceuticals", "food processing", "animal feed"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Provitamins, vitamins and their vitamin-function derivatives map uniquely to 2936.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2936 covers provitamins and vitamins, natural or synthetic, and their derivatives used primarily as vitamins — raw material for pharma, food fortification and animal feed.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2936 — provitamins and vitamins. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2937", "Hormones, prostaglandins, thromboxanes and leukotrienes, natural or synthetic, and their derivatives", {
    "synonyms": ["insulin (synthetic/derived)", "cortisone", "synthetic hormone", "prostaglandin"],
    "market_terms": ["pharmaceutical raw material trade", "biotech raw material supply", "bulk drug API trade"],
    "hindi_transliterated": [], "examples": ["synthetic hormone compound used in pharmaceutical manufacturing", "cortisone used in anti-inflammatory drug formulation"],
    "attributes": {"material": ["hormone", "prostaglandin"], "use": ["pharmaceutical manufacturing"], "form": ["powder", "solution"], "industry": ["chemicals", "pharmaceuticals", "biotechnology"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Hormones, prostaglandins, thromboxanes and leukotrienes map uniquely to 2937.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2937 covers hormones, prostaglandins, thromboxanes and leukotrienes, natural or synthetic — key active pharmaceutical raw materials, including insulin and cortisone-type compounds.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2937 — hormones and related compounds. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2938", "Glycosides, natural or synthesised, and their salts, ethers, esters and other derivatives", {
    "synonyms": ["stevia glycoside", "digoxin", "rutin", "glycoside compound"],
    "market_terms": ["natural sweetener raw material trade", "pharma raw material supply", "food ingredient trade"],
    "hindi_transliterated": [], "examples": ["stevia glycoside used as a natural sweetener", "digoxin used as a cardiac pharmaceutical raw material"],
    "attributes": {"material": ["glycoside"], "use": ["food sweetener manufacturing", "pharmaceutical manufacturing"], "form": ["powder"], "industry": ["chemicals", "food processing", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Glycosides and their derivatives map uniquely to 2938.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2938 covers glycosides, natural or synthesised, and their derivatives — stevia glycoside is a well-known natural sweetener, and digoxin is a cardiac pharmaceutical raw material.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2938 — glycosides. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2939", "Alkaloids, natural or reproduced by synthesis, and their salts, ethers, esters and other derivatives", {
    "synonyms": ["caffeine (natural)", "morphine", "quinine", "nicotine"],
    "market_terms": ["pharma raw material trade", "alkaloid extraction trade", "bulk drug API trade"],
    "hindi_transliterated": [], "examples": ["quinine used in pharmaceutical (antimalarial) manufacturing", "morphine used as a controlled pharmaceutical raw material"],
    "attributes": {"material": ["alkaloid"], "use": ["pharmaceutical manufacturing"], "form": ["powder", "extract"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [],
    "exclusion_notes": [{"excluded_code": "HSN_2933", "reason": "Named heterocyclic drug intermediates without natural plant/alkaloid origin are usually classified under 2932-2934 instead of the alkaloid heading 2939"}],
    "classification_confidence": {"level": "Medium", "rationale": "The named alkaloids (quinine, morphine, caffeine, nicotine) map clearly here, but this heading has many unnamed residual sub-codes (e.g. 'other alkaloids') where a specific unfamiliar compound needs professional identification.", "ambiguity_triggers": ["synthetic heterocyclic drug", "unfamiliar plant extract"]},
    "plain_rationale": "HSN 2939 covers alkaloids, natural or synthesised, and their derivatives — quinine, morphine, caffeine and nicotine are the best-known examples. This is a controlled-substance-adjacent category; specific unfamiliar alkaloids should be confirmed with a regulatory/pharma professional.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2939 — alkaloids. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2941", "Antibiotics", {
    "synonyms": ["penicillin", "amoxicillin", "ciprofloxacin", "antibiotic (bulk drug)"],
    "market_terms": ["pharma bulk drug trade", "antibiotic API trade", "pharmaceutical formulation raw material trade"],
    "hindi_transliterated": [], "examples": ["amoxicillin bulk drug (API) used in pharmaceutical manufacturing", "penicillin used as an antibiotic raw material"],
    "attributes": {"material": ["antibiotic"], "use": ["pharmaceutical manufacturing"], "form": ["powder"], "industry": ["chemicals", "pharmaceuticals"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Antibiotics map uniquely to 2941.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 2941 covers antibiotics — bulk drug active pharmaceutical ingredients (APIs) like penicillin, amoxicillin and ciprofloxacin.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2941 — antibiotics. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add29("HSN_2942", "Other organic compounds", {
    "synonyms": ["miscellaneous organic compound", "specialty organic chemical", "unclassified organic chemical", "custom-synthesised organic compound"],
    "market_terms": ["specialty organic chemical trade", "chemical research trade", "custom synthesis chemical trade"],
    "hindi_transliterated": [], "examples": ["organic compound not classified under any more specific heading in this chapter", "specialty organic intermediate used in chemical research/synthesis"],
    "attributes": {"material": ["organic compound"], "use": ["chemical research/synthesis"], "form": ["various"], "industry": ["chemicals"]},
    "clarification_questions": [],
    "exclusion_notes": [{"excluded_code": "HSN_2933", "reason": "Check the specific functional-group headings elsewhere in this chapter (e.g. heterocyclic compounds under 2932-2934, acids under 2915-2918) before using this residual catch-all"}],
    "classification_confidence": {"level": "Low", "rationale": "This is the residual 'other organic compounds' catch-all for the entire chapter; reaching it correctly requires first ruling out every named functional-group heading.", "ambiguity_triggers": ["named functional group", "specific compound class"]},
    "plain_rationale": "HSN 2942 is a residual heading for organic compounds that don't fit any of the specific functional-group headings elsewhere in Chapter 29. Check whether your compound matches a named class (acid, amine, ketone, heterocycle, etc.) first — this code should be a last resort, and a tax professional or chemist should confirm the fit.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 29, Heading 2942 — other organic compounds.",
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
