#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild everything, in order, from source.

    python scripts/rebuild_all.py

Runs the four build stages, stops at the first failure, then sanity-checks the
result. Use this after changing anything upstream - a rate in the reference
data, enrichment content, a manual seed, the blocklist, or the scope lists.

    --keep      keep the intermediate files (enriched_v6.jsonl,
                enriched_final.jsonl, needs_one_liner.txt) instead of removing
                them; useful when you want to re-run a single stage afterwards
    --dry-run   list what would run, change nothing

WHERE TO MAKE AN EDIT SO IT SURVIVES
------------------------------------
Never edit enriched_complete.jsonl by hand - it is a build output and the next
rebuild overwrites it. Edit the source, then re-run this script:

  a rate that comes from the schedules   ->  "merged 1.jsonl"
  a hand-seeded rate                     ->  DEMO_SEED in scripts/gap_fill_v6.py
                                             (demo_seed.json is OUTPUT, not input)
  chapter 84 / SAC / 8708 enrichment     ->  scripts/gap_content.py
  the final 6 headings                   ->  scripts/close_gap_content.py
  demo one-line rationales               ->  ONE_LINERS in scripts/gap_content.py
  blocked artifact codes                 ->  BLOCKED_HARDCODED in close_gap_v6.py
  which chapters are in scope            ->  MVP_CHAPTERS in the stage scripts
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)

STAGES = [
    ("patch_enriched_v5_to_v6.py", "enriched.jsonl -> enriched_v6.jsonl + quarantine"),
    ("gap_fill_v6.py", "-> enriched_final.jsonl + demo_seed.json"),
    ("close_gap_v6.py", "-> enriched_complete.jsonl + artifact_blocklist.json"),
    ("build_browser.py", "-> gst_browser.html"),
]

INTERMEDIATES = ["enriched_v6.jsonl", "enriched_final.jsonl", "needs_one_liner.txt"]

FINAL = os.path.join(BASE, "enriched_complete.jsonl")
BROWSER = os.path.join(BASE, "gst_browser.html")

REQUIRED_SOURCES = ["enriched.jsonl", "golden_dataset.jsonl", "merged 1.jsonl",
                    "quarantine.jsonl"]


def sha(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true",
                    help="keep intermediate build files")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    missing = [f for f in REQUIRED_SOURCES if not os.path.exists(os.path.join(BASE, f))]
    if missing:
        sys.stderr.write("Missing source file(s), cannot build:\n")
        for f in missing:
            sys.stderr.write("  - %s\n" % f)
        return 1

    before_final = sha(FINAL)
    before_browser = sha(BROWSER)

    if a.dry_run:
        print("Would run, in order:")
        for i, (s, what) in enumerate(STAGES, 1):
            print("  %d. %-28s %s" % (i, s, what))
        print("Then %s the intermediates: %s"
              % ("keep" if a.keep else "remove", ", ".join(INTERMEDIATES)))
        return 0

    t0 = time.time()
    for i, (script, what) in enumerate(STAGES, 1):
        print("\n[%d/%d] %s" % (i, len(STAGES), script))
        print("       %s" % what)
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           cwd=BASE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        for line in (r.stdout or "").splitlines():
            print("       " + line)
        if r.returncode != 0:
            sys.stderr.write("\n" + (r.stderr or "").strip() + "\n")
            sys.stderr.write("\nSTOPPED at stage %d (%s). Nothing further was run.\n"
                             % (i, script))
            sys.stderr.write("The previous enriched_complete.jsonl is untouched.\n")
            return 1

    # ---- sanity-check the result -------------------------------------------
    print("\n[check] verifying the rebuilt knowledge base")
    recs = [json.loads(l) for l in io.open(FINAL, encoding="utf-8") if l.strip()]
    problems = []
    for r in recs:
        ck = hashlib.sha256(json.dumps(r["ai"], sort_keys=True, ensure_ascii=False,
                                       separators=(",", ":")).encode("utf-8")).hexdigest()
        if r["ai_checksum"] != ck:
            problems.append("%s: stale ai_checksum" % r["id"])
        rt = r["rate"]
        if rt["gst_rate"] is not None:
            if rt["cgst"] != rt["gst_rate"] / 2 or rt["sgst"] != rt["gst_rate"] / 2 \
               or rt["igst"] != rt["gst_rate"]:
                problems.append("%s: CGST/SGST/IGST split wrong" % r["id"])
        elif any(rt[k] is not None for k in ("cgst", "sgst", "igst")):
            problems.append("%s: null rate but non-null split" % r["id"])
    ids = [r["id"] for r in recs]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids present")

    if problems:
        sys.stderr.write("       FAILED - %d problem(s):\n" % len(problems))
        for p in problems[:15]:
            sys.stderr.write("         %s\n" % p)
        return 1
    print("       %d records, checksums fresh, splits exact, no duplicates" % len(recs))

    if not a.keep:
        removed = []
        for f in INTERMEDIATES:
            p = os.path.join(BASE, f)
            if os.path.exists(p):
                os.remove(p)
                removed.append(f)
        if removed:
            print("\n[tidy] removed intermediates: %s" % ", ".join(removed))
            print("       (pass --keep to retain them for single-stage re-runs)")

    after_final, after_browser = sha(FINAL), sha(BROWSER)
    print("\n%s" % ("-" * 62))
    print("REBUILD OK in %.1fs" % (time.time() - t0))
    print("  enriched_complete.jsonl : %d records  %s" % (
        len(recs),
        "unchanged" if before_final == after_final else
        ("CHANGED" if before_final else "created")))
    print("  gst_browser.html        : %s" % (
        "unchanged" if before_browser == after_browser else
        ("CHANGED" if before_browser else "created")))
    if before_final and before_final == after_final:
        print("\n  Nothing changed. If you edited something and expected a diff, you")
        print("  probably edited a build output rather than a source - see the header")
        print("  of this file for where each kind of change belongs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
