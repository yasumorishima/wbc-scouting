"""Fetch Statcast data for USA WBC batters/pitchers and save to CSV.

Usage:
    python fetch_data_usa.py                    # batters, 2024 + 2025
    python fetch_data_usa.py --pitchers         # pitchers, 2024 + 2025
    python fetch_data_usa.py --pitchers --year 2024
"""

import argparse
import time

import pandas as pd
from pybaseball import statcast_batter, statcast_pitcher

from players_usa_batters import USA_BATTERS
from players_usa_pitchers import USA_PITCHERS

KEEP_COLS_BATTER = [
    "batter",
    "player_name",
    "game_date",
    "pitch_type",
    "plate_x",
    "plate_z",
    "zone",
    "description",
    "events",
    "type",
    "hc_x",
    "hc_y",
    "hit_distance_sc",
    "launch_speed",
    "launch_angle",
    "bb_type",
    "estimated_ba_using_speedangle",
    "estimated_woba_using_speedangle",
    "p_throws",
    "stand",
    "balls",
    "strikes",
]

KEEP_COLS_PITCHER = [
    "pitcher",
    "player_name",
    "game_date",
    "pitch_type",
    "release_speed",
    "release_spin_rate",
    "pfx_x",
    "pfx_z",
    "plate_x",
    "plate_z",
    "zone",
    "description",
    "events",
    "type",
    "launch_speed",
    "launch_angle",
    "estimated_ba_using_speedangle",
    "estimated_woba_using_speedangle",
    "p_throws",
    "stand",
    "balls",
    "strikes",
    "bb_type",
    "release_extension",
    "spin_axis",
]

SEASONS = {
    2024: ("2024-03-20", "2024-11-05"),
    2025: ("2025-03-20", "2025-11-05"),
}

OUT_PATH_BATTER = "data/usa_statcast.csv"
OUT_PATH_PITCHER = "data/usa_pitchers_statcast.csv"


def fetch_batters(years: list[int]) -> pd.DataFrame:
    frames = []
    total = len(USA_BATTERS) * len(years)
    idx = 0
    for year in years:
        start, end = SEASONS[year]
        for p in USA_BATTERS:
            idx += 1
            print(f"[{idx}/{total}] {p['name']} ({year}) ...", end=" ", flush=True)
            try:
                df = statcast_batter(start, end, p["mlbam_id"])
                if df is not None and len(df) > 0:
                    available = [c for c in KEEP_COLS_BATTER if c in df.columns]
                    df = df[available].copy()
                    df["season"] = year
                    frames.append(df)
                    print(f"{len(df)} rows")
                else:
                    print("no data")
            except Exception as e:
                print(f"ERROR: {e}")
            time.sleep(2)
    if not frames:
        raise RuntimeError("No data fetched at all — check network / pybaseball.")
    return pd.concat(frames, ignore_index=True)


def fetch_pitchers(years: list[int]) -> pd.DataFrame:
    frames = []
    total = len(USA_PITCHERS) * len(years)
    idx = 0
    for year in years:
        start, end = SEASONS[year]
        for p in USA_PITCHERS:
            idx += 1
            print(f"[{idx}/{total}] {p['name']} ({year}) ...", end=" ", flush=True)
            try:
                df = statcast_pitcher(start, end, p["mlbam_id"])
                if df is not None and len(df) > 0:
                    available = [c for c in KEEP_COLS_PITCHER if c in df.columns]
                    df = df[available].copy()
                    df["season"] = year
                    frames.append(df)
                    print(f"{len(df)} rows")
                else:
                    print("no data")
            except Exception as e:
                print(f"ERROR: {e}")
            time.sleep(2)
    if not frames:
        raise RuntimeError("No data fetched at all — check network / pybaseball.")
    return pd.concat(frames, ignore_index=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year",
        type=int,
        choices=[2024, 2025],
        default=None,
        help="Fetch single season (default: both 2024 & 2025)",
    )
    parser.add_argument(
        "--pitchers",
        action="store_true",
        help="Fetch pitcher data instead of batter data",
    )
    args = parser.parse_args()
    years = [args.year] if args.year else [2024, 2025]

    if args.pitchers:
        print(f"Fetching Statcast data for {len(USA_PITCHERS)} USA pitchers, seasons {years}")
        combined = fetch_pitchers(years)
        combined.to_csv(OUT_PATH_PITCHER, index=False)
        print(f"\nSaved {len(combined)} rows to {OUT_PATH_PITCHER}")
    else:
        print(f"Fetching Statcast data for {len(USA_BATTERS)} USA batters, seasons {years}")
        combined = fetch_batters(years)
        combined.to_csv(OUT_PATH_BATTER, index=False)
        print(f"\nSaved {len(combined)} rows to {OUT_PATH_BATTER}")

    print(f"File size: {combined.memory_usage(deep=True).sum() / 1e6:.1f} MB (in-memory)")


if __name__ == "__main__":
    main()
