# Wiki Schema

The `wiki/` is this harness's compiled-knowledge layer (LLM-wiki pattern: sources →
LLM-written notes → registry). One claim per note. Edit-over-duplicate.

## Note types
- `finding` (`wiki/findings/`) — a claim tested on our own cohorts/ledgers.
- `literature` (`wiki/literature/`) — a claim from external research/practice, not tested
  on our data.
- `concept` (`wiki/concepts/`) — definitional/background (greeks, IV mechanics, etc.).

## Required header block (every note)
```
Status: active | superseded
Type: finding | literature | concept
Tag: proven-on-cohort | falsified-on-cohort | fragile-conditional |
     literature-established | untested-hypothesis | policy-adopted
Exit-context: <the hold period + exit rule the evidence assumes; "n/a" only for
               methodology/concept notes>
Source: <engine doc / study / paper / journal entry>
Date: YYYY-MM-DD
```

**`Exit-context` is the load-bearing field.** This cohort's central lesson is that edges
are exit-conditional (mom_60 is real on a 3-day hold and ZERO on same-day GIGO). A finding
cited without its exit context is meaningless; the trade-critic fails any thesis that
cites a note whose exit-context doesn't match the planned hold.

## Tag semantics
- `proven-on-cohort` — held up on our labeled data with real N; still era-bound (note the
  cohort + exit).
- `falsified-on-cohort` — tested on our data and rejected; anti-edge. Falsified notes are
  as valuable as proven ones — keep them active.
- `fragile-conditional` — survived testing only under specific conditions; proposer-only;
  never load-bearing alone.
- `literature-established` — settled in published research; we deliberately did not
  re-test it on our small N.
- `untested-hypothesis` — plausible, not yet tested; never cite as support for a trade.
- `policy-adopted` — an operating rule we run (often literature-anchored), distinct from a
  measured edge.

## Conventions
- Wikilinks: `[[note-slug]]` (slug = filename without `.md`), resolvable across
  `findings/`, `literature/`, `concepts/`.
- Plain, concrete prose. Numbers with their N and cohort. No hype.
- Every note registered in `_index/FINDINGS.md` (one line + tag). `scripts/lint.py`
  enforces headers, tags, registry completeness, and link resolution.

## Firewall
Distillation may read external research docs (research ledger,
briefs, docs/DECISIONS) and external literature. It may NOT copy in anything
that would leak the any external pick or same-day engine state — the
wiki is knowledge, not a data side-channel.
