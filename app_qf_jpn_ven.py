"""WBC 2026 Quarterfinal: Japan vs Venezuela — Scouting Dashboard.

A unified scouting report for Japan's coaching staff, covering Venezuela's
predicted lineup, starting pitcher (Ranger Suárez), and bullpen.
All analysis is based on Venezuela players' MLB Statcast data (2024-2025).
"""

import pathlib

import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib_fontja  # noqa: F401 — enables Japanese font
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import gaussian_kde

from players import (
    PITCHER_BY_NAME,
    PLAYER_BY_NAME,
    VENEZUELA_BATTERS,
    VENEZUELA_PITCHERS,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
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

PREDICTED_LINEUP = [
    {"order": 1, "name": "Ronald Acuña Jr.", "pos": "RF", "note_en": "Elite speed + power, leadoff threat", "note_ja": "俊足強打のリードオフ"},
    {"order": 2, "name": "Luis Arráez", "pos": "1B", "note_en": "Best contact hitter in MLB, batting title contender", "note_ja": "MLB最高のコンタクトヒッター、首位打者候補"},
    {"order": 3, "name": "Eugenio Suárez", "pos": "3B", "note_en": "Corner infield power (3B), veteran slugger", "note_ja": "コーナー内野のパワーヒッター（三塁）"},
    {"order": 4, "name": "William Contreras", "pos": "C", "note_en": "Switch hitter, starting catcher", "note_ja": "スイッチヒッター、正捕手"},
    {"order": 5, "name": "Salvador Perez", "pos": "DH", "note_en": "Veteran power bat, 3x All-Star catcher as DH", "note_ja": "ベテランパワー打者、3度のオールスター捕手のDH起用"},
    {"order": 6, "name": "Jackson Chourio", "pos": "CF", "note_en": "Young star, 5-tool talent", "note_ja": "若き5ツールプレイヤー"},
    {"order": 7, "name": "Andrés Giménez", "pos": "2B", "note_en": "Gold Glove defense at 2B, switch hitter", "note_ja": "ゴールドグラブ級二塁守備、スイッチヒッター"},
    {"order": 8, "name": "Wilyer Abreu", "pos": "LF", "note_en": "Solid LHB, strong defense", "note_ja": "堅実な左打者、好守備"},
    {"order": 9, "name": "Ezequiel Tovar", "pos": "SS", "note_en": "Athletic SS, power potential", "note_ja": "身体能力の高い遊撃手、パワーも秘める"},
]

# Bench / Pinch-hit candidates
BENCH_PLAYERS = [
    {"name": "Willson Contreras", "role_en": "LHB pinch-hit option (3x All-Star catcher)", "role_ja": "左打ちの代打要員（元3度オールスター捕手）"},
    {"name": "Maikel Garcia", "role_en": "AVG .286, 16 HR, 23 SB, Gold Glove (2024)", "role_ja": "打率.286、16HR、23盗塁、ゴールドグラブ（2024）"},
    {"name": "Gleyber Torres", "role_en": "Utility infielder (2B/SS), former starter", "role_ja": "ユーティリティ内野手（二塁/遊撃）、元スタメン"},
    {"name": "Javier Sanoha", "role_en": "Minor league prospect, limited MLB data", "role_ja": "マイナーリーグ有望株、MLBデータ少"},
]

PREDICTED_SP = "Ranger Suárez"

KEY_RELIEVERS = ["José Buttó", "Eduard Bazardo", "Daniel Palencia", "Keider Montero", "Luinder Ávila"]

# MLB average benchmarks (2024 season)
_MLB_AVG_BAT = {"AVG": .243, "OBP": .312, "SLG": .397, "OPS": .709, "K%": 22.4, "BB%": 8.3, "xwOBA": .311}
_MLB_AVG_PIT = {"Opp AVG": .243, "Opp SLG": .397, "K%": 22.4, "BB%": 8.3, "xwOBA": .311, "Whiff%": 25.0, "Velo": 93.5}

# Stat help tooltips (bilingual) — shown as ? icon on st.metric
_STAT_HELP = {
    "EN": {
        "AVG": "Batting average — hits ÷ at-bats. MLB avg ≈ .243",
        "OBP": "On-base percentage — how often the batter reaches base. MLB avg ≈ .312",
        "SLG": "Slugging percentage — total bases ÷ at-bats. Measures power. MLB avg ≈ .397",
        "OPS": "OBP + SLG combined. Above .800 = strong hitter. MLB avg ≈ .709",
        "K%": "Strikeout rate — % of plate appearances ending in a strikeout. MLB avg ≈ 22.4%",
        "BB%": "Walk rate — % of plate appearances ending in a walk. MLB avg ≈ 8.3%",
        "xwOBA": "Expected weighted on-base average — combines exit velocity & launch angle to estimate true hitting quality. Removes luck. MLB avg ≈ .311",
        "Whiff%": "Whiff rate — swinging strikes ÷ total swings. Higher = harder to make contact. MLB avg ≈ 25%",
        "Chase%": "Chase rate — swings at pitches outside the strike zone ÷ pitches outside zone",
        "Opp AVG": "Opponent batting average — batting average allowed by the pitcher. MLB avg ≈ .243",
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
        "xwOBA": "期待加重出塁率 — 打球速度と角度から算出した「運を排除した」真の打撃力。MLB平均 ≈ .311",
        "Whiff%": "空振率 — スイング中の空振りの割合。高いほどコンタクトが難しい。MLB平均 ≈ 25%",
        "Chase%": "チェイス率 — ストライクゾーン外の球を振る割合",
        "Opp AVG": "被打率 — 投手が打たれた打率。MLB平均 ≈ .243",
        "Opp SLG": "被長打率 — 投手が許した長打率。MLB平均 ≈ .397",
        "Avg Velo": "平均球速（mph / km/h）",
        "Put Away%": "決め球成功率 — 2ストライク後に三振を取った割合",
    },
}


def _help(stat_key: str, lang: str) -> str:
    """Return tooltip help text for a stat."""
    return _STAT_HELP.get(lang, _STAT_HELP["EN"]).get(stat_key, "")


# ---------------------------------------------------------------------------
# Stadium data
# ---------------------------------------------------------------------------
STADIUM_SCALE = 2.495 / 2.33
STADIUM_CSV = pathlib.Path(__file__).parent / "data" / "mlbstadiums_wbc.csv"


@st.cache_data
def load_stadium_coords() -> pd.DataFrame:
    df = pd.read_csv(STADIUM_CSV)
    df["x"] = (df["x"] - 125) * STADIUM_SCALE + 125
    df["y"] = -((df["y"] - 199) * STADIUM_SCALE + 199)
    df["y"] = -df["y"]
    return df


# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
TEXTS = {
    "EN": {
        "page_title": "WBC 2026 QF: Japan vs Venezuela",
        "main_title": "WBC 2026 Quarterfinal: Japan vs Venezuela",
        "subtitle": "Mar 15 (Sun) 10:00 JST — LoanDepot Park, Miami",
        "tab1": "Matchup Overview",
        "tab2": "Lineup Scouting",
        "tab3": "Starting Pitcher",
        "tab4": "Bullpen Scouting",
        "season": "Season",
        "predicted_lineup": "Venezuela Predicted Starting Lineup",
        "predicted_sp": "Predicted Starting Pitcher",
        "pool_d_record": "Data Source: MLB Statcast (2024-2025 Regular Season)",
        "key_tendencies": "Team Characteristics",
        "tendency_text": (
            "- **1-2番:** Acuña Jr. (2024 SB 72, SLG .476) + Arráez (2024 AVG .314, K% 8.2%)\n"
            "- **3-4-5番:** E. Suárez + W. Contreras (2024 OPS .823) + S. Perez (2024 HR 29, RBI 104)\n"
            "- **6番:** Chourio (2024 AVG .275, 21HR, 26歳以下)\n"
            "- **7-9番:** Giménez (2024 DRS +9) + Tovar (2024 OPS .718)\n"
            "- **控え:** Willson Contreras (LHB), Maikel Garcia (.286/16HR), Torres\n"
            "- **Data Source:** All analysis based on MLB Statcast (2024-2025 regular season)"
        ),
        "order": "#", "pos": "Pos", "player": "Player", "note": "Note",
        "team": "Team", "bats": "Bats", "throws": "Throws", "role": "Role",
        "profile": "Player Profile",
        "scouting_summary": "Scouting Summary",
        "zone_heatmap": "Strike Zone Heatmap (BA)",
        "zone_3x3": "Zone Chart (3x3 BA)",
        "pitch_type_perf": "Performance by Pitch Type",
        "pitch_type": "Pitch Type", "count": "Count", "ba": "BA", "slg": "SLG",
        "whiff_pct": "Whiff%", "chase_pct": "Chase%",
        "platoon": "Platoon Splits",
        "vs_lhp": "vs LHP", "vs_rhp": "vs RHP",
        "vs_lhb": "vs LHB", "vs_rhb": "vs RHB",
        "no_data": "No data available for this selection.",
        "danger_zone": "BA = Batting Average (hits ÷ at-bats). Red = danger zone (high BA), Blue = attack zone (low BA)",
        "team_radar_title": "Team Batting Profile (Predicted Lineup)",
        "arsenal": "Pitch Arsenal",
        "usage_pct": "Usage%",
        "avg_velo": "Avg Velo (mph / km/h)",
        "max_velo": "Max Velo (mph / km/h)",
        "avg_spin": "Avg Spin (rpm)",
        "h_break": "Horizontal Break (inches)",
        "v_break": "Vertical Break (inches)",
        "put_away_pct": "Put Away%",
        "movement_chart": "Pitch Movement Chart",
        "movement_note": "Each dot = 1 pitch. Horizontal axis = glove-side break, vertical = induced vertical break.",
        "opp_avg": "Opp AVG", "opp_slg": "Opp SLG",
        "k_pct": "K%", "bb_pct": "BB%",
        "xwoba": "xwOBA",
        "where_to_attack": "Where to Attack",
        "bullpen_overview": "Bullpen Usage Pattern",
        "bullpen_text": (
            "- **Daniel Palencia** (RHP, Cubs) — ERA 2.91, 22 SV, avg 99.6 mph, K% 29.3%\n"
            "- **José Buttó** (RHP, Giants) — ERA 3.42, Whiff% 28.1%, avg 95.2 mph\n"
            "- **Eduard Bazardo** (RHP, Mariners) — ERA 3.18, 52.1 IP in 2024\n"
            "- **Keider Montero** (RHP, Tigers) — ERA 4.50, avg 93.8 mph\n"
            "- **Luinder Ávila** (RHP, Royals) — ERA 4.85, 37 IP in 2024\n"
            "- ⚠️ **Andrés Machado** (RHP, Orix Buffaloes) — NPB 2024: 28 SV, ERA 1.92. Statcastデータなし\n"
            "- MLB成績は全て2024-2025レギュラーシーズン（マチャドを除く）"
        ),
        "reliever_profile": "Reliever Profile",
        "sp_label": "Starter", "rp_label": "Reliever",
        "glossary_stats": (
            "- **AVG** = Batting Average\n"
            "- **OBP** = On-Base Percentage\n"
            "- **SLG** = Slugging Percentage\n"
            "- **OPS** = OBP + SLG\n"
            "- **xwOBA** = Expected Weighted On-Base Average"
        ),
        "glossary_pitch": (
            "- **Whiff%** = Swing-and-miss rate\n"
            "- **Chase%** = Swing rate on pitches outside the zone"
        ),
        "glossary_platoon": (
            "Platoon splits show performance vs left-handed vs right-handed pitchers/batters."
        ),
        "zone_heatmap_pitch": "Pitch Location Heatmap",
        "usage_heatmap": "Usage by Zone",
        "ba_heatmap": "Batting Avg by Zone",
        "xwoba_heatmap": "xwOBA by Zone",
        "zone_5x5": "Zone Heatmap (5x5)",
        "spray_chart": "Spray Chart",
        "spray_caption": "Shows where each batted ball landed on the field",
        "batted_ball": "Batted Ball Profile",
        "density_map": "Hit Density Map",
        "pull_pct": "Pull% (to batter's strong side)",
        "cent_pct": "Center%",
        "oppo_pct": "Oppo% (opposite field)",
        "gb_pct": "GB% (ground balls)",
        "ld_pct": "LD% (line drives)",
        "fb_pct": "FB% (fly balls)",
        "avg_ev": "Avg Exit Velocity (mph)",
        "avg_la": "Avg Launch Angle (deg)",
        "count_perf": "Performance by Count",
        "count_explain": (
            "Counts are written as **Balls-Strikes** (e.g. 3-1 means 3 balls, 1 strike).\n\n"
            "🟢 **Hitter Ahead** = more balls than strikes (e.g. 2-1, 3-0, 3-1). "
            "The pitcher must throw strikes to avoid a walk, so the batter can be selective and wait for a good pitch.\n\n"
            "🔴 **Hitter Behind** = more strikes than balls (e.g. 0-2, 1-2). "
            "The batter is closer to striking out and must protect the plate, giving the pitcher an advantage.\n\n"
            "🟡 **Even** = balls and strikes are equal (e.g. 1-1, 2-2). Neither side has a clear advantage."
        ),
        "ahead": "Hitter Ahead (Balls > Strikes)",
        "behind": "Hitter Behind (Strikes > Balls)",
        "even": "Even (Balls = Strikes)",
        "danger_zone_xwoba": "xwOBA = Expected Weighted On-Base Average — estimates true hitting quality from exit velocity & launch angle, removing luck. MLB avg ≈ .311. Red = high xwOBA (danger), Blue = low xwOBA (attack)",
        "glossary_batted": (
            "- **Pull%** = Percentage of batted balls hit to the batter's strong side (left field for right-handed batters)\n"
            "- **GB%** = Ground ball rate — balls hit on the ground toward infielders\n"
            "- **LD%** = Line drive rate — hard, flat hits that often become base hits\n"
            "- **FB%** = Fly ball rate — balls hit high into the air toward outfielders\n"
            "- **Avg Exit Velocity (EV)** = How hard the ball comes off the bat (mph). Higher = more power\n"
            "- **Avg Launch Angle (LA)** = The angle the ball leaves the bat (degrees). 10-25° is ideal for hits"
        ),
        "glossary_pct": "- **K%** = Strikeout rate (strikeouts / plate appearances)\n- **BB%** = Walk rate (walks / plate appearances)",
        "glossary_stats_title": "What do these stats mean?",
        "radar_explain": "Each axis shows a stat vs MLB average (gray). Farther from center = better. K% is inverted (lower = better).",
        "zone_explain": "Strike zone split into 9 areas. Red = batter hits well (danger). Green = batter struggles (attack here).",
        "spray_explain": "Where each batted ball landed. Red = HR, Orange = Extra-base hit, Green = Single, Gray = Out.",
        "platoon_explain": "Performance vs left-handed (LHP) and right-handed (RHP) pitchers. Most batters hit better against opposite-hand pitching.",
        "arsenal_explain": "Usage% = frequency thrown. Whiff% = swing-and-miss rate. Chase% = swing rate outside zone. Put Away% = strikeout rate on this pitch.",
        "zone_usage_explain": "Where pitches are thrown most often. Darker = more pitches in that zone.",
        "zone_opp_ba_explain": "Opponents' batting average by zone. Red = batters hit well (avoid). Green = effective zone (attack).",
        "platoon_pitcher_explain": "Performance against left-handed (LHB) vs right-handed (RHB) batters.",
        "glossary_arsenal_pct": (
            "- **Usage%** = Frequency this pitch is thrown\n"
            "- **Whiff%** = Swing-and-miss rate\n"
            "- **Chase%** = Swing rate on pitches outside the zone\n"
            "- **Put Away%** = Strikeout rate on this pitch"
        ),
        "pitch_selection_by_count": "Pitch Selection by Count",
        "pitch_selection_explain": (
            "Shows what pitch types the pitcher throws in different count situations. "
            "When the pitcher is ahead, expect more breaking balls and off-speed pitches. "
            "When behind, expect more fastballs — the pitcher needs a strike."
        ),
        "count_ahead_pitcher": "Pitcher Ahead (Strikes > Balls)",
        "count_behind_pitcher": "Pitcher Behind (Balls > Strikes)",
        "count_even_pitcher": "Even Count (Balls = Strikes)",
        "count_first_pitch": "First Pitch (0-0)",
        "count_two_strikes": "Two Strikes (0-2, 1-2, 2-2, 3-2 — all counts with 2 strikes)",
        "game_plan": "Game Plan: How Japan Wins",
        "game_plan_batting": "Batting Strategy vs Venezuela Pitching",
        "game_plan_pitching": "Pitching Strategy vs Venezuela Lineup",
        "team_weaknesses_title": "Venezuela Team Weaknesses",
        "pitching_plan_title": "How to Pitch to This Batter",
        "pitching_plan_explain": "Data-driven analysis of this batter's vulnerabilities — pitch types, zones, counts, and platoon splits.",
        "hitting_plan_title": "How to Hit This Pitcher",
        "hitting_plan_explain": "Data-driven approach guide — which pitches to look for, which to lay off, and optimal count strategy.",
        "pitching_plan_vs_lhp": "Approach with Left-Handed Pitcher",
        "pitching_plan_vs_rhp": "Approach with Right-Handed Pitcher",
        "hitting_plan_as_lhb": "Approach as Left-Handed Batter",
        "hitting_plan_as_rhb": "Approach as Right-Handed Batter",
        "defensive_positioning": "Defensive Positioning",
        "defensive_explain": "Recommended fielder alignment based on batted ball data (spray angle, ground ball rate, pull tendency).",
        "infield_shift": "Infield",
        "outfield_shift": "Outfield",
        "tab_gameplan": "Game Plan",
        "machado_warning": (
            "⚠️ **Andrés Machado (RHP, Orix Buffaloes — NPB)**\n\n"
            "- NPB 2024: 28 SV, ERA 1.92\n"
            "- **Statcastデータなし**（NPB所属 — MLBデータベースに記録なし）\n"
            "- NPB/KBO所属選手はStatcastベースの分析対象外"
        ),
        "bench_title": "Bench / Pinch-Hit Candidates",
        "gp_inning_1_3": "1st-3rd Inning: vs Suárez (Starter)",
        "gp_inning_4_5": "4th-5th Inning: SP Continuation or Bullpen Transition",
        "gp_inning_6_plus": "6th Inning+: Bullpen Back (High-Leverage)",
        "gp_pinch_hit": "Pinch-Hit Matchups (6th Inning+)",
        "gp_batting": "Batting Strategy",
        "gp_pitching": "Pitching Strategy",
        "gp_team_weakness": "Venezuela Team Weaknesses",
    },
    "JA": {
        "page_title": "WBC 2026 準々決勝: 日本 vs ベネズエラ",
        "main_title": "WBC 2026 準々決勝: 日本 vs ベネズエラ",
        "subtitle": "3月15日(日) 10:00 JST — ローンデポ・パーク（マイアミ）",
        "tab1": "対戦プレビュー",
        "tab2": "打線スカウティング",
        "tab3": "先発投手分析",
        "tab4": "ブルペン分析",
        "season": "シーズン",
        "predicted_lineup": "ベネズエラ 予想スタメン",
        "predicted_sp": "予想先発投手",
        "pool_d_record": "データ出典: MLB Statcast（2024-2025レギュラーシーズン）",
        "key_tendencies": "チームの特徴",
        "tendency_text": (
            "- **1-2番:** アクーニャJr.（2024 盗塁72, SLG .476）+ アラエス（2024 打率.314, 三振率8.2%）\n"
            "- **3-4-5番:** E.スアレス + W.コントレラス（2024 OPS .823）+ S.ペレス（2024 HR29, 打点104）\n"
            "- **6番:** チュリオ（2024 打率.275, 21HR, 26歳以下）\n"
            "- **7-9番:** ヒメネス（2024 DRS +9）+ トバー（2024 OPS .718）\n"
            "- **控え:** Willsonコントレラス（左打）、M.ガルシア（.286/16HR）、トーレス\n"
            "- **データソース:** 全分析はMLB Statcast（2024-2025レギュラーシーズン）に基づく"
        ),
        "order": "#", "pos": "守備", "player": "選手", "note": "備考",
        "team": "チーム", "bats": "打席", "throws": "投", "role": "役割",
        "profile": "選手プロフィール",
        "scouting_summary": "スカウティング要約",
        "zone_heatmap": "ストライクゾーン ヒートマップ（打率）",
        "zone_3x3": "ゾーンチャート (3x3 打率)",
        "pitch_type_perf": "球種別パフォーマンス",
        "pitch_type": "球種", "count": "投球数", "ba": "打率", "slg": "長打率",
        "whiff_pct": "空振率", "chase_pct": "チェイス率",
        "platoon": "左右投手別成績",
        "vs_lhp": "vs 左投手", "vs_rhp": "vs 右投手",
        "vs_lhb": "vs 左打者", "vs_rhb": "vs 右打者",
        "no_data": "データがありません。",
        "danger_zone": "BA = 打率（安打数÷打数）。赤 = 危険ゾーン（高打率）、青 = 攻めるゾーン（低打率）",
        "team_radar_title": "チーム打線の特徴（予想スタメン）",
        "arsenal": "球種構成",
        "usage_pct": "使用率",
        "avg_velo": "平均球速 (mph / km/h)",
        "max_velo": "最高球速 (mph / km/h)",
        "avg_spin": "平均回転数 (rpm)",
        "h_break": "横変化（インチ）",
        "v_break": "縦変化（インチ）",
        "put_away_pct": "決め球率",
        "movement_chart": "変化量チャート",
        "movement_note": "各ドット = 1球。横軸 = グラブ側への曲がり、縦軸 = 重力に逆らう縦の変化量。",
        "opp_avg": "被打率", "opp_slg": "被長打率",
        "k_pct": "奪三振率", "bb_pct": "与四球率",
        "xwoba": "xwOBA",
        "where_to_attack": "攻略ポイント",
        "bullpen_overview": "ブルペン運用パターン",
        "bullpen_text": (
            "- **ダニエル・パレンシア**（右腕、カブス） — 防御率2.91、22セーブ、平均球速99.6mph、奪三振率29.3%\n"
            "- **ホセ・ブット**（右腕、ジャイアンツ） — 防御率3.42、空振率28.1%、平均球速95.2mph\n"
            "- **エドゥアルド・バサルド**（右腕、マリナーズ） — 防御率3.18、2024年52.1イニング登板\n"
            "- **ケイダー・モンテロ**（右腕、タイガース） — 防御率4.50、平均球速93.8mph\n"
            "- **ルインデル・アビラ**（右腕、ロイヤルズ） — 防御率4.85、2024年37イニング\n"
            "- ⚠️ **アンドレス・マチャド**（右腕、オリックス） — NPB 2024: 28セーブ、防御率1.92。Statcastデータなし\n"
            "- MLB成績は全て2024-2025レギュラーシーズン（マチャドを除く）"
        ),
        "reliever_profile": "リリーフ投手プロフィール",
        "sp_label": "先発", "rp_label": "リリーフ",
        "glossary_stats": (
            "- **AVG（打率）** = 安打数 / 打数\n"
            "- **OBP（出塁率）** = 塁に出る割合\n"
            "- **SLG（長打率）** = 塁打数 / 打数\n"
            "- **OPS** = OBP + SLG\n"
            "- **xwOBA** = 打球の質から算出した期待値"
        ),
        "glossary_pitch": (
            "- **空振率（Whiff%）** = スイングに対する空振りの割合\n"
            "- **チェイス率（Chase%）** = ゾーン外の球に手を出す割合"
        ),
        "glossary_platoon": (
            "左右投手/打者に対する成績の比較。大きな差がある場合、マッチアップを活用可能。"
        ),
        "zone_heatmap_pitch": "配球ヒートマップ",
        "usage_heatmap": "ゾーン別投球分布",
        "ba_heatmap": "ゾーン別 打率",
        "xwoba_heatmap": "ゾーン別 xwOBA",
        "zone_5x5": "ゾーンヒートマップ (5x5)",
        "spray_chart": "スプレーチャート（打球方向図）",
        "spray_caption": "打球がフィールドのどこに飛んだかの分布図",
        "batted_ball": "打球傾向",
        "density_map": "打球密度マップ",
        "pull_pct": "プル%（引っ張り＝自分の力が入る方向への打球）",
        "cent_pct": "センター%（中堅方向への打球）",
        "oppo_pct": "逆方向%（流し打ち＝バットに当てて逆側へ運ぶ打球）",
        "gb_pct": "ゴロ%（地面を転がる打球）",
        "ld_pct": "ライナー%（低い弾道で鋭く飛ぶ打球）",
        "fb_pct": "フライ%（高く上がる打球）",
        "avg_ev": "平均打球速度（mph＝マイル毎時）",
        "avg_la": "平均打球角度（度）",
        "count_perf": "カウント別パフォーマンス",
        "count_explain": (
            "カウントは **ボール数-ストライク数** の順で表記します（例: 3-1 = 3ボール1ストライク）。\n\n"
            "🟢 **打者有利** = ボールがストライクより多い状態（例: 2-1, 3-0, 3-1）。"
            "投手は四球を避けるためにストライクを投げなければならず、打者は甘い球を待てます。\n\n"
            "🔴 **打者不利** = ストライクがボールより多い状態（例: 0-2, 1-2）。"
            "打者は三振が近いため、多少のボール球にも手を出さざるを得ず、投手が有利です。\n\n"
            "🟡 **イーブン** = ボールとストライクが同数（例: 1-1, 2-2）。どちらにも明確な有利はありません。"
        ),
        "ahead": "打者有利（ボール > ストライク）",
        "behind": "打者不利（ストライク > ボール）",
        "even": "イーブン（ボール = ストライク）",
        "danger_zone_xwoba": "xwOBA（期待加重出塁率）= 打球速度と角度から算出した「運を排除した」打撃の質。MLB平均 ≈ .311。赤 = 高xwOBA（危険）、青 = 低xwOBA（攻めるゾーン）",
        "glossary_batted": (
            "- **プル%** = 引っ張り方向（右打者なら左翼方向、左打者なら右翼方向）への打球割合\n"
            "- **ゴロ%** = 地面を転がる打球の割合。内野ゴロになりやすい\n"
            "- **ライナー%** = 低い弾道で鋭く飛ぶ打球の割合。最もヒットになりやすい打球\n"
            "- **フライ%** = 高く上がる打球の割合。本塁打か外野フライになりやすい\n"
            "- **平均打球速度（EV）** = バットから飛び出す打球の速さ（mph＝マイル毎時）。速いほどパワーがある\n"
            "- **平均打球角度（LA）** = 打球が飛び出す角度。10〜25°がヒットになりやすい最適角度"
        ),
        "glossary_pct": "- **K%（三振率）** = 打席に対する三振の割合\n- **BB%（四球率）** = 打席に対する四球の割合",
        "glossary_stats_title": "これらの指標の意味は？",
        "radar_explain": "各軸はMLB平均（灰色）と比較した成績。中心から遠いほど優秀。K%（三振率）は逆転表示—低いほど外側。",
        "zone_explain": "ストライクゾーンを9分割。赤 = 打者が得意なゾーン（投手にとって危険）。緑 = 打者が苦手なゾーン（攻めどころ）。",
        "spray_explain": "打球がフィールドのどこに飛んだかの分布。赤 = 本塁打、橙 = 長打（二塁打/三塁打）、緑 = 単打、灰 = アウト。",
        "platoon_explain": "左投手（LHP）・右投手（RHP）別の成績。多くの打者は反対の手の投手に強い傾向。",
        "arsenal_explain": "使用率 = この球種を投げる頻度。空振率 = スイングに対する空振りの割合。チェイス率 = ゾーン外の球を振る割合。決め球率 = この球種で三振を奪う割合。",
        "zone_usage_explain": "投球が多いゾーン。色が濃いほど投球数が多い。",
        "zone_opp_ba_explain": "ゾーン別の被打率。赤 = 打者が得意（避けるべき）。緑 = 有効なゾーン（攻める）。",
        "platoon_pitcher_explain": "左打者（LHB）・右打者（RHB）別の投球成績。",
        "glossary_arsenal_pct": (
            "- **使用率（Usage%）** = この球種を投げる頻度\n"
            "- **空振率（Whiff%）** = スイングに対する空振りの割合\n"
            "- **チェイス率（Chase%）** = ゾーン外の球に手を出す割合\n"
            "- **決め球率（Put Away%）** = この球種で三振を奪う割合"
        ),
        "pitch_selection_by_count": "カウント別球種選択",
        "pitch_selection_explain": (
            "カウント状況ごとに投手がどの球種を投げるかの分布です。"
            "投手有利では変化球・落ちる球が増え、投手不利ではストレート系が増える傾向があります。"
            "打席でどの球を予測すべきかの参考にしてください。"
        ),
        "count_ahead_pitcher": "投手有利（ストライク > ボール）",
        "count_behind_pitcher": "投手不利（ボール > ストライク）",
        "count_even_pitcher": "イーブン（ボール = ストライク）",
        "count_first_pitch": "初球 (0-0)",
        "count_two_strikes": "2ストライク（0-2, 1-2, 2-2, 3-2 — 2ストライクの全カウント）",
        "game_plan": "ゲームプラン: 日本の勝ち方",
        "game_plan_batting": "打撃戦略 — ベネズエラ投手陣攻略",
        "game_plan_pitching": "投手戦略 — ベネズエラ打線対策",
        "team_weaknesses_title": "ベネズエラ打線の弱点",
        "pitching_plan_title": "この打者の攻略法",
        "pitching_plan_explain": "球種・ゾーン・カウント・左右の弱点をデータから分析した投手への配球プラン。",
        "hitting_plan_title": "この投手の攻略法",
        "hitting_plan_explain": "狙う球種・見逃す球・カウント戦略をデータから分析した打撃アプローチ。",
        "pitching_plan_vs_lhp": "左投手で投げる場合の攻め方",
        "pitching_plan_vs_rhp": "右投手で投げる場合の攻め方",
        "hitting_plan_as_lhb": "左打者として打つ場合のアプローチ",
        "hitting_plan_as_rhb": "右打者として打つ場合のアプローチ",
        "defensive_positioning": "守備位置・シフト推奨",
        "defensive_explain": "打球データ（方向・ゴロ率・引っ張り傾向）に基づく守備配置の推奨。",
        "infield_shift": "内野",
        "outfield_shift": "外野",
        "tab_gameplan": "ゲームプラン",
        "machado_warning": (
            "⚠️ **アンドレス・マチャド（右腕、オリックス・バファローズ — NPB）**\n\n"
            "- NPB 2024: 28セーブ、防御率1.92\n"
            "- **Statcastデータなし**（NPB所属のためMLBデータベースに存在しない）\n"
            "- NPB/KBO所属選手はStatcast分析の対象外"
        ),
        "bench_title": "控え・代打候補",
        "gp_inning_1_3": "1〜3回: vs スアレス（先発）",
        "gp_inning_4_5": "4〜5回: 先発続投 or 中継ぎ移行",
        "gp_inning_6_plus": "6回以降: ブルペン後半（勝ちパターン）",
        "gp_pinch_hit": "代打マッチアップ（6回以降）",
        "gp_batting": "打撃戦略",
        "gp_pitching": "投球戦略",
        "gp_team_weakness": "ベネズエラ打線の弱点",
    },
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
DATA_DIR = pathlib.Path(__file__).parent / "data"
BATTER_CSV = DATA_DIR / "venezuela_statcast.csv"
PITCHER_CSV = DATA_DIR / "venezuela_pitchers_statcast.csv"


@st.cache_data
def load_batter_data() -> pd.DataFrame:
    df = pd.read_csv(BATTER_CSV, low_memory=False)
    df["game_date"] = pd.to_datetime(df["game_date"])
    if "season" not in df.columns:
        df["season"] = df["game_date"].dt.year
    return df


@st.cache_data
def load_pitcher_data() -> pd.DataFrame:
    df = pd.read_csv(PITCHER_CSV, low_memory=False)
    df["game_date"] = pd.to_datetime(df["game_date"])
    if "season" not in df.columns:
        df["season"] = df["game_date"].dt.year
    return df


def filter_season(df: pd.DataFrame, season) -> pd.DataFrame:
    return df[df["season"] == int(season)]


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------
_AB_EVENTS = {"single", "double", "triple", "home_run", "field_out",
              "strikeout", "grounded_into_double_play", "double_play",
              "force_out", "fielders_choice", "fielders_choice_out",
              "strikeout_double_play", "triple_play", "field_error"}
_PA_EVENTS = _AB_EVENTS | {"walk", "hit_by_pitch", "sac_fly", "sac_bunt",
                            "sac_fly_double_play", "catcher_interf",
                            "intent_walk"}
_HIT_EVENTS = {"single", "double", "triple", "home_run"}


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


def generate_sp_pitch_analysis(df: pd.DataFrame, lang: str) -> str:
    """Generate data-driven pitch usage analysis by count and batter side.

    Returns markdown text showing:
    - Overall pitch mix with usage %
    - Count-specific usage (first pitch, ahead, behind, 2-strike)
    - vs RHB / vs LHB zone + pitch tendencies
    """
    if df.empty or "pitch_type" not in df.columns:
        return ""

    lines = []
    total = len(df)

    # --- Overall pitch mix ---
    pt_counts = df["pitch_type"].dropna().value_counts()
    pt_total = pt_counts.sum()
    if pt_total == 0:
        return ""

    mix_items = []
    for pt, cnt in pt_counts.head(5).items():
        label = PITCH_LABELS.get(pt, pt)
        pct = cnt / pt_total * 100
        pt_df = df[df["pitch_type"] == pt]
        # whiff rate
        swing_events = {"hit_into_play", "foul", "swinging_strike",
                        "swinging_strike_blocked", "foul_tip",
                        "hit_into_play_score", "hit_into_play_no_out"}
        swings = pt_df[pt_df["description"].isin(swing_events)]
        whiffs = pt_df[pt_df["description"].isin({"swinging_strike", "swinging_strike_blocked"})]
        w_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0
        # batting average against this pitch type
        pt_evts = pt_df.dropna(subset=["events"])
        pt_ab = pt_evts[pt_evts["events"].isin(_AB_EVENTS)]
        pt_hits = pt_evts[pt_evts["events"].isin(_HIT_EVENTS)]
        ba_str = f".{int(len(pt_hits) / len(pt_ab) * 1000):03d}" if len(pt_ab) >= 10 else "—"
        if lang == "EN":
            mix_items.append(f"  - {label}: {pct:.0f}% usage, whiff {w_pct:.0f}%, opp BA {ba_str}")
        else:
            mix_items.append(f"  - {label}: 使用率{pct:.0f}%, 空振率{w_pct:.0f}%, 被打率{ba_str}")

    header = "**Pitch Mix (overall):**" if lang == "EN" else "**球種配分（全体）:**"
    lines.append(header)
    lines.extend(mix_items)

    # --- Count-specific usage ---
    if "balls" in df.columns and "strikes" in df.columns:
        def _count_mix(subset, label_text):
            if subset.empty:
                return None
            sub_counts = subset["pitch_type"].dropna().value_counts()
            sub_total = sub_counts.sum()
            if sub_total < 10:
                return None
            items = []
            for pt, cnt in sub_counts.head(3).items():
                lbl = PITCH_LABELS.get(pt, pt)
                items.append(f"{lbl} {cnt / sub_total * 100:.0f}%")
            return f"- **{label_text}:** {', '.join(items)} (n={sub_total})"

        first_pitch = df[(df["balls"] == 0) & (df["strikes"] == 0)]
        ahead = df[df["strikes"] > df["balls"]]
        behind = df[df["balls"] > df["strikes"]]
        two_strikes = df[df["strikes"] == 2]

        count_header = "**Count-specific pitch selection:**" if lang == "EN" else "**カウント別の球種選択:**"
        lines.append("")
        lines.append(count_header)

        fp_label = "First pitch (0-0)" if lang == "EN" else "初球 (0-0)"
        ah_label = "Pitcher ahead (S>B)" if lang == "EN" else "投手有利 (S>B)"
        bh_label = "Pitcher behind (B>S)" if lang == "EN" else "投手不利 (B>S)"
        ts_label = "2 strikes" if lang == "EN" else "2ストライク"

        for subset, lbl in [(first_pitch, fp_label), (ahead, ah_label),
                            (behind, bh_label), (two_strikes, ts_label)]:
            line = _count_mix(subset, lbl)
            if line:
                lines.append(line)

    # --- vs RHB / vs LHB ---
    if "stand" in df.columns:
        for side, side_label_en, side_label_ja in [("R", "vs RHB", "vs 右打者"), ("L", "vs LHB", "vs 左打者")]:
            side_df = df[df["stand"] == side]
            if len(side_df) < 20:
                continue

            # Overall opp BA for this side
            side_evts = side_df.dropna(subset=["events"])
            side_ab = side_evts[side_evts["events"].isin(_AB_EVENTS)]
            side_hits = side_evts[side_evts["events"].isin(_HIT_EVENTS)]
            side_ba = f".{int(len(side_hits) / len(side_ab) * 1000):03d}" if len(side_ab) >= 10 else "—"

            side_pt = side_df["pitch_type"].dropna().value_counts()
            side_total = side_pt.sum()
            if side_total < 20:
                continue

            # Top 3 pitches with usage % and per-pitch opp BA
            top3 = []
            for pt, cnt in side_pt.head(3).items():
                lbl = PITCH_LABELS.get(pt, pt)
                usage_pct = cnt / side_total * 100
                # per-pitch BA against this side
                pt_side = side_df[side_df["pitch_type"] == pt]
                pt_side_evts = pt_side.dropna(subset=["events"])
                pt_side_ab = pt_side_evts[pt_side_evts["events"].isin(_AB_EVENTS)]
                pt_side_hits = pt_side_evts[pt_side_evts["events"].isin(_HIT_EVENTS)]
                pt_ba = f".{int(len(pt_side_hits) / len(pt_side_ab) * 1000):03d}" if len(pt_side_ab) >= 5 else "—"
                top3.append(f"{lbl} {usage_pct:.0f}%(BA {pt_ba})")

            # Zone tendency (inner/outer/high/low)
            zone_text = ""
            if "plate_x" in side_df.columns and "plate_z" in side_df.columns:
                valid = side_df.dropna(subset=["plate_x", "plate_z"])
                if len(valid) >= 20:
                    if side == "R":
                        inner = valid[valid["plate_x"] < -0.3]
                        outer = valid[valid["plate_x"] > 0.3]
                    else:
                        inner = valid[valid["plate_x"] > 0.3]
                        outer = valid[valid["plate_x"] < -0.3]
                    high = valid[valid["plate_z"] > 2.8]
                    low = valid[valid["plate_z"] < 2.0]
                    inner_pct = len(inner) / len(valid) * 100
                    outer_pct = len(outer) / len(valid) * 100
                    high_pct = len(high) / len(valid) * 100
                    low_pct = len(low) / len(valid) * 100
                    if lang == "EN":
                        zone_text = f"\n  Zone: inner {inner_pct:.0f}%, outer {outer_pct:.0f}%, high {high_pct:.0f}%, low {low_pct:.0f}%"
                    else:
                        zone_text = f"\n  コース: 内角{inner_pct:.0f}%, 外角{outer_pct:.0f}%, 高め{high_pct:.0f}%, 低め{low_pct:.0f}%"

            side_label = side_label_en if lang == "EN" else side_label_ja
            ba_label = "Opp BA" if lang == "EN" else "被打率"
            lines.append(f"- **{side_label}** ({ba_label} {side_ba}, n={len(side_ab)}): {', '.join(top3)}{zone_text}")

    return "\n".join(lines)


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
                        f"(OPS .{int(weak_ops * 1000):03d})"
                    )
                else:
                    weak_ja = "左投手" if weak_side == "LHP" else "右投手"
                    weaknesses.append(
                        f"左右差が大きい — {weak_ja}に弱い "
                        f"（OPS .{int(weak_ops * 1000):03d}）"
                    )

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
                        f"(Opp AVG .{int(weak_avg * 1000):03d})"
                    )
                else:
                    weak_ja = "左打者" if weak_side == "LHB" else "右打者"
                    weaknesses.append(
                        f"左右差あり — {weak_ja}に打たれやすい "
                        f"（被打率 .{int(weak_avg * 1000):03d}）"
                    )

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
# Visualization helpers
# ---------------------------------------------------------------------------
def _dark_fig(figsize=(6, 5)):
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


def draw_zone_heatmap(df: pd.DataFrame, metric: str, title: str, ax, lang: str = "EN"):
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


def draw_zone_3x3(df: pd.DataFrame, metric: str, title: str, ax, lang: str = "EN"):
    """Draw 3x3 zone chart using Statcast zone 1-9."""
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

    if metric == "ba":
        vmin, vmax = 0, 0.450
    else:  # xwoba
        vmin, vmax = 0.150, 0.500

    for zone_num, (row, col) in zone_map.items():
        zdf = valid[valid["zone"] == zone_num]
        if metric == "ba":
            ab = zdf[zdf["events"].isin(_AB_EVENTS)]
            hits = zdf[zdf["events"].isin(_HIT_EVENTS)]
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


def draw_spray_chart(df: pd.DataFrame, title: str, ax, stadium: str = "marlins",
                     density: bool = False, lang: str = "EN"):
    """Draw spray chart on LoanDepot Park outline."""
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
        ax.scatter(row["hc_x"], row["hc_y"], c=row["color"], s=18, alpha=0.7,
                   edgecolors="none", zorder=row["zorder"])

    ax.set_xlim(0, 250)
    ax.set_ylim(220, -20)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=16, fontweight="bold", color="white")
    ax.axis("off")

    if lang == "JA":
        legend_labels = [("本塁打", "#e53935"), ("長打", "#ff9800"), ("単打", "#4caf50"), ("アウト", "#888888")]
    else:
        legend_labels = [("Home Run", "#e53935"), ("Extra-base Hit", "#ff9800"), ("Single", "#4caf50"), ("Out", "#888888")]
    for label, color in legend_labels:
        ax.scatter([], [], c=color, s=30, label=label)
    ax.legend(loc="upper right", fontsize=10, framealpha=0.6)


def draw_movement_chart(df: pd.DataFrame, title: str, ax, density: bool = True):
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
            t["avg_velo"]: f"{avg_velo:.1f} / {avg_velo * 1.609:.0f}" if avg_velo and not pd.isna(avg_velo) else "\u2014",
            t["max_velo"]: f"{max_velo:.1f} / {max_velo * 1.609:.0f}" if max_velo and not pd.isna(max_velo) else "\u2014",
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


def batted_ball_profile(df: pd.DataFrame, t) -> dict:
    """Pull/Center/Oppo, GB/LD/FB, avg EV/LA."""
    bip = df.dropna(subset=["hc_x", "hc_y"]).copy()
    n = len(bip)
    if n == 0:
        return {}

    # Spray angle: 0 = center, negative = pull for RHB, positive = pull for LHB
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


def _style_count_type(val, t):
    """Return CSS for count category cell — clean, corporate-style color coding."""
    if val == t["ahead"]:
        return "background-color: rgba(56, 142, 60, 0.50); color: #e8f5e9; font-weight: bold;"
    elif val == t["behind"]:
        return "background-color: rgba(211, 47, 47, 0.50); color: #ffebee; font-weight: bold;"
    elif val == t["even"]:
        return "background-color: rgba(245, 166, 35, 0.45); color: #fff8e1; font-weight: bold;"
    return ""


def pitch_selection_by_count(df: pd.DataFrame, t, lang: str):
    """Show pitch type distribution for different count situations."""
    valid = df.dropna(subset=["pitch_type", "balls", "strikes"]).copy()
    valid["balls"] = valid["balls"].astype(int)
    valid["strikes"] = valid["strikes"].astype(int)

    situations = {
        t["count_first_pitch"]: valid[(valid["balls"] == 0) & (valid["strikes"] == 0)],
        t["count_ahead_pitcher"]: valid[valid["strikes"] > valid["balls"]],
        t["count_behind_pitcher"]: valid[valid["balls"] > valid["strikes"]],
        t["count_even_pitcher"]: valid[(valid["balls"] == valid["strikes"]) & (valid["balls"] > 0)],
        t["count_two_strikes"]: valid[valid["strikes"] == 2],
    }

    rows = []
    for sit_name, sit_df in situations.items():
        if sit_df.empty:
            continue
        total = len(sit_df)
        top_types = sit_df["pitch_type"].value_counts().head(6)
        pitch_parts = []
        for pt, cnt in top_types.items():
            label = PITCH_LABELS.get(pt, pt)
            pct = cnt / total * 100
            pitch_parts.append(f"{label} {pct:.0f}%")
        rows.append({
            ("Situation" if lang == "EN" else "\u72b6\u6cc1"): sit_name,
            ("Pitches" if lang == "EN" else "\u7403\u6570"): total,
            ("Distribution" if lang == "EN" else "\u7403\u7a2e\u5206\u5e03"): " | ".join(pitch_parts),
        })

    if rows:
        return pd.DataFrame(rows)
    return pd.DataFrame()


def draw_pitch_selection_pies(df: pd.DataFrame, t, lang: str, st_container=None):
    """Draw pie charts for pitch selection by count situation.

    Uses a 3-column then 2-column grid for 5 situations.
    """
    import streamlit as _st
    container = st_container or _st

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

    # Filter out empty situations
    situations = [(name, sdf) for name, sdf in situations if not sdf.empty]
    if not situations:
        return

    # Layout: up to 3 per row
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
                    wedgeprops=dict(width=0.45, edgecolor="#0e1117", linewidth=1.5),
                )
                # Add percentage labels on wedges (only if >= 5%)
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

                # Legend below
                legend = ax_pie.legend(
                    wedges, labels, loc="center", bbox_to_anchor=(0.5, -0.08),
                    ncol=min(3, len(labels)), fontsize=9,
                    facecolor="#0e1117", edgecolor="gray", framealpha=0.9,
                )
                for txt in legend.get_texts():
                    txt.set_color("white")

                fig_pie.tight_layout()
                container_col = col
                container_col.pyplot(fig_pie, use_container_width=True)
                plt.close(fig_pie)
        idx += 3


def _zone_names_for_bats(bats: str, lang: str) -> dict:
    """Return zone names adjusted for batter handedness.

    Statcast zones 1-9 from catcher's POV:
      1 | 2 | 3   (top, catcher's left to right)
      4 | 5 | 6   (middle)
      7 | 8 | 9   (bottom)
    Catcher's left = 3rd base side = RHB inside / LHB outside.
    """
    if bats == "L":
        # LHB: catcher-left = outside, catcher-right = inside
        if lang == "JA":
            return {1: "高めアウト", 2: "高め真ん中", 3: "高めイン",
                    4: "真ん中アウト", 5: "ど真ん中", 6: "真ん中イン",
                    7: "低めアウト", 8: "低め真ん中", 9: "低めイン"}
        return {1: "Up-Away", 2: "Up-Mid", 3: "Up-In",
                4: "Mid-Away", 5: "Heart", 6: "Mid-In",
                7: "Down-Away", 8: "Down-Mid", 9: "Down-In"}
    # RHB (default): catcher-left = inside, catcher-right = outside
    if lang == "JA":
        return {1: "高めイン", 2: "高め真ん中", 3: "高めアウト",
                4: "真ん中イン", 5: "ど真ん中", 6: "真ん中アウト",
                7: "低めイン", 8: "低め真ん中", 9: "低めアウト"}
    return {1: "Up-In", 2: "Up-Mid", 3: "Up-Away",
            4: "Mid-In", 5: "Heart", 6: "Mid-Away",
            7: "Down-In", 8: "Down-Mid", 9: "Down-Away"}


# Swing descriptions (used across plan functions)
_SWING_DESCS = {"hit_into_play", "foul", "swinging_strike", "swinging_strike_blocked", "foul_tip"}
# Whiff descriptions — foul_tip is NOT a whiff in Statcast standard definition
_WHIFF_DESCS = {"swinging_strike", "swinging_strike_blocked"}


def generate_pitching_plan(pdf: pd.DataFrame, stats: dict, player_info: dict, lang: str) -> str:
    """Generate data-driven pitching plan for a batter.

    Analyzes: pitch type vulnerabilities, zone weaknesses, count tendencies,
    platoon splits, batted ball profile to produce actionable coaching advice.
    """
    lines = []
    bats = player_info.get("bats", "R")

    # 1. Pitch type vulnerability analysis
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
            pt_stats.append({
                "type": pt, "label": label, "count": len(grp),
                "ba": ba, "whiff": whiff_pct, "chase": chase_pct,
            })

        if pt_stats:
            best_whiff = sorted([p for p in pt_stats if p["whiff"] > 0], key=lambda x: x["whiff"], reverse=True)
            hittable = sorted([p for p in pt_stats if p["ba"] is not None], key=lambda x: x["ba"], reverse=True)
            best_chase = sorted([p for p in pt_stats if p["chase"] > 0], key=lambda x: x["chase"], reverse=True)

            if best_whiff:
                bw = best_whiff[0]
                if lang == "EN":
                    lines.append(f"- **Best strikeout pitch:** {bw['label']} (Whiff% {bw['whiff']:.1f}%)")
                else:
                    lines.append(f"- **決め球に最適:** {bw['label']}（空振率 {bw['whiff']:.1f}%）")

            if hittable and hittable[0]["ba"] is not None and hittable[0]["ba"] >= 0.280:
                h = hittable[0]
                if lang == "EN":
                    lines.append(f"- **Avoid:** {h['label']} — he hits it well (BA .{int(h['ba']*1000):03d})")
                else:
                    lines.append(f"- **要注意球種:** {h['label']} — 打率 .{int(h['ba']*1000):03d} で打たれている")

            if best_chase:
                bc = best_chase[0]
                if lang == "EN":
                    lines.append(f"- **Chase pitch:** {bc['label']} outside the zone (Chase% {bc['chase']:.1f}%)")
                else:
                    lines.append(f"- **ゾーン外で振らせる球:** {bc['label']}（チェイス率 {bc['chase']:.1f}%）")

    # 2. Zone weakness analysis (3x3) — handedness-adjusted names
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
            if lang == "EN":
                lines.append(f"- **Attack zones (low BA):** {weak_str}")
            else:
                lines.append(f"- **攻めるゾーン（低打率）:** {weak_str}")
        if strong_str:
            if lang == "EN":
                lines.append(f"- **Danger zones (high BA):** {strong_str}")
            else:
                lines.append(f"- **危険ゾーン（高打率）:** {strong_str}")

    # 3. Count situation analysis
    count_valid = pdf.dropna(subset=["balls", "strikes"]).copy()
    count_valid["balls"] = count_valid["balls"].astype(int)
    count_valid["strikes"] = count_valid["strikes"].astype(int)

    ahead_df = count_valid[count_valid["balls"] > count_valid["strikes"]]
    behind_df = count_valid[count_valid["strikes"] > count_valid["balls"]]
    two_strike_df = count_valid[count_valid["strikes"] == 2]

    ahead_stats = batting_stats(ahead_df) if not ahead_df.empty else None
    behind_stats = batting_stats(behind_df) if not behind_df.empty else None
    two_strike_stats = batting_stats(two_strike_df) if not two_strike_df.empty else None

    if ahead_stats and behind_stats and ahead_stats["PA"] >= 20 and behind_stats["PA"] >= 20:
        if ahead_stats["OPS"] >= 0.800 and behind_stats["OPS"] < 0.600:
            if lang == "EN":
                lines.append(f"- **Count split:** Ahead OPS .{int(ahead_stats['OPS']*1000):03d} / "
                           f"Behind OPS .{int(behind_stats['OPS']*1000):03d} — "
                           f"difference of {int((ahead_stats['OPS'] - behind_stats['OPS'])*1000)} pts")
            else:
                lines.append(f"- **カウント別OPS:** 有利 .{int(ahead_stats['OPS']*1000):03d} / "
                           f"不利 .{int(behind_stats['OPS']*1000):03d}（差 {int((ahead_stats['OPS'] - behind_stats['OPS'])*1000)} pts）")
        elif behind_stats["OPS"] >= 0.700:
            if lang == "EN":
                lines.append(f"- **Count split:** Behind OPS .{int(behind_stats['OPS']*1000):03d} — "
                           f"remains productive even when behind in count")
            else:
                lines.append(f"- **カウント別OPS:** 不利カウントでも OPS .{int(behind_stats['OPS']*1000):03d}")

    if two_strike_stats and two_strike_stats["PA"] >= 20:
        if two_strike_stats["K%"] >= 35:
            if lang == "EN":
                lines.append(f"- **2-strike K%:** {two_strike_stats['K%']:.1f}% "
                           f"(MLB avg with 2 strikes ≈ 30%)")
            else:
                lines.append(f"- **2ストライク後の三振率:** {two_strike_stats['K%']:.1f}%"
                           f"（MLB平均 約30%）")
        elif two_strike_stats["K%"] < 20:
            if lang == "EN":
                lines.append(f"- **2-strike K%:** {two_strike_stats['K%']:.1f}% — "
                           f"well below MLB avg (~30%)")
            else:
                lines.append(f"- **2ストライク後の三振率:** {two_strike_stats['K%']:.1f}%"
                           f"（MLB平均 約30% を大きく下回る）")

    # 4. Platoon recommendation
    vs_l = pdf[pdf["p_throws"] == "L"]
    vs_r = pdf[pdf["p_throws"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        sl = batting_stats(vs_l)
        sr = batting_stats(vs_r)
        if sl["PA"] >= 30 and sr["PA"] >= 30:
            if sl["OPS"] < sr["OPS"] - 0.080:
                if lang == "EN":
                    lines.append(f"- **Platoon split:** vs LHP OPS .{int(sl['OPS']*1000):03d} / "
                               f"vs RHP OPS .{int(sr['OPS']*1000):03d} (diff {int((sr['OPS']-sl['OPS'])*1000)} pts)")
                else:
                    lines.append(f"- **左右別OPS:** 左投手 .{int(sl['OPS']*1000):03d} / "
                               f"右投手 .{int(sr['OPS']*1000):03d}（差 {int((sr['OPS']-sl['OPS'])*1000)} pts）")
            elif sr["OPS"] < sl["OPS"] - 0.080:
                if lang == "EN":
                    lines.append(f"- **Platoon split:** vs RHP OPS .{int(sr['OPS']*1000):03d} / "
                               f"vs LHP OPS .{int(sl['OPS']*1000):03d} (diff {int((sl['OPS']-sr['OPS'])*1000)} pts)")
                else:
                    lines.append(f"- **左右別OPS:** 右投手 .{int(sr['OPS']*1000):03d} / "
                               f"左投手 .{int(sl['OPS']*1000):03d}（差 {int((sl['OPS']-sr['OPS'])*1000)} pts）")

    # 5. Batted ball tendency
    bip = pdf.dropna(subset=["hc_x", "hc_y"]).copy()
    if len(bip) >= 20:
        bip["spray_angle"] = np.degrees(np.arctan2(bip["hc_x"] - 125.42, 198.27 - bip["hc_y"]))
        if bats == "R":
            pull_pct = (bip["spray_angle"] < -15).sum() / len(bip) * 100
        else:
            pull_pct = (bip["spray_angle"] > 15).sum() / len(bip) * 100

        bb_types = pdf.dropna(subset=["bb_type"])
        if len(bb_types) >= 20:
            gb_pct = (bb_types["bb_type"] == "ground_ball").sum() / len(bb_types) * 100
            fb_pct = (bb_types["bb_type"] == "fly_ball").sum() / len(bb_types) * 100

            if pull_pct >= 45:
                if lang == "EN":
                    lines.append(f"- **Pull%:** {pull_pct:.0f}% (MLB avg ~40%)")
                else:
                    lines.append(f"- **引っ張り率:** {pull_pct:.0f}%（MLB平均 約40%）")

            if gb_pct >= 50:
                if lang == "EN":
                    lines.append(f"- **GB%:** {gb_pct:.0f}% (MLB avg ~43%)")
                else:
                    lines.append(f"- **ゴロ率:** {gb_pct:.0f}%（MLB平均 約43%）")
            elif fb_pct >= 45:
                if lang == "EN":
                    lines.append(f"- **FB%:** {fb_pct:.0f}% (MLB avg ~35%)")
                else:
                    lines.append(f"- **フライ率:** {fb_pct:.0f}%（MLB平均 約35%）")

    if not lines:
        if lang == "EN":
            return "- No statistically significant vulnerabilities detected in the data."
        else:
            return "- データ上、統計的に有意な弱点は検出されず。"

    return "\n".join(lines)


def generate_hitting_plan(pdf: pd.DataFrame, stats: dict, pitcher_info: dict, lang: str) -> str:
    """Generate data-driven hitting plan against a pitcher.

    Analyzes: pitch arsenal weaknesses, hittable zones, count tendencies,
    platoon splits to produce actionable batting advice.
    """
    lines = []

    # 1. Pitch type vulnerability (what batters hit well)
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
            pt_stats.append({
                "type": pt, "label": label, "count": len(grp), "usage": usage,
                "ba": ba, "whiff": whiff_pct,
            })

        if pt_stats:
            hittable = sorted([p for p in pt_stats if p["ba"] is not None], key=lambda x: x["ba"], reverse=True)
            best_pitch = sorted([p for p in pt_stats if p["whiff"] > 0], key=lambda x: x["whiff"], reverse=True)
            primary = sorted(pt_stats, key=lambda x: x["usage"], reverse=True)

            if primary:
                pr = primary[0]
                if lang == "EN":
                    lines.append(f"- **Primary pitch:** {pr['label']} ({pr['usage']:.0f}% usage)")
                else:
                    lines.append(f"- **主要球種:** {pr['label']}（使用率 {pr['usage']:.0f}%）")

            if hittable and hittable[0]["ba"] is not None and hittable[0]["ba"] >= 0.250:
                h = hittable[0]
                if lang == "EN":
                    lines.append(f"- **Highest opp BA pitch:** {h['label']} (BA .{int(h['ba']*1000):03d})")
                else:
                    lines.append(f"- **被打率が最も高い球種:** {h['label']}（被打率 .{int(h['ba']*1000):03d}）")

            if best_pitch:
                bp = best_pitch[0]
                if lang == "EN":
                    lines.append(f"- **Best strikeout pitch:** {bp['label']} (Whiff% {bp['whiff']:.1f}%)")
                else:
                    lines.append(f"- **最も空振りを取る球種:** {bp['label']}（空振率 {bp['whiff']:.1f}%）")

    # 2. Zone vulnerability — pitcher context: use "R" default (zone names are relative to generic batter POV)
    zone_valid = pdf.dropna(subset=["zone"]).copy()
    zone_valid["zone"] = zone_valid["zone"].astype(int)
    # For pitcher analysis, zone names use catcher's perspective labels (no in/out flip)
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
            if lang == "EN":
                lines.append(f"- **High opp BA zones:** {hit_str}")
            else:
                lines.append(f"- **被打率が高いゾーン:** {hit_str}")
        if tough_str:
            if lang == "EN":
                lines.append(f"- **Low opp BA zones:** {tough_str}")
            else:
                lines.append(f"- **被打率が低いゾーン:** {tough_str}")

    # 3. Count strategy
    count_valid = pdf.dropna(subset=["balls", "strikes"]).copy()
    count_valid["balls"] = count_valid["balls"].astype(int)
    count_valid["strikes"] = count_valid["strikes"].astype(int)

    p_ahead = count_valid[count_valid["strikes"] > count_valid["balls"]]
    p_behind = count_valid[count_valid["balls"] > count_valid["strikes"]]

    if not p_ahead.empty and not p_behind.empty:
        pa_stats = pitching_stats(p_ahead) if len(p_ahead) >= 30 else None
        pb_stats = pitching_stats(p_behind) if len(p_behind) >= 30 else None

        if pa_stats and pb_stats:
            if pb_stats["Opp AVG"] >= 0.280:
                if lang == "EN":
                    lines.append(f"- **Pitcher behind in count:** Opp AVG .{int(pb_stats['Opp AVG']*1000):03d}")
                else:
                    lines.append(f"- **投手不利カウント時の被打率:** .{int(pb_stats['Opp AVG']*1000):03d}")

            if pa_stats["K%"] >= 30:
                if lang == "EN":
                    lines.append(f"- **Pitcher ahead in count:** K% {pa_stats['K%']:.1f}%")
                else:
                    lines.append(f"- **投手有利カウント時の奪三振率:** {pa_stats['K%']:.1f}%")

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

            if lang == "EN":
                lines.append(f"- **First pitch:** {label} {top_fp_pct:.0f}%. "
                           f"First-pitch strike rate: {fp_strike_pct:.0f}%")
            else:
                lines.append(f"- **初球:** {label} {top_fp_pct:.0f}%。"
                           f"初球ストライク率: {fp_strike_pct:.0f}%")

    # 5. Platoon recommendation
    vs_l = pdf[pdf["stand"] == "L"]
    vs_r = pdf[pdf["stand"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        sl = pitching_stats(vs_l)
        sr = pitching_stats(vs_r)
        if sl["PA"] >= 20 and sr["PA"] >= 20:
            if sl["Opp AVG"] > sr["Opp AVG"] + 0.030:
                if lang == "EN":
                    lines.append(f"- **Platoon split:** vs LHB Opp AVG .{int(sl['Opp AVG']*1000):03d} / "
                               f"vs RHB .{int(sr['Opp AVG']*1000):03d}")
                else:
                    lines.append(f"- **左右別被打率:** 左打者 .{int(sl['Opp AVG']*1000):03d} / "
                               f"右打者 .{int(sr['Opp AVG']*1000):03d}")
            elif sr["Opp AVG"] > sl["Opp AVG"] + 0.030:
                if lang == "EN":
                    lines.append(f"- **Platoon split:** vs RHB Opp AVG .{int(sr['Opp AVG']*1000):03d} / "
                               f"vs LHB .{int(sl['Opp AVG']*1000):03d}")
                else:
                    lines.append(f"- **左右別被打率:** 右打者 .{int(sr['Opp AVG']*1000):03d} / "
                               f"左打者 .{int(sl['Opp AVG']*1000):03d}")

    if not lines:
        if lang == "EN":
            return "- No statistically significant vulnerabilities detected in the data."
        else:
            return "- データ上、統計的に有意な弱点は検出されず。"

    return "\n".join(lines)


def generate_defensive_positioning(pdf: pd.DataFrame, player_info: dict, lang: str) -> str:
    """Generate defensive positioning recommendation from spray chart data."""
    bats = player_info.get("bats", "R")
    lines = []

    bip = pdf.dropna(subset=["hc_x", "hc_y"]).copy()
    if len(bip) < 20:
        if lang == "EN":
            return "Insufficient batted ball data for positioning recommendation."
        return "打球データが不足しており、守備位置の推奨はできません。"

    # Spray angle analysis
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

    # Batted ball type
    bb = pdf.dropna(subset=["bb_type"])
    gb_pct = (bb["bb_type"] == "ground_ball").sum() / len(bb) * 100 if len(bb) >= 20 else None
    fb_pct = (bb["bb_type"] == "fly_ball").sum() / len(bb) * 100 if len(bb) >= 20 else None
    ld_pct = (bb["bb_type"] == "line_drive").sum() / len(bb) * 100 if len(bb) >= 20 else None

    # Exit velocity for depth
    avg_ev = pdf["launch_speed"].dropna().mean() if pdf["launch_speed"].notna().any() else None

    # Infield positioning
    if lang == "EN":
        lines.append("**Infield:**")
        if pull_pct >= 50:
            lines.append(f"- **Full pull shift recommended** — {pull_pct:.0f}% of batted balls go to {pull_side}")
            if gb_pct and gb_pct >= 50:
                lines.append(f"- SS shades toward {pull_side} (ground ball hitter, {gb_pct:.0f}% GB)")
            else:
                lines.append(f"- 2B/SS shift pull-heavy")
        elif pull_pct >= 40:
            lines.append(f"- **Shade pull-side** — {pull_pct:.0f}% pull tendency to {pull_side}")
            lines.append(f"- Standard depth, SS shades slightly toward {pull_side}")
        else:
            lines.append(f"- **Standard positioning** — balanced spray (Pull {pull_pct:.0f}% / Center {center_pct:.0f}% / Oppo {oppo_pct:.0f}%)")

        if gb_pct and gb_pct >= 55:
            lines.append(f"- **Play infield in** if situation allows — high ground ball rate ({gb_pct:.0f}%)")
        elif gb_pct and gb_pct < 35:
            lines.append(f"- Normal/deep depth — low ground ball rate ({gb_pct:.0f}%), more fly balls")

        lines.append("")
        lines.append("**Outfield:**")
        if pull_pct >= 45:
            if avg_ev and avg_ev >= 90:
                lines.append(f"- Shift all outfielders pull-heavy and deep (hard hitter, Avg EV {avg_ev:.1f} mph)")
            else:
                lines.append(f"- Shift outfielders pull-heavy toward {pull_side}")
        elif oppo_pct >= 35:
            lines.append(f"- Balanced positioning — this hitter uses the whole field ({oppo_pct:.0f}% oppo)")
            lines.append(f"- RF/LF should not shade too far pull-side")
        else:
            lines.append(f"- Standard outfield alignment")

        if fb_pct and fb_pct >= 45:
            lines.append(f"- **Deep positioning** — fly ball hitter ({fb_pct:.0f}% FB)")
            if avg_ev and avg_ev >= 90:
                lines.append(f"- Warning: hard fly balls (Avg EV {avg_ev:.1f} mph) — extra depth needed")
        elif fb_pct and fb_pct < 30:
            lines.append(f"- Can play slightly shallow — low fly ball rate ({fb_pct:.0f}%)")
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
            lines.append(f"- RF/LFをプル側に寄せすぎない")
        else:
            lines.append(f"- 標準的な外野配置")

        if fb_pct and fb_pct >= 45:
            lines.append(f"- **深めに守る** — フライ打者（{fb_pct:.0f}%）")
            if avg_ev and avg_ev >= 90:
                lines.append(f"- 注意: 強いフライが多い（平均EV {avg_ev:.1f} mph）— さらに深く")
        elif fb_pct and fb_pct < 30:
            lines.append(f"- やや浅めに守れる — フライ率が低い（{fb_pct:.0f}%）")

    return "\n".join(lines)


def _name_display(name: str, lang: str) -> str:
    """Get bilingual display name."""
    p = PLAYER_BY_NAME.get(name) or PITCHER_BY_NAME.get(name)
    if p and lang == "JA":
        ja = p.get("name_ja", "")
        if ja:
            return f"{ja}（{name}）"
    return name


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="WBC 2026 QF: JPN vs VEN",
        page_icon="\U0001F1EF\U0001F1F5",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown("""
    <style>
    /* ============================================
       WBC 2026 QF — Premium Dark Theme
       ============================================ */

    /* --- Global --- */
    .stApp { background-color: #0a0a1a; }

    /* --- Metric Cards --- */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #141428 0%, #1a1a35 100%);
        border: 1px solid #2a2a4a;
        border-radius: 10px;
        padding: 14px 16px;
        transition: border-color 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: #e94560;
    }
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
    [data-testid="stExpander"] summary:hover {
        color: #e94560 !important;
    }

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
    .stDataFrame [data-testid="glideDataEditor"] tr:nth-child(even) td {
        background: rgba(20, 20, 50, 0.5) !important;
    }
    .stDataFrame [data-testid="glideDataEditor"] tr:hover td {
        background: rgba(79, 195, 247, 0.08) !important;
    }

    /* --- Selectbox --- */
    [data-testid="stSelectbox"] > div > div {
        border-color: #2a2a4a !important;
        border-radius: 8px !important;
        background: #141428 !important;
    }

    /* --- Dividers --- */
    hr { border-color: #1a1a35 !important; }

    /* --- Sidebar --- */
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
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.08);
        transition: box-shadow 0.2s ease, transform 0.2s ease;
    }
    .player-card-header:hover {
        box-shadow: 0 6px 25px rgba(233, 69, 96, 0.15);
        transform: translateY(-1px);
    }
    .player-card-header .order-badge {
        background: linear-gradient(135deg, #e94560, #c23152);
        color: white;
        font-size: 1.4rem;
        font-weight: 900;
        width: 46px;
        height: 46px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(233, 69, 96, 0.3);
    }
    .player-card-header .player-name {
        font-size: 1.25rem;
        font-weight: 700;
        color: #e6f1ff;
        margin: 0;
        line-height: 1.3;
    }
    .player-card-header .player-meta {
        font-size: 0.85rem;
        color: #8892b0;
        margin: 3px 0 0 0;
        letter-spacing: 0.02em;
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
    .hero-banner .hero-flags {
        font-size: 3.5rem;
        margin-bottom: 8px;
        letter-spacing: 16px;
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
        letter-spacing: 0.05em;
    }

    /* --- Section header --- */
    .section-header {
        background: linear-gradient(90deg, #141432, transparent);
        border-left: 3px solid #4fc3f7;
        border-radius: 0 8px 8px 0;
        padding: 10px 18px;
        margin: 20px 0 14px 0;
    }
    .section-header h3 {
        color: #e6f1ff;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0;
    }
    .section-header p {
        color: #8892b0;
        font-size: 0.8rem;
        margin: 3px 0 0 0;
    }

    /* --- Section divider --- */
    .section-label {
        background: linear-gradient(90deg, #e94560, transparent);
        height: 2px;
        margin: 28px 0 14px 0;
        border-radius: 2px;
    }

    /* --- Tab content header --- */
    .tab-header {
        background: linear-gradient(135deg, #0f0f23, #141432);
        border: 1px solid #2a2a4a;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 18px;
    }
    .tab-header h2 {
        color: #e6f1ff;
        font-size: 1.4rem;
        font-weight: 800;
        margin: 0 0 4px 0;
    }
    .tab-header .tab-sub {
        color: #8892b0;
        font-size: 0.85rem;
        margin: 0;
    }

    /* --- Info/Success/Warning box overrides --- */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
        border-left-width: 4px !important;
        font-size: 1.0rem !important;
        line-height: 1.7 !important;
    }
    /* Info = scouting blue */
    [data-testid="stAlert"][data-baseweb*="info"],
    div[class*="stAlert"]:has(svg[fill="rgb(49, 130, 206)"]) {
        background: rgba(79, 195, 247, 0.06) !important;
        border-left-color: #4fc3f7 !important;
    }
    /* Success = action green */
    [data-testid="stAlert"][data-baseweb*="success"],
    div[class*="stAlert"]:has(svg[fill="rgb(56, 161, 105)"]) {
        background: rgba(76, 175, 80, 0.06) !important;
        border-left-color: #4caf50 !important;
    }
    /* Warning = caution amber */
    [data-testid="stAlert"][data-baseweb*="warning"],
    div[class*="stAlert"]:has(svg[fill="rgb(214, 158, 46)"]) {
        background: rgba(255, 193, 7, 0.06) !important;
        border-left-color: #ffc107 !important;
    }

    /* --- Caption styling --- */
    [data-testid="stCaption"], .stCaption {
        color: #8892b0 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.01em;
    }

    /* --- Metric delta (consistent with brand) --- */
    [data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
    }

    /* --- Mobile responsive --- */
    @media (max-width: 768px) {
        [data-testid="stMetric"] { padding: 8px 10px; }
        [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.05rem !important; }
        [data-testid="stHorizontalBlock"] { gap: 4px !important; }
        .stDataFrame td, .stDataFrame th { font-size: 1.05rem !important; }
        .hero-banner { padding: 18px 16px; }
        .hero-banner .hero-flags { font-size: 2.5rem; letter-spacing: 10px; }
        .hero-banner .hero-title { font-size: 1.2rem; }
        .player-card-header { padding: 10px 14px; gap: 12px; }
        .player-card-header .order-badge { width: 38px; height: 38px; font-size: 1.2rem; }
        .player-card-header .player-name { font-size: 1.05rem; }
        [data-testid="stTabs"] button { font-size: 0.8rem !important; padding: 6px 12px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    # -- Sidebar --
    lang = st.sidebar.radio("Language / 言語", ["JA", "EN"], horizontal=True)
    t = TEXTS[lang]

    st.sidebar.markdown("""
    <div style="text-align:center; padding: 16px 0 8px 0;">
        <div style="font-size:2.4rem; letter-spacing:8px;">🇯🇵 ⚔️ 🇻🇪</div>
        <div style="font-size:1.1rem; font-weight:700; color:#e6f1ff; margin-top:6px;">
            WBC 2026 Quarterfinal
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.caption(t["subtitle"])
    st.sidebar.markdown("---")

    # Load data
    df_bat_all = load_batter_data()
    df_pit_all = load_pitcher_data()

    # Season filter
    bat_seasons = sorted(df_bat_all["season"].unique().tolist())
    pit_seasons = sorted(df_pit_all["season"].unique().tolist())
    all_seasons = sorted(set(bat_seasons) | set(pit_seasons))
    season = st.sidebar.selectbox(t["season"], all_seasons, index=len(all_seasons) - 1, format_func=str)
    df_bat = filter_season(df_bat_all, season)
    df_pit = filter_season(df_pit_all, season)

    st.sidebar.markdown("---")
    st.sidebar.caption("Data: MLB Statcast via Baseball Savant")

    # -- Hero Banner --
    _data_label = "MLB Statcast 2024-2025 Regular Season" if lang == "EN" else "MLB Statcast 2024-2025レギュラーシーズン"
    _qf_label = "Quarterfinal" if lang == "EN" else "準々決勝"
    st.markdown(f"""<div class="hero-banner">
        <div class="hero-flags">🇯🇵 🇻🇪</div>
        <p class="hero-title">{t['main_title']}</p>
        <p class="hero-sub">{t['subtitle']}</p>
        <span class="hero-badge">📊 {_data_label}</span>
    </div>""", unsafe_allow_html=True)

    tab1, tab_gp, tab2, tab3, tab4 = st.tabs([
        f"🎯 {t['tab1']}",
        f"📋 {t['tab_gameplan']}",
        f"⚔️ {t['tab2']}",
        f"🎱 {t['tab3']}",
        f"🔥 {t['tab4']}",
    ])

    # ===================================================================
    # TAB 1: Matchup Overview
    # ===================================================================
    with tab1:
        st.markdown(f"""<div class="tab-header">
            <h2>🎯 {t['predicted_lineup']}</h2>
            <p class="tab-sub">{t['pool_d_record']} | {_data_label}</p>
        </div>""", unsafe_allow_html=True)

        # Lineup table
        lineup_rows = []
        for p in PREDICTED_LINEUP:
            note = p["note_ja"] if lang == "JA" else p["note_en"]
            player_info = PLAYER_BY_NAME.get(p["name"], {})
            pos_full = POS_LABELS[lang].get(p["pos"], p["pos"])
            pos_display = f"{p['pos']} ({pos_full})"
            lineup_rows.append({
                t["order"]: p["order"],
                t["player"]: _name_display(p["name"], lang),
                t["pos"]: pos_display,
                t["team"]: player_info.get("team", "—"),
                t["bats"]: player_info.get("bats", "—"),
                t["note"]: note,
            })
        lineup_df = pd.DataFrame(lineup_rows)
        st.dataframe(lineup_df, use_container_width=True, hide_index=True)

        # Machado NPB warning
        st.warning(t["machado_warning"])

        # Bench / Pinch-hit candidates
        st.subheader(t["bench_title"])
        bench_rows = []
        for bp in BENCH_PLAYERS:
            bp_info = PLAYER_BY_NAME.get(bp["name"], {})
            role = bp["role_ja"] if lang == "JA" else bp["role_en"]
            bench_rows.append({
                t["player"]: _name_display(bp["name"], lang),
                t["team"]: bp_info.get("team", "—"),
                t["bats"]: bp_info.get("bats", "—"),
                t["note"]: role,
            })
        bench_df = pd.DataFrame(bench_rows)
        st.dataframe(bench_df, use_container_width=True, hide_index=True)

        # Glossary — compact, visually distinct from player cards
        _gl_col1, _gl_col2 = st.columns(2)
        with _gl_col1:
            with st.expander("📖 " + ("Position abbreviations" if lang == "EN" else "守備略称")):
                pos_legend = POS_LABELS[lang]
                pos_order = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"]
                st.markdown(" · ".join(f"**{a}**={pos_legend[a]}" for a in pos_order))
        with _gl_col2:
            with st.expander("📖 " + ("Stats glossary" if lang == "EN" else "成績用語")):
                st.markdown(t["glossary_stats"])

        st.markdown('<div class="section-label"></div>', unsafe_allow_html=True)
        st.subheader("🔍 " + ("選手別スカウティング" if lang == "JA" else "Individual Scouting Reports"))
        st.caption(
            "各選手カードを展開すると完全な分析が表示されます。"
            if lang == "JA" else
            "Expand each player card for the full scouting report."
        )

        # --- Interactive player cards (click to expand) ---
        for p in PREDICTED_LINEUP:
            player_info = PLAYER_BY_NAME.get(p["name"])
            if not player_info:
                continue
            pdf_player = df_bat[df_bat["batter"] == player_info["mlbam_id"]]
            display_name = _name_display(p["name"], lang)
            pos_full = POS_LABELS[lang].get(p["pos"], p["pos"])

            # Rich player card header
            st.markdown(f"""<div class="player-card-header">
                <div class="order-badge">{p['order']}</div>
                <div>
                    <p class="player-name">{display_name}</p>
                    <p class="player-meta">{p['pos']} ({pos_full}) | {player_info.get('team', '')} | {
                        '打席: ' + player_info.get('bats', '') if lang == 'JA'
                        else 'Bats: ' + player_info.get('bats', '')
                    }</p>
                </div>
            </div>""", unsafe_allow_html=True)

            expander_label = ("📊 詳細分析を開く" if lang == "JA" else "📊 Open full analysis")

            with st.expander(expander_label):
                if pdf_player.empty:
                    st.warning(t["no_data"])
                    continue

                stats = batting_stats(pdf_player)

                # Key metrics row
                mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
                mc1.metric("AVG", f"{stats['AVG']:.3f}", help=_help("AVG", lang))
                mc2.metric("OBP", f"{stats['OBP']:.3f}", help=_help("OBP", lang))
                mc3.metric("SLG", f"{stats['SLG']:.3f}", help=_help("SLG", lang))
                mc4.metric("OPS", f"{stats['OPS']:.3f}", help=_help("OPS", lang))
                mc5.metric("K%", f"{stats['K%']:.1f}%", help=_help("K%", lang))
                mc6.metric("BB%", f"{stats['BB%']:.1f}%", help=_help("BB%", lang))

                # Metrics glossary expander
                with st.expander(
                    "What do these stats mean?" if lang == "EN"
                    else "これらの指標の意味は？"
                ):
                    st.markdown(t["glossary_stats"])

                # Scouting summary
                summary = generate_player_summary(stats, pdf_player, player_info, lang)
                st.info(summary)

                # --- Charts: spacer columns constrain width on PC ---
                # Row 1: Radar + Zone (centered ~37.5% each)
                _sp1, chart_left, chart_right, _sp2 = st.columns([1, 3, 3, 1])

                # Radar chart
                with chart_left:
                    _MLB_AVG_EX = {"AVG": .243, "OBP": .312, "SLG": .397, "K%": 22.4, "BB%": 8.3}
                    radar_cats_ex = ["AVG", "OBP", "SLG",
                                     "K%" if lang == "EN" else "\u4e09\u632f\u7387",
                                     "BB%" if lang == "EN" else "\u56db\u7403\u7387"]
                    player_vals_ex = [
                        min(stats["AVG"] / 0.300, 1.0),
                        min(stats["OBP"] / 0.380, 1.0),
                        min(stats["SLG"] / 0.500, 1.0),
                        1.0 - min(stats["K%"] / 35.0, 1.0),
                        min(stats["BB%"] / 15.0, 1.0),
                    ]
                    mlb_vals_ex = [
                        min(_MLB_AVG_EX["AVG"] / 0.300, 1.0),
                        min(_MLB_AVG_EX["OBP"] / 0.380, 1.0),
                        min(_MLB_AVG_EX["SLG"] / 0.500, 1.0),
                        1.0 - min(_MLB_AVG_EX["K%"] / 35.0, 1.0),
                        min(_MLB_AVG_EX["BB%"] / 15.0, 1.0),
                    ]
                    raw_vals_ex = [f"{stats['AVG']:.3f}", f"{stats['OBP']:.3f}", f"{stats['SLG']:.3f}",
                                   f"{stats['K%']:.1f}%", f"{stats['BB%']:.1f}%"]
                    angles_ex = np.linspace(0, 2 * np.pi, len(radar_cats_ex), endpoint=False).tolist()
                    p_plot_ex = player_vals_ex + [player_vals_ex[0]]
                    m_plot_ex = mlb_vals_ex + [mlb_vals_ex[0]]
                    a_plot_ex = angles_ex + [angles_ex[0]]

                    fig_ex, ax_ex = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True),
                                                  facecolor="#0e1117")
                    ax_ex.set_facecolor("#0e1117")
                    ax_ex.plot(a_plot_ex, m_plot_ex, "--", linewidth=1.5, color="#888888",
                               alpha=0.7, label="MLB avg")
                    ax_ex.fill(a_plot_ex, m_plot_ex, alpha=0.08, color="#888888")
                    ax_ex.plot(a_plot_ex, p_plot_ex, "o-", linewidth=2, color="#4fc3f7",
                               label=display_name)
                    ax_ex.fill(a_plot_ex, p_plot_ex, alpha=0.25, color="#4fc3f7")
                    ax_ex.set_thetagrids(np.degrees(angles_ex), radar_cats_ex, color="white", fontsize=11)
                    ax_ex.set_ylim(0, 1.2)  # headroom so annotations don't clip
                    ax_ex.set_yticks([0.25, 0.5, 0.75, 1.0])
                    ax_ex.set_yticklabels(["", "", "", ""], color="white")
                    ax_ex.grid(color="gray", alpha=0.3)
                    ax_ex.spines["polar"].set_color("gray")
                    for angle_ex, val_ex, raw_ex in zip(angles_ex, player_vals_ex, raw_vals_ex):
                        # Calculate offset direction based on angle to push text outward
                        dx = np.cos(angle_ex - np.pi / 2) * 35
                        dy = np.sin(angle_ex - np.pi / 2) * 35
                        ax_ex.annotate(raw_ex, xy=(angle_ex, val_ex),
                                       xytext=(dx, dy),
                                       textcoords="offset points",
                                       fontsize=11, ha="center", va="center",
                                       color="white", fontweight="bold")
                    leg_ex = ax_ex.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
                                           fontsize=10, facecolor="#0e1117", edgecolor="gray",
                                           framealpha=0.9)
                    for txt_ex in leg_ex.get_texts():
                        txt_ex.set_color("white")
                    fig_ex.tight_layout()
                    st.pyplot(fig_ex, use_container_width=True)
                    plt.close(fig_ex)
                    st.caption(t["radar_explain"])

                # 3x3 Zone heatmap (split by pitcher handedness)
                with chart_right:
                    st.markdown(f"**{t['zone_3x3']}**")
                    _t1_z3_lhp = pdf_player[pdf_player["p_throws"] == "L"]
                    _t1_z3_rhp = pdf_player[pdf_player["p_throws"] == "R"]
                    for _t1_z3df, _t1_z3lbl in [
                        (_t1_z3_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                        (_t1_z3_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
                    ]:
                        st.markdown(f"**{_t1_z3lbl}**")
                        _t1_z3df_use = _t1_z3df if len(_t1_z3df) >= 30 else pdf_player
                        fig_z3_ex, ax_z3_ex = _dark_fig(figsize=(4, 3.5))
                        im_z3_ex = draw_zone_3x3(_t1_z3df_use, "ba", f"{_t1_z3lbl} — {t['ba_heatmap']}", ax_z3_ex, lang=lang)
                        cb_z3_ex = fig_z3_ex.colorbar(im_z3_ex, ax=ax_z3_ex, fraction=0.046, pad=0.04)
                        cb_z3_ex.ax.tick_params(colors="white", labelsize=10)
                        fig_z3_ex.tight_layout(pad=2.0)
                        st.pyplot(fig_z3_ex, use_container_width=True)
                        plt.close(fig_z3_ex)
                        if len(_t1_z3df) < 30:
                            st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))
                    st.caption(t["zone_explain"])

                # Row 2: Spray chart (vs LHP / vs RHP) + Platoon splits
                _sp3, chart2_left, chart2_right, _sp4 = st.columns([1, 3, 3, 1])

                with chart2_left:
                    st.markdown(f"**{t['spray_chart']}**")
                    _t1_sp_lhp = pdf_player[pdf_player["p_throws"] == "L"]
                    _t1_sp_rhp = pdf_player[pdf_player["p_throws"] == "R"]
                    for _t1_spdf, _t1_splbl in [
                        (_t1_sp_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                        (_t1_sp_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
                    ]:
                        st.markdown(f"**{_t1_splbl}**")
                        _t1_spdf_use = _t1_spdf if len(_t1_spdf.dropna(subset=["hc_x", "hc_y"])) >= 15 else pdf_player
                        fig_sp_ex, ax_sp_ex = plt.subplots(figsize=(4, 4), facecolor="#0e1117")
                        ax_sp_ex.set_facecolor("#0e1117")
                        draw_spray_chart(_t1_spdf_use, f"{display_name} {_t1_splbl}", ax_sp_ex, stadium="marlins", density=True, lang=lang)
                        fig_sp_ex.tight_layout()
                        st.pyplot(fig_sp_ex, use_container_width=True)
                        plt.close(fig_sp_ex)
                        if len(_t1_spdf.dropna(subset=["hc_x", "hc_y"])) < 15:
                            st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))
                    st.caption(t["spray_explain"])

                # Platoon splits
                with chart2_right:
                    st.markdown(f"**{t['platoon']}**")
                    for ps_throws, ps_label in [("L", t["vs_lhp"]), ("R", t["vs_rhp"])]:
                        split_ps = pdf_player[pdf_player["p_throws"] == ps_throws]
                        if split_ps.empty:
                            st.markdown(f"**{ps_label}**: {t['no_data']}")
                            continue
                        ss_ps = batting_stats(split_ps)
                        st.markdown(f"#### {ps_label}")
                        pm1, pm2, pm3 = st.columns(3)
                        pm1.metric("AVG", f"{ss_ps['AVG']:.3f}", help=_help("AVG", lang))
                        pm2.metric("OPS", f"{ss_ps['OPS']:.3f}", help=_help("OPS", lang))
                        pm3.metric("K%", f"{ss_ps['K%']:.1f}%", help=_help("K%", lang))
                    st.caption(t["platoon_explain"])

                # === Pitching Plan (How to get this batter out) ===
                st.markdown(f"### {t['pitching_plan_title']}")
                st.caption(t["pitching_plan_explain"])
                _t1_plan = generate_pitching_plan(pdf_player, stats, player_info, lang)
                st.success(_t1_plan)

                _t1_vs_l = pdf_player[pdf_player["p_throws"] == "L"]
                _t1_vs_r = pdf_player[pdf_player["p_throws"] == "R"]
                _t1_sl, _t1_cl, _t1_cr, _t1_sr = st.columns([0.5, 2, 2, 0.5])
                with _t1_cl:
                    st.markdown(f"**{t['pitching_plan_vs_lhp']}**")
                    if not _t1_vs_l.empty and len(_t1_vs_l) >= 30:
                        _t1_sl_stats = batting_stats(_t1_vs_l)
                        st.info(generate_pitching_plan(_t1_vs_l, _t1_sl_stats, player_info, lang))
                    else:
                        st.write(t["no_data"])
                with _t1_cr:
                    st.markdown(f"**{t['pitching_plan_vs_rhp']}**")
                    if not _t1_vs_r.empty and len(_t1_vs_r) >= 30:
                        _t1_sr_stats = batting_stats(_t1_vs_r)
                        st.info(generate_pitching_plan(_t1_vs_r, _t1_sr_stats, player_info, lang))
                    else:
                        st.write(t["no_data"])

                # === Defensive Positioning (split by pitcher handedness) ===
                st.markdown(f"### {t['defensive_positioning']}")
                st.caption(t["defensive_explain"])
                _def_vs_lhp = pdf_player[pdf_player["p_throws"] == "L"]
                _def_vs_rhp = pdf_player[pdf_player["p_throws"] == "R"]
                _dsl, _dcl, _dcr, _dsr = st.columns([0.5, 2, 2, 0.5])
                with _dcl:
                    st.markdown(f"**{'vs LHP（左投手時）' if lang == 'JA' else 'vs LHP'}**")
                    if len(_def_vs_lhp.dropna(subset=["hc_x", "hc_y"])) >= 20:
                        st.warning(generate_defensive_positioning(_def_vs_lhp, player_info, lang))
                    else:
                        st.warning(generate_defensive_positioning(pdf_player, player_info, lang))
                        st.caption("⚠️ " + ("左投手データ不足のため全体データで算出" if lang == "JA" else "Insufficient LHP data — using overall"))
                with _dcr:
                    st.markdown(f"**{'vs RHP（右投手時）' if lang == 'JA' else 'vs RHP'}**")
                    if len(_def_vs_rhp.dropna(subset=["hc_x", "hc_y"])) >= 20:
                        st.warning(generate_defensive_positioning(_def_vs_rhp, player_info, lang))
                    else:
                        st.warning(generate_defensive_positioning(pdf_player, player_info, lang))
                        st.caption("⚠️ " + ("右投手データ不足のため全体データで算出" if lang == "JA" else "Insufficient RHP data — using overall"))

                # === 5x5 Zone heatmaps (split by pitcher handedness) ===
                st.markdown(f"**{t['zone_5x5']}**")
                _t1_zone_vs_lhp = pdf_player[pdf_player["p_throws"] == "L"]
                _t1_zone_vs_rhp = pdf_player[pdf_player["p_throws"] == "R"]
                for _t1_hm_m, _t1_hm_t, _t1_hm_c in [
                    ("ba", t["ba_heatmap"], t["danger_zone"]),
                    ("xwoba", t["xwoba_heatmap"], t.get("danger_zone_xwoba", t["danger_zone"])),
                ]:
                    st.caption(_t1_hm_c)
                    _t1_hzl, _t1_hcl, _t1_hcr, _t1_hzr = st.columns([0.5, 2, 2, 0.5])
                    for _t1_hcol, _t1_hdf, _t1_hlbl in [
                        (_t1_hcl, _t1_zone_vs_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                        (_t1_hcr, _t1_zone_vs_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
                    ]:
                        with _t1_hcol:
                            st.markdown(f"**{_t1_hlbl}**")
                            _t1_hdf_use = _t1_hdf if len(_t1_hdf) >= 30 else pdf_player
                            _t1_fh, _t1_ah = _dark_fig(figsize=(5, 4))
                            _t1_ih = draw_zone_heatmap(_t1_hdf_use, _t1_hm_m, f"{_t1_hlbl} — {_t1_hm_t}", _t1_ah, lang=lang)
                            _t1_cb = _t1_fh.colorbar(_t1_ih, ax=_t1_ah, fraction=0.046, pad=0.04)
                            _t1_cb.ax.tick_params(colors="white")
                            _t1_fh.tight_layout()
                            st.pyplot(_t1_fh, use_container_width=True)
                            plt.close(_t1_fh)
                            if len(_t1_hdf) < 30:
                                st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

                # === Batted Ball Profile ===
                st.markdown(f"**{t['batted_ball']}**")
                with st.expander("What do these mean?" if lang == "EN" else "用語の説明を見る"):
                    st.markdown(t["glossary_batted"])
                _t1_bb_lhp = pdf_player[pdf_player["p_throws"] == "L"]
                _t1_bb_rhp = pdf_player[pdf_player["p_throws"] == "R"]
                _t1_bbsl, _t1_bbcl, _t1_bbcr, _t1_bbsr = st.columns([0.5, 2, 2, 0.5])
                for _t1_bbcol, _t1_bbdf, _t1_bblbl in [
                    (_t1_bbcl, _t1_bb_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                    (_t1_bbcr, _t1_bb_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
                ]:
                    with _t1_bbcol:
                        st.markdown(f"**{_t1_bblbl}**")
                        _t1_bbdf_use = _t1_bbdf if len(_t1_bbdf) >= 30 else pdf_player
                        _t1_prof = batted_ball_profile(_t1_bbdf_use, t)
                        if _t1_prof:
                            _t1_bbc = st.columns(2)
                            for _t1_i, (_t1_k, _t1_v) in enumerate(_t1_prof.items()):
                                _t1_bbc[_t1_i % 2].metric(_t1_k, _t1_v)
                        else:
                            st.write(t["no_data"])
                        if len(_t1_bbdf) < 30:
                            st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

                # === Pitch type performance (split by pitcher handedness) ===
                st.markdown(f"**{t['pitch_type_perf']}**")
                with st.expander(t["glossary_pitch"] if lang == "EN" else "空振率・チェイス率とは？"):
                    st.markdown(t["glossary_pitch"])
                _t1_pt_lhp = pdf_player[pdf_player["p_throws"] == "L"]
                _t1_pt_rhp = pdf_player[pdf_player["p_throws"] == "R"]
                for _t1_ptdf, _t1_ptlbl in [
                    (_t1_pt_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                    (_t1_pt_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
                ]:
                    st.markdown(f"**{_t1_ptlbl}**")
                    _t1_ptdf_use = _t1_ptdf if len(_t1_ptdf) >= 30 else pdf_player
                    _t1_ptt = pitch_type_table(_t1_ptdf_use, t)
                    if not _t1_ptt.empty:
                        st.dataframe(_t1_ptt, use_container_width=True, hide_index=True)

                        _t1_cd = _t1_ptt[[t["pitch_type"], t["whiff_pct"]]].copy()
                        _t1_cd["wv"] = _t1_cd[t["whiff_pct"]].str.rstrip("%").astype(float)
                        _t1_cd = _t1_cd.sort_values("wv", ascending=True)
                        _t1_wsl, _t1_wcc, _t1_wsr = st.columns([1, 4, 1])
                        with _t1_wcc:
                            _t1_fw, _t1_aw = _dark_fig(figsize=(8, max(3, len(_t1_cd) * 0.5)))
                            _t1_clrs = plt.cm.RdYlGn_r(_t1_cd["wv"] / max(_t1_cd["wv"].max(), 1))
                            _t1_bars = _t1_aw.barh(_t1_cd[t["pitch_type"]], _t1_cd["wv"], color=_t1_clrs)
                            for _t1_bar, _t1_val in zip(_t1_bars, _t1_cd["wv"]):
                                _t1_aw.text(_t1_bar.get_width() + 0.5, _t1_bar.get_y() + _t1_bar.get_height() / 2,
                                            f"{_t1_val:.1f}%", va="center", ha="left", color="white",
                                            fontsize=12, fontweight="bold")
                            _t1_aw.set_xlabel(t["whiff_pct"], color="white", fontsize=14)
                            _t1_aw.tick_params(colors="white", labelsize=12)
                            _t1_aw.set_title(f"{_t1_ptlbl} — {t['whiff_pct']}", color="white", fontsize=16, fontweight="bold")
                            _t1_xm = _t1_cd["wv"].max()
                            _t1_aw.set_xlim(0, _t1_xm * 1.25 if _t1_xm > 0 else 10)
                            for sp in _t1_aw.spines.values():
                                sp.set_color("white")
                            _t1_fw.tight_layout()
                            st.pyplot(_t1_fw, use_container_width=True)
                            plt.close(_t1_fw)
                        if len(_t1_ptdf) < 30:
                            st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

                # === Platoon zone heatmaps ===
                st.markdown(f"**{t['platoon']} — {t['zone_heatmap_pitch']}**")
                _t1_psl, _t1_pcl, _t1_pcr, _t1_psr = st.columns([0.5, 2, 2, 0.5])
                for _t1_pcol, _t1_pthr, _t1_plbl in [(_t1_pcl, "L", t["vs_lhp"]), (_t1_pcr, "R", t["vs_rhp"])]:
                    with _t1_pcol:
                        st.markdown(f"**{_t1_plbl}**")
                        _t1_sdf = pdf_player[pdf_player["p_throws"] == _t1_pthr]
                        if _t1_sdf.empty:
                            st.write(t["no_data"])
                            continue
                        _t1_ss = batting_stats(_t1_sdf)
                        _t1_m1, _t1_m2, _t1_m3, _t1_m4 = st.columns(4)
                        _t1_m1.metric("AVG", f"{_t1_ss['AVG']:.3f}", help=_help("AVG", lang))
                        _t1_m2.metric("OBP", f"{_t1_ss['OBP']:.3f}", help=_help("OBP", lang))
                        _t1_m3.metric("SLG", f"{_t1_ss['SLG']:.3f}", help=_help("SLG", lang))
                        _t1_m4.metric("OPS", f"{_t1_ss['OPS']:.3f}", help=_help("OPS", lang))
                        _t1_fz, _t1_az = _dark_fig(figsize=(5, 4))
                        draw_zone_heatmap(_t1_sdf, "ba", f"{_t1_plbl} — {t['ba_heatmap']}", _t1_az, lang=lang)
                        _t1_fz.tight_layout()
                        st.pyplot(_t1_fz, use_container_width=True)
                        plt.close(_t1_fz)

                # === Count-by-count performance (split by pitcher handedness) ===
                st.markdown(f"**{t['count_perf']}**")
                st.caption(t["count_explain"])
                _t1_cnt_lhp = pdf_player[pdf_player["p_throws"] == "L"]
                _t1_cnt_rhp = pdf_player[pdf_player["p_throws"] == "R"]
                _t1_all_counts = [
                    (0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
                    (2, 1), (1, 2), (3, 0), (2, 2), (3, 1), (3, 2),
                ]
                for _t1_cntdf, _t1_cntlbl in [
                    (_t1_cnt_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                    (_t1_cnt_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
                ]:
                    st.markdown(f"**{_t1_cntlbl}**")
                    _t1_cntdf_use = _t1_cntdf if len(_t1_cntdf) >= 50 else pdf_player
                    _t1_cdf = _t1_cntdf_use.dropna(subset=["balls", "strikes"]).copy()
                    _t1_cdf["balls"] = _t1_cdf["balls"].astype(int)
                    _t1_cdf["strikes"] = _t1_cdf["strikes"].astype(int)
                    _t1_crows = []
                    for _t1_b, _t1_s in _t1_all_counts:
                        _t1_cat = count_category(_t1_b, _t1_s)
                        _t1_tag = {"ahead": t["ahead"], "behind": t["behind"], "even": t["even"]}[_t1_cat]
                        _t1_cdf2 = _t1_cdf[(_t1_cdf["balls"] == _t1_b) & (_t1_cdf["strikes"] == _t1_s)]
                        if _t1_cdf2.empty:
                            continue
                        _t1_cs = batting_stats(_t1_cdf2)
                        if _t1_cs["PA"] < 5:
                            continue
                        _t1_crows.append({
                            ("Count" if lang == "EN" else "カウント"): f"{_t1_b}-{_t1_s}",
                            ("Type" if lang == "EN" else "分類"): _t1_tag,
                            "PA": _t1_cs["PA"], "AVG": _t1_cs["AVG"], "OBP": _t1_cs["OBP"],
                            "SLG": _t1_cs["SLG"], "OPS": _t1_cs["OPS"],
                            "K%": _t1_cs["K%"], "BB%": _t1_cs["BB%"],
                        })
                    if _t1_crows:
                        _t1_ct = pd.DataFrame(_t1_crows)
                        _t1_type_col = "Type" if lang == "EN" else "分類"
                        st.dataframe(
                            _t1_ct.style.format({
                                "AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}",
                                "OPS": "{:.3f}", "K%": "{:.1f}", "BB%": "{:.1f}",
                            }).background_gradient(subset=["AVG"], cmap="YlOrRd", vmin=0.150, vmax=0.350
                            ).background_gradient(subset=["OPS"], cmap="YlOrRd", vmin=0.400, vmax=1.000
                            ).background_gradient(subset=["K%"], cmap="YlOrRd_r", vmin=10, vmax=40
                            ).map(lambda v: _style_count_type(v, t), subset=[_t1_type_col]),
                            use_container_width=True, hide_index=True,
                        )
                    if len(_t1_cntdf) < 50:
                        st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

        st.divider()

        # Predicted SP card
        st.markdown('<div class="section-label"></div>', unsafe_allow_html=True)
        _t1_sp_info = PITCHER_BY_NAME.get(PREDICTED_SP, {})
        _t1_sp_display = _name_display(PREDICTED_SP, lang)
        _t1_sp_throws = _t1_sp_info.get("throws", "—")
        _t1_sp_team = _t1_sp_info.get("team", "—")
        st.markdown(f"""<div class="player-card-header">
            <div class="order-badge">SP</div>
            <div>
                <p class="player-name">{_t1_sp_display}</p>
                <p class="player-meta">{t['sp_label']} | {_t1_sp_team} | {'投: ' + _t1_sp_throws if lang == 'JA' else 'Throws: ' + _t1_sp_throws}</p>
            </div>
        </div>""", unsafe_allow_html=True)
        sp_info = _t1_sp_info
        sp_cols = st.columns(3)
        sp_cols[0].metric(t["team"], sp_info.get("team", "—"))
        sp_cols[1].metric(t["throws"], sp_info.get("throws", "—"))
        sp_cols[2].metric(t["role"], t["sp_label"])

        # SP MLB stats from Statcast
        sp_data = df_pit[df_pit["pitcher"] == sp_info.get("mlbam_id", -1)]
        if not sp_data.empty:
            sp_stats = pitching_stats(sp_data)
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric(t["opp_avg"], f"{sp_stats['Opp AVG']:.3f}", help=_help("Opp AVG", lang))
            sc2.metric(t["k_pct"], f"{sp_stats['K%']:.1f}%", help=_help("K%", lang))
            sc3.metric(t["bb_pct"], f"{sp_stats['BB%']:.1f}%", help=_help("BB%", lang))
            sc4.metric(t["whiff_pct"], f"{sp_stats['Whiff%']:.1f}%", help=_help("Whiff%", lang))
            if sp_stats["Avg Velo"]:
                velo_label = "平均球速" if lang == "JA" else "Avg Velo"
                st.caption(f"{velo_label}: {sp_stats['Avg Velo']:.1f} mph ({sp_stats['Avg Velo'] * 1.609:.0f} km/h)")

            # --- SP Detailed Analysis in Tab 1 (folded into expanders) ---
            # Scouting summary (always visible)
            _t1_sp_summary = generate_pitcher_summary(sp_stats, sp_data, sp_info, lang)
            st.info(_t1_sp_summary)

            # --- Expander: Hitting Plan ---
            with st.expander("📋 " + t['hitting_plan_title'], expanded=False):
                st.caption(t["hitting_plan_explain"])
                _t1_hit_plan = generate_hitting_plan(sp_data, sp_stats, sp_info, lang)
                st.success(_t1_hit_plan)

                # Left/Right hitting plans
                _t1_sp_vs_lhb = sp_data[sp_data["stand"] == "L"]
                _t1_sp_vs_rhb = sp_data[sp_data["stand"] == "R"]
                _t1_sl_hp, _t1_col_hp_l, _t1_col_hp_r, _t1_sr_hp = st.columns([0.5, 2, 2, 0.5])
                with _t1_col_hp_l:
                    st.markdown(f"**{t['hitting_plan_as_lhb']}**")
                    if not _t1_sp_vs_lhb.empty and len(_t1_sp_vs_lhb) >= 30:
                        _t1_stats_lhb = pitching_stats(_t1_sp_vs_lhb)
                        _t1_plan_lhb = generate_hitting_plan(_t1_sp_vs_lhb, _t1_stats_lhb, sp_info, lang)
                        st.info(_t1_plan_lhb)
                    else:
                        st.write(t["no_data"])
                with _t1_col_hp_r:
                    st.markdown(f"**{t['hitting_plan_as_rhb']}**")
                    if not _t1_sp_vs_rhb.empty and len(_t1_sp_vs_rhb) >= 30:
                        _t1_stats_rhb = pitching_stats(_t1_sp_vs_rhb)
                        _t1_plan_rhb = generate_hitting_plan(_t1_sp_vs_rhb, _t1_stats_rhb, sp_info, lang)
                        st.info(_t1_plan_rhb)
                    else:
                        st.write(t["no_data"])

            # --- Expander: Arsenal & Movement ---
            with st.expander("⚾ " + (t["arsenal"] + " & " + t["movement_chart"]), expanded=False):
                st.markdown(f"**{t['arsenal']}**")
                _t1_at = arsenal_table(sp_data, t)
                if not _t1_at.empty:
                    st.dataframe(_t1_at, use_container_width=True, hide_index=True)
                with st.expander("Stats glossary" if lang == "EN" else "指標の説明"):
                    st.markdown(t["arsenal_explain"])

                st.divider()

                st.markdown(f"**{t['movement_chart']}**")
                st.caption(t["movement_note"])
                _t1_fig_m, _t1_ax_m = plt.subplots(figsize=(8, 5), facecolor="#0e1117")
                _t1_ax_m.set_facecolor("#1a1a2e")
                for _sp_spine in _t1_ax_m.spines.values():
                    _sp_spine.set_color("white")
                draw_movement_chart(sp_data, _name_display(PREDICTED_SP, lang), _t1_ax_m, density=True)
                _t1_fig_m.tight_layout(rect=[0, 0, 0.82, 1])
                _t1_sl_mv, _t1_cc_mv, _t1_sr_mv = st.columns([1, 4, 1])
                with _t1_cc_mv:
                    st.pyplot(_t1_fig_m, use_container_width=True)
                plt.close(_t1_fig_m)

            # --- Expander: Zone & Platoon ---
            with st.expander("🎯 " + (t["zone_heatmap_pitch"] + " & " + t["platoon"]), expanded=False):
                st.markdown(f"**{t['zone_heatmap_pitch']}**")
                for _t1_hm_metric, _t1_hm_title in [("usage", t["usage_heatmap"]), ("ba", t["ba_heatmap"])]:
                    _t1_fig_hm, _t1_ax_hm = _dark_fig(figsize=(6, 5))
                    _t1_im_hm = draw_zone_heatmap(sp_data, _t1_hm_metric, _t1_hm_title, _t1_ax_hm, lang=lang)
                    _t1_cb_hm = _t1_fig_hm.colorbar(_t1_im_hm, ax=_t1_ax_hm, fraction=0.046, pad=0.04)
                    _t1_cb_hm.ax.tick_params(colors="white")
                    _t1_fig_hm.tight_layout(pad=2.0)
                    _t1_sl_hm, _t1_cc_hm, _t1_sr_hm = st.columns([1, 4, 1])
                    with _t1_cc_hm:
                        st.pyplot(_t1_fig_hm, use_container_width=True)
                        if _t1_hm_metric == "usage":
                            st.caption(t["zone_usage_explain"])
                        else:
                            st.caption(t["zone_opp_ba_explain"])
                    plt.close(_t1_fig_hm)

                st.divider()

                st.markdown(f"**{t['platoon']}**")
                st.caption(t["platoon_pitcher_explain"])
                _t1_sl_pl, _t1_cl_pl, _t1_cr_pl, _t1_sr_pl = st.columns([0.5, 2, 2, 0.5])
                for _t1_pl_col, _t1_stand, _t1_pl_label in [(_t1_cl_pl, "L", t["vs_lhb"]), (_t1_cr_pl, "R", t["vs_rhb"])]:
                    with _t1_pl_col:
                        st.markdown(f"**{_t1_pl_label}**")
                        _t1_split_df = sp_data[sp_data["stand"] == _t1_stand]
                        if _t1_split_df.empty:
                            st.write(t["no_data"])
                            continue
                        _t1_ss = pitching_stats(_t1_split_df)
                        _t1_m1, _t1_m2, _t1_m3, _t1_m4 = st.columns(4)
                        _t1_m1.metric(t["opp_avg"], f"{_t1_ss['Opp AVG']:.3f}", help=_help("Opp AVG", lang))
                        _t1_m2.metric(t["opp_slg"], f"{_t1_ss['Opp SLG']:.3f}", help=_help("Opp SLG", lang))
                        _t1_m3.metric(t["k_pct"], f"{_t1_ss['K%']:.1f}%", help=_help("K%", lang))
                        _t1_m4.metric(t["bb_pct"], f"{_t1_ss['BB%']:.1f}%", help=_help("BB%", lang))
                        _t1_fig_z, _t1_ax_z = _dark_fig(figsize=(5, 4))
                        draw_zone_heatmap(_t1_split_df, "ba", f"{_t1_pl_label} — {t['ba_heatmap']}", _t1_ax_z, lang=lang)
                        _t1_fig_z.tight_layout(pad=2.0)
                        st.pyplot(_t1_fig_z, use_container_width=True)
                        plt.close(_t1_fig_z)

            # --- Expander: Count Analysis ---
            with st.expander("📈 " + t["pitch_selection_by_count"], expanded=False):
                st.caption(t["pitch_selection_explain"])
                _t1_sp_lhb = sp_data[sp_data["stand"] == "L"]
                _t1_sp_rhb = sp_data[sp_data["stand"] == "R"]
                _t1_all_counts = [
                    (0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
                    (2, 1), (1, 2), (3, 0), (2, 2), (3, 1), (3, 2),
                ]
                for _t1_spdf, _t1_splbl in [
                    (_t1_sp_lhb, t["vs_lhb"]),
                    (_t1_sp_rhb, t["vs_rhb"]),
                ]:
                    st.markdown(f"**{_t1_splbl}**")
                    _t1_spdf_use = _t1_spdf if len(_t1_spdf) >= 50 else sp_data

                    _t1_ps_table = pitch_selection_by_count(_t1_spdf_use, t, lang)
                    if not _t1_ps_table.empty:
                        st.dataframe(_t1_ps_table, use_container_width=True, hide_index=True)
                    draw_pitch_selection_pies(_t1_spdf_use, t, lang)

                    st.markdown(f"**{t['count_perf']}**")
                    st.caption(t["count_explain"])
                    _t1_pit_count_df = _t1_spdf_use.dropna(subset=["balls", "strikes"]).copy()
                    _t1_pit_count_df["balls"] = _t1_pit_count_df["balls"].astype(int)
                    _t1_pit_count_df["strikes"] = _t1_pit_count_df["strikes"].astype(int)
                    _t1_pit_count_rows = []
                    for _t1_b, _t1_s in _t1_all_counts:
                        _t1_cat = count_category(_t1_b, _t1_s)
                        _t1_tag = {"ahead": t["behind"], "behind": t["ahead"], "even": t["even"]}[_t1_cat]
                        _t1_cdf = _t1_pit_count_df[(_t1_pit_count_df["balls"] == _t1_b) & (_t1_pit_count_df["strikes"] == _t1_s)]
                        if _t1_cdf.empty:
                            continue
                        _t1_ps2 = pitching_stats(_t1_cdf)
                        if _t1_ps2["PA"] < 3:
                            continue
                        _t1_pit_count_rows.append({
                            ("Count" if lang == "EN" else "カウント"): f"{_t1_b}-{_t1_s}",
                            ("Type" if lang == "EN" else "分類"): _t1_tag,
                            "PA": _t1_ps2["PA"],
                            t["opp_avg"]: _t1_ps2["Opp AVG"],
                            t["k_pct"]: _t1_ps2["K%"],
                            t["bb_pct"]: _t1_ps2["BB%"],
                            t["whiff_pct"]: _t1_ps2["Whiff%"],
                        })
                    if _t1_pit_count_rows:
                        _t1_pit_count_table = pd.DataFrame(_t1_pit_count_rows)
                        _t1_pit_type_col = "Type" if lang == "EN" else "分類"
                        st.dataframe(
                            _t1_pit_count_table.style.format({
                                t["opp_avg"]: "{:.3f}",
                                t["k_pct"]: "{:.1f}",
                                t["bb_pct"]: "{:.1f}",
                                t["whiff_pct"]: "{:.1f}",
                            }).background_gradient(subset=[t["opp_avg"]], cmap="YlOrRd", vmin=0.150, vmax=0.350
                            ).background_gradient(subset=[t["k_pct"]], cmap="YlOrRd", vmin=10, vmax=40
                            ).background_gradient(subset=[t["whiff_pct"]], cmap="YlOrRd", vmin=15, vmax=45
                            ).map(lambda v: _style_count_type(v, t), subset=[_t1_pit_type_col]),
                            use_container_width=True,
                            hide_index=True,
                        )
                    if len(_t1_spdf) < 50:
                        st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))
                    st.divider()

    # ===================================================================
    # TAB: Game Plan (inning-by-inning strategy)
    # ===================================================================
    with tab_gp:
        st.markdown(f"""<div class="tab-header">
            <h2>📋 {t['tab_gameplan']}</h2>
            <p class="tab-sub">{"Inning-by-inning strategy based on MLB Statcast data" if lang == "EN" else "MLB Statcastデータに基づくイニング別攻略"}</p>
        </div>""", unsafe_allow_html=True)

        # ----- Build all data needed for game plan -----
        # SP stats
        _gp_sp_info = PITCHER_BY_NAME.get(PREDICTED_SP, {})
        _gp_sp_data = df_pit[df_pit["pitcher"] == _gp_sp_info.get("mlbam_id", 0)] if _gp_sp_info else pd.DataFrame()
        _gp_sp_stats = pitching_stats(_gp_sp_data) if not _gp_sp_data.empty else {}

        # SP pitch type usage breakdown
        _gp_sp_pitch_usage = {}
        if not _gp_sp_data.empty:
            _pt_counts = _gp_sp_data["pitch_type"].dropna().value_counts()
            _pt_total = _pt_counts.sum()
            if _pt_total > 0:
                for pt, cnt in _pt_counts.items():
                    label = PITCH_LABELS.get(pt, pt)
                    _gp_sp_pitch_usage[label] = round(cnt / _pt_total * 100, 1)

        _sp_k = f"{_gp_sp_stats.get('K%', 0):.1f}" if _gp_sp_stats else "?"
        _sp_bb = f"{_gp_sp_stats.get('BB%', 0):.1f}" if _gp_sp_stats else "?"
        _sp_whiff = f"{_gp_sp_stats.get('Whiff%', 0):.1f}" if _gp_sp_stats else "?"
        _sp_velo = f"{_gp_sp_stats.get('Avg Velo', 0):.1f}" if _gp_sp_stats.get("Avg Velo") else "?"

        # Build bullpen stats
        _gp_bp_stats = {}
        for rp_name in KEY_RELIEVERS:
            rp_info = PITCHER_BY_NAME.get(rp_name, {})
            if not rp_info:
                continue
            rp_data = df_pit[df_pit["pitcher"] == rp_info["mlbam_id"]]
            if rp_data.empty:
                continue
            rp_s = pitching_stats(rp_data)
            # Chase rate
            _rp_outside = rp_data[rp_data["zone"].isin([11, 12, 13, 14]) if "zone" in rp_data.columns else pd.Series(dtype=bool)]
            _rp_chase_pct = 0.0
            if "zone" in rp_data.columns:
                _rp_outside = rp_data[rp_data["zone"] >= 11]
                _swing_events = {"hit_into_play", "foul", "swinging_strike",
                                 "swinging_strike_blocked", "foul_tip",
                                 "hit_into_play_score", "hit_into_play_no_out"}
                _rp_outside_swings = _rp_outside[_rp_outside["description"].isin(_swing_events)]
                _rp_chase_pct = len(_rp_outside_swings) / len(_rp_outside) * 100 if len(_rp_outside) > 0 else 0.0
            _gp_bp_stats[rp_name] = {**rp_s, "Chase%": round(_rp_chase_pct, 1)}

        # Batter weakness analysis
        high_k_batters = []
        low_bb_batters = []
        platoon_weak_batters = []
        _gp_batter_stats = {}

        for p in PREDICTED_LINEUP:
            player_info = PLAYER_BY_NAME.get(p["name"])
            if not player_info:
                continue
            pdf_gp = df_bat[df_bat["batter"] == player_info["mlbam_id"]]
            if pdf_gp.empty:
                continue
            s_gp = batting_stats(pdf_gp)
            _gp_batter_stats[p["name"]] = s_gp
            display = _name_display(p["name"], lang)

            if s_gp["K%"] >= 22.0:
                high_k_batters.append(f"{display} ({s_gp['K%']:.1f}%)")
            if s_gp["BB%"] < 7.0:
                low_bb_batters.append(f"{display} ({s_gp['BB%']:.1f}%)")

            vs_l_gp = pdf_gp[pdf_gp["p_throws"] == "L"]
            vs_r_gp = pdf_gp[pdf_gp["p_throws"] == "R"]
            if not vs_l_gp.empty and not vs_r_gp.empty:
                sl_gp = batting_stats(vs_l_gp)
                sr_gp = batting_stats(vs_r_gp)
                if sl_gp["PA"] >= 30 and sr_gp["PA"] >= 30:
                    if sl_gp["OPS"] < sr_gp["OPS"] - 0.080:
                        if lang == "EN":
                            platoon_weak_batters.append(f"{display} (OPS .{int(sl_gp['OPS']*1000):03d} vs LHP)")
                        else:
                            platoon_weak_batters.append(f"{display}\uff08\u5de6\u6295\u624bOPS .{int(sl_gp['OPS']*1000):03d}\uff09")
                    elif sr_gp["OPS"] < sl_gp["OPS"] - 0.080:
                        if lang == "EN":
                            platoon_weak_batters.append(f"{display} (OPS .{int(sr_gp['OPS']*1000):03d} vs RHP)")
                        else:
                            platoon_weak_batters.append(f"{display}\uff08\u53f3\u6295\u624bOPS .{int(sr_gp['OPS']*1000):03d}\uff09")

        # ===== Section A: Team Weakness Summary =====
        st.subheader(t["gp_team_weakness"])

        if high_k_batters:
            if lang == "EN":
                st.markdown("**High K% batters — target with strikeout pitching:**\n"
                            + "MLB avg K% = 22.4%. These batters are above average — use put-away pitches aggressively with 2 strikes.\n"
                            + "\n".join(f"- {b}" for b in high_k_batters))
            else:
                st.markdown("**三振率がMLB平均（22.4%）以上の打者:**\n"
                            + "\n".join(f"- {b}" for b in high_k_batters))

        if low_bb_batters:
            if lang == "EN":
                st.markdown("**Aggressive batters — expand the zone:**\n"
                            + "MLB avg BB% = 8.3%. These batters swing at pitches outside the zone more often — use offspeed away to induce weak contact or chases.\n"
                            + "\n".join(f"- {b}" for b in low_bb_batters))
            else:
                st.markdown("**四球率がMLB平均（8.3%）未満の打者（ゾーン外を振る傾向）:**\n"
                            + "\n".join(f"- {b}" for b in low_bb_batters))

        if platoon_weak_batters:
            if lang == "EN":
                st.markdown("**Platoon vulnerabilities — exploit with matchups:**\n"
                            + "OPS drops 80+ points against one side — use bullpen matchups to target this weakness in key at-bats.\n"
                            + "\n".join(f"- {b}" for b in platoon_weak_batters))
            else:
                st.markdown("**左右別OPSに80ポイント以上の差がある打者:**\n"
                            + "\n".join(f"- {b}" for b in platoon_weak_batters))

        st.divider()

        # ===== Section B: 1-3回 (1st Time Through Order) =====
        st.subheader(t["gp_inning_1_3"])

        # Pitch usage summary string
        _pitch_usage_str_en = ", ".join(f"{lbl} {pct}%" for lbl, pct in sorted(_gp_sp_pitch_usage.items(), key=lambda x: -x[1])[:4])
        _pitch_usage_str_ja = ", ".join(f"{lbl} {pct}%" for lbl, pct in sorted(_gp_sp_pitch_usage.items(), key=lambda x: -x[1])[:4])

        st.markdown(f"**{t['gp_batting']}**")
        if lang == "EN":
            st.success(
                f"**vs Ranger Suárez (LHP) — 60-65 pitch target, max 80 (QF rule):**\n"
                f"- K% {_sp_k}%, BB% {_sp_bb}%, Whiff% {_sp_whiff}%, Avg Velo {_sp_velo} mph\n"
                "- Pitch count determines 2-4 innings (QF pitch limit rule)"
            )
        else:
            st.success(
                f"**vs レンジャー・スアレス（左腕） — 目安60-65球、最大80球（準々決勝規定）:**\n"
                f"- 奪三振率 {_sp_k}%（MLB平均22.4%）, 与四球率 {_sp_bb}%, 空振率 {_sp_whiff}%（MLB平均25%）, 平均球速 {_sp_velo} mph\n"
                "- 球数次第で2-4回の幅（準々決勝球数制限ルール）"
            )
        # Data-driven pitch analysis from Statcast
        _gp_sp_analysis = generate_sp_pitch_analysis(_gp_sp_data, lang)
        if _gp_sp_analysis:
            st.info(_gp_sp_analysis)

        st.markdown(f"**{t['gp_pitching']}**")

        # Build 1st-time-through pitching approach by batting order groups
        _top_order = [p for p in PREDICTED_LINEUP if p["order"] <= 3]
        _mid_order = [p for p in PREDICTED_LINEUP if 4 <= p["order"] <= 6]
        _bot_order = [p for p in PREDICTED_LINEUP if p["order"] >= 7]

        def _batter_line(p_list, lang_code):
            lines = []
            for p in p_list:
                dn = _name_display(p["name"], lang_code)
                s = _gp_batter_stats.get(p["name"], {})
                if s:
                    lines.append(f"- **{dn} (#{p['order']}):** AVG .{int(s['AVG']*1000):03d}, K% {s['K%']:.1f}%, BB% {s['BB%']:.1f}%")
                else:
                    lines.append(f"- **{dn} (#{p['order']})**")
            return "\n".join(lines)

        if lang == "EN":
            st.info(
                "**1st time through — batter stats:**\n\n"
                "**#1-3:**\n"
                + _batter_line(_top_order, "EN") + "\n\n"
                "**#4-6:**\n"
                + _batter_line(_mid_order, "EN") + "\n\n"
                "**#7-9:**\n"
                + _batter_line(_bot_order, "EN")
            )
        else:
            st.info(
                "**1巡目の打者別データ:**\n\n"
                "**#1-3:**\n"
                + _batter_line(_top_order, "JA") + "\n\n"
                "**#4-6:**\n"
                + _batter_line(_mid_order, "JA") + "\n\n"
                "**#7-9:**\n"
                + _batter_line(_bot_order, "JA")
            )

        st.divider()

        # ===== Section C: 4-5回 (Bullpen Front — Bridge Relievers) =====
        st.subheader(t["gp_inning_4_5"])

        # Build bridge reliever stats (Bazardo, Montero — inning-eater types)
        _bridge_names = ["Eduard Bazardo", "Keider Montero"]
        _bridge_stats_en = []
        _bridge_stats_ja = []
        for rp_name in _bridge_names:
            rp_s = _gp_bp_stats.get(rp_name)
            if not rp_s:
                continue
            velo_str = f"{rp_s['Avg Velo']:.1f}" if rp_s.get("Avg Velo") else "?"
            _bridge_stats_en.append(
                f"- **{rp_name}:** K% {rp_s['K%']:.1f}%, BB% {rp_s['BB%']:.1f}%, "
                f"Whiff% {rp_s['Whiff%']:.1f}%, Velo {velo_str} mph"
            )
            _bridge_stats_ja.append(
                f"- **{_name_display(rp_name, 'JA')}:** 奪三振率 {rp_s['K%']:.1f}%, "
                f"与四球率 {rp_s['BB%']:.1f}%, 空振率 {rp_s['Whiff%']:.1f}%, 球速 {velo_str} mph"
            )

        st.markdown(f"**{t['gp_batting']}**")
        if lang == "EN":
            st.success(
                "**vs Bridge Relievers (Bazardo, Montero, etc.):**\n"
                + "\n".join(_bridge_stats_en) + "\n"
                f"- Suárez pitch mix: {_pitch_usage_str_en}\n"
                "- MLB avg: 2nd time through order, pitcher opp OPS rises 15-20%"
            )
        else:
            st.success(
                "**スアレス続投の場合（2巡目）:**\n"
                "- MLB統計: 2巡目は投手の被OPSが15-20%上昇する傾向\n"
                f"- スアレスの球種配分: {_pitch_usage_str_ja}\n\n"
                "**中継ぎ移行の場合:**\n"
                + "\n".join(_bridge_stats_ja) + "\n"
                "- MLB統計: 2巡目は投手の被OPSが15-20%上昇する傾向"
            )

        st.markdown(f"**{t['gp_pitching']}**")

        # Identify high-K and low-K batters for mid-game approach
        _high_k_names = [p["name"] for p in PREDICTED_LINEUP
                         if _gp_batter_stats.get(p["name"], {}).get("K%", 0) >= 22.0]
        _patient_names = [p["name"] for p in PREDICTED_LINEUP
                          if _gp_batter_stats.get(p["name"], {}).get("BB%", 0) >= 9.0]

        _high_k_display = ", ".join(_name_display(n, lang) for n in _high_k_names[:3]) if _high_k_names else "N/A"
        _patient_display = ", ".join(_name_display(n, lang) for n in _patient_names[:3]) if _patient_names else "N/A"

        if lang == "EN":
            st.info(
                "**2nd time through — data trends:**\n"
                "- MLB avg: 2nd time through, pitcher opp OPS rises 15-20%\n\n"
                f"**K% ≥ 22.4% (MLB avg):** {_high_k_display}\n\n"
                f"**BB% ≥ 9.0%:** {_patient_display}\n"
                "- MLB data: opp BA drops significantly after first-pitch strike"
            )
        else:
            st.info(
                "**2巡目のデータ傾向:**\n"
                "- MLB全体の統計: 2巡目は投手の被OPSが15-20%上昇する傾向\n\n"
                f"**三振率 ≥ 22.4%（MLB平均以上）:** {_high_k_display}\n\n"
                f"**四球率 ≥ 9.0%:** {_patient_display}\n"
                "- MLB統計: 初球ストライク後の被打率は大幅低下"
            )

        st.divider()

        # ===== Section D: 6回+ (High-Leverage Bullpen) =====
        st.subheader(t["gp_inning_6_plus"])

        st.markdown(f"**{t['gp_batting']}**")

        # Build high-leverage reliever approach (Palencia closer, Buttó, Machado warning)
        _hlev_names = ["Daniel Palencia", "José Buttó"]
        _bp_approach_en = []
        _bp_approach_ja = []
        for rp_name in _hlev_names:
            rp_s = _gp_bp_stats.get(rp_name)
            if not rp_s:
                continue
            rp_disp_ja = _name_display(rp_name, "JA")
            velo_str = f"{rp_s['Avg Velo']:.1f}" if rp_s.get("Avg Velo") else "?"
            chase_str = f"{rp_s['Chase%']:.1f}" if rp_s.get("Chase%") else "?"

            if rp_s["K%"] >= 25.0:
                approach_en = f"K% above MLB avg (22.4%)"
                approach_ja = f"奪三振率がMLB平均（22.4%）以上"
            elif rp_s["BB%"] >= 10.0:
                approach_en = f"BB% above MLB avg (8.3%)"
                approach_ja = f"与四球率がMLB平均（8.3%）以上"
            else:
                approach_en = "K% and BB% both below MLB avg"
                approach_ja = "奪三振率・与四球率ともにMLB平均未満"

            _bp_approach_en.append(
                f"- **{rp_name}:** K% {rp_s['K%']:.1f}%, Whiff% {rp_s['Whiff%']:.1f}%, "
                f"Chase% {chase_str}%, Velo {velo_str} mph — {approach_en}"
            )
            _bp_approach_ja.append(
                f"- **{rp_disp_ja}:** 奪三振率 {rp_s['K%']:.1f}%, 空振率 {rp_s['Whiff%']:.1f}%, "
                f"チェイス率 {chase_str}%, 球速 {velo_str} mph — {approach_ja}"
            )

        if lang == "EN":
            st.success(
                "**vs High-Leverage Arms (Palencia, Buttó):**\n"
                + "\n".join(_bp_approach_en) + "\n"
                "- **Palencia:** ERA 2.91, 22 SV, avg 99.6 mph\n"
                "- ⚠️ **Machado (Orix, NPB):** NPB 2024 — 28 SV, ERA 1.92. No Statcast data"
            )
        else:
            st.success(
                "**vs 勝ちパターン投手:**\n"
                + "\n".join(_bp_approach_ja) + "\n"
                "- **パレンシア:** 防御率2.91、22セーブ、平均球速99.6mph\n"
                "- ⚠️ **マチャド（オリックス）:** NPB 2024 — 28セーブ、防御率1.92。Statcastデータなし"
            )

        st.markdown(f"**{t['gp_pitching']}**")

        # Build late-game pitching strategy
        _platoon_targets = []
        for p in PREDICTED_LINEUP:
            s = _gp_batter_stats.get(p["name"], {})
            if not s:
                continue
            dn = _name_display(p["name"], lang)
            pi = PLAYER_BY_NAME.get(p["name"])
            if not pi:
                continue
            pdf_gp = df_bat[df_bat["batter"] == pi["mlbam_id"]]
            if pdf_gp.empty:
                continue
            vs_l = pdf_gp[pdf_gp["p_throws"] == "L"]
            vs_r = pdf_gp[pdf_gp["p_throws"] == "R"]
            if not vs_l.empty and not vs_r.empty:
                sl = batting_stats(vs_l)
                sr = batting_stats(vs_r)
                if sl["PA"] >= 30 and sr["PA"] >= 30:
                    if sl["OPS"] < sr["OPS"] - 0.080:
                        if lang == "EN":
                            _platoon_targets.append(f"- **{dn}:** Weak vs LHP (OPS .{int(sl['OPS']*1000):03d}) — use left-handed reliever")
                        else:
                            _platoon_targets.append(f"- **{dn}:** 左投手に弱い（OPS .{int(sl['OPS']*1000):03d}） — 左腕リリーフを起用")
                    elif sr["OPS"] < sl["OPS"] - 0.080:
                        if lang == "EN":
                            _platoon_targets.append(f"- **{dn}:** Weak vs RHP (OPS .{int(sr['OPS']*1000):03d}) — use right-handed reliever")
                        else:
                            _platoon_targets.append(f"- **{dn}:** 右投手に弱い（OPS .{int(sr['OPS']*1000):03d}） — 右腕リリーフを起用")

        _platoon_block = "\n".join(_platoon_targets) if _platoon_targets else ("- No significant platoon splits detected" if lang == "EN" else "- 大きな左右差は検出されず")

        # Per-batter scouting lines for late-game
        _late_bat_en = []
        _late_bat_ja = []
        for p in PREDICTED_LINEUP:
            s = _gp_batter_stats.get(p["name"], {})
            if not s:
                continue
            dn_en = p["name"]
            dn_ja = _name_display(p["name"], "JA")
            stat_tag = f"AVG .{int(s['AVG']*1000):03d}, OPS .{int(s['OPS']*1000):03d}, K% {s['K%']:.1f}%, BB% {s['BB%']:.1f}%"
            _late_bat_en.append(f"- **{dn_en} (#{p['order']}):** {stat_tag} — {p['note_en']}")
            _late_bat_ja.append(f"- **{dn_ja} (#{p['order']}):** {stat_tag} — {p['note_ja']}")

        if lang == "EN":
            st.info(
                "**Late-game batter data:**\n\n"
                "**Platoon splits (OPS diff ≥ 80 pts):**\n"
                + _platoon_block + "\n\n"
                "**Per-batter stats (3rd time through or pinch-hit):**\n"
                + "\n".join(_late_bat_en)
            )
        else:
            st.info(
                "**終盤の打者別データ:**\n\n"
                "**左右別OPSに差がある打者（80pts以上）:**\n"
                + _platoon_block + "\n\n"
                "**打者別成績一覧（3巡目 or 代打想定）:**\n"
                + "\n".join(_late_bat_ja)
            )

        # ===== Section E: Pinch-Hit Matchups =====
        st.divider()
        st.subheader(t["gp_pinch_hit"])

        # Build pinch-hit candidate lines with stats from data
        _ph_lines_en = []
        _ph_lines_ja = []
        for bp in BENCH_PLAYERS:
            bp_info = PLAYER_BY_NAME.get(bp["name"])
            if not bp_info:
                _ph_lines_en.append(f"- **{bp['name']}:** {bp['role_en']}")
                _ph_lines_ja.append(f"- **{_name_display(bp['name'], 'JA')}:** {bp['role_ja']}")
                continue
            bp_data = df_bat[df_bat["batter"] == bp_info["mlbam_id"]]
            if bp_data.empty:
                _ph_lines_en.append(f"- **{bp['name']}:** {bp['role_en']}")
                _ph_lines_ja.append(f"- **{_name_display(bp['name'], 'JA')}:** {bp['role_ja']}")
                continue
            bp_s = batting_stats(bp_data)
            stat_tag = f"AVG .{int(bp_s['AVG']*1000):03d}, OPS .{int(bp_s['OPS']*1000):03d}, K% {bp_s['K%']:.1f}%"
            _ph_lines_en.append(f"- **{bp['name']}:** {stat_tag} — {bp['role_en']}")
            _ph_lines_ja.append(f"- **{_name_display(bp['name'], 'JA')}:** {stat_tag} — {bp['role_ja']}")

        if lang == "EN":
            st.info(
                "**Watch for these pinch-hitters from the 6th inning:**\n"
                + "\n".join(_ph_lines_en) + "\n\n"
                "**MLB stats note:** All stats from 2024-2025 regular season (Statcast)"
            )
        else:
            st.info(
                "**代打候補の成績データ:**\n"
                + "\n".join(_ph_lines_ja)
            )

    # ===================================================================
    # TAB 2: Venezuela Lineup Scouting
    # ===================================================================
    with tab2:
        season_label = f"{season} MLB Season (Statcast)" if lang == "EN" else f"{season}年 MLBシーズン（Statcast）"
        st.markdown(f"""<div class="tab-header">
            <h2>⚔️ {t['tab2']}</h2>
            <p class="tab-sub">{season_label}</p>
        </div>""", unsafe_allow_html=True)

        # Team batting radar chart (using predicted lineup)
        lineup_stats_list = []
        for p in PREDICTED_LINEUP:
            player_info = PLAYER_BY_NAME.get(p["name"])
            if not player_info:
                continue
            pdf = df_bat[df_bat["batter"] == player_info["mlbam_id"]]
            if pdf.empty:
                continue
            s = batting_stats(pdf)
            if s["PA"] >= 50:
                lineup_stats_list.append({"name": p["name"], **s})

        if lineup_stats_list:
            _team_radar_sub = "スタメン9名の平均をMLB平均と比較" if lang == "JA" else "Starting 9 average vs MLB average"
            st.markdown(f"""<div class="section-header"><h3>📡 {t['team_radar_title']}</h3><p>{_team_radar_sub}</p></div>""", unsafe_allow_html=True)
            avg_avg = np.mean([ps["AVG"] for ps in lineup_stats_list])
            avg_obp = np.mean([ps["OBP"] for ps in lineup_stats_list])
            avg_slg = np.mean([ps["SLG"] for ps in lineup_stats_list])
            avg_k = np.mean([ps["K%"] for ps in lineup_stats_list])
            avg_bb = np.mean([ps["BB%"] for ps in lineup_stats_list])

            norm_avg = min(avg_avg / 0.300, 1.0)
            norm_obp = min(avg_obp / 0.380, 1.0)
            norm_slg = min(avg_slg / 0.500, 1.0)
            norm_k = 1.0 - min(avg_k / 35.0, 1.0)
            norm_bb = min(avg_bb / 15.0, 1.0)

            categories = ["AVG", "OBP", "SLG",
                          "K%" if lang == "EN" else "三振率",
                          "BB%" if lang == "EN" else "四球率"]
            values = [norm_avg, norm_obp, norm_slg, norm_k, norm_bb]
            raw_values = [f"{avg_avg:.3f}", f"{avg_obp:.3f}", f"{avg_slg:.3f}",
                          f"{avg_k:.1f}%", f"{avg_bb:.1f}%"]

            mlb_vals = [
                min(_MLB_AVG_BAT["AVG"] / 0.300, 1.0),
                min(_MLB_AVG_BAT["OBP"] / 0.380, 1.0),
                min(_MLB_AVG_BAT["SLG"] / 0.500, 1.0),
                1.0 - min(_MLB_AVG_BAT["K%"] / 35.0, 1.0),
                min(_MLB_AVG_BAT["BB%"] / 15.0, 1.0),
            ]

            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            values_plot = values + [values[0]]
            angles_plot = angles + [angles[0]]
            mlb_plot = mlb_vals + [mlb_vals[0]]

            _sl_tr, _cc_tr, _sr_tr = st.columns([1, 4, 1])
            with _cc_tr:
                fig_radar, ax_radar = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True),
                                                   facecolor="#0e1117")
                ax_radar.set_facecolor("#0e1117")
                ax_radar.plot(angles_plot, mlb_plot, "--", linewidth=1.5, color="#888888",
                              alpha=0.7, label="MLB avg")
                ax_radar.fill(angles_plot, mlb_plot, alpha=0.08, color="#888888")
                ax_radar.plot(angles_plot, values_plot, "o-", linewidth=2, color="#4fc3f7",
                              label="Team avg" if lang == "EN" else "チーム平均")
                ax_radar.fill(angles_plot, values_plot, alpha=0.25, color="#4fc3f7")
                ax_radar.set_thetagrids(np.degrees(angles), categories, color="white", fontsize=12)
                ax_radar.set_ylim(0, 1.2)
                ax_radar.set_yticks([0.25, 0.5, 0.75, 1.0])
                ax_radar.set_yticklabels(["", "", "", ""], color="white")
                ax_radar.grid(color="gray", alpha=0.3)
                ax_radar.spines["polar"].set_color("gray")
                for angle, val, raw in zip(angles, values, raw_values):
                    dx = np.cos(angle - np.pi / 2) * 35
                    dy = np.sin(angle - np.pi / 2) * 35
                    ax_radar.annotate(raw, xy=(angle, val),
                                      xytext=(dx, dy), textcoords="offset points",
                                      fontsize=12, ha="center", va="center",
                                      color="white", fontweight="bold")
                leg = ax_radar.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
                                      fontsize=12, facecolor="#0e1117", edgecolor="gray")
                for txt in leg.get_texts():
                    txt.set_color("white")
                fig_radar.tight_layout()
                st.pyplot(fig_radar, use_container_width=True)
                plt.close(fig_radar)
                st.caption("Gray dashed = MLB avg. K% inverted (lower = better)."
                           if lang == "EN" else
                           "灰色の破線 = MLB平均。K%（三振率）は低いほど外側 = 良い。")

        st.divider()

        # ---------------------------------------------------------------
        # All-batters summary table + selectbox for individual report
        # ---------------------------------------------------------------
        _bat_roster_title = "打者一覧（全ロースター）" if lang == "JA" else "All Batters (Full Roster)"
        _bat_roster_sub = "スタメン9名 ＋ 控え選手。選手を選択すると詳細分析が表示されます。" if lang == "JA" else "Starting 9 + bench. Select a player for detailed analysis."
        st.markdown(f"""<div class="section-header"><h3>🇻🇪 {_bat_roster_title}</h3><p>{_bat_roster_sub}</p></div>""", unsafe_allow_html=True)

        # Build lineup lookup for quick order retrieval
        _lineup_order = {le["name"]: le["order"] for le in PREDICTED_LINEUP}
        _lineup_pos = {le["name"]: le["pos"] for le in PREDICTED_LINEUP}

        batter_rows = []
        for p in VENEZUELA_BATTERS:
            pi = PLAYER_BY_NAME.get(p["name"])
            if not pi:
                continue
            bdf = df_bat[df_bat["batter"] == pi["mlbam_id"]]
            order = _lineup_order.get(p["name"])
            role = f"#{order}" if order else ("控え" if lang == "JA" else "Bench")
            pos = _lineup_pos.get(p["name"], pi["pos"])
            if bdf.empty:
                batter_rows.append({"_sort": (0 if order else 1, order or 99), "_key": p["name"],
                                    "role": role, "name": _name_display(p["name"], lang),
                                    "pos": pos, "team": pi["team"], "bats": pi["bats"],
                                    "PA": 0, "AVG": .0, "OBP": .0, "SLG": .0, "OPS": .0})
            else:
                s = batting_stats(bdf)
                batter_rows.append({"_sort": (0 if order else 1, order or 99), "_key": p["name"],
                                    "role": role, "name": _name_display(p["name"], lang),
                                    "pos": pos, "team": pi["team"], "bats": pi["bats"],
                                    "PA": s["PA"], "AVG": s["AVG"], "OBP": s["OBP"],
                                    "SLG": s["SLG"], "OPS": s["OPS"]})

        batter_rows.sort(key=lambda x: x["_sort"])

        # Display summary table
        sum_df = pd.DataFrame(batter_rows)
        col_map = {"role": "打順" if lang == "JA" else "#",
                   "name": "選手名" if lang == "JA" else "Name",
                   "pos": "守備" if lang == "JA" else "Pos",
                   "team": "所属" if lang == "JA" else "Team",
                   "bats": "打席" if lang == "JA" else "Bats",
                   "PA": "PA", "AVG": "AVG", "OBP": "OBP", "SLG": "SLG", "OPS": "OPS"}
        disp_cols = ["role", "name", "pos", "team", "bats", "PA", "AVG", "OBP", "SLG", "OPS"]
        disp_df = sum_df[disp_cols].rename(columns=col_map)
        st.dataframe(
            disp_df.style.format({"AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}", "OPS": "{:.3f}"}
                                 ).background_gradient(subset=["AVG"], cmap="YlOrRd", vmin=0.200, vmax=0.320
                                 ).background_gradient(subset=["OPS"], cmap="YlOrRd", vmin=0.500, vmax=0.900),
            use_container_width=True, hide_index=True, height=min(520, 38 + 35 * len(batter_rows)),
        )

        # Player selector
        sel_options = [f"{r['role']}  {r['name']}（{r['pos']}）" for r in batter_rows]
        sel_idx = st.selectbox(
            "👇 " + ("詳細を見たい選手を選択" if lang == "JA" else "Select a batter for detailed analysis"),
            range(len(sel_options)), format_func=lambda i: sel_options[i],
            key="tab2_batter_select",
        )

        sel_batter_key = batter_rows[sel_idx]["_key"]
        player_info = PLAYER_BY_NAME[sel_batter_key]
        pdf = df_bat[df_bat["batter"] == player_info["mlbam_id"]]
        lineup_entry_match = next((le for le in PREDICTED_LINEUP if le["name"] == sel_batter_key), None)
        order_label = f"#{lineup_entry_match['order']}" if lineup_entry_match else ("控え" if lang == "JA" else "Bench")
        display_name = _name_display(sel_batter_key, lang)
        pos_str = _lineup_pos.get(sel_batter_key, player_info["pos"])
        pos_full_t2 = POS_LABELS[lang].get(pos_str, pos_str)

        _t2_badge = order_label.lstrip("#") if order_label.startswith("#") else order_label
        _t2_bats_label = f"打席: {player_info['bats']}" if lang == "JA" else f"Bats: {player_info['bats']}"
        st.markdown(f"""<div class="player-card-header">
            <div class="order-badge">{_t2_badge}</div>
            <div>
                <p class="player-name">{display_name}</p>
                <p class="player-meta">{pos_str} ({pos_full_t2}) | {player_info.get('team', '')} | {_t2_bats_label}</p>
            </div>
        </div>""", unsafe_allow_html=True)

        if pdf.empty:
            st.warning(t["no_data"])
        else:
            stats = batting_stats(pdf)

            # Profile metrics
            c1, c2, c3 = st.columns(3)
            c1.metric(t["team"], player_info["team"])
            c2.metric(t["pos"], pos_full_t2)
            c3.metric(t["bats"], player_info["bats"])

            c4, c5, c6, c7, c8 = st.columns(5)
            c4.metric("AVG", f"{stats['AVG']:.3f}", delta=f"{stats['AVG'] - 0.243:+.3f}", help=_help("AVG", lang))
            c5.metric("OBP", f"{stats['OBP']:.3f}", delta=f"{stats['OBP'] - 0.312:+.3f}", help=_help("OBP", lang))
            c6.metric("SLG", f"{stats['SLG']:.3f}", delta=f"{stats['SLG'] - 0.397:+.3f}", help=_help("SLG", lang))
            c7.metric("OPS", f"{stats['OPS']:.3f}", delta=f"{stats['OPS'] - 0.709:+.3f}", help=_help("OPS", lang))
            xwoba_vals = pdf[pdf["estimated_woba_using_speedangle"].notna()]["estimated_woba_using_speedangle"]
            xwoba = xwoba_vals.mean() if len(xwoba_vals) > 0 else 0
            c8.metric("xwOBA", f"{xwoba:.3f}", delta=f"{xwoba - 0.311:+.3f}", help=_help("xwOBA", lang))

            kc1, kc2 = st.columns(2)
            kc1.metric("K%", f"{stats['K%']:.1f}%", help=_help("K%", lang))
            kc2.metric("BB%", f"{stats['BB%']:.1f}%", help=_help("BB%", lang))

            with st.expander(t.get("glossary_stats_title", "What do these stats mean?")):
                st.markdown(t["glossary_stats"])
                st.markdown(t["glossary_pct"])

            # Scouting summary
            st.markdown(f"**{t['scouting_summary']}**")
            summary = generate_player_summary(stats, pdf, player_info, lang)
            st.info(summary)

            # === Pitching Plan (How to get this batter out) ===
            st.markdown(f"### {t['pitching_plan_title']}")
            st.caption(t["pitching_plan_explain"])
            pitching_plan = generate_pitching_plan(pdf, stats, player_info, lang)
            st.success(pitching_plan)

            pdf_vs_l = pdf[pdf["p_throws"] == "L"]
            pdf_vs_r = pdf[pdf["p_throws"] == "R"]
            _sl_pp, col_pp_l, col_pp_r, _sr_pp = st.columns([0.5, 2, 2, 0.5])
            with col_pp_l:
                st.markdown(f"**{t['pitching_plan_vs_lhp']}**")
                if not pdf_vs_l.empty and len(pdf_vs_l) >= 30:
                    stats_vs_l = batting_stats(pdf_vs_l)
                    plan_vs_l = generate_pitching_plan(pdf_vs_l, stats_vs_l, player_info, lang)
                    st.info(plan_vs_l)
                else:
                    st.write(t["no_data"])
            with col_pp_r:
                st.markdown(f"**{t['pitching_plan_vs_rhp']}**")
                if not pdf_vs_r.empty and len(pdf_vs_r) >= 30:
                    stats_vs_r = batting_stats(pdf_vs_r)
                    plan_vs_r = generate_pitching_plan(pdf_vs_r, stats_vs_r, player_info, lang)
                    st.info(plan_vs_r)
                else:
                    st.write(t["no_data"])

            # === Defensive Positioning (split by pitcher handedness) ===
            st.markdown(f"### {t['defensive_positioning']}")
            st.caption(t["defensive_explain"])
            _t2_def_vs_lhp = pdf[pdf["p_throws"] == "L"]
            _t2_def_vs_rhp = pdf[pdf["p_throws"] == "R"]
            _t2_dsl, _t2_dcl, _t2_dcr, _t2_dsr = st.columns([0.5, 2, 2, 0.5])
            with _t2_dcl:
                st.markdown(f"**{'vs LHP（左投手時）' if lang == 'JA' else 'vs LHP'}**")
                if len(_t2_def_vs_lhp.dropna(subset=["hc_x", "hc_y"])) >= 20:
                    st.warning(generate_defensive_positioning(_t2_def_vs_lhp, player_info, lang))
                else:
                    st.warning(generate_defensive_positioning(pdf, player_info, lang))
                    st.caption("⚠️ " + ("左投手データ不足のため全体データで算出" if lang == "JA" else "Insufficient LHP data — using overall"))
            with _t2_dcr:
                st.markdown(f"**{'vs RHP（右投手時）' if lang == 'JA' else 'vs RHP'}**")
                if len(_t2_def_vs_rhp.dropna(subset=["hc_x", "hc_y"])) >= 20:
                    st.warning(generate_defensive_positioning(_t2_def_vs_rhp, player_info, lang))
                else:
                    st.warning(generate_defensive_positioning(pdf, player_info, lang))
                    st.caption("⚠️ " + ("右投手データ不足のため全体データで算出" if lang == "JA" else "Insufficient RHP data — using overall"))

            # --- Individual radar chart ---
            _MLB_AVG_R = {"AVG": .243, "OBP": .312, "SLG": .397, "K%": 22.4, "BB%": 8.3}
            radar_cats = ["AVG", "OBP", "SLG",
                          "K%" if lang == "EN" else "三振率",
                          "BB%" if lang == "EN" else "四球率"]
            player_vals = [
                min(stats["AVG"] / 0.300, 1.0), min(stats["OBP"] / 0.380, 1.0),
                min(stats["SLG"] / 0.500, 1.0), 1.0 - min(stats["K%"] / 35.0, 1.0),
                min(stats["BB%"] / 15.0, 1.0),
            ]
            mlb_vals_r = [
                min(_MLB_AVG_R["AVG"] / 0.300, 1.0), min(_MLB_AVG_R["OBP"] / 0.380, 1.0),
                min(_MLB_AVG_R["SLG"] / 0.500, 1.0), 1.0 - min(_MLB_AVG_R["K%"] / 35.0, 1.0),
                min(_MLB_AVG_R["BB%"] / 15.0, 1.0),
            ]
            raw_vals_r = [f"{stats['AVG']:.3f}", f"{stats['OBP']:.3f}", f"{stats['SLG']:.3f}",
                          f"{stats['K%']:.1f}%", f"{stats['BB%']:.1f}%"]
            angles_r = np.linspace(0, 2 * np.pi, len(radar_cats), endpoint=False).tolist()
            p_plot = player_vals + [player_vals[0]]
            m_plot = mlb_vals_r + [mlb_vals_r[0]]
            a_plot = angles_r + [angles_r[0]]
            _sl_ir, _cc_ir, _sr_ir = st.columns([1, 4, 1])
            with _cc_ir:
                fig_pr, ax_pr = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True), facecolor="#0e1117")
                ax_pr.set_facecolor("#0e1117")
                ax_pr.plot(a_plot, m_plot, "--", linewidth=1.5, color="#888888", alpha=0.7, label="MLB avg")
                ax_pr.fill(a_plot, m_plot, alpha=0.08, color="#888888")
                ax_pr.plot(a_plot, p_plot, "o-", linewidth=2, color="#4fc3f7", label=display_name)
                ax_pr.fill(a_plot, p_plot, alpha=0.25, color="#4fc3f7")
                ax_pr.set_thetagrids(np.degrees(angles_r), radar_cats, color="white", fontsize=12)
                ax_pr.set_ylim(0, 1.2)
                ax_pr.set_yticks([0.25, 0.5, 0.75, 1.0])
                ax_pr.set_yticklabels(["", "", "", ""], color="white")
                ax_pr.grid(color="gray", alpha=0.3)
                ax_pr.spines["polar"].set_color("gray")
                for angle, val, raw in zip(angles_r, player_vals, raw_vals_r):
                    dx = np.cos(angle - np.pi / 2) * 35
                    dy = np.sin(angle - np.pi / 2) * 35
                    ax_pr.annotate(raw, xy=(angle, val), xytext=(dx, dy), textcoords="offset points",
                                   fontsize=12, ha="center", va="center", color="white", fontweight="bold")
                leg_pr = ax_pr.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15),
                                       fontsize=12, facecolor="#0e1117", edgecolor="gray")
                for txt in leg_pr.get_texts():
                    txt.set_color("white")
                fig_pr.tight_layout()
                st.pyplot(fig_pr, use_container_width=True)
                plt.close(fig_pr)
                st.caption("Gray dashed = MLB avg (2024). K% is inverted — lower is better."
                           if lang == "EN" else
                           "灰色の破線 = MLB平均（2024年）。K%（三振率）は低いほど外側 = 良い。")

            # --- 3x3 Zone heatmap (BA + xwOBA) ---
            for z3_metric, z3_title in [("ba", t["ba_heatmap"]), ("xwoba", t["xwoba_heatmap"])]:
                st.markdown(f"**{t['zone_3x3']} — {z3_title}**")
                z3_cap = t["danger_zone"] if z3_metric == "ba" else t.get("danger_zone_xwoba", t["danger_zone"])
                st.caption(z3_cap)
                _sl_z3, _cc_z3, _sr_z3 = st.columns([1, 4, 1])
                with _cc_z3:
                    fig_z3, ax_z3 = _dark_fig(figsize=(6, 5))
                    im_z3 = draw_zone_3x3(pdf, z3_metric, z3_title, ax_z3, lang=lang)
                    cb_z3 = fig_z3.colorbar(im_z3, ax=ax_z3, fraction=0.046, pad=0.04)
                    cb_z3.ax.tick_params(colors="white")
                    fig_z3.tight_layout(pad=2.0)
                    st.pyplot(fig_z3, use_container_width=True)
                    plt.close(fig_z3)

            # --- 5x5 Zone heatmaps (split by pitcher handedness) ---
            st.markdown(f"**{t['zone_5x5']}**")
            _t2_zone_vs_lhp = pdf[pdf["p_throws"] == "L"]
            _t2_zone_vs_rhp = pdf[pdf["p_throws"] == "R"]
            for hm_metric, hm_title, hm_caption in [
                ("ba", t["ba_heatmap"], t["danger_zone"]),
                ("xwoba", t["xwoba_heatmap"], t.get("danger_zone_xwoba", t["danger_zone"])),
            ]:
                st.caption(hm_caption)
                _t2_hzl, _t2_hcl, _t2_hcr, _t2_hzr = st.columns([0.5, 2, 2, 0.5])
                for _t2_hcol, _t2_hdf, _t2_hlbl in [
                    (_t2_hcl, _t2_zone_vs_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                    (_t2_hcr, _t2_zone_vs_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
                ]:
                    with _t2_hcol:
                        st.markdown(f"**{_t2_hlbl}**")
                        _t2_hdf_use = _t2_hdf if len(_t2_hdf) >= 30 else pdf
                        fig_hm, ax_hm = _dark_fig(figsize=(5, 4))
                        im_hm = draw_zone_heatmap(_t2_hdf_use, hm_metric, f"{_t2_hlbl} — {hm_title}", ax_hm, lang=lang)
                        cb_hm = fig_hm.colorbar(im_hm, ax=ax_hm, fraction=0.046, pad=0.04)
                        cb_hm.ax.tick_params(colors="white")
                        fig_hm.tight_layout()
                        st.pyplot(fig_hm, use_container_width=True)
                        plt.close(fig_hm)
                        if len(_t2_hdf) < 30:
                            st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

            # --- Spray chart ---
            st.markdown(f"**{t['spray_chart']}**")
            st.caption(t["spray_caption"])
            _sl_sp, _cc_sp, _sr_sp = st.columns([1, 4, 1])
            with _cc_sp:
                fig_sp, ax_sp = plt.subplots(figsize=(5, 5), facecolor="#0e1117")
                ax_sp.set_facecolor("#0e1117")
                draw_spray_chart(pdf, display_name, ax_sp, stadium="marlins", density=True, lang=lang)
                fig_sp.tight_layout()
                st.pyplot(fig_sp, use_container_width=True)
                plt.close(fig_sp)

            # Spray chart vs LHP / vs RHP
            spray_lhp = "Spray Chart — vs LHP" if lang == "EN" else "打球方向図 — vs 左投手"
            spray_rhp = "Spray Chart — vs RHP" if lang == "EN" else "打球方向図 — vs 右投手"
            _sl_slr, col_sp_l, col_sp_r, _sr_slr = st.columns([0.5, 2, 2, 0.5])
            for col_sp, throws_sp, sp_title in [(col_sp_l, "L", spray_lhp), (col_sp_r, "R", spray_rhp)]:
                with col_sp:
                    split_sp = pdf[pdf["p_throws"] == throws_sp]
                    if split_sp.empty:
                        st.write(t["no_data"])
                        continue
                    fig_sps, ax_sps = plt.subplots(figsize=(5, 5), facecolor="#0e1117")
                    ax_sps.set_facecolor("#0e1117")
                    draw_spray_chart(split_sp, sp_title, ax_sps, stadium="marlins", density=True, lang=lang)
                    fig_sps.tight_layout()
                    st.pyplot(fig_sps, use_container_width=True)
                    plt.close(fig_sps)

            # --- Batted Ball Profile (split by pitcher handedness) ---
            st.markdown(f"**{t['batted_ball']}**")
            with st.expander("What do these mean?" if lang == "EN" else "用語の説明を見る"):
                st.markdown(t["glossary_batted"])
            _t2_bb_lhp = pdf[pdf["p_throws"] == "L"]
            _t2_bb_rhp = pdf[pdf["p_throws"] == "R"]
            _t2_bbsl, _t2_bbcl, _t2_bbcr, _t2_bbsr = st.columns([0.5, 2, 2, 0.5])
            for _t2_bbcol, _t2_bbdf, _t2_bblbl in [
                (_t2_bbcl, _t2_bb_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                (_t2_bbcr, _t2_bb_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
            ]:
                with _t2_bbcol:
                    st.markdown(f"**{_t2_bblbl}**")
                    _t2_bbdf_use = _t2_bbdf if len(_t2_bbdf) >= 30 else pdf
                    profile = batted_ball_profile(_t2_bbdf_use, t)
                    if profile:
                        bb_cols = st.columns(2)
                        for idx, (k, v) in enumerate(profile.items()):
                            bb_cols[idx % 2].metric(k, v)
                    else:
                        st.write(t["no_data"])
                    if len(_t2_bbdf) < 30:
                        st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

            # --- Pitch type performance (split by pitcher handedness) ---
            st.markdown(f"**{t['pitch_type_perf']}**")
            with st.expander(t["glossary_pitch"] if lang == "EN" else "空振率・チェイス率とは？"):
                st.markdown(t["glossary_pitch"])
            _t2_pt_lhp = pdf[pdf["p_throws"] == "L"]
            _t2_pt_rhp = pdf[pdf["p_throws"] == "R"]
            for _t2_ptdf, _t2_ptlbl in [
                (_t2_pt_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                (_t2_pt_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
            ]:
                st.markdown(f"**{_t2_ptlbl}**")
                _t2_ptdf_use = _t2_ptdf if len(_t2_ptdf) >= 30 else pdf
                pt_tbl = pitch_type_table(_t2_ptdf_use, t)
                if not pt_tbl.empty:
                    st.dataframe(pt_tbl, use_container_width=True, hide_index=True)

                    chart_data = pt_tbl[[t["pitch_type"], t["whiff_pct"]]].copy()
                    chart_data["whiff_val"] = chart_data[t["whiff_pct"]].str.rstrip("%").astype(float)
                    chart_data = chart_data.sort_values("whiff_val", ascending=True)

                    _sl_wh, _cc_wh, _sr_wh = st.columns([1, 4, 1])
                    with _cc_wh:
                        fig_pt, ax_pt = _dark_fig(figsize=(8, max(3, len(chart_data) * 0.5)))
                        colors_bar = plt.cm.RdYlGn_r(chart_data["whiff_val"] / max(chart_data["whiff_val"].max(), 1))
                        bars = ax_pt.barh(chart_data[t["pitch_type"]], chart_data["whiff_val"], color=colors_bar)
                        for bar, val in zip(bars, chart_data["whiff_val"]):
                            ax_pt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                                       f"{val:.1f}%", va="center", ha="left", color="white",
                                       fontsize=12, fontweight="bold")
                        ax_pt.set_xlabel(t["whiff_pct"], color="white", fontsize=14)
                        ax_pt.tick_params(colors="white", labelsize=12)
                        ax_pt.set_title(f"{_t2_ptlbl} — {t['whiff_pct']}", color="white", fontsize=16, fontweight="bold")
                        x_max = chart_data["whiff_val"].max()
                        ax_pt.set_xlim(0, x_max * 1.25 if x_max > 0 else 10)
                        for spine in ax_pt.spines.values():
                            spine.set_color("white")
                        fig_pt.tight_layout()
                        st.pyplot(fig_pt, use_container_width=True)
                        plt.close(fig_pt)
                    if len(_t2_ptdf) < 30:
                        st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

            # --- Platoon splits ---
            st.markdown(f"**{t['platoon']}**")
            with st.expander("What are platoon splits?" if lang == "EN" else "左右投手別成績とは？"):
                st.markdown(t["glossary_platoon"])
            _sl_pl, col_l, col_r, _sr_pl = st.columns([0.5, 2, 2, 0.5])

            for col, throws_val, label in [(col_l, "L", t["vs_lhp"]), (col_r, "R", t["vs_rhp"])]:
                with col:
                    st.markdown(f"**{label}**")
                    split_df = pdf[pdf["p_throws"] == throws_val]
                    if split_df.empty:
                        st.write(t["no_data"])
                        continue
                    ss = batting_stats(split_df)
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("AVG", f"{ss['AVG']:.3f}", help=_help("AVG", lang))
                    m2.metric("OBP", f"{ss['OBP']:.3f}", help=_help("OBP", lang))
                    m3.metric("SLG", f"{ss['SLG']:.3f}", help=_help("SLG", lang))
                    m4.metric("OPS", f"{ss['OPS']:.3f}", help=_help("OPS", lang))

                    fig_z_pl, ax_z_pl = _dark_fig(figsize=(5, 4))
                    draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_z_pl, lang=lang)
                    fig_z_pl.tight_layout()
                    st.pyplot(fig_z_pl, use_container_width=True)
                    plt.close(fig_z_pl)

            # --- Count-by-count performance (split by pitcher handedness) ---
            st.markdown(f"**{t['count_perf']}**")
            st.caption(t["count_explain"])
            _t2_cnt_lhp = pdf[pdf["p_throws"] == "L"]
            _t2_cnt_rhp = pdf[pdf["p_throws"] == "R"]
            all_counts = [
                (0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
                (2, 1), (1, 2), (3, 0), (2, 2), (3, 1), (3, 2),
            ]
            for _t2_cntdf, _t2_cntlbl in [
                (_t2_cnt_lhp, "vs LHP" if lang == "EN" else "vs 左投手"),
                (_t2_cnt_rhp, "vs RHP" if lang == "EN" else "vs 右投手"),
            ]:
                st.markdown(f"**{_t2_cntlbl}**")
                _t2_cntdf_use = _t2_cntdf if len(_t2_cntdf) >= 50 else pdf
                count_df = _t2_cntdf_use.dropna(subset=["balls", "strikes"]).copy()
                count_df["balls"] = count_df["balls"].astype(int)
                count_df["strikes"] = count_df["strikes"].astype(int)
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
                        ("Count" if lang == "EN" else "カウント"): f"{b}-{s}",
                        ("Type" if lang == "EN" else "分類"): tag,
                        "PA": cs["PA"], "AVG": cs["AVG"], "OBP": cs["OBP"],
                        "SLG": cs["SLG"], "OPS": cs["OPS"], "K%": cs["K%"], "BB%": cs["BB%"],
                    })
                if count_rows:
                    count_table = pd.DataFrame(count_rows)
                    _ct_type_col = "Type" if lang == "EN" else "分類"
                    st.dataframe(
                        count_table.style.format({
                            "AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}",
                            "OPS": "{:.3f}", "K%": "{:.1f}", "BB%": "{:.1f}",
                        }).background_gradient(subset=["AVG"], cmap="YlOrRd", vmin=0.150, vmax=0.350
                        ).background_gradient(subset=["OPS"], cmap="YlOrRd", vmin=0.400, vmax=1.000
                        ).background_gradient(subset=["K%"], cmap="YlOrRd_r", vmin=10, vmax=40
                        ).map(lambda v: _style_count_type(v, t), subset=[_ct_type_col]),
                        use_container_width=True, hide_index=True,
                    )
                if len(_t2_cntdf) < 50:
                    st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))

    # ===================================================================
    # TAB 3: Ranger Suarez Analysis
    # ===================================================================
    with tab3:
        season_label = f"{season} MLB Season (Statcast)" if lang == "EN" else f"{season}年 MLBシーズン（Statcast）"
        st.markdown(f"""<div class="tab-header">
            <h2>🎱 {t['tab3']}</h2>
            <p class="tab-sub">{season_label}</p>
        </div>""", unsafe_allow_html=True)

        sp_info = PITCHER_BY_NAME.get(PREDICTED_SP, {})
        sp_data = df_pit[df_pit["pitcher"] == sp_info.get("mlbam_id", -1)]

        # Profile card — rich header
        _sp_display = _name_display(PREDICTED_SP, lang)
        _sp_throws = sp_info.get("throws", "—")
        _sp_team = sp_info.get("team", "—")
        st.markdown(f"""<div class="player-card-header">
            <div class="order-badge">SP</div>
            <div>
                <p class="player-name">{_sp_display}</p>
                <p class="player-meta">{t['sp_label']} | {_sp_team} | {'投: ' + _sp_throws if lang == 'JA' else 'Throws: ' + _sp_throws}</p>
            </div>
        </div>""", unsafe_allow_html=True)
        pc1, pc2, pc3 = st.columns(3)
        pc1.metric(t["team"], _sp_team)
        pc2.metric(t["throws"], _sp_throws)
        pc3.metric(t["role"], t["sp_label"])

        if sp_data.empty:
            st.warning(t["no_data"])
        else:
            sp_stats = pitching_stats(sp_data)

            # Key metrics with MLB comparison
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric(t["opp_avg"], f"{sp_stats['Opp AVG']:.3f}",
                       delta=f"{sp_stats['Opp AVG'] - _MLB_AVG_PIT['Opp AVG']:+.3f} vs MLB avg",
                       delta_color="inverse", help=_help("Opp AVG", lang))
            sc2.metric(t["k_pct"], f"{sp_stats['K%']:.1f}%",
                       delta=f"{sp_stats['K%'] - _MLB_AVG_PIT['K%']:+.1f}% vs MLB avg",
                       help=_help("K%", lang))
            sc3.metric(t["bb_pct"], f"{sp_stats['BB%']:.1f}%",
                       delta=f"{sp_stats['BB%'] - _MLB_AVG_PIT['BB%']:+.1f}% vs MLB avg",
                       delta_color="inverse", help=_help("BB%", lang))
            sc4, sc5 = st.columns(2)
            sc4.metric(t["whiff_pct"], f"{sp_stats['Whiff%']:.1f}%", help=_help("Whiff%", lang))
            if sp_stats["xwOBA"]:
                sc5.metric(t["xwoba"], f"{sp_stats['xwOBA']:.3f}",
                           delta=f"{sp_stats['xwOBA'] - _MLB_AVG_PIT['xwOBA']:+.3f} vs MLB avg",
                           delta_color="inverse", help=_help("xwOBA", lang))

            # Scouting summary (always visible)
            st.subheader(t["scouting_summary"])
            sp_summary = generate_pitcher_summary(sp_stats, sp_data, sp_info, lang)
            st.info(sp_summary)

            # --- Expander 1: Hitting Plan ---
            with st.expander("📋 " + (t['hitting_plan_title']), expanded=False):
                st.caption(t["hitting_plan_explain"])
                hitting_plan = generate_hitting_plan(sp_data, sp_stats, sp_info, lang)
                st.success(hitting_plan)

                # Split by batter handedness
                sp_vs_lhb = sp_data[sp_data["stand"] == "L"]
                sp_vs_rhb = sp_data[sp_data["stand"] == "R"]
                _sl_hp, col_hp_l, col_hp_r, _sr_hp = st.columns([0.5, 2, 2, 0.5])
                with col_hp_l:
                    st.markdown(f"**{t['hitting_plan_as_lhb']}**")
                    if not sp_vs_lhb.empty and len(sp_vs_lhb) >= 30:
                        stats_lhb = pitching_stats(sp_vs_lhb)
                        plan_lhb = generate_hitting_plan(sp_vs_lhb, stats_lhb, sp_info, lang)
                        st.info(plan_lhb)
                    else:
                        st.write(t["no_data"])
                with col_hp_r:
                    st.markdown(f"**{t['hitting_plan_as_rhb']}**")
                    if not sp_vs_rhb.empty and len(sp_vs_rhb) >= 30:
                        stats_rhb = pitching_stats(sp_vs_rhb)
                        plan_rhb = generate_hitting_plan(sp_vs_rhb, stats_rhb, sp_info, lang)
                        st.info(plan_rhb)
                    else:
                        st.write(t["no_data"])

                # Where to attack — data-driven pitch analysis
                st.markdown(f"### {t['where_to_attack']}")
                _sp_analysis = generate_sp_pitch_analysis(sp_data, lang)
                if _sp_analysis:
                    st.success(_sp_analysis)

            # --- Expander 2: Arsenal & Movement ---
            with st.expander("⚾ " + (t["arsenal"] + " & " + t["movement_chart"]), expanded=False):
                # Arsenal table
                st.markdown(f"**{t['arsenal']}**")
                at = arsenal_table(sp_data, t)
                if not at.empty:
                    st.dataframe(at, use_container_width=True, hide_index=True)
                with st.expander("Stats glossary" if lang == "EN" else "指標の説明"):
                    st.markdown(t["arsenal_explain"])

                st.divider()

                # Movement chart
                st.markdown(f"**{t['movement_chart']}**")
                st.caption(t["movement_note"])
                fig_m, ax_m = plt.subplots(figsize=(8, 5), facecolor="#0e1117")
                ax_m.set_facecolor("#1a1a2e")
                for spine in ax_m.spines.values():
                    spine.set_color("white")
                draw_movement_chart(sp_data, _name_display(PREDICTED_SP, lang), ax_m, density=True)
                fig_m.tight_layout(rect=[0, 0, 0.82, 1])
                _sl_t3_mv, _cc_t3_mv, _sr_t3_mv = st.columns([1, 4, 1])
                with _cc_t3_mv:
                    st.pyplot(fig_m, use_container_width=True)
                plt.close(fig_m)

            # --- Expander 3: Zone Analysis & Platoon ---
            with st.expander("🎯 " + (t["zone_heatmap_pitch"] + " & " + t["platoon"]), expanded=False):
                # Zone heatmap (pitcher location — usage + opp BA)
                st.markdown(f"**{t['zone_heatmap_pitch']}**")
                for _hm_idx, (metric, hm_title) in enumerate([("usage", t["usage_heatmap"]), ("ba", t["ba_heatmap"])]):
                    fig_hm, ax_hm = _dark_fig(figsize=(6, 5))
                    im_hm = draw_zone_heatmap(sp_data, metric, hm_title, ax_hm, lang=lang)
                    cb_hm = fig_hm.colorbar(im_hm, ax=ax_hm, fraction=0.046, pad=0.04)
                    cb_hm.ax.tick_params(colors="white")
                    fig_hm.tight_layout()
                    _sl_t3_hm, _cc_t3_hm, _sr_t3_hm = st.columns([1, 4, 1])
                    with _cc_t3_hm:
                        st.pyplot(fig_hm, use_container_width=True)
                        if metric == "usage":
                            st.caption(t["zone_usage_explain"])
                        else:
                            st.caption(t["zone_opp_ba_explain"])
                    plt.close(fig_hm)

                st.divider()

                # Platoon splits (vs LHB / vs RHB)
                st.markdown(f"**{t['platoon']}**")
                st.caption(t["platoon_pitcher_explain"])
                _sl_t3_pl, _cl_t3_pl, _cr_t3_pl, _sr_t3_pl = st.columns([0.5, 2, 2, 0.5])
                for col, stand, label in [(_cl_t3_pl, "L", t["vs_lhb"]), (_cr_t3_pl, "R", t["vs_rhb"])]:
                    with col:
                        st.markdown(f"**{label}**")
                        split_df = sp_data[sp_data["stand"] == stand]
                        if split_df.empty:
                            st.write(t["no_data"])
                            continue
                        ss = pitching_stats(split_df)
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric(t["opp_avg"], f"{ss['Opp AVG']:.3f}", help=_help("Opp AVG", lang))
                        m2.metric(t["opp_slg"], f"{ss['Opp SLG']:.3f}", help=_help("Opp SLG", lang))
                        m3.metric(t["k_pct"], f"{ss['K%']:.1f}%", help=_help("K%", lang))
                        m4.metric(t["bb_pct"], f"{ss['BB%']:.1f}%", help=_help("BB%", lang))

                        # Zone heatmap per platoon side
                        fig_z, ax_z = _dark_fig(figsize=(5, 4))
                        draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_z, lang=lang)
                        fig_z.tight_layout()
                        st.pyplot(fig_z, use_container_width=True)
                        plt.close(fig_z)

            # --- Expander 4: Count Analysis (split by batter handedness) ---
            with st.expander("📈 " + t["pitch_selection_by_count"], expanded=False):
                st.caption(t["pitch_selection_explain"])
                _sp_cnt_lhb = sp_data[sp_data["stand"] == "L"]
                _sp_cnt_rhb = sp_data[sp_data["stand"] == "R"]

                all_counts_pit = [
                    (0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
                    (2, 1), (1, 2), (3, 0), (2, 2), (3, 1), (3, 2),
                ]

                for _sp_cdf, _sp_clbl in [
                    (_sp_cnt_lhb, t["vs_lhb"]),
                    (_sp_cnt_rhb, t["vs_rhb"]),
                ]:
                    st.markdown(f"**{_sp_clbl}**")
                    _sp_cdf_use = _sp_cdf if len(_sp_cdf) >= 50 else sp_data

                    # Pitch selection by count
                    _sp_ps_tbl = pitch_selection_by_count(_sp_cdf_use, t, lang)
                    if not _sp_ps_tbl.empty:
                        st.dataframe(_sp_ps_tbl, use_container_width=True, hide_index=True)
                    draw_pitch_selection_pies(_sp_cdf_use, t, lang)

                    # Count-by-count pitcher performance
                    st.markdown(f"**{t['count_perf']}**")
                    st.caption(t["count_explain"])

                    pit_count_df = _sp_cdf_use.dropna(subset=["balls", "strikes"]).copy()
                    pit_count_df["balls"] = pit_count_df["balls"].astype(int)
                    pit_count_df["strikes"] = pit_count_df["strikes"].astype(int)

                    pit_count_rows = []
                    for b, s in all_counts_pit:
                        cat = count_category(b, s)
                        tag = {"ahead": t["behind"], "behind": t["ahead"], "even": t["even"]}[cat]  # inverted for pitcher perspective
                        cdf = pit_count_df[(pit_count_df["balls"] == b) & (pit_count_df["strikes"] == s)]
                        if cdf.empty:
                            continue
                        ps = pitching_stats(cdf)
                        if ps["PA"] < 3:
                            continue
                        pit_count_rows.append({
                            ("Count" if lang == "EN" else "\u30ab\u30a6\u30f3\u30c8"): f"{b}-{s}",
                            ("Type" if lang == "EN" else "\u5206\u985e"): tag,
                            "PA": ps["PA"],
                            t["opp_avg"]: ps["Opp AVG"],
                            t["k_pct"]: ps["K%"],
                            t["bb_pct"]: ps["BB%"],
                            t["whiff_pct"]: ps["Whiff%"],
                        })

                    if pit_count_rows:
                        pit_count_table = pd.DataFrame(pit_count_rows)
                        _pit_type_col = "Type" if lang == "EN" else "分類"
                        st.dataframe(
                            pit_count_table.style.format({
                                t["opp_avg"]: "{:.3f}",
                                t["k_pct"]: "{:.1f}",
                                t["bb_pct"]: "{:.1f}",
                                t["whiff_pct"]: "{:.1f}",
                            }).background_gradient(subset=[t["opp_avg"]], cmap="YlOrRd", vmin=0.150, vmax=0.350
                            ).background_gradient(subset=[t["k_pct"]], cmap="YlOrRd", vmin=10, vmax=40
                            ).background_gradient(subset=[t["whiff_pct"]], cmap="YlOrRd", vmin=15, vmax=45
                            ).map(lambda v: _style_count_type(v, t), subset=[_pit_type_col]),
                            use_container_width=True,
                            hide_index=True,
                        )
                    if len(_sp_cdf) < 50:
                        st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))
                    st.divider()

    # ===================================================================
    # TAB 4: Bullpen Scouting
    # ===================================================================
    with tab4:
        season_label = f"{season} MLB Season (Statcast)" if lang == "EN" else f"{season}年 MLBシーズン（Statcast）"
        st.markdown(f"""<div class="tab-header">
            <h2>🔥 {t['tab4']}</h2>
            <p class="tab-sub">{season_label}</p>
        </div>""", unsafe_allow_html=True)

        # Bullpen usage overview
        st.info(t["bullpen_text"])

        with st.expander("📖 " + ("Stats glossary" if lang == "EN" else "指標の説明")):
            st.markdown(t["glossary_stats"])
            st.markdown(t.get("glossary_arsenal_pct", ""))

        # ---------------------------------------------------------------
        # All relievers summary table + selectbox for individual report
        # ---------------------------------------------------------------
        all_relievers = [p for p in VENEZUELA_PITCHERS if p["name"] != PREDICTED_SP]

        # Build summary table
        rp_rows = []
        for p in all_relievers:
            pi = PITCHER_BY_NAME.get(p["name"])
            if not pi:
                continue
            rpd = df_pit[df_pit["pitcher"] == pi["mlbam_id"]]
            is_key = p["name"] in KEY_RELIEVERS
            tag = ("主力" if lang == "JA" else "Key") if is_key else (p.get("role", "RP"))
            if rpd.empty:
                rp_rows.append({"_key": p["name"], "tag": tag,
                                "name": _name_display(p["name"], lang),
                                "throws": pi.get("throws", "—"), "team": pi["team"],
                                "Opp AVG": 0, "K%": 0, "BB%": 0, "Whiff%": 0,
                                "_is_key": is_key})
            else:
                rs = pitching_stats(rpd)
                rp_rows.append({"_key": p["name"], "tag": tag,
                                "name": _name_display(p["name"], lang),
                                "throws": pi.get("throws", "—"), "team": pi["team"],
                                "Opp AVG": rs["Opp AVG"], "K%": rs["K%"],
                                "BB%": rs["BB%"], "Whiff%": rs["Whiff%"],
                                "_is_key": is_key})

        # Key relievers first, then others
        rp_rows.sort(key=lambda x: (0 if x["_is_key"] else 1, x["name"]))

        _pit_roster_title = "投手一覧（先発除く）" if lang == "JA" else "All Pitchers (excl. Starter)"
        _pit_roster_sub = "主力リリーバー ＋ 控え投手。選手を選択すると詳細分析が表示されます。" if lang == "JA" else "Key relievers + bench. Select a pitcher for detailed analysis."
        st.markdown(f"""<div class="section-header"><h3>🇻🇪 {_pit_roster_title}</h3><p>{_pit_roster_sub}</p></div>""", unsafe_allow_html=True)
        rp_sum_df = pd.DataFrame(rp_rows)
        rp_col_map = {"tag": "役割" if lang == "JA" else "Role",
                      "name": "選手名" if lang == "JA" else "Name",
                      "throws": "投" if lang == "JA" else "Throws",
                      "team": "所属" if lang == "JA" else "Team",
                      "Opp AVG": t["opp_avg"], "K%": t["k_pct"],
                      "BB%": t["bb_pct"], "Whiff%": t["whiff_pct"]}
        rp_disp_cols = ["tag", "name", "throws", "team", "Opp AVG", "K%", "BB%", "Whiff%"]
        rp_disp_df = rp_sum_df[rp_disp_cols].rename(columns=rp_col_map)
        st.dataframe(
            rp_disp_df.style.format({t["opp_avg"]: "{:.3f}", t["k_pct"]: "{:.1f}",
                                      t["bb_pct"]: "{:.1f}", t["whiff_pct"]: "{:.1f}"}
                                    ).background_gradient(subset=[t["opp_avg"]], cmap="YlOrRd", vmin=0.180, vmax=0.300
                                    ).background_gradient(subset=[t["k_pct"]], cmap="YlOrRd", vmin=15, vmax=35
                                    ).background_gradient(subset=[t["whiff_pct"]], cmap="YlOrRd", vmin=18, vmax=40),
            use_container_width=True, hide_index=True, height=min(520, 38 + 35 * len(rp_rows)),
        )

        # Player selector
        rp_sel_options = [f"{r['tag']}  {r['name']}（{r['throws']}）" for r in rp_rows]
        rp_sel_idx = st.selectbox(
            "👇 " + ("詳細を見たい投手を選択" if lang == "JA" else "Select a reliever for detailed analysis"),
            range(len(rp_sel_options)), format_func=lambda i: rp_sel_options[i],
            key="tab4_reliever_select",
        )

        reliever_name = rp_rows[rp_sel_idx]["_key"]
        pitcher_info = PITCHER_BY_NAME[reliever_name]
        rp_data = df_pit[df_pit["pitcher"] == pitcher_info["mlbam_id"]]

        _rp_display = _name_display(reliever_name, lang)
        _rp_throws = pitcher_info.get("throws", "—")
        _rp_team = pitcher_info.get("team", "—")
        _rp_role = pitcher_info.get("role", "RP")
        st.markdown(f"""<div class="player-card-header">
            <div class="order-badge">RP</div>
            <div>
                <p class="player-name">{_rp_display}</p>
                <p class="player-meta">{_rp_role} | {_rp_team} | {'投: ' + _rp_throws if lang == 'JA' else 'Throws: ' + _rp_throws}</p>
            </div>
        </div>""", unsafe_allow_html=True)

        rpc1, rpc2, rpc3 = st.columns(3)
        rpc1.metric(t["team"], _rp_team)
        rpc2.metric(t["throws"], _rp_throws)
        rpc3.metric(t["role"], _rp_role)

        if rp_data.empty:
            st.warning(t["no_data"])
        else:
            rp_stats = pitching_stats(rp_data)

            rm1, rm2, rm3, rm4 = st.columns(4)
            rm1.metric(t["opp_avg"], f"{rp_stats['Opp AVG']:.3f}", help=_help("Opp AVG", lang))
            rm2.metric(t["k_pct"], f"{rp_stats['K%']:.1f}%", help=_help("K%", lang))
            rm3.metric(t["bb_pct"], f"{rp_stats['BB%']:.1f}%", help=_help("BB%", lang))
            rm4.metric(t["whiff_pct"], f"{rp_stats['Whiff%']:.1f}%", help=_help("Whiff%", lang))
            if rp_stats["Avg Velo"]:
                velo_label = "平均球速" if lang == "JA" else "Avg Velo"
                st.caption(f"{velo_label}: {rp_stats['Avg Velo']:.1f} mph ({rp_stats['Avg Velo'] * 1.609:.0f} km/h)")

            rp_summary = generate_pitcher_summary(rp_stats, rp_data, pitcher_info, lang)
            st.info(rp_summary)

            # --- Expander 1: Hitting Plan ---
            with st.expander("📋 " + t['hitting_plan_title'], expanded=False):
                st.caption(t["hitting_plan_explain"])
                rp_hitting_plan = generate_hitting_plan(rp_data, rp_stats, pitcher_info, lang)
                st.success(rp_hitting_plan)

                rp_vs_lhb = rp_data[rp_data["stand"] == "L"]
                rp_vs_rhb = rp_data[rp_data["stand"] == "R"]
                _sl_rphp, col_rphp_l, col_rphp_r, _sr_rphp = st.columns([0.5, 2, 2, 0.5])
                with col_rphp_l:
                    st.markdown(f"**{t['hitting_plan_as_lhb']}**")
                    if not rp_vs_lhb.empty and len(rp_vs_lhb) >= 30:
                        rp_stats_lhb = pitching_stats(rp_vs_lhb)
                        rp_plan_lhb = generate_hitting_plan(rp_vs_lhb, rp_stats_lhb, pitcher_info, lang)
                        st.info(rp_plan_lhb)
                    else:
                        st.write(t["no_data"])
                with col_rphp_r:
                    st.markdown(f"**{t['hitting_plan_as_rhb']}**")
                    if not rp_vs_rhb.empty and len(rp_vs_rhb) >= 30:
                        rp_stats_rhb = pitching_stats(rp_vs_rhb)
                        rp_plan_rhb = generate_hitting_plan(rp_vs_rhb, rp_stats_rhb, pitcher_info, lang)
                        st.info(rp_plan_rhb)
                    else:
                        st.write(t["no_data"])

            # --- Expander 2: Arsenal & Movement ---
            with st.expander("⚾ " + (t["arsenal"] + " & " + t["movement_chart"]), expanded=False):
                rp_arsenal = arsenal_table(rp_data, t)
                if not rp_arsenal.empty:
                    st.markdown(f"**{t['arsenal']}**")
                    st.caption(t["arsenal_explain"])
                    st.dataframe(rp_arsenal, use_container_width=True, hide_index=True)

                st.divider()

                # Movement chart
                st.markdown(f"**{t['movement_chart']}**")
                st.caption(t["movement_note"])
                fig_rp_m, ax_rp_m = plt.subplots(figsize=(8, 5), facecolor="#0e1117")
                ax_rp_m.set_facecolor("#1a1a2e")
                for spine in ax_rp_m.spines.values():
                    spine.set_color("white")
                draw_movement_chart(rp_data, _name_display(reliever_name, lang), ax_rp_m, density=True)
                fig_rp_m.tight_layout(rect=[0, 0, 0.82, 1])
                _sl_rp_mv, _cc_rp_mv, _sr_rp_mv = st.columns([1, 4, 1])
                with _cc_rp_mv:
                    st.pyplot(fig_rp_m, use_container_width=True)
                plt.close(fig_rp_m)

            # --- Expander 3: Zone Analysis & Platoon ---
            with st.expander("🎯 " + (t["zone_heatmap_pitch"] + " & " + t["platoon"]), expanded=False):
                st.markdown(f"**{t['zone_heatmap_pitch']}**")
                for _rp_hm_idx, (rp_hm_metric, rp_hm_title) in enumerate([("usage", t["usage_heatmap"]), ("ba", t["ba_heatmap"])]):
                    fig_rp_hm, ax_rp_hm = _dark_fig(figsize=(6, 5))
                    im_rp_hm = draw_zone_heatmap(rp_data, rp_hm_metric, rp_hm_title, ax_rp_hm, lang=lang)
                    cb_rp_hm = fig_rp_hm.colorbar(im_rp_hm, ax=ax_rp_hm, fraction=0.046, pad=0.04)
                    cb_rp_hm.ax.tick_params(colors="white")
                    fig_rp_hm.tight_layout()
                    _sl_rp_hm, _cc_rp_hm, _sr_rp_hm = st.columns([1, 4, 1])
                    with _cc_rp_hm:
                        st.pyplot(fig_rp_hm, use_container_width=True)
                        if rp_hm_metric == "usage":
                            st.caption(t["zone_usage_explain"])
                        else:
                            st.caption(t["zone_opp_ba_explain"])
                    plt.close(fig_rp_hm)

                st.divider()

                # Platoon splits
                st.markdown(f"**{t['platoon']}**")
                st.caption(t["platoon_pitcher_explain"])
                _sl_rp_pl, _cl_rp_pl, _cr_rp_pl, _sr_rp_pl = st.columns([0.5, 2, 2, 0.5])
                for col, stand, label in [(_cl_rp_pl, "L", t["vs_lhb"]), (_cr_rp_pl, "R", t["vs_rhb"])]:
                    with col:
                        st.markdown(f"**{label}**")
                        split_df = rp_data[rp_data["stand"] == stand]
                        if split_df.empty:
                            st.write(t["no_data"])
                            continue
                        ss = pitching_stats(split_df)
                        sm1, sm2, sm3, sm4 = st.columns(4)
                        sm1.metric(t["opp_avg"], f"{ss['Opp AVG']:.3f}", help=_help("Opp AVG", lang))
                        sm2.metric(t["opp_slg"], f"{ss['Opp SLG']:.3f}", help=_help("Opp SLG", lang))
                        sm3.metric(t["k_pct"], f"{ss['K%']:.1f}%", help=_help("K%", lang))
                        sm4.metric(t["bb_pct"], f"{ss['BB%']:.1f}%", help=_help("BB%", lang))

                        fig_rp_z, ax_rp_z = _dark_fig(figsize=(5, 4))
                        draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_rp_z, lang=lang)
                        fig_rp_z.tight_layout()
                        st.pyplot(fig_rp_z, use_container_width=True)
                        plt.close(fig_rp_z)

            # --- Expander 4: Count Analysis (split by batter handedness) ---
            with st.expander("📈 " + t["pitch_selection_by_count"], expanded=False):
                st.caption(t["pitch_selection_explain"])
                _rp_cnt_lhb = rp_data[rp_data["stand"] == "L"]
                _rp_cnt_rhb = rp_data[rp_data["stand"] == "R"]

                _rp_all_counts = [
                    (0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
                    (2, 1), (1, 2), (3, 0), (2, 2), (3, 1), (3, 2),
                ]

                for _rp_cdf, _rp_clbl in [
                    (_rp_cnt_lhb, t["vs_lhb"]),
                    (_rp_cnt_rhb, t["vs_rhb"]),
                ]:
                    st.markdown(f"**{_rp_clbl}**")
                    _rp_cdf_use = _rp_cdf if len(_rp_cdf) >= 50 else rp_data

                    # Pitch selection by count
                    rp_ps_table = pitch_selection_by_count(_rp_cdf_use, t, lang)
                    if not rp_ps_table.empty:
                        st.dataframe(rp_ps_table, use_container_width=True, hide_index=True)
                    draw_pitch_selection_pies(_rp_cdf_use, t, lang)

                    # Count-by-count pitcher performance
                    st.markdown(f"**{t['count_perf']}**")
                    st.caption(t["count_explain"])

                    _rp_cnt_df = _rp_cdf_use.dropna(subset=["balls", "strikes"]).copy()
                    _rp_cnt_df["balls"] = _rp_cnt_df["balls"].astype(int)
                    _rp_cnt_df["strikes"] = _rp_cnt_df["strikes"].astype(int)

                    _rp_cnt_rows = []
                    for b, s in _rp_all_counts:
                        cat = count_category(b, s)
                        tag = {"ahead": t["behind"], "behind": t["ahead"], "even": t["even"]}[cat]
                        cdf = _rp_cnt_df[(_rp_cnt_df["balls"] == b) & (_rp_cnt_df["strikes"] == s)]
                        if cdf.empty:
                            continue
                        ps = pitching_stats(cdf)
                        if ps["PA"] < 3:
                            continue
                        _rp_cnt_rows.append({
                            ("Count" if lang == "EN" else "\u30ab\u30a6\u30f3\u30c8"): f"{b}-{s}",
                            ("Type" if lang == "EN" else "\u5206\u985e"): tag,
                            "PA": ps["PA"],
                            t["opp_avg"]: ps["Opp AVG"],
                            t["k_pct"]: ps["K%"],
                            t["bb_pct"]: ps["BB%"],
                            t["whiff_pct"]: ps["Whiff%"],
                        })

                    if _rp_cnt_rows:
                        _rp_cnt_table = pd.DataFrame(_rp_cnt_rows)
                        _rp_type_col = "Type" if lang == "EN" else "分類"
                        st.dataframe(
                            _rp_cnt_table.style.format({
                                t["opp_avg"]: "{:.3f}",
                                t["k_pct"]: "{:.1f}",
                                t["bb_pct"]: "{:.1f}",
                                t["whiff_pct"]: "{:.1f}",
                            }).background_gradient(subset=[t["opp_avg"]], cmap="YlOrRd", vmin=0.150, vmax=0.350
                            ).background_gradient(subset=[t["k_pct"]], cmap="YlOrRd", vmin=10, vmax=40
                            ).background_gradient(subset=[t["whiff_pct"]], cmap="YlOrRd", vmin=15, vmax=45
                            ).map(lambda v: _style_count_type(v, t), subset=[_rp_type_col]),
                            use_container_width=True,
                            hide_index=True,
                        )
                    if len(_rp_cdf) < 50:
                        st.caption("⚠️ " + ("データ不足のため全体で算出" if lang == "JA" else "Insufficient data — using overall"))
                    st.divider()


if __name__ == "__main__":
    main()
