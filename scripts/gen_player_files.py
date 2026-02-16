"""Generate players_XX_batters.py and players_XX_pitchers.py for all WBC countries.

Reads data/wbc2026_rosters.csv, looks up MLBAM IDs via pybaseball.playerid_lookup,
and writes player files for each country.

Usage:
    python scripts/gen_player_files.py            # all remaining countries
    python scripts/gen_player_files.py --country japan  # single country
"""

import argparse
import re
import time
from pathlib import Path

import pandas as pd
from pybaseball import playerid_lookup

# Country header prefix → (file_code, display_name)
COUNTRY_MAP = {
    "Japan":           ("japan", "Japan"),
    "Mexico":          ("mex",   "Mexico"),
    "Korea":           ("kor",   "Korea"),
    "Chinese Taipei":  ("twn",   "Chinese Taipei"),
    "Netherlands":     ("ned",   "Netherlands"),
    "Cuba":            ("cuba",  "Cuba"),
    "Canada":          ("can",   "Canada"),
    "Italy":           ("ita",   "Italy"),
    "Israel":          ("isr",   "Israel"),
    "Great Britain":   ("gb",    "Great Britain"),
    "Panama":          ("pan",   "Panama"),
    "Colombia":        ("col",   "Colombia"),
    "Nicaragua":       ("nic",   "Nicaragua"),
    "Australia":       ("aus",   "Australia"),
    "Brazil":          ("bra",   "Brazil"),
}

# Already done — skip by default
DONE_CODES = {"usa", "dr", "venezuela", "pr"}

PITCHER_POS = {"LHP", "RHP", "SP", "RP", "CP"}


def is_pitcher(pos: str) -> bool:
    pos = pos.strip().upper()
    return pos in PITCHER_POS or pos.endswith("HP")


def parse_english_name(raw: str) -> str:
    """Extract English name.
    '大谷翔平 / Shohei Ohtani' → 'Shohei Ohtani'
    'Woo Suk Go（高宇錫）'      → 'Woo Suk Go'
    'Alex Bregman'             → 'Alex Bregman'
    """
    # Japanese/Chinese: 'Japanese / English'
    if " / " in raw:
        return raw.split(" / ", 1)[1].strip()
    # Korean/Chinese Taipei: 'English（Chinese）'
    raw = re.sub(r"（.*?）", "", raw).strip()
    return raw


def lookup_mlbam_id(name: str) -> int:
    """Return MLBAM ID for a player name, or 0 if not found."""
    parts = name.split()
    if len(parts) < 2:
        return 0
    last = parts[-1]
    first = parts[0]
    try:
        result = playerid_lookup(last, first)
        if result is not None and len(result) > 0:
            # Prefer active players (mlb_played_last is recent)
            result = result.sort_values("mlb_played_last", ascending=False)
            mlbam = int(result.iloc[0]["key_mlbam"])
            if mlbam > 0:
                return mlbam
    except Exception as e:
        print(f"    lookup error for {name}: {e}")
    return 0


def parse_roster_csv(csv_path: Path) -> dict:
    """Parse roster CSV. Returns {country_key: {batters: [...], pitchers: [...]}}"""
    with open(csv_path, encoding="utf-8-sig") as f:
        lines = f.readlines()

    teams = {}
    current_key = None

    for line in lines:
        line = line.strip()
        if not line:
            current_key = None
            continue

        # Team header line
        if "—" in line and "プール" in line:
            # e.g. "Japan（日本） — プールC（東京ドーム） — MLB組織所属: 9人,,,,"
            # Extract English country name
            raw_team = line.split("（")[0].strip()
            for prefix, (code, display) in COUNTRY_MAP.items():
                if raw_team.startswith(prefix):
                    current_key = code
                    teams[current_key] = {
                        "display": display,
                        "batters": [],
                        "pitchers": [],
                    }
                    break
            continue

        # Player line: "Name,POS,Team,40man,#"
        if current_key and "," in line and "選手名" not in line:
            parts = line.split(",")
            if len(parts) < 2:
                continue
            raw_name = parts[0].strip()
            pos = parts[1].strip()
            if not raw_name or not pos:
                continue
            eng_name = parse_english_name(raw_name)
            entry = {"raw": raw_name, "name": eng_name, "pos": pos}
            if is_pitcher(pos):
                teams[current_key]["pitchers"].append(entry)
            else:
                teams[current_key]["batters"].append(entry)

    return teams


def batter_throws(pos: str) -> str:
    return "R"  # unknown → default R


def write_batters_file(code: str, display: str, batters: list, out_dir: Path):
    lines = [f'"""WBC 2026 {display} roster — MLB batters."""\n\n']
    lines.append(f"{code.upper()}_BATTERS = [\n")
    not_found = []
    for p in batters:
        mid = p.get("mlbam_id", 0)
        name = p["name"]
        pos = p["pos"]
        comment = "  # TODO: ID not found" if mid == 0 else ""
        lines.append(
            f'    {{"name": "{name}",{" " * max(1, 28 - len(name))}'
            f'"mlbam_id": {mid}, "pos": "{pos}", "team": "", "bats": "R"}},{comment}\n'
        )
        if mid == 0:
            not_found.append(name)
    lines.append("]\n\n")
    lines.append(f"PLAYER_BY_ID   = {{p['mlbam_id']: p for p in {code.upper()}_BATTERS}}\n")
    lines.append(f"PLAYER_BY_NAME = {{p['name']: p for p in {code.upper()}_BATTERS}}\n")

    out_path = out_dir / f"players_{code}_batters.py"
    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"  Written: {out_path.name}  (not_found={not_found})")


def write_pitchers_file(code: str, display: str, pitchers: list, out_dir: Path):
    lines = [f'"""WBC 2026 {display} roster — MLB pitchers."""\n\n']
    lines.append(f"{code.upper()}_PITCHERS = [\n")
    not_found = []
    for p in pitchers:
        mid = p.get("mlbam_id", 0)
        name = p["name"]
        pos = p["pos"]
        role = "SP" if pos == "SP" else "RP"
        throws = "L" if "L" in pos else "R"
        comment = "  # TODO: ID not found" if mid == 0 else ""
        lines.append(
            f'    {{"name": "{name}",{" " * max(1, 28 - len(name))}'
            f'"mlbam_id": {mid}, "team": "", "throws": "{throws}", "role": "{role}"}},{comment}\n'
        )
        if mid == 0:
            not_found.append(name)
    lines.append("]\n\n")
    lines.append(f"PITCHER_BY_ID   = {{p['mlbam_id']: p for p in {code.upper()}_PITCHERS}}\n")
    lines.append(f"PITCHER_BY_NAME = {{p['name']: p for p in {code.upper()}_PITCHERS}}\n")

    out_path = out_dir / f"players_{code}_pitchers.py"
    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"  Written: {out_path.name}  (not_found={not_found})")


def process_country(code: str, data: dict, out_dir: Path):
    display = data["display"]
    print(f"\n{'='*50}")
    print(f"Processing: {display} ({code})")

    # Batters
    batters = data["batters"]
    print(f"  Looking up {len(batters)} batters...")
    for p in batters:
        mid = lookup_mlbam_id(p["name"])
        p["mlbam_id"] = mid
        status = mid if mid else "NOT FOUND"
        print(f"    {p['name']:30s} → {status}")
        time.sleep(0.3)

    # Pitchers
    pitchers = data["pitchers"]
    print(f"  Looking up {len(pitchers)} pitchers...")
    for p in pitchers:
        mid = lookup_mlbam_id(p["name"])
        p["mlbam_id"] = mid
        status = mid if mid else "NOT FOUND"
        print(f"    {p['name']:30s} → {status}")
        time.sleep(0.3)

    write_batters_file(code, display, batters, out_dir)
    write_pitchers_file(code, display, pitchers, out_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", default=None, help="Single country code to process")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    csv_path = root / "data" / "wbc2026_rosters.csv"
    teams = parse_roster_csv(csv_path)

    if args.country:
        if args.country not in teams:
            print(f"Country code '{args.country}' not found. Available: {list(teams.keys())}")
            return
        process_country(args.country, teams[args.country], root)
    else:
        for code, data in teams.items():
            if code in DONE_CODES:
                print(f"Skipping {code} (already done)")
                continue
            process_country(code, data, root)

    print("\nDone!")


if __name__ == "__main__":
    main()
