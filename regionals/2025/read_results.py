import os
import re

import pandas as pd

YEARS = {"FR", "SO", "JR", "SR"}
MARK_RE = re.compile(r"^\d{1,2}:\d{2}(\.\d+)?$")
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(DATA_DIR, "regionals2025.xlsx")


def _parse_line(line):
    tokens = line.split()
    if len(tokens) < 5:
        return None
    mark_idx = next(i for i, t in enumerate(tokens) if MARK_RE.match(t))
    return {
        "place": int(tokens[0]),
        "mark_idx": mark_idx,
        "name_tokens": tokens[1:mark_idx],
        "mark": tokens[mark_idx],
        "points": int(tokens[mark_idx + 1]) if mark_idx + 1 < len(tokens) else None,
    }


def read_results(filepath):
    rows = []
    known_teams = set()
    parsed = []
    with open(filepath) as f:
        for line in f:
            if line.split()[0] == "PLACE":
                continue
            row = _parse_line(line)
            if row is None:
                continue
            parsed.append(row)
            if any(t in YEARS for t in row["name_tokens"]):
                year_idx = next(
                    i for i, t in enumerate(row["name_tokens"]) if t in YEARS
                )
                known_teams.add(" ".join(row["name_tokens"][year_idx + 1 :]))
    for row in parsed:
        name_tokens = row["name_tokens"]
        if any(t in YEARS for t in name_tokens):
            year_idx = next(i for i, t in enumerate(name_tokens) if t in YEARS)
            year = name_tokens[year_idx]
            athlete = " ".join(name_tokens[:year_idx])
            team = " ".join(name_tokens[year_idx + 1 :])
        else:
            team = next(
                (
                    " ".join(name_tokens[i:])
                    for i in range(len(name_tokens))
                    if " ".join(name_tokens[i:]) in known_teams
                ),
                "",
            )
            athlete = " ".join(name_tokens[: len(name_tokens) - len(team.split())])
            year = ""
        rows.append(
            {
                "PLACE": row["place"],
                "ATHLETE": athlete,
                "YEAR": year,
                "TEAM": team,
                "MARK": row["mark"],
                "POINTS": row["points"],
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    sheets = {}
    for name in sorted(os.listdir(DATA_DIR)):
        if name.endswith(".txt"):
            stem = os.path.splitext(name)[0]
            sheets[stem] = read_results(os.path.join(DATA_DIR, name))
    with pd.ExcelWriter(OUTPUT) as writer:
        for stem, df in sheets.items():
            df.to_excel(writer, sheet_name=stem, index=False)
    print(f"Wrote {list(sheets)} to {OUTPUT}")