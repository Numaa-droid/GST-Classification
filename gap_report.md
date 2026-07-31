# Gap-fill report - `updat_enriched.jsonl` -> `enriched_final.jsonl`

Project: IRIS-HACK-P-2026-001 - GST Classification Engine  
Script: `scripts/gap_fill_v6.py` + `scripts/gap_content.py`

## Headline

| | |
|---|---|
| Starting records | 224 |
| Part A - Chapter 84 | +86 |
| Part B - auto parts | +2 |
| Part C - SAC breadth | +20 |
| Restored from quarantine | +1 |
| **Final total** | **333** |
| Validation errors | 0 |
| Rate drift | 0 |

## Count reconciliation

The spec predicted ~350 (224 + 87 + 2 + 20 + 17). Actual is **333**. Two reasons:

- **Chapter 84 has 86 four-digit headings in the reference data, not 87.** Heading 8469 (typewriters) was deleted from the tariff, so the chapter runs 8401-8487 with one gap. All 86 present headings were enriched.
- **The spec's own Part C arithmetic double-counts.** The summary table says "~17" but the code table lists **20** codes and the text says this "brings SAC to 32" (12 + 20 = 32). The 20-code list was treated as authoritative.

So: 224 + 86 + 2 + 20 + 1 restored = **333**.

## Part A - Chapter 84

- Headings enriched: **86** (8401-8487, 8469 absent from the tariff)
- With a rate from `merged 1.jsonl`: **84**
- Left `unresolved` (no rate in the source): **2** - `HSN_8401`, `HSN_8413`

The spec expected 3 unresolved; the reference data has **2**. Neither was seeded - Part A explicitly says not to.

Rate distribution: 5% = 8, 18% = 76

**Abstained (residual "other" headings):** 4 - `HSN_8412`, `HSN_8472`, `HSN_8479`, `HSN_8487`

These are catch-all headings ("other engines and motors", "machines having individual functions n.e.s.", "other office machines", "machinery parts n.e.s."). A record only belongs in one after every named heading has been ruled out, which a plain-language query cannot establish. They carry full enrichment so search still reaches them, but `enrichment_status: "abstained"` flags that the classification needs human confirmation rather than being asserted.

**Multi-sector assignments** (the spec's watch-list):

| Heading | Sectors |
|---|---|
| `HSN_8419` Machinery for treating materials by a change | Engineering & Machinery + Food & Beverages |
| `HSN_8422` Dish washing machines; bottle cleaning and f | Engineering & Machinery + Food & Beverages |
| `HSN_8429` Self-propelled bulldozers, graders, scrapers | Engineering & Machinery + Construction & Building Materials |
| `HSN_8430` Other moving, grading, excavating, tamping,  | Engineering & Machinery + Construction & Building Materials |
| `HSN_8434` Milking machines and dairy machinery | Engineering & Machinery + Food & Beverages |
| `HSN_8435` Presses, crushers and similar machinery used | Engineering & Machinery + Food & Beverages |
| `HSN_8437` Machines for cleaning, sorting or grading se | Engineering & Machinery + Food & Beverages |
| `HSN_8438` Machinery for the industrial preparation or  | Engineering & Machinery + Food & Beverages |
| `HSN_8444` Machines for extruding, drawing, texturing o | Engineering & Machinery + Textiles & Apparel |
| `HSN_8445` Machines for preparing textile fibres; spinn | Engineering & Machinery + Textiles & Apparel |
| `HSN_8446` Weaving machines (looms) | Engineering & Machinery + Textiles & Apparel |
| `HSN_8447` Knitting machines, stitch-bonding machines a | Engineering & Machinery + Textiles & Apparel |
| `HSN_8448` Auxiliary machinery and parts for the textil | Engineering & Machinery + Textiles & Apparel |
| `HSN_8449` Machinery for the manufacture or finishing o | Engineering & Machinery + Textiles & Apparel |
| `HSN_8451` Machinery for washing, dyeing, dressing, fin | Engineering & Machinery + Textiles & Apparel |
| `HSN_8452` Sewing machines; furniture, bases and covers | Engineering & Machinery + Textiles & Apparel |
| `HSN_8454` Converters, ladles, ingot moulds and casting | Engineering & Machinery + Metals & Metal Products |
| `HSN_8455` Metal-rolling mills and rolls therefor | Engineering & Machinery + Metals & Metal Products |
| `HSN_8456` Machine-tools working any material by remova | Engineering & Machinery + Metals & Metal Products |
| `HSN_8457` Machining centres, unit construction machine | Engineering & Machinery + Metals & Metal Products |
| `HSN_8458` Lathes (including turning centres) for remov | Engineering & Machinery + Metals & Metal Products |
| `HSN_8459` Machine-tools for drilling, boring, milling, | Engineering & Machinery + Metals & Metal Products |
| `HSN_8460` Machine-tools for deburring, sharpening, gri | Engineering & Machinery + Metals & Metal Products |
| `HSN_8461` Machine-tools for planing, shaping, slotting | Engineering & Machinery + Metals & Metal Products |
| `HSN_8462` Machine-tools for working metal by forging,  | Engineering & Machinery + Metals & Metal Products |
| `HSN_8463` Other machine-tools for working metal or cer | Engineering & Machinery + Metals & Metal Products |
| `HSN_8464` Machine-tools for working stone, ceramics, c | Engineering & Machinery + Construction & Building Materials |
| `HSN_8466` Parts and accessories for the machine-tools  | Engineering & Machinery + Metals & Metal Products |
| `HSN_8468` Machinery for soldering, brazing or welding; | Engineering & Machinery + Metals & Metal Products |
| `HSN_8471` Automatic data processing machines and units | Engineering & Machinery + IT & Software Services |
| `HSN_8473` Parts and accessories for the machines of he | Engineering & Machinery + IT & Software Services |
| `HSN_8474` Machinery for sorting, crushing, grinding or | Engineering & Machinery + Construction & Building Materials |
| `HSN_8477` Machinery for working rubber or plastics or  | Engineering & Machinery + Plastics & Rubber |
| `HSN_8480` Moulding boxes for metal foundry; mould base | Engineering & Machinery + Metals & Metal Products |
| `HSN_8481` Taps, cocks, valves and similar appliances f | Engineering & Machinery + Metals & Metal Products |
| `HSN_8482` Ball or roller bearings | Engineering & Machinery + Metals & Metal Products |
| `HSN_8483` Transmission shafts and cranks; bearing hous | Engineering & Machinery + Metals & Metal Products |
| `HSN_8484` Gaskets and similar joints of metal sheeting | Engineering & Machinery + Metals & Metal Products |

**Clarification questions** were written for the near-neighbour pairs the spec named:

| Pair | Attribute | Question |
|---|---|---|
| `HSN_8413` vs `HSN_8414` | `use` | Does the pump move a liquid such as water or oil, or does it move air or another gas? |
| `HSN_8407` vs `HSN_8408` | `use` | Does the engine run on petrol/gas with a spark plug, or on diesel by compression ignition? |
| `HSN_8481` vs `HSN_8484` | `use` | Does the item control or shut off flow, or does it seal a joint between two surfaces? |
| `HSN_8484` vs `HSN_8481` | `use` | Does the item seal a joint between two surfaces, or does it control or shut off flow? |
| `HSN_8414` vs `HSN_8413` | `use` | Does the unit move air or another gas, or does it move a liquid such as water? |
| `HSN_8408` vs `HSN_8407` | `use` | Does the engine run on diesel by compression ignition, or on petrol/gas with a spark plug? |

## Part B - `HSN_8708` and the bolt test

| Check | Result |
|---|---|
| `HSN_8708` present | yes |
| `HSN_8714` present | yes |
| `HSN_7318` -> `HSN_8708` in `exclusion_notes` | yes |
| `HSN_8708` -> `HSN_7318` in `exclusion_notes` | yes |
| `HSN_7318` clarification question targets 8708 | yes |
| `HSN_8708` clarification question targets 7318 | yes |

**`HSN_7318` needed no patch.** Part B asks for its `exclusion_notes` to be edited to add `HSN_8708`, but that note *and* a matching clarification question were already present from the original enrichment. The cross-reference was verified in both directions rather than assumed, and 7318's checksum is untouched.

`HSN_8708` carries rate **5%** (`medium`, from merged). `HSN_8714` is **null** - no rate exists for it anywhere in the reference data, so it was left unresolved rather than seeded or inferred from 8708.

## Part C - SAC breadth

SAC total: **32** (12 existing + 20 added). Distinct sectors: **8**.

| Sector | SAC codes |
|---|---:|
| Professional Services | 11 |
| Construction & Building Materials | 9 |
| IT & Software Services | 3 |
| Transport & Logistics Services | 3 |
| Financial & Business Services | 2 |
| Repair & Maintenance Services | 2 |
| Engineering & Machinery | 1 |
| Metals & Metal Products | 1 |

The clustering is fixed: before this pass all 12 SAC records sat in construction (9954x) and accounting (99822x) alone. IT, transport, legal, advertising, repair and job-work families are now represented.

**Job-work codes** `SAC_998873` and `SAC_998877` sound like goods but are services. Both carry a `retail_industrial` clarification question separating "I make and sell the product" (goods, HSN) from "I process material the customer supplies" (service, SAC), with `disambiguates_from` pointing at the corresponding HSN headings.

## Part D1 - Manual rate seeds

| Record | Rate | Confidence | Scope | Source |
|---|---:|---|---|---|
| `HSN_6307` | 5% | medium | heading | `manual_seed` |
| `HSN_63079091` | 5% | low | heading | `manual_seed` |

Both entries are written to `demo_seed.json` with a full `source_note`. Reproduced here:

**`HSN_6307`** - Seeded from CGST ready reckoner 01.05.2022, Schedule I entry 224 - other made up textile articles, sale value not exceeding Rs 1000 per piece (2.5% CGST = 5% total). Figure supplied by the task specification. NOT independently verified against the CBIC portal: this build runs offline with no network access, so the notification text could not be re-read. The 2022 reckoner predates the 2025 rate revision and Notification 9/2025-Integrated Tax (Rate) was not cross-checked for this heading - confirm before any figure is relied on for invoicing.

**`HSN_63079091`** - Inherited from the seeded parent heading HSN_6307, of which 63079091 (textile face masks without a replaceable filter or mechanical parts) is a tariff item. No entry specific to 63079091 exists in the knowledge base, so the heading-level figure is applied and rate_scope is recorded as 'heading'. rate_confidence is deliberately set one step lower than the parent ('low') because the value is inherited rather than matched. Carries the same caveats as HSN_6307: supplied by the task specification, not independently verified offline, and predating the 2025 revision.

> **Verification status - read this before the demo.** Part D1 says to "verify the ready-reckoner values yourself before committing them". This build runs offline with no network access, so **the CBIC notification could not be independently checked**. The `HSN_6307` figure is the one supplied in the task specification, recorded as such; `HSN_63079091` inherits it from its parent heading at one confidence step lower. Neither was cross-checked against Notification 9/2025, which the spec flags as a possible conflict. Both are marked `rate_source: "manual_seed"` so they are distinguishable from matched rates everywhere downstream, and both are excluded from the rate-drift check by design.

### Mask test

| Code | Title | Rate | Source |
|---|---|---:|---|
| `HSN_63079091` | Textile face masks, without a replaceable filter or  | 5% | `manual_seed` |
| `HSN_90200000` | Breathing appliances and gas masks, excluding masks  | 5% | `merged` |
| `HSN_3304` | Beauty, make-up and skin-care preparations, includin | 5% | `merged` |

**PASS** - all three mask codes carry a rate.

## Part D2 - One-line rationales

Written: **14**. Still null: **319** of 333.

| Record | One-liner | Chars |
|---|---|---:|
| `HSN_63079091` | Textile face masks without a filter or mechanical parts; a made-up textile article, not a medical device. | 105 |
| `HSN_90200000` | Breathing appliances and gas masks with mechanical parts or filters - the medical-device side of 'mask'. | 104 |
| `HSN_3304` | Beauty and make-up preparations; a cosmetic face mask belongs here, not with textile or breathing masks. | 104 |
| `HSN_2201` | Packaged drinking and mineral water, unsweetened and unflavoured; flavoured drinks move to 2202. | 96 |
| `SAC_998222` | Accounting and book-keeping services; tax return preparation is billed under 998231 instead. | 92 |
| `HSN_7318` | Generic iron or steel screws, bolts and nuts; the same bolt sold as a vehicle spare is 8708. | 92 |
| `HSN_8708` | Parts made specifically for cars, trucks and tractors; generic hardware fasteners stay in 7318. | 95 |
| `HSN_6109` | Knitted or crocheted T-shirts, singlets and vests; woven shirts are classified under 6205 or 6206. | 98 |
| `HSN_6206` | Women's and girls' woven blouses and shirts; the knitted equivalent belongs under 6106. | 87 |
| `HSN_2106` | Food preparations not elsewhere specified, the residual food heading covering namkeen and mixes. | 96 |
| `HSN_1904` | Cereal products from puffing or roasting - corn flakes, muri and chira; not general namkeen. | 92 |
| `HSN_6307` | Other made-up textile articles, the residual textile heading that also covers textile face masks. | 97 |
| `HSN_3923` | Plastic articles for conveying or packing goods - boxes, bottles, crates, sacks and closures. | 93 |
| `HSN_4819` | Cartons, boxes and packing containers of paper or paperboard; the plastic equivalent is 3923. | 93 |

All are within the 120-char limit and written as standalone sentences - none is a truncation of `plain_rationale`. The remaining records stay null by design; they are reachable by search but will not be on screen during the demo.

## Chapter coverage

| Chapter | Records | Status |
|---|---:|---|
| 19 | 5 | light |
| 20 | 8 | light |
| 21 | 5 | light |
| 22 | 2 | thin |
| 28 | 48 | ok |
| 29 | 41 | ok |
| 33 | 8 | light |
| 39 | 26 | ok |
| 48 (added this pass) | 1 | thin |
| 61 | 16 | ok |
| 62 | 17 | ok |
| 63 | 9 | light |
| 73 | 26 | ok |
| 84 | 86 | ok |
| 87 (added this pass) | 2 | thin |
| 90 | 1 | thin |
| SAC (all) | 32 | ok |
| **Total** | **333** | |

**No MVP chapter is at zero.** Chapter 84 went from 0 to 86 this pass - it was the single largest gap in the set.

## Scope change - two chapters added to `MVP_CHAPTERS`

The gap spec requires records the v6 scope rule excludes, so `MVP_CHAPTERS` was widened by two. Without this the spec's own instruction to run the patch validator with zero errors is unsatisfiable:

| Chapter | Why it had to be added | Records |
|---|---|---:|
| 87 | Part B requires `HSN_8708` and `HSN_8714`; the bolt test is a named success criterion | 2 |
| 48 | Part D2 lists `HSN_4819` in the packing-material demo path | 1 |

This resolves the contradiction flagged in the v6 patch report, where `HSN_8708` appeared on the demo path but was quarantined by the scope rule.

## Validation and rate drift

**Validator: PASS** - all 333 records pass the patch spec's `validate()` with zero errors.

Additional checks, also all passing:

- `rate_source` enum, and every resolved rate carrying `merged` or `manual_seed`
- `ai_checksum` matches the `ai` object on every record
- `rate` and `ai` key order identical to the existing 224
- `search_text` regenerates exactly from the `ai` object, on all 109 records this pass authored
- every `one_line_rationale` within 120 chars
- **no invented codes**: every `excluded_code` and every `disambiguates_from` id resolves either to a record in the final set or to one of the 16,441 real HSN/SAC codes in the reference tariff. Cross-references to real-but-not-yet-enriched codes are allowed (the existing data already does this, e.g. `HSN_2106` -> `HSN_21069020`); a reference to neither would be a fabrication and fails the build.

**Rate drift: PASS.** 331 records compared against `merged 1.jsonl` on `(entity_type, code)`; zero differences in `gst_rate` or `rate_confidence`. 2 `manual_seed` records were skipped, as the spec requires - they are expected to differ because merged has no rate for them at all.

## Notes and deviations

- `HSN_4819` (paper cartons, chapter 48) was restored from `quarantine.jsonl` and migrated to v6. Part D2 lists it in the packing-material demo path, but chapter 48 was out of MVP scope under the v6 patch, so it had been quarantined.
- `HSN_4819`'s sector was still the v5 value ['Wood, Paper & Packaging'] and was remapped to ['Other'] on restore - quarantined records never went through the v6 Step 6 normalisation. Its `search_text` was regenerated to match.
- `HSN_8708` was rebuilt from scratch by Part B rather than restored, because it was absent from the v6 input - the v6 patch had quarantined it as out-of-chapter. The new record therefore **supersedes** an earlier enrichment of the same id rather than filling an empty slot. The original's bolt-specific vocabulary ("vehicle bolt", "chassis bolt", "automotive fastener") and its caveat that the 5% rate applies to specified tractor parts while most vehicle parts attract 18% were both carried forward deliberately; the rebuild adds cross-references to HSN_8714 and HSN_8409 and a second clarification question.
- Part B asks for `HSN_7318`'s `exclusion_notes` to be patched to reference `HSN_8708`. That note - and a matching clarification question - was already present from the original enrichment, so no edit was made and its checksum is unchanged. The cross-reference was verified in both directions rather than assumed.
- `enrichment_prompt_v6.md` is named as the enrichment prompt but is not present in the project. The existing 224 records were used as the style contract instead, which the spec's own rule ("new records must match the existing 224 exactly") makes the authoritative source anyway. Field shapes, key order and the `search_text` rule were reverse-engineered from them and verified.
- `HSN_SAC.xlsx` (`HSN_MSTR` / `SAC_MSTR`) is absent, so `merged 1.jsonl` was used as the code list and rate source. It contains all 86 Chapter 84 headings, both Chapter 87 codes and all 20 target SAC codes, so nothing was lost.
- The rate reference is `merged 1.jsonl` on disk, not `merged_1.jsonl`.
- **6 untouched record(s) have a `search_text` that no longer regenerates from their `ai` object**: `HSN_3303`, `HSN_3304`, `HSN_33049990`, `HSN_3305`, `HSN_3306`, `HSN_3307`. All are chapter-33 records whose `search_text` still contains the pre-v6 sector wording ("consumer goods household") because the v6 patch normalised `sector` but deliberately left `search_text` alone. Harmless - it only adds stale search tokens - and reported rather than silently rewritten, since rewriting them is a scope decision, not a gap-fill one.
- New-record `plain_rationale` text is composed from the record's own rate block rather than typed by hand, so a rationale can never state a rate the record does not carry.

