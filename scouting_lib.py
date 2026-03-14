"""Shared scouting library for WBC 2026 dashboards.

Contains all visualization, analysis, and utility functions used across
country-specific scouting apps. Eliminates code duplication.
"""

import pathlib

import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import gaussian_kde

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PITCH_LABELS = {
    "FF": "4-Seam", "SI": "Sinker", "FC": "Cutter", "SL": "Slider",
    "CU": "Curveball", "CH": "Changeup", "FS": "Splitter",
    "KC": "Knuckle Curve", "ST": "Sweeper", "SV": "Slurve",
}
PITCH_COLORS = {
    "FF": "#FF6347", "SI": "#FF8C00", "FC": "#DAA520", "SL": "#4169E1",
    "CU": "#9370DB", "CH": "#2E8B57", "FS": "#20B2AA", "KC": "#BA55D3",
    "ST": "#1E90FF", "SV": "#7B68EE",
}
POS_LABELS = {
    "EN": {
        "C": "Catcher", "1B": "First Base", "2B": "Second Base",
        "3B": "Third Base", "SS": "Shortstop", "LF": "Left Field",
        "CF": "Center Field", "RF": "Right Field", "DH": "Designated Hitter",
        "P": "Pitcher", "SP": "Starting Pitcher", "RP": "Relief Pitcher",
    },
    "JA": {
        "C": "捕手", "1B": "一塁手", "2B": "二塁手",
        "3B": "三塁手", "SS": "遊撃手", "LF": "左翼手",
        "CF": "中堅手", "RF": "右翼手", "DH": "指名打者",
        "P": "投手", "SP": "先発投手", "RP": "救援投手",
    },
}

_AB_EVENTS = {"single", "double", "triple", "home_run", "field_out",
              "strikeout", "grounded_into_double_play", "double_play",
              "force_out", "fielders_choice", "fielders_choice_out",
              "strikeout_double_play", "triple_play", "field_error"}
_PA_EVENTS = _AB_EVENTS | {"walk", "hit_by_pitch", "sac_fly", "sac_bunt",
                            "sac_fly_double_play", "catcher_interf",
                            "intent_walk"}
_HIT_EVENTS = {"single", "double", "triple", "home_run"}
_SWING_DESCS = {"hit_into_play", "foul", "swinging_strike",
                "swinging_strike_blocked", "foul_tip"}
_WHIFF_DESCS = {"swinging_strike", "swinging_strike_blocked"}

_MLB_AVG_BAT = {"AVG": .243, "OBP": .312, "SLG": .397, "OPS": .709,
                "K%": 22.4, "BB%": 8.3, "xwOBA": .311}
_MLB_AVG_PIT = {"Opp AVG": .243, "Opp SLG": .397, "K%": 22.4, "BB%": 8.3,
                "xwOBA": .311, "Whiff%": 25.0, "Velo": 93.5}

_STAT_HELP = {
    "EN": {
        "AVG": "Batting average — hits ÷ at-bats. MLB avg ≈ .243",
        "OBP": "On-base percentage — how often the batter reaches base. MLB avg ≈ .312",
        "SLG": "Slugging percentage — total bases ÷ at-bats. Measures power. MLB avg ≈ .397",
        "OPS": "OBP + SLG combined. Above .800 = strong hitter. MLB avg ≈ .709",
        "K%": "Strikeout rate — % of PA ending in a strikeout. MLB avg ≈ 22.4%",
        "BB%": "Walk rate — % of PA ending in a walk. MLB avg ≈ 8.3%",
        "xwOBA": "Expected weighted on-base average — batted ball quality measure. MLB avg ≈ .311",
        "Whiff%": "Whiff rate — swinging strikes ÷ total swings. MLB avg ≈ 25%",
        "Chase%": "Chase rate — swings at pitches outside the zone ÷ pitches outside zone",
        "Opp AVG": "Opponent batting average — batting average allowed. MLB avg ≈ .243",
        "Opp SLG": "Opponent slugging — slugging percentage allowed. MLB avg ≈ .397",
        "Avg Velo": "Average fastball velocity in mph (km/h)",
        "Put Away%": "Put-away rate — strikeouts on 2-strike counts ÷ total 2-strike pitches",
    },
    "JA": {
        "AVG": "打率 — 安打数÷打数。MLB平均 ≈ .243",
        "OBP": "出塁率 — 打席で塁に出る割合。MLB平均 ≈ .312",
        "SLG": "長打率 — 塁打数÷打数。長打力の指標。MLB平均 ≈ .397",
        "OPS": "出塁率+長打率。.800以上で強打者。MLB平均 ≈ .709",
        "K%": "三振率 — 打席に占める三振の割合。MLB平均 ≈ 22.4%",
        "BB%": "四球率 — 打席に占める四球の割合。MLB平均 ≈ 8.3%",
        "xwOBA": "期待加重出塁率 — 打球速度と角度から算出した打撃力。MLB平均 ≈ .311",
        "Whiff%": "空振率 — スイング中の空振りの割合。MLB平均 ≈ 25%",
        "Chase%": "チェイス率 — ストライクゾーン外の球を振る割合",
        "Opp AVG": "被打率 — 投手が打たれた打率。MLB平均 ≈ .243",
        "Opp SLG": "被長打率 — 投手が許した長打率。MLB平均 ≈ .397",
        "Avg Velo": "平均球速（mph / km/h）",
        "Put Away%": "決め球成功率 — 2ストライク後に三振を取った割合",
    },
}

STADIUMS = {
    "EN": {
        "astros": "Daikin Park (Houston)",
        "marlins": "LoanDepot Park (Miami)",
    },
    "JA": {
        "astros": "ダイキン・パーク（ヒューストン）",
        "marlins": "ローンデポ・パーク（マイアミ）",
    },
}

STADIUM_SCALE = 2.495 / 2.33
STADIUM_CSV = pathlib.Path(__file__).parent / "data" / "mlbstadiums_wbc.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def stat_help(stat_key: str, lang: str) -> str:
    """Return tooltip help text for a stat."""
    return _STAT_HELP.get(lang, _STAT_HELP["EN"]).get(stat_key, "")


def display_name(name: str, player_by_name: dict, lang: str) -> str:
    """Get bilingual display name from player lookup dict."""
    p = player_by_name.get(name)
    if p and lang == "JA":
        ja = p.get("name_ja", "")
        if ja:
            return f"{ja}（{name}）"
    return name


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
@st.cache_data
def load_stadium_coords() -> pd.DataFrame:
    df = pd.read_csv(STADIUM_CSV)
    df["x"] = (df["x"] - 125) * STADIUM_SCALE + 125
    df["y"] = -((df["y"] - 199) * STADIUM_SCALE + 199)
    df["y"] = -df["y"]
    return df


@st.cache_data
def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df["game_date"] = pd.to_datetime(df["game_date"])
    if "season" not in df.columns:
        df["season"] = df["game_date"].dt.year
    return df


def filter_season(df: pd.DataFrame, season) -> pd.DataFrame:
    return df[df["season"] == int(season)]


# ---------------------------------------------------------------------------
# Stats computation
# ---------------------------------------------------------------------------
def batting_stats(df: pd.DataFrame) -> dict:
    """Compute basic batting stats from Statcast event-level data."""
    evts = df.dropna(subset=["events"])
    pa = evts[evts["events"].isin(_PA_EVENTS)]
    ab = evts[evts["events"].isin(_AB_EVENTS)]
    hits = evts[evts["events"].isin(_HIT_EVENTS)]

    n_pa = len(pa)
    n_ab = len(ab)
    n_h = len(hits)
    n_bb = len(pa[pa["events"].isin({"walk", "intent_walk"})])
    n_hbp = len(pa[pa["events"].isin({"hit_by_pitch"})])
    n_1b = len(hits[hits["events"] == "single"])
    n_2b = len(hits[hits["events"] == "double"])
    n_3b = len(hits[hits["events"] == "triple"])
    n_hr = len(hits[hits["events"] == "home_run"])
    n_k = len(ab[ab["events"].str.contains("strikeout", na=False)])
    tb = n_1b + 2 * n_2b + 3 * n_3b + 4 * n_hr

    avg = n_h / n_ab if n_ab else 0
    obp = (n_h + n_bb + n_hbp) / n_pa if n_pa else 0
    slg = tb / n_ab if n_ab else 0
    ops = obp + slg
    k_pct = n_k / n_pa * 100 if n_pa else 0
    bb_pct = n_bb / n_pa * 100 if n_pa else 0
    xwoba = df["estimated_woba_using_speedangle"].dropna().mean()

    return {
        "PA": n_pa, "AB": n_ab, "H": n_h, "HR": n_hr,
        "AVG": round(avg, 3), "OBP": round(obp, 3),
        "SLG": round(slg, 3), "OPS": round(ops, 3),
        "K%": round(k_pct, 1), "BB%": round(bb_pct, 1),
        "xwOBA": round(xwoba, 3) if not pd.isna(xwoba) else None,
    }


def pitching_stats(df: pd.DataFrame) -> dict:
    """Compute pitching stats from Statcast pitch-level data."""
    total_pitches = len(df)
    evts = df.dropna(subset=["events"])
    pa = evts[evts["events"].isin(_PA_EVENTS)]
    ab = evts[evts["events"].isin(_AB_EVENTS)]
    hits = evts[evts["events"].isin(_HIT_EVENTS)]

    n_pa = len(pa)
    n_ab = len(ab)
    n_h = len(hits)
    n_k = len(ab[ab["events"].str.contains("strikeout", na=False)])
    n_bb = len(pa[pa["events"].isin({"walk", "intent_walk"})])
    n_1b = len(hits[hits["events"] == "single"])
    n_2b = len(hits[hits["events"] == "double"])
    n_3b = len(hits[hits["events"] == "triple"])
    n_hr = len(hits[hits["events"] == "home_run"])
    tb = n_1b + 2 * n_2b + 3 * n_3b + 4 * n_hr

    opp_avg = n_h / n_ab if n_ab else 0
    opp_slg = tb / n_ab if n_ab else 0
    k_pct = n_k / n_pa * 100 if n_pa else 0
    bb_pct = n_bb / n_pa * 100 if n_pa else 0
    xwoba = df["estimated_woba_using_speedangle"].dropna().mean()
    avg_velo = df["release_speed"].dropna().mean() if "release_speed" in df.columns else None

    swing_events = {"hit_into_play", "foul", "swinging_strike",
                    "swinging_strike_blocked", "foul_tip", "hit_into_play_score",
                    "hit_into_play_no_out"}
    swings = df[df["description"].isin(swing_events)]
    whiffs = df[df["description"].isin({"swinging_strike", "swinging_strike_blocked", "foul_tip"})]
    whiff_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0

    return {
        "Pitches": total_pitches,
        "PA": n_pa, "K": n_k, "BB": n_bb, "HR": n_hr,
        "Opp AVG": round(opp_avg, 3),
        "Opp SLG": round(opp_slg, 3),
        "K%": round(k_pct, 1),
        "BB%": round(bb_pct, 1),
        "Whiff%": round(whiff_pct, 1),
        "xwOBA": round(xwoba, 3) if not pd.isna(xwoba) else None,
        "Avg Velo": round(avg_velo, 1) if avg_velo and not pd.isna(avg_velo) else None,
    }


# ---------------------------------------------------------------------------
# Scouting summaries
# ---------------------------------------------------------------------------
def generate_player_summary(stats: dict, pdf: pd.DataFrame, player: dict,
                            lang: str) -> str:
    """Auto-generate a scouting summary for a batter."""
    strengths = []
    weaknesses = []

    if stats["SLG"] >= 0.450:
        strengths.append(f"SLG .{int(stats['SLG']*1000):03d} (MLB avg .397)" if lang == "EN"
                         else f"長打率 .{int(stats['SLG']*1000):03d}（MLB平均 .397）")
    elif stats["SLG"] >= 0.400:
        strengths.append(f"SLG .{int(stats['SLG']*1000):03d} (MLB avg .397)" if lang == "EN"
                         else f"長打率 .{int(stats['SLG']*1000):03d}（MLB平均 .397）")
    if stats["AVG"] >= 0.300:
        strengths.append(f"AVG .{int(stats['AVG']*1000):03d} (MLB avg .248)" if lang == "EN"
                         else f"打率 .{int(stats['AVG']*1000):03d}（MLB平均 .248）")
    elif stats["AVG"] >= 0.270:
        strengths.append(f"AVG .{int(stats['AVG']*1000):03d} (MLB avg .248)" if lang == "EN"
                         else f"打率 .{int(stats['AVG']*1000):03d}（MLB平均 .248）")
    if stats["BB%"] >= 10.0:
        strengths.append(f"BB% {stats['BB%']:.1f}% (MLB avg 8.3%)" if lang == "EN"
                         else f"四球率 {stats['BB%']:.1f}%（MLB平均 8.3%）")
    if stats["xwOBA"] and stats["xwOBA"] >= 0.350:
        strengths.append(f"xwOBA .{int(stats['xwOBA']*1000):03d} (MLB avg .311)" if lang == "EN"
                         else f"xwOBA .{int(stats['xwOBA']*1000):03d}（MLB平均 .311）")
    if stats["K%"] >= 25.0:
        weaknesses.append(f"K% {stats['K%']:.1f}% (MLB avg 22.4%)" if lang == "EN"
                          else f"三振率 {stats['K%']:.1f}%（MLB平均 22.4%）")
    elif stats["K%"] >= 20.0:
        weaknesses.append(f"K% {stats['K%']:.1f}% (MLB avg 22.4%)" if lang == "EN"
                          else f"三振率 {stats['K%']:.1f}%（MLB平均 22.4%）")

    vs_l = pdf[pdf["p_throws"] == "L"]
    vs_r = pdf[pdf["p_throws"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        s_l = batting_stats(vs_l)
        s_r = batting_stats(vs_r)
        if s_l["PA"] >= 30 and s_r["PA"] >= 30:
            ops_diff = abs(s_l["OPS"] - s_r["OPS"])
            if ops_diff >= 0.100:
                weak_side = "LHP" if s_l["OPS"] < s_r["OPS"] else "RHP"
                weak_ops = s_l["OPS"] if s_l["OPS"] < s_r["OPS"] else s_r["OPS"]
                if lang == "EN":
                    weaknesses.append(
                        f"notable platoon split — weaker vs {weak_side} "
                        f"(OPS .{int(weak_ops * 1000):03d})")
                else:
                    weak_ja = "左投手" if weak_side == "LHP" else "右投手"
                    weaknesses.append(
                        f"左右差が大きい — {weak_ja}に弱い "
                        f"（OPS .{int(weak_ops * 1000):03d}）")

    lines = []
    if strengths:
        header = "**Strengths:**" if lang == "EN" else "**強み:**"
        lines.append(header)
        for s in strengths:
            lines.append(f"- {s}")
    if weaknesses:
        header = "**Weaknesses:**" if lang == "EN" else "**弱み:**"
        lines.append(header)
        for w in weaknesses:
            lines.append(f"- {w}")
    if not lines:
        return ("- Balanced profile with no extreme strengths or weaknesses."
                if lang == "EN" else "- 特に目立つ偏りのないバランス型の打者。")
    return "\n".join(lines)


def generate_pitcher_summary(stats: dict, pdf: pd.DataFrame, pitcher: dict,
                             lang: str) -> str:
    """Auto-generate a scouting summary for a pitcher."""
    strengths = []
    weaknesses = []

    if stats["K%"] >= 25.0:
        strengths.append(f"K% {stats['K%']:.1f}% (MLB avg 22.4%)" if lang == "EN"
                         else f"奪三振率 {stats['K%']:.1f}%（MLB平均 22.4%）")
    elif stats["K%"] >= 20.0:
        strengths.append(f"K% {stats['K%']:.1f}% (MLB avg 22.4%)" if lang == "EN"
                         else f"奪三振率 {stats['K%']:.1f}%（MLB平均 22.4%）")
    if stats["Opp AVG"] <= 0.220:
        strengths.append(f"Opp AVG .{int(stats['Opp AVG'] * 1000):03d} (MLB avg .248)" if lang == "EN"
                         else f"被打率 .{int(stats['Opp AVG'] * 1000):03d}（MLB平均 .248）")
    if stats["xwOBA"] and stats["xwOBA"] <= 0.290:
        strengths.append(f"xwOBA .{int(stats['xwOBA']*1000):03d} (MLB avg .311)" if lang == "EN"
                         else f"被xwOBA .{int(stats['xwOBA']*1000):03d}（MLB平均 .311）")
    if stats["Avg Velo"] and stats["Avg Velo"] >= 95.0:
        strengths.append(f"Avg Velo {stats['Avg Velo']:.1f} mph (MLB avg 93.5 mph)" if lang == "EN"
                         else f"平均球速 {stats['Avg Velo']:.1f} mph（MLB平均 93.5 mph）")
    if stats["BB%"] >= 10.0:
        weaknesses.append(f"BB% {stats['BB%']:.1f}% (MLB avg 8.3%)" if lang == "EN"
                          else f"与四球率 {stats['BB%']:.1f}%（MLB平均 8.3%）")
    elif stats["BB%"] >= 8.0:
        weaknesses.append(f"BB% {stats['BB%']:.1f}% (MLB avg 8.3%)" if lang == "EN"
                          else f"与四球率 {stats['BB%']:.1f}%（MLB平均 8.3%）")
    if stats["K%"] < 15.0:
        weaknesses.append(f"K% {stats['K%']:.1f}% (MLB avg 22.4%)" if lang == "EN"
                          else f"奪三振率 {stats['K%']:.1f}%（MLB平均 22.4%）")

    vs_l = pdf[pdf["stand"] == "L"]
    vs_r = pdf[pdf["stand"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        s_l = pitching_stats(vs_l)
        s_r = pitching_stats(vs_r)
        if s_l["PA"] >= 30 and s_r["PA"] >= 30:
            avg_diff = abs(s_l["Opp AVG"] - s_r["Opp AVG"])
            if avg_diff >= 0.040:
                weak_side = "LHB" if s_l["Opp AVG"] > s_r["Opp AVG"] else "RHB"
                weak_avg = max(s_l["Opp AVG"], s_r["Opp AVG"])
                if lang == "EN":
                    weaknesses.append(
                        f"platoon vulnerability — weaker vs {weak_side} "
                        f"(Opp AVG .{int(weak_avg * 1000):03d})")
                else:
                    weak_ja = "左打者" if weak_side == "LHB" else "右打者"
                    weaknesses.append(
                        f"左右差あり — {weak_ja}に打たれやすい "
                        f"（被打率 .{int(weak_avg * 1000):03d}）")

    lines = []
    if strengths:
        header = "**Strengths:**" if lang == "EN" else "**強み:**"
        lines.append(header)
        for s in strengths:
            lines.append(f"- {s}")
    if weaknesses:
        header = "**Weaknesses:**" if lang == "EN" else "**弱み:**"
        lines.append(header)
        for w in weaknesses:
            lines.append(f"- {w}")
    if not lines:
        return ("- Balanced profile with no extreme strengths or weaknesses."
                if lang == "EN" else "- 特に目立つ偏りのないバランス型の投手。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Strategic analysis
# ---------------------------------------------------------------------------
def _zone_names_for_bats(bats: str, lang: str) -> dict:
    """Return zone names adjusted for batter handedness."""
    if bats == "L":
        if lang == "JA":
            return {1: "高めアウト", 2: "高め真ん中", 3: "高めイン",
                    4: "真ん中アウト", 5: "ど真ん中", 6: "真ん中イン",
                    7: "低めアウト", 8: "低め真ん中", 9: "低めイン"}
        return {1: "Up-Away", 2: "Up-Mid", 3: "Up-In",
                4: "Mid-Away", 5: "Heart", 6: "Mid-In",
                7: "Down-Away", 8: "Down-Mid", 9: "Down-In"}
    if lang == "JA":
        return {1: "高めイン", 2: "高め真ん中", 3: "高めアウト",
                4: "真ん中イン", 5: "ど真ん中", 6: "真ん中アウト",
                7: "低めイン", 8: "低め真ん中", 9: "低めアウト"}
    return {1: "Up-In", 2: "Up-Mid", 3: "Up-Away",
            4: "Mid-In", 5: "Heart", 6: "Mid-Away",
            7: "Down-In", 8: "Down-Mid", 9: "Down-Away"}


def generate_pitching_plan(pdf: pd.DataFrame, stats: dict,
                           player_info: dict, lang: str) -> str:
    """Generate data-driven pitching plan for a batter."""
    lines = []
    bats = player_info.get("bats", "R")

    # 1. Pitch type vulnerability
    valid_pt = pdf.dropna(subset=["pitch_type"]).copy()
    if not valid_pt.empty:
        pt_stats = []
        for pt, grp in valid_pt.groupby("pitch_type"):
            if len(grp) < 15:
                continue
            ab = grp[grp["events"].isin(_AB_EVENTS)]
            hits = grp[grp["events"].isin(_HIT_EVENTS)]
            swings = grp[grp["description"].isin(_SWING_DESCS)]
            whiffs = grp[grp["description"].isin(_WHIFF_DESCS)]
            ba = len(hits) / len(ab) if len(ab) >= 10 else None
            whiff_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0
            outside = grp[(grp["zone"].notna()) & (grp["zone"] >= 11)]
            chase_swings = outside[outside["description"].isin(_SWING_DESCS)]
            chase_pct = len(chase_swings) / len(outside) * 100 if len(outside) > 0 else 0
            label = PITCH_LABELS.get(pt, pt)
            pt_stats.append({"type": pt, "label": label, "count": len(grp),
                             "ba": ba, "whiff": whiff_pct, "chase": chase_pct})

        if pt_stats:
            best_whiff = sorted([p for p in pt_stats if p["whiff"] > 0],
                                key=lambda x: x["whiff"], reverse=True)
            hittable = sorted([p for p in pt_stats if p["ba"] is not None],
                              key=lambda x: x["ba"], reverse=True)
            best_chase = sorted([p for p in pt_stats if p["chase"] > 0],
                                key=lambda x: x["chase"], reverse=True)
            if best_whiff:
                bw = best_whiff[0]
                lines.append(
                    f"- **Best strikeout pitch:** {bw['label']} (Whiff% {bw['whiff']:.1f}%)"
                    if lang == "EN" else
                    f"- **決め球に最適:** {bw['label']}（空振率 {bw['whiff']:.1f}%）")
            if hittable and hittable[0]["ba"] is not None and hittable[0]["ba"] >= 0.280:
                h = hittable[0]
                lines.append(
                    f"- **Avoid:** {h['label']} — he hits it well (BA .{int(h['ba']*1000):03d})"
                    if lang == "EN" else
                    f"- **要注意球種:** {h['label']} — 打率 .{int(h['ba']*1000):03d} で打たれている")
            if best_chase:
                bc = best_chase[0]
                lines.append(
                    f"- **Chase pitch:** {bc['label']} outside the zone (Chase% {bc['chase']:.1f}%)"
                    if lang == "EN" else
                    f"- **ゾーン外で振らせる球:** {bc['label']}（チェイス率 {bc['chase']:.1f}%）")

    # 2. Zone weakness (3x3)
    zone_valid = pdf.dropna(subset=["zone"]).copy()
    zone_valid["zone"] = zone_valid["zone"].astype(int)
    zone_names = _zone_names_for_bats(bats, lang)
    zone_ba = {}
    for z in range(1, 10):
        zdf = zone_valid[zone_valid["zone"] == z]
        ab = zdf[zdf["events"].isin(_AB_EVENTS)]
        hits = zdf[zdf["events"].isin(_HIT_EVENTS)]
        if len(ab) >= 5:
            zone_ba[z] = len(hits) / len(ab)
    if zone_ba:
        weak_zones = sorted(zone_ba.items(), key=lambda x: x[1])[:2]
        strong_zones = sorted(zone_ba.items(), key=lambda x: x[1], reverse=True)[:2]
        weak_str = ", ".join([f"{zone_names[z]} (.{int(ba*1000):03d})" for z, ba in weak_zones if ba < 0.250])
        strong_str = ", ".join([f"{zone_names[z]} (.{int(ba*1000):03d})" for z, ba in strong_zones if ba >= 0.300])
        if weak_str:
            lines.append(f"- **Attack zones (low BA):** {weak_str}" if lang == "EN"
                         else f"- **攻めるゾーン（低打率）:** {weak_str}")
        if strong_str:
            lines.append(f"- **Danger zones (high BA):** {strong_str}" if lang == "EN"
                         else f"- **危険ゾーン（高打率）:** {strong_str}")

    # 3. Count analysis
    count_valid = pdf.dropna(subset=["balls", "strikes"]).copy()
    count_valid["balls"] = count_valid["balls"].astype(int)
    count_valid["strikes"] = count_valid["strikes"].astype(int)
    ahead_df = count_valid[count_valid["balls"] > count_valid["strikes"]]
    behind_df = count_valid[count_valid["strikes"] > count_valid["balls"]]
    two_strike_df = count_valid[count_valid["strikes"] == 2]
    ahead_s = batting_stats(ahead_df) if not ahead_df.empty else None
    behind_s = batting_stats(behind_df) if not behind_df.empty else None
    two_s = batting_stats(two_strike_df) if not two_strike_df.empty else None
    if ahead_s and behind_s and ahead_s["PA"] >= 20 and behind_s["PA"] >= 20:
        if ahead_s["OPS"] >= 0.800 and behind_s["OPS"] < 0.600:
            lines.append(
                f"- **Count split:** Ahead OPS .{int(ahead_s['OPS']*1000):03d} / "
                f"Behind OPS .{int(behind_s['OPS']*1000):03d}"
                if lang == "EN" else
                f"- **カウント別OPS:** 有利 .{int(ahead_s['OPS']*1000):03d} / "
                f"不利 .{int(behind_s['OPS']*1000):03d}")
        elif behind_s["OPS"] >= 0.700:
            lines.append(
                f"- **Count split:** Behind OPS .{int(behind_s['OPS']*1000):03d} — "
                f"productive even when behind" if lang == "EN" else
                f"- **カウント別OPS:** 不利カウントでも OPS .{int(behind_s['OPS']*1000):03d}")
    if two_s and two_s["PA"] >= 20:
        if two_s["K%"] >= 35:
            lines.append(
                f"- **2-strike K%:** {two_s['K%']:.1f}% (MLB avg ~30%)" if lang == "EN"
                else f"- **2ストライク後の三振率:** {two_s['K%']:.1f}%（MLB平均 約30%）")
        elif two_s["K%"] < 20:
            lines.append(
                f"- **2-strike K%:** {two_s['K%']:.1f}% — well below avg (~30%)"
                if lang == "EN" else
                f"- **2ストライク後の三振率:** {two_s['K%']:.1f}%（MLB平均 約30% を大きく下回る）")

    # 4. Platoon
    vs_l = pdf[pdf["p_throws"] == "L"]
    vs_r = pdf[pdf["p_throws"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        sl = batting_stats(vs_l)
        sr = batting_stats(vs_r)
        if sl["PA"] >= 30 and sr["PA"] >= 30:
            if sl["OPS"] < sr["OPS"] - 0.080:
                lines.append(
                    f"- **Platoon split:** vs LHP OPS .{int(sl['OPS']*1000):03d} / "
                    f"vs RHP OPS .{int(sr['OPS']*1000):03d}" if lang == "EN" else
                    f"- **左右別OPS:** 左投手 .{int(sl['OPS']*1000):03d} / "
                    f"右投手 .{int(sr['OPS']*1000):03d}")
            elif sr["OPS"] < sl["OPS"] - 0.080:
                lines.append(
                    f"- **Platoon split:** vs RHP OPS .{int(sr['OPS']*1000):03d} / "
                    f"vs LHP OPS .{int(sl['OPS']*1000):03d}" if lang == "EN" else
                    f"- **左右別OPS:** 右投手 .{int(sr['OPS']*1000):03d} / "
                    f"左投手 .{int(sl['OPS']*1000):03d}")

    # 5. Batted ball tendency
    bip = pdf.dropna(subset=["hc_x", "hc_y"]).copy()
    if len(bip) >= 20:
        bip["spray_angle"] = np.degrees(np.arctan2(bip["hc_x"] - 125.42, 198.27 - bip["hc_y"]))
        pull_pct = ((bip["spray_angle"] < -15).sum() if bats == "R"
                    else (bip["spray_angle"] > 15).sum()) / len(bip) * 100
        bb_types = pdf.dropna(subset=["bb_type"])
        if len(bb_types) >= 20:
            gb_pct = (bb_types["bb_type"] == "ground_ball").sum() / len(bb_types) * 100
            fb_pct = (bb_types["bb_type"] == "fly_ball").sum() / len(bb_types) * 100
            if pull_pct >= 45:
                lines.append(f"- **Pull%:** {pull_pct:.0f}% (MLB avg ~40%)" if lang == "EN"
                             else f"- **引っ張り率:** {pull_pct:.0f}%（MLB平均 約40%）")
            if gb_pct >= 50:
                lines.append(f"- **GB%:** {gb_pct:.0f}% (MLB avg ~43%)" if lang == "EN"
                             else f"- **ゴロ率:** {gb_pct:.0f}%（MLB平均 約43%）")
            elif fb_pct >= 45:
                lines.append(f"- **FB%:** {fb_pct:.0f}% (MLB avg ~35%)" if lang == "EN"
                             else f"- **フライ率:** {fb_pct:.0f}%（MLB平均 約35%）")

    if not lines:
        return ("- No statistically significant vulnerabilities detected in the data."
                if lang == "EN" else "- データ上、統計的に有意な弱点は検出されず。")
    return "\n".join(lines)


def generate_hitting_plan(pdf: pd.DataFrame, stats: dict,
                          pitcher_info: dict, lang: str) -> str:
    """Generate data-driven hitting plan against a pitcher."""
    lines = []

    # 1. Pitch type vulnerability
    valid_pt = pdf.dropna(subset=["pitch_type"]).copy()
    if not valid_pt.empty:
        pt_stats = []
        for pt, grp in valid_pt.groupby("pitch_type"):
            if len(grp) < 15:
                continue
            total = len(valid_pt)
            usage = len(grp) / total * 100
            ab = grp[grp["events"].isin(_AB_EVENTS)]
            hits = grp[grp["events"].isin(_HIT_EVENTS)]
            swings = grp[grp["description"].isin(_SWING_DESCS)]
            whiffs = grp[grp["description"].isin(_WHIFF_DESCS)]
            ba = len(hits) / len(ab) if len(ab) >= 10 else None
            whiff_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0
            label = PITCH_LABELS.get(pt, pt)
            pt_stats.append({"type": pt, "label": label, "count": len(grp),
                             "usage": usage, "ba": ba, "whiff": whiff_pct})

        if pt_stats:
            hittable = sorted([p for p in pt_stats if p["ba"] is not None],
                              key=lambda x: x["ba"], reverse=True)
            best_pitch = sorted([p for p in pt_stats if p["whiff"] > 0],
                                key=lambda x: x["whiff"], reverse=True)
            primary = sorted(pt_stats, key=lambda x: x["usage"], reverse=True)
            if primary:
                pr = primary[0]
                lines.append(
                    f"- **Primary pitch:** {pr['label']} ({pr['usage']:.0f}% usage)"
                    if lang == "EN" else
                    f"- **主要球種:** {pr['label']}（使用率 {pr['usage']:.0f}%）")
            if hittable and hittable[0]["ba"] is not None and hittable[0]["ba"] >= 0.250:
                h = hittable[0]
                lines.append(
                    f"- **Highest opp BA pitch:** {h['label']} (BA .{int(h['ba']*1000):03d})"
                    if lang == "EN" else
                    f"- **被打率が最も高い球種:** {h['label']}（被打率 .{int(h['ba']*1000):03d}）")
            if best_pitch:
                bp = best_pitch[0]
                lines.append(
                    f"- **Best strikeout pitch:** {bp['label']} (Whiff% {bp['whiff']:.1f}%)"
                    if lang == "EN" else
                    f"- **最も空振りを取る球種:** {bp['label']}（空振率 {bp['whiff']:.1f}%）")

    # 2. Zone vulnerability
    zone_valid = pdf.dropna(subset=["zone"]).copy()
    zone_valid["zone"] = zone_valid["zone"].astype(int)
    zone_names = _zone_names_for_bats("R", lang)
    zone_ba = {}
    for z in range(1, 10):
        zdf = zone_valid[zone_valid["zone"] == z]
        ab = zdf[zdf["events"].isin(_AB_EVENTS)]
        hits = zdf[zdf["events"].isin(_HIT_EVENTS)]
        if len(ab) >= 5:
            zone_ba[z] = len(hits) / len(ab)
    if zone_ba:
        hittable_zones = sorted(zone_ba.items(), key=lambda x: x[1], reverse=True)[:2]
        tough_zones = sorted(zone_ba.items(), key=lambda x: x[1])[:2]
        hit_str = ", ".join([f"{zone_names[z]} (.{int(ba*1000):03d})" for z, ba in hittable_zones if ba >= 0.280])
        tough_str = ", ".join([f"{zone_names[z]} (.{int(ba*1000):03d})" for z, ba in tough_zones if ba < 0.220])
        if hit_str:
            lines.append(f"- **High opp BA zones:** {hit_str}" if lang == "EN"
                         else f"- **被打率が高いゾーン:** {hit_str}")
        if tough_str:
            lines.append(f"- **Low opp BA zones:** {tough_str}" if lang == "EN"
                         else f"- **被打率が低いゾーン:** {tough_str}")

    # 3. Count strategy
    count_valid = pdf.dropna(subset=["balls", "strikes"]).copy()
    count_valid["balls"] = count_valid["balls"].astype(int)
    count_valid["strikes"] = count_valid["strikes"].astype(int)
    p_ahead = count_valid[count_valid["strikes"] > count_valid["balls"]]
    p_behind = count_valid[count_valid["balls"] > count_valid["strikes"]]
    if not p_ahead.empty and not p_behind.empty:
        pa_s = pitching_stats(p_ahead) if len(p_ahead) >= 30 else None
        pb_s = pitching_stats(p_behind) if len(p_behind) >= 30 else None
        if pa_s and pb_s:
            if pb_s["Opp AVG"] >= 0.280:
                lines.append(
                    f"- **Pitcher behind in count:** Opp AVG .{int(pb_s['Opp AVG']*1000):03d}"
                    if lang == "EN" else
                    f"- **投手不利カウント時の被打率:** .{int(pb_s['Opp AVG']*1000):03d}")
            if pa_s["K%"] >= 30:
                lines.append(
                    f"- **Pitcher ahead in count:** K% {pa_s['K%']:.1f}%"
                    if lang == "EN" else
                    f"- **投手有利カウント時の奪三振率:** {pa_s['K%']:.1f}%")

    # 4. First pitch tendency
    first_pitch = count_valid[(count_valid["balls"] == 0) & (count_valid["strikes"] == 0)]
    if len(first_pitch) >= 30:
        fp_types = first_pitch["pitch_type"].value_counts()
        if len(fp_types) > 0:
            top_fp = fp_types.index[0]
            top_fp_pct = fp_types.iloc[0] / len(first_pitch) * 100
            label = PITCH_LABELS.get(top_fp, top_fp)
            fp_strikes = first_pitch[first_pitch["description"].isin({
                "called_strike", "swinging_strike", "swinging_strike_blocked",
                "foul", "foul_tip", "hit_into_play",
            })]
            fp_strike_pct = len(fp_strikes) / len(first_pitch) * 100
            lines.append(
                f"- **First pitch:** {label} {top_fp_pct:.0f}%. Strike rate: {fp_strike_pct:.0f}%"
                if lang == "EN" else
                f"- **初球:** {label} {top_fp_pct:.0f}%。ストライク率: {fp_strike_pct:.0f}%")

    # 5. Platoon
    vs_l = pdf[pdf["stand"] == "L"]
    vs_r = pdf[pdf["stand"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        sl = pitching_stats(vs_l)
        sr = pitching_stats(vs_r)
        if sl["PA"] >= 20 and sr["PA"] >= 20:
            if sl["Opp AVG"] > sr["Opp AVG"] + 0.030:
                lines.append(
                    f"- **Platoon split:** vs LHB .{int(sl['Opp AVG']*1000):03d} / "
                    f"vs RHB .{int(sr['Opp AVG']*1000):03d}" if lang == "EN" else
                    f"- **左右別被打率:** 左打者 .{int(sl['Opp AVG']*1000):03d} / "
                    f"右打者 .{int(sr['Opp AVG']*1000):03d}")
            elif sr["Opp AVG"] > sl["Opp AVG"] + 0.030:
                lines.append(
                    f"- **Platoon split:** vs RHB .{int(sr['Opp AVG']*1000):03d} / "
                    f"vs LHB .{int(sl['Opp AVG']*1000):03d}" if lang == "EN" else
                    f"- **左右別被打率:** 右打者 .{int(sr['Opp AVG']*1000):03d} / "
                    f"左打者 .{int(sl['Opp AVG']*1000):03d}")

    if not lines:
        return ("- No statistically significant vulnerabilities detected."
                if lang == "EN" else "- データ上、統計的に有意な弱点は検出されず。")
    return "\n".join(lines)


def generate_defensive_positioning(pdf: pd.DataFrame, player_info: dict,
                                   lang: str) -> str:
    """Generate defensive positioning recommendation from spray chart data."""
    bats = player_info.get("bats", "R")
    lines = []

    bip = pdf.dropna(subset=["hc_x", "hc_y"]).copy()
    if len(bip) < 20:
        return ("Insufficient batted ball data for positioning recommendation."
                if lang == "EN" else "打球データが不足しており、守備位置の推奨はできません。")

    bip["spray_angle"] = np.degrees(np.arctan2(bip["hc_x"] - 125.42, 198.27 - bip["hc_y"]))
    if bats == "R":
        pull = (bip["spray_angle"] < -15).sum()
        oppo = (bip["spray_angle"] > 15).sum()
        pull_side = "3B side / left field" if lang == "EN" else "三塁側・レフト方向"
        oppo_side = "1B side / right field" if lang == "EN" else "一塁側・ライト方向"
    else:
        pull = (bip["spray_angle"] > 15).sum()
        oppo = (bip["spray_angle"] < -15).sum()
        pull_side = "1B side / right field" if lang == "EN" else "一塁側・ライト方向"
        oppo_side = "3B side / left field" if lang == "EN" else "三塁側・レフト方向"

    center = len(bip) - pull - oppo
    pull_pct = pull / len(bip) * 100
    oppo_pct = oppo / len(bip) * 100
    center_pct = center / len(bip) * 100

    bb = pdf.dropna(subset=["bb_type"])
    gb_pct = (bb["bb_type"] == "ground_ball").sum() / len(bb) * 100 if len(bb) >= 20 else None
    fb_pct = (bb["bb_type"] == "fly_ball").sum() / len(bb) * 100 if len(bb) >= 20 else None
    avg_ev = pdf["launch_speed"].dropna().mean() if pdf["launch_speed"].notna().any() else None

    if lang == "EN":
        lines.append("**Infield:**")
        if pull_pct >= 50:
            lines.append(f"- **Full pull shift recommended** — {pull_pct:.0f}% go to {pull_side}")
            if gb_pct and gb_pct >= 50:
                lines.append(f"- SS shades toward {pull_side} (GB hitter, {gb_pct:.0f}%)")
            else:
                lines.append(f"- 2B/SS shift pull-heavy")
        elif pull_pct >= 40:
            lines.append(f"- **Shade pull-side** — {pull_pct:.0f}% pull to {pull_side}")
            lines.append(f"- Standard depth, SS shades slightly toward {pull_side}")
        else:
            lines.append(f"- **Standard positioning** — balanced (Pull {pull_pct:.0f}% / Center {center_pct:.0f}% / Oppo {oppo_pct:.0f}%)")
        if gb_pct and gb_pct >= 55:
            lines.append(f"- **Play infield in** if situation allows — high GB rate ({gb_pct:.0f}%)")
        elif gb_pct and gb_pct < 35:
            lines.append(f"- Normal/deep depth — low GB rate ({gb_pct:.0f}%)")
        lines.append("")
        lines.append("**Outfield:**")
        if pull_pct >= 45:
            if avg_ev and avg_ev >= 90:
                lines.append(f"- Shift all OFs pull-heavy and deep (Avg EV {avg_ev:.1f} mph)")
            else:
                lines.append(f"- Shift outfielders pull-heavy toward {pull_side}")
        elif oppo_pct >= 35:
            lines.append(f"- Balanced — this hitter uses the whole field ({oppo_pct:.0f}% oppo)")
        else:
            lines.append(f"- Standard outfield alignment")
        if fb_pct and fb_pct >= 45:
            lines.append(f"- **Deep positioning** — fly ball hitter ({fb_pct:.0f}% FB)")
            if avg_ev and avg_ev >= 90:
                lines.append(f"- Warning: hard fly balls (Avg EV {avg_ev:.1f} mph)")
        elif fb_pct and fb_pct < 30:
            lines.append(f"- Can play slightly shallow — low FB rate ({fb_pct:.0f}%)")
    else:
        lines.append("**内野:**")
        if pull_pct >= 50:
            lines.append(f"- **フルシフト推奨** — 打球の{pull_pct:.0f}%が{pull_side}方向")
            if gb_pct and gb_pct >= 50:
                lines.append(f"- SSは{pull_side}に寄せる（ゴロ打者、{gb_pct:.0f}%）")
            else:
                lines.append(f"- 二遊間をプル方向にシフト")
        elif pull_pct >= 40:
            lines.append(f"- **プル側にやや寄せる** — 引っ張り{pull_pct:.0f}%（{pull_side}方向）")
            lines.append(f"- 標準深さ、SSは{pull_side}にやや寄せ")
        else:
            lines.append(f"- **標準配置** — バランス型（プル{pull_pct:.0f}% / センター{center_pct:.0f}% / 逆方向{oppo_pct:.0f}%）")
        if gb_pct and gb_pct >= 55:
            lines.append(f"- **前進守備も選択肢** — ゴロ率が高い（{gb_pct:.0f}%）")
        elif gb_pct and gb_pct < 35:
            lines.append(f"- 通常〜やや深めの守備位置 — ゴロ率が低い（{gb_pct:.0f}%）")
        lines.append("")
        lines.append("**外野:**")
        if pull_pct >= 45:
            if avg_ev and avg_ev >= 90:
                lines.append(f"- 全外野手をプル側＆深めに配置（強い打球、平均EV {avg_ev:.1f} mph）")
            else:
                lines.append(f"- 外野手を{pull_side}にシフト")
        elif oppo_pct >= 35:
            lines.append(f"- バランス配置 — 広角に打つ打者（逆方向{oppo_pct:.0f}%）")
        else:
            lines.append(f"- 標準的な外野配置")
        if fb_pct and fb_pct >= 45:
            lines.append(f"- **深めに守る** — フライ打者（{fb_pct:.0f}%）")
            if avg_ev and avg_ev >= 90:
                lines.append(f"- 注意: 強いフライが多い（平均EV {avg_ev:.1f} mph）")
        elif fb_pct and fb_pct < 30:
            lines.append(f"- やや浅めに守れる — フライ率が低い（{fb_pct:.0f}%）")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Visualization helpers
# ---------------------------------------------------------------------------
def dark_fig(figsize=(6, 5)):
    fig, ax = plt.subplots(figsize=figsize, facecolor="#0e1117")
    ax.set_facecolor("#1a1a2e")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_color("white")
    return fig, ax


def _zone_text_color(val: float, vmin: float, vmax: float) -> str:
    norm = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    if 0.25 < norm < 0.65:
        return "black"
    return "white"


def draw_zone_heatmap(df: pd.DataFrame, metric: str, title: str, ax,
                      lang: str = "EN"):
    """Draw a 5x5 heatmap over the strike zone."""
    x_bins = np.linspace(-1.5, 1.5, 6)
    z_bins = np.linspace(1.0, 4.0, 6)
    valid = df.dropna(subset=["plate_x", "plate_z"]).copy()

    if metric == "usage":
        total = len(valid)
        grid = np.full((5, 5), np.nan)
        for i in range(5):
            for j in range(5):
                mask = ((valid["plate_x"] >= x_bins[j]) & (valid["plate_x"] < x_bins[j + 1])
                        & (valid["plate_z"] >= z_bins[i]) & (valid["plate_z"] < z_bins[i + 1]))
                cell_count = mask.sum()
                if cell_count >= 3:
                    grid[i, j] = cell_count / total * 100
        vmin, vmax = 0, 10
        cmap = plt.cm.YlOrRd.copy()
    elif metric == "xwoba":
        valid = valid.dropna(subset=["estimated_woba_using_speedangle"])
        value_col = "estimated_woba_using_speedangle"
        grid = np.full((5, 5), np.nan)
        for i in range(5):
            for j in range(5):
                mask = ((valid["plate_x"] >= x_bins[j]) & (valid["plate_x"] < x_bins[j + 1])
                        & (valid["plate_z"] >= z_bins[i]) & (valid["plate_z"] < z_bins[i + 1]))
                cell = valid.loc[mask, value_col]
                if len(cell) >= 5:
                    grid[i, j] = cell.mean()
        vmin, vmax = 0.150, 0.500
        cmap = plt.cm.RdYlGn.copy()
    else:  # ba
        valid = valid[valid["events"].isin(_AB_EVENTS)]
        valid["is_hit"] = valid["events"].isin(_HIT_EVENTS).astype(int)
        grid = np.full((5, 5), np.nan)
        for i in range(5):
            for j in range(5):
                mask = ((valid["plate_x"] >= x_bins[j]) & (valid["plate_x"] < x_bins[j + 1])
                        & (valid["plate_z"] >= z_bins[i]) & (valid["plate_z"] < z_bins[i + 1]))
                cell = valid.loc[mask, "is_hit"]
                if len(cell) >= 5:
                    grid[i, j] = cell.mean()
        vmin, vmax = 0, 0.450
        cmap = plt.cm.RdYlGn.copy()

    cmap.set_bad(color="#222222")
    im = ax.pcolormesh(x_bins, z_bins, grid, cmap=cmap, vmin=vmin, vmax=vmax,
                       edgecolors="white", linewidth=0.5)
    rect = patches.Rectangle((-0.83, 1.5), 1.66, 2.0,
                              linewidth=2, edgecolor="black", facecolor="none")
    ax.add_patch(rect)
    for i in range(5):
        for j in range(5):
            val = grid[i, j]
            if not np.isnan(val):
                txt = f"{val:.1f}%" if metric == "usage" else f".{int(val * 1000):03d}"
                txt_color = _zone_text_color(val, vmin, vmax)
                ax.text((x_bins[j] + x_bins[j + 1]) / 2,
                        (z_bins[i] + z_bins[i + 1]) / 2,
                        txt, ha="center", va="center",
                        fontsize=9, fontweight="bold", color=txt_color,
                        path_effects=[pe.withStroke(linewidth=2,
                                                    foreground="white" if txt_color == "black" else "black")])
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(0.5, 4.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, fontweight="bold", color="white")
    ax.set_xlabel("Horizontal Position (ft)" if lang == "EN" else "横位置 (ft)", fontsize=14, color="white")
    ax.set_ylabel("Height (ft)" if lang == "EN" else "高さ (ft)", fontsize=14, color="white", labelpad=10)
    return im


def draw_zone_3x3(df: pd.DataFrame, metric: str, title: str, ax,
                   lang: str = "EN"):
    """Draw 3x3 zone chart using Statcast zone 1-9."""
    valid = df.dropna(subset=["zone"]).copy()
    valid["zone"] = valid["zone"].astype(int)
    x_edges = np.linspace(-0.83, 0.83, 4)
    z_edges = np.linspace(1.5, 3.5, 4)
    grid = np.full((3, 3), np.nan)
    zone_map = {1: (2, 0), 2: (2, 1), 3: (2, 2),
                4: (1, 0), 5: (1, 1), 6: (1, 2),
                7: (0, 0), 8: (0, 1), 9: (0, 2)}
    vmin, vmax = (0, 0.450) if metric == "ba" else (0.150, 0.500)
    for zone_num, (row, col) in zone_map.items():
        zdf = valid[valid["zone"] == zone_num]
        if metric == "ba":
            ab = zdf[zdf["events"].isin(_AB_EVENTS)]
            hits = zdf[zdf["events"].isin(_HIT_EVENTS)]
            if len(ab) >= 5:
                grid[row, col] = len(hits) / len(ab)
        else:
            vals = zdf["estimated_woba_using_speedangle"].dropna()
            if len(vals) >= 5:
                grid[row, col] = vals.mean()
    cmap = plt.cm.RdYlGn.copy()
    cmap.set_bad(color="#222222")
    im = ax.pcolormesh(x_edges, z_edges, grid, cmap=cmap, vmin=vmin, vmax=vmax,
                       edgecolors="white", linewidth=1.5)
    rect = patches.Rectangle((-0.83, 1.5), 1.66, 2.0,
                              linewidth=2, edgecolor="black", facecolor="none")
    ax.add_patch(rect)
    for zone_num, (row, col) in zone_map.items():
        val = grid[row, col]
        if not np.isnan(val):
            cx = (x_edges[col] + x_edges[col + 1]) / 2
            cz = (z_edges[row] + z_edges[row + 1]) / 2
            txt = f".{int(val * 1000):03d}"
            txt_color = _zone_text_color(val, vmin, vmax)
            ax.text(cx, cz, txt, ha="center", va="center",
                    fontsize=14, fontweight="bold", color=txt_color,
                    path_effects=[pe.withStroke(linewidth=2,
                                               foreground="white" if txt_color == "black" else "black")])
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(1.0, 4.0)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, fontweight="bold", color="white")
    ax.set_xlabel("Horizontal Position (ft)" if lang == "EN" else "横位置 (ft)", fontsize=14, color="white")
    ax.set_ylabel("Height (ft)" if lang == "EN" else "高さ (ft)", fontsize=14, color="white", labelpad=10)
    return im


def draw_spray_chart(df: pd.DataFrame, title: str, ax,
                     stadium: str = "marlins", density: bool = False,
                     lang: str = "EN"):
    """Draw spray chart on stadium outline."""
    stadium_df = load_stadium_coords()
    coords = stadium_df[stadium_df["team"] == stadium]
    if coords.empty:
        theta = np.linspace(-np.pi / 4, np.pi / 4, 100)
        fence_r = 250
        ax.plot(fence_r * np.sin(theta) + 125.42,
                198.27 - fence_r * np.cos(theta),
                color="white", linewidth=1.5)
    else:
        for segment in coords["segment"].unique():
            seg = coords[coords["segment"] == segment]
            path = mpath.Path(seg[["x", "y"]].values)
            patch = patches.PathPatch(path, facecolor="none", edgecolor="white",
                                      lw=1.5, zorder=1)
            ax.add_patch(patch)

    valid = df.dropna(subset=["hc_x", "hc_y", "events"]).copy()
    color_map = {"home_run": "#e53935", "triple": "#ff9800",
                 "double": "#ff9800", "single": "#4caf50"}
    valid["color"] = valid["events"].map(color_map).fillna("#888888")
    valid["zorder"] = valid["events"].apply(
        lambda x: 5 if x == "home_run" else (4 if x in ("double", "triple") else 3))

    if density and len(valid) >= 10:
        try:
            xy = np.vstack([valid["hc_x"].values, valid["hc_y"].values])
            kde = gaussian_kde(xy, bw_method=0.15)
            xg = np.linspace(0, 250, 200)
            yg = np.linspace(-20, 220, 200)
            xx, yy = np.meshgrid(xg, yg)
            zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
            ax.contourf(xx, yy, zz, levels=10, cmap="YlOrRd", alpha=0.35, zorder=2)
        except np.linalg.LinAlgError:
            pass

    for _, row in valid.iterrows():
        ax.scatter(row["hc_x"], row["hc_y"], c=row["color"], s=18, alpha=0.7,
                   edgecolors="none", zorder=row["zorder"])

    ax.set_xlim(0, 250)
    ax.set_ylim(220, -20)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, fontweight="bold", color="white")
    ax.axis("off")

    if lang == "JA":
        legend_labels = [("本塁打", "#e53935"), ("長打", "#ff9800"),
                         ("単打", "#4caf50"), ("アウト", "#888888")]
    else:
        legend_labels = [("Home Run", "#e53935"), ("Extra-base Hit", "#ff9800"),
                         ("Single", "#4caf50"), ("Out", "#888888")]
    for label, color in legend_labels:
        ax.scatter([], [], c=color, s=30, label=label)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.6)


def draw_movement_chart(df: pd.DataFrame, title: str, ax,
                        density: bool = True):
    """Draw pitch movement chart (horizontal vs vertical break)."""
    valid = df.dropna(subset=["pfx_x", "pfx_z", "pitch_type"]).copy()
    valid["pfx_x_in"] = valid["pfx_x"] * 12
    valid["pfx_z_in"] = valid["pfx_z"] * 12
    top_types = valid["pitch_type"].value_counts().head(8).index

    if density:
        for pt in top_types:
            sub = valid[valid["pitch_type"] == pt]
            if len(sub) < 20:
                continue
            try:
                xy = np.vstack([sub["pfx_x_in"].values, sub["pfx_z_in"].values])
                kde = gaussian_kde(xy, bw_method=0.3)
                xmin, xmax = sub["pfx_x_in"].min(), sub["pfx_x_in"].max()
                zmin, zmax = sub["pfx_z_in"].min(), sub["pfx_z_in"].max()
                xg = np.linspace(xmin, xmax, 80)
                yg = np.linspace(zmin, zmax, 80)
                xx, yy = np.meshgrid(xg, yg)
                zz = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
                color = PITCH_COLORS.get(pt, "#AAAAAA")
                ax.contour(xx, yy, zz, levels=3, colors=[color], alpha=0.6,
                           linewidths=1.5, zorder=1)
            except np.linalg.LinAlgError:
                pass

    for pt in top_types:
        sub = valid[valid["pitch_type"] == pt]
        color = PITCH_COLORS.get(pt, "#AAAAAA")
        label = PITCH_LABELS.get(pt, pt)
        ax.scatter(sub["pfx_x_in"], sub["pfx_z_in"],
                   c=color, s=15, alpha=0.5, label=label, edgecolors="none", zorder=3)

    ax.axhline(0, color="white", linewidth=0.5, alpha=0.3)
    ax.axvline(0, color="white", linewidth=0.5, alpha=0.3)
    ax.set_xlabel("Horizontal Break (in)", color="white", fontsize=14)
    ax.set_ylabel("Induced Vertical Break (in)", color="white", fontsize=14)
    ax.set_title(title, fontsize=16, fontweight="bold", color="white")
    leg = ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=12,
                    facecolor="#0e1117", edgecolor="white",
                    labelspacing=1.0, borderpad=1.0,
                    markerscale=3.0, handletextpad=0.8)
    for text in leg.get_texts():
        text.set_color("white")
    ax.tick_params(colors="white")


def draw_radar_chart(categories: list, values: list, mlb_values: list,
                     raw_labels: list, label: str, lang: str = "EN"):
    """Draw a radar chart comparing player/team values to MLB average."""
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    v_plot = values + [values[0]]
    m_plot = mlb_values + [mlb_values[0]]
    a_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True),
                           facecolor="#0e1117")
    ax.set_facecolor("#0e1117")
    ax.plot(a_plot, m_plot, "--", linewidth=1.5, color="#888888", alpha=0.7, label="MLB avg")
    ax.fill(a_plot, m_plot, alpha=0.08, color="#888888")
    ax.plot(a_plot, v_plot, "o-", linewidth=2, color="#4fc3f7", label=label)
    ax.fill(a_plot, v_plot, alpha=0.25, color="#4fc3f7")
    ax.set_thetagrids(np.degrees(angles), categories, color="white", fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["", "", "", ""], color="white")
    ax.grid(color="gray", alpha=0.3)
    ax.spines["polar"].set_color("gray")
    for angle, val, raw in zip(angles, values, raw_labels):
        ax.annotate(raw, xy=(angle, val), fontsize=9,
                    ha="center", va="bottom", color="white", fontweight="bold")
    leg = ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1),
                    fontsize=9, facecolor="#0e1117", edgecolor="gray")
    for txt in leg.get_texts():
        txt.set_color("white")
    fig.tight_layout()
    return fig


def batter_radar_values(stats: dict) -> tuple:
    """Compute normalized radar values and raw labels for a batter."""
    values = [
        min(stats["AVG"] / 0.300, 1.0),
        min(stats["OBP"] / 0.380, 1.0),
        min(stats["SLG"] / 0.500, 1.0),
        1.0 - min(stats["K%"] / 35.0, 1.0),
        min(stats["BB%"] / 15.0, 1.0),
    ]
    mlb = [
        min(_MLB_AVG_BAT["AVG"] / 0.300, 1.0),
        min(_MLB_AVG_BAT["OBP"] / 0.380, 1.0),
        min(_MLB_AVG_BAT["SLG"] / 0.500, 1.0),
        1.0 - min(_MLB_AVG_BAT["K%"] / 35.0, 1.0),
        min(_MLB_AVG_BAT["BB%"] / 15.0, 1.0),
    ]
    raw = [f"{stats['AVG']:.3f}", f"{stats['OBP']:.3f}", f"{stats['SLG']:.3f}",
           f"{stats['K%']:.1f}%", f"{stats['BB%']:.1f}%"]
    return values, mlb, raw


def pitcher_radar_values(stats: dict) -> tuple:
    """Compute normalized radar values and raw labels for a pitcher."""
    values = [
        min(stats["K%"] / 35.0, 1.0),
        min(stats["Whiff%"] / 40.0, 1.0),
        1.0 - min(stats["BB%"] / 15.0, 1.0),
        1.0 - min(stats["Opp AVG"] / 0.300, 1.0),
        min(stats["Avg Velo"] / 100.0, 1.0) if stats["Avg Velo"] else 0.5,
    ]
    mlb = [
        min(_MLB_AVG_PIT["K%"] / 35.0, 1.0),
        min(_MLB_AVG_PIT["Whiff%"] / 40.0, 1.0),
        1.0 - min(_MLB_AVG_PIT["BB%"] / 15.0, 1.0),
        1.0 - min(_MLB_AVG_PIT["Opp AVG"] / 0.300, 1.0),
        min(_MLB_AVG_PIT["Velo"] / 100.0, 1.0),
    ]
    raw = [f"{stats['K%']:.1f}%", f"{stats['Whiff%']:.1f}%",
           f"{stats['BB%']:.1f}%", f".{int(stats['Opp AVG']*1000):03d}",
           f"{stats['Avg Velo']:.1f}" if stats["Avg Velo"] else "—"]
    return values, mlb, raw


# ---------------------------------------------------------------------------
# Table builders
# ---------------------------------------------------------------------------
def pitch_type_table(df: pd.DataFrame, t) -> pd.DataFrame:
    """Build pitch-type performance table for a batter."""
    valid = df.dropna(subset=["pitch_type"]).copy()
    top_types = valid["pitch_type"].value_counts().head(8).index
    valid.loc[~valid["pitch_type"].isin(top_types), "pitch_type"] = "Other"

    rows = []
    for pt, grp in valid.groupby("pitch_type"):
        n_pitches = len(grp)
        swings = grp[grp["description"].isin({
            "hit_into_play", "foul", "swinging_strike",
            "swinging_strike_blocked", "foul_tip", "foul_bunt",
            "missed_bunt", "bunt_foul_tip",
        })]
        whiffs = grp[grp["description"].isin({
            "swinging_strike", "swinging_strike_blocked", "foul_tip",
        })]
        whiff_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0
        outside = grp[(grp["zone"].notna()) & (grp["zone"] >= 11)]
        chase_swings = outside[outside["description"].isin({
            "hit_into_play", "foul", "swinging_strike",
            "swinging_strike_blocked", "foul_tip",
        })]
        chase_pct = len(chase_swings) / len(outside) * 100 if len(outside) > 0 else 0
        ab = grp[grp["events"].isin(_AB_EVENTS)]
        hits = grp[grp["events"].isin(_HIT_EVENTS)]
        n_ab = len(ab)
        n_h = len(hits)
        n_1b = len(hits[hits["events"] == "single"])
        n_2b = len(hits[hits["events"] == "double"])
        n_3b_h = len(hits[hits["events"] == "triple"])
        n_hr = len(hits[hits["events"] == "home_run"])
        tb = n_1b + 2 * n_2b + 3 * n_3b_h + 4 * n_hr
        ba = n_h / n_ab if n_ab >= 10 else None
        slg = tb / n_ab if n_ab >= 10 else None
        label = PITCH_LABELS.get(pt, pt)
        rows.append({
            t["pitch_type"]: label,
            t["count"]: n_pitches,
            t["ba"]: f".{int(ba * 1000):03d}" if ba is not None else "—",
            t["slg"]: f".{int(slg * 1000):03d}" if slg is not None else "—",
            t["whiff_pct"]: f"{whiff_pct:.1f}%",
            t["chase_pct"]: f"{chase_pct:.1f}%",
        })

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values(t["count"], ascending=False).reset_index(drop=True)
    return result


def arsenal_table(df: pd.DataFrame, t) -> pd.DataFrame:
    """Build pitch arsenal table for a pitcher."""
    valid = df.dropna(subset=["pitch_type"]).copy()
    top_types = valid["pitch_type"].value_counts().head(8).index
    valid.loc[~valid["pitch_type"].isin(top_types), "pitch_type"] = "Other"

    total = len(valid)
    rows = []
    for pt, grp in valid.groupby("pitch_type"):
        n_pitches = len(grp)
        usage = n_pitches / total * 100
        avg_velo = grp["release_speed"].dropna().mean() if "release_speed" in grp.columns else None
        max_velo = grp["release_speed"].dropna().max() if "release_speed" in grp.columns else None
        avg_spin = grp["release_spin_rate"].dropna().mean() if "release_spin_rate" in grp.columns else None
        h_break = grp["pfx_x"].dropna().mean() * 12 if "pfx_x" in grp.columns and grp["pfx_x"].notna().any() else None
        v_break = grp["pfx_z"].dropna().mean() * 12 if "pfx_z" in grp.columns and grp["pfx_z"].notna().any() else None
        swings = grp[grp["description"].isin({
            "hit_into_play", "foul", "swinging_strike",
            "swinging_strike_blocked", "foul_tip",
        })]
        whiffs = grp[grp["description"].isin({
            "swinging_strike", "swinging_strike_blocked", "foul_tip",
        })]
        whiff_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0
        two_strike = grp[grp["strikes"] == 2]
        k_on_two = two_strike[two_strike["events"].str.contains("strikeout", na=False)] if "events" in two_strike.columns else pd.DataFrame()
        put_away = len(k_on_two) / len(two_strike) * 100 if len(two_strike) > 0 else 0
        label = PITCH_LABELS.get(pt, pt)
        rows.append({
            t["pitch_type"]: label,
            t["count"]: n_pitches,
            t["usage_pct"]: f"{usage:.1f}%",
            t["avg_velo"]: f"{avg_velo:.1f} / {avg_velo * 1.609:.0f}" if avg_velo and not pd.isna(avg_velo) else "—",
            t["max_velo"]: f"{max_velo:.1f} / {max_velo * 1.609:.0f}" if max_velo and not pd.isna(max_velo) else "—",
            t["avg_spin"]: f"{avg_spin:.0f}" if avg_spin and not pd.isna(avg_spin) else "—",
            t["h_break"]: f"{h_break:.1f}" if h_break is not None else "—",
            t["v_break"]: f"{v_break:.1f}" if v_break is not None else "—",
            t["whiff_pct"]: f"{whiff_pct:.1f}%",
            t["put_away_pct"]: f"{put_away:.1f}%",
        })

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values(t["count"], ascending=False).reset_index(drop=True)
    return result


def batted_ball_profile(df: pd.DataFrame, t) -> dict:
    """Pull/Center/Oppo, GB/LD/FB, avg EV/LA."""
    bip = df.dropna(subset=["hc_x", "hc_y"]).copy()
    n = len(bip)
    if n == 0:
        return {}
    bip["spray_angle"] = np.degrees(
        np.arctan2(bip["hc_x"] - 125.42, 198.27 - bip["hc_y"]))
    stand = bip["stand"].mode().iloc[0] if len(bip["stand"].mode()) > 0 else "R"
    if stand == "R":
        pull = bip["spray_angle"] < -15
        oppo = bip["spray_angle"] > 15
    else:
        pull = bip["spray_angle"] > 15
        oppo = bip["spray_angle"] < -15
    center = ~pull & ~oppo
    bb = df.dropna(subset=["bb_type"])
    n_bb = len(bb)
    return {
        t["pull_pct"]: f"{pull.sum() / n * 100:.1f}%",
        t["cent_pct"]: f"{center.sum() / n * 100:.1f}%",
        t["oppo_pct"]: f"{oppo.sum() / n * 100:.1f}%",
        t["gb_pct"]: f"{(bb['bb_type'] == 'ground_ball').sum() / n_bb * 100:.1f}%" if n_bb else "—",
        t["ld_pct"]: f"{(bb['bb_type'] == 'line_drive').sum() / n_bb * 100:.1f}%" if n_bb else "—",
        t["fb_pct"]: f"{(bb['bb_type'] == 'fly_ball').sum() / n_bb * 100:.1f}%" if n_bb else "—",
        t["avg_ev"]: f"{df['launch_speed'].dropna().mean():.1f}" if df["launch_speed"].notna().any() else "—",
        t["avg_la"]: f"{df['launch_angle'].dropna().mean():.1f}" if df["launch_angle"].notna().any() else "—",
    }


def count_category(balls: int, strikes: int) -> str:
    if balls > strikes:
        return "ahead"
    elif strikes > balls:
        return "behind"
    return "even"


def draw_pitch_selection_pies(df: pd.DataFrame, t, lang: str,
                              st_container=None):
    """Draw pie charts for pitch selection by count situation."""
    container = st_container or st

    valid = df.dropna(subset=["pitch_type", "balls", "strikes"]).copy()
    if valid.empty:
        return
    valid["balls"] = valid["balls"].astype(int)
    valid["strikes"] = valid["strikes"].astype(int)

    situations = [
        (t["count_first_pitch"], valid[(valid["balls"] == 0) & (valid["strikes"] == 0)]),
        (t["count_ahead_pitcher"], valid[valid["strikes"] > valid["balls"]]),
        (t["count_behind_pitcher"], valid[valid["balls"] > valid["strikes"]]),
        (t["count_even_pitcher"], valid[(valid["balls"] == valid["strikes"]) & (valid["balls"] > 0)]),
        (t["count_two_strikes"], valid[valid["strikes"] == 2]),
    ]
    situations = [(name, sdf) for name, sdf in situations if not sdf.empty]
    if not situations:
        return

    idx = 0
    while idx < len(situations):
        batch = situations[idx:idx + 3]
        cols = container.columns(len(batch))
        for col, (sit_name, sit_df) in zip(cols, batch):
            with col:
                total = len(sit_df)
                counts = sit_df["pitch_type"].value_counts()
                labels = [PITCH_LABELS.get(pt, pt) for pt in counts.index]
                colors = [PITCH_COLORS.get(pt, "#AAAAAA") for pt in counts.index]
                sizes = counts.values

                fig_pie, ax_pie = plt.subplots(figsize=(3.5, 3.5), facecolor="#0e1117")
                wedges, texts, autotexts = ax_pie.pie(
                    sizes, labels=None, colors=colors, autopct="",
                    startangle=90, pctdistance=0.75,
                    wedgeprops=dict(width=0.45, edgecolor="#0e1117", linewidth=1.5))
                for i, (w, val) in enumerate(zip(wedges, sizes)):
                    pct = val / total * 100
                    if pct >= 5:
                        ang = (w.theta2 - w.theta1) / 2.0 + w.theta1
                        x = np.cos(np.radians(ang)) * 0.55
                        y = np.sin(np.radians(ang)) * 0.55
                        ax_pie.text(x, y, f"{pct:.0f}%", ha="center", va="center",
                                    fontsize=11, fontweight="bold", color="white")
                ax_pie.set_title(f"{sit_name}\n(n={total})", color="white",
                                 fontsize=13, fontweight="bold", pad=8)
                legend = ax_pie.legend(
                    wedges, labels, loc="center", bbox_to_anchor=(0.5, -0.08),
                    ncol=min(3, len(labels)), fontsize=9,
                    facecolor="#0e1117", edgecolor="gray", framealpha=0.9)
                for txt in legend.get_texts():
                    txt.set_color("white")
                fig_pie.tight_layout()
                col.pyplot(fig_pie, use_container_width=True)
                plt.close(fig_pie)
        idx += 3


# ---------------------------------------------------------------------------
# Team weakness analysis
# ---------------------------------------------------------------------------
def analyze_team_weaknesses(player_stats_list: list, lang: str) -> str:
    """Auto-detect team-level weaknesses from batter stats."""
    lines = []

    # High K% batters
    high_k = [ps for ps in player_stats_list if ps["PA"] >= 50 and ps["K%"] >= 22.4]
    if high_k:
        header = "**High K% batters (≥22.4% MLB avg):**" if lang == "EN" else "**三振率が高い打者（≥22.4% MLB平均）:**"
        lines.append(header)
        for ps in sorted(high_k, key=lambda x: x["K%"], reverse=True):
            lines.append(f"- {ps['name']}: K% {ps['K%']:.1f}%")

    # Low BB% batters
    low_bb = [ps for ps in player_stats_list if ps["PA"] >= 50 and ps["BB%"] < 7.0]
    if low_bb:
        header = "**Low BB% batters (<7%):**" if lang == "EN" else "**四球率が低い打者（<7%）:**"
        lines.append(header)
        for ps in sorted(low_bb, key=lambda x: x["BB%"]):
            lines.append(f"- {ps['name']}: BB% {ps['BB%']:.1f}%")

    # Platoon vulnerability
    platoon_weak = [ps for ps in player_stats_list
                    if ps.get("platoon_diff") and ps["platoon_diff"] >= 80]
    if platoon_weak:
        header = "**Platoon vulnerability (OPS diff ≥80 pts):**" if lang == "EN" else "**左右差が大きい打者（OPS差≥80pts）:**"
        lines.append(header)
        for ps in sorted(platoon_weak, key=lambda x: x["platoon_diff"], reverse=True):
            weak = ps.get("platoon_weak_side", "?")
            lines.append(f"- {ps['name']}: weaker vs {weak} (diff {ps['platoon_diff']:.0f} pts)"
                         if lang == "EN" else
                         f"- {ps['name']}: {weak}に弱い（差 {ps['platoon_diff']:.0f} pts）")

    if not lines:
        return ("No significant team-level weaknesses detected."
                if lang == "EN" else "チーム全体で顕著な弱点は検出されませんでした。")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Premium CSS theme
# ---------------------------------------------------------------------------
PREMIUM_CSS = """
<style>
/* ============================================
   WBC 2026 — Premium Dark Theme
   ============================================ */
.stApp { background-color: #0a0a1a; }

/* --- Metric Cards --- */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #141428 0%, #1a1a35 100%);
    border: 1px solid #2a2a4a;
    border-radius: 10px;
    padding: 14px 16px;
    transition: border-color 0.2s ease;
}
[data-testid="stMetric"]:hover { border-color: #e94560; }
[data-testid="stMetricLabel"] {
    color: #8892b0 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: #ccd6f6 !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}

/* --- Tabs --- */
[data-testid="stTabs"] > div:first-child {
    background: linear-gradient(90deg, #0f0f23, #141432, #0f0f23);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
[data-testid="stTabs"] button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 8px 20px !important;
    color: #8892b0 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #e94560, #c23152) !important;
    color: #ffffff !important;
}
[data-testid="stTabs"] button:hover:not([aria-selected="true"]) {
    background: #1a1a35 !important;
    color: #ccd6f6 !important;
}

/* --- Expanders --- */
[data-testid="stExpander"] {
    border: 1px solid #2a2a4a;
    border-radius: 10px;
    background: #0e0e20;
    margin-bottom: 8px;
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    padding: 10px 14px;
}
[data-testid="stExpander"] summary:hover { color: #e94560 !important; }

/* --- DataFrames --- */
.stDataFrame { border-radius: 8px; overflow: hidden; }
.stDataFrame [data-testid="glideDataEditor"] th,
.stDataFrame thead th {
    background: linear-gradient(135deg, #1a1a40, #0f3460) !important;
    color: #e6f1ff !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border-bottom: 2px solid #e94560 !important;
}

/* --- Selectbox --- */
[data-testid="stSelectbox"] > div > div {
    border-color: #2a2a4a !important;
    border-radius: 8px !important;
    background: #141428 !important;
}

hr { border-color: #1a1a35 !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a1a 0%, #0f0f23 100%) !important;
    border-right: 1px solid #1a1a35;
}

/* --- Player card header --- */
.player-card-header {
    background: linear-gradient(135deg, #141432 0%, #1a1a40 40%, #0f3460 100%);
    border-left: 4px solid #e94560;
    border-radius: 10px;
    padding: 14px 20px;
    margin: 20px 0 6px 0;
    box-shadow: 0 4px 15px rgba(233, 69, 96, 0.08);
}

/* --- Hero banner --- */
.hero-banner {
    background: linear-gradient(135deg, #0f0f23 0%, #141432 30%, #1a1a40 60%, #0f3460 100%);
    border: 1px solid #2a2a4a;
    border-radius: 14px;
    padding: 28px 32px;
    text-align: center;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #e94560, #4fc3f7, #e94560);
}
.hero-banner .hero-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #e6f1ff;
    margin: 8px 0 4px 0;
}
.hero-banner .hero-sub {
    font-size: 0.95rem;
    color: #8892b0;
    margin: 0;
}
.hero-banner .hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, #e94560, #c23152);
    color: white;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 10px;
}

/* --- Responsive --- */
@media (max-width: 768px) {
    [data-testid="stMetric"] { padding: 0.3rem 0.4rem; }
    [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
    [data-testid="stHorizontalBlock"] { gap: 0.3rem !important; }
    .stDataFrame td, .stDataFrame th { font-size: 0.8rem !important; }
}
</style>
"""
