"""
Wave 2, Chapter 73 (articles of iron or steel) — 26 heading-level records.
Same harness as prior waves. Rates are mostly heading-scope/medium-confidence
(no caveat needed); 7304/7308/7309 are heading-scope but low-confidence
(caveat auto-applied), and 7319/7326 are unresolved. Several headings
(7310, 7317, 7321, 7323) repeat the "inverted exception" pattern from Ch33/39:
the listed base rate is 5% but the exception text shows most goods in the
heading actually sit at 18%.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_harness import load_master, validate, finalize, write_jsonl
from wave1_records import build_record

MASTER = load_master()

CH73_HEADINGS = [f"HSN_73{n:02d}" for n in range(1, 27)]  # 7301-7326

RECORDS = []


def add(mid, title, ai, status="complete", exceptions=None, caveat=None):
    RECORDS.append((mid, CH73_HEADINGS, title, ai, status, exceptions or [], caveat))


add("HSN_7301", "Sheet piling of iron or steel; welded angles, shapes and sections, of iron or steel", {
    "synonyms": ["sheet piling", "steel angle section", "welded steel shape", "structural steel section"],
    "market_terms": ["structural steel trade", "construction steel supply", "steel fabrication raw material"],
    "hindi_transliterated": [], "examples": ["steel sheet piling for foundation work", "welded steel angle sections for fabrication"],
    "attributes": {"material": ["iron", "steel"], "use": ["construction", "structural fabrication"], "form": ["sheet piling", "angle/shape/section"], "industry": ["steel", "construction", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sheet piling and welded structural angles/shapes map clearly to 7301.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7301 covers steel sheet piling (used in foundations and retaining walls) and welded structural angles, shapes and sections of iron or steel. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7301 — sheet piling and welded structural sections. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7302", "Railway or tramway track construction material, of iron or steel", {
    "synonyms": ["railway rail", "steel sleeper", "fishplate", "rail switch blade"],
    "market_terms": ["railway track material supply", "rail infrastructure steel trade", "track fastener supply"],
    "hindi_transliterated": [], "examples": ["steel rails for railway track", "fishplates for rail joints"],
    "attributes": {"material": ["iron", "steel"], "use": ["railway infrastructure"], "form": ["rail", "sleeper", "fishplate"], "industry": ["steel", "railways", "infrastructure"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Railway/tramway track construction material maps uniquely to 7302.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7302 covers railway and tramway track construction material of iron or steel — rails, check-rails, switch blades, crossings, sleepers and fishplates. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7302 — railway/tramway track construction material. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7303", "Tubes, pipes and hollow profiles, of cast iron", {
    "synonyms": ["cast iron pipe", "cast iron tube", "cast iron drainage pipe", "cast iron water main"],
    "market_terms": ["cast iron pipe manufacturing", "water/sewer pipe supply", "foundry pipe trade"],
    "hindi_transliterated": [], "examples": ["cast iron water supply pipe", "cast iron drainage/sewer pipe"],
    "attributes": {"material": ["cast iron"], "use": ["water supply", "drainage/sewerage"], "form": ["pipe", "tube"], "industry": ["steel", "construction", "water infrastructure"]},
    "clarification_questions": [{"question": "Is the pipe cast iron, or seamless/welded steel?", "attribute": "material", "options": ["Cast iron", "Steel (seamless or welded)"], "disambiguates_from": ["HSN_7304"]}],
    "exclusion_notes": [{"excluded_code": "HSN_7304", "reason": "7304 is seamless tubes/pipes of iron (other than cast) or steel — 7303 is specifically cast iron"}],
    "classification_confidence": {"level": "Medium", "rationale": "Pipe classification here hinges on cast-iron vs. steel construction, which the plain description doesn't always state.", "ambiguity_triggers": ["steel pipe", "seamless", "welded"]},
    "plain_rationale": "HSN 7303 covers tubes, pipes and hollow profiles made specifically of cast iron — commonly used for water and sewer pipelines. Steel (non-cast) pipes fall under HSN 7304-7306 instead. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7303 — cast iron tubes, pipes and hollow profiles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7304", "Tubes, pipes and hollow profiles, seamless, of iron (other than cast iron) or steel", {
    "synonyms": ["seamless steel pipe", "seamless steel tube", "seamless pipe", "boiler tube"],
    "market_terms": ["seamless pipe manufacturing", "seamless tube supply", "oil & gas pipeline pipe trade"],
    "hindi_transliterated": [], "examples": ["seamless steel pipe for an oil & gas pipeline", "seamless tube for a boiler application"],
    "attributes": {"material": ["steel", "iron (non-cast)"], "use": ["piping", "pipeline", "boiler tubing"], "form": ["seamless pipe/tube"], "industry": ["steel", "oil & gas", "manufacturing"]},
    "clarification_questions": [{"question": "Is the pipe seamless, or welded/riveted?", "attribute": "form", "options": ["Seamless", "Welded/riveted"], "disambiguates_from": ["HSN_7305", "HSN_7306"]}],
    "exclusion_notes": [{"excluded_code": "HSN_7305", "reason": "7305 covers large-diameter welded/riveted pipes — 7304 is seamless only"}, {"excluded_code": "HSN_7303", "reason": "7303 is cast iron pipe — 7304 is seamless iron (non-cast) or steel pipe"}],
    "classification_confidence": {"level": "Medium", "rationale": "The seamless-vs-welded manufacturing method decides between this heading and 7305/7306; the plain description doesn't always state it.", "ambiguity_triggers": ["welded", "riveted", "cast iron"]},
    "plain_rationale": "HSN 7304 covers seamless tubes, pipes and hollow profiles of steel or non-cast iron. Welded or riveted pipes instead fall under 7305 or 7306, and cast iron pipe falls under 7303. GST is 18%, but this rate was matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7304 — seamless steel/iron tubes and pipes. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7305", "Other tubes and pipes, having circular cross-sections, external diameter exceeding 406.4 mm, of iron or steel", {
    "synonyms": ["welded steel pipe (large diameter)", "riveted steel pipe", "line pipe", "large-bore steel pipe"],
    "market_terms": ["large-diameter pipe manufacturing", "pipeline steel supply", "line pipe trade"],
    "hindi_transliterated": [], "examples": ["welded steel line pipe for an oil/gas pipeline", "large-diameter riveted steel pipe"],
    "attributes": {"material": ["steel"], "use": ["pipeline", "large-bore piping"], "form": ["welded/riveted pipe"], "industry": ["steel", "oil & gas", "infrastructure"]},
    "clarification_questions": [], "exclusion_notes": [{"excluded_code": "HSN_7304", "reason": "7304 is seamless pipe — 7305 is welded/riveted large external-diameter circular pipe"}, {"excluded_code": "HSN_7306", "reason": "7306 covers other welded tubes/hollow profiles including smaller-diameter and non-circular sections — 7305 is specifically large-diameter circular pipe"}],
    "classification_confidence": {"level": "Medium", "rationale": "This heading is narrowly defined by diameter and cross-section, which needs confirming against the closely related 7304/7306.", "ambiguity_triggers": ["seamless", "small diameter", "square/rectangular"]},
    "plain_rationale": "HSN 7305 covers welded or riveted steel pipes with a circular cross-section and external diameter over 406.4mm — typically large pipeline pipe. Smaller or non-circular welded tubes fall under 7306, and seamless pipe falls under 7304. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7305 — large-diameter welded/riveted steel pipe. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7306", "Other tubes, pipes and hollow profiles, of iron or steel", {
    "synonyms": ["welded steel tube", "ERW pipe", "hollow steel profile", "structural steel tube"],
    "market_terms": ["ERW pipe manufacturing", "structural tube supply", "hollow section trade"],
    "hindi_transliterated": [], "examples": ["ERW (electric resistance welded) steel tube", "square/rectangular hollow steel section for fabrication"],
    "attributes": {"material": ["steel"], "use": ["structural fabrication", "piping"], "form": ["welded tube", "hollow section"], "industry": ["steel", "construction", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [{"excluded_code": "HSN_7305", "reason": "7305 is large external-diameter (>406.4mm) circular welded pipe — 7306 covers other welded tubes/hollow profiles, including structural sections"}],
    "classification_confidence": {"level": "Medium", "rationale": "This is a broad 'other' welded-tube heading; the diameter/shape needs checking against the narrower 7305.", "ambiguity_triggers": ["large diameter pipeline pipe"]},
    "plain_rationale": "HSN 7306 covers welded, riveted or similarly closed steel tubes, pipes and hollow profiles not covered by the large-diameter circular pipe heading 7305 — this includes structural square and rectangular hollow sections (ERW tube) commonly used in fabrication. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7306 — other welded steel tubes, pipes and hollow profiles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7307", "Tube or pipe fittings, of iron or steel", {
    "synonyms": ["pipe fitting", "elbow (pipe)", "coupling", "pipe flange"],
    "market_terms": ["pipe fitting manufacturing", "plumbing fitting supply", "industrial pipe fitting trade"],
    "hindi_transliterated": [], "examples": ["steel pipe elbow fitting", "pipe coupling/sleeve", "steel flange"],
    "attributes": {"material": ["iron", "steel"], "use": ["plumbing", "industrial piping"], "form": ["fitting"], "industry": ["steel", "plumbing", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Iron/steel pipe fittings map uniquely to 7307.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7307 covers pipe fittings of iron or steel — couplings, elbows, sleeves, flanges and similar. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7307 — iron/steel tube and pipe fittings. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7308", "Structures and parts of structures, of iron or steel", {
    "synonyms": ["steel structure", "structural steel fabrication", "steel roof truss", "steel door/window frame"],
    "market_terms": ["structural steel fabrication trade", "prefab steel structure supply", "steel truss manufacturing"],
    "hindi_transliterated": [], "examples": ["steel roof truss for a factory shed", "structural steel column and beam fabrication"],
    "attributes": {"material": ["iron", "steel"], "use": ["construction", "structural fabrication"], "form": ["structure", "structural parts"], "industry": ["steel", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Steel structures and structural parts (bridges, roofs, gates, columns) map clearly to 7308, except prefabricated buildings which sit under a separate heading (94.06).", "ambiguity_triggers": ["prefabricated building"]},
    "plain_rationale": "HSN 7308 covers structures and parts of structures of iron or steel — bridges, towers, roof trusses, columns, beams, doors, windows and similar structural/fabricated items — but not prefabricated buildings, which fall under a separate heading. GST is 18%, but this rate was matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7308 — iron/steel structures and structural parts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7309", "Reservoirs, tanks, vats and similar containers, of iron or steel, capacity exceeding 300 litres", {
    "synonyms": ["steel storage tank", "large steel reservoir", "steel silo", "industrial vat"],
    "market_terms": ["large steel tank fabrication", "industrial storage tank supply", "silo manufacturing"],
    "hindi_transliterated": [], "examples": ["large steel water storage tank above 300 litres", "industrial chemical storage vat"],
    "attributes": {"material": ["iron", "steel"], "use": ["industrial storage"], "form": ["tank", "reservoir", "vat"], "industry": ["steel", "manufacturing", "chemicals"]},
    "clarification_questions": [{"question": "Is the container's capacity over 300 litres or 300 litres or less?", "attribute": "form", "options": ["Over 300 litres", "300 litres or less"], "disambiguates_from": ["HSN_7310"]}],
    "exclusion_notes": [{"excluded_code": "HSN_7310", "reason": "7310 covers smaller containers of 300 litres capacity or less — 7309 is for larger reservoirs, tanks and vats"}],
    "classification_confidence": {"level": "Medium", "rationale": "The 300-litre capacity threshold is the deciding factor against the sibling heading 7310, and needs the specific product spec to confirm.", "ambiguity_triggers": ["drum", "small container", "300 litres or less"]},
    "plain_rationale": "HSN 7309 covers reservoirs, tanks, vats and similar iron/steel containers with a capacity over 300 litres — industrial storage tanks and silos, not compressed/liquefied gas containers. Smaller containers (300 litres or less) fall under HSN 7310 instead. GST is 18%, but this rate was matched with low confidence at the heading level, so confirm it with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7309 — iron/steel reservoirs and tanks over 300 litres. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7310", "Tanks, casks, drums, cans, boxes and similar containers, of iron or steel, capacity not exceeding 300 litres", {
    "synonyms": ["steel drum", "tin can", "metal container (small)", "steel box container"],
    "market_terms": ["steel drum manufacturing", "tin/metal can supply", "small container trade"],
    "hindi_transliterated": [], "examples": ["200-litre steel drum for chemical storage", "tin can for food packaging"],
    "attributes": {"material": ["iron", "steel", "tin"], "use": ["storage", "packaging"], "form": ["drum", "can", "box"], "industry": ["steel", "packaging", "manufacturing"]},
    "clarification_questions": [{"question": "Is the container's capacity 300 litres or less, or over 300 litres?", "attribute": "form", "options": ["300 litres or less", "Over 300 litres"], "disambiguates_from": ["HSN_7309"]}],
    "exclusion_notes": [{"excluded_code": "HSN_7309", "reason": "7309 covers larger reservoirs/tanks over 300 litres capacity — 7310 is for containers of 300 litres or less"}],
    "classification_confidence": {"level": "Medium", "rationale": "The 300-litre capacity threshold decides between this heading and 7309, needing the specific product spec to confirm.", "ambiguity_triggers": ["large tank", "over 300 litres", "silo"]},
    "plain_rationale": "HSN 7310 covers tanks, casks, drums, cans, boxes and similar iron/steel containers of 300 litres capacity or less — steel drums and tin cans are the classic examples. Larger containers fall under HSN 7309. The base rate shown is 5%, but most goods in this heading actually attract 18% per the notification, so confirm the exact rate for your specific container with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7310 — iron/steel containers of 300 litres or less. Rate per Notification 9/2025-Integrated Tax (Rate).",
}, exceptions=[{"gst_rate": 18.0, "condition": "Most tanks, drums, cans, boxes and similar containers (≤300 L) actually attract 18%, not the 5% shown as the base rate"}])

add("HSN_7311", "Containers for compressed or liquefied gas, of iron or steel", {
    "synonyms": ["gas cylinder", "LPG cylinder", "compressed gas tank", "gas container (steel)"],
    "market_terms": ["gas cylinder manufacturing", "LPG cylinder supply", "industrial gas container trade"],
    "hindi_transliterated": [], "examples": ["LPG gas cylinder", "industrial compressed gas cylinder"],
    "attributes": {"material": ["iron", "steel"], "use": ["gas storage/transport"], "form": ["cylinder", "tank"], "industry": ["steel", "gas/energy", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Compressed/liquefied gas containers map uniquely to 7311.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7311 covers containers for compressed or liquefied gas made of iron or steel — LPG cylinders and industrial gas cylinders. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7311 — iron/steel containers for compressed/liquefied gas. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7312", "Stranded wire, ropes, cables, plaited bands, slings and the like, of iron or steel, not electrically insulated", {
    "synonyms": ["steel wire rope", "steel cable", "stranded wire", "wire sling"],
    "market_terms": ["steel wire rope manufacturing", "crane cable supply", "rigging sling trade"],
    "hindi_transliterated": [], "examples": ["steel wire rope for crane lifting", "steel cable sling for rigging"],
    "attributes": {"material": ["iron", "steel"], "use": ["lifting", "rigging"], "form": ["wire rope", "cable", "sling"], "industry": ["steel", "construction", "material handling"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Non-insulated iron/steel wire rope and cable map uniquely to 7312.", "ambiguity_triggers": ["electrically insulated cable"]},
    "plain_rationale": "HSN 7312 covers stranded wire, ropes, cables, plaited bands and slings of iron or steel that are not electrically insulated — used for lifting, rigging and hoisting. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7312 — iron/steel wire rope, cable and slings. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7313", "Barbed wire of iron or steel; twisted hoop or single flat wire, barbed or not, used for fencing", {
    "synonyms": ["barbed wire", "fencing wire", "twisted wire (fencing)", "concertina wire"],
    "market_terms": ["barbed wire manufacturing", "fencing material supply", "agricultural fencing trade"],
    "hindi_transliterated": [], "examples": ["barbed wire roll for farm fencing", "twisted fencing wire"],
    "attributes": {"material": ["iron", "steel"], "use": ["fencing"], "form": ["wire"], "industry": ["steel", "agriculture", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Barbed wire and fencing-grade twisted wire map uniquely to 7313.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7313 covers barbed wire of iron or steel, and twisted hoop or flat wire used for fencing. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7313 — barbed wire and fencing wire. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7314", "Cloth, grill, netting and fencing, of iron or steel wire; expanded metal of iron or steel", {
    "synonyms": ["wire mesh", "chain-link fencing", "wire netting", "expanded metal sheet"],
    "market_terms": ["wire mesh manufacturing", "chain-link fence supply", "expanded metal trade"],
    "hindi_transliterated": [], "examples": ["chain-link fencing roll", "welded wire mesh for construction"],
    "attributes": {"material": ["iron", "steel"], "use": ["fencing", "construction reinforcement"], "form": ["mesh", "netting", "expanded metal"], "industry": ["steel", "construction", "agriculture"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Iron/steel wire mesh, netting, fencing cloth and expanded metal map uniquely to 7314.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7314 covers wire cloth, grill, netting and fencing made of iron or steel wire, plus expanded metal sheet. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7314 — iron/steel wire mesh, netting and expanded metal. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7315", "Chain and parts thereof, of iron or steel", {
    "synonyms": ["steel chain", "iron chain", "chain link (steel)", "hoist chain"],
    "market_terms": ["steel chain manufacturing", "industrial chain supply", "security chain trade"],
    "hindi_transliterated": ["zanjeer"], "examples": ["steel chain for hoisting", "chain link for security gates"],
    "attributes": {"material": ["iron", "steel"], "use": ["lifting", "security", "industrial"], "form": ["chain", "chain link"], "industry": ["steel", "material handling", "hardware"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Iron/steel chain and its parts map uniquely to 7315.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7315 covers chain and chain parts of iron or steel — from hoist chains to security/fencing chain. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7315 — iron/steel chain and parts. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7316", "Anchors, grapnels and parts thereof, of iron or steel", {
    "synonyms": ["ship anchor", "grapnel hook", "boat anchor (steel)", "mooring anchor"],
    "market_terms": ["marine hardware manufacturing", "anchor supply", "boat fitting trade"],
    "hindi_transliterated": [], "examples": ["steel ship anchor", "grapnel hook for boats"],
    "attributes": {"material": ["iron", "steel"], "use": ["marine/nautical"], "form": ["anchor", "grapnel"], "industry": ["steel", "marine hardware"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Anchors and grapnels map uniquely to 7316.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7316 covers anchors, grapnels and their parts made of iron or steel — marine hardware for boats and ships. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7316 — iron/steel anchors and grapnels. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7317", "Nails, tacks, drawing pins, corrugated nails, staples and similar articles, of iron or steel", {
    "synonyms": ["nails", "tacks", "drawing pins", "staples (metal)"],
    "market_terms": ["nail manufacturing", "fastener hardware supply", "construction hardware trade"],
    "hindi_transliterated": ["kil"], "examples": ["box of steel nails", "staple pins for stapling"],
    "attributes": {"material": ["iron", "steel"], "use": ["fastening"], "form": ["nail", "tack", "staple"], "industry": ["steel", "hardware", "construction"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Nails, tacks, drawing pins and staples of iron or steel map uniquely to 7317.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7317 covers nails, tacks, drawing pins, corrugated nails, staples and similar iron/steel fasteners. The base rate shown is 5%, but most goods in this heading actually attract 18% per the notification — the source text for the specific carve-out that keeps 5% was truncated in our data, so confirm the exact rate with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7317 — iron/steel nails, tacks and staples. Rate per Notification 9/2025-Integrated Tax (Rate).",
}, exceptions=[{"gst_rate": 18.0, "condition": "Most nails, tacks, staples and similar iron/steel fasteners attract 18%; the specific carve-out that keeps 5% is truncated in our source notification text"}])

add("HSN_7318", "Screws, bolts, nuts, coach screws, screw hooks, rivets, cotters, washers and similar articles, of iron or steel", {
    "synonyms": ["screw", "bolt", "nut", "rivet", "washer"],
    "market_terms": ["fastener manufacturing", "nut-bolt hardware supply", "industrial fastener trade"],
    "hindi_transliterated": [], "examples": ["box of machine screws", "hex bolts and nuts set", "rivets for sheet metal work"],
    "attributes": {"material": ["iron", "steel"], "use": ["fastening"], "form": ["screw", "bolt", "nut", "rivet", "washer"], "industry": ["steel", "hardware", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Threaded and mechanical fasteners of iron or steel map uniquely to 7318.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7318 covers screws, bolts, nuts, rivets, washers and similar threaded or mechanical fasteners of iron or steel. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7318 — iron/steel screws, bolts, nuts and fasteners. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7319", "Sewing needles, knitting needles, bodkins, crochet hooks and similar hand-use articles, of iron or steel", {
    "synonyms": ["sewing needle", "knitting needle", "safety pin", "crochet hook"],
    "market_terms": ["needle manufacturing", "tailoring hardware supply", "haberdashery trade"],
    "hindi_transliterated": ["sui"], "examples": ["packet of sewing needles", "knitting needle set"],
    "attributes": {"material": ["iron", "steel"], "use": ["sewing", "knitting", "handicraft"], "form": ["needle", "hook", "pin"], "industry": ["steel", "textiles", "hardware"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Sewing/knitting needles, bodkins and crochet hooks map uniquely to 7319.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7319 covers sewing needles, knitting needles, bodkins, crochet hooks, embroidery stilettos and similar hand-use iron/steel articles. No GST rate could be matched to this code from the notification schedules in our data; confirm the current rate with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7319 — iron/steel needles and hand-sewing tools.",
})

add("HSN_7320", "Springs and leaves for springs, of iron or steel", {
    "synonyms": ["steel spring", "leaf spring", "coil spring", "torsion spring"],
    "market_terms": ["spring manufacturing", "automotive suspension spring supply", "industrial spring trade"],
    "hindi_transliterated": [], "examples": ["leaf spring for a truck suspension", "coil spring for machinery"],
    "attributes": {"material": ["iron", "steel"], "use": ["automotive", "industrial machinery"], "form": ["spring", "leaf spring"], "industry": ["steel", "automotive", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Springs and spring leaves of iron or steel map uniquely to 7320.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7320 covers springs and leaves for springs made of iron or steel — including automotive leaf springs and industrial coil springs. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7320 — iron/steel springs. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7321", "Stoves, ranges, grates, cookers, barbecues and similar non-electric domestic appliances, of iron or steel", {
    "synonyms": ["gas stove", "cooking range", "barbecue grill", "wood/coal stove"],
    "market_terms": ["gas stove manufacturing", "kitchen appliance (non-electric) supply", "barbecue equipment trade"],
    "hindi_transliterated": ["chulha"], "examples": ["LPG gas stove/burner", "barbecue grill", "wood-fired cooking stove"],
    "attributes": {"material": ["iron", "steel"], "use": ["cooking", "heating"], "form": ["stove", "range", "grill"], "industry": ["steel", "kitchen appliances", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Non-electric domestic cooking/heating appliances of iron or steel map clearly to 7321.", "ambiguity_triggers": ["electric appliance"]},
    "plain_rationale": "HSN 7321 covers stoves, ranges, cookers, barbecues, braziers, gas-rings and similar non-electric domestic appliances (and their parts) made of iron or steel — includes LPG gas stoves. Most goods in this heading actually attract 18%, not the 5% shown as the base rate, so confirm the exact rate with your CA before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7321 — iron/steel non-electric domestic appliances. Rate per Notification 9/2025-Integrated Tax (Rate).",
}, exceptions=[{"gst_rate": 18.0, "condition": "Most non-electric domestic stoves, cookers, ranges and heating appliances actually attract 18%, not the 5% shown as the base rate"}])

add("HSN_7322", "Radiators for central heating, air heaters and hot air distributors, of iron or steel", {
    "synonyms": ["radiator (heating)", "air heater", "hot air distributor", "central heating radiator"],
    "market_terms": ["heating equipment manufacturing", "radiator supply", "HVAC hardware trade"],
    "hindi_transliterated": [], "examples": ["steel radiator for a central heating system", "industrial air heater unit"],
    "attributes": {"material": ["iron", "steel"], "use": ["heating", "HVAC"], "form": ["radiator", "air heater"], "industry": ["steel", "HVAC", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [],
    "classification_confidence": {"level": "High", "rationale": "Non-electric heating radiators and air heaters of iron or steel map uniquely to 7322.", "ambiguity_triggers": []},
    "plain_rationale": "HSN 7322 covers radiators for central heating (not electrically heated) and their parts, plus air heaters and hot air distributors, made of iron or steel. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7322 — iron/steel radiators and air heaters. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7323", "Table, kitchen or household articles of iron or steel; iron/steel wool; pot scourers", {
    "synonyms": ["steel utensil", "iron kadai/pan", "steel wool", "pot scourer", "milk can (steel)"],
    "market_terms": ["steel kitchenware manufacturing", "household hardware supply", "steel utensil trade"],
    "hindi_transliterated": ["kadai", "patila"], "examples": ["stainless steel cooking pot", "steel wool scouring pad", "milk can made of steel"],
    "attributes": {"material": ["iron", "steel"], "use": ["cooking", "household use"], "form": ["utensil", "wool", "scourer"], "industry": ["steel", "kitchenware", "household goods"]},
    "clarification_questions": [{"question": "Is the item a milk can, or another table/kitchen/household iron-steel article?", "attribute": "use", "options": ["Milk can (iron/steel)", "Other table/kitchen/household article"], "disambiguates_from": []}],
    "exclusion_notes": [{"excluded_code": "HSN_7324", "reason": "7324 is iron/steel sanitary ware (bathroom fixtures) — 7323 is table/kitchen/household articles"}],
    "classification_confidence": {"level": "Medium", "rationale": "Most goods here (utensils, steel wool, scourers) attract a different rate than the one narrow carve-out (milk cans), so the specific product needs confirming.", "ambiguity_triggers": ["sanitary ware", "bathroom fixture"]},
    "plain_rationale": "HSN 7323 covers table, kitchen and household articles of iron or steel, plus iron/steel wool and pot scourers/scouring pads. Table/kitchen/household articles, steel wool and scourers generally attract 18%; only milk cans of iron or steel keep the 5% base rate — check which bucket your product falls into before invoicing.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7323 — iron/steel table, kitchen and household articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
}, exceptions=[{"gst_rate": 18.0, "condition": "Table/kitchen/household iron-steel articles, iron-steel wool and scourers attract 18%; only milk cans of iron or steel keep 5%"}])

add("HSN_7324", "Sanitary ware and parts thereof, of iron or steel", {
    "synonyms": ["steel sink", "iron bathtub", "steel washbasin", "steel wash-basin unit"],
    "market_terms": ["steel sanitaryware manufacturing", "bathroom fixture supply", "commercial kitchen sink trade"],
    "hindi_transliterated": [], "examples": ["stainless steel kitchen sink", "steel bathtub"],
    "attributes": {"material": ["iron", "steel"], "use": ["bathroom/kitchen fixtures"], "form": ["sink", "basin", "tub"], "industry": ["steel", "sanitaryware", "construction"]},
    "clarification_questions": [], "exclusion_notes": [{"excluded_code": "HSN_7323", "reason": "7323 is table/kitchen/household utensils — 7324 is specifically sanitary ware (sinks, tubs, basins) for bathroom/plumbing use"}],
    "classification_confidence": {"level": "Medium", "rationale": "Sanitary fixtures map clearly to this heading, but sinks in particular can be confused with kitchen articles under 7323.", "ambiguity_triggers": ["kitchen utensil", "cooking pot"]},
    "plain_rationale": "HSN 7324 covers sanitary ware and parts of iron or steel — sinks, wash-basins and bathtubs. A steel cooking utensil instead falls under HSN 7323. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7324 — iron/steel sanitary ware. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7325", "Other cast articles of iron or steel", {
    "synonyms": ["cast iron article", "steel casting", "cast manhole cover", "cast machine part"],
    "market_terms": ["iron/steel casting manufacturing", "foundry casting supply", "cast component trade"],
    "hindi_transliterated": [], "examples": ["cast iron manhole cover", "cast steel machine part"],
    "attributes": {"material": ["cast iron", "cast steel"], "use": ["infrastructure", "machinery components"], "form": ["cast article"], "industry": ["steel", "foundry", "manufacturing"]},
    "clarification_questions": [{"question": "Is the article made by casting, or by forging/machining/fabrication?", "attribute": "form", "options": ["Cast", "Forged/machined/fabricated"], "disambiguates_from": ["HSN_7326"]}],
    "exclusion_notes": [{"excluded_code": "HSN_7326", "reason": "7326 is other (non-cast, e.g. forged/machined/fabricated) articles of iron or steel — 7325 is specifically cast articles"}],
    "classification_confidence": {"level": "Medium", "rationale": "This is a residual 'other cast articles' heading; the casting-vs-other-manufacture distinction needs confirming against 7326.", "ambiguity_triggers": ["forged", "machined", "welded fabrication"]},
    "plain_rationale": "HSN 7325 covers cast articles of iron or steel not classified elsewhere in this chapter — manhole covers and cast machine parts are typical examples. Non-cast (forged, machined or fabricated) iron/steel articles fall under HSN 7326 instead. GST is 18%, matched at the heading level.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7325 — other cast iron/steel articles. Rate per Notification 9/2025-Integrated Tax (Rate).",
})

add("HSN_7326", "Other articles of iron or steel", {
    "synonyms": ["miscellaneous steel article", "fabricated steel part", "forged steel component", "machined steel part"],
    "market_terms": ["steel fabrication trade", "general steel hardware supply", "machined steel part trade"],
    "hindi_transliterated": [], "examples": ["fabricated steel bracket", "forged steel component not covered by a specific heading"],
    "attributes": {"material": ["iron", "steel"], "use": ["general fabrication"], "form": ["fabricated/forged/machined article"], "industry": ["steel", "manufacturing"]},
    "clarification_questions": [], "exclusion_notes": [{"excluded_code": "HSN_7325", "reason": "7325 is cast iron/steel articles — 7326 is the residual bucket for other (non-cast) iron/steel articles not covered elsewhere in the chapter"}],
    "classification_confidence": {"level": "Low", "rationale": "This is a residual 'other articles of iron or steel' catch-all covering many unrelated products; reaching it correctly requires first ruling out every more specific heading in the chapter.", "ambiguity_triggers": ["cast", "specific named article"]},
    "plain_rationale": "HSN 7326 is a residual heading for articles of iron or steel that don't fit any more specific heading elsewhere in Chapter 73 — a very broad catch-all for fabricated, forged or machined steel components. No GST rate could be matched to this code from the notification schedules in our data; consult a tax professional, and check whether a more specific heading fits your product first.",
    "regulatory_citation": "ITC(HS) 2022, Chapter 73, Heading 7326 — other articles of iron or steel.",
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
