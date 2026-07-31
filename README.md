# GST Classification Engine — knowledge base

**IRIS-HACK-P-2026-001**

The deliverable is **`enriched_complete.jsonl`** — 339 records, v6 schema, validator-clean.
Open **`gst_browser.html`** in any browser to explore it (no server needed).

---

## Files — what each one is for

### Deliverables

| File | What it is |
|---|---|
| `enriched_complete.jsonl` | **The knowledge base.** 339 records (307 HSN + 32 SAC), v6 schema. |
| `gst_browser.html` | Self-contained UI. Double-click to open — data is embedded, no server. |
| `artifact_blocklist.json` | 13 codes that look like HSN headings but aren't. **Wire this into whatever loads the KB** so they are never indexed or returned. |
| `demo_seed.json` | Provenance for the 2 hand-entered rates. Each entry carries a `source_note`. |

### Source data — never delete

| File | Why it must stay |
|---|---|
| `merged 1.jsonl` | The rate source (34 MB). Every build stage reads it. |
| `enriched.jsonl` | The original 340-record file. Rollback point and input to stage 1. Never modified by any script. |
| `golden_dataset.jsonl` | Input to stage 1. |
| `quarantine.jsonl` | The 116 records held out of MVP scope, each with a `quarantine_reason`. Input to stage 2, which restores `HSN_4819` from it. |
| `sources.yaml` | Source registry. |

### Calculator

`scripts/gst_calc.py` — deterministic GST computation. Pure stdlib, no floats: every
money value is a `decimal.Decimal` quantised with `ROUND_HALF_UP`.

```bash
python scripts/gst_calc.py --value 10000 --rate 18 --from 27 --to 27   # CGST + SGST
python scripts/gst_calc.py --value 10000 --rate 18 --from 04 --to 04   # CGST + UTGST
python scripts/gst_calc.py --value 11800 --rate 18 --from 27 --to 27 --inclusive
python scripts/gst_calc.py --code HSN_6109 --value 5000 --from 27 --to 24
python scripts/gst_calc.py --selftest        # 15 vectors + invariants
python scripts/gst_calc.py --list-states     # every code and its state half
```

**SGST vs UTGST is not "State vs Union Territory".** The UTGST Act 2017 s.2(8) excludes
Delhi and Puducherry, which have their own legislatures and their own SGST Acts; Jammu &
Kashmir likewise became a UT *with* legislature in Oct 2019. So:

| Jurisdiction | Count | State half |
|---|---:|---|
| States | 28 | **SGST** |
| UTs **with** legislature — Delhi, Puducherry, Jammu & Kashmir | 3 | **SGST** |
| UTs **without** legislature — Chandigarh, Ladakh, Lakshadweep, A&N Islands, D&NH and D&D | 5 | **UTGST** |
| Other Territory (97) | 1 | UTGST |

Codes `25` (Daman & Diu) and `28` (pre-bifurcation Andhra Pradesh) are **deprecated** and
are rejected rather than silently accepted.

**Rounding is stated, not implied.** Each component is computed independently from the
taxable value at its own rate, then rounded to 2 dp half-up — CGST and SGST/UTGST are each
computed at `rate/2`, never by halving a rounded total. A consequence, reported as
`split_residue` rather than hidden: for some values an intra-State total can differ from
the inter-State total by ₹0.01, because two roundings are not one. `--round-total` rounds
the invoice total to the nearest rupee per CGST Act s.170 (off by default).

`--code` reads the rate straight from `enriched_complete.jsonl` and **refuses** to compute
when that rate is `null`, rather than assuming zero.

The browser embeds a JavaScript port that works in integer paise. It recomputes 252
Python-generated vectors on load and prints the result in the sidebar — if the two
implementations ever disagree the page says so instead of showing a wrong tax.

### Audit trail

`patch_report.md` → `gap_report.md` → `coverage_report.md`, one per build stage. Each
records what changed, what was validated, and every deviation from its spec. Read these
before trusting a number.

---

## Rebuilding — after any GST update

**One command rebuilds everything:**

```bash
python scripts/rebuild_all.py
```

It runs all four stages in order, stops at the first failure without touching the previous
good output, checks the result (checksums, rate splits, duplicate ids), and tells you
whether `enriched_complete.jsonl` actually **CHANGED** or was **unchanged**.

`--keep` retains the intermediates if you want to re-run a single stage. `--dry-run` lists
what would run.

### Where to make the edit so it survives

**Never hand-edit `enriched_complete.jsonl`.** It is a build output — the next rebuild
overwrites it, and a hand edit also invalidates that record's `ai_checksum`. Edit the
source below, then re-run:

| What you changed | Edit this |
|---|---|
| A rate that comes from the schedules | `merged 1.jsonl` |
| A hand-seeded rate | `DEMO_SEED` in `scripts/gap_fill_v6.py` — **`demo_seed.json` is an output, not an input** |
| Chapter 84 / SAC / `8708` enrichment | `scripts/gap_content.py` |
| The final 6 headings (`2105`, `2006`, chemicals) | `scripts/close_gap_content.py` |
| A demo one-line rationale | `ONE_LINERS` in `scripts/gap_content.py` |
| Blocked artifact codes | `BLOCKED_HARDCODED` in `scripts/close_gap_v6.py` |
| Which chapters are in scope | `MVP_CHAPTERS` in the stage scripts |

If the rebuild reports **unchanged** when you expected a diff, you almost certainly edited
a build output rather than a source.

### Running the stages individually

```bash
python scripts/patch_enriched_v5_to_v6.py   # enriched.jsonl  -> enriched_v6.jsonl (+ quarantine)
python scripts/gap_fill_v6.py               #                 -> enriched_final.jsonl (+ demo_seed)
python scripts/close_gap_v6.py              #                 -> enriched_complete.jsonl (+ blocklist)
python scripts/build_browser.py             #                 -> gst_browser.html
```

Stage 2 reads `updat_enriched.jsonl` **or** `enriched_v6.jsonl` — they are the same file
under two names. The intermediates (`enriched_v6.jsonl`, `enriched_final.jsonl`,
`needs_one_liner.txt`) are build artifacts and are not kept; every stage tells you which
script regenerates its input if it is missing.

`scripts/_legacy/` holds the 10 scripts that authored the original `enriched.jsonl`.
Nothing in the current pipeline uses them, but they are the only record of how that
content was written. **`_legacy/build_legacy_golden.py` writes into `enriched.jsonl`** —
do not run it unless you intend to modify the original.

---

## Known open items

Carried forward from the build reports. None blocks the demo; all matter before production.

1. **Two seeded rates are unverified.** `HSN_6307` and `HSN_63079091` (textile face masks)
   are set to 5% from figures supplied in the task spec, **not** checked against CBIC —
   the builds ran offline. They are on the flagship demo path. See `demo_seed.json`.
2. **19 records have no rate.** Including `HSN_2105` (ice cream) and `HSN_8413` (liquid
   pumps), both plain-language search terms. `coverage_report.md` explains why, and how
   to change it with one flag.
3. **The artifact scan never ran.** `HSN_SAC.xlsx` is absent, so only the 13 known
   artifacts are blocked. There may be more in unaudited chapters.
4. **325 of 339 records have `one_line_rationale: null`.** Only the 14 demo-path records
   were written.
5. **6 chapter-33 records have a stale `search_text`** containing pre-v6 sector wording.
   Cosmetic — it only adds stray search tokens.

## Conventions

- Rates come from `merged 1.jsonl`, or from `demo_seed.json` with a `source_note`, or are
  `null`. **Never invented.** `rate_source` records which, on every record.
- `cgst` and `sgst` in the data are each exactly half of `gst_rate`; `igst` equals it. No
  rounding. The `sgst` **field name is jurisdiction-neutral** — it carries the state half,
  which is levied as UTGST in a Union Territory without a legislature. Use
  `gst_calc.state_tax_label(code)` to resolve the correct name; never print "SGST" blindly.
- `classification_confidence` (how sure we are of the code) is independent of
  `rate_confidence` (how sure we are of the rate). A record can be High on one and
  unresolved on the other.
- Every build is idempotent — re-running produces a byte-identical file.
