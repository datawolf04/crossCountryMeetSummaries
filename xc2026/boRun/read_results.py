"""Read cross country meet results from a single multi-race *.txt file into per-race DataFrames."""

import re
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
GRADES = {"FR", "SO", "JR", "SR"}
TEAMS = [
    "Arendell Parrott Academy",
    "Christ Covenant MS",
    "Christ Covenant",
    "D.H. Conley",
    "J.H. Rose",
    "Northside - Pinetown",
    "Pamlico County",
    "Pope John Paul II",
    "South Central",
    "South Lenoir",
    "Terra Ceia Christian",
    "West Carteret",
    "Western Harnett",
    "A G Cox MS",
    "Bath MS",
    "Hobgood MS",
    "Oakwood MS",
    "Unattached",
    "Riptides",
    "Oakwood",
]
RACES = {
    "Girls Championship": "girlsVarsity",
    "Boys Championship": "boysVarsity",
    "Boys JV": "boysJV",
    "Girls JV": "girlsJV",
}
RACE_TITLE_RE = re.compile(r"^(?P<race>[A-Za-z]+(?:\s+[A-Za-z]+)*)\s+\d+\s+(?:Meter|Meters)\s*$")
SEPARATOR_RE = re.compile(r"^[-=]+$")
TIME_RE = re.compile(
    r"^(?P<place>\d+)\s+(?P<field>.+?)\s+(?P<mark>\d+:\d+\.\d+)\s*(?P<points>\d+)?\s*$"
)


def split_name_grade_team(field):
    tokens = field.split()
    for i, token in enumerate(tokens):
        if token in GRADES or token.isdigit():
            return " ".join(tokens[:i]), token, " ".join(tokens[i + 1 :])
    for team in sorted(TEAMS, key=len, reverse=True):
        team_tokens = team.split()
        if tokens[-len(team_tokens):] == team_tokens:
            return " ".join(tokens[:-len(team_tokens)]), None, team
    return field, None, None


def parse_line(line):
    match = TIME_RE.match(line.strip())
    if not match:
        return None
    athlete, grade, team = split_name_grade_team(match["field"])
    minutes, seconds = match["mark"].split(":")
    return {
        "place": int(match["place"]),
        "athlete": athlete,
        "grade": grade,
        "team": team,
        "mark": match["mark"],
        "time_seconds": int(minutes) * 60 + float(seconds),
        "points": pd.NA if match["points"] is None else int(match["points"]),
    }


def parse_lines(lines, label):
    rows = []
    for line_no, line in enumerate(lines, start=1):
        if not line.strip() or SEPARATOR_RE.match(line.strip()) or line.strip().startswith("Athlete"):
            continue
        row = parse_line(line)
        if row is None:
            print(f"{label}:{line_no}: skipped: {line.rstrip()}")
            continue
        rows.append(row)
    df = pd.DataFrame(rows)
    return df.astype({"place": int, "points": "Int64"})[
        ["place", "athlete", "grade", "team", "mark", "time_seconds", "points"]
    ]


def parse_file(path=RESULTS_DIR / "boRunRaw.txt"):
    races = {}
    race = None
    with open(path) as f:
        for line in f:
            title = RACE_TITLE_RE.match(line.strip())
            if title:
                race = " ".join(title["race"].split())
                continue
            if race is not None:
                races.setdefault(race, []).append(line)
    for race in [r for r in races if r not in RACES]:
        print(f"skipped race not in RACES: {race}")
    return {RACES[race]: parse_lines(lines, race) for race, lines in races.items() if race in RACES}


def load_races(path=RESULTS_DIR / "boRunRaw.txt"):
    return parse_file(path)


def write_excel(races=None, path=RESULTS_DIR / "boRun2026.xlsx"):
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
