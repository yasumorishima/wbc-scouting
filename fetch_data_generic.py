"""Generic Statcast fetch script — works for any WBC country.

Usage:
    python fetch_data_generic.py --country japan
    python fetch_data_generic.py --country japan --pitchers
    python fetch_data_generic.py --country japan --pitchers --year 2024
"""

import argparse
import importlib
import time

import pandas as pd
from pybaseball import statcast_batter, statcast_pitcher

KEEP_COLS_BATTER = [
    "batter", "player_name", "game_date", "pitch_type",
    "plate_x", "plate_z", "zone", "description", "events", "type",
    "hc_x", "hc_y", "hit_distance_sc", "launch_speed", "launch_angle",
    "bb_type", "estimated_ba_using_speedangle", "estimated_woba_using_speedangle",
    "p_throws", "stand", "balls", "strikes",
]

KEEP_COLS_PITCHER = [
    "pitcher", "player_name", "game_date", "pitch_type",
    "release_speed", "release_spin_rate", "pfx_x", "pfx_z",
    "plate_x", "plate_z", "zone", "description", "events", "type",
    "launch_speed", "launch_angle", "estimated_ba_using_speedangle",
    "estimated_woba_using_speedangle", "p_throws", "stand", "balls", "strikes",
    "bb_type", "release_extension", "spin_axis",
]

SEASONS = {
    2024: ("2024-03-20", "2024-11-05"),
    2025: ("2025-03-20", "2025-11-05"),
}


def load_players(country: str, pitchers: bool):
    kind = "pitchers" if pitchers else "batters"
    module_name = f"players_{country}_{kind}"
    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError:
        raise SystemExit(f"ERROR: {module_name}.py not found. Run gen_player_files.py first.")

    # Find the list variable (e.g. JAPAN_BATTERS, MEX_PITCHERS, ...)
    for attr in dir(mod):
        val = getattr(mod, attr)
        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
            if "mlbam_id" in val[0]:
                return [p for p in val if p["mlbam_id"] != 0]
    # No list found or all mlbam_id == 0 → return empty (will be skipped)
    return []


def fetch_batters(players: list, years: list) -> pd.DataFrame:
    frames = []
    total = len(players) * len(years)
    idx = 0
    for year in years:
        start, end = SEASONS[year]
        for p in players:
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
        return None
    return pd.concat(frames, ignore_index=True)


def fetch_pitchers(players: list, years: list) -> pd.DataFrame:
    frames = []
    total = len(players) * len(years)
    idx = 0
    for year in years:
        start, end = SEASONS[year]
        for p in players:
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
        return None
    return pd.concat(frames, ignore_index=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", required=True, help="Country code (e.g. japan, mex, kor)")
    parser.add_argument("--pitchers", action="store_true")
    parser.add_argument("--year", type=int, choices=[2024, 2025], default=None)
    args = parser.parse_args()

    years = [args.year] if args.year else [2024, 2025]
    players = load_players(args.country, args.pitchers)

    kind = "pitchers" if args.pitchers else "batters"
    out_path = f"data/{args.country}_{'pitchers_' if args.pitchers else ''}statcast.csv"

    print(f"Fetching {len(players)} {kind} for {args.country}, seasons {years}")
    if not players:
        print("No players with valid mlbam_id — skipping.")
        return

    if args.pitchers:
        df = fetch_pitchers(players, years)
    else:
        df = fetch_batters(players, years)

    if df is None or len(df) == 0:
        print("No data fetched — skipping.")
        return

    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} rows → {out_path}")
    print(f"Memory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
