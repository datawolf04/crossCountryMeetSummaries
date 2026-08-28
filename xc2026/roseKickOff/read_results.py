"""Read cross country meet results from *.txt files into per-race DataFrames."""

import re
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
PLACE_RE = re.compile(r"^\s*(?P<place>\d+)\s*\.\s*(?P<rest>.+)$")
TIME_RE = re.compile(r"(?P<time>\d{1,2}[:;.]\d{2}(?:\.\d+)?)\s*$")
INITIALS_RE = re.compile(r"^(?:[A-Za-z]\.)+$")
DOTTED_NAME_RE = re.compile(r"^[A-Za-z]\.[A-Za-z-]+$")
COLUMNS = ["Place", "Athlete", "Team", "Mark", "Time"]


def to_mark_and_time(mark):
    mark = re.sub(r"^(\d+)[;.]", r"\1:", mark.strip())
    minutes, seconds = mark.split(":")
    return mark, int(minutes) * 60 + float(seconds)


def split_name_school(tokens):
    if tokens[0] == "?" or INITIALS_RE.match(tokens[0]):
        return " ".join(tokens[:2]), " ".join(tokens[2:])
    if DOTTED_NAME_RE.match(tokens[0]):
        return tokens[0], " ".join(tokens[1:])
    return tokens[0], " ".join(tokens[1:])


def split_school_name(tokens):
    for i, token in enumerate(tokens):
        if token == "?" or INITIALS_RE.match(token):
            return " ".join(tokens[i:]), " ".join(tokens[:i])
    return tokens[-1], " ".join(tokens[:-1])


def parse_placed_line(line):
    match = PLACE_RE.match(line.strip())
    if not match:
        return None
    time_match = TIME_RE.search(match["rest"])
    if not time_match:
        return None
    name, school = split_name_school(match["rest"][: time_match.start()].split())
    return place_record(int(match["place"]), name, school, time_match["time"])


def parse_unplaced_line(line, place):
    time_match = TIME_RE.search(line.strip())
    if not time_match:
        return None
    name, school = split_school_name(line[: time_match.start()].split())
    return place_record(place, name, school, time_match["time"])


def place_record(place, name, school, mark):
    mark, time_seconds = to_mark_and_time(mark)
    return place, name, school, mark, time_seconds


def parse_file(path):
    rows = []
    with open(path) as f:
        lines = f.readlines()
    placed = lines[0].split()[0].lower() == "place"
    seq = 0
    for line_no, line in enumerate(lines[1:], start=2):
        row = parse_placed_line(line) if placed else parse_unplaced_line(line, seq + 1)
        if row is None:
            if line.strip():
                print(f"{path.name}:{line_no}: skipped: {line.rstrip()}")
            continue
        if not placed:
            seq += 1
        rows.append(row)
    return pd.DataFrame(rows, columns=COLUMNS).astype({"Place": int})


def load_races(directory=RESULTS_DIR):
    files = sorted(Path(directory).glob("*.txt"))
    races = {}
    for path in files:
        races[path.stem] = parse_file(path)
    return races


def write_excel(races=None, path=RESULTS_DIR / "roseKickoff26.xlsx"):
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
