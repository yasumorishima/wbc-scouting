"""WBC 2026 Dominican Republic Pitching Scouting Dashboard."""

import pathlib

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import matplotlib_fontja  # noqa: F401 — enables Japanese font
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import gaussian_kde

from players_dr_pitchers import DR_PITCHERS, PITCHER_BY_NAME

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
TEXTS = {
    "EN": {
        "title": "Dominican Republic Pitching Scouting Report",
        "subtitle": "WBC 2026 — Projected Opponent Pitching Analysis",
        "select_pitcher": "Select Pitcher",
        "team_overview": "Staff Overview",
        "season": "Season",
        "all_seasons": "All",
        "profile": "Pitcher Profile",
        "team": "Team",
        "throws": "Throws",
        "role": "Role",
        "arsenal": "Pitch Arsenal",
        "pitch_type": "Pitch Type",
        "count": "Count",
        "usage_pct": "Usage%",
        "avg_velo": "Avg Velo (mph)",
        "max_velo": "Max Velo (mph)",
        "avg_spin": "Avg Spin (rpm)",
        "h_break": "H-Break (in)",
        "v_break": "V-Break (in)",
        "whiff_pct": "Whiff%",
        "put_away_pct": "Put Away%",
        "zone_heatmap": "Pitch Location Heatmap",
        "usage_heatmap": "Usage by Zone",
        "ba_heatmap": "Opp BA by Zone",
        "batted_ball": "Batted Ball Against",
        "gb_pct": "GB%",
        "ld_pct": "LD%",
        "fb_pct": "FB%",
        "avg_ev": "Avg EV Against (mph)",
        "avg_la": "Avg LA Against (deg)",
        "platoon": "Platoon Splits",
        "vs_lhb": "vs LHB",
        "vs_rhb": "vs RHB",
        "count_perf": "Performance by Count",
        "ahead": "Pitcher Ahead (S > B)",
        "behind": "Pitcher Behind (B > S)",
        "even": "Even (B = S)",
        "no_data": "No data available for this selection.",
        "danger_zone": "Red = high opp BA (danger), Blue = low opp BA (attack)",
        "sp": "Starter",
        "rp": "Reliever",
        "velo_spin": "Velocity & Spin Profile",
        "movement_chart": "Pitch Movement Chart",
        "pitches": "Pitches",
        "k_pct": "K%",
        "bb_pct": "BB%",
        "opp_avg": "Opp AVG",
        "opp_slg": "Opp SLG",
        "xwoba_against": "xwOBA Against",
        "zone_3x3": "Zone Chart (3×3)",
        "team_strengths": "Staff Strengths & Weaknesses",
        "strength_note": (
            "The Dominican Republic features a deep and versatile pitching staff. "
            "The rotation is led by Sandy Alcantara, Brayan Bello, and Luis Severino, "
            "all power arms with plus stuff. The bullpen is loaded with high-velocity relievers "
            "such as Camilo Doval, Carlos Estevez, and Abner Uribe. "
            "Key vulnerabilities: some relievers have elevated walk rates, "
            "and the staff is predominantly right-handed — "
            "left-handed depth is limited to Wandy Peralta, Cristopher Sanchez, and Gregory Soto."
        ),
        "overview_guide": (
            "Select a pitcher from the sidebar to see their detailed scouting report: "
            "pitch arsenal, movement chart, zone heatmaps, platoon splits, and count-by-count performance."
        ),
        "count_explain": (
            "Pitcher Ahead = strike count > ball count (e.g. 0-2, 1-2). "
            "Pitcher Behind = ball count > strike count (e.g. 2-0, 3-1). "
            "Even = same count (e.g. 1-1, 2-2)."
        ),
        "glossary_stats": (
            "**Opp AVG** = Opponents' batting average | "
            "**Opp SLG** = Opponents' slugging percentage | "
            "**K%** = Strikeout rate (strikeouts / plate appearances) | "
            "**BB%** = Walk rate (walks / plate appearances) | "
            "**xwOBA Against** = Expected weighted on-base average allowed (batted ball quality)"
        ),
        "glossary_arsenal": (
            "**Usage%** = How often this pitch is thrown | "
            "**Avg Velo** = Average velocity (mph) | "
            "**Avg Spin** = Average spin rate (rpm) | "
            "**H-Break** = Horizontal movement (inches, glove side positive) | "
            "**V-Break** = Induced vertical break (inches) | "
            "**Whiff%** = Swing-and-miss rate | "
            "**Put Away%** = Rate of strikeouts when pitching with 2 strikes"
        ),
        "glossary_batted": (
            "**GB%** = Ground ball rate | **LD%** = Line drive rate | **FB%** = Fly ball rate | "
            "**Avg EV Against** = Average exit velocity allowed (mph) | "
            "**Avg LA Against** = Average launch angle allowed (degrees)"
        ),
        "glossary_platoon": (
            "Platoon splits show how a pitcher performs against left-handed batters (LHB) "
            "vs right-handed batters (RHB). Large differences reveal matchup vulnerabilities."
        ),
        "glossary_movement": (
            "Each dot represents a pitch. Horizontal axis = glove-side break, "
            "vertical axis = induced vertical break. Pitches are colored by type."
        ),
        "pitcher_summary": "Scouting Summary",
        "pitch_filter": "Filter by pitch type",
        "all_pitches": "All Pitches",
        "count_pitch_mix": "Pitch Mix by Count",
    },
    "JA": {
        "title": "ドミニカ共和国 投手スカウティングレポート",
        "subtitle": "WBC 2026 — 対戦相手投手分析（想定）",
        "select_pitcher": "投手を選択",
        "team_overview": "投手陣概要",
        "season": "シーズン",
        "all_seasons": "全シーズン",
        "profile": "投手プロフィール",
        "team": "チーム",
        "throws": "投",
        "role": "役割",
        "arsenal": "球種構成",
        "pitch_type": "球種",
        "count": "投球数",
        "usage_pct": "使用率",
        "avg_velo": "平均球速 (mph)",
        "max_velo": "最高球速 (mph)",
        "avg_spin": "平均回転数 (rpm)",
        "h_break": "横変化 (in)",
        "v_break": "縦変化 (in)",
        "whiff_pct": "空振率",
        "put_away_pct": "決め球率",
        "zone_heatmap": "配球ヒートマップ",
        "usage_heatmap": "ゾーン別投球分布",
        "ba_heatmap": "ゾーン別 被打率",
        "batted_ball": "被打球傾向",
        "gb_pct": "ゴロ%",
        "ld_pct": "ライナー%",
        "fb_pct": "フライ%",
        "avg_ev": "被平均打球速度 (mph)",
        "avg_la": "被平均打球角度 (度)",
        "platoon": "左右打者別成績",
        "vs_lhb": "vs 左打者",
        "vs_rhb": "vs 右打者",
        "count_perf": "カウント別パフォーマンス",
        "ahead": "投手有利 (S > B)",
        "behind": "投手不利 (B > S)",
        "even": "イーブン (B = S)",
        "no_data": "このフィルターではデータがありません。",
        "danger_zone": "赤 = 高被打率（危険）、青 = 低被打率（攻めどころ）",
        "sp": "先発",
        "rp": "リリーフ",
        "velo_spin": "球速・回転数プロフィール",
        "movement_chart": "変化量チャート",
        "pitches": "投球数",
        "k_pct": "奪三振率",
        "bb_pct": "与四球率",
        "opp_avg": "被打率",
        "opp_slg": "被長打率",
        "xwoba_against": "被xwOBA",
        "zone_3x3": "ゾーンチャート (3×3)",
        "team_strengths": "投手陣の強み・弱み",
        "strength_note": (
            "ドミニカ共和国は層の厚い投手陣を誇る。"
            "先発はアルカンタラ・ベロ・セベリーノとパワーアームが揃い、"
            "リリーフもドバル・エステベス・ウリベなど高球速の投手が充実。\n\n"
            "弱点: 一部のリリーフは与四球率が高い傾向がある。"
            "また投手陣は右腕に偏りがあり、"
            "左腕はペラルタ・C.サンチェス・ソトの3人に限られる。"
        ),
        "overview_guide": (
            "左のサイドバーから投手を選ぶと、個人の詳細スカウティングレポートを表示します: "
            "球種構成、変化量チャート、ゾーン別ヒートマップ、左右打者別成績など。"
        ),
        "count_explain": (
            "投手有利 = ストライク数 > ボール数（例: 0-2, 1-2）。"
            "投手不利 = ボール数 > ストライク数（例: 2-0, 3-1）。"
            "イーブン = 同数（例: 1-1, 2-2）。"
        ),
        "glossary_stats": (
            "**被打率（Opp AVG）** = 対戦打者の打率 | "
            "**被長打率（Opp SLG）** = 対戦打者の長打率 | "
            "**奪三振率（K%）** = 打席あたりの三振を奪う割合 | "
            "**与四球率（BB%）** = 打席あたりの四球を与える割合 | "
            "**被xwOBA** = 打球の質から算出した期待被出塁率（低いほど良い）"
        ),
        "glossary_arsenal": (
            "**使用率** = その球種を投げる割合 | "
            "**平均球速** = 平均的な球の速さ (mph) | "
            "**平均回転数** = 球の回転の速さ (rpm) | "
            "**横変化** = グラブ側への横の曲がり幅（インチ） | "
            "**縦変化** = 重力に逆らう縦の変化量（インチ） | "
            "**空振率（Whiff%）** = スイングに対する空振りの割合 | "
            "**決め球率（Put Away%）** = 2ストライクから三振を奪う割合"
        ),
        "glossary_batted": (
            "**ゴロ%** = ゴロの割合 | **ライナー%** = ライナーの割合 | **フライ%** = フライの割合 | "
            "**被平均打球速度** = 打たれた打球のスピード (mph) | "
            "**被平均打球角度** = 打たれた打球の角度"
        ),
        "glossary_platoon": (
            "左右打者別成績は、左打者（LHB）と右打者（RHB）に対する投球成績です。"
            "左右で成績に大きな差がある投手は、苦手な打席の打者を並べられると不利になります。"
        ),
        "glossary_movement": (
            "各ドットが1球を表します。横軸 = グラブ側への曲がり、"
            "縦軸 = 重力に逆らう縦の変化量。球種ごとに色分けされています。"
        ),
        "pitcher_summary": "スカウティング要約",
        "pitch_filter": "球種で絞り込み",
        "all_pitches": "全球種",
        "count_pitch_mix": "カウント別 球種配分",
    },
}

PITCH_LABELS = {
    "FF": "4-Seam",
    "SI": "Sinker",
    "FC": "Cutter",
    "SL": "Slider",
    "CU": "Curveball",
    "CH": "Changeup",
    "FS": "Splitter",
    "KC": "Knuckle Curve",
    "ST": "Sweeper",
    "SV": "Slurve",
}

PITCH_COLORS = {
    "FF": "#FF6347", "SI": "#FF8C00", "FC": "#DAA520",
    "SL": "#4169E1", "CU": "#9370DB", "CH": "#2E8B57",
    "FS": "#20B2AA", "KC": "#BA55D3", "ST": "#1E90FF",
    "SV": "#7B68EE",
}

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent / "data" / "dr_pitchers_statcast.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    df["game_date"] = pd.to_datetime(df["game_date"])
    if "season" not in df.columns:
        df["season"] = df["game_date"].dt.year
    return df


def filter_season(df: pd.DataFrame, season) -> pd.DataFrame:
    if season == "All":
        return df
    return df[df["season"] == int(season)]


# ---------------------------------------------------------------------------
# Pitching stats helpers
# ---------------------------------------------------------------------------
def pitching_stats(df: pd.DataFrame) -> dict:
    """Compute pitching stats from Statcast pitch-level data."""
    total_pitches = len(df)
    evts = df.dropna(subset=["events"])

    ab_events = {"single", "double", "triple", "home_run", "field_out",
                 "strikeout", "grounded_into_double_play", "double_play",
                 "force_out", "fielders_choice", "fielders_choice_out",
                 "strikeout_double_play", "triple_play", "field_error"}
    pa_events = ab_events | {"walk", "hit_by_pitch", "sac_fly", "sac_bunt",
                             "sac_fly_double_play", "catcher_interf",
                             "intent_walk"}
    hit_events = {"single", "double", "triple", "home_run"}

    pa = evts[evts["events"].isin(pa_events)]
    ab = evts[evts["events"].isin(ab_events)]
    hits = evts[evts["events"].isin(hit_events)]

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

    return {
        "Pitches": total_pitches,
        "PA": n_pa, "K": n_k, "BB": n_bb, "HR": n_hr,
        "Opp AVG": round(opp_avg, 3),
        "Opp SLG": round(opp_slg, 3),
        "K%": round(k_pct, 1),
        "BB%": round(bb_pct, 1),
        "xwOBA": round(xwoba, 3) if not pd.isna(xwoba) else None,
        "Avg Velo": round(avg_velo, 1) if avg_velo and not pd.isna(avg_velo) else None,
    }


def generate_pitcher_summary(stats: dict, pdf: pd.DataFrame, pitcher: dict,
                             lang: str) -> str:
    """Auto-generate a scouting summary for a pitcher."""
    strengths = []
    weaknesses = []

    if stats["K%"] >= 25.0:
        strengths.append("elite strikeout ability (K% 25+)" if lang == "EN"
                         else "三振を奪う能力が非常に高い（K% 25以上）")
    elif stats["K%"] >= 20.0:
        strengths.append("above-average strikeout rate" if lang == "EN"
                         else "平均以上の奪三振率")

    if stats["Opp AVG"] <= 0.220:
        strengths.append(f"excellent contact management (Opp AVG .{int(stats['Opp AVG'] * 1000):03d})" if lang == "EN"
                         else f"被打率が非常に低い（被打率 .{int(stats['Opp AVG'] * 1000):03d}）")

    if stats["xwOBA"] and stats["xwOBA"] <= 0.290:
        strengths.append("low batted-ball quality allowed (xwOBA .290-)" if lang == "EN"
                         else "打球の質を抑えている（被xwOBA .290以下）")

    if stats["Avg Velo"] and stats["Avg Velo"] >= 95.0:
        strengths.append(f"power arm (Avg Velo {stats['Avg Velo']:.1f} mph)" if lang == "EN"
                         else f"パワーアーム（平均球速 {stats['Avg Velo']:.1f} mph）")

    if stats["BB%"] >= 10.0:
        weaknesses.append(f"high walk rate (BB% {stats['BB%']:.1f})" if lang == "EN"
                          else f"四球が多い（与四球率 {stats['BB%']:.1f}%）")
    elif stats["BB%"] >= 8.0:
        weaknesses.append(f"moderate walk rate (BB% {stats['BB%']:.1f})" if lang == "EN"
                          else f"四球がやや多い（与四球率 {stats['BB%']:.1f}%）")

    if stats["K%"] < 15.0:
        weaknesses.append(f"low strikeout rate (K% {stats['K%']:.1f})" if lang == "EN"
                          else f"三振を奪えない（奪三振率 {stats['K%']:.1f}%）")

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
                        f"(Opp AVG .{int(weak_avg * 1000):03d})"
                    )
                else:
                    weak_ja = "左打者" if weak_side == "LHB" else "右打者"
                    weaknesses.append(
                        f"左右差あり — {weak_ja}に打たれやすい "
                        f"（被打率 .{int(weak_avg * 1000):03d}）"
                    )

    parts = []
    if strengths:
        prefix = "Strengths: " if lang == "EN" else "強み: "
        parts.append(prefix + ", ".join(strengths) + ".")
    if weaknesses:
        prefix = "Weaknesses: " if lang == "EN" else "弱み: "
        parts.append(prefix + ", ".join(weaknesses) + ".")
    if not parts:
        return ("Balanced profile with no extreme strengths or weaknesses."
                if lang == "EN" else "特に目立つ偏りのないバランス型の投手。")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Visualisation helpers
# ---------------------------------------------------------------------------
def _zone_text_color(val: float, vmin: float, vmax: float) -> str:
    norm = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    if 0.25 < norm < 0.65:
        return "black"
    return "white"


def draw_zone_heatmap(df: pd.DataFrame, metric: str, title: str, ax):
    x_bins = np.linspace(-1.5, 1.5, 6)
    z_bins = np.linspace(1.0, 4.0, 6)

    valid = df.dropna(subset=["plate_x", "plate_z"]).copy()

    if metric == "usage":
        total = len(valid)
        grid = np.full((5, 5), np.nan)
        for i in range(5):
            for j in range(5):
                mask = (
                    (valid["plate_x"] >= x_bins[j]) & (valid["plate_x"] < x_bins[j + 1])
                    & (valid["plate_z"] >= z_bins[i]) & (valid["plate_z"] < z_bins[i + 1])
                )
                cell_count = mask.sum()
                if cell_count >= 3:
                    grid[i, j] = cell_count / total * 100
        vmin, vmax = 0, 10
        cmap = plt.cm.YlOrRd
    else:  # ba
        hit_events = {"single", "double", "triple", "home_run"}
        ab_events = hit_events | {"field_out", "strikeout", "grounded_into_double_play",
                                  "double_play", "force_out", "fielders_choice",
                                  "fielders_choice_out", "strikeout_double_play", "field_error"}
        valid = valid[valid["events"].isin(ab_events)]
        valid["is_hit"] = valid["events"].isin(hit_events).astype(int)
        grid = np.full((5, 5), np.nan)
        for i in range(5):
            for j in range(5):
                mask = (
                    (valid["plate_x"] >= x_bins[j]) & (valid["plate_x"] < x_bins[j + 1])
                    & (valid["plate_z"] >= z_bins[i]) & (valid["plate_z"] < z_bins[i + 1])
                )
                cell = valid.loc[mask, "is_hit"]
                if len(cell) >= 5:
                    grid[i, j] = cell.mean()
        vmin, vmax = 0, 0.450
        cmap = plt.cm.RdYlGn_r

    cmap_copy = cmap.copy()
    cmap_copy.set_bad(color="#222222")
    im = ax.pcolormesh(
        x_bins, z_bins, grid, cmap=cmap_copy, vmin=vmin, vmax=vmax,
        edgecolors="white", linewidth=0.5,
    )

    rect = patches.Rectangle(
        (-0.83, 1.5), 1.66, 2.0,
        linewidth=2, edgecolor="black", facecolor="none",
    )
    ax.add_patch(rect)

    for i in range(5):
        for j in range(5):
            val = grid[i, j]
            if not np.isnan(val):
                if metric == "usage":
                    txt = f"{val:.1f}%"
                else:
                    txt = f".{int(val * 1000):03d}"
                txt_color = _zone_text_color(val, vmin, vmax)
                ax.text(
                    (x_bins[j] + x_bins[j + 1]) / 2,
                    (z_bins[i] + z_bins[i + 1]) / 2,
                    txt, ha="center", va="center",
                    fontsize=9, fontweight="bold", color=txt_color,
                    path_effects=[pe.withStroke(linewidth=2,
                                               foreground="white" if txt_color == "black" else "black")],
                )

    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(0.5, 4.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=13, fontweight="bold", color="white")
    ax.set_xlabel("plate_x (ft)")
    ax.set_ylabel("plate_z (ft)")
    return im


def draw_zone_3x3(df: pd.DataFrame, metric: str, title: str, ax):
    hit_events = {"single", "double", "triple", "home_run"}
    ab_events = hit_events | {"field_out", "strikeout", "grounded_into_double_play",
                              "double_play", "force_out", "fielders_choice",
                              "fielders_choice_out", "strikeout_double_play", "field_error"}

    valid = df.dropna(subset=["zone"]).copy()
    valid["zone"] = valid["zone"].astype(int)

    x_edges = np.linspace(-0.83, 0.83, 4)
    z_edges = np.linspace(1.5, 3.5, 4)

    grid = np.full((3, 3), np.nan)
    zone_map = {
        1: (2, 0), 2: (2, 1), 3: (2, 2),
        4: (1, 0), 5: (1, 1), 6: (1, 2),
        7: (0, 0), 8: (0, 1), 9: (0, 2),
    }

    if metric == "usage":
        vmin, vmax = 0, 20
        cmap = plt.cm.YlOrRd.copy()
    else:
        vmin, vmax = 0, 0.450
        cmap = plt.cm.RdYlGn_r.copy()

    for zone_num, (row, col) in zone_map.items():
        zdf = valid[valid["zone"] == zone_num]
        if metric == "usage":
            total_in_zone = len(valid[(valid["zone"] >= 1) & (valid["zone"] <= 9)])
            if len(zdf) >= 3 and total_in_zone > 0:
                grid[row, col] = len(zdf) / total_in_zone * 100
        else:
            ab = zdf[zdf["events"].isin(ab_events)]
            hits = zdf[zdf["events"].isin(hit_events)]
            if len(ab) >= 5:
                grid[row, col] = len(hits) / len(ab)

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
            if metric == "usage":
                txt = f"{val:.1f}%"
            else:
                txt = f".{int(val * 1000):03d}"
            txt_color = _zone_text_color(val, vmin, vmax)
            ax.text(cx, cz, txt, ha="center", va="center",
                    fontsize=12, fontweight="bold", color=txt_color,
                    path_effects=[pe.withStroke(linewidth=2,
                                               foreground="white" if txt_color == "black" else "black")])

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(1.0, 4.0)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=13, fontweight="bold", color="white")
    ax.set_xlabel("plate_x (ft)")
    ax.set_ylabel("plate_z (ft)")
    return im


def draw_movement_chart(df: pd.DataFrame, title: str, ax, density: bool = True):
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
        ax.scatter(
            sub["pfx_x_in"], sub["pfx_z_in"],
            c=color, s=15, alpha=0.5, label=label, edgecolors="none", zorder=3,
        )

    ax.axhline(0, color="white", linewidth=0.5, alpha=0.3)
    ax.axvline(0, color="white", linewidth=0.5, alpha=0.3)
    ax.set_xlabel("Horizontal Break (in)", color="white")
    ax.set_ylabel("Induced Vertical Break (in)", color="white")
    ax.set_title(title, fontsize=13, fontweight="bold", color="white")
    leg = ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=12,
                    facecolor="#0e1117", edgecolor="white",
                    labelspacing=1.0, borderpad=1.0,
                    markerscale=3.0, handletextpad=0.8)
    for text in leg.get_texts():
        text.set_color("white")
    ax.tick_params(colors="white")


def arsenal_table(df: pd.DataFrame, t) -> pd.DataFrame:
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

        two_strike = grp[(grp["strikes"] == 2)]
        k_on_two = two_strike[two_strike["events"].str.contains("strikeout", na=False)] if "events" in two_strike.columns else pd.DataFrame()
        put_away = len(k_on_two) / len(two_strike) * 100 if len(two_strike) > 0 else 0

        label = PITCH_LABELS.get(pt, pt)
        rows.append({
            t["pitch_type"]: label,
            t["count"]: n_pitches,
            t["usage_pct"]: f"{usage:.1f}%",
            t["avg_velo"]: f"{avg_velo:.1f}" if avg_velo and not pd.isna(avg_velo) else "\u2014",
            t["max_velo"]: f"{max_velo:.1f}" if max_velo and not pd.isna(max_velo) else "\u2014",
            t["avg_spin"]: f"{avg_spin:.0f}" if avg_spin and not pd.isna(avg_spin) else "\u2014",
            t["h_break"]: f"{h_break:.1f}" if h_break is not None else "\u2014",
            t["v_break"]: f"{v_break:.1f}" if v_break is not None else "\u2014",
            t["whiff_pct"]: f"{whiff_pct:.1f}%",
            t["put_away_pct"]: f"{put_away:.1f}%",
        })

    result = pd.DataFrame(rows)
    if not result.empty:
        result = result.sort_values(t["count"], ascending=False).reset_index(drop=True)
    return result


def batted_ball_against(df: pd.DataFrame, t) -> dict:
    bb = df.dropna(subset=["bb_type"])
    n_bb = len(bb)
    if n_bb == 0:
        return {}

    return {
        t["gb_pct"]: f"{(bb['bb_type'] == 'ground_ball').sum() / n_bb * 100:.1f}%",
        t["ld_pct"]: f"{(bb['bb_type'] == 'line_drive').sum() / n_bb * 100:.1f}%",
        t["fb_pct"]: f"{(bb['bb_type'] == 'fly_ball').sum() / n_bb * 100:.1f}%",
        t["avg_ev"]: f"{df['launch_speed'].dropna().mean():.1f}" if df["launch_speed"].notna().any() else "\u2014",
        t["avg_la"]: f"{df['launch_angle'].dropna().mean():.1f}" if df["launch_angle"].notna().any() else "\u2014",
    }


def count_category(balls: int, strikes: int) -> str:
    if strikes > balls:
        return "ahead"
    elif balls > strikes:
        return "behind"
    return "even"


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Dominican Republic Pitching \u2014 WBC 2026",
        page_icon="\U0001F1E9\U0001F1F4",
        layout="wide",
    )

    lang = st.sidebar.radio("Language / \u8a00\u8a9e", ["EN", "JA"], horizontal=True)
    t = TEXTS[lang]

    st.sidebar.markdown(f"# \U0001F1E9\U0001F1F4 {t['title']}")
    st.sidebar.caption(t["subtitle"])

    pitcher_names = [t["team_overview"]] + [p["name"] for p in DR_PITCHERS]
    selected = st.sidebar.selectbox(t["select_pitcher"], pitcher_names)

    df_all = load_data()

    seasons = ["All"] + sorted(df_all["season"].unique().tolist())
    season = st.sidebar.selectbox(t["season"], seasons, format_func=lambda x: t["all_seasons"] if x == "All" else str(x))
    df_all = filter_season(df_all, season)

    # -----------------------------------------------------------------------
    # Staff Overview
    # -----------------------------------------------------------------------
    if selected == t["team_overview"]:
        st.header(f"\U0001F1E9\U0001F1F4 {t['team_overview']}")

        st.info(t["overview_guide"])

        with st.expander("Stats glossary" if lang == "EN" else "\u7528\u8a9e\u306e\u8aac\u660e\u3092\u898b\u308b"):
            st.markdown(t["glossary_stats"])

        rows = []
        for p in DR_PITCHERS:
            pdf = df_all[df_all["pitcher"] == p["mlbam_id"]]
            if pdf.empty:
                continue
            s = pitching_stats(pdf)
            role_label = t["sp"] if p["role"] == "SP" else t["rp"]
            rows.append({
                "Pitcher": p["name"],
                t["team"]: p["team"],
                t["throws"]: p["throws"],
                t["role"]: role_label,
                t["pitches"]: s["Pitches"],
                t["k_pct"]: s["K%"],
                t["bb_pct"]: s["BB%"],
                t["opp_avg"]: s["Opp AVG"],
                t["opp_slg"]: s["Opp SLG"],
                t["xwoba_against"]: s["xwOBA"],
                t["avg_velo"]: s["Avg Velo"],
            })

        if rows:
            overview = pd.DataFrame(rows)
            st.dataframe(
                overview.style.format({
                    t["k_pct"]: "{:.1f}", t["bb_pct"]: "{:.1f}",
                    t["opp_avg"]: "{:.3f}", t["opp_slg"]: "{:.3f}",
                    t["xwoba_against"]: "{:.3f}", t["avg_velo"]: "{:.1f}",
                }).background_gradient(subset=[t["k_pct"]], cmap="RdYlGn")
                .background_gradient(subset=[t["opp_avg"]], cmap="RdYlGn_r"),
                use_container_width=True,
                hide_index=True,
            )

            st.subheader(t["team_strengths"])
            st.info(t["strength_note"])
        else:
            st.warning(t["no_data"])
        return

    # -----------------------------------------------------------------------
    # Individual Pitcher Report
    # -----------------------------------------------------------------------
    pitcher = PITCHER_BY_NAME[selected]
    pdf = df_all[df_all["pitcher"] == pitcher["mlbam_id"]]

    if pdf.empty:
        st.warning(t["no_data"])
        return

    stats = pitching_stats(pdf)
    role_label = t["sp"] if pitcher["role"] == "SP" else t["rp"]

    st.header(f"\U0001F1E9\U0001F1F4 {pitcher['name']}")
    c1, c2, c3 = st.columns(3)
    c1.metric(t["team"], pitcher["team"])
    c2.metric(t["throws"], pitcher["throws"])
    c3.metric(t["role"], role_label)

    c4, c5, c6, c7, c8 = st.columns(5)
    c4.metric(t["opp_avg"], f"{stats['Opp AVG']:.3f}")
    c5.metric(t["opp_slg"], f"{stats['Opp SLG']:.3f}")
    c6.metric(t["k_pct"], f"{stats['K%']:.1f}%")
    c7.metric(t["bb_pct"], f"{stats['BB%']:.1f}%")
    c8.metric(t["xwoba_against"], f"{stats['xwOBA']:.3f}" if stats["xwOBA"] else "\u2014")

    with st.expander("Stats glossary" if lang == "EN" else "\u7528\u8a9e\u306e\u8aac\u660e\u3092\u898b\u308b"):
        st.markdown(t["glossary_stats"])

    st.subheader(t["pitcher_summary"])
    summary = generate_pitcher_summary(stats, pdf, pitcher, lang)
    st.info(summary)

    st.divider()

    # Arsenal Table
    st.subheader(t["arsenal"])
    with st.expander("What do these columns mean?" if lang == "EN" else "\u5404\u5217\u306e\u8aac\u660e\u3092\u898b\u308b"):
        st.markdown(t["glossary_arsenal"])
    at = arsenal_table(pdf, t)
    if not at.empty:
        st.dataframe(at, use_container_width=True, hide_index=True)

    st.divider()

    # Movement Chart
    st.subheader(t["movement_chart"])
    with st.expander("How to read this chart" if lang == "EN" else "\u30c1\u30e3\u30fc\u30c8\u306e\u898b\u65b9"):
        st.markdown(t["glossary_movement"])
    show_mvt_density = st.checkbox(
        "Density contour" if lang == "EN" else "\u5bc6\u5ea6\u7b49\u9ad8\u7dda\u3092\u8868\u793a",
        value=True, key="mvt_density",
    )
    fig_m, ax_m = plt.subplots(figsize=(10, 5), facecolor="#0e1117")
    ax_m.set_facecolor("#0e1117")
    for spine in ax_m.spines.values():
        spine.set_color("white")
    draw_movement_chart(pdf, pitcher["name"], ax_m, density=show_mvt_density)
    fig_m.tight_layout(rect=[0, 0, 0.82, 1])
    st.pyplot(fig_m)
    plt.close(fig_m)

    st.divider()

    # Batted Ball Against
    st.subheader(t["batted_ball"])
    with st.expander("What do these mean?" if lang == "EN" else "\u7528\u8a9e\u306e\u8aac\u660e\u3092\u898b\u308b"):
        st.markdown(t["glossary_batted"])
    bb_profile = batted_ball_against(pdf, t)
    if bb_profile:
        bb_cols = st.columns(len(bb_profile))
        for i, (k, v) in enumerate(bb_profile.items()):
            bb_cols[i].metric(k, v)
    else:
        st.write(t["no_data"])

    st.divider()

    # Pitch type filter
    st.markdown(f"### {t['pitch_filter']}")
    avail_types = pdf.dropna(subset=["pitch_type"])["pitch_type"].value_counts().head(8).index.tolist()
    pitch_options = [t["all_pitches"]] + [PITCH_LABELS.get(pt, pt) for pt in avail_types]
    selected_pitch = st.selectbox(t["pitch_filter"], pitch_options, key="pitch_filter",
                                  label_visibility="collapsed")

    if selected_pitch == t["all_pitches"]:
        fdf = pdf
    else:
        label_to_code = {PITCH_LABELS.get(pt, pt): pt for pt in avail_types}
        fdf = pdf[pdf["pitch_type"] == label_to_code[selected_pitch]]

    pitch_suffix = f" \u2014 {selected_pitch}" if selected_pitch != t["all_pitches"] else ""

    # Zone Heatmaps
    st.subheader(t["zone_heatmap"] + pitch_suffix)
    st.caption(t["danger_zone"])
    fig = plt.figure(figsize=(14, 5), facecolor="#0e1117")
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.05], wspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    cax = fig.add_subplot(gs[0, 2])
    for ax in (ax1, ax2):
        ax.set_facecolor("#0e1117")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
    draw_zone_heatmap(fdf, "usage", t["usage_heatmap"], ax1)
    im = draw_zone_heatmap(fdf, "ba", t["ba_heatmap"], ax2)
    cb = fig.colorbar(im, cax=cax)
    cb.ax.tick_params(colors="white")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # 3x3 Zone Chart
    st.subheader(t["zone_3x3"] + pitch_suffix)
    fig3 = plt.figure(figsize=(12, 4.5), facecolor="#0e1117")
    gs3 = fig3.add_gridspec(1, 3, width_ratios=[1, 1, 0.05], wspace=0.35)
    ax3a = fig3.add_subplot(gs3[0, 0])
    ax3b = fig3.add_subplot(gs3[0, 1])
    cax3 = fig3.add_subplot(gs3[0, 2])
    for ax in (ax3a, ax3b):
        ax.set_facecolor("#0e1117")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
    draw_zone_3x3(fdf, "usage", t["usage_heatmap"], ax3a)
    im3 = draw_zone_3x3(fdf, "ba", t["ba_heatmap"], ax3b)
    cb3 = fig3.colorbar(im3, cax=cax3)
    cb3.ax.tick_params(colors="white")
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    st.divider()

    # Platoon Splits
    st.subheader(t["platoon"] + pitch_suffix)
    with st.expander("What are platoon splits?" if lang == "EN" else "\u5de6\u53f3\u6253\u8005\u5225\u6210\u7e3e\u3068\u306f\uff1f"):
        st.markdown(t["glossary_platoon"])

    col_l, col_r = st.columns(2)

    for col, stand, label in [(col_l, "L", t["vs_lhb"]), (col_r, "R", t["vs_rhb"])]:
        with col:
            st.markdown(f"**{label}**")
            split_df = fdf[fdf["stand"] == stand]
            if split_df.empty:
                st.write(t["no_data"])
                continue
            ss = pitching_stats(split_df)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(t["opp_avg"], f"{ss['Opp AVG']:.3f}")
            m2.metric(t["opp_slg"], f"{ss['Opp SLG']:.3f}")
            m3.metric(t["k_pct"], f"{ss['K%']:.1f}%")
            m4.metric(t["bb_pct"], f"{ss['BB%']:.1f}%")

            fig_z, ax_z = plt.subplots(figsize=(5, 4), facecolor="#0e1117")
            ax_z.set_facecolor("#0e1117")
            ax_z.tick_params(colors="white")
            ax_z.xaxis.label.set_color("white")
            ax_z.yaxis.label.set_color("white")
            ax_z.title.set_color("white")
            draw_zone_heatmap(split_df, "ba", f"{label} \u2014 {t['ba_heatmap']}", ax_z)
            fig_z.tight_layout()
            st.pyplot(fig_z)
            plt.close(fig_z)

    st.divider()

    # Count-based Performance
    st.subheader(t["count_perf"] + pitch_suffix)
    st.caption(t["count_explain"])

    count_df = fdf.dropna(subset=["balls", "strikes"]).copy()
    count_df["balls"] = count_df["balls"].astype(int)
    count_df["strikes"] = count_df["strikes"].astype(int)

    all_counts = [
        (0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
        (2, 1), (1, 2), (3, 0), (2, 2), (3, 1), (3, 2),
    ]

    count_rows = []
    for b, s in all_counts:
        cat = count_category(b, s)
        tag = {"ahead": t["ahead"], "behind": t["behind"], "even": t["even"]}[cat]
        cdf = count_df[(count_df["balls"] == b) & (count_df["strikes"] == s)]
        if cdf.empty:
            continue
        cs = pitching_stats(cdf)
        if cs["PA"] < 5:
            continue
        count_rows.append({
            ("Count" if lang == "EN" else "\u30ab\u30a6\u30f3\u30c8"): f"{b}-{s}",
            ("Type" if lang == "EN" else "\u5206\u985e"): tag,
            t["pitches"]: cs["Pitches"],
            t["opp_avg"]: cs["Opp AVG"],
            t["opp_slg"]: cs["Opp SLG"],
            t["k_pct"]: cs["K%"],
            t["bb_pct"]: cs["BB%"],
        })

    if count_rows:
        count_table = pd.DataFrame(count_rows)
        st.dataframe(
            count_table.style.format({
                t["opp_avg"]: "{:.3f}", t["opp_slg"]: "{:.3f}",
                t["k_pct"]: "{:.1f}", t["bb_pct"]: "{:.1f}",
            }).background_gradient(subset=[t["opp_avg"]], cmap="RdYlGn_r"),
            use_container_width=True,
            hide_index=True,
        )

    # Pitch Mix by Count
    st.subheader(t["count_pitch_mix"])
    mix_data = count_df.dropna(subset=["pitch_type"]).copy()
    top_pt = mix_data["pitch_type"].value_counts().head(8).index.tolist()
    mix_data = mix_data[mix_data["pitch_type"].isin(top_pt)]

    count_labels = []
    mix_rows = []
    for b, s in all_counts:
        cdf = mix_data[(mix_data["balls"] == b) & (mix_data["strikes"] == s)]
        if len(cdf) < 10:
            continue
        count_labels.append(f"{b}-{s}")
        total = len(cdf)
        row = {}
        for pt in top_pt:
            row[pt] = len(cdf[cdf["pitch_type"] == pt]) / total * 100
        mix_rows.append(row)

    if mix_rows:
        fig_mix, ax_mix = plt.subplots(figsize=(10, 5), facecolor="#0e1117")
        ax_mix.set_facecolor("#0e1117")
        x = np.arange(len(count_labels))
        bottoms = np.zeros(len(count_labels))
        bar_width = 0.6

        for pt in top_pt:
            vals = [row.get(pt, 0) for row in mix_rows]
            color = PITCH_COLORS.get(pt, "#AAAAAA")
            label = PITCH_LABELS.get(pt, pt)
            ax_mix.bar(x, vals, bar_width, bottom=bottoms, color=color,
                       label=label, edgecolor="white", linewidth=0.8)
            for i, v in enumerate(vals):
                if v >= 10:
                    ax_mix.text(x[i], bottoms[i] + v / 2, f"{v:.0f}%",
                                ha="center", va="center", fontsize=8,
                                fontweight="bold", color="white",
                                path_effects=[pe.withStroke(linewidth=2,
                                                            foreground="black")])
            bottoms += np.array(vals)

        ax_mix.set_xticks(x)
        ax_mix.set_xticklabels(count_labels, color="white", fontsize=10)
        ax_mix.set_ylabel("Usage %" if lang == "EN" else "\u4f7f\u7528\u7387 %",
                          color="white", fontsize=11)
        ax_mix.set_ylim(0, 105)
        ax_mix.tick_params(colors="white")
        for spine in ax_mix.spines.values():
            spine.set_color("white")
        leg_mix = ax_mix.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0),
                                fontsize=11, facecolor="#0e1117",
                                edgecolor="white", markerscale=2.0,
                                labelspacing=0.8, borderpad=0.8)
        for txt in leg_mix.get_texts():
            txt.set_color("white")
        fig_mix.tight_layout(rect=[0, 0, 0.82, 1])
        st.pyplot(fig_mix)
        plt.close(fig_mix)


if __name__ == "__main__":
    main()
