"""Read cross country meet results from *.txt files into per-race DataFrames."""

import re
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
GRADES = {"FR", "SO", "JR", "SR"}
TEAMS = ["New Bern", "J. H. Rose", "White Oak", "D. H. Conley", "Jacksonville", "South Central"]
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


def parse_file(path):
    rows = []
    with open(path) as f:
        next(f)
        for line_no, line in enumerate(f, start=2):
            row = parse_line(line)
            if row is None:
                if line.strip():
                    print(f"{path.name}:{line_no}: skipped: {line.rstrip()}")
                continue
            rows.append(row)
    df = pd.DataFrame(rows)
    return df.astype({"place": int, "points": "Int64"})[
        ["place", "athlete", "grade", "team", "mark", "time_seconds", "points"]
    ]


def load_races(directory=RESULTS_DIR):
    files = sorted(Path(directory).glob("*.txt"))
    races = {}
    for path in files:
        races[path.stem] = parse_file(path)
    return races


def write_excel(races=None, path=RESULTS_DIR / "bccJamboree0909.xlsx"):
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
