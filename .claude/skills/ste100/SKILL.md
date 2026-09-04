---
name: ste100
description: Write prose in ASD-STE100 Simplified Technical English. Use this skill before you write or edit any prose in this repo - chat replies, docs, PRDs, PR descriptions, commit messages, and emails. It holds the house style rules, and it builds a local searchable copy of the official standard on request. Triggers - "STE", "Simplified Technical English", "plain English", "simplify this text", "make this easier to read", or any request to write a document, README, PRD, spec, email, or release note.
---

# Simplified Technical English (ASD-STE100)

## Purpose

Write text that is easy to read. The goal is the reader's comprehension, not compliance
with a standard. When a rule and clarity disagree, choose clarity. Then say which rule
you broke.

Trading text has a second reason to be plain. A consult is read fast, in the morning,
before the market moves. A sentence the reader must read twice is a sentence that costs
money.

## The rules that always apply

Apply these to every sentence. You do not need the full standard for them.

1. **Start with the answer.** Give the conclusion in the first sentence. Then the detail.
2. **Short sentences.** 20 words maximum in a procedure. 25 in a description.
3. **Active voice.** "The screen dropped 20 names", not "20 names were dropped".
4. **Imperative for instructions.** "Check the spread", not "the spread should be checked".
5. **Simple tenses only.** Do not use the "-ing" form as a verb.
6. **One instruction per sentence.**
7. **One topic per paragraph.** Six sentences maximum.
8. **Same word, same thing, every time.** Do not vary the word for variety.
9. **No semicolons.**
10. **Spell out each acronym at first use.**

## Word substitutions you will need most

The standard has a full table of about 40. These are the ones that come up in this repo:

| Do not write | Write |
|---|---|
| perform | do |
| ensure, verify | make sure that |
| however | but |
| shall, should | must |
| e.g. | for example |
| i.e. | that is |
| utilize | use |
| in order to | to |
| prior to | before |
| via | with, by |
| approximately | about |
| may | can |

Run `build.py` (below) to generate the complete official table.

## What STE does not cover

STE applies to prose only. Keep these verbatim. Do not simplify them:

- Code, commands, SQL, file paths, and configuration
- Identifiers: function names, table names, flags, environment variables
- Quoted tool output, log lines, and error messages
- Numbers, tickers, strikes, and measured values
- Domain terms that are technical nouns: delta, theta, spread, open interest,
  time-stop, maximum favorable excursion, implied volatility

A technical noun stays a technical noun. Do not replace "theta" with "time decay cost"
to satisfy a word list. Do spell it out once, the first time.

## Get the full standard (optional, and it is yours to download)

This repository does **not** ship the standard. ASD-STE100 is copyrighted by the
Aerospace, Security and Defence Industries Association of Europe (ASD), and the document
states that no reproduction or publication of it, in whole or in part, may be made
without written authority from an officer of ASD. ASD grants free reproduction rights to
a named list of bodies: members of ASD, AIA, AIAC and ICCAIA and their customers, defence
ministries, Airlines for America, airworthiness authorities, and universities for
educational purposes. A public repository is not on that list.

The rules above are enough for daily writing. If you want the full reference, download
your own copy. ASD offers it free of charge:

```bash
python .claude/skills/ste100/build.py
```

The script downloads the PDF from asd-ste100.org and writes these files into
`.claude/skills/ste100/reference/`:

| File | What it holds |
|---|---|
| `dictionary.txt` | Part 2, the dictionary, as searchable text |
| `part1-rules-full.txt` | Part 1, all writing rules with their examples |
| `rules-summary.md` | Every rule number and its statement, in one table |
| `verbs.txt` | The approved verbs |
| `recurring-errors.md` | The official substitution table |
| `ASD-STE100_ISSUE9.pdf` | Your downloaded copy |

`reference/` is gitignored. Do not commit anything in it.

You need one PDF text extractor:

```bash
pip install pymupdf        # preferred
pip install pypdf          # or this
apt-get install poppler-utils   # or this, for the pdftotext command
```

Search the dictionary once it is built:

```bash
grep -n -i -A6 '^ENSURE' .claude/skills/ste100/reference/dictionary.txt
grep -n -i 'however' .claude/skills/ste100/reference/dictionary.txt | head
```

## Checklist before you send

1. Does the first sentence give the answer?
2. Is any sentence longer than 20 words, or 25 in a description?
3. Is any verb passive, or in the "-ing" form?
4. Does a paragraph hold more than one topic, or more than six sentences?
5. Did you use a word from the left column of the table above?
6. Did you spell out each acronym at first use?
7. Is there a semicolon?

If the reader says "unclear", write the reply again in a simpler form. Do not defend the
first version.
