# Claude Session Context — Wordler

> Paste as first message in a new chat to resume immediately.

---

## Who I Am
- **Name:** Grandmaster (Spencer Thompson)
- **GitHub account:** `spencer-thompson-2-vu`
- **Claude goes by:** Fez

---

## This Project

- **Name:** Wordler
- **Type:** Coding / PWA
- **Goal:** Wordle helper app — enter guesses, mark tile colors, filter remaining possible words
- **Status:** Active
- **Repo:** https://github.com/spencer-thompson-2-vu/wordler
- **Live URL:** https://spencer-thompson-2-vu.github.io/wordler/
- **Current version:** v1.4
- **Stack:** Single-file HTML, vanilla JS, localStorage, PWA (manifest + service worker), GitHub Pages

---

## File Structure

```
wordler/
├── index.html       ← Full app (~120KB self-contained, all CSS+JS inline)
├── manifest.json    ← PWA manifest (start_url: /wordler/, scope: /wordler/)
├── sw.js            ← Service worker, cache name: wordler-v1.4
├── icon-192.png     ← App icon
├── icon-512.png     ← App icon
├── README.md        ← Technical documentation
└── CONTEXT.md       ← This file
```

---

## Current Features

### Guess Grid
- 6-row × 5-col tile grid
- Type word in input → ADD (or Enter) → word fills next row
- Tap tile to cycle: empty → gray → yellow → green → empty
- Word list + all panes update instantly on each tap

### Suggestion Panes (2-column layout above word list)
**Left column (stacked):**
- **Starters** — 2 editable starter words (default: ARISE, COUNT), tap to fill guess box, ✎ pencil opens edit modal, persisted in localStorage as `wordler_starters`
- **Common** — top 6 frequency-ranked words from the filtered list

**Right column (full height):**
- **Helpful** — top 6 words by entropy score
  - **Easy mode**: candidates = full word list (any word that maximizes letter elimination, not required to be a viable answer)
  - **Hard mode**: candidates = filtered list only (must be a viable solution satisfying all constraints)
  - Sub-label updates: "any word · max info" vs "viable answers · max info"

### Mode Toggle (header)
- **EASY / HARD** pill toggle in header next to NEW PUZZLE
- EASY = green label active; HARD = yellow label active
- Affects Helpful pane candidate pool and filterWords behavior

### Word List Panel
- Shows top 500 words on load (before any guesses)
- After filtering: shows all matching words, capped at 500 display
- **Word chip color** (text + border): yellow→red gradient by frequency rank (most common = yellow)
- **Per-letter background tint**: green→blue by letter frequency in remaining pool (most common letter = green)
- Blue border = previously used NYT Wordle answer

### Letter Frequency Sidebar
- Counts each letter across remaining filtered words (unique per word)
- Sorted descending by count
- Bar color: green→blue matching word chip letter tints
- Confirmed green letters removed; excluded gray letters removed
- Populated on load from top 500 words

### Past Answers
- Fetched async on load from public GitHub source
- Cached in localStorage key `wordler_past_v1` with daily refresh (`wordler_past_date`)

### Settings Modal (footer ⚙ link)
- Shows installed vs latest version
- Check for Update button (fetches live index.html, compares APP_VERSION)
- Clear Cache & Refresh button (unregisters SW, clears all caches)

---

## Key Technical Decisions

### Version Bumping (always all 3 simultaneously)
1. `APP_VERSION` constant in `index.html`: `const APP_VERSION = 'v1.4';`
2. Footer in `index.html`: `WORDLER v1.4`
3. `VERSION` in `sw.js`: `const VERSION = 'v1.4';` (also updates CACHE name)
4. `# Wordler v1.4` in README.md title
5. `logo-version` span in header: `id="headerVersion"` — content set dynamically from APP_VERSION in init

### PWA
- `manifest.json` `start_url` and `scope` must be `/wordler/` (not `/`) — this was the v1.1 bug fix
- Service worker: cache-first for same-origin, network-only for external fetches
- Installed via Chrome → ⋮ → Add to Home Screen on Android

### Word List
- Source: tabatkins/wordle-list (~14,855 words)
- Frequency: combined google-10000-english + hermitdave/FrequencyWords en_50k
- Baked in as comma-separated string constant `WORD_LIST_RAW`, split at runtime
- ~28% of words have frequency data; rest ranked last

### Entropy Engine
- `getPattern(guess, answer)` — simulates color result as base-3 integer (0–242)
- `computeEntropy(guess, pool)` — Shannon entropy across 243 pattern buckets
- `topByEntropy(candidates, pool, n)` — returns top N highest-entropy words
- Easy mode candidate pool: WORDS.slice(0, 1000) — any word, maximize elimination
- Hard mode candidate pool: filtered — viable solutions only

### Filter Engine (`buildConstraints` + `filterWords`)
- Gray → excludeLetters (unless same letter also green/yellow in same guess)
- Yellow → includeLetters (must appear) + notAt[pos] (not at this position)
- Green → greenAt[pos] (exact match required)
- All constraints AND'd

### Color Gradients
- Word frequency: yellow `rgb(181,159,59)` → red `rgb(204,51,51)`, sqrt easing on position
- Letter tint: green `rgba(83,141,78,0.35)` → blue `rgba(58,123,213,0.35)`
- Letter panel bars: same green→blue, solid (no alpha)

### localStorage Keys
- `wordler_starters` — JSON array of 2 starter words
- `wordler_past_v1` — JSON array of past NYT Wordle answers
- `wordler_past_date` — ISO date string for daily cache invalidation

### GitHub Desktop Workflow
1. Pull origin before starting
2. Copy files into local repo folder
3. Commit with version message (e.g. `v1.4 — [changes]`)
4. Push origin

---

## Version History

| Version | Changes |
|---------|---------|
| v1.0 | Initial release — guess grid, word list with frequency gradient + letter tints, letter frequency sidebar, past answer highlighting, PWA |
| v1.1 | Fix PWA start_url/scope for GitHub Pages subdirectory install; Settings modal with update checker and cache clear |
| v1.2 | Common + Helpful suggestion panes; entropy-based best-guess engine; tap-to-fill chips; top 500 words on load |
| v1.3 | Hard mode toggle; Starters pane (editable, persisted); Best Pair pane; 6 words in Common+Helpful; all panes populated on load |
| v1.4 | Version in header; EASY/HARD mode toggle in header; consolidated Helpful pane (Easy=any word max info, Hard=viable only); Starters+Common left col, Helpful right col |

---

## Packaging Convention
- Zip name: `wordler-vX.Y.zip`
- Include all 7 repo files (including CONTEXT.md)

---

## Next Steps / Open Ideas
- Investigate past Wordle answers fetch reliability (current source sometimes 404s)
- Consider adding a "solved" indicator when filtered list reaches 1 word
