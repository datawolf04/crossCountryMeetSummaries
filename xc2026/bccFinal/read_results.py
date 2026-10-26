"""Fetch individual results from MileSplit into per-race DataFrames."""

import html
import re
from pathlib import Path

import pandas as pd
import requests

RESULTS_DIR = Path(__file__).resolve().parent
PAGE_URL = (
    "https://nc.milesplit.com/meets/"
    "790480-bcc-xc-6a-7a-conference-championships-2026/results"
)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
PRE_RE = re.compile(r"<pre>(?P<body>.*?)</pre>", re.DOTALL)
RACE_RE = re.compile(
    r"^\s*Varsity\s+(?P<gender>Boys|Girls)\s+(?P<distance>\d+)\s+Meter\s+Run\s*$"
)
TIME_RE = re.compile(r"^\d+:\d{2}\.\d{2}$")
COLUMNS = ["place", "athlete", "team", "mark", "time_seconds"]


def fetch_results_text():
    response = requests.get(PAGE_URL, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    match = PRE_RE.search(response.text)
    if match is None:
        raise ValueError("No results found on the MileSplit page")
    return html.unescape(match["body"])


def parse_line(line):
    if len(line) < 58:
        return None
    mark = line[50:58].strip()
    if not TIME_RE.match(mark):
        return None
    athlete = line[4:26].strip()
    team = line[29:50].strip()
    if not athlete or not team:
        return None
    minutes, seconds = mark.split(":")
    return {
        "place": int(line[0:4]),
        "athlete": athlete,
        "team": team,
        "mark": mark,
        "time_seconds": int(minutes) * 60 + float(seconds),
    }


def parse_races(text):
    races = {}
    current = None
    for line in text.splitlines():
        race = RACE_RE.match(line)
        if race:
            current = f"{race['gender'].lower()}{int(race['distance'])}"
            races.setdefault(current, [])
            continue
        if not line.strip():
            current = None
            continue
        if current is None:
            continue
        record = parse_line(line)
        if record is not None:
            races[current].append(record)
    return races


def load_races():
    frames = {}
    for name, records in sorted(parse_races(fetch_results_text()).items()):
        frames[name] = (
            pd.DataFrame(records, columns=COLUMNS)
            .astype({"place": int})
            .sort_values("place")
        )
    return frames


def write_excel(races=None, path=RESULTS_DIR / "bccFinal.xlsx"):
    if races is None:
        races = load_races()
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in races.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return Path(path)


if __name__ == "__main__":
    races = load_races()
    globals().update(races)
    for name, df in races.items():
        print(f"{name}: {len(df)} finishers")
        print(df.head(), "\n")
    print(f"\nWrote {write_excel(races)}")
