# How the kit is designed

> **TL;DR:** Keep the reusable machinery separate from the trip. Use one explicit document and one rendering engine for the editor, commands and offline examples. Keep unknowns visible.

## The workflow

Start with requirements and a reusable packing catalog. Research candidate places with sources and dated quotes. Keep a ranked shortlist, alternatives and reasons for ruling something out. Turn decisions into a day plan, then record what worked afterward. These are connected parts of one trip, rather than four unrelated documents.

The catalog uses stable item IDs and trip tags. Explicit additions and exclusions survive changes to the suggested selection. The departure-morning block repeats high-attention items instead of hiding them in a long checklist. The print layout keeps the two-column structure.

The planning document retains uncertainty and ownership: open decisions have urgency, options, an owner and a due date. Preferences stay next to the plan so later edits do not erase why a choice was made. The review section supplies the next trip's starting point.

Rental comparisons preserve the richer design: illustrated header, jump navigation, ranked cards, photo strips, sleeping and practical details, alternatives and rejected choices. The separate 22-column view supports careful comparison. Its print version groups the same fields into readable landscape tables.

## Implementation

`schema.py` validates a closed versioned format and returns a deep copy. `model.py` handles dates, selection, URL safety and Decimal money. `render.py` escapes user text and produces complete HTML using local CSS. `cli.py` and the loopback editor call those same renderers. No module generates files or starts a network request merely because it is imported.

The editor holds the draft in browser memory. Saving validates it and downloads JSON. It does not silently write to the original configuration, choose arbitrary disk paths, or accept newer unsupported formats. Failed imports leave the draft alone; failed previews leave the previous good document visible. The server is limited to one chosen asset folder and requires its session token and exact local origin for actions.

Photo collection is deliberately separate. `fetch-photos` is an explicit network operation with bounded pages, timeouts and per-listing failures. `apply-photos` attaches the resulting URLs by stable property ID without fetching image bytes. Local images embed into documents; external images remain links by default.

## Adapting the design

Document colors and font stacks live in `travel_kit/theme.py`. Packing and plan layout rules live in `document.css`. The gallery and editor use the forest/copper palette in their own CSS files. No remote fonts are required; the kit uses system fonts. Change the theme files in your copy if you prefer different typography or colors.

The templates and optional skill work with any research process. Google Docs upload is not integrated. You can copy text from the plan into your own document, print HTML to PDF, or build a separate integration using your own account. A trip portal can also consume selected fields, but this kit does not require one or promise compatibility with a particular portal schema.
