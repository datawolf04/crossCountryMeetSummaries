"""Read cross country meet results from *.txt files into per-race DataFrames."""

import re
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
TEAMS = [
    "Christ Covenant School",
    "Terra Ceia Christian School",
    "Martin County High School",
    "Rolesville High School",
    "Faith Christian School",
    "Pitt County Pacers",
    "Northside (1A)",
    "Camden County",
    "D.H. Conley",
    "Hunt High School",
    "North Pitt",
    "South Johnston",
    "South Lenoir",
    "South Central",
    "Croatan",
    "Havelock",
    "Northwood",
    "Wakefield",
]
RACES = {
    "boysChamp.txt": "boysVarsity",
    "girlsChamp.txt": "girlsVarsity",
}
COLUMNS = ["place", "athlete", "team", "mark", "time_seconds"]
TIME_RE = re.compile(r"^(?P<place>\d+)\s+(?P<field>.+?)\s+(?P<mark>\d+:\d+(?:\.\d+)?)\s*$")


def split_name_team(field):
    tokens = field.split()
    for team in sorted(TEAMS, key=len, reverse=True):
        team_tokens = team.split()
        if tokens[-len(team_tokens) :] == team_tokens:
            return " ".join(tokens[: -len(team_tokens)]), team
    return field, None


def parse_line(line):
    match = TIME_RE.match(line.strip())
    if not match:
        return None
    athlete, team = split_name_team(match["field"])
    minutes, seconds = match["mark"].split(":")
    return {
        "place": int(match["place"]),
        "athlete": athlete,
        "team": team,
        "mark": match["mark"],
        "time_seconds": int(minutes) * 60 + float(seconds),
    }


def parse_file(path):
    rows = []
    with open(path) as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip() or line.strip().startswith("Place"):
                continue
            row = parse_line(line)
            if row is None:
                print(f"{path.name}:{line_no}: skipped: {line.rstrip()}")
                continue
            rows.append(row)
    return pd.DataFrame(rows, columns=COLUMNS).astype({"place": int})[COLUMNS]


def load_races():
    races = {}
    for filename, sheet in RACES.items():
        df = parse_file(RESULTS_DIR / filename)
        if df["team"].isna().any():
            unmatched = df.loc[df["team"].isna(), "athlete"].tolist()
            print(f"{filename}: unmatched team for: {unmatched}")
        races[sheet] = df
    return races


def write_excel(races=None, path=RESULTS_DIR / "pirateInvite2026.xlsx"):
    if races is None:
        races = load_races()
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, df in races.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return Path(path)


globals().update(load_races())

if __name__ == "__main__":
    for name, df in load_races().items():
        print(f"{name}: {len(df)} finishers")
        print(df.head(), "\n")
    print(f"\nWrote {write_excel()}")
