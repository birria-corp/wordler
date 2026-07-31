# Wordler v1.0

A Wordle helper PWA — enter your guesses, mark tile colors, and instantly filter the remaining possible words. Ranked by English word frequency so the most likely answers appear first.

---

## How to Use

1. **Type your guess** in the input box and tap **ADD** (or press Enter)
2. The word appears in the 6-row guess grid
3. **Tap each letter tile** to cycle its color:
   - ⬜ Empty → ⬛ **Gray** (letter not in word)
   - ⬛ Gray → 🟨 **Yellow** (letter in word, wrong position)
   - 🟨 Yellow → 🟩 **Green** (correct letter, correct position)
   - 🟩 Green → ⬜ Empty (reset)
4. The word list and letter frequency panel update **instantly** after each tap
5. Tap **NEW PUZZLE** to reset everything

---

## Features

### Word List Panel
- Shows all remaining possible words after applying your constraints
- Words ranked **most common → least common** (Google corpus + spoken frequency data)
- Color gradient: **Yellow** = most common English words, **Red** = least common
- Each letter within a word has a **heatmap tint**: **Green** = that letter appears frequently across remaining words, **Blue** = appears infrequently — helps you spot which letters are most useful to play next
- **Blue border** on a word = previously used as an official NYT Wordle answer (fetched daily)
- Displays up to 500 words; shows count of additional words if more remain

### Letter Frequency Panel (right sidebar)
- Lists every letter that still appears in the remaining word pool, sorted by count descending
- Bar color matches the green→blue gradient in the word chips — consistent visual language
- Confirmed green letters are removed (already known); excluded gray letters are removed
- Use this to decide your next guess: play words that contain the top-listed letters

### Filter Engine
- **Gray tiles**: removes any word containing that letter (unless the same letter is also marked yellow/green elsewhere in the same guess — handles duplicate letter edge cases correctly)
- **Yellow tiles**: word must contain that letter, and it cannot appear at that position
- **Green tiles**: word must have that exact letter at that exact position
- All constraints are AND'd together across all guesses

### Past Answers
- On load, fetches the list of previously used NYT Wordle answers from a public source
- Cached in `localStorage` with a daily refresh — works offline after first load
- Words that have already been used as answers are highlighted with a blue border (still shown as valid guesses, just flagged)

---

## Technical Architecture

### Stack
| Layer | Choice | Reason |
|---|---|---|
| UI | Vanilla HTML/CSS/JS | Zero build step, single file, fast on mobile |
| Hosting | GitHub Pages | Free, HTTPS, auto-deploy on push |
| Installability | PWA (manifest + service worker) | Chrome "Add to Home Screen" on Android |
| Offline | Service worker cache-first | Works without network after first load |
| Data | Baked-in JS string | No fetch required for word list, instant startup |

### File Structure
```
wordler/
├── index.html       ← Full app (~111KB, self-contained)
├── manifest.json    ← PWA manifest (name, icons, display mode)
├── sw.js            ← Service worker (cache-first, versioned cache)
├── icon-192.png     ← App icon (192×192)
├── icon-512.png     ← App icon (512×512)
└── README.md        ← This file
```

### Word List
- **Source**: [tabatkins/wordle-list](https://github.com/tabatkins/wordle-list) — official Wordle answers + valid guesses (~14,855 words)
- **Frequency ranking**: Combined from two sources:
  - [first20hours/google-10000-english](https://github.com/first20hours/google-10000-english) — Google Books n-gram corpus
  - [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords) — spoken language frequency (en_50k)
  - Words ranked by average of both sources; words appearing in neither ranked last
- **Format**: Single comma-separated string constant `WORD_LIST_RAW`, split at runtime — no JSON parse overhead, compresses well (53% gzip ratio)

### JavaScript Functions
| Function | Purpose |
|---|---|
| `buildGrid()` | Creates 6×5 tile DOM grid |
| `updateGridDisplay()` | Syncs tile classes/text to state |
| `onTileClick(e)` | Cycles tile color on tap |
| `submitGuess()` | Validates and adds a guess row |
| `buildConstraints()` | Derives gray/yellow/green constraint sets from all guesses |
| `filterWords()` | Applies constraints to WORDS array, returns filtered list |
| `computeLetterCounts(filtered)` | Counts unique letter occurrences across filtered words |
| `wordFreqColor(t)` | Returns RGB color on yellow→red gradient (t=0 most common) |
| `letterFreqColor(t)` | Returns RGBA color on green→blue gradient (t=0 most frequent) |
| `renderWordList()` | Renders word chips with frequency gradient and letter tints |
| `renderLetterFreq()` | Renders letter frequency sidebar bars |
| `fetchPastAnswers()` | Async: fetches NYT answer list, caches in localStorage |
| `resetAll()` | Clears all state for a new puzzle |
| `showToast(msg)` | Displays a timed notification banner |

### State Model
```js
guesses = [
  { word: "CRANE", tiles: ["gray", "yellow", "green", "empty", "empty"] },
  ...
]
activeRow = 1  // next row to fill
```
Tile states: `"empty"` | `"gray"` | `"yellow"` | `"green"`

### Color System
```
Word frequency gradient (chip text/border):
  t=0 (most common) → rgb(181, 159, 59)  // yellow
  t=1 (least common) → rgb(204, 51, 51)  // red

Letter frequency tint (per-letter background in chip):
  t=0 (most frequent letter) → rgba(83, 141, 78, 0.35)   // green
  t=1 (least frequent letter) → rgba(58, 123, 213, 0.35) // blue

Letter panel bars: same green→blue, solid (no alpha)
```

### Service Worker
- Cache name: `wordler-v1.0` — update this string on each release to force cache refresh
- Strategy: cache-first for same-origin assets, network-only for external fetches (past answers API)
- On activate: purges all caches not matching current version name

### PWA Manifest
- `display: standalone` — full-screen, no browser chrome
- `orientation: portrait` — locked portrait on Android
- `theme_color: #121213` — matches app background (affects Android status bar)

---

## Deploy to GitHub Pages

```
1. Create repo at github.com (public, no auto-init)
2. Clone in GitHub Desktop
3. Copy all 6 files into the cloned folder
4. Commit: "Initial deploy v1.0"
5. Push to main
6. Settings → Pages → Source: main / (root) → Save
7. Live at: https://yourusername.github.io/wordler/
```

**Install on Android:**
Open the URL in Chrome → tap ⋮ menu → **Add to Home screen** → Add

---

## Versioning

| Version | Description |
|---|---|
| v1.0 | Initial release — guess grid, word list with frequency gradient + letter tints, letter frequency sidebar, past answer highlighting, PWA |
| v1.1 | Fix PWA start_url/scope for GitHub Pages subdirectory install; add Settings modal with update checker and cache clear |

**Version is tracked in three places — update all three on each release:**
1. `<footer>` in `index.html`: `WORDLER v1.1`
2. `APP_VERSION` constant in JS: `const APP_VERSION = 'v1.1';`
3. Service worker cache name in `sw.js`: `const VERSION = 'v1.1';`

Download zip naming convention: `wordler-vX.Y.zip`

---

## Known Limitations

- Past answers list depends on a public GitHub source being available; falls back gracefully to no highlighting if offline or source unavailable
- Word frequency data covers ~28% of the 14k word list; remaining words are ranked last (shown in red)
- Maximum 500 words displayed at once — add more guess constraints to narrow down further
