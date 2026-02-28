"""WBC 2026 Venezuela Pitching Scouting Dashboard."""

import pathlib

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import matplotlib_fontja  # noqa: F401 — enables Japanese font
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import gaussian_kde

from players import VENEZUELA_PITCHERS, PITCHER_BY_NAME

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
TEXTS = {
    "EN": {
        "title": "Venezuela Pitching Scouting Report",
        "subtitle": "WBC 2026 — Projected Quarterfinal Opponent Pitching Analysis",
        "select_pitcher": "Select Pitcher",
        "team_overview": "Staff Overview",
        "season": "Season",
        "profile": "Pitcher Profile",
        "team": "Team",
        "throws": "Throws",
        "role": "Role",
        "arsenal": "Pitch Arsenal",
        "pitch_type": "Pitch Type",
        "count": "Count",
        "usage_pct": "Usage%",
        "avg_velo": "Avg Velo (mph / km/h)",
        "max_velo": "Max Velo (mph / km/h)",
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
        "withdrawal_note": (
            "⚠️ Roster update (as of Mar 1): Pablo López (Twins) has withdrawn — Tommy John surgery, "
            "out for the 2026 season. Replaced by Jhonathan Díaz (Mariners). "
            "José Alvarado (Phillies) is ineligible due to insurance denial (forearm strain history). "
            "Replaced by Christian Suárez (Dodgers org, minor league). "
            "Oddanier Mosqueda (Pirates) also withdrew due to left forearm inflammation. "
            "Replaced by Luinder Ávila (Royals)."
        ),
        "strength_note": (
            "Venezuela's staff has undergone late roster changes. With Pablo López unavailable, "
            "the rotation relies on Eduardo Rodríguez and Antonio Senzatela as lead starters, "
            "supported by a bullpen mixing power arms. "
            "Jhonathan Díaz (Mariners) and Luinder Ávila (Royals) join as replacement arms. "
            "Left-handed depth includes Ranger Suárez (high GB%, elite contact management). "
            "Key vulnerabilities: several relievers rely heavily on fastballs and may be exposed "
            "by disciplined lineups that sit on velocity."
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
            "- **Opp AVG** = Opponents' batting average\n"
            "- **Opp SLG** = Opponents' slugging percentage\n"
            "- **K%** = Strikeout rate (strikeouts / plate appearances)\n"
            "- **BB%** = Walk rate (walks / plate appearances)\n"
            "- **xwOBA Against** = Expected weighted on-base average allowed (batted ball quality)"
        ),
        "glossary_arsenal": (
            "- **Usage%** = How often this pitch is thrown\n"
            "- **Avg Velo** = Average velocity (mph)\n"
            "- **Avg Spin** = Average spin rate (rpm)\n"
            "- **H-Break** = Horizontal movement (inches, glove side positive)\n"
            "- **V-Break** = Induced vertical break (inches)\n"
            "- **Whiff%** = Swing-and-miss rate\n"
            "- **Put Away%** = Rate of strikeouts when pitching with 2 strikes"
        ),
        "glossary_batted": (
            "- **GB%** = Ground ball rate\n- **LD%** = Line drive rate\n- **FB%** = Fly ball rate\n"
            "- **Avg EV Against** = Average exit velocity allowed (mph)\n"
            "- **Avg LA Against** = Average launch angle allowed (degrees)"
        ),
        "glossary_platoon": (
            "Platoon splits show how a pitcher performs against left-handed batters (LHB) "
            "vs right-handed batters (RHB). Large differences reveal matchup vulnerabilities."
        ),
        "glossary_movement": (
            "Each dot represents a pitch. Horizontal axis = glove-side break, "
            "vertical axis = induced vertical break. Pitches are colored by type."
        ),
        "pitcher": "Pitcher",
        "pitcher_summary": "Scouting Summary",
        "pitch_filter": "Filter by pitch type",
        "all_pitches": "All Pitches",
        "count_pitch_mix": "Pitch Mix by Count",
        "top3_title": "Top 3 Pitchers (by K%)",
        "team_radar_title": "Staff Pitching Profile",
        "full_stats_table": "Full Stats Table",
        "zone_caption": "Shows where pitches are located and how batters perform in each zone",
        "arsenal_caption": "Breakdown of each pitch type: velocity, movement, and swing-and-miss ability",
        "movement_caption": "Each dot is a pitch — shows how much each pitch type moves horizontally and vertically",
        "batted_ball_caption": "How opposing batters' batted balls behave against this pitcher",
        "platoon_caption": "Compares pitching stats against left-handed vs right-handed batters",
    },
    "JA": {
        "title": "ベネズエラ 投手スカウティングレポート",
        "subtitle": "WBC 2026 — 準々決勝（想定）対戦相手投手分析",
        "select_pitcher": "投手を選択",
        "team_overview": "投手陣概要",
        "season": "シーズン",
        "profile": "投手プロフィール",
        "team": "チーム",
        "throws": "投",
        "role": "役割",
        "arsenal": "球種構成",
        "pitch_type": "球種",
        "count": "投球数",
        "usage_pct": "使用率",
        "avg_velo": "平均球速 (mph / km/h)",
        "max_velo": "最高球速 (mph / km/h)",
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
        "pitches": "Pitches\uff08\u6295\u7403\u6570\uff09",
        "k_pct": "K%\uff08\u596a\u4e09\u632f\u7387\uff09",
        "bb_pct": "BB%\uff08\u4e0e\u56db\u7403\u7387\uff09",
        "opp_avg": "Opp AVG\uff08\u88ab\u6253\u7387\uff09",
        "opp_slg": "Opp SLG\uff08\u88ab\u9577\u6253\u7387\uff09",
        "xwoba_against": "xwOBA\uff08\u88ab\u671f\u5f85\u5024\uff09",
        "zone_3x3": "ゾーンチャート (3×3)",
        "team_strengths": "投手陣の強み・弱み",
        "withdrawal_note": (
            "⚠️ ロスター更新（3/1時点）: パブロ・ロペス（ツインズ）が辞退 — 右肘Tommy John手術、2026年全休見込み。"
            "代替: ジョナサン・ディアス（マリナーズ）。"
            "ホセ・アルバラード（フィリーズ）は保険適用拒否（左前腕既往歴）で出場不可。"
            "代替: クリスチャン・スアレス（ドジャース傘下・マイナー）。"
            "オダニエル・モスケダ（パイレーツ）も左前腕炎症で辞退。"
            "代替: ルインデル・アビラ（ロイヤルズ）。"
        ),
        "strength_note": (
            "ベネズエラ投手陣はロスター変更後、先発はエドゥアルド・ロドリゲスとアントニオ・センサテーラが軸。"
            "代替として加わったジョナサン・ディアス（マリナーズ）、ルインデル・アビラ（ロイヤルズ）がブルペンを補強。"
            "左腕はレンジャー・スアレスが中心（高いゴロ率、優れたコンタクト管理）。\n\n"
            "弱点: リリーフの一部は速球依存の傾向があり、"
            "速球を狙い打てる規律のある打線には対応を迫られる可能性がある。"
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
            "- **被打率（Opp AVG）** = 対戦打者の打率\n"
            "- **被長打率（Opp SLG）** = 対戦打者の長打率\n"
            "- **奪三振率（K%）** = 打席あたりの三振を奪う割合\n"
            "- **与四球率（BB%）** = 打席あたりの四球を与える割合\n"
            "- **被xwOBA** = 打球の質から算出した期待被出塁率（低いほど良い）"
        ),
        "glossary_arsenal": (
            "- **使用率** = その球種を投げる割合\n"
            "- **平均球速** = 平均的な球の速さ (mph)\n"
            "- **平均回転数** = 球の回転の速さ (rpm)\n"
            "- **横変化** = グラブ側への横の曲がり幅（インチ）\n"
            "- **縦変化** = 重力に逆らう縦の変化量（インチ）\n"
            "- **空振率（Whiff%）** = スイングに対する空振りの割合\n"
            "- **決め球率（Put Away%）** = 2ストライクから三振を奪う割合"
        ),
        "glossary_batted": (
            "- **ゴロ%** = ゴロの割合\n- **ライナー%** = ライナーの割合\n- **フライ%** = フライの割合\n"
            "- **被平均打球速度** = 打たれた打球のスピード (mph)\n"
            "- **被平均打球角度** = 打たれた打球の角度"
        ),
        "glossary_platoon": (
            "左右打者別成績は、左打者（LHB）と右打者（RHB）に対する投球成績です。"
            "左右で成績に大きな差がある投手は、苦手な打席の打者を並べられると不利になります。"
        ),
        "glossary_movement": (
            "各ドットが1球を表します。横軸 = グラブ側への曲がり、"
            "縦軸 = 重力に逆らう縦の変化量。球種ごとに色分けされています。"
        ),
        "pitcher": "投手",
        "pitcher_summary": "スカウティング要約",
        "pitch_filter": "球種で絞り込み",
        "all_pitches": "全球種",
        "count_pitch_mix": "カウント別 球種配分",
        "top3_title": "注目投手 TOP3（奪三振率順）",
        "team_radar_title": "投手陣の特徴",
        "full_stats_table": "詳細成績一覧",
        "zone_caption": "各ゾーンへの投球分布と、ゾーンごとの被打率を表示",
        "arsenal_caption": "球種ごとの球速・変化量・空振り率の詳細",
        "movement_caption": "各ドットが1球 — 球種ごとの縦横の変化量を可視化",
        "batted_ball_caption": "この投手に対する打球の傾向（ゴロ・ライナー・フライの割合）",
        "platoon_caption": "左打者と右打者、それぞれに対する投球成績の比較",
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
DATA_PATH = pathlib.Path(__file__).parent / "data" / "venezuela_pitchers_statcast.csv"


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

    # Whiff% (swing-and-miss rate)
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


def generate_pitcher_summary(stats: dict, pdf: pd.DataFrame, pitcher: dict,
                             lang: str) -> str:
    """Auto-generate a scouting summary for a pitcher."""
    strengths = []
    weaknesses = []

    # Strikeout ability
    if stats["K%"] >= 25.0:
        strengths.append("elite strikeout ability (K% 25+)" if lang == "EN"
                         else "三振を奪う能力が非常に高い（K% 25以上）")
    elif stats["K%"] >= 20.0:
        strengths.append("above-average strikeout rate" if lang == "EN"
                         else "平均以上の奪三振率")

    # Contact management
    if stats["Opp AVG"] <= 0.220:
        strengths.append(f"excellent contact management (Opp AVG .{int(stats['Opp AVG'] * 1000):03d})" if lang == "EN"
                         else f"被打率が非常に低い（被打率 .{int(stats['Opp AVG'] * 1000):03d}）")

    # xwOBA
    if stats["xwOBA"] and stats["xwOBA"] <= 0.290:
        strengths.append("low batted-ball quality allowed (xwOBA .290-)" if lang == "EN"
                         else "打球の質を抑えている（被xwOBA .290以下）")

    # Velocity
    if stats["Avg Velo"] and stats["Avg Velo"] >= 95.0:
        strengths.append(f"power arm (Avg Velo {stats['Avg Velo']:.1f} mph)" if lang == "EN"
                         else f"パワーアーム（平均球速 {stats['Avg Velo']:.1f} mph）")

    # Walk rate
    if stats["BB%"] >= 10.0:
        weaknesses.append(f"high walk rate (BB% {stats['BB%']:.1f})" if lang == "EN"
                          else f"四球が多い（与四球率 {stats['BB%']:.1f}%）")
    elif stats["BB%"] >= 8.0:
        weaknesses.append(f"moderate walk rate (BB% {stats['BB%']:.1f})" if lang == "EN"
                          else f"四球がやや多い（与四球率 {stats['BB%']:.1f}%）")

    # Low K rate
    if stats["K%"] < 15.0:
        weaknesses.append(f"low strikeout rate (K% {stats['K%']:.1f})" if lang == "EN"
                          else f"三振を奪えない（奪三振率 {stats['K%']:.1f}%）")

    # Platoon split
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
    """Return black for light cells (mid-range), white for dark cells."""
    norm = (val - vmin) / (vmax - vmin) if vmax > vmin else 0.5
    if 0.25 < norm < 0.65:
        return "black"
    return "white"


def draw_zone_heatmap(df: pd.DataFrame, metric: str, title: str, ax):
    """Draw a 5x5 heatmap over the strike zone."""
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

    # strike zone box
    rect = patches.Rectangle(
        (-0.83, 1.5), 1.66, 2.0,
        linewidth=2, edgecolor="black", facecolor="none",
    )
    ax.add_patch(rect)

    # annotate
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
    """Draw 3x3 zone chart using Statcast zone 1-9 (pitcher version)."""
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
        else:  # ba (opp BA)
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
    """Plot pitch movement (pfx_x vs pfx_z) colored by pitch type."""
    valid = df.dropna(subset=["pfx_x", "pfx_z", "pitch_type"]).copy()
    valid["pfx_x_in"] = valid["pfx_x"] * 12
    valid["pfx_z_in"] = valid["pfx_z"] * 12
    top_types = valid["pitch_type"].value_counts().head(8).index

    # Density contour per pitch type (clipped to each type's data range)
    if density:
        for pt in top_types:
            sub = valid[valid["pitch_type"] == pt]
            if len(sub) < 20:
                continue
            try:
                xy = np.vstack([sub["pfx_x_in"].values, sub["pfx_z_in"].values])
                kde = gaussian_kde(xy, bw_method=0.3)
                # Grid only within this pitch type's data range (no edge artifacts)
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
    """Build pitch arsenal summary table."""
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

        # put-away: K with 2 strikes
        two_strike = grp[(grp["strikes"] == 2)]
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


def batted_ball_against(df: pd.DataFrame, t) -> dict:
    """GB/LD/FB against, avg EV and LA against."""
    bb = df.dropna(subset=["bb_type"])
    n_bb = len(bb)
    if n_bb == 0:
        return {}

    return {
        t["gb_pct"]: f"{(bb['bb_type'] == 'ground_ball').sum() / n_bb * 100:.1f}%",
        t["ld_pct"]: f"{(bb['bb_type'] == 'line_drive').sum() / n_bb * 100:.1f}%",
        t["fb_pct"]: f"{(bb['bb_type'] == 'fly_ball').sum() / n_bb * 100:.1f}%",
        t["avg_ev"]: f"{df['launch_speed'].dropna().mean():.1f}" if df["launch_speed"].notna().any() else "—",
        t["avg_la"]: f"{df['launch_angle'].dropna().mean():.1f}" if df["launch_angle"].notna().any() else "—",
    }


def count_category(balls: int, strikes: int) -> str:
    if strikes > balls:
        return "ahead"  # pitcher ahead
    elif balls > strikes:
        return "behind"
    return "even"


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Venezuela Pitching — WBC 2026",
        page_icon="🇻🇪",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # -- Responsive CSS for mobile --
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Shrink metric cards */
        [data-testid="stMetric"] {
            padding: 0.3rem 0.4rem;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.75rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        /* Tighter column gaps */
        [data-testid="stHorizontalBlock"] {
            gap: 0.3rem !important;
        }
        /* Readable table text */
        .stDataFrame td, .stDataFrame th {
            font-size: 0.8rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    lang = st.sidebar.radio("Language / 言語", ["JA", "EN"], horizontal=True)
    t = TEXTS[lang]

    st.sidebar.markdown(f"# 🇻🇪 {t['title']}")
    st.sidebar.caption(t["subtitle"])

    _name_ja_map = {p["name"]: p.get("name_ja", "") for p in VENEZUELA_PITCHERS}

    def _display_name(name):
        ja = _name_ja_map.get(name, "")
        if lang == "JA" and ja:
            return f"{ja}（{name}）"
        return name

    pitcher_names = [t["team_overview"]] + [p["name"] for p in VENEZUELA_PITCHERS]
    selected = st.sidebar.selectbox(
        t["select_pitcher"], pitcher_names,
        format_func=lambda x: x if x == t["team_overview"] else _display_name(x),
    )

    df_all = load_data()

    seasons = sorted(df_all["season"].unique().tolist())
    season = st.sidebar.selectbox(t["season"], seasons, index=len(seasons) - 1, format_func=str)
    df_all = filter_season(df_all, season)

    # -----------------------------------------------------------------------
    # Staff Overview
    # -----------------------------------------------------------------------
    if selected == t["team_overview"]:
        season_label = f"{season} Season" if lang == "EN" else f"{season}年シーズン"
        st.header(f"🇻🇪 {t['team_overview']} — {season_label}")

        st.info(t["overview_guide"])
        st.warning(t["withdrawal_note"])

        rows = []
        pitcher_stats_list = []
        for p in VENEZUELA_PITCHERS:
            pdf = df_all[df_all["pitcher"] == p["mlbam_id"]]
            if pdf.empty:
                continue
            s = pitching_stats(pdf)
            role_label = t["sp"] if p["role"] == "SP" else t["rp"]
            rows.append({
                t["pitcher"]: _display_name(p["name"]),
                t["team"]: p["team"],
                t["throws"]: p["throws"],
                t["role"]: role_label,
                t["pitches"]: s["Pitches"],
                t["k_pct"]: s["K%"],
                t["bb_pct"]: s["BB%"],
                t["opp_avg"]: s["Opp AVG"],
                t["opp_slg"]: s["Opp SLG"],
                t["xwoba_against"]: s["xwOBA"],
                t["avg_velo"]: f"{s['Avg Velo']:.1f} / {s['Avg Velo'] * 1.609:.0f}" if s["Avg Velo"] else "\u2014",
            })
            pitcher_stats_list.append({
                "name": _display_name(p["name"]),
                "team": p["team"],
                "role": role_label,
                **s,
            })

        if rows:
            # --- TOP 3 Pitchers by K% ---
            if pitcher_stats_list:
                sorted_by_k = sorted(
                    [ps for ps in pitcher_stats_list if ps["PA"] >= 30],
                    key=lambda x: x["K%"],
                    reverse=True,
                )
                top3 = sorted_by_k[:3]
                if top3:
                    st.subheader(t["top3_title"])
                    st.caption(f"{season}" + (" season" if lang == "EN" else "\u5e74\u30b7\u30fc\u30ba\u30f3"))
                    opp_avg_label = "Opp AVG\uff08\u88ab\u6253\u7387\uff09" if lang == "JA" else t["opp_avg"]
                    bb_label = "BB%\uff08\u4e0e\u56db\u7403\u7387\uff09" if lang == "JA" else t["bb_pct"]
                    velo_label = "\u7403\u901f (mph)" if lang == "JA" else "Velo (mph)"
                    _MLB_AVG_T3P = {"K%": 22.4, "Whiff%": 25.0, "BB%": 8.3,
                                    "Opp AVG": .243, "xwOBA": .311, "Velo": 93.5}
                    cols = st.columns(len(top3))
                    for i, ps in enumerate(top3):
                        with cols[i]:
                            st.metric(ps["name"], f"K% {ps['K%']:.1f}%")
                            st.caption(f"{ps['role']} / {ps['team']}")
                            sub_cols = st.columns(3)
                            sub_cols[0].metric(opp_avg_label, f"{ps['Opp AVG']:.3f}")
                            sub_cols[1].metric(bb_label, f"{ps['BB%']:.1f}%")
                            velo_str = f"{ps['Avg Velo']:.1f}" if ps["Avg Velo"] else "\u2014"
                            sub_cols[2].metric(velo_label, velo_str)
                            if ps["Avg Velo"]:
                                sub_cols[2].caption(f"\u2248 {ps['Avg Velo'] * 1.609:.0f} km/h")
                            # Mini radar chart per pitcher
                            _t3_cats_p = ["K%", "Whiff%", "BB%",
                                          "Opp AVG" if lang == "EN" else "\u88ab\u6253\u7387",
                                          "xwOBA",
                                          "Velo" if lang == "EN" else "\u7403\u901f"]
                            _velo = ps["Avg Velo"] if ps["Avg Velo"] else 0
                            _xwoba = ps["xwOBA"] if ps["xwOBA"] else 0
                            _t3_pvals_p = [
                                min(ps["K%"] / 35.0, 1.0),
                                min(ps["Whiff%"] / 40.0, 1.0),
                                1.0 - min(ps["BB%"] / 15.0, 1.0),
                                1.0 - min(ps["Opp AVG"] / 0.300, 1.0),
                                1.0 - min(_xwoba / 0.400, 1.0) if _xwoba else 0,
                                min(_velo / 100.0, 1.0),
                            ]
                            _t3_mvals_p = [
                                min(_MLB_AVG_T3P["K%"] / 35.0, 1.0),
                                min(_MLB_AVG_T3P["Whiff%"] / 40.0, 1.0),
                                1.0 - min(_MLB_AVG_T3P["BB%"] / 15.0, 1.0),
                                1.0 - min(_MLB_AVG_T3P["Opp AVG"] / 0.300, 1.0),
                                1.0 - min(_MLB_AVG_T3P["xwOBA"] / 0.400, 1.0),
                                min(_MLB_AVG_T3P["Velo"] / 100.0, 1.0),
                            ]
                            _t3_ang_p = np.linspace(0, 2 * np.pi, 6, endpoint=False).tolist()
                            _fig_t3p, _ax_t3p = plt.subplots(figsize=(3, 3),
                                                              subplot_kw=dict(polar=True),
                                                              facecolor="#0e1117")
                            _ax_t3p.set_facecolor("#0e1117")
                            _ax_t3p.plot(_t3_ang_p + [_t3_ang_p[0]],
                                         _t3_mvals_p + [_t3_mvals_p[0]],
                                         "--", linewidth=1.2, color="#888888", alpha=0.7)
                            _ax_t3p.fill(_t3_ang_p + [_t3_ang_p[0]],
                                         _t3_mvals_p + [_t3_mvals_p[0]],
                                         alpha=0.08, color="#888888")
                            _ax_t3p.plot(_t3_ang_p + [_t3_ang_p[0]],
                                         _t3_pvals_p + [_t3_pvals_p[0]],
                                         "o-", linewidth=2, color="#ef5350")
                            _ax_t3p.fill(_t3_ang_p + [_t3_ang_p[0]],
                                         _t3_pvals_p + [_t3_pvals_p[0]],
                                         alpha=0.25, color="#ef5350")
                            _ax_t3p.set_thetagrids(np.degrees(_t3_ang_p), _t3_cats_p,
                                                   color="white", fontsize=8)
                            _ax_t3p.set_ylim(0, 1)
                            _ax_t3p.set_yticks([])
                            _ax_t3p.grid(color="gray", alpha=0.3)
                            _ax_t3p.spines["polar"].set_color("gray")
                            _fig_t3p.tight_layout()
                            st.pyplot(_fig_t3p, use_container_width=True)
                            plt.close(_fig_t3p)

                # --- Staff Pitching Radar ---
                valid_stats = [ps for ps in pitcher_stats_list if ps["PA"] >= 30]
                if valid_stats:
                    st.subheader(t["team_radar_title"])
                    avg_k = np.mean([ps["K%"] for ps in valid_stats])
                    avg_bb = np.mean([ps["BB%"] for ps in valid_stats])
                    avg_opp_avg = np.mean([ps["Opp AVG"] for ps in valid_stats])
                    avg_whiff = np.mean([ps["Whiff%"] for ps in valid_stats])
                    xwobas = [ps["xwOBA"] for ps in valid_stats if ps["xwOBA"] is not None]
                    avg_xwoba = np.mean(xwobas) if xwobas else 0
                    velos = [ps["Avg Velo"] for ps in valid_stats if ps["Avg Velo"]]
                    avg_velo = np.mean(velos) if velos else 0

                    norm_k = min(avg_k / 35.0, 1.0)
                    norm_whiff = min(avg_whiff / 40.0, 1.0)
                    norm_bb = 1.0 - min(avg_bb / 15.0, 1.0)
                    norm_opp_avg = 1.0 - min(avg_opp_avg / 0.300, 1.0)
                    norm_xwoba = 1.0 - min(avg_xwoba / 0.400, 1.0) if avg_xwoba else 0
                    norm_velo = min(avg_velo / 100.0, 1.0) if avg_velo else 0

                    categories = ["K%", "Whiff%", "BB%",
                                  "Opp AVG" if lang == "EN" else "被打率",
                                  "xwOBA",
                                  "Velo" if lang == "EN" else "球速"]
                    values = [norm_k, norm_whiff, norm_bb, norm_opp_avg, norm_xwoba, norm_velo]
                    raw_values = [f"{avg_k:.1f}%", f"{avg_whiff:.1f}%", f"{avg_bb:.1f}%",
                                 f"{avg_opp_avg:.3f}",
                                 f"{avg_xwoba:.3f}" if avg_xwoba else "—",
                                 f"{avg_velo:.1f} mph ({avg_velo * 1.609:.0f} km/h)" if avg_velo else "—"]

                    # MLB average for radar overlay
                    mlb_k = min(22.4 / 35.0, 1.0)
                    mlb_whiff = min(25.0 / 40.0, 1.0)
                    mlb_bb = 1.0 - min(8.3 / 15.0, 1.0)
                    mlb_opp_avg = 1.0 - min(0.243 / 0.300, 1.0)
                    mlb_xwoba = 1.0 - min(0.311 / 0.400, 1.0)
                    mlb_velo = min(93.5 / 100.0, 1.0)
                    mlb_values = [mlb_k, mlb_whiff, mlb_bb, mlb_opp_avg, mlb_xwoba, mlb_velo]

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
                    ax_radar.plot(angles_plot, values_plot, "o-", linewidth=2, color="#ef5350",
                                  label="Team avg" if lang == "EN" else "\u30c1\u30fc\u30e0\u5e73\u5747")
                    ax_radar.fill(angles_plot, values_plot, alpha=0.25, color="#ef5350")
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
                    radar_note = ("Outer = better. Gray dashed = MLB avg. BB%, Opp AVG, and xwOBA are inverted (lower is better)." if lang == "EN"
                                  else "\u5916\u5074\u307b\u3069\u826f\u3044\u3002\u7070\u8272\u7834\u7dda=MLB\u5e73\u5747\u3002BB%\u30fb\u88ab\u6253\u7387\u30fbxwOBA\u306f\u4f4e\u3044\u307b\u3069\u5916\u5074\u306b\u8868\u793a\u3002")
                    st.caption(radar_note)

            # --- Full Stats Table (in expander) ---
            with st.expander(t["full_stats_table"], expanded=False):
                with st.expander("Stats glossary" if lang == "EN" else "用語の説明を見る"):
                    st.markdown(t["glossary_stats"])

                overview = pd.DataFrame(rows)
                st.dataframe(
                    overview.style.format({
                        t["k_pct"]: "{:.1f}", t["bb_pct"]: "{:.1f}",
                        t["opp_avg"]: "{:.3f}", t["opp_slg"]: "{:.3f}",
                        t["xwoba_against"]: "{:.3f}",
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

    # Row 1: Profile — 2 rows
    season_label = f"{season} Season" if lang == "EN" else f"{season}年シーズン"
    st.header(f"🇻🇪 {_display_name(pitcher['name'])} — {season_label}")
    c1, c2, c3 = st.columns(3)
    c1.metric(t["team"], pitcher["team"])
    c2.metric(t["throws"], pitcher["throws"])
    c3.metric(t["role"], role_label)

    # MLB average benchmarks (2024 season) — for pitchers, lower is better except K%
    _MLB_AVG_P = {"Opp AVG": .243, "Opp SLG": .397, "K%": 22.4, "BB%": 8.3, "xwOBA": .311}

    c4, c5, c6 = st.columns(3)
    c4.metric(t["opp_avg"], f"{stats['Opp AVG']:.3f}",
              delta=f"{stats['Opp AVG'] - _MLB_AVG_P['Opp AVG']:+.3f} (MLB avg: .{int(_MLB_AVG_P['Opp AVG']*1000):03d})",
              delta_color="inverse")
    c5.metric(t["opp_slg"], f"{stats['Opp SLG']:.3f}",
              delta=f"{stats['Opp SLG'] - _MLB_AVG_P['Opp SLG']:+.3f} (MLB avg: .{int(_MLB_AVG_P['Opp SLG']*1000):03d})",
              delta_color="inverse")
    c6.metric(t["k_pct"], f"{stats['K%']:.1f}%",
              delta=f"{stats['K%'] - _MLB_AVG_P['K%']:+.1f}% (MLB avg: {_MLB_AVG_P['K%']:.1f}%)")
    c7, c8 = st.columns(2)
    c7.metric(t["bb_pct"], f"{stats['BB%']:.1f}%",
              delta=f"{stats['BB%'] - _MLB_AVG_P['BB%']:+.1f}% (MLB avg: {_MLB_AVG_P['BB%']:.1f}%)",
              delta_color="inverse")
    if stats["xwOBA"]:
        c8.metric(t["xwoba_against"], f"{stats['xwOBA']:.3f}",
                  delta=f"{stats['xwOBA'] - _MLB_AVG_P['xwOBA']:+.3f} (MLB avg: .{int(_MLB_AVG_P['xwOBA']*1000):03d})",
                  delta_color="inverse")
    else:
        c8.metric(t["xwoba_against"], "—")

    # Glossary
    with st.expander("Stats glossary" if lang == "EN" else "用語の説明を見る"):
        st.markdown(t["glossary_stats"])
        _bench_text_p = ("MLB avg (2024): Opp AVG .243 / Opp SLG .397 / K% 22.4% / BB% 8.3% / xwOBA .311"
                         if lang == "EN" else
                         "MLB平均 (2024): 被打率 .243 / 被長打率 .397 / K% 22.4% / BB% 8.3% / xwOBA .311")
        st.caption(_bench_text_p)

    # Pitcher summary
    st.subheader(t["pitcher_summary"])
    summary = generate_pitcher_summary(stats, pdf, pitcher, lang)
    st.info(summary)

    # Individual Pitcher Radar
    _MLB_AVG_PR = {"K%": 22.4, "Whiff%": 25.0, "BB%": 8.3,
                   "Opp AVG": .243, "xwOBA": .311, "Velo": 93.5}
    _pr_cats = ["K%", "Whiff%", "BB%",
                "Opp AVG" if lang == "EN" else "\u88ab\u6253\u7387",
                "xwOBA",
                "Velo" if lang == "EN" else "\u7403\u901f"]
    _avg_velo_p = stats["Avg Velo"] or 0
    _avg_whiff_p = stats["Whiff%"] or 0
    _avg_xwoba_p = stats["xwOBA"] or 0
    _pr_pvals = [
        min(stats["K%"] / 35.0, 1.0),
        min(_avg_whiff_p / 40.0, 1.0),
        1.0 - min(stats["BB%"] / 15.0, 1.0),
        1.0 - min(stats["Opp AVG"] / 0.300, 1.0),
        1.0 - min(_avg_xwoba_p / 0.400, 1.0) if _avg_xwoba_p else 0,
        min(_avg_velo_p / 100.0, 1.0),
    ]
    _pr_mvals = [
        min(_MLB_AVG_PR["K%"] / 35.0, 1.0),
        min(_MLB_AVG_PR["Whiff%"] / 40.0, 1.0),
        1.0 - min(_MLB_AVG_PR["BB%"] / 15.0, 1.0),
        1.0 - min(_MLB_AVG_PR["Opp AVG"] / 0.300, 1.0),
        1.0 - min(_MLB_AVG_PR["xwOBA"] / 0.400, 1.0),
        min(_MLB_AVG_PR["Velo"] / 100.0, 1.0),
    ]
    _pr_raw = [f"{stats['K%']:.1f}%",
               f"{_avg_whiff_p:.1f}%",
               f"{stats['BB%']:.1f}%",
               f"{stats['Opp AVG']:.3f}",
               f"{_avg_xwoba_p:.3f}" if _avg_xwoba_p else "\u2014",
               f"{_avg_velo_p:.1f} mph" if _avg_velo_p else "\u2014"]
    _pr_ang = np.linspace(0, 2 * np.pi, 6, endpoint=False).tolist()
    _pr_pp = _pr_pvals + [_pr_pvals[0]]
    _pr_mp = _pr_mvals + [_pr_mvals[0]]
    _pr_ap = _pr_ang + [_pr_ang[0]]
    fig_ipr, ax_ipr = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor="#0e1117")
    ax_ipr.set_facecolor("#0e1117")
    ax_ipr.plot(_pr_ap, _pr_mp, "--", linewidth=1.5, color="#888888", alpha=0.7, label="MLB avg")
    ax_ipr.fill(_pr_ap, _pr_mp, alpha=0.08, color="#888888")
    ax_ipr.plot(_pr_ap, _pr_pp, "o-", linewidth=2, color="#ef5350",
                label=_display_name(pitcher["name"]))
    ax_ipr.fill(_pr_ap, _pr_pp, alpha=0.25, color="#ef5350")
    ax_ipr.set_thetagrids(np.degrees(_pr_ang), _pr_cats, color="white", fontsize=11)
    ax_ipr.set_ylim(0, 1)
    ax_ipr.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax_ipr.set_yticklabels(["", "", "", ""], color="white")
    ax_ipr.grid(color="gray", alpha=0.3)
    ax_ipr.spines["polar"].set_color("gray")
    for angle, val, raw in zip(_pr_ang, _pr_pvals, _pr_raw):
        ax_ipr.annotate(raw, xy=(angle, val), fontsize=9,
                        ha="center", va="bottom", color="white", fontweight="bold")
    leg_ipr = ax_ipr.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1),
                            fontsize=9, facecolor="#0e1117", edgecolor="gray")
    for txt in leg_ipr.get_texts():
        txt.set_color("white")
    fig_ipr.tight_layout()
    st.pyplot(fig_ipr, use_container_width=True)
    plt.close(fig_ipr)
    st.caption("Gray dashed = MLB avg (2024). BB%, Opp AVG, xwOBA are inverted — lower is better." if lang == "EN"
               else "\u7070\u8272\u7834\u7dda=MLB\u5e73\u5747(2024)\u3002BB%\u30fb\u88ab\u6253\u7387\u30fbxwOBA\u306f\u9006\u8ee2\u2014\u4f4e\u3044\u307b\u3069\u5916\u5074\u3002")

    st.divider()

    # Row 2: Arsenal Table
    st.subheader(t["arsenal"])
    st.caption(t["arsenal_caption"])
    with st.expander("What do these columns mean?" if lang == "EN" else "各列の説明を見る"):
        st.markdown(t["glossary_arsenal"])
    at = arsenal_table(pdf, t)
    if not at.empty:
        st.dataframe(at, use_container_width=True, hide_index=True)

    st.divider()

    # Row 3: Movement Chart (full width, landscape)
    st.subheader(t["movement_chart"])
    st.caption(t["movement_caption"])
    with st.expander("How to read this chart" if lang == "EN" else "チャートの見方"):
        st.markdown(t["glossary_movement"])
    show_mvt_density = st.checkbox(
        "Density contour" if lang == "EN" else "密度等高線を表示",
        value=True, key="mvt_density",
    )
    fig_m, ax_m = plt.subplots(figsize=(8, 4), facecolor="#0e1117")
    ax_m.set_facecolor("#0e1117")
    for spine in ax_m.spines.values():
        spine.set_color("white")
    draw_movement_chart(pdf, pitcher["name"], ax_m, density=show_mvt_density)
    fig_m.tight_layout(rect=[0, 0, 0.82, 1])  # leave room for legend
    st.pyplot(fig_m, use_container_width=True)
    plt.close(fig_m)

    st.divider()

    # Row 3b: Batted Ball Against
    st.subheader(t["batted_ball"])
    st.caption(t["batted_ball_caption"])
    with st.expander("What do these mean?" if lang == "EN" else "用語の説明を見る"):
        st.markdown(t["glossary_batted"])
    bb_profile = batted_ball_against(pdf, t)
    if bb_profile:
        bb_cols = st.columns(len(bb_profile))
        for i, (k, v) in enumerate(bb_profile.items()):
            bb_cols[i].metric(k, v)
    else:
        st.write(t["no_data"])

    st.divider()

    # --- Pitch type filter (shared for heatmaps, zone, platoon, count) ---
    st.markdown(f"### {t['pitch_filter']}")
    avail_types = pdf.dropna(subset=["pitch_type"])["pitch_type"].value_counts().head(8).index.tolist()
    pitch_options = [t["all_pitches"]] + [PITCH_LABELS.get(pt, pt) for pt in avail_types]
    selected_pitch = st.selectbox(t["pitch_filter"], pitch_options, key="pitch_filter",
                                  label_visibility="collapsed")

    if selected_pitch == t["all_pitches"]:
        fdf = pdf  # filtered dataframe
    else:
        # reverse lookup from label to code
        label_to_code = {PITCH_LABELS.get(pt, pt): pt for pt in avail_types}
        fdf = pdf[pdf["pitch_type"] == label_to_code[selected_pitch]]

    pitch_suffix = f" — {selected_pitch}" if selected_pitch != t["all_pitches"] else ""

    # Zone Heatmaps (vertical layout for mobile)
    st.subheader(t["zone_heatmap"] + pitch_suffix)
    st.caption(t["zone_caption"])
    st.caption(t["danger_zone"])
    for hm_metric, hm_title in [("usage", t["usage_heatmap"]), ("ba", t["ba_heatmap"])]:
        fig_hm, ax_hm = plt.subplots(figsize=(6, 5), facecolor="#0e1117")
        ax_hm.set_facecolor("#0e1117")
        ax_hm.tick_params(colors="white")
        ax_hm.xaxis.label.set_color("white")
        ax_hm.yaxis.label.set_color("white")
        ax_hm.title.set_color("white")
        im_hm = draw_zone_heatmap(fdf, hm_metric, hm_title, ax_hm)
        cb_hm = fig_hm.colorbar(im_hm, ax=ax_hm, fraction=0.046, pad=0.04)
        cb_hm.ax.tick_params(colors="white")
        fig_hm.tight_layout()
        st.pyplot(fig_hm, use_container_width=True)
        plt.close(fig_hm)

    # 3x3 Zone Chart (vertical layout for mobile)
    st.subheader(t["zone_3x3"] + pitch_suffix)
    for z3_metric, z3_title in [("usage", t["usage_heatmap"]), ("ba", t["ba_heatmap"])]:
        fig_z3, ax_z3 = plt.subplots(figsize=(6, 5), facecolor="#0e1117")
        ax_z3.set_facecolor("#0e1117")
        ax_z3.tick_params(colors="white")
        ax_z3.xaxis.label.set_color("white")
        ax_z3.yaxis.label.set_color("white")
        ax_z3.title.set_color("white")
        im_z3 = draw_zone_3x3(fdf, z3_metric, z3_title, ax_z3)
        cb_z3 = fig_z3.colorbar(im_z3, ax=ax_z3, fraction=0.046, pad=0.04)
        cb_z3.ax.tick_params(colors="white")
        fig_z3.tight_layout()
        st.pyplot(fig_z3, use_container_width=True)
        plt.close(fig_z3)

    st.divider()

    # Row 5: Platoon Splits
    st.subheader(t["platoon"] + pitch_suffix)
    st.caption(t["platoon_caption"])
    with st.expander("What are platoon splits?" if lang == "EN" else "左右打者別成績とは？"):
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

            # mini zone heatmap
            fig_z, ax_z = plt.subplots(figsize=(5, 4), facecolor="#0e1117")
            ax_z.set_facecolor("#0e1117")
            ax_z.tick_params(colors="white")
            ax_z.xaxis.label.set_color("white")
            ax_z.yaxis.label.set_color("white")
            ax_z.title.set_color("white")
            draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_z)
            fig_z.tight_layout()
            st.pyplot(fig_z, use_container_width=True)
            plt.close(fig_z)

    st.divider()

    # Row 6: Count-based Performance — full count matrix
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
            ("Count" if lang == "EN" else "カウント"): f"{b}-{s}",
            ("Type" if lang == "EN" else "分類"): tag,
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

    # Count-by-pitch-type usage chart (stacked bar)
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
        fig_mix, ax_mix = plt.subplots(figsize=(8, 4), facecolor="#0e1117")
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
            # Add percentage label for segments >= 10%
            for i, v in enumerate(vals):
                if v >= 8:
                    ax_mix.text(x[i], bottoms[i] + v / 2, f"{v:.0f}%",
                                ha="center", va="center", fontsize=11,
                                fontweight="bold", color="white",
                                path_effects=[pe.withStroke(linewidth=2,
                                                            foreground="black")])
            bottoms += np.array(vals)

        ax_mix.set_xticks(x)
        ax_mix.set_xticklabels(count_labels, color="white", fontsize=13)
        ax_mix.set_ylabel("Usage %" if lang == "EN" else "\u4f7f\u7528\u7387 %",
                          color="white", fontsize=13)
        ax_mix.set_ylim(0, 105)
        ax_mix.tick_params(colors="white")
        for spine in ax_mix.spines.values():
            spine.set_color("white")
        leg_mix = ax_mix.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0),
                                fontsize=12, facecolor="#0e1117",
                                edgecolor="white", markerscale=2.0,
                                labelspacing=0.8, borderpad=0.8)
        for txt in leg_mix.get_texts():
            txt.set_color("white")
        fig_mix.tight_layout(rect=[0, 0, 0.82, 1])
        st.pyplot(fig_mix, use_container_width=True)
        plt.close(fig_mix)


if __name__ == "__main__":
    main()
