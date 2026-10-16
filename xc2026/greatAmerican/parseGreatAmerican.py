"""Parse Great American XC Festival 2026 results CSV into per-race Excel sheets.

Reads great_american_2026_results.csv and writes greatAmerican2026.xlsx
with one sheet per race. Sheet names follow conventions like girlsBlue, boysJV.
"""

import re
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
CSV_FILE = RESULTS_DIR / "great_american_2026_results.csv"
OUTPUT_FILE = RESULTS_DIR / "greatAmerican2026.xlsx"

# Map division names to short sheet suffixes
DIVISION_MAP = {
    "Varsity Championship": "Champ",
    "Varsity Blue": "Blue",
    "Varsity Red": "Red",
    "Varsity White": "White",
    "Varsity Red/White": "RedWhite",
    "Junior Varsity I": "JVI",
    "Junior Varsity II": "JVII",
    "Middle School": "MS",
}


def sheet_name(sex, division):
    """Generate sheet name like boysVarsity, girlsBlue, boysJVII, boysMS."""
    gender = "boys" if str(sex).lower().startswith("b") else "girls"
    suffix = DIVISION_MAP.get(division, re.sub(r"[^A-Za-z0-9]", "", str(division)))
    # For JV I/II, also allow shorter forms if desired - but be explicit
    if division == "Junior Varsity I":
        return f"{gender}JV"
    if division == "Junior Varsity II":
        return f"{gender}JVII"
    if "Varsity" in division and division != "Varsity Championship":
        # e.g., Varsity Blue -> girlsBlue/boysBlue
        color = division.replace("Varsity", "").strip()
        color_clean = re.sub(r"[^A-Za-z0-9]", "", color)
        return f"{gender}{color_clean}"
    if division == "Varsity Championship":
        return f"{gender}Champ"
    if division == "Middle School":
        return f"{gender}MS"
    return f"{gender}{suffix}"


def load_data():
    df = pd.read_csv(CSV_FILE)
    # Normalize grade - keep as int if whole number, else as is
    if "grade" in df.columns:
        df["grade"] = df["grade"].apply(
            lambda x: int(x) if pd.notna(x) and float(x).is_integer() else x
        )
    return df


def write_excel(df=None, path=OUTPUT_FILE):
    if df is None:
        df = load_data()
    # Select columns to match common conventions
    base_cols = ["place", "name", "grade", "team", "mark", "time_seconds"]
    # Keep only existing columns in order
    cols = [c for c in base_cols if c in df.columns]
    # Add any extra useful cols if missing? Also ensure athlete/name naming matches
    # Many files use 'athlete' not 'name' - rename for consistency
    df_out = df.copy()
    if "name" in df_out.columns and "athlete" not in df_out.columns:
        df_out = df_out.rename(columns={"name": "athlete"})
        cols = [c if c != "name" else "athlete" for c in base_cols if c in df.columns or c == "name"]
        cols = [c for c in cols if c in df_out.columns]

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for (sex, division), group in sorted(
            df_out.groupby(["sex", "division"]), key=lambda x: (x[0][0], x[0][1])
        ):
            sheet = sheet_name(sex, division)
            group_sorted = group.sort_values("place")
            # Select columns
            out_cols = ["place", "athlete"]
            if "grade" in group_sorted.columns:
                out_cols.append("grade")
            out_cols.extend(["team", "mark", "time_seconds"])
            # Filter to existing
            out_cols = [c for c in out_cols if c in group_sorted.columns]
            group_sorted[out_cols].to_excel(writer, sheet_name=sheet[:31], index=False)
    return Path(path)


if __name__ == "__main__":
    df = load_data()
    for (sex, division), group in df.groupby(["sex", "division"]):
        sheet = sheet_name(sex, division)
        print(f"{sheet}: {len(group)} finishers")
    print(f"\nWrote {write_excel(df)}")
