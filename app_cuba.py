"""WBC 2026 Cuba Batter Scouting Dashboard."""

import pathlib

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.patheffects as pe
import matplotlib_fontja  # noqa: F401 — enables Japanese font
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import gaussian_kde

from players_cuba_batters import CUBA_BATTERS, PLAYER_BY_NAME

from scouting_lib import (
    PREMIUM_CSS,
    generate_pitching_plan,
    generate_defensive_positioning,
    analyze_team_weaknesses,
)

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
TEXTS = {
    "EN": {
        "title": "Cuba Batter Scouting Report",
        "subtitle": "WBC 2026 — Projected Opponent Analysis",
        "select_player": "Select Player",
        "team_overview": "Team Overview",
        "season": "Season",
        "profile": "Player Profile",
        "pos": "Pos",
        "team": "Team",
        "bats": "Bats",
        "zone_heatmap": "Strike Zone Heatmap",
        "ba_heatmap": "Batting Avg by Zone",
        "xwoba_heatmap": "xwOBA by Zone",
        "spray_chart": "Spray Chart",
        "batted_ball": "Batted Ball Profile",
        "pull_pct": "Pull%",
        "cent_pct": "Center%",
        "oppo_pct": "Oppo%",
        "gb_pct": "GB%",
        "ld_pct": "LD%",
        "fb_pct": "FB%",
        "avg_ev": "Avg EV (mph)",
        "avg_la": "Avg LA (deg)",
        "pitch_type_perf": "Performance by Pitch Type",
        "pitch_type": "Pitch Type",
        "count": "Count",
        "ba": "BA",
        "slg": "SLG",
        "whiff_pct": "Whiff%",
        "chase_pct": "Chase%",
        "platoon": "Platoon Splits",
        "vs_lhp": "vs LHP",
        "vs_rhp": "vs RHP",
        "count_perf": "Performance by Count",
        "ahead": "Hitter Ahead (B > S)",
        "behind": "Hitter Behind (S > B)",
        "even": "Even (B = S)",
        "team_strengths": "Team Strengths & Weaknesses",
        "strength_note": (
            "Cuba has a legendary baseball tradition and fields a physically imposing lineup. The team historically emphasizes power hitting and aggressive approach at the plate. MLB-experienced Cuban players may bring elite-level talent to anchor the lineup."
        ),
        "no_data": "No data available for this selection.",
        "danger_zone": "Red = danger zone (high BA), Blue = attack zone (low BA)",
        "stadium": "Stadium",
        "zone_3x3": "Zone Chart (3×3)",
        "density_map": "Hit Density Map",
        "overview_guide": (
            "Select a player from the sidebar to see their detailed scouting report: "
            "zone heatmaps, spray charts, pitch-type performance, platoon splits, and more."
        ),
        "count_explain": (
            "Ahead = ball count > strike count (e.g. 2-1, 3-0). "
            "Behind = strike count > ball count (e.g. 0-2, 1-2). "
            "Even = same count (e.g. 1-1, 2-2)."
        ),
        "glossary_stats": (
            "- **AVG** = Batting Average (hits / at-bats)\n"
            "- **OBP** = On-Base Percentage (how often a batter reaches base)\n"
            "- **SLG** = Slugging Percentage (total bases / at-bats, measures power)\n"
            "- **OPS** = OBP + SLG (overall offensive value)\n"
            "- **xwOBA** = Expected Weighted On-Base Average (batted ball quality based on exit velocity & launch angle)"
        ),
        "glossary_pct": (
            "- **K%** = Strikeout rate\n- **BB%** = Walk rate"
        ),
        "glossary_pitch": (
            "- **Whiff%** = Swing-and-miss rate (misses / total swings)\n"
            "- **Chase%** = Rate of swinging at pitches outside the strike zone"
        ),
        "glossary_batted": (
            "- **Pull%** = Hit to batter's pull side\n"
            "- **GB%** = Ground ball rate\n- **LD%** = Line drive rate\n- **FB%** = Fly ball rate\n"
            "- **Avg EV** = Average exit velocity (mph)\n- **Avg LA** = Average launch angle (degrees)"
        ),
        "glossary_platoon": (
            "Platoon splits show how a batter performs against left-handed pitchers (LHP) "
            "vs right-handed pitchers (RHP). Large differences reveal matchup vulnerabilities."
        ),
        "player": "Player",
        "player_summary": "Scouting Summary",
        "top3_title": "Top 3 Batters (by OPS)",
        "team_radar_title": "Team Batting Profile",
        "full_stats_table": "Full Stats Table",
        "zone_caption": "Red zones = high batting avg (danger), Blue zones = low batting avg (attack)",
        "spray_caption": "Shows where each batted ball landed on the field",
        "pitch_caption": "Batting performance broken down by the type of pitch faced",
        "platoon_caption": "Compares batting stats against left-handed vs right-handed pitchers",
        "glossary_count": (
            "- **PA** = Plate Appearances (total times at bat)\n"
            "- **AVG** = Batting Average (hits / at-bats)\n"
            "- **OBP** = On-Base Percentage\n"
            "- **SLG** = Slugging Percentage (total bases / at-bats)\n"
            "- **OPS** = OBP + SLG (overall offensive value)\n"
            "- **K%** = Strikeout rate\n- **BB%** = Walk rate"
        ),
        "pos_glossary": (
            "- **C** = Catcher\n- **1B** = First Base\n- **2B** = Second Base\n"
            "- **3B** = Third Base\n- **SS** = Shortstop\n"
            "- **LF** = Left Field\n- **CF** = Center Field\n- **RF** = Right Field\n"
            "- **DH** = Designated Hitter\n- **UTL** = Utility (multi-position player)"
        ),
        "pos_glossary_label": "Position abbreviations",
        "pitching_plan_title": "Pitching Plan — How to Get This Batter Out",
        "pitching_plan_explain": "Data-driven approach based on pitch type vulnerabilities, zone weaknesses, count tendencies, and platoon splits.",
        "defensive_positioning": "Defensive Positioning & Shift Recommendation",
        "defensive_explain": "Auto-generated from spray chart data: pull/center/oppo tendencies, batted ball types, and exit velocity.",
        "team_weaknesses_title": "Team Weakness Analysis (Auto-Detected)",
    },
    "JA": {
        "title": "キューバ 打者スカウティングレポート",
        "subtitle": "WBC 2026 — 対戦相手分析（想定）",
        "select_player": "選手を選択",
        "team_overview": "チーム概要",
        "season": "シーズン",
        "profile": "選手プロフィール",
        "pos": "ポジション",
        "team": "チーム",
        "bats": "打席",
        "zone_heatmap": "ストライクゾーン ヒートマップ",
        "ba_heatmap": "ゾーン別 打率",
        "xwoba_heatmap": "ゾーン別 xwOBA",
        "spray_chart": "スプレーチャート（打球方向図）",
        "batted_ball": "打球傾向",
        "pull_pct": "プル%（引っ張り）",
        "cent_pct": "センター%",
        "oppo_pct": "逆方向%（流し打ち）",
        "gb_pct": "ゴロ%",
        "ld_pct": "ライナー%",
        "fb_pct": "フライ%",
        "avg_ev": "平均打球速度 (mph)",
        "avg_la": "平均打球角度 (度)",
        "pitch_type_perf": "球種別パフォーマンス",
        "pitch_type": "球種",
        "count": "投球数",
        "ba": "打率",
        "slg": "長打率",
        "whiff_pct": "空振率",
        "chase_pct": "チェイス率",
        "platoon": "左右投手別成績",
        "vs_lhp": "vs 左投手",
        "vs_rhp": "vs 右投手",
        "count_perf": "カウント別パフォーマンス",
        "ahead": "有利カウント (B > S)",
        "behind": "不利カウント (S > B)",
        "even": "イーブン (B = S)",
        "team_strengths": "チームの強み・弱み",
        "strength_note": (
            "キューバは野球の伝統国として長い歴史を誇り、身体的に強靭な打者が揃う打線が特徴とされている。\n\n積極的な打撃スタイルと長打力が持ち味で、MLB経験を持つキューバ系選手が打線の中心となる可能性がある。"
        ),
        "no_data": "このフィルターではデータがありません。",
        "danger_zone": "赤 = 危険ゾーン（高打率）、青 = 攻めるゾーン（低打率）",
        "stadium": "球場",
        "zone_3x3": "ゾーンチャート (3×3)",
        "density_map": "打球密度マップ",
        "overview_guide": (
            "左のサイドバーから選手を選ぶと、個人の詳細スカウティングレポートを表示します: "
            "ゾーン別ヒートマップ、打球方向図、球種別成績、左右投手別成績など。"
        ),
        "count_explain": (
            "有利カウント = ボール数 > ストライク数（例: 2-1, 3-0）。"
            "不利カウント = ストライク数 > ボール数（例: 0-2, 1-2）。"
            "イーブン = 同数（例: 1-1, 2-2）。"
        ),
        "glossary_stats": (
            "- **AVG（打率）** = 安打数 / 打数\n"
            "- **OBP（出塁率）** = 打者が塁に出る割合\n"
            "- **SLG（長打率）** = 塁打数 / 打数（長打力の指標）\n"
            "- **OPS** = OBP + SLG（総合的な打撃力）\n"
            "- **xwOBA** = 打球の質（打球速度と角度から算出した期待値）"
        ),
        "glossary_pct": (
            "- **K%（三振率）** = 打席あたりの三振割合\n- **BB%（四球率）** = 打席あたりの四球割合"
        ),
        "glossary_pitch": (
            "- **空振率（Whiff%）** = スイングに対する空振りの割合\n"
            "- **チェイス率（Chase%）** = ストライクゾーン外の球に手を出す割合"
        ),
        "glossary_batted": (
            "- **プル%** = 引っ張り方向への打球割合\n"
            "- **ゴロ%** = ゴロの割合\n- **ライナー%** = ライナーの割合\n- **フライ%** = フライの割合\n"
            "- **平均打球速度** = 打球のスピード（mph）\n- **平均打球角度** = 打球の打ち出し角度"
        ),
        "glossary_platoon": (
            "左右投手別成績は、左投手（LHP）と右投手（RHP）に対する打撃成績です。"
            "左右で成績に大きな差がある打者は、苦手な側の投手でマッチアップを作ると有利です。"
        ),
        "player": "選手",
        "player_summary": "スカウティング要約",
        "top3_title": "注目打者 TOP3（OPS順）",
        "team_radar_title": "チーム打線の特徴",
        "full_stats_table": "詳細成績一覧",
        "zone_caption": "赤いゾーン = よく打つ場所、青いゾーン = 打てない場所",
        "spray_caption": "打球がフィールドのどこに飛んだかの分布図",
        "pitch_caption": "対戦した球種ごとの打撃成績",
        "platoon_caption": "左投手と右投手、それぞれに対する打撃成績の比較",
        "glossary_count": (
            "- **PA（打席数）** = 打席に立った総回数\n"
            "- **AVG（打率）** = 安打数 ÷ 打数\n"
            "- **OBP（出塁率）** = 塁に出た割合\n"
            "- **SLG（長打率）** = 塁打数 ÷ 打数\n"
            "- **OPS** = OBP + SLG（総合打撃指標）\n"
            "- **K%（三振率）** = 打席あたりの三振割合\n- **BB%（四球率）** = 打席あたりの四球割合"
        ),
        "pos_glossary": (
            "- **C** = 捕手（キャッチャー）\n- **1B** = 一塁手\n- **2B** = 二塁手\n"
            "- **3B** = 三塁手\n- **SS** = 遊撃手（ショート）\n"
            "- **LF** = 左翼手（レフト）\n- **CF** = 中堅手（センター）\n- **RF** = 右翼手（ライト）\n"
            "- **DH** = 指名打者\n- **UTL** = ユーティリティ（複数ポジション対応）"
        ),
        "pos_glossary_label": "ポジション略称の説明",
        "pitching_plan_title": "投球プラン — この打者の攻略法",
        "pitching_plan_explain": "球種別の弱点、ゾーン別打率、カウント傾向、左右差からデータに基づく攻め方を自動生成。",
        "defensive_positioning": "守備位置・シフト推奨",
        "defensive_explain": "スプレーチャートデータから自動生成: プル/センター/逆方向の傾向、打球種別、打球速度に基づく。",
        "team_weaknesses_title": "チーム弱点分析（自動検出）",
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

# ---------------------------------------------------------------------------
# Stadium data
# ---------------------------------------------------------------------------
STADIUM_SCALE = 2.495 / 2.33
STADIUM_CSV = pathlib.Path(__file__).parent / "data" / "mlbstadiums_wbc.csv"

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


@st.cache_data
def load_stadium_coords() -> pd.DataFrame:
    df = pd.read_csv(STADIUM_CSV)
    # Apply pybaseball's coordinate transform
    df["x"] = (df["x"] - 125) * STADIUM_SCALE + 125
    df["y"] = -((df["y"] - 199) * STADIUM_SCALE + 199)
    # Negate y to match our positive-y, inverted-axis convention
    df["y"] = -df["y"]
    return df


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent / "data" / "cuba_statcast.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, low_memory=False)
    df["game_date"] = pd.to_datetime(df["game_date"])
    if "season" not in df.columns:
        df["season"] = df["game_date"].dt.year
    return df


def filter_season(df: pd.DataFrame, season) -> pd.DataFrame:
    return df[df["season"] == int(season)]


# ---------------------------------------------------------------------------
# Computed stats helpers
# ---------------------------------------------------------------------------
def batting_stats(df: pd.DataFrame) -> dict:
    """Compute basic batting stats from Statcast event-level data."""
    ab_events = {"single", "double", "triple", "home_run", "field_out",
                 "strikeout", "grounded_into_double_play", "double_play",
                 "force_out", "fielders_choice", "fielders_choice_out",
                 "strikeout_double_play", "triple_play", "field_error"}
    pa_events = ab_events | {"walk", "hit_by_pitch", "sac_fly", "sac_bunt",
                             "sac_fly_double_play", "catcher_interf",
                             "intent_walk"}
    hit_events = {"single", "double", "triple", "home_run"}

    evts = df.dropna(subset=["events"])
    pa = evts[evts["events"].isin(pa_events)]
    ab = evts[evts["events"].isin(ab_events)]
    hits = evts[evts["events"].isin(hit_events)]

    n_pa = len(pa)
    n_ab = len(ab)
    n_h = len(hits)
    n_bb = len(pa[pa["events"].isin({"walk", "intent_walk"})])
    n_hbp = len(pa[pa["events"].isin({"hit_by_pitch"})])
    n_sf = len(pa[pa["events"].isin({"sac_fly", "sac_fly_double_play"})])
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


def generate_player_summary(stats: dict, pdf: pd.DataFrame, player: dict,
                            lang: str) -> str:
    """Auto-generate a scouting summary for a player."""
    strengths = []
    weaknesses = []

    # Power
    if stats["SLG"] >= 0.450:
        strengths.append("elite power (SLG .450+)" if lang == "EN"
                         else "長打力が非常に高い（SLG .450以上）")
    elif stats["SLG"] >= 0.400:
        strengths.append("above-average power" if lang == "EN"
                         else "平均以上の長打力")

    # Contact
    if stats["AVG"] >= 0.300:
        strengths.append("elite contact ability (AVG .300+)" if lang == "EN"
                         else "卓越したコンタクト力（打率 .300以上）")
    elif stats["AVG"] >= 0.270:
        strengths.append("solid contact hitter" if lang == "EN"
                         else "安定したコンタクトヒッター")

    # Discipline
    if stats["BB%"] >= 10.0:
        strengths.append(f"patient approach (BB% {stats['BB%']:.1f})" if lang == "EN"
                         else f"選球眼が良い（四球率 {stats['BB%']:.1f}%）")

    # xwOBA
    if stats["xwOBA"] and stats["xwOBA"] >= 0.350:
        strengths.append("high batted-ball quality (xwOBA .350+)" if lang == "EN"
                         else "打球の質が高い（xwOBA .350以上）")

    # Strikeouts
    if stats["K%"] >= 25.0:
        weaknesses.append(f"high strikeout rate (K% {stats['K%']:.1f})" if lang == "EN"
                          else f"三振が多い（三振率 {stats['K%']:.1f}%）")
    elif stats["K%"] >= 20.0:
        weaknesses.append(f"moderate strikeout rate (K% {stats['K%']:.1f})" if lang == "EN"
                          else f"三振がやや多い（三振率 {stats['K%']:.1f}%）")

    # Platoon split
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
                        f"(OPS .{int(weak_ops * 1000):03d})"
                    )
                else:
                    weak_ja = "左投手" if weak_side == "LHP" else "右投手"
                    weaknesses.append(
                        f"左右差が大きい — {weak_ja}に弱い "
                        f"（OPS .{int(weak_ops * 1000):03d}）"
                    )

    # Build summary
    parts = []
    if strengths:
        prefix = "Strengths: " if lang == "EN" else "強み: "
        parts.append(prefix + ", ".join(strengths) + ".")
    if weaknesses:
        prefix = "Weaknesses: " if lang == "EN" else "弱み: "
        parts.append(prefix + ", ".join(weaknesses) + ".")
    if not parts:
        return ("Balanced profile with no extreme strengths or weaknesses."
                if lang == "EN" else "特に目立つ偏りのないバランス型の打者。")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Visualisation helpers
# ---------------------------------------------------------------------------
def _zone_text_color(val: float, vmin: float, vmax: float) -> str:
    """Return black for light cells (mid-range values), white for dark cells."""
    norm = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    if 0.25 < norm < 0.65:
        return "black"
    return "white"


def draw_zone_heatmap(df: pd.DataFrame, metric: str, title: str, ax):
    """Draw a 5x5 heatmap over the strike zone."""
    x_bins = np.linspace(-1.5, 1.5, 6)
    z_bins = np.linspace(1.0, 4.0, 6)

    valid = df.dropna(subset=["plate_x", "plate_z"]).copy()

    if metric == "ba":
        hit_events = {"single", "double", "triple", "home_run"}
        ab_events = {"single", "double", "triple", "home_run", "field_out",
                     "strikeout", "grounded_into_double_play", "double_play",
                     "force_out", "fielders_choice", "fielders_choice_out",
                     "strikeout_double_play", "field_error"}
        valid = valid[valid["events"].isin(ab_events)]
        valid["is_hit"] = valid["events"].isin(hit_events).astype(int)
        value_col = "is_hit"
        vmin, vmax = 0, 0.450
    else:  # xwoba
        valid = valid.dropna(subset=["estimated_woba_using_speedangle"])
        value_col = "estimated_woba_using_speedangle"
        vmin, vmax = 0.150, 0.500

    grid = np.full((5, 5), np.nan)
    for i in range(5):
        for j in range(5):
            mask = (
                (valid["plate_x"] >= x_bins[j])
                & (valid["plate_x"] < x_bins[j + 1])
                & (valid["plate_z"] >= z_bins[i])
                & (valid["plate_z"] < z_bins[i + 1])
            )
            cell = valid.loc[mask, value_col]
            if len(cell) >= 5:
                grid[i, j] = cell.mean()

    cmap = plt.cm.RdYlGn
    cmap.set_bad(color="#222222")
    im = ax.pcolormesh(
        x_bins, z_bins, grid, cmap=cmap, vmin=vmin, vmax=vmax,
        edgecolors="white", linewidth=0.5,
    )

    # strike zone box
    sz_left, sz_right = -0.83, 0.83
    sz_bot, sz_top = 1.5, 3.5
    rect = patches.Rectangle(
        (sz_left, sz_bot), sz_right - sz_left, sz_top - sz_bot,
        linewidth=2, edgecolor="black", facecolor="none",
    )
    ax.add_patch(rect)

    # annotate cells
    for i in range(5):
        for j in range(5):
            val = grid[i, j]
            if not np.isnan(val):
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
    """Draw 3x3 zone chart using plate_x/plate_z coordinates."""
    hit_events = {"single", "double", "triple", "home_run"}
    ab_events = hit_events | {"field_out", "strikeout", "grounded_into_double_play",
                              "double_play", "force_out", "fielders_choice",
                              "fielders_choice_out", "strikeout_double_play", "field_error"}

    valid = df.dropna(subset=["plate_x", "plate_z"]).copy()

    x_edges = np.linspace(-0.83, 0.83, 4)
    z_edges = np.linspace(1.5, 3.5, 4)

    grid = np.full((3, 3), np.nan)
    zone_map = {
        1: (2, 0), 2: (2, 1), 3: (2, 2),
        4: (1, 0), 5: (1, 1), 6: (1, 2),
        7: (0, 0), 8: (0, 1), 9: (0, 2),
    }

    if metric == "ba":
        vmin, vmax = 0, 0.450
    else:
        vmin, vmax = 0.150, 0.500

    for zone_num, (row, col) in zone_map.items():
        mask = ((valid["plate_x"] >= x_edges[col])
                & (valid["plate_x"] < x_edges[col + 1])
                & (valid["plate_z"] >= z_edges[row])
                & (valid["plate_z"] < z_edges[row + 1]))
        zdf = valid[mask]
        if metric == "ba":
            ab = zdf[zdf["events"].isin(ab_events)]
            hits = zdf[zdf["events"].isin(hit_events)]
            if len(ab) >= 5:
                grid[row, col] = len(hits) / len(ab)
        else:  # xwoba
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


def draw_spray_chart(df: pd.DataFrame, title: str, ax, stadium: str = "astros",
                     density: bool = False):
    """Draw spray chart on a real stadium outline."""
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
    color_map = {
        "home_run": "#e53935",
        "triple": "#ff9800",
        "double": "#ff9800",
        "single": "#4caf50",
    }
    valid["color"] = valid["events"].map(color_map).fillna("#888888")
    valid["zorder"] = valid["events"].apply(
        lambda x: 5 if x == "home_run" else (4 if x in ("double", "triple") else 3)
    )

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
        ax.scatter(
            row["hc_x"], row["hc_y"],
            c=row["color"], s=18, alpha=0.7,
            edgecolors="none", zorder=row["zorder"],
        )

    ax.set_xlim(0, 250)
    ax.set_ylim(220, -20)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=13, fontweight="bold", color="white")
    ax.axis("off")

    for label, color in [("HR", "#e53935"), ("XBH", "#ff9800"), ("1B", "#4caf50"), ("Out", "#888888")]:
        ax.scatter([], [], c=color, s=30, label=label)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.6)


def pitch_type_table(df: pd.DataFrame, t) -> pd.DataFrame:
    """Build pitch-type performance table."""
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

        grp_coords = grp.dropna(subset=["plate_x", "plate_z"])
        outside = grp_coords[
            (grp_coords["plate_x"] < -0.83) | (grp_coords["plate_x"] > 0.83)
            | (grp_coords["plate_z"] < 1.5) | (grp_coords["plate_z"] > 3.5)]
        chase_swings = outside[outside["description"].isin({
            "hit_into_play", "foul", "swinging_strike",
            "swinging_strike_blocked", "foul_tip",
        })]
        chase_pct = len(chase_swings) / len(outside) * 100 if len(outside) > 0 else 0

        hit_events = {"single", "double", "triple", "home_run"}
        ab_events = hit_events | {"field_out", "strikeout", "grounded_into_double_play",
                                  "double_play", "force_out", "fielders_choice",
                                  "fielders_choice_out", "strikeout_double_play", "field_error"}
        ab = grp[grp["events"].isin(ab_events)]
        hits = grp[grp["events"].isin(hit_events)]
        n_ab = len(ab)
        n_h = len(hits)
        n_1b = len(hits[hits["events"] == "single"])
        n_2b = len(hits[hits["events"] == "double"])
        n_3b = len(hits[hits["events"] == "triple"])
        n_hr = len(hits[hits["events"] == "home_run"])
        tb = n_1b + 2 * n_2b + 3 * n_3b + 4 * n_hr
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


def batted_ball_profile(df: pd.DataFrame, t) -> dict:
    """Pull/Center/Oppo, GB/LD/FB, avg EV/LA."""
    bip = df.dropna(subset=["hc_x", "hc_y"]).copy()
    n = len(bip)
    if n == 0:
        return {}

    bip["spray_angle"] = np.degrees(
        np.arctan2(bip["hc_x"] - 125.42, 198.27 - bip["hc_y"])
    )
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
    """Classify count as ahead/behind/even for the hitter."""
    if balls > strikes:
        return "ahead"
    elif strikes > balls:
        return "behind"
    return "even"


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Cuba Scouting — WBC 2026",
        page_icon="\U0001F1E8\U0001F1FA",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # -- Premium dark theme CSS --
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

    # Sidebar
    lang = st.sidebar.radio("Language / \u8a00\u8a9e", ["JA", "EN"], horizontal=True)
    t = TEXTS[lang]

    # -- Hero banner --
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">{t['title']}</div>
        <div class="hero-sub">{t['subtitle']}</div>
        <div class="hero-badge">MLB Statcast 2024-2025</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"# \U0001F1E8\U0001F1FA {t['title']}")
    st.sidebar.caption(t["subtitle"])

    _name_ja_map = {p["name"]: p.get("name_ja", "") for p in CUBA_BATTERS}

    def _display_name(name):
        ja = _name_ja_map.get(name, "")
        if lang == "JA" and ja:
            return f"{ja}（{name}）"
        return name

    player_names = [t["team_overview"]] + [p["name"] for p in CUBA_BATTERS]
    selected = st.sidebar.selectbox(
        t["select_player"], player_names,
        format_func=lambda x: x if x == t["team_overview"] else _display_name(x),
    )

    df_all = load_data()

    seasons = sorted(df_all["season"].unique().tolist())
    season = st.sidebar.selectbox(t["season"], seasons, index=len(seasons) - 1, format_func=str)
    df_all = filter_season(df_all, season)

    # -----------------------------------------------------------------------
    # Team Overview
    # -----------------------------------------------------------------------
    if selected == t["team_overview"]:
        season_label = f"{season} Season" if lang == "EN" else f"{season}年シーズン"
        st.header(f"\U0001F1E8\U0001F1FA {t['team_overview']} — {season_label}")

        st.info(t["overview_guide"])

        rows = []
        player_stats_list = []
        for p in CUBA_BATTERS:
            pdf = df_all[df_all["batter"] == p["mlbam_id"]]
            if pdf.empty:
                continue
            s = batting_stats(pdf)
            rows.append({
                t["player"]: _display_name(p["name"]),
                "Pos": p["pos"],
                "Team": p["team"],
                "Bats": p["bats"],
                "PA": s["PA"],
                "AVG": s["AVG"],
                "OBP": s["OBP"],
                "SLG": s["SLG"],
                "OPS": s["OPS"],
                "HR": s["HR"],
                "K%": s["K%"],
                "BB%": s["BB%"],
                "xwOBA": s["xwOBA"],
            })
            # Compute platoon vulnerability for team weakness analysis
            _vs_l = pdf[pdf["p_throws"] == "L"]
            _vs_r = pdf[pdf["p_throws"] == "R"]
            _platoon_info = {}
            if not _vs_l.empty and not _vs_r.empty:
                _sl = batting_stats(_vs_l)
                _sr = batting_stats(_vs_r)
                if _sl["PA"] >= 30 and _sr["PA"] >= 30:
                    _pdiff = abs(_sl["OPS"] - _sr["OPS"]) * 1000
                    _platoon_info["platoon_diff"] = _pdiff
                    _platoon_info["platoon_weak_side"] = "LHP" if _sl["OPS"] < _sr["OPS"] else "RHP"
            player_stats_list.append({
                "name": _display_name(p["name"]),
                "pos": p["pos"],
                "team": p["team"],
                **s,
                **_platoon_info,
            })

        if rows:
            # --- TOP 3 Batters by OPS ---
            if player_stats_list:
                sorted_by_ops = sorted(
                    [ps for ps in player_stats_list if ps["PA"] >= 50],
                    key=lambda x: x["OPS"],
                    reverse=True,
                )
                top3 = sorted_by_ops[:3]
                if top3:
                    st.subheader(t["top3_title"])
                    st.caption(f"{season}" + (" season" if lang == "EN" else "\u5e74\u30b7\u30fc\u30ba\u30f3"))
                    cols = st.columns(len(top3))
                    avg_label = "AVG\uff08\u6253\u7387\uff09" if lang == "JA" else "AVG"
                    hr_label = "HR\uff08\u672c\u5851\u6253\uff09" if lang == "JA" else "HR"
                    xwoba_label = "xwOBA\uff08\u671f\u5f85\u6253\u6483\u5024\uff09" if lang == "JA" else "xwOBA"
                    _MLB_AVG_T3 = {"AVG": .243, "OBP": .312, "SLG": .397, "K%": 22.4, "BB%": 8.3}
                    for i, ps in enumerate(top3):
                        with cols[i]:
                            st.metric(ps["name"], f"OPS {ps['OPS']:.3f}")
                            st.caption(f"{ps['pos']} / {ps['team']}")
                            sub_cols = st.columns(3)
                            sub_cols[0].metric(avg_label, f"{ps['AVG']:.3f}")
                            sub_cols[1].metric(hr_label, str(ps["HR"]))
                            sub_cols[2].metric(xwoba_label, f"{ps['xwOBA']:.3f}" if ps["xwOBA"] else "\u2014")
                            # Mini radar chart per player
                            _t3_cats = ["AVG", "OBP", "SLG",
                                        "K%" if lang == "EN" else "\u4e09\u632f\u7387",
                                        "BB%" if lang == "EN" else "\u56db\u7403\u7387"]
                            _t3_pvals = [
                                min(ps["AVG"] / 0.300, 1.0),
                                min(ps["OBP"] / 0.380, 1.0),
                                min(ps["SLG"] / 0.500, 1.0),
                                1.0 - min(ps["K%"] / 35.0, 1.0),
                                min(ps["BB%"] / 15.0, 1.0),
                            ]
                            _t3_mvals = [
                                min(_MLB_AVG_T3["AVG"] / 0.300, 1.0),
                                min(_MLB_AVG_T3["OBP"] / 0.380, 1.0),
                                min(_MLB_AVG_T3["SLG"] / 0.500, 1.0),
                                1.0 - min(_MLB_AVG_T3["K%"] / 35.0, 1.0),
                                min(_MLB_AVG_T3["BB%"] / 15.0, 1.0),
                            ]
                            _t3_ang = np.linspace(0, 2 * np.pi, 5, endpoint=False).tolist()
                            _fig_t3, _ax_t3 = plt.subplots(figsize=(3, 3),
                                                            subplot_kw=dict(polar=True),
                                                            facecolor="#0e1117")
                            _ax_t3.set_facecolor("#0e1117")
                            _ax_t3.plot(_t3_ang + [_t3_ang[0]], _t3_mvals + [_t3_mvals[0]],
                                        "--", linewidth=1.2, color="#888888", alpha=0.7)
                            _ax_t3.fill(_t3_ang + [_t3_ang[0]], _t3_mvals + [_t3_mvals[0]],
                                        alpha=0.08, color="#888888")
                            _ax_t3.plot(_t3_ang + [_t3_ang[0]], _t3_pvals + [_t3_pvals[0]],
                                        "o-", linewidth=2, color="#4fc3f7")
                            _ax_t3.fill(_t3_ang + [_t3_ang[0]], _t3_pvals + [_t3_pvals[0]],
                                        alpha=0.25, color="#4fc3f7")
                            _ax_t3.set_thetagrids(np.degrees(_t3_ang), _t3_cats,
                                                  color="white", fontsize=8)
                            _ax_t3.set_ylim(0, 1)
                            _ax_t3.set_yticks([])
                            _ax_t3.grid(color="gray", alpha=0.3)
                            _ax_t3.spines["polar"].set_color("gray")
                            _fig_t3.tight_layout()
                            st.pyplot(_fig_t3, use_container_width=True)
                            plt.close(_fig_t3)

                # --- Team Batting Radar ---
                valid_stats = [ps for ps in player_stats_list if ps["PA"] >= 50]
                if valid_stats:
                    st.subheader(t["team_radar_title"])
                    avg_avg = np.mean([ps["AVG"] for ps in valid_stats])
                    avg_obp = np.mean([ps["OBP"] for ps in valid_stats])
                    avg_slg = np.mean([ps["SLG"] for ps in valid_stats])
                    avg_k = np.mean([ps["K%"] for ps in valid_stats])
                    avg_bb = np.mean([ps["BB%"] for ps in valid_stats])

                    # Normalize to 0-1 (MLB typical ranges)
                    norm_avg = min(avg_avg / 0.300, 1.0)
                    norm_obp = min(avg_obp / 0.380, 1.0)
                    norm_slg = min(avg_slg / 0.500, 1.0)
                    norm_k = 1.0 - min(avg_k / 35.0, 1.0)  # lower K% is better
                    norm_bb = min(avg_bb / 15.0, 1.0)

                    categories = ["AVG", "OBP", "SLG",
                                  "K%" if lang == "EN" else "\u4e09\u632f\u7387",
                                  "BB%" if lang == "EN" else "\u56db\u7403\u7387"]
                    values = [norm_avg, norm_obp, norm_slg, norm_k, norm_bb]
                    raw_values = [f"{avg_avg:.3f}", f"{avg_obp:.3f}", f"{avg_slg:.3f}",
                                 f"{avg_k:.1f}%", f"{avg_bb:.1f}%"]

                    # MLB average for radar overlay
                    mlb_avg = min(0.243 / 0.300, 1.0)
                    mlb_obp = min(0.312 / 0.380, 1.0)
                    mlb_slg = min(0.397 / 0.500, 1.0)
                    mlb_k = 1.0 - min(22.4 / 35.0, 1.0)
                    mlb_bb = min(8.3 / 15.0, 1.0)
                    mlb_values = [mlb_avg, mlb_obp, mlb_slg, mlb_k, mlb_bb]

                    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
                    values_plot = values + [values[0]]
                    angles_plot = angles + [angles[0]]
                    mlb_plot = mlb_values + [mlb_values[0]]

                    fig_radar, ax_radar = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True),
                                                       facecolor="#0e1117")
                    ax_radar.set_facecolor("#0e1117")
                    ax_radar.plot(angles_plot, mlb_plot, "--", linewidth=1.5, color="#888888",
                                  alpha=0.7, label="MLB avg")
                    ax_radar.fill(angles_plot, mlb_plot, alpha=0.08, color="#888888")
                    ax_radar.plot(angles_plot, values_plot, "o-", linewidth=2, color="#4fc3f7",
                                  label="Team avg" if lang == "EN" else "\u30c1\u30fc\u30e0\u5e73\u5747")
                    ax_radar.fill(angles_plot, values_plot, alpha=0.25, color="#4fc3f7")
                    ax_radar.set_thetagrids(np.degrees(angles), categories, color="white", fontsize=11)
                    ax_radar.set_ylim(0, 1)
                    ax_radar.set_yticks([0.25, 0.5, 0.75, 1.0])
                    ax_radar.set_yticklabels(["", "", "", ""], color="white")
                    ax_radar.grid(color="gray", alpha=0.3)
                    ax_radar.spines["polar"].set_color("gray")
                    for angle, val, raw in zip(angles, values, raw_values):
                        ax_radar.annotate(raw, xy=(angle, val), fontsize=9,
                                          ha="center", va="bottom", color="white",
                                          fontweight="bold")
                    leg = ax_radar.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1),
                                          fontsize=9, facecolor="#0e1117", edgecolor="gray")
                    for txt in leg.get_texts():
                        txt.set_color("white")
                    fig_radar.tight_layout()
                    st.pyplot(fig_radar, use_container_width=True)
                    plt.close(fig_radar)
                    low_k_note = ("Lower K% is better for batters. Gray dashed = MLB avg." if lang == "EN"
                                  else "\u4e09\u632f\u7387\u306f\u4f4e\u3044\u307b\u3069\u826f\u3044\uff08\u30b0\u30e9\u30d5\u3067\u306f\u4f4eK%\u307b\u3069\u5916\u5074\uff09\u3002\u7070\u8272\u7834\u7dda=MLB\u5e73\u5747\u3002")
                    st.caption(low_k_note)

            # --- Full Stats Table (in expander) ---
            with st.expander(t["full_stats_table"], expanded=False):
                with st.expander(t["glossary_stats"].split("**")[1].split("**")[0] + "..." if lang == "EN" else "\u7528\u8a9e\u306e\u8aac\u660e\u3092\u898b\u308b"):
                    st.markdown(t["glossary_stats"])
                    st.markdown(t["glossary_pct"])

                with st.expander(t["pos_glossary_label"]):
                    st.markdown(t["pos_glossary"])

                overview = pd.DataFrame(rows)
                if lang == "JA":
                    ja_cols = {
                        "Pos": "Pos\uff08\u5b88\u5099\uff09",
                        "Bats": "Bats\uff08\u6253\u5e2d\uff09",
                        "PA": "PA\uff08\u6253\u5e2d\uff09",
                        "AVG": "AVG\uff08\u6253\u7387\uff09",
                        "OBP": "OBP\uff08\u51fa\u5841\u7387\uff09",
                        "SLG": "SLG\uff08\u9577\u6253\u7387\uff09",
                        "OPS": "OPS\uff08\u51fa\u5841+\u9577\u6253\uff09",
                        "HR": "HR\uff08\u672c\u5851\u6253\uff09",
                        "K%": "K%\uff08\u4e09\u632f\u7387\uff09",
                        "BB%": "BB%\uff08\u56db\u7403\u7387\uff09",
                        "xwOBA": "xwOBA\uff08\u671f\u5f85\u6253\u6483\u5024\uff09",
                    }
                    overview = overview.rename(columns=ja_cols)
                    fmt = {ja_cols.get(k, k): v for k, v in {
                        "PA": "{:.0f}", "HR": "{:.0f}",
                        "AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}",
                        "OPS": "{:.3f}", "K%": "{:.1f}", "BB%": "{:.1f}",
                        "xwOBA": "{:.3f}",
                    }.items()}
                    ops_col = ja_cols["OPS"]
                    k_col = ja_cols["K%"]
                else:
                    fmt = {
                        "PA": "{:.0f}", "HR": "{:.0f}",
                        "AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}",
                        "OPS": "{:.3f}", "K%": "{:.1f}", "BB%": "{:.1f}",
                        "xwOBA": "{:.3f}",
                    }
                    ops_col = "OPS"
                    k_col = "K%"
                st.dataframe(
                    overview.style.format(fmt, na_rep="\u2014")
                    .background_gradient(subset=[ops_col], cmap="RdYlGn")
                    .background_gradient(subset=[k_col], cmap="RdYlGn_r"),
                    use_container_width=True,
                    hide_index=True,
                )

            st.subheader(t["team_strengths"])
            st.info(t["strength_note"])

            # --- Auto-detected team weaknesses ---
            st.subheader(t["team_weaknesses_title"])
            weakness_report = analyze_team_weaknesses(player_stats_list, lang)
            st.warning(weakness_report)
        else:
            st.warning(t["no_data"])
        return

    # -----------------------------------------------------------------------
    # Individual Scouting Report
    # -----------------------------------------------------------------------
    player = PLAYER_BY_NAME[selected]
    pdf = df_all[df_all["batter"] == player["mlbam_id"]]

    if pdf.empty:
        st.warning(t["no_data"])
        return

    stats = batting_stats(pdf)

    season_label = f"{season} Season" if lang == "EN" else f"{season}年シーズン"
    st.header(f"\U0001F1E8\U0001F1FA {_display_name(player['name'])} — {season_label}")
    c1, c2, c3 = st.columns(3)
    c1.metric(t["pos"], player["pos"])
    c2.metric(t["team"], player["team"])
    c3.metric(t["bats"], player["bats"])

    # MLB average benchmarks (2024 season)
    _MLB_AVG = {"AVG": .243, "OBP": .312, "SLG": .397, "OPS": .709, "xwOBA": .311}

    c4, c5, c6 = st.columns(3)
    c4.metric("AVG", f"{stats['AVG']:.3f}",
              delta=f"{stats['AVG'] - _MLB_AVG['AVG']:+.3f} (MLB avg: .{int(_MLB_AVG['AVG']*1000):03d})")
    c5.metric("OBP", f"{stats['OBP']:.3f}",
              delta=f"{stats['OBP'] - _MLB_AVG['OBP']:+.3f} (MLB avg: .{int(_MLB_AVG['OBP']*1000):03d})")
    c6.metric("SLG", f"{stats['SLG']:.3f}",
              delta=f"{stats['SLG'] - _MLB_AVG['SLG']:+.3f} (MLB avg: .{int(_MLB_AVG['SLG']*1000):03d})")
    c7, c8 = st.columns(2)
    c7.metric("OPS", f"{stats['OPS']:.3f}",
              delta=f"{stats['OPS'] - _MLB_AVG['OPS']:+.3f} (MLB avg: .{int(_MLB_AVG['OPS']*1000):03d})")
    if stats["xwOBA"]:
        c8.metric("xwOBA", f"{stats['xwOBA']:.3f}",
                  delta=f"{stats['xwOBA'] - _MLB_AVG['xwOBA']:+.3f} (MLB avg: .{int(_MLB_AVG['xwOBA']*1000):03d})")
    else:
        c8.metric("xwOBA", "\u2014")

    with st.expander("Stats glossary" if lang == "EN" else "\u7528\u8a9e\u306e\u8aac\u660e\u3092\u898b\u308b"):
        st.markdown(t["glossary_stats"])
        st.markdown(t["glossary_pct"])
        _bench_text = ("MLB avg (2024): AVG .243 / OBP .312 / SLG .397 / OPS .709 / xwOBA .311"
                       if lang == "EN" else
                       "MLB平均 (2024): AVG .243 / OBP .312 / SLG .397 / OPS .709 / xwOBA .311")
        st.caption(_bench_text)

    st.subheader(t["player_summary"])
    summary = generate_player_summary(stats, pdf, player, lang)
    st.info(summary)

    # --- Pitching Plan ---
    st.divider()
    st.subheader(t["pitching_plan_title"])
    st.caption(t["pitching_plan_explain"])
    pitching_plan = generate_pitching_plan(pdf, stats, player, lang)
    st.success(pitching_plan)

    # --- Defensive Positioning ---
    st.divider()
    st.subheader(t["defensive_positioning"])
    st.caption(t["defensive_explain"])
    defensive_pos = generate_defensive_positioning(pdf, player, lang)
    st.warning(defensive_pos)

    st.divider()

    # Individual Batting Radar
    _MLB_AVG_R = {"AVG": .243, "OBP": .312, "SLG": .397, "K%": 22.4, "BB%": 8.3}
    radar_categories = ["AVG", "OBP", "SLG",
                        "K%" if lang == "EN" else "\u4e09\u632f\u7387",
                        "BB%" if lang == "EN" else "\u56db\u7403\u7387"]
    player_vals = [
        min(stats["AVG"] / 0.300, 1.0),
        min(stats["OBP"] / 0.380, 1.0),
        min(stats["SLG"] / 0.500, 1.0),
        1.0 - min(stats["K%"] / 35.0, 1.0),
        min(stats["BB%"] / 15.0, 1.0),
    ]
    mlb_vals_r = [
        min(_MLB_AVG_R["AVG"] / 0.300, 1.0),
        min(_MLB_AVG_R["OBP"] / 0.380, 1.0),
        min(_MLB_AVG_R["SLG"] / 0.500, 1.0),
        1.0 - min(_MLB_AVG_R["K%"] / 35.0, 1.0),
        min(_MLB_AVG_R["BB%"] / 15.0, 1.0),
    ]
    raw_vals_r = [f"{stats['AVG']:.3f}", f"{stats['OBP']:.3f}", f"{stats['SLG']:.3f}",
                  f"{stats['K%']:.1f}%", f"{stats['BB%']:.1f}%"]
    angles_r = np.linspace(0, 2 * np.pi, len(radar_categories), endpoint=False).tolist()
    p_plot = player_vals + [player_vals[0]]
    m_plot = mlb_vals_r + [mlb_vals_r[0]]
    a_plot = angles_r + [angles_r[0]]
    fig_pr, ax_pr = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor="#0e1117")
    ax_pr.set_facecolor("#0e1117")
    ax_pr.plot(a_plot, m_plot, "--", linewidth=1.5, color="#888888", alpha=0.7, label="MLB avg")
    ax_pr.fill(a_plot, m_plot, alpha=0.08, color="#888888")
    ax_pr.plot(a_plot, p_plot, "o-", linewidth=2, color="#4fc3f7",
               label=_display_name(player["name"]))
    ax_pr.fill(a_plot, p_plot, alpha=0.25, color="#4fc3f7")
    ax_pr.set_thetagrids(np.degrees(angles_r), radar_categories, color="white", fontsize=11)
    ax_pr.set_ylim(0, 1)
    ax_pr.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax_pr.set_yticklabels(["", "", "", ""], color="white")
    ax_pr.grid(color="gray", alpha=0.3)
    ax_pr.spines["polar"].set_color("gray")
    for angle, val, raw in zip(angles_r, player_vals, raw_vals_r):
        ax_pr.annotate(raw, xy=(angle, val), fontsize=9,
                       ha="center", va="bottom", color="white", fontweight="bold")
    leg_pr = ax_pr.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1),
                          fontsize=9, facecolor="#0e1117", edgecolor="gray")
    for txt in leg_pr.get_texts():
        txt.set_color("white")
    fig_pr.tight_layout()
    st.pyplot(fig_pr, use_container_width=True)
    plt.close(fig_pr)
    st.caption("Gray dashed = MLB avg (2024). K% is inverted — lower is better." if lang == "EN"
               else "\u7070\u8272\u7834\u7dda=MLB\u5e73\u5747(2024)\u3002K%\u306f\u9006\u8ee2\u2014\u4f4e\u3044\u307b\u3069\u5916\u5074\u3002")

    st.divider()

    # Row 2: Zone Heatmaps (vertical layout for mobile)
    st.subheader(t["zone_heatmap"])
    st.caption(t["zone_caption"])
    st.caption(t["danger_zone"])
    for hm_metric, hm_title in [("ba", t["ba_heatmap"]), ("xwoba", t["xwoba_heatmap"])]:
        fig_hm, ax_hm = plt.subplots(figsize=(6, 5), facecolor="#0e1117")
        ax_hm.set_facecolor("#0e1117")
        ax_hm.tick_params(colors="white")
        ax_hm.xaxis.label.set_color("white")
        ax_hm.yaxis.label.set_color("white")
        ax_hm.title.set_color("white")
        im_hm = draw_zone_heatmap(pdf, hm_metric, hm_title, ax_hm)
        cb_hm = fig_hm.colorbar(im_hm, ax=ax_hm, fraction=0.046, pad=0.04)
        cb_hm.ax.tick_params(colors="white")
        fig_hm.tight_layout()
        st.pyplot(fig_hm, use_container_width=True)
        plt.close(fig_hm)

    # 3x3 Zone Chart (vertical layout for mobile)
    st.subheader(t["zone_3x3"])
    for z3_metric, z3_title in [("ba", t["ba_heatmap"]), ("xwoba", t["xwoba_heatmap"])]:
        fig_z3, ax_z3 = plt.subplots(figsize=(6, 5), facecolor="#0e1117")
        ax_z3.set_facecolor("#0e1117")
        ax_z3.tick_params(colors="white")
        ax_z3.xaxis.label.set_color("white")
        ax_z3.yaxis.label.set_color("white")
        ax_z3.title.set_color("white")
        im_z3 = draw_zone_3x3(pdf, z3_metric, z3_title, ax_z3)
        cb_z3 = fig_z3.colorbar(im_z3, ax=ax_z3, fraction=0.046, pad=0.04)
        cb_z3.ax.tick_params(colors="white")
        fig_z3.tight_layout()
        st.pyplot(fig_z3, use_container_width=True)
        plt.close(fig_z3)

    st.divider()

    # Row 3: Spray Chart + Batted Ball
    col_spray, col_bb = st.columns([3, 2])

    with col_spray:
        st.subheader(t["spray_chart"])
        st.caption(t["spray_caption"])
        stadium_keys = list(STADIUMS["EN"].keys())
        stadium_labels = [STADIUMS[lang][k] for k in stadium_keys]
        stadium_idx = st.selectbox(t["stadium"], range(len(stadium_keys)),
                                   format_func=lambda i: stadium_labels[i])
        stadium_key = stadium_keys[stadium_idx]
        show_density = st.checkbox(t["density_map"], value=True)

        fig_sp, ax_sp = plt.subplots(figsize=(5, 5), facecolor="#0e1117")
        ax_sp.set_facecolor("#0e1117")
        draw_spray_chart(pdf, player["name"], ax_sp, stadium=stadium_key,
                         density=show_density)
        fig_sp.tight_layout()
        st.pyplot(fig_sp, use_container_width=True)
        plt.close(fig_sp)

    with col_bb:
        st.subheader(t["batted_ball"])
        with st.expander("What do these mean?" if lang == "EN" else "\u7528\u8a9e\u306e\u8aac\u660e\u3092\u898b\u308b"):
            st.markdown(t["glossary_batted"])
        profile = batted_ball_profile(pdf, t)
        if profile:
            for k, v in profile.items():
                st.metric(k, v)
        else:
            st.write(t["no_data"])

    # Spray Chart: vs LHP / vs RHP
    spray_lhp = "Spray Chart \u2014 vs LHP" if lang == "EN" else "\u6253\u7403\u65b9\u5411\u56f3 \u2014 vs \u5de6\u6295\u624b"
    spray_rhp = "Spray Chart \u2014 vs RHP" if lang == "EN" else "\u6253\u7403\u65b9\u5411\u56f3 \u2014 vs \u53f3\u6295\u624b"
    col_sp_l, col_sp_r = st.columns(2)
    for col_sp, throws, sp_title in [(col_sp_l, "L", spray_lhp), (col_sp_r, "R", spray_rhp)]:
        with col_sp:
            split_sp = pdf[pdf["p_throws"] == throws]
            if split_sp.empty:
                st.write(t["no_data"])
                continue
            fig_sps, ax_sps = plt.subplots(figsize=(5, 5), facecolor="#0e1117")
            ax_sps.set_facecolor("#0e1117")
            draw_spray_chart(split_sp, sp_title, ax_sps, stadium=stadium_key,
                             density=show_density)
            fig_sps.tight_layout()
            st.pyplot(fig_sps, use_container_width=True)
            plt.close(fig_sps)

    st.divider()

    # Row 4: Pitch Type Performance
    st.subheader(t["pitch_type_perf"])
    st.caption(t["pitch_caption"])
    with st.expander("What are Whiff% and Chase%?" if lang == "EN" else "\u7a7a\u632f\u7387\u30fb\u30c1\u30a7\u30a4\u30b9\u7387\u3068\u306f\uff1f"):
        st.markdown(t["glossary_pitch"])

    pt_table = pitch_type_table(pdf, t)
    if not pt_table.empty:
        st.dataframe(pt_table, use_container_width=True, hide_index=True)

        chart_data = pt_table[[t["pitch_type"], t["whiff_pct"]]].copy()
        chart_data["whiff_val"] = chart_data[t["whiff_pct"]].str.rstrip("%").astype(float)
        chart_data = chart_data.sort_values("whiff_val", ascending=True)

        fig_pt, ax_pt = plt.subplots(figsize=(8, max(3, len(chart_data) * 0.5)), facecolor="#0e1117")
        ax_pt.set_facecolor("#0e1117")
        colors = plt.cm.RdYlGn_r(chart_data["whiff_val"] / max(chart_data["whiff_val"].max(), 1))
        bars = ax_pt.barh(chart_data[t["pitch_type"]], chart_data["whiff_val"], color=colors)
        for bar, val in zip(bars, chart_data["whiff_val"]):
            ax_pt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                       f"{val:.1f}%", va="center", ha="left", color="white",
                       fontsize=10, fontweight="bold")
        ax_pt.set_xlabel(t["whiff_pct"], color="white")
        ax_pt.tick_params(colors="white")
        ax_pt.set_title(t["whiff_pct"], color="white", fontweight="bold")
        x_max = chart_data["whiff_val"].max()
        ax_pt.set_xlim(0, x_max * 1.25 if x_max > 0 else 10)
        for spine in ax_pt.spines.values():
            spine.set_color("white")
        fig_pt.tight_layout()
        st.pyplot(fig_pt, use_container_width=True)
        plt.close(fig_pt)

    st.divider()

    # Row 5: Platoon Splits
    st.subheader(t["platoon"])
    st.caption(t["platoon_caption"])
    with st.expander("What are platoon splits?" if lang == "EN" else "\u5de6\u53f3\u6295\u624b\u5225\u6210\u7e3e\u3068\u306f\uff1f"):
        st.markdown(t["glossary_platoon"])

    col_l, col_r = st.columns(2)

    for col, throws, label in [(col_l, "L", t["vs_lhp"]), (col_r, "R", t["vs_rhp"])]:
        with col:
            st.markdown(f"**{label}**")
            split_df = pdf[pdf["p_throws"] == throws]
            if split_df.empty:
                st.write(t["no_data"])
                continue
            ss = batting_stats(split_df)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("AVG", f"{ss['AVG']:.3f}")
            m2.metric("OBP", f"{ss['OBP']:.3f}")
            m3.metric("SLG", f"{ss['SLG']:.3f}")
            m4.metric("OPS", f"{ss['OPS']:.3f}")

            fig_z, ax_z = plt.subplots(figsize=(5, 4), facecolor="#0e1117")
            ax_z.set_facecolor("#0e1117")
            ax_z.tick_params(colors="white")
            ax_z.xaxis.label.set_color("white")
            ax_z.yaxis.label.set_color("white")
            ax_z.title.set_color("white")
            draw_zone_heatmap(split_df, "ba", f"{label} \u2014 {t['ba_heatmap']}", ax_z)
            fig_z.tight_layout()
            st.pyplot(fig_z, use_container_width=True)
            plt.close(fig_z)

    st.divider()

    # Row 6: Count-based Performance
    st.subheader(t["count_perf"])
    st.caption(t["count_explain"])

    count_df = pdf.dropna(subset=["balls", "strikes"]).copy()
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
        cs = batting_stats(cdf)
        if cs["PA"] < 5:
            continue
        count_rows.append({
            ("Count" if lang == "EN" else "\u30ab\u30a6\u30f3\u30c8"): f"{b}-{s}",
            ("Type" if lang == "EN" else "\u5206\u985e"): tag,
            "PA": cs["PA"],
            "AVG": cs["AVG"],
            "OBP": cs["OBP"],
            "SLG": cs["SLG"],
            "OPS": cs["OPS"],
            "K%": cs["K%"],
            "BB%": cs["BB%"],
        })

    if count_rows:
        count_table = pd.DataFrame(count_rows)
        st.dataframe(
            count_table.style.format({
                "AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}",
                "OPS": "{:.3f}", "K%": "{:.1f}", "BB%": "{:.1f}",
            }).background_gradient(subset=["OPS"], cmap="RdYlGn"),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(t["glossary_count"])


if __name__ == "__main__":
    main()
