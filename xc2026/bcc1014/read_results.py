"""Fetch individual results from MileSplit into per-race DataFrames."""

import re
from pathlib import Path

import pandas as pd
import requests

RESULTS_DIR = Path(__file__).resolve().parent
MEET_ID = "790989"
RESULTS_ID = "1332988"
PAGE_URL = f"https://nc.milesplit.com/meets/{MEET_ID}-bcc-1014-2026/results/{RESULTS_ID}/formatted"
API_URL = f"https://nc.milesplit.com/api/v1/meets/{MEET_ID}/performances"
FIELDS = ",".join(
    [
        "teamName",
        "firstName",
        "lastName",
        "gender",
        "eventDistance",
        "mark",
        "place",
        "statusCode",
    ]
)
COLUMNS = ["place", "athlete", "team", "mark", "time_seconds"]
APP_TOKEN_RE = re.compile(r"appHash: '(?P<token>[0-9a-f]+)'")
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def fetch_rows():
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    page = session.get(PAGE_URL)
    page.raise_for_status()
    token = APP_TOKEN_RE.search(page.text)["token"]
    response = session.get(
        API_URL,
        headers={
            "appName": "MileSplit",
            "appToken": token,
            "userId": "",
            "userToken": "",
        },
        params={
            "isMeetPro": 0,
            "resultsId": RESULTS_ID,
            "fields": FIELDS,
        },
    )
    response.raise_for_status()
    return response.json()["data"]


def mark_to_seconds(mark):
    minutes, seconds = mark.split(":")
    return int(minutes) * 60 + float(seconds)


def normalize_mark(mark):
    parts = mark.split(":")
    if len(parts) == 3:
        minutes, seconds, hundredths = parts[0], int(parts[1]), round(float(parts[2]))
    elif len(parts) == 2:
        minutes = parts[0]
        total = float(parts[1])
        seconds = int(total)
        hundredths = round((total - seconds) * 100)
    else:
        return mark
    return f"{minutes}:{seconds:02d}.{hundredths:02d}"


def sheet_name(row):
    gender = "boys" if row["gender"] == "M" else "girls"
    distance = int(float(row.get("eventDistance") or 0))
    return f"{gender}{distance}"


def row_to_record(row):
    mark = normalize_mark(row.get("statusCode") or row["mark"])
    return {
        "place": int(row["place"]),
        "athlete": f"{row['firstName']} {row['lastName']}".strip(),
        "team": row["teamName"],
        "mark": mark,
        "time_seconds": mark_to_seconds(mark),
    }


def load_races():
    races = {}
    for row in fetch_rows():
        if row["mark"] == "0.00" and not row.get("statusCode"):
            continue
        races.setdefault(sheet_name(row), []).append(row_to_record(row))
    frames = {}
    for name, records in sorted(races.items()):
        frames[name] = pd.DataFrame(records, columns=COLUMNS).sort_values("place")
    return frames


def write_excel(races=None, path=RESULTS_DIR / "bcc1014.xlsx"):
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
