#!/usr/bin/env python3
"""build.py — fetch ASD-STE100 Issue 9 and extract the local reference files.

Run this once, from anywhere:

    python .claude/skills/ste100/build.py

It downloads the official standard from asd-ste100.org and writes the searchable
reference into `reference/`, beside this script. Everything it writes is gitignored.

WHY THIS IS A DOWNLOADER AND NOT A DATA FILE
--------------------------------------------
ASD-STE100 is copyrighted by the Aerospace, Security and Defence Industries Association
of Europe (ASD). The standard states: "no reproduction or publication of it, in whole or
in part, shall be made without the written authority of an officer of ASD." It grants
free reproduction rights to a named list of bodies (ASD/AIA/AIAC/ICCAIA members and their
customers, defence ministries, Airlines for America, airworthiness authorities, and
universities for educational purposes). A public MIT-licensed repository is not on that
list.

So this repository ships the tool, not the text. You download your own copy, which
asd-ste100.org offers free of charge. The extracted files stay on your machine.

DEPENDENCIES
------------
One PDF text extractor. The script tries them in order and tells you what to install:
    pip install pymupdf        (preferred)
    pip install pypdf
    apt-get install poppler-utils   (gives the `pdftotext` command)
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

URL = "https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf"
HERE = Path(__file__).resolve().parent
REF = HERE / "reference"
PDF = REF / "ASD-STE100_ISSUE9.pdf"

# Part boundaries as 1-based document pages, from the Issue 9 table of contents.
PART1 = (43, 128)      # Writing rules
PART2 = (129, 434)     # Dictionary
MIN_PAGES = 400        # sanity check that we got the whole document


def die(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def download() -> None:
    if PDF.exists() and PDF.stat().st_size > 1_000_000:
        print(f"  have {PDF.name} ({PDF.stat().st_size:,} bytes) — skipping download")
        return
    REF.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {URL}")
    try:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(PDF, "wb") as f:
            shutil.copyfileobj(r, f)
    except Exception as e:                                    # noqa: BLE001
        die(f"download failed ({e}).\n"
            f"       Get the PDF by hand from {URL}\n"
            f"       and put it at {PDF}")
    print(f"  saved {PDF.stat().st_size:,} bytes")


def pages() -> list[str]:
    """Return per-page text. Try pymupdf, then pypdf, then pdftotext."""
    try:
        import fitz                                           # type: ignore
        d = fitz.open(PDF)
        return [d[i].get_text() for i in range(d.page_count)]
    except ImportError:
        pass
    try:
        from pypdf import PdfReader                           # type: ignore
        return [p.extract_text() or "" for p in PdfReader(str(PDF)).pages]
    except ImportError:
        pass
    if shutil.which("pdftotext"):
        txt = REF / "_raw.txt"
        subprocess.run(["pdftotext", "-layout", str(PDF), str(txt)], check=True)
        out = txt.read_text(errors="replace").split("\f")
        txt.unlink(missing_ok=True)
        return out
    die("no PDF text extractor found.\n"
        "       pip install pymupdf   (or pypdf, or apt-get install poppler-utils)")
    return []


HEADERS = (
    r"ASD[- ]STE100 Simplified Technical English\s*",
    r"Page \d+-\d+-\d+\s*",
    r"Part \d+ [-–] [A-Za-z ]+\s*",
    r"Issue 9\s*",
    r"2025-01-15\s*",
)


def clean(t: str) -> str:
    for pat in HEADERS:
        t = re.sub(pat, "", t)
    return t


def slice_text(pg: list[str], span: tuple[int, int]) -> str:
    lo, hi = span
    return "".join(clean(pg[i]) for i in range(lo - 1, min(hi, len(pg))))


def extract_rules(part1: str) -> dict[str, str]:
    hits = list(re.finditer(r"\bRule (\d+\.\d+)\s*\n", part1))
    rules: dict[str, str] = {}
    for n, m in enumerate(hits):
        num = m.group(1)
        end = hits[n + 1].start() if n + 1 < len(hits) else len(part1)
        body = part1[m.end():end]
        stmt = " ".join(re.split(r"\n\s*\n|Examples?:|Example:|Note:", body)[0].split())
        if len(stmt) > len(rules.get(num, "")):
            rules[num] = stmt[:300]
    return rules


def extract_errors(pg: list[str]) -> list[tuple[str, str]]:
    """The 'List of recurring errors' table: alternating non-STE / STE lines."""
    body = ""
    for i, t in enumerate(pg):
        if "List of recurring errors" in t:
            body += clean(t).split("List of recurring errors", 1)[1]
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    try:
        start = lines.index("STE") + 1
    except ValueError:
        start = 0
    rows, buf = [], []
    for ln in lines[start:]:
        if ln in ("Non-STE", "STE", "(continued)"):
            continue
        buf.append(ln)
        if len(buf) == 2:
            rows.append((buf[0], buf[1]))
            buf = []
    return rows


def main() -> None:
    print("ASD-STE100 reference builder")
    download()
    REF.mkdir(parents=True, exist_ok=True)

    pg = pages()
    if len(pg) < MIN_PAGES:
        die(f"got {len(pg)} pages, expected >= {MIN_PAGES}. The PDF looks wrong or partial.")
    print(f"  {len(pg)} pages read")

    part1 = slice_text(pg, PART1)
    part2 = slice_text(pg, PART2)
    (REF / "part1-rules-full.txt").write_text(part1)
    (REF / "dictionary.txt").write_text(part2)

    rules = extract_rules(part1)
    lines = ["# ASD-STE100 Issue 9 — rule statements", "",
             "Generated by build.py. Not for redistribution.", "",
             "| Rule | Statement |", "|---|---|"]
    for k in sorted(rules, key=lambda s: [int(x) for x in s.split(".")]):
        lines.append(f"| {k} | {rules[k]} |")
    (REF / "rules-summary.md").write_text("\n".join(lines) + "\n")

    verbs = sorted(set(re.findall(r"\b([A-Z][A-Z\-]{1,20})\s*\(v\)", part2)))
    (REF / "verbs.txt").write_text("\n".join(verbs) + "\n")

    errors = extract_errors(pg)
    elines = ["# Recurring errors", "",
              "Generated by build.py. Not for redistribution.", "",
              "| Do not write | Write |", "|---|---|"]
    elines += [f"| {a} | {b} |" for a, b in errors]
    (REF / "recurring-errors.md").write_text("\n".join(elines) + "\n")

    print(f"\n  rules-summary.md     {len(rules)} rules")
    print(f"  verbs.txt            {len(verbs)} approved verbs")
    print(f"  recurring-errors.md  {len(errors)} substitutions")
    print(f"  dictionary.txt       {len(part2):,} characters")
    print(f"  part1-rules-full.txt {len(part1):,} characters")
    print(f"\nDone. Files are in {REF}")
    print("They are gitignored. Do not commit them or the PDF.")
    json.dump({"rules": len(rules), "verbs": len(verbs), "errors": len(errors),
               "pages": len(pg)}, open(REF / "build-manifest.json", "w"), indent=1)


if __name__ == "__main__":
    main()
