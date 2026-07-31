# Patch report - enriched.jsonl v5 -> v6

Project: IRIS-HACK-P-2026-001 - GST Classification Engine  
Script: `scripts/patch_enriched_v5_to_v6.py` - deterministic, offline, stdlib only. No LLM calls.

## Headline

| | |
|---|---|
| Input records | 340 |
| Kept -> `enriched_v6.jsonl` | 224 |
| Quarantined -> `quarantine.jsonl` | 116 |
| Validation errors | 0 |
| Rate drift caused by patch | 0 |

## Action required

**The spec contradicts itself on the demo path.** Step 8 lists these ids as demo-path records a judge will see, but the Step 2 scope rule removes them. Step 2 was applied as written rather than silently widening scope - decide which of the two is wrong before the demo:

- `HSN_8708` - quarantined by Step 2 - reason `hsn_chapter_out_of_mvp_scope`

  To keep them, add the relevant chapter to `MVP_CHAPTERS` in the script and re-run; the record will be migrated rather than quarantined.

**Zero-coverage MVP chapter(s): 84.** See the chapter coverage table below.

**224 kept record(s) still need a `one_line_rationale`** - see `needs_one_liner.txt`, demo-path records first.

## Step 1 - `golden_dataset.jsonl` redundancy

**Confirmed redundant.** All 26 ids already exist in `enriched.jsonl`, so the file was ignored for the merge and no records were dropped.

- Byte-identical to the matching `enriched.jsonl` record: **26**
- Same id but differing content: **0**

## Step 2 - Quarantine

MVP scope: 11 PRD Table 11 chapters (19, 20, 21, 28, 29, 33, 39, 61, 62, 73, 84) plus demo exceptions 22, 63, 90. All SAC is in scope.

| Reason | Count | Expected |
|---|---:|---:|
| `nic_post_hackathon` | 47 | ~47 |
| `hsn_chapter_out_of_mvp_scope` | 69 | ~65 |
| **Total quarantined** | **116** | |

Out-of-scope HSN chapters removed:

| Chapter | Records | Example record |
|---|---:|---|
| 01 | 30 | Other sheep |
| 02 | 9 | Meat of bovine animals, fresh or chilled |
| 03 | 9 | Live fish |
| 04 | 10 | Milk and cream, not concentrated nor sweetened |
| 05 | 9 | Human hair, unworked |
| 48 | 1 | Cartons, boxes and other packing containers, and box files/letter trays, of paper or paperboard |
| 87 | 1 | Parts and accessories of motor vehicles of headings 8701 to 8705 |

All quarantined records are written verbatim in their **v5 form** with a `quarantine_reason` field appended. They are not patched to v6 - the v6 migration is deliberately scoped to MVP records, and re-running this script after widening `MVP_CHAPTERS` will patch them properly.

## Steps 3-4 - CGST / SGST / IGST split and `rate_source`

- Records given a split: **213**
- Records left null (no resolved rate): **11**

| gst_rate | igst | cgst | sgst | Records |
|---:|---:|---:|---:|---:|
| 5.0 | 5.0 | 2.5 | 2.5 | 119 |
| 18.0 | 18.0 | 9.0 | 9.0 | 93 |
| 40.0 | 40.0 | 20.0 | 20.0 | 1 |

No rounding applied - 5.0 splits to 2.5 / 2.5, 18.0 to 9.0 / 9.0. All three values are exact in binary floating point, so the equality checks in `validate()` hold after a JSON round trip.

`rate_source` distribution: `merged` = 213, `none` = 11
 - `manual_seed` does not appear yet by design; the field exists so a later seed pass is traceable.

## Step 5 - `composition_note` removed

Removed from **224** kept records (present on 100% of the input, not the ~281 the spec estimated). It appears nowhere in PRD Tables 11 or 12.

## Step 6 - Sector normalisation

| Before | After | Kept records remapped |
|---|---|---:|
| Consumer Goods & Household | Other | 6 |

Sector distribution after remap (kept records):

| Sector | Records |
|---|---:|
| Chemicals & Pharmaceuticals | 91 |
| Textiles & Apparel | 42 |
| Metals & Metal Products | 26 |
| Plastics & Rubber | 26 |
| Food & Beverages | 20 |
| Construction & Building Materials | 9 |
| Other | 6 |
| Professional Services | 4 |
| Engineering & Machinery | 2 |

No unmappable sector values remained. Every kept record carries 1-2 values, all inside the v6 enum.

Most stray v5 values sat on records Step 2 had already quarantined - `Agriculture & Live Animals` in particular is concentrated in chapters 01-05.

## Step 7 - History capped at 3

| Record | Entries before | After | Dropped (oldest) |
|---|---:|---:|---|
| `HSN_2106` | 4 | 3 | 0.0 |
| `HSN_3926` | 4 | 3 | 0.0 |

Truncated: **2** record(s). Deduplicated `(effective_from, gst_rate)` pairs: **0** record(s). Empty arrays stayed empty; no entries were invented.

History length distribution after the cap:

| Entries | Records |
|---:|---:|
| 0 | 14 |
| 1 | 67 |
| 2 | 85 |
| 3 | 58 |

## Step 8 - `one_line_rationale`

- Key added to **all 224** kept records
- Set to `null` (awaiting authoring): **224**
- Already authored and preserved: **0**

The field cannot be derived mechanically. Truncating `plain_rationale` at 120 chars produces mid-sentence garbage, so nothing was fabricated. `needs_one_liner.txt` lists every record awaiting one, with its title and full `plain_rationale` as source material.

**Demo-path records are listed first.** 11 of the 12 demo-path ids are in the kept set:

- `HSN_6109`
- `HSN_6206`
- `HSN_6307`
- `HSN_63079091`
- `HSN_90200000`
- `HSN_3304`
- `HSN_2201`
- `HSN_2106`
- `HSN_1904`
- `HSN_7318`
- `SAC_998222`

**Not in the kept set:**

- `HSN_8708` - quarantined by Step 2 - reason `hsn_chapter_out_of_mvp_scope`

## Step 9 - Checksums

Recomputed `ai_checksum` for **all 224** kept records, not just mutated ones, using `sha256` over `json.dumps(ai, sort_keys=True, ensure_ascii=False, separators=(',',':'))`.

- Checksums whose value changed: **224**
- Checksums that recomputed to the same value: **0**

Every input checksum matched the formula before patching, which confirms the digest recipe is the one that generated the v5 file.

## Step 10 - Validation

**PASS** - all 224 kept records pass `validate()` with zero errors.

Additional checks beyond the spec's `validate()` - `rate_source` enum, resolved rates carrying a real source, checksum integrity, and v6 key order - also pass on all 224 records.

## Step 10b - Rate drift

Two independent checks. `merged 1.jsonl` holds several record kinds per code (HSN/SAC masters plus `GST_RATE` notification rows), so `code` alone is not a unique key - the join is on `(entity_type, code)`, asserted unique across all 224 matched records.

**1. Patch drift (output vs input) - is this script the cause of any change?**

**PASS.** Zero differences in `gst_rate` or `rate_confidence` between each kept record and its input. The patch provably added the derived split and changed no rate value.

**2. Source drift (output vs `merged 1.jsonl`) - does the file still agree with the rate source?**

- Records compared: **224**
- `gst_rate` mismatches: **0**
- `rate_confidence` mismatches: **0**

8 record(s) carry `rate_confidence = "unresolved"` where merged has `metadata.rate_confidence = null`. These are treated as equivalent encodings of "no rate matched" - a pre-existing convention difference between the enrichment pass and the source file, present before this patch and unchanged by it. Not counted as drift.

## Chapter coverage - the remaining enrichment gap

| Chapter | Records | Status |
|---|---:|---|
| 19 | 5 | light |
| 20 | 8 | light |
| 21 | 5 | light |
| 22 (demo exception) | 2 | thin |
| 28 | 48 | ok |
| 29 | 41 | ok |
| 33 | 8 | light |
| 39 | 26 | ok |
| 61 | 16 | ok |
| 62 | 17 | ok |
| 63 (demo exception) | 9 | light |
| 73 | 26 | ok |
| 84 | 0 | **ZERO COVERAGE** |
| 90 (demo exception) | 1 | thin |
| SAC (all) | 12 | thin |
| **Total kept** | **224** | |

### Zero-coverage chapters

- **Chapter 84 has no records at all.** Engineering and machinery, 87 headings in the tariff - the single largest gap in the MVP set.

### Thin chapters

chapter 19 (5), chapter 20 (8), chapter 21 (5), chapter 22 (2), chapter 33 (8), chapter 63 (9), chapter 90 (1), and the SAC set (12) are all light relative to their tariff size.

## Outputs

| File | Records | Contents |
|---|---:|---|
| `enriched_v6.jsonl` | 224 | kept records, v6 schema |
| `quarantine.jsonl` | 116 | out-of-scope records, v5 + `quarantine_reason` |
| `needs_one_liner.txt` | 224 | kept records awaiting a one-liner, demo-path first |
| `patch_report.md` | - | this file |

Input files were not modified. Output is UTF-8 with LF line endings and compact `(',',':')` separators, matching the input's encoding style. Re-running the script on its own output produces a byte-identical `enriched_v6.jsonl`.

## Notes and deviations

- golden_dataset.jsonl was fully redundant (all 26 ids already in enriched.jsonl) and was not merged. No records dropped.
- The rate reference is named `merged_1.jsonl` in the task spec but is `merged 1.jsonl` (space) on disk; the script uses the real filename.
- `HSN_SAC.xlsx` is listed as a reference input but is not present in the project. It is reference-only in the spec and nothing in Steps 1-11 reads from it, so no step was affected and `openpyxl` is not imported.
- Quarantined records keep the v5 `rate` shape (with `composition_note`, no split). They are preserved for a post-hackathon pass, not migrated.
- `one_line_rationale` is placed immediately after `plain_rationale` in the `ai` object. Key order does not affect `ai_checksum`, which sorts keys.
- A re-run preserves any `one_line_rationale` that has been authored by hand rather than resetting it to null, so filling them in and re-running is safe and still idempotent.
- Re-running against `enriched_v6.jsonl` reproduces it byte for byte. Note that 4 of the 26 golden ids (`HSN_8708`, `HSN_4819`, `HSN_04090000`, `NIC_14101`) are out of MVP scope, so on such a re-run Step 1 sees them as absent and re-merges them, and Step 2 immediately re-quarantines them. The kept set is unaffected; only `quarantine.jsonl` is shorter on the second pass.

