# Contributing

> **TL;DR:** Useful improvements are welcome. Preserve the complete workflows, use fictional fixtures, and test the behavior you change.

Run from the source folder with Python 3.11+:

```sh
python3 -m unittest discover -s tests
```

The browser suite uses Playwright only as a development tool. In a disposable virtual environment, install `playwright==1.58.0`, run `python -m playwright install chromium`, then run `python scripts/test-browser.py`. It exercises editing, validation recovery, JSON save/import, four document exports, responsive layouts and offline examples. Set `TRAVEL_SCREENSHOTS` to a temporary folder to retain screenshots and PDFs.

Keep rendering in the shared Python engine so the command line and editor agree. Preserve supported fields on round trips. Treat estimates as estimates, keep date/scope caveats visible, and test exact split remainders. New schema fields need a deliberate compatibility decision. Unsafe imports must fail without discarding the current draft.

Do not contribute real family rosters, trips, booking references, private communications, addresses or listing photos without appropriate permission. Invent the events and values, rather than just changing names in a real record. Keep source history and release archives free of private outputs. Add new source paths explicitly to the release allowlist.

For release packaging, use the pinned build requirements in `requirements-build.txt`, then run `python scripts/build-release.py`. The builder packages only explicitly allowlisted source files plus newly rendered fictional examples. Build artifacts are ignored. Review their contents, test a fresh extraction and installed wheel, and publish only after that review passes.
