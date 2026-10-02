# Claude session context — Wordler

> Paste as the first message in a new chat to resume.

## Who I am

- **Name:** Grandmaster (Spencer Thompson)
- **GitHub account:** `spencer-thompson-2-vu`
- **Claude goes by:** Fez

## Project

- **Name:** Wordler
- **Type:** Coding / PWA
- **Goal:** Wordle helper: enter guesses, mark tile colors, filter and rank remaining words.
- **Status:** Active
- **Repo:** https://github.com/spencer-thompson-2-vu/wordler
- **Live URL:** https://spencer-thompson-2-vu.github.io/wordler/
- **Current version:** v1.5
- **Stack:** Single-file HTML, vanilla JS, localStorage, PWA (manifest + service worker), GitHub Pages, one GitHub Action.

## Files

```
index.html                         App; all CSS + JS inline (~134 KB with word list)
manifest.json                      start_url and scope MUST stay /wordler/
sw.js                              Network-first shell/version/past-answers; cache-first assets
version.json                       {"version": "1.5"}
past-answers.json                  {"updated", "dates": {"YYYY-MM-DD": "WORD"}}; written by Action
icon-192.png, icon-512.png         purpose "any"
icon-maskable-512.png              purpose "maskable"; art inside 80% safe zone
scripts/update_past_answers.py     Stdlib-only fetcher (NYT /svc/wordle/v2/DATE.json)
.github/workflows/past-answers.yml Daily 09:30 UTC + manual run; commits past-answers.json
README.md, CONTEXT.md
```

## Features

- **Grid:** 6×5. ADD (or Enter) fills next row; tap tile cycles empty → gray → yellow → green. **↶** undo pops last row and returns its word to the input. NEW PUZZLE clears.
- **Header:** title, version (from `APP_VERSION`), EASY/HARD toggle, NEW PUZZLE.
- **Left column:** Starters (3 slots; default ARISE, COUNT, SLATE; wraps to two lines; ✎ edit modal) above Common (top 6 of pool).
- **Right column:** Helpful (6), full height.
  - Easy: any of 14,855 words; score = Σ `min(count, n − count)` over untested letters; one spelling per letter set; tie-break by entropy on top 40 vs 500-word sample. Pool ≤ 2 → just the pool.
  - Hard: viable answers only; entropy, 300 candidates × 400-word sample.
- **Possible words:** up to 500. Word color = log of absolute rank (yellow → red; unranked = red). Letter tint = green → blue by count in pool. Blue border = past answer.
- **Letters pane:** unique-letter counts in pool; hides excluded and green letters.
- **Pre-guess:** all panes filled; top 500 words act as the pool until a tile is marked.
- **Settings (footer):** compares `APP_VERSION` with `version.json`; Reload App / Clear Cache.

## Key technical decisions

- **Constraints:** `greenAt`, `notAt` (yellow + gray positions), `minCount`, `maxCount` (gray caps at the guess's green + yellow count; 0 = excluded). Handles duplicate letters.
- **State:** `guesses = [{word, tiles}]`; active row = `guesses.length`. `updateResults()` builds constraints once per tap and passes them down.
- **Word data:** tabatkins/wordle-list ranked by hermitdave `en_full`; 11,370 ranked (`RANKED_COUNT`), rest alphabetical. `WORD_RANK` Map for O(1) lookups.
- **Entropy:** `getPattern` uses typed arrays, base-3 code 0–242; `computeEntropy` uses a 243-slot `Int32Array`.
- **Storage:** `lsGet`/`lsSet` wrap all access in try/catch. Keys: `wordler_starters`, `wordler_starters_v15` (SLATE migration flag), `wordler_past_v2`.
- **Past answers:** Action fetches through yesterday ET only (no spoilers). App caches one day. NYT endpoint is unofficial — first suspect if past answers stop updating.
- **Performance (jsdom):** worst-case Easy tap ~200–350 ms including 500-chip render; was 1.3 s compute alone in v1.4.

## Version bump (all together)

1. `APP_VERSION` in `index.html`
1. `version.json`
1. `VERSION` in `sw.js`
1. `README.md` title + history; this file

## Deploy

1. GitHub Desktop → **Pull origin** (the Action commits to `main`).
1. Copy files in, including hidden `.github/`.
1. Commit `vX.Y — summary` → **Push origin**.
1. First deploy of v1.5 only: Actions → Update past Wordle answers → **Run workflow** (~15 min backfill). If push fails: Settings → Actions → General → Workflow permissions → Read and write.

Packaging: `wordler-vX.Y.zip` with all repo files.

## Version history

| Version | Changes |
|---|---|
| v1.0 | Initial release |
| v1.1 | PWA start_url/scope fix; Settings + update check |
| v1.2 | Common + Helpful panes; entropy engine; tap-to-fill; top 500 on load |
| v1.3 | Hard mode; Starters; Best Pair; 6 words per pane |
| v1.4 | Header version + EASY/HARD; merged Helpful; two-column suggestions |
| v1.5 | SLATE starter; undo; daily past answers Action; en_full corpus; absolute-rank colors; maskable icon; version.json; Easy letter-coverage scoring; fixes from adversarial review (freeze, list wipe, letters reset, update button, stale SW, duplicate letters, storage crash) |

## Open ideas

- Persist EASY/HARD and in-progress puzzle across app close.
- Warn when a typed guess isn't a valid word.
- Exclude yellow letters from the Letters pane (always at max count).
- Move storage keys to a `WDL_` prefix per repo convention (needs migration).
