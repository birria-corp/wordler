"""Update past-answers.json with past NYT Wordle solutions.

Fetches every puzzle date from the first Wordle (2021-06-19) through yesterday
(US Eastern time) that isn't already in the file. Today's answer is never
fetched, so the app can't spoil the current puzzle.

Source: https://www.nytimes.com/svc/wordle/v2/YYYY-MM-DD.json (unofficial
endpoint used by the NYT web app). Standard library only.
"""

import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

FIRST_PUZZLE = date(2021, 6, 19)
URL = "https://www.nytimes.com/svc/wordle/v2/{}.json"
OUT = Path(__file__).resolve().parent.parent / "past-answers.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (wordler past-answers updater)"}
MAX_CONSECUTIVE_ERRORS = 5
DELAY_SECONDS = 0.25


def load() -> dict:
    if OUT.exists():
        try:
            data = json.loads(OUT.read_text())
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    data.setdefault("dates", {})
    return data


def fetch(day: date) -> str | None:
    req = urllib.request.Request(URL.format(day.isoformat()), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        solution = json.load(resp).get("solution", "")
    solution = solution.strip().upper()
    return solution if len(solution) == 5 and solution.isalpha() else None


def main() -> int:
    data = load()
    yesterday = datetime.now(ZoneInfo("America/New_York")).date() - timedelta(days=1)
    added, errors = 0, 0
    day = FIRST_PUZZLE
    while day <= yesterday:
        key = day.isoformat()
        if key not in data["dates"]:
            try:
                word = fetch(day)
                if word:
                    data["dates"][key] = word
                    added += 1
                errors = 0
            except urllib.error.HTTPError as e:
                print(f"{key}: HTTP {e.code}")
                errors = 0 if e.code == 404 else errors + 1
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                print(f"{key}: {e}")
                errors += 1
            if errors >= MAX_CONSECUTIVE_ERRORS:
                print("Too many consecutive errors; saving progress and stopping.")
                break
            time.sleep(DELAY_SECONDS)
        day += timedelta(days=1)

    data["dates"] = dict(sorted(data["dates"].items()))
    data["updated"] = yesterday.isoformat()
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"Added {added}; total {len(data['dates'])}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
