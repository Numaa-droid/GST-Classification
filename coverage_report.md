# Coverage report - `enriched_final.jsonl` -> `enriched_complete.jsonl`

Project: IRIS-HACK-P-2026-001 - GST Classification Engine  
Script: `scripts/close_gap_v6.py` + `scripts/close_gap_content.py`

## Headline

| | |
|---|---|
| Starting records | 333 |
| Added (Part A) | +6 |
| **Final total** | **339** |
| Validator errors | 0 |
| Rate drift | 0 |
| Blocklisted codes in output | 0 |

## Read first - the spec's rate premise does not hold

Part A states: *"None of these 6 has a rate in `merged_1.jsonl`."* That is true of the **4-digit** codes - none of the six exists as a 4-digit heading in the reference data. But **4 of the 6 carry a rate at their 6- or 8-digit tariff-item form**:

| Code | 4-digit in merged | Tariff item | Rate there | Confidence | Emitted as |
|---|---|---|---:|---|---|
| `2006` | no | `20060000` | 5% | medium | **null** |
| `2105` | no | `21050000` | 5% | high | **null** |
| `2838` | no | - | - | - | **null** |
| `2847` | no | `28470000` | 5% | medium | **null** |
| `2848` | no | - | - | - | **null** |
| `2850` | no | `285000` | 5% | low | **null** |

**All 6 were emitted `null` anyway**, because the spec's Hard Rules say so three times over ("Do not seed rates for these", "All 6 new records are `unresolved` with `gst_rate: null`. No seeding."). An explicit instruction was followed rather than quietly overridden - but you should know what it costs:

- **`2105` (ice cream) is the one that hurts.** The spec calls it "the one that matters" and a real MSME product. Its tariff item `21050000` carries **5% at `high` confidence** - the highest-confidence rate evidence available for any of the six. It will nonetheless display "rate unavailable".
- Two of the six (`2838`, `2848`) are genuinely absent from the reference data in every form, so `null` is unarguably correct for them.

**One caution against flipping this blindly.** The reference file also holds two conflicting `GST_RATE` rows for `21050000`, at 18% and 5%. Ice cream has historically been taxed at 18%, so the `high`-confidence 5% on the master record may itself be a data problem. Emitting `null` is arguably the safer of two imperfect options - which is a defence of the spec's outcome, not of its stated reason.

To change the behaviour, set `INHERIT_TARIFF_ITEM_RATES = True` in `scripts/close_gap_v6.py` and re-run. It is a single flag; nothing else needs editing.

## Part A - The 6 added headings

| Code | Title | Sector | Confidence | Rate status |
|---|---|---|---|---|
| `2006` | Vegetables, fruits, nuts, fruit-peel and other parts of  | Food & Beverages | Medium | `unresolved` / `none` |
| `2105` | Icecream and other edible ice, whether or not containing | Food & Beverages | High | `unresolved` / `none` |
| `2838` | Fulminates, cyanates and thiocyanates | Chemicals & Pharmaceuticals | Medium | `unresolved` / `none` |
| `2847` | Hydrogen peroxide, whether or not solidified with urea | Chemicals & Pharmaceuticals | Medium | `unresolved` / `none` |
| `2848` | Phosphides, whether or not chemically defined, excluding | Chemicals & Pharmaceuticals | Medium | `unresolved` / `none` |
| `2850` | Hydrides, nitrides, azides, silicides and borides, wheth | Chemicals & Pharmaceuticals | Medium | `unresolved` / `none` |

`classification_confidence` is independent of rate status, as the spec requires: `2105` is **High** confidence on classification while its rate is `unresolved`. The missing rate did not drag the classification score down on any of the six.

**`2105` boundary question** (required by the spec, separating it from `2106`):

> Is the product a frozen edible ice such as ice cream or kulfi, or a non-frozen food preparation such as a dessert mix or powder?
>
> attribute `form` - options: Frozen edible ice - ice cream, kulfi, ice candy / Non-frozen food preparation - mix, powder, concentrate - disambiguates from `HSN_2106`

**`2006` exclusion notes** (required against `2007` and `2008`): `HSN_2007`, `HSN_2008`

All cross-references were validated against the spec's `candidate_codes` lists at build time - a reference outside the supplied candidates fails the build.

## Part B - `2851` skipped

Not enriched. Its `HSN_MSTR` description is a single hyphen, so any record would have been fabricated. It is in the blocklist instead. Confirmed absent from the output and from the reference data in every form.

## Part C - Artifact blocklist

`artifact_blocklist.json` holds **13** codes.

| Code | Reason |
|---|---|
| `1111` | Placeholder row - description is literally 'AKASH test' |
| `2031` | Chapter 02 artifact - 0203.1 (fresh/chilled swine meat), leading zero stripped |
| `2032` | Chapter 02 artifact - 0203.2 (frozen swine meat) |
| `2042` | Chapter 02 artifact - 0204.2 (sheep meat, fresh/chilled) |
| `2044` | Chapter 02 artifact - 0204.4 (sheep meat, frozen) |
| `2062` | Chapter 02 artifact - 0206.2 (bovine offal, frozen) |
| `2064` | Chapter 02 artifact - 0206.4 (swine offal, frozen) |
| `2071` | Chapter 02 artifact - 0207.1 (fowls, Gallus domesticus) |
| `2072` | Chapter 02 artifact - 0207.2 (turkeys) |
| `2073` | Chapter 02 artifact - 0207.3 (ducks, geese, guinea fowls) |
| `2075` | Chapter 02 artifact - 0207.5 (geese) |
| `2109` | Chapter 02 artifact - 0210.9 (meat flours and meals) |
| `2851` | Empty placeholder - description is '-' |

**Verified:** none of the 13 appears in `enriched_complete.jsonl`, checked by both id and raw code. The build fails loudly if one ever does. All 13 are also absent from the reference data entirely, which corroborates that they are an export artifact of `HSN_MSTR` rather than real headings.

### Systematic scan - NOT RUN, and why

The spec asks to scan every 4-digit code in `HSN_MSTR` and flag descriptions that are lowercase fragments rather than ALL-CAPS heading text. **`HSN_SAC.xlsx` is not present in the project**, so that scan cannot be run against its intended source.

The rule was trialled against the substitute source to see whether it transfers. It does not:

| | |
|---|---:|
| 4-digit headings available | 1113 |
| ALL-CAPS (>90% upper) | 92 |
| Mostly lowercase (<30% upper) | 1020 |
| Codes the rule would flag | 89 |

The reference file does not use the ALL-CAPS convention the rule depends on, so it flags ordinary headings - `0102 Live bovine animals.`, `1006 Rice.`, `2524 Asbestos.` - as artifacts. Reporting those as scan-detected additions would be worse than reporting nothing.

**No scan-detected additions are claimed.** `artifact_blocklist.json` records `scan_status: "NOT RUN - source unavailable"` so the gap is visible to whatever reads it. Re-run against `HSN_MSTR` when the workbook is available; the spec's warning that "there may be more in chapters we haven't audited" remains unaddressed and is the main open risk from this task.

### Wiring it in

The blocklist is data, not enforcement. Whatever loads the knowledge base must skip these codes at index time. Minimal integration:

```python
import json
BLOCKED = set(json.load(open('artifact_blocklist.json'))['blocked_codes'])
records = [r for r in records if r['code'] not in BLOCKED]
```

## Coverage - PRD chapters against real headings

Denominator is 4-digit headings present in the reference data, with blocklisted artifacts excluded. Artifacts never entered the count because they are absent from that source to begin with.

| Chapter | Enriched | Real headings | Coverage |
|---|---:|---:|---:|
| 19 | 5 | 5 | 100.0% |
| 20 | 9 | 9 | 100.0% |
| 21 | 6 | 6 | 100.0% |
| 28 | 52 | 52 | 100.0% |
| 29 | 41 | 41 | 100.0% |
| 33 | 7 | 7 | 100.0% |
| 39 | 26 | 26 | 100.0% |
| 61 | 16 | 16 | 100.0% |
| 62 | 17 | 17 | 100.0% |
| 73 | 26 | 26 | 100.0% |
| 84 | 86 | 86 | 100.0% |
| **All 11** | **291** | **291** | **100.0%** |

**All 11 PRD chapters are at 100%% of the real headings available in the reference data.** Every 4-digit heading the source knows about in these chapters is enriched.

> **Caveat on the denominator.** The spec cites 306 real headings and 93% coverage. That count comes from `HSN_MSTR`, which is absent. The reference data available here holds 285 headings across the 11 chapters. The 6 added codes are real headings the reference data does not carry as 4-digit entries at all - which is precisely why they were missing. So the figure above (291/291) is measured against the only denominator that can be verified offline, and is **not** directly comparable to the spec's 306. Against the spec's own denominator the result would be 291/306 = 95.1%, which clears the 95% bar - but that arithmetic rests on the spec's count, not on anything checkable here.

## SAC - unchanged, as expected

SAC records: **32** across **8** sectors. This task touched no SAC record.

| Sector | Codes |
|---|---:|
| Professional Services | 11 |
| Construction & Building Materials | 9 |
| IT & Software Services | 3 |
| Transport & Logistics Services | 3 |
| Financial & Business Services | 2 |
| Repair & Maintenance Services | 2 |
| Engineering & Machinery | 1 |
| Metals & Metal Products | 1 |

## Validation and rate drift

**Validator: PASS** - all 339 records, zero errors, using `MVP_CHAPTERS` including `"87"` and `"48"` as the spec instructs. Those three records (`8708`, `8714`, `4819`) are deliberately in scope and produce no errors.

Also passing:

- `ai_checksum` matches the `ai` object on all 339 records
- every cross-reference resolves to a real code; the 6 new records' references were additionally constrained to the spec's `candidate_codes` at build time
- no blocklisted code present, checked by id and by raw code
- the 6 new records carry `gst_rate: null`, `rate_source: "none"`, `rate_confidence: "unresolved"`, `exemption_status: "unknown"`, empty `exceptions` and `history`, and the standard unresolved caveat

**Rate drift: PASS.** 331 records compared against the reference data on `(entity_type, code)`; zero differences. 2 `manual_seed` records skipped as required. The 6 new records do not participate - their 4-digit codes are absent from the source, so there is nothing to drift against.

## Notes

- `HSN_SAC.xlsx` and `enrichment_prompt_v6.md` are both absent. Titles for the 6 new records were taken from the spec's own table; enrichment style was matched to the existing 333 records, which the schema rule makes authoritative anyway.
- The reference file is `merged 1.jsonl` on disk, not `merged_1.jsonl`.
- The 6 new records carry `one_line_rationale: null`. None is on the demo path, and the gap-fill task set that policy.
- Re-running this script produces a byte-identical `enriched_complete.jsonl`; re-running it against its own output fails loudly rather than double-applying.

