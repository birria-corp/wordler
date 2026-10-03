# Wordler v1.6

A Wordle helper PWA. Enter your guesses, mark tile colors, and filter the remaining possible words, ranked by how common they are in English.

**Live:** https://spencer-thompson-2-vu.github.io/wordler/

## Features

### Guess grid

1. Type a guess and tap **ADD** (or press Enter). The word fills the next row.
1. Tap a tile to cycle its color: empty → gray → yellow → green → empty.
1. Tap **↶** to remove the last row. Its word returns to the input so you can fix a typo.
1. Tap **NEW PUZZLE** to clear the board.

Every pane updates as soon as you tap a tile.

### Mode toggle

The **EASY / HARD** toggle in the header (also in Settings) changes only the **Helpful** pane. Your choice is saved.

- **Easy:** Helpful suggests any valid word that confirms or eliminates the most letters still in play. The suggestion doesn't need to be a possible answer.
- **Hard:** Helpful suggests only words that are still possible answers, ranked by information gained.

### Suggestion panes

| Pane | Contents |
|---|---|
| Starters | Up to three saved opening words (default ARISE, COUNT, SLATE). Tap **✎** to edit. |
| Common | The six most common words in the remaining pool. |
| Helpful | Six best next guesses for the current mode. |

Tap any suggestion to put it in the guess input. All panes are filled before your first guess; the top 500 words stand in for the answer pool until you mark a tile.

### Possible words

- Shows up to 500 matching words, most common first.
- **Word color:** yellow (common) to red (rare), on a log scale of the word's absolute frequency rank. Words with no frequency data are red.
- **Letter tint:** green (letter appears in many remaining words) to blue (few).
- **Blue border:** the word was a past Wordle answer. NYT now repeats some answers, so a blue border doesn't rule a word out.

### Letters pane

Counts how many remaining words contain each letter, sorted high to low. Excluded letters and confirmed green letters are hidden.

## How it works

### Filter engine

`buildConstraints()` turns marked tiles into four rule sets:

| Rule | Source |
|---|---|
| `greenAt[pos]` | Green tile: letter must be at that position. |
| `notAt[pos]` | Yellow or gray tile: letter can't be at that position. |
| `minCount[letter]` | Green + yellow tiles of a letter in one guess. |
| `maxCount[letter]` | Gray tile caps the letter at its green + yellow count in that guess; 0 excludes it. |

This handles duplicate letters. For example, guessing BOBBY with one yellow, one green, and one gray B means the answer has exactly two Bs.

### Helpful scoring

- **Easy:** Each untested letter is worth `min(count, poolSize − count)`. A letter that splits the pool in half is worth the most; a letter in nearly every word, or almost none, is worth little. All 14,855 words are scored, one spelling per letter set, and ties go to the word with higher entropy.
- **Hard:** Shannon entropy across the 243 possible color patterns, using up to 300 candidates against a 400-word sample of the pool. This is the same idea NYT WordleBot uses.

### Word list and ranking

- **Words:** [tabatkins/wordle-list](https://github.com/tabatkins/wordle-list), 14,855 valid guesses.
- **Ranking:** [hermitdave/FrequencyWords](https://github.com/hermitdave/FrequencyWords) `en_full` (2018 subtitle corpus). 11,370 words (77%) have frequency data; the rest sort alphabetically after them.
- Stored inline as the `WORD_LIST_RAW` string in `index.html`. `RANKED_COUNT` marks where ranked words end.

### Past answers

A GitHub Action (`.github/workflows/past-answers.yml`) runs daily at 09:30 UTC. It calls `scripts/update_past_answers.py`, which fetches each missing date from NYT's daily puzzle endpoint through yesterday (US Eastern time) and commits `past-answers.json`. Today's answer is never fetched, so the app can't spoil it.

The app loads `past-answers.json` from the same origin and caches it in `localStorage` for one day.

**First-time setup:** in the repo, open **Actions → Update past Wordle answers → Run workflow**. The first run backfills about 1,900 dates and takes roughly 15 minutes. If the push step fails with a permissions error, open **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**.

> Note: The Action commits to `main`. Always **Pull origin** in GitHub Desktop before you push.

### Service worker

| Request | Strategy |
|---|---|
| `index.html`, page navigations, `version.json`, `past-answers.json` | Network first, cache fallback. New deploys show on the next launch. |
| Icons, manifest | Cache first. |

Cache keys ignore query strings. The cache name is `wordler-<VERSION>`; activating a new version deletes old caches.

### Settings

Tap **⚙** in the header (or **⚙ Settings** in the footer). Settings are saved on the device.

| Setting | Options | Default | Effect |
|---|---|---|---|
| Mode | Easy, Hard | Easy | Same as the header toggle. |
| Valid words only | On, Off | On | Rejects guesses that aren't in the word list, to catch typos. |
| Remember puzzle | On, Off | On | Restores today's guesses if the app closes. Clears automatically on a new day. |
| Edit Starters | — | — | Opens the starter editor. |
| Past answers | Mark, Hide, Off | Mark | Mark adds a blue border. Hide removes past answers from Possible words, Common, and Helpful (Hard). Off ignores the list. |
| Refresh | — | — | Re-downloads `past-answers.json` and shows the count and date. |
| Text size | S, M, L | M | Scales the app with `%` on the root font size (90%, 100%, 112%). |
| Words in list | 100, 250, 500 | 500 | Caps Possible words; fewer renders faster. |
| Check for Update | — | — | Compares the installed version with `version.json`, then offers Reload App. |
| Clear Cache | — | — | Unregisters the service worker, deletes caches, and reloads. |
| Reset Settings | — | — | Restores the defaults above. Doesn't touch starters. |

### Storage keys

| Key | Contents |
|---|---|
| `wordler_starters` | JSON array of up to three starter words. |
| `wordler_starters_v15` | One-time flag: SLATE was appended to an older two-word list. |
| `wordler_past_v2` | `{ fetched, updated, words }` cached past answers. |
| `wordler_settings` | Settings object. Unknown or invalid values fall back to defaults. |
| `wordler_puzzle` | `{ date, guesses }` for today's puzzle (local date). |

All reads go through `lsGet()`, which returns a default instead of throwing on bad data.

## File structure

```
wordler/
├── index.html                       Full app; all CSS and JS inline
├── manifest.json                    PWA manifest; start_url and scope are /wordler/
├── sw.js                            Service worker
├── version.json                     {"version": "X.X"}; read by the update checker
├── past-answers.json                Past answers by date; written by the Action
├── icon-192.png                     App icon
├── icon-512.png                     App icon
├── icon-maskable-512.png            Android adaptive icon (art inside the safe zone)
├── scripts/update_past_answers.py   Past-answers fetcher
├── .github/workflows/past-answers.yml
├── README.md
└── CONTEXT.md                       Session context for resuming work in Claude
```

## Update workflow

1. In GitHub Desktop, **Pull origin**.
1. Copy the new files into the local repo folder, including the hidden `.github` folder.
1. Commit with a message such as `v1.5 — <summary>`.
1. **Push origin**. GitHub Pages updates in about a minute.

### Version bump

Update all of these together:

1. `APP_VERSION` in `index.html` (header and footer read it at load).
1. `version.json`.
1. `VERSION` in `sw.js`.
1. The title and version history in `README.md`, and `CONTEXT.md`.

Zip name: `wordler-vX.Y.zip`.

### If an update doesn't appear

1. Open **⚙ → Check for Update → Reload App**.
1. Or swipe the app closed and reopen it. From v1.4 or older, reopen twice.
1. Or open the live URL in a Chrome tab and pull to refresh.

## Install on Android

1. Open the live URL in Chrome.
1. Tap **⋮ → Add to Home screen → Add**.

## Version history

| Version | Changes |
|---|---|
| v1.0 | Initial release: guess grid, word list with frequency gradient and letter tints, letters pane, PWA. |
| v1.1 | Fixed PWA `start_url` and `scope` for the GitHub Pages subdirectory. Added Settings with update check and cache clear. |
| v1.2 | Added Common and Helpful panes, entropy engine, tap-to-fill chips, top 500 on load. |
| v1.3 | Added hard mode, editable Starters, Best Pair, six words per pane. |
| v1.4 | Moved version and EASY/HARD toggle to header. Merged Best Pair into Helpful. Starters and Common on the left, Helpful on the right. |
| v1.5 | Added SLATE as a third starter, undo, daily past answers via GitHub Action, larger frequency corpus (28% → 77%), absolute-rank colors, maskable icon, `version.json`. Easy Helpful now scores letters confirmed or eliminated across all words. Fixed phone freezes, the top-500 list being wiped, the Letters pane blanking on reset, the stuck update button, stale deploys, duplicate-letter filtering, and crashes from corrupted storage. |
| v1.6 | Added a header ⚙ button and a Settings panel: mode, valid words only, remember puzzle, past answers (mark, hide, off) with refresh, text size, list size, update check, clear cache, reset settings. Mode and puzzle now persist. Fixed the near-invisible footer link and the ADD button clipping at phone width. |

## Known limitations

- The NYT puzzle endpoint is unofficial and could change. If it does, the Action logs errors and the app keeps the last good list.
- Frequency data comes from film subtitles, so conversational words (GONNA, WANNA) rank high.
- 23% of words have no frequency data and sort alphabetically at the end.
