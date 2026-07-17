#!/usr/bin/env python3
"""Deterministic health check for the gammarips-trader harness.

Checks wiki note headers/tags/registry/links and journal entry shape.
Run after any journal or wiki change: python scripts/lint.py
Exit code 0 = clean, 1 = problems found.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI_DIRS = [ROOT / "wiki" / d for d in ("findings", "literature", "concepts")]
REGISTRY = ROOT / "wiki" / "_index" / "FINDINGS.md"
JOURNAL = ROOT / "journal"

VALID_STATUS = {"active", "superseded"}
VALID_TYPE = {"finding", "literature", "concept"}
VALID_TAG = {
    "proven-on-cohort", "falsified-on-cohort", "fragile-conditional",
    "literature-established", "untested-hypothesis", "policy-adopted",
}
VALID_JOURNAL_STATUS = {"draft", "committed", "open", "closed", "no-trade"}
REQUIRED_HEADERS = ["Status", "Type", "Tag", "Exit-context", "Source", "Date"]
JOURNAL_SECTIONS = ["## Pool context", "## Thesis", "## Exit plan", "## Critic"]

problems = []


def err(path, msg):
    problems.append(f"{path.relative_to(ROOT)}: {msg}")


def header_value(text, key):
    m = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else None


# --- wiki notes ---
notes = {}  # slug -> path
for d in WIKI_DIRS:
    if not d.exists():
        continue
    for f in sorted(d.glob("*.md")):
        notes[f.stem] = f
        text = f.read_text()
        for key in REQUIRED_HEADERS:
            if header_value(text, key) is None:
                err(f, f"missing header line '{key}:'")
        status = header_value(text, "Status")
        if status and status not in VALID_STATUS:
            err(f, f"invalid Status '{status}'")
        ntype = header_value(text, "Type")
        if ntype and ntype not in VALID_TYPE:
            err(f, f"invalid Type '{ntype}'")
        tag = header_value(text, "Tag")
        if tag and tag.split()[0] not in VALID_TAG:
            err(f, f"invalid Tag '{tag}'")

# --- registry ---
if REGISTRY.exists():
    reg_text = REGISTRY.read_text()
    reg_slugs = set(re.findall(r"\[\[([a-z0-9-]+)\]\]", reg_text))
    for slug, f in notes.items():
        if slug not in reg_slugs:
            err(f, "not registered in _index/FINDINGS.md")
    for slug in reg_slugs:
        if slug not in notes:
            err(REGISTRY, f"registry entry [[{slug}]] has no note file")
else:
    problems.append("wiki/_index/FINDINGS.md missing")

# --- wikilink resolution (wiki + journal) ---
link_sources = [f for d in WIKI_DIRS if d.exists() for f in d.glob("*.md")]
if JOURNAL.exists():
    link_sources += [f for f in JOURNAL.glob("*.md") if f.name != "_TEMPLATE.md"]
for f in link_sources:
    for slug in re.findall(r"\[\[([a-z0-9-]+)\]\]", f.read_text()):
        if slug not in notes:
            err(f, f"broken wikilink [[{slug}]]")

# --- journal entries ---
for f in sorted(JOURNAL.glob("*.md")) if JOURNAL.exists() else []:
    if f.name == "_TEMPLATE.md":
        continue
    if not re.match(r"^\d{4}-\d{2}-\d{2}\.md$", f.name):
        err(f, "journal filename must be YYYY-MM-DD.md")
        continue
    text = f.read_text()
    status = header_value(text, "Status")
    if status is None or status not in VALID_JOURNAL_STATUS:
        err(f, f"missing or invalid journal Status '{status}'")
        continue
    if status in {"committed", "open", "closed"}:
        committed = header_value(text, "Committed-at")
        if not committed or committed.startswith("("):
            err(f, f"Status '{status}' but Committed-at not set")
        for section in JOURNAL_SECTIONS:
            if section not in text:
                err(f, f"missing section '{section}'")
    if status == "closed" and "## Outcome" not in text:
        err(f, "closed entry missing '## Outcome'")

if problems:
    print(f"LINT: {len(problems)} problem(s)")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
print(f"LINT: clean ({len(notes)} wiki notes, "
      f"{len([f for f in JOURNAL.glob('*.md') if f.name != '_TEMPLATE.md']) if JOURNAL.exists() else 0} journal entries)")
