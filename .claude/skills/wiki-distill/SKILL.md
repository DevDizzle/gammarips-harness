---
name: wiki-distill
description: Ingest a finding into the wiki as a claim-tagged note — from journal lessons, the GammaRips engine research docs, or external literature. Use when a lesson recurs, engine research lands, or a best practice needs encoding.
---

# wiki-distill

Read `wiki/_index/WIKI-SCHEMA.md` first. One claim per note; edit-over-duplicate; the
`Exit-context` field is mandatory and load-bearing.

## Procedure
1. **Check for an existing note** (`wiki/_index/FINDINGS.md` + grep). An update to an
   existing claim edits that note (and flips `Status: superseded` on what it replaces if
   the claim reversed). Only genuinely new claims get new files.
2. **Pick the tag honestly** per the schema vocabulary. The two classic errors:
   - upgrading `fragile-conditional` → `proven-on-cohort` because it "keeps working"
     (that's what the forward label arm is for);
   - tagging literature `proven-on-cohort` because it matches our intuition.
3. **State the evidence with its N, cohort, and exit-context.** A finding without its
   hold/exit assumption is not admissible.
4. **Write the Application paragraph** — how the daily loop actually uses it. A note no
   skill would ever cite is trivia; leave it out.
5. **Wire wikilinks** to related notes; register in `_index/FINDINGS.md` (one line + tag).
6. `python scripts/lint.py`.

## Allowed sources
Journal lessons; external research docs (research ledger, briefs,
docs/DECISIONS — knowledge curation is the one firewall exception); external literature
(verify the citation before asserting it). NEVER distill anything that encodes the
any external pick or same-day engine state.
