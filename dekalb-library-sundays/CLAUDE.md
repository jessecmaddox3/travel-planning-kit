# Open Sundays DeKalb — project instructions

A resident campaign to open all 23 DeKalb County, Georgia public libraries on Sundays from noon to 5. Start with `README.md`. If `private/HANDOFF.md` exists, read it next: it holds the project history, decisions and next steps.

## Decisions already made by the organiser (do not reopen)
- The ask is **every branch**, opening on the same day. No pilot, no subset. If the county offers less, bring it to the organiser to decide.
- Public material lives in this folder and may be committed. Candid political notes live in `private/`, which is git-ignored and must never be committed, published or quoted in public files.
- "Open Sundays DeKalb" is a working name.

## Rules for facts
- Every number in a public file must appear in `research/01-facts-and-sources.md` with a source and a confidence label. Add it there first.
- Cost figures are the campaign's estimates until DeKalb County Public Library supplies its own. Say "we estimate". When the library's numbers arrive, put them in the cost model and update every file that quotes the old ones.
- Never invent quotes, endorsements, survey results, signature counts or personal stories. Templates use brackets for anything not yet true.
- People named in these files are real. Describe them only from public sources, and keep inference in `private/`, labelled as inference.

## Cost model
- `cost-model/build_cost_model.py` writes `cost-model/sunday-hours-cost-model.xlsx`. Inputs and the branch list live in the script; every result in the workbook is a formula.
- After changing inputs: run the script, recalculate, then update the figures quoted in `README.md`, `the-case-for-sundays.md`, `cost-model/README.md`, `research/01-facts-and-sources.md` and the toolkit. Search for the old number to find them all.
- Base case as of November 21, 2026: $1,648,950 a year; $2.15 per resident; 0.27% of the General Fund; 115 added hours a week (9.8%); first year $627,664 with a September 12, 2027 opening.

## Tone
- For the library, never against it. No criticism of library staff or of named officials in public material.
- Plain words, one number at a time, and state the weak points honestly.

## Working with the organiser
- Draft emails, requests and posts; do not send or publish anything without being asked.
- Budget dates matter. The county's CEO recommends a budget by December 15, commissioners adopt by March 1, and a mid-year adjustment follows in June–July. Check current dates on dekalbcountyga.gov and dekalblibrary.org before quoting them.
