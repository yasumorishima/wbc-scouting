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
    {"order": 2, "name": "Jackson Chourio", "pos": "CF", "note_en": "Young star, 5-tool talent", "note_ja": "若き5ツールプレイヤー"},
    {"order": 3, "name": "Luis Arráez", "pos": "1B", "note_en": "Best contact hitter in MLB, batting title contender", "note_ja": "MLB最高のコンタクトヒッター、首位打者候補"},
    {"order": 4, "name": "Willson Contreras", "pos": "DH", "note_en": "Power bat, veteran catcher as DH", "note_ja": "パワー打者、ベテラン捕手のDH起用"},
    {"order": 5, "name": "Eugenio Suárez", "pos": "3B", "note_en": "Corner infield utility (3B/1B)", "note_ja": "コーナー内野ユーティリティ（三塁/一塁）"},
    {"order": 6, "name": "Wilyer Abreu", "pos": "LF", "note_en": "Solid LHB, strong defense", "note_ja": "堅実な左打者、好守備"},
    {"order": 7, "name": "William Contreras", "pos": "C", "note_en": "Switch hitter, starting catcher", "note_ja": "スイッチヒッター、正捕手"},
    {"order": 8, "name": "Gleyber Torres", "pos": "2B", "note_en": "Power from middle infield", "note_ja": "中距離パワーの内野手"},
    {"order": 9, "name": "Andrés Giménez", "pos": "SS", "note_en": "Elite defensive SS, switch hitter", "note_ja": "守備の名手、スイッチヒッター"},
]
# Maikel Garcia — 途中出場（括弧なし＝スタメン外）

PREDICTED_SP = "Ranger Suárez"

KEY_RELIEVERS = ["José Buttó", "Eduard Bazardo", "Daniel Palencia", "Luinder Ávila"]

# MLB average benchmarks (2024 season)
_MLB_AVG_BAT = {"AVG": .243, "OBP": .312, "SLG": .397, "OPS": .709, "K%": 22.4, "BB%": 8.3, "xwOBA": .311}
_MLB_AVG_PIT = {"Opp AVG": .243, "Opp SLG": .397, "K%": 22.4, "BB%": 8.3, "xwOBA": .311, "Whiff%": 25.0, "Velo": 93.5}

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
            "Venezuela's lineup is anchored by Ronald Acuña Jr. at leadoff and Luis Arráez in the #2 hole — "
            "elite speed paired with the best contact hitter in MLB. "
            "The middle of the order features Salvador Perez and William Contreras providing power. "
            "Jackson Chourio adds youth and athleticism in center field. "
            "Andrés Giménez brings left-handed balance and Gold Glove defense at 2B. "
            "All analysis is based on MLB Statcast data (2024-2025 regular season)."
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
        "danger_zone": "Red = danger zone (high BA), Blue = attack zone (low BA)",
        "team_radar_title": "Team Batting Profile (Predicted Lineup)",
        "arsenal": "Pitch Arsenal",
        "usage_pct": "Usage%",
        "avg_velo": "Avg Velo (mph / km/h)",
        "max_velo": "Max Velo (mph / km/h)",
        "avg_spin": "Avg Spin (rpm)",
        "h_break": "H-Break (in)",
        "v_break": "V-Break (in)",
        "put_away_pct": "Put Away%",
        "movement_chart": "Pitch Movement Chart",
        "movement_note": "Each dot = 1 pitch. Horizontal axis = glove-side break, vertical = induced vertical break.",
        "opp_avg": "Opp AVG", "opp_slg": "Opp SLG",
        "k_pct": "K%", "bb_pct": "BB%",
        "xwoba": "xwOBA",
        "where_to_attack": "Where to Attack",
        "attack_text_suarez": (
            "Ranger Suarez is a soft-contact LHP who relies heavily on his sinker and changeup. "
            "Against RHB: look for the changeup down and away — it generates swings and misses "
            "but can be vulnerable when left up in the zone. "
            "Against LHB: his sinker runs arm-side; sit on pitches on the inner half. "
            "Key: be patient early — he is a pitch-to-contact pitcher with a low K rate. "
            "Force him to elevate or fall behind in counts."
        ),
        "bullpen_overview": "Bullpen Usage Pattern",
        "bullpen_text": (
            "Venezuela's bullpen features a mix of power arms and multi-inning options. "
            "José Buttó (RHP, Giants) is a high-leverage reliever with swing-and-miss stuff. "
            "Eduard Bazardo (RHP, Mariners) serves as a multi-inning bridge option. "
            "Daniel Palencia (RHP, Cubs) adds depth with power stuff. "
            "Luinder Ávila (RHP, Royals) is a replacement call-up. "
            "All stats below are from MLB Statcast (2024-2025 regular season)."
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
        "pull_pct": "Pull%",
        "cent_pct": "Center%",
        "oppo_pct": "Oppo%",
        "gb_pct": "GB%",
        "ld_pct": "LD%",
        "fb_pct": "FB%",
        "avg_ev": "Avg EV (mph)",
        "avg_la": "Avg LA (deg)",
        "count_perf": "Performance by Count",
        "count_explain": (
            "Ahead = ball count > strike count (e.g. 2-1, 3-0). "
            "Behind = strike count > ball count (e.g. 0-2, 1-2). "
            "Even = same count (e.g. 1-1, 2-2)."
        ),
        "ahead": "Hitter Ahead (B > S)",
        "behind": "Hitter Behind (S > B)",
        "even": "Even (B = S)",
        "danger_zone_xwoba": "Red = high xwOBA (danger), Blue = low xwOBA (attack)",
        "glossary_batted": (
            "- **Pull%** = Hit to batter's pull side\n"
            "- **GB%** = Ground ball rate\n- **LD%** = Line drive rate\n- **FB%** = Fly ball rate\n"
            "- **Avg EV** = Average exit velocity (mph)\n- **Avg LA** = Average launch angle (degrees)"
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
        "pitch_selection_explain": "Shows what pitch types the pitcher throws in different count situations. Use this to predict what pitch is coming.",
        "count_ahead_pitcher": "Pitcher Ahead (S > B)",
        "count_behind_pitcher": "Pitcher Behind (B > S)",
        "count_even_pitcher": "Even Count (B = S)",
        "count_first_pitch": "First Pitch (0-0)",
        "count_two_strikes": "Two Strikes (x-2)",
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
            "ベネズエラ打線はアクーニャJr.のリードオフとアラエスの2番で構成 — "
            "俊足とMLB最高のコンタクト力の組み合わせ。"
            "中軸はサルバドール・ペレスとウィリアム・コントレラスのパワー。"
            "ジャクソン・チュリオがセンターで若さと身体能力を加える。"
            "アンドレス・ヒメネスは左打者のバランスとゴールドグラブ級の二塁守備。"
            "全ての分析はMLB Statcastデータ（2024-2025レギュラーシーズン）に基づいています。"
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
        "danger_zone": "赤 = 危険ゾーン（高打率）、青 = 攻めるゾーン（低打率）",
        "team_radar_title": "チーム打線の特徴（予想スタメン）",
        "arsenal": "球種構成",
        "usage_pct": "使用率",
        "avg_velo": "平均球速 (mph / km/h)",
        "max_velo": "最高球速 (mph / km/h)",
        "avg_spin": "平均回転数 (rpm)",
        "h_break": "横変化 (in)",
        "v_break": "縦変化 (in)",
        "put_away_pct": "決め球率",
        "movement_chart": "変化量チャート",
        "movement_note": "各ドット = 1球。横軸 = グラブ側への曲がり、縦軸 = 重力に逆らう縦の変化量。",
        "opp_avg": "被打率", "opp_slg": "被長打率",
        "k_pct": "奪三振率", "bb_pct": "与四球率",
        "xwoba": "xwOBA",
        "where_to_attack": "攻略ポイント",
        "attack_text_suarez": (
            "レンジャー・スアレスはソフトコンタクト型の左腕。シンカーとチェンジアップが主体。"
            "対右打者: 外角低めのチェンジアップに空振りを取るが、高めに浮くと打たれやすい。"
            "対左打者: シンカーがアーム側に動く。インコースの球に狙いを絞る。"
            "攻略の鍵: 早いカウントで仕掛けない。奪三振率が低い投手なので、"
            "ボールを見極めてカウントを有利に進め、甘い球を待つ。"
        ),
        "bullpen_overview": "ブルペン運用パターン",
        "bullpen_text": (
            "ベネズエラのブルペンはパワーアームとイニング跨ぎが可能な中継ぎで構成。"
            "ホセ・ブット（右腕、ジャイアンツ）はハイレバレッジの切り札。"
            "エドゥアルド・バサルド（右腕、マリナーズ）はイニング跨ぎの中継ぎ。"
            "ダニエル・パレンシア（右腕、カブス）はパワーピッチャー。"
            "ルインデル・アビラ（右腕、ロイヤルズ）は代替招集。"
            "以下の成績は全てMLB Statcast（2024-2025レギュラーシーズン）のデータです。"
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
        "pull_pct": "プル%（引っ張り）",
        "cent_pct": "センター%",
        "oppo_pct": "逆方向%（流し打ち）",
        "gb_pct": "ゴロ%",
        "ld_pct": "ライナー%",
        "fb_pct": "フライ%",
        "avg_ev": "平均打球速度 (mph)",
        "avg_la": "平均打球角度 (度)",
        "count_perf": "カウント別パフォーマンス",
        "count_explain": (
            "有利カウント = ボール数 > ストライク数（例: 2-1, 3-0）。"
            "不利カウント = ストライク数 > ボール数（例: 0-2, 1-2）。"
            "イーブン = 同数（例: 1-1, 2-2）。"
        ),
        "ahead": "有利カウント (B > S)",
        "behind": "不利カウント (S > B)",
        "even": "イーブン (B = S)",
        "danger_zone_xwoba": "赤 = 高xwOBA（危険）、青 = 低xwOBA（攻めるゾーン）",
        "glossary_batted": (
            "- **プル%** = 引っ張り方向への打球割合\n"
            "- **ゴロ%** = ゴロの割合\n- **ライナー%** = ライナーの割合\n- **フライ%** = フライの割合\n"
            "- **平均打球速度** = 打球のスピード（mph）\n- **平均打球角度** = 打球の打ち出し角度"
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
        "pitch_selection_explain": "カウント状況ごとに投手がどの球種を投げるかの分布。打席でどの球を予測すべきかの参考に。",
        "count_ahead_pitcher": "投手有利 (S > B)",
        "count_behind_pitcher": "投手不利 (B > S)",
        "count_even_pitcher": "イーブン (B = S)",
        "count_first_pitch": "初球 (0-0)",
        "count_two_strikes": "2ストライク (x-2)",
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


def generate_player_summary(stats: dict, pdf: pd.DataFrame, player: dict,
                            lang: str) -> str:
    """Auto-generate a scouting summary for a batter."""
    strengths = []
    weaknesses = []

    if stats["SLG"] >= 0.450:
        strengths.append("elite power (SLG .450+)" if lang == "EN"
                         else "長打力が非常に高い（SLG .450以上）")
    elif stats["SLG"] >= 0.400:
        strengths.append("above-average power" if lang == "EN"
                         else "平均以上の長打力")
    if stats["AVG"] >= 0.300:
        strengths.append("elite contact ability (AVG .300+)" if lang == "EN"
                         else "卓越したコンタクト力（打率 .300以上）")
    elif stats["AVG"] >= 0.270:
        strengths.append("solid contact hitter" if lang == "EN"
                         else "安定したコンタクトヒッター")
    if stats["BB%"] >= 10.0:
        strengths.append(f"patient approach (BB% {stats['BB%']:.1f})" if lang == "EN"
                         else f"選球眼が良い（四球率 {stats['BB%']:.1f}%）")
    if stats["xwOBA"] and stats["xwOBA"] >= 0.350:
        strengths.append("high batted-ball quality (xwOBA .350+)" if lang == "EN"
                         else "打球の質が高い（xwOBA .350以上）")
    if stats["K%"] >= 25.0:
        weaknesses.append(f"high strikeout rate (K% {stats['K%']:.1f})" if lang == "EN"
                          else f"三振が多い（三振率 {stats['K%']:.1f}%）")
    elif stats["K%"] >= 20.0:
        weaknesses.append(f"moderate strikeout rate (K% {stats['K%']:.1f})" if lang == "EN"
                          else f"三振がやや多い（三振率 {stats['K%']:.1f}%）")

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
    ax.set_ylabel("Height (ft)" if lang == "EN" else "高さ (ft)", fontsize=14, color="white")
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
    ax.set_ylabel("Height (ft)" if lang == "EN" else "高さ (ft)", fontsize=14, color="white")
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
            swings = grp[grp["description"].isin({
                "hit_into_play", "foul", "swinging_strike",
                "swinging_strike_blocked", "foul_tip",
            })]
            whiffs = grp[grp["description"].isin({
                "swinging_strike", "swinging_strike_blocked", "foul_tip",
            })]
            ba = len(hits) / len(ab) if len(ab) >= 10 else None
            whiff_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0

            outside = grp[(grp["zone"].notna()) & (grp["zone"] >= 11)]
            chase_swings = outside[outside["description"].isin({
                "hit_into_play", "foul", "swinging_strike",
                "swinging_strike_blocked", "foul_tip",
            })]
            chase_pct = len(chase_swings) / len(outside) * 100 if len(outside) > 0 else 0

            label = PITCH_LABELS.get(pt, pt)
            pt_stats.append({
                "type": pt, "label": label, "count": len(grp),
                "ba": ba, "whiff": whiff_pct, "chase": chase_pct,
            })

        if pt_stats:
            # Best pitch to use (highest whiff%)
            best_whiff = sorted([p for p in pt_stats if p["whiff"] > 0], key=lambda x: x["whiff"], reverse=True)
            # Worst pitch (highest BA against)
            hittable = sorted([p for p in pt_stats if p["ba"] is not None], key=lambda x: x["ba"], reverse=True)
            # Best chase pitch
            best_chase = sorted([p for p in pt_stats if p["chase"] > 0], key=lambda x: x["chase"], reverse=True)

            if best_whiff:
                bw = best_whiff[0]
                if lang == "EN":
                    lines.append(f"**Best strikeout pitch:** {bw['label']} (Whiff% {bw['whiff']:.1f}%)")
                else:
                    lines.append(f"**決め球に最適:** {bw['label']}（空振率 {bw['whiff']:.1f}%）")

            if hittable and hittable[0]["ba"] is not None and hittable[0]["ba"] >= 0.280:
                h = hittable[0]
                if lang == "EN":
                    lines.append(f"**Avoid:** {h['label']} — he hits it well (BA .{int(h['ba']*1000):03d})")
                else:
                    lines.append(f"**要注意球種:** {h['label']} — 打率 .{int(h['ba']*1000):03d} で打たれている")

            if best_chase:
                bc = best_chase[0]
                if lang == "EN":
                    lines.append(f"**Chase pitch:** {bc['label']} outside the zone (Chase% {bc['chase']:.1f}%)")
                else:
                    lines.append(f"**ゾーン外で振らせる球:** {bc['label']}（チェイス率 {bc['chase']:.1f}%）")

    # 2. Zone weakness analysis (3x3)
    zone_valid = pdf.dropna(subset=["zone"]).copy()
    zone_valid["zone"] = zone_valid["zone"].astype(int)
    zone_names_en = {1: "Up-In", 2: "Up-Mid", 3: "Up-Away", 4: "Mid-In", 5: "Heart", 6: "Mid-Away", 7: "Down-In", 8: "Down-Mid", 9: "Down-Away"}
    zone_names_ja = {1: "高めイン", 2: "高め真ん中", 3: "高めアウト", 4: "真ん中イン", 5: "ど真ん中", 6: "真ん中アウト", 7: "低めイン", 8: "低め真ん中", 9: "低めアウト"}
    zone_names = zone_names_ja if lang == "JA" else zone_names_en

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
                lines.append(f"**Attack zones (low BA):** {weak_str}")
            else:
                lines.append(f"**攻めるゾーン（低打率）:** {weak_str}")
        if strong_str:
            if lang == "EN":
                lines.append(f"**Danger zones (high BA):** {strong_str}")
            else:
                lines.append(f"**危険ゾーン（高打率）:** {strong_str}")

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
                lines.append(f"**Count strategy:** Dangerous when ahead in count (OPS .{int(ahead_stats['OPS']*1000):03d}). "
                           f"Get ahead early — he collapses behind (OPS .{int(behind_stats['OPS']*1000):03d})")
            else:
                lines.append(f"**カウント戦略:** 有利カウントで強い（OPS .{int(ahead_stats['OPS']*1000):03d}）。"
                           f"先手を取れ — 不利カウントでは崩れる（OPS .{int(behind_stats['OPS']*1000):03d}）")
        elif behind_stats["OPS"] >= 0.700:
            if lang == "EN":
                lines.append(f"**Count strategy:** Still dangerous behind in count (OPS .{int(behind_stats['OPS']*1000):03d}). "
                           f"Don't let up with 2 strikes — compete through the at-bat.")
            else:
                lines.append(f"**カウント戦略:** 不利カウントでもしぶとい（OPS .{int(behind_stats['OPS']*1000):03d}）。"
                           f"追い込んでも油断禁物 — 最後まで攻め切る")

    if two_strike_stats and two_strike_stats["PA"] >= 20:
        if two_strike_stats["K%"] >= 35:
            if lang == "EN":
                lines.append(f"**2-strike approach:** High K rate with 2 strikes ({two_strike_stats['K%']:.1f}%). "
                           f"Use best put-away pitch aggressively.")
            else:
                lines.append(f"**2ストライク後:** 三振率が高い（{two_strike_stats['K%']:.1f}%）。"
                           f"決め球を大胆に使え")
        elif two_strike_stats["K%"] < 20:
            if lang == "EN":
                lines.append(f"**2-strike approach:** Very hard to strike out ({two_strike_stats['K%']:.1f}% K rate). "
                           f"Expand the zone gradually — don't waste pitches down the middle.")
            else:
                lines.append(f"**2ストライク後:** 三振しにくい（{two_strike_stats['K%']:.1f}%）。"
                           f"ゾーンを少しずつ広げろ — 甘い球は禁物")

    # 4. Platoon recommendation
    vs_l = pdf[pdf["p_throws"] == "L"]
    vs_r = pdf[pdf["p_throws"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        sl = batting_stats(vs_l)
        sr = batting_stats(vs_r)
        if sl["PA"] >= 30 and sr["PA"] >= 30:
            if sl["OPS"] < sr["OPS"] - 0.080:
                if lang == "EN":
                    lines.append(f"**Platoon edge:** Weaker vs LHP (OPS .{int(sl['OPS']*1000):03d} vs .{int(sr['OPS']*1000):03d}). "
                               f"Use left-handed pitcher if available.")
                else:
                    lines.append(f"**左右マッチアップ:** 左投手に弱い（OPS .{int(sl['OPS']*1000):03d} vs 右 .{int(sr['OPS']*1000):03d}）。"
                               f"左腕を当てたい")
            elif sr["OPS"] < sl["OPS"] - 0.080:
                if lang == "EN":
                    lines.append(f"**Platoon edge:** Weaker vs RHP (OPS .{int(sr['OPS']*1000):03d} vs .{int(sl['OPS']*1000):03d}). "
                               f"Use right-handed pitcher if available.")
                else:
                    lines.append(f"**左右マッチアップ:** 右投手に弱い（OPS .{int(sr['OPS']*1000):03d} vs 左 .{int(sl['OPS']*1000):03d}）。"
                               f"右腕を当てたい")

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
                    lines.append(f"**Batted ball:** Strong pull tendency ({pull_pct:.0f}%). "
                               f"Shift defense pull-side. Pitch away to neutralize power.")
                else:
                    lines.append(f"**打球傾向:** プル方向が多い（{pull_pct:.0f}%）。"
                               f"守備シフトをプル側に。外角で長打を防ぐ")

            if gb_pct >= 50:
                if lang == "EN":
                    lines.append(f"**Ground ball hitter ({gb_pct:.0f}% GB).** Keep the ball down — sinkers and low changeups effective.")
                else:
                    lines.append(f"**ゴロ打者（{gb_pct:.0f}%）。** 低め中心の投球が有効 — シンカー、低めチェンジアップ")
            elif fb_pct >= 45:
                if lang == "EN":
                    lines.append(f"**Fly ball hitter ({fb_pct:.0f}% FB).** Careful with pitches up in zone — he elevates. "
                               f"Keep offspeed down and bury breaking balls.")
                else:
                    lines.append(f"**フライ打者（{fb_pct:.0f}%）。** 高めの球は打ち上げる。"
                               f"変化球は低めに集め、ブレーキングボールを叩きつけろ")

    if not lines:
        if lang == "EN":
            return "Balanced hitter with no extreme vulnerabilities. Compete with best stuff and mix locations."
        else:
            return "極端な弱点のないバランス型打者。持ち球で勝負し、コースを散らせ。"

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
            swings = grp[grp["description"].isin({
                "hit_into_play", "foul", "swinging_strike",
                "swinging_strike_blocked", "foul_tip",
            })]
            whiffs = grp[grp["description"].isin({
                "swinging_strike", "swinging_strike_blocked", "foul_tip",
            })]
            ba = len(hits) / len(ab) if len(ab) >= 10 else None
            whiff_pct = len(whiffs) / len(swings) * 100 if len(swings) > 0 else 0

            label = PITCH_LABELS.get(pt, pt)
            pt_stats.append({
                "type": pt, "label": label, "count": len(grp), "usage": usage,
                "ba": ba, "whiff": whiff_pct,
            })

        if pt_stats:
            # Most hittable pitch (highest BA against)
            hittable = sorted([p for p in pt_stats if p["ba"] is not None], key=lambda x: x["ba"], reverse=True)
            # His best pitch (highest whiff%)
            best_pitch = sorted([p for p in pt_stats if p["whiff"] > 0], key=lambda x: x["whiff"], reverse=True)
            # Primary pitch (highest usage)
            primary = sorted(pt_stats, key=lambda x: x["usage"], reverse=True)

            if primary:
                pr = primary[0]
                if lang == "EN":
                    lines.append(f"**Primary pitch:** {pr['label']} ({pr['usage']:.0f}% usage). "
                               f"You will see this most — time it early in counts.")
                else:
                    lines.append(f"**主要球種:** {pr['label']}（使用率 {pr['usage']:.0f}%）。"
                               f"最も多く来る球 — 早いカウントで狙え")

            if hittable and hittable[0]["ba"] is not None and hittable[0]["ba"] >= 0.250:
                h = hittable[0]
                if lang == "EN":
                    lines.append(f"**Most hittable pitch:** {h['label']} (BA .{int(h['ba']*1000):03d}). "
                               f"Look for this pitch to drive.")
                else:
                    lines.append(f"**最も打ちやすい球種:** {h['label']}（被打率 .{int(h['ba']*1000):03d}）。"
                               f"この球を狙って長打を狙え")

            if best_pitch:
                bp = best_pitch[0]
                if lang == "EN":
                    lines.append(f"**Beware:** {bp['label']} is his best pitch (Whiff% {bp['whiff']:.1f}%). "
                               f"Lay off this pitch unless it's in the zone.")
                else:
                    lines.append(f"**要注意:** {bp['label']} が最も空振りを取る球（空振率 {bp['whiff']:.1f}%）。"
                               f"ゾーン外なら見逃せ")

    # 2. Zone vulnerability (where opponents hit him hardest)
    zone_valid = pdf.dropna(subset=["zone"]).copy()
    zone_valid["zone"] = zone_valid["zone"].astype(int)
    zone_names_en = {1: "up-in", 2: "up-middle", 3: "up-away", 4: "mid-in", 5: "heart", 6: "mid-away", 7: "down-in", 8: "down-middle", 9: "down-away"}
    zone_names_ja = {1: "高めイン", 2: "高め真ん中", 3: "高めアウト", 4: "真ん中イン", 5: "ど真ん中", 6: "真ん中アウト", 7: "低めイン", 8: "低め真ん中", 9: "低めアウト"}
    zone_names = zone_names_ja if lang == "JA" else zone_names_en

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
                lines.append(f"**Look for pitches here (high opp BA):** {hit_str}")
            else:
                lines.append(f"**狙うゾーン（被打率高い）:** {hit_str}")
        if tough_str:
            if lang == "EN":
                lines.append(f"**Tough zones (low opp BA):** {tough_str} — lay off or foul off")
            else:
                lines.append(f"**手を出しにくいゾーン（被打率低い）:** {tough_str} — 見逃すかファウルで粘れ")

    # 3. Count strategy
    count_valid = pdf.dropna(subset=["balls", "strikes"]).copy()
    count_valid["balls"] = count_valid["balls"].astype(int)
    count_valid["strikes"] = count_valid["strikes"].astype(int)

    # Pitcher ahead vs behind
    p_ahead = count_valid[count_valid["strikes"] > count_valid["balls"]]
    p_behind = count_valid[count_valid["balls"] > count_valid["strikes"]]

    if not p_ahead.empty and not p_behind.empty:
        pa_stats = pitching_stats(p_ahead) if len(p_ahead) >= 30 else None
        pb_stats = pitching_stats(p_behind) if len(p_behind) >= 30 else None

        if pa_stats and pb_stats:
            if pb_stats["Opp AVG"] >= 0.280:
                if lang == "EN":
                    lines.append(f"**When behind in count:** He gives up hits (Opp AVG .{int(pb_stats['Opp AVG']*1000):03d}). "
                               f"Be patient — work counts and make him come to you.")
                else:
                    lines.append(f"**投手不利カウントで:** 被打率が高い（.{int(pb_stats['Opp AVG']*1000):03d}）。"
                               f"粘ってカウントを有利に持ち込め")

            if pa_stats["K%"] >= 30:
                if lang == "EN":
                    lines.append(f"**When he's ahead:** High K rate ({pa_stats['K%']:.1f}%). "
                               f"Shorten up and protect the plate — don't give away ABs.")
                else:
                    lines.append(f"**投手有利カウントで:** 奪三振率が高い（{pa_stats['K%']:.1f}%）。"
                               f"コンパクトに振り、ゾーン内の球をカットして粘れ")

    # 4. First pitch tendency
    first_pitch = count_valid[(count_valid["balls"] == 0) & (count_valid["strikes"] == 0)]
    if len(first_pitch) >= 30:
        fp_types = first_pitch["pitch_type"].value_counts()
        if len(fp_types) > 0:
            top_fp = fp_types.index[0]
            top_fp_pct = fp_types.iloc[0] / len(first_pitch) * 100
            label = PITCH_LABELS.get(top_fp, top_fp)

            # Check first pitch strike rate
            fp_strikes = first_pitch[first_pitch["description"].isin({
                "called_strike", "swinging_strike", "swinging_strike_blocked",
                "foul", "foul_tip", "hit_into_play",
            })]
            fp_strike_pct = len(fp_strikes) / len(first_pitch) * 100

            if lang == "EN":
                lines.append(f"**First pitch:** {label} {top_fp_pct:.0f}% of the time. "
                           f"Strike rate: {fp_strike_pct:.0f}%. "
                           + ("Aggressive on first pitch can pay off." if fp_strike_pct >= 60 else "Patient approach recommended — he misses often."))
            else:
                lines.append(f"**初球:** {label} が {top_fp_pct:.0f}%。"
                           f"ストライク率: {fp_strike_pct:.0f}%。"
                           + ("初球から積極的に狙える。" if fp_strike_pct >= 60 else "初球は様子を見るのが得策 — ボールになることが多い。"))

    # 5. Platoon recommendation
    vs_l = pdf[pdf["stand"] == "L"]
    vs_r = pdf[pdf["stand"] == "R"]
    if not vs_l.empty and not vs_r.empty:
        sl = pitching_stats(vs_l)
        sr = pitching_stats(vs_r)
        if sl["PA"] >= 20 and sr["PA"] >= 20:
            if sl["Opp AVG"] > sr["Opp AVG"] + 0.030:
                if lang == "EN":
                    lines.append(f"**Platoon weakness:** Gives up more hits to LHB (Opp AVG .{int(sl['Opp AVG']*1000):03d}). "
                               f"Stack left-handed batters.")
                else:
                    lines.append(f"**左右差:** 左打者に打たれやすい（被打率 .{int(sl['Opp AVG']*1000):03d}）。"
                               f"左打者を並べたい")
            elif sr["Opp AVG"] > sl["Opp AVG"] + 0.030:
                if lang == "EN":
                    lines.append(f"**Platoon weakness:** Gives up more hits to RHB (Opp AVG .{int(sr['Opp AVG']*1000):03d}). "
                               f"Stack right-handed batters.")
                else:
                    lines.append(f"**左右差:** 右打者に打たれやすい（被打率 .{int(sr['Opp AVG']*1000):03d}）。"
                               f"右打者を並べたい")

    if not lines:
        if lang == "EN":
            return "Balanced pitcher with no extreme vulnerabilities. Compete at the plate and be ready to adjust."
        else:
            return "極端な弱点のないバランス型投手。打席で積極的に対応し、試合の中で調整せよ。"

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
    /* Mobile */
    @media (max-width: 768px) {
        [data-testid="stMetric"] { padding: 0.3rem 0.4rem; }
        [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
        [data-testid="stMetricValue"] { font-size: 1.1rem !important; }
        [data-testid="stHorizontalBlock"] { gap: 0.3rem !important; }
        .stDataFrame td, .stDataFrame th { font-size: 0.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

    # -- Sidebar --
    lang = st.sidebar.radio("Language / 言語", ["JA", "EN"], horizontal=True)
    t = TEXTS[lang]

    st.sidebar.markdown(f"# \U0001F1EF\U0001F1F5 vs \U0001F1FB\U0001F1EA")
    st.sidebar.caption(t["subtitle"])

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

    # -- Main content --
    st.title(t["main_title"])
    st.caption(t["subtitle"])
    st.caption(
        "All statistics: MLB Statcast 2024-2025 Regular Season"
        if lang == "EN" else
        "全成績データ: MLB Statcast 2024-2025レギュラーシーズン"
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        f"\U0001F3AF {t['tab1']}",
        f"\u2694\uFE0F {t['tab2']}",
        f"\U0001F3B1 {t['tab3']}",
        f"\U0001F525 {t['tab4']}",
    ])

    # ===================================================================
    # TAB 1: Matchup Overview
    # ===================================================================
    with tab1:
        st.header(t["predicted_lineup"])
        st.markdown(f"**{t['pool_d_record']}**")

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

        # Position abbreviation legend
        with st.expander(
            "Position abbreviations" if lang == "EN" else "守備ポジション略称の説明"
        ):
            pos_legend = POS_LABELS[lang]
            pos_order = ["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"]
            for abbr in pos_order:
                st.markdown(f"- **{abbr}** = {pos_legend[abbr]}")

        # Stats glossary for beginners
        with st.expander(
            "Stats glossary (what do AVG, OPS, etc. mean?)" if lang == "EN"
            else "成績用語の説明（AVG・OPS等の意味）"
        ):
            st.markdown(t["glossary_stats"])

        # --- Interactive player cards (click to expand) ---
        for p in PREDICTED_LINEUP:
            player_info = PLAYER_BY_NAME.get(p["name"])
            if not player_info:
                continue
            pdf_player = df_bat[df_bat["batter"] == player_info["mlbam_id"]]
            display_name = _name_display(p["name"], lang)
            pos_full = POS_LABELS[lang].get(p["pos"], p["pos"])
            expander_label = f"#{p['order']} {display_name} — {p['pos']} ({pos_full}) | {player_info.get('team', '')}"

            with st.expander(expander_label):
                if pdf_player.empty:
                    st.warning(t["no_data"])
                    continue

                stats = batting_stats(pdf_player)

                # Key metrics row
                mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
                mc1.metric("AVG", f"{stats['AVG']:.3f}")
                mc2.metric("OBP", f"{stats['OBP']:.3f}")
                mc3.metric("SLG", f"{stats['SLG']:.3f}")
                mc4.metric("OPS", f"{stats['OPS']:.3f}")
                mc5.metric("K%", f"{stats['K%']:.1f}%")
                mc6.metric("BB%", f"{stats['BB%']:.1f}%")

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
                        dx = np.cos(angle_ex - np.pi / 2) * 20
                        dy = np.sin(angle_ex - np.pi / 2) * 20
                        ax_ex.annotate(raw_ex, xy=(angle_ex, val_ex),
                                       xytext=(dx, dy),
                                       textcoords="offset points",
                                       fontsize=11, ha="center", va="center",
                                       color="white", fontweight="bold")
                    leg_ex = ax_ex.legend(loc="lower right", bbox_to_anchor=(1.25, -0.05),
                                           fontsize=10, facecolor="#0e1117", edgecolor="gray",
                                           framealpha=0.9)
                    for txt_ex in leg_ex.get_texts():
                        txt_ex.set_color("white")
                    fig_ex.tight_layout()
                    st.pyplot(fig_ex, use_container_width=True)
                    plt.close(fig_ex)
                    st.caption(t["radar_explain"])

                # 3x3 Zone heatmap
                with chart_right:
                    st.markdown(f"**{t['zone_3x3']}**")
                    fig_z3_ex, ax_z3_ex = _dark_fig(figsize=(4, 3.5))
                    im_z3_ex = draw_zone_3x3(pdf_player, "ba", t["ba_heatmap"], ax_z3_ex, lang=lang)
                    cb_z3_ex = fig_z3_ex.colorbar(im_z3_ex, ax=ax_z3_ex, fraction=0.046, pad=0.04)
                    cb_z3_ex.ax.tick_params(colors="white", labelsize=10)
                    fig_z3_ex.tight_layout()
                    st.pyplot(fig_z3_ex, use_container_width=True)
                    plt.close(fig_z3_ex)
                    st.caption(t["zone_explain"])

                # Row 2: Spray chart + Platoon splits (centered ~37.5% each)
                _sp3, chart2_left, chart2_right, _sp4 = st.columns([1, 3, 3, 1])

                with chart2_left:
                    st.markdown(f"**{t['spray_chart']}**")
                    fig_sp_ex, ax_sp_ex = plt.subplots(figsize=(4, 4), facecolor="#0e1117")
                    ax_sp_ex.set_facecolor("#0e1117")
                    draw_spray_chart(pdf_player, display_name, ax_sp_ex, stadium="marlins", density=True, lang=lang)
                    fig_sp_ex.tight_layout()
                    st.pyplot(fig_sp_ex, use_container_width=True)
                    plt.close(fig_sp_ex)
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
                        pm1.metric("AVG", f"{ss_ps['AVG']:.3f}")
                        pm2.metric("OPS", f"{ss_ps['OPS']:.3f}")
                        pm3.metric("K%", f"{ss_ps['K%']:.1f}%")
                    st.caption(t["platoon_explain"])

                st.caption(
                    "See Tab 2 for full details (5x5 zone, batted ball, count matrix, Whiff%)."
                    if lang == "EN" else
                    "\u8a73\u7d30\u306fTab 2\uff08\u30be\u30fc\u30f3\u30d2\u30fc\u30c8\u30de\u30c3\u30d7\u30fb\u6253\u7403\u30d7\u30ed\u30d5\u30a3\u30fc\u30eb\u30fb\u30ab\u30a6\u30f3\u30c8\u5225\u30fb\u7a7a\u632f\u7387\uff09\u3092\u53c2\u7167\u3002"
                )

        st.divider()

        # Predicted SP card
        st.subheader(t["predicted_sp"])
        sp_info = PITCHER_BY_NAME.get(PREDICTED_SP, {})
        sp_cols = st.columns(4)
        sp_cols[0].metric(t["player"], _name_display(PREDICTED_SP, lang))
        sp_cols[1].metric(t["team"], sp_info.get("team", "—"))
        sp_cols[2].metric(t["throws"], sp_info.get("throws", "—"))
        sp_cols[3].metric(t["role"], t["sp_label"])

        # SP MLB stats from Statcast
        sp_data = df_pit[df_pit["pitcher"] == sp_info.get("mlbam_id", -1)]
        if not sp_data.empty:
            sp_stats = pitching_stats(sp_data)
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric(t["opp_avg"], f"{sp_stats['Opp AVG']:.3f}")
            sc2.metric(t["k_pct"], f"{sp_stats['K%']:.1f}%")
            sc3.metric(t["bb_pct"], f"{sp_stats['BB%']:.1f}%")
            sc4.metric(t["whiff_pct"], f"{sp_stats['Whiff%']:.1f}%")
            if sp_stats["Avg Velo"]:
                velo_label = "平均球速" if lang == "JA" else "Avg Velo"
                st.caption(f"{velo_label}: {sp_stats['Avg Velo']:.1f} mph ({sp_stats['Avg Velo'] * 1.609:.0f} km/h)")

        st.divider()

        # Key tendencies
        st.subheader(t["key_tendencies"])
        st.info(t["tendency_text"])

        st.divider()

        # ===== GAME PLAN =====
        st.header(t["game_plan"])

        # Team weakness analysis (auto-generated from data)
        st.subheader(t["team_weaknesses_title"])
        weakness_points = []
        high_k_batters = []
        platoon_weak_batters = []
        low_bb_batters = []

        for p in PREDICTED_LINEUP:
            player_info = PLAYER_BY_NAME.get(p["name"])
            if not player_info:
                continue
            pdf_gp = df_bat[df_bat["batter"] == player_info["mlbam_id"]]
            if pdf_gp.empty:
                continue
            s_gp = batting_stats(pdf_gp)
            display = _name_display(p["name"], lang)

            if s_gp["K%"] >= 22.0:
                high_k_batters.append(f"{display} ({s_gp['K%']:.1f}%)")
            if s_gp["BB%"] < 7.0:
                low_bb_batters.append(f"{display} ({s_gp['BB%']:.1f}%)")

            # Check platoon split
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

        if high_k_batters:
            if lang == "EN":
                st.markdown(f"**High K% batters (target with strikeout pitching):** {', '.join(high_k_batters)}")
            else:
                st.markdown(f"**\u4e09\u632f\u7387\u306e\u9ad8\u3044\u6253\u8005\uff08\u4e09\u632f\u3092\u72d9\u3048\u308b\uff09:** {', '.join(high_k_batters)}")

        if low_bb_batters:
            if lang == "EN":
                st.markdown(f"**Aggressive batters (low BB%, expand the zone):** {', '.join(low_bb_batters)}")
            else:
                st.markdown(f"**\u7a4d\u6975\u7684\u306a\u6253\u8005\uff08\u56db\u7403\u7387\u304c\u4f4e\u3044\uff1d\u30be\u30fc\u30f3\u5916\u3092\u632f\u308a\u3084\u3059\u3044\uff09:** {', '.join(low_bb_batters)}")

        if platoon_weak_batters:
            if lang == "EN":
                st.markdown(f"**Platoon vulnerabilities (exploit with matchups):** {', '.join(platoon_weak_batters)}")
            else:
                st.markdown(f"**\u5de6\u53f3\u5dee\u304c\u5927\u304d\u3044\u6253\u8005\uff08\u30de\u30c3\u30c1\u30a2\u30c3\u30d7\u3067\u653b\u3081\u308b\uff09:** {', '.join(platoon_weak_batters)}")

        # Batting strategy
        st.subheader(t["game_plan_batting"])
        if lang == "EN":
            st.success(
                "**vs Ranger Su\u00e1rez (LHP starter):**\n"
                "- Be patient early \u2014 he is a pitch-to-contact pitcher (low K%). "
                "Force him to throw strikes and wait for the pitch to drive.\n"
                "- Against RHB: the changeup down and away generates whiffs but hangs when elevated. Lay off the low change, punish mistakes up.\n"
                "- Against LHB: his sinker runs arm-side. Look for pitches over the inner half.\n\n"
                "**vs Bullpen:**\n"
                "- Jos\u00e9 Butt\u00f3 is their high-leverage reliever. If he enters in a tight spot, "
                "be patient \u2014 look for hangers when he falls behind in count.\n"
                "- Bazardo is a multi-inning bridge \u2014 be aggressive early in his outings before he settles."
            )
        else:
            st.success(
                "**vs \u30ec\u30f3\u30b8\u30e3\u30fc\u30fb\u30b9\u30a2\u30ec\u30b9\uff08\u5de6\u8155\u5148\u767a\uff09:**\n"
                "- \u65e9\u3044\u30ab\u30a6\u30f3\u30c8\u3067\u7121\u7406\u306b\u4ed5\u639b\u3051\u306a\u3044\u3002\u596a\u4e09\u632f\u7387\u304c\u4f4e\u3044\u6295\u624b\u306a\u306e\u3067\u3001\u7518\u3044\u7403\u3092\u5f85\u3064\u3002\n"
                "- \u53f3\u6253\u8005: \u5916\u89d2\u4f4e\u3081\u306e\u30c1\u30a7\u30f3\u30b8\u30a2\u30c3\u30d7\u306f\u7a7a\u632f\u308a\u3092\u53d6\u308c\u308b\u304c\u3001\u9ad8\u3081\u306b\u6d6e\u304f\u3068\u6253\u3066\u308b\u3002\u4f4e\u3081\u306f\u898b\u9003\u3057\u3001\u9ad8\u3081\u3092\u72d9\u3046\u3002\n"
                "- \u5de6\u6253\u8005: \u30b7\u30f3\u30ab\u30fc\u304c\u30a2\u30fc\u30e0\u5074\u306b\u9003\u3052\u308b\u3002\u30a4\u30f3\u30b3\u30fc\u30b9\u306e\u7403\u306b\u72d9\u3044\u3092\u7d5e\u308b\u3002\n\n"
                "**vs \u30d6\u30eb\u30da\u30f3:**\n"
                "- \u30db\u30bb\u30fb\u30d6\u30c3\u30c8\u306f\u30cf\u30a4\u30ec\u30d0\u30ec\u30c3\u30b8\u306e\u5207\u308a\u672d\u3002"
                "\u767b\u677f\u6642\u306f\u30ab\u30a6\u30f3\u30c8\u4e0d\u5229\u3067\u7518\u304f\u306a\u308b\u7403\u3092\u898b\u9003\u3055\u306a\u3044\u3002\n"
                "- \u30d0\u30b5\u30eb\u30c9\u306f\u30a4\u30cb\u30f3\u30b0\u8de8\u304e\u306e\u4e2d\u7d99\u304e\u3002\u767b\u677f\u5e8f\u76e4\u306b\u7a4d\u6975\u7684\u306b\u4ed5\u639b\u3051\u308b\u3002"
            )

        # Pitching strategy
        st.subheader(t["game_plan_pitching"])
        if lang == "EN":
            st.success(
                "**Top of Order (1-4):**\n"
                "- Acu\u00f1a Jr.: Elite talent. Don't let him beat you \u2014 pitch carefully, "
                "use offspeed away. If he's struggling, still don't give in.\n"
                "- Arr\u00e1ez: Best contact hitter in MLB. Do NOT give him anything in the zone "
                "early in counts. Live with walks if necessary.\n"
                "- Contreras (W.): Power threat. Attack with elevated fastballs and breaking balls down.\n\n"
                "**Middle/Bottom (5-9):**\n"
                "- Torres, Tovar: Can expand the zone \u2014 use slider/sweeper glove-side.\n"
                "- S. Perez: Aggressive swinger, low BB%. Throw strikes early, expand late.\n"
                "- Abreu: Solid but not elite \u2014 compete in the zone with good stuff."
            )
        else:
            st.success(
                "**\u4e0a\u4f4d\u6253\u7dda (1\u301c4\u756a):**\n"
                "- \u30a2\u30af\u30fc\u30cb\u30e3Jr.: \u30a8\u30ea\u30fc\u30c8\u3002\u30b9\u30c8\u30ec\u30fc\u30c8\u52dd\u8ca0\u3092\u907f\u3051\u3001\u5909\u5316\u7403\u3067\u5916\u3059\u3002\u6253\u305f\u308c\u3066\u3082\u5358\u6253\u306b\u6291\u3048\u308b\u3002\n"
                "- \u30a2\u30e9\u30a8\u30b9: MLB\u6700\u9ad8\u306e\u30b3\u30f3\u30bf\u30af\u30c8\u30d2\u30c3\u30bf\u30fc\u3002\u5e8f\u76e4\u306b\u30be\u30fc\u30f3\u5185\u3092\u6295\u3052\u306a\u3044\u3002"
                "\u56db\u7403\u3092\u6050\u308c\u305a\u3001\u6253\u305f\u305b\u3066\u53d6\u308b\u7403\u3092\u5fb9\u5e95\u3002\n"
                "- W.\u30b3\u30f3\u30c8\u30ec\u30e9\u30b9: \u30d1\u30ef\u30fc\u30d2\u30c3\u30bf\u30fc\u3002\u9ad8\u3081\u306e\u901f\u7403\u3068\u4f4e\u3081\u306e\u5909\u5316\u7403\u3067\u653b\u3081\u308b\u3002\n\n"
                "**\u4e2d\u8ef8\u301c\u4e0b\u4f4d (5\u301c9\u756a):**\n"
                "- \u30c8\u30fc\u30ec\u30b9\u3001\u30c8\u30d0\u30fc: \u30be\u30fc\u30f3\u5916\u3092\u632f\u308b\u50be\u5411\u3002\u30b9\u30e9\u30a4\u30c0\u30fc\u30fb\u30b9\u30a6\u30a3\u30fc\u30d1\u30fc\u3067\u30b0\u30e9\u30d6\u5074\u306b\u653b\u3081\u308b\u3002\n"
                "- S.\u30da\u30ec\u30b9: \u7a4d\u6975\u7684\u6253\u8005\uff08\u56db\u7403\u7387\u4f4e\u3044\uff09\u3002\u5e8f\u76e4\u30b9\u30c8\u30e9\u30a4\u30af\u5148\u884c\u3001\u8ffd\u3044\u8fbc\u3093\u3067\u304b\u3089\u5916\u3059\u3002\n"
                "- \u30a2\u30d6\u30ec\u30a6: \u5b89\u5b9a\u578b\u3060\u304c\u30a8\u30ea\u30fc\u30c8\u3067\u306f\u306a\u3044\u3002\u7403\u5a01\u3067\u52dd\u8ca0\u3057\u3066\u69cb\u308f\u306a\u3044\u3002"
            )

    # ===================================================================
    # TAB 2: Venezuela Lineup Scouting
    # ===================================================================
    with tab2:
        season_label = f"{season} MLB Season (Statcast)" if lang == "EN" else f"{season}年 MLBシーズン（Statcast）"
        st.header(f"\u2694\uFE0F {t['tab2']} — {season_label}")

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
            st.subheader(t["team_radar_title"])
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
                    dx = np.cos(angle - np.pi / 2) * 20
                    dy = np.sin(angle - np.pi / 2) * 20
                    ax_radar.annotate(raw, xy=(angle, val),
                                      xytext=(dx, dy), textcoords="offset points",
                                      fontsize=12, ha="center", va="center",
                                      color="white", fontweight="bold")
                leg = ax_radar.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1),
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
        st.subheader("🇻🇪 " + ("打者一覧（全ロースター）" if lang == "JA" else "All Batters (Full Roster)"))

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
                                 ).background_gradient(subset=["OPS"], cmap="RdYlGn", vmin=0.500, vmax=0.900),
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

        st.markdown("---")
        st.subheader(f"{order_label} {display_name} — {pos_str} ({pos_full_t2})")

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
            c4.metric("AVG", f"{stats['AVG']:.3f}", delta=f"{stats['AVG'] - 0.243:+.3f}")
            c5.metric("OBP", f"{stats['OBP']:.3f}", delta=f"{stats['OBP'] - 0.312:+.3f}")
            c6.metric("SLG", f"{stats['SLG']:.3f}", delta=f"{stats['SLG'] - 0.397:+.3f}")
            c7.metric("OPS", f"{stats['OPS']:.3f}", delta=f"{stats['OPS'] - 0.709:+.3f}")
            xwoba_vals = pdf[pdf["estimated_woba_using_speedangle"].notna()]["estimated_woba_using_speedangle"]
            xwoba = xwoba_vals.mean() if len(xwoba_vals) > 0 else 0
            c8.metric("xwOBA", f"{xwoba:.3f}", delta=f"{xwoba - 0.311:+.3f}")

            kc1, kc2 = st.columns(2)
            kc1.metric("K%", f"{stats['K%']:.1f}%")
            kc2.metric("BB%", f"{stats['BB%']:.1f}%")

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

            # === Defensive Positioning ===
            st.markdown(f"### {t['defensive_positioning']}")
            st.caption(t["defensive_explain"])
            def_pos = generate_defensive_positioning(pdf, player_info, lang)
            st.warning(def_pos)

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
                    dx = np.cos(angle - np.pi / 2) * 20
                    dy = np.sin(angle - np.pi / 2) * 20
                    ax_pr.annotate(raw, xy=(angle, val), xytext=(dx, dy), textcoords="offset points",
                                   fontsize=12, ha="center", va="center", color="white", fontweight="bold")
                leg_pr = ax_pr.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1),
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
                    fig_z3.tight_layout()
                    st.pyplot(fig_z3, use_container_width=True)
                    plt.close(fig_z3)

            # --- 5x5 Zone heatmaps ---
            st.markdown(f"**{t['zone_5x5']}**")
            for hm_metric, hm_title, hm_caption in [
                ("ba", t["ba_heatmap"], t["danger_zone"]),
                ("xwoba", t["xwoba_heatmap"], t.get("danger_zone_xwoba", t["danger_zone"])),
            ]:
                st.caption(hm_caption)
                _sl_hm, _cc_hm, _sr_hm = st.columns([1, 4, 1])
                with _cc_hm:
                    fig_hm, ax_hm = _dark_fig(figsize=(6, 5))
                    im_hm = draw_zone_heatmap(pdf, hm_metric, hm_title, ax_hm, lang=lang)
                    cb_hm = fig_hm.colorbar(im_hm, ax=ax_hm, fraction=0.046, pad=0.04)
                    cb_hm.ax.tick_params(colors="white")
                    fig_hm.tight_layout()
                    st.pyplot(fig_hm, use_container_width=True)
                    plt.close(fig_hm)

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

            # --- Batted Ball Profile ---
            st.markdown(f"**{t['batted_ball']}**")
            with st.expander("What do these mean?" if lang == "EN" else "用語の説明を見る"):
                st.markdown(t["glossary_batted"])
            profile = batted_ball_profile(pdf, t)
            if profile:
                bb_cols = st.columns(4)
                bb_items = list(profile.items())
                for idx, (k, v) in enumerate(bb_items):
                    bb_cols[idx % 4].metric(k, v)
            else:
                st.write(t["no_data"])

            # --- Pitch type performance table ---
            st.markdown(f"**{t['pitch_type_perf']}**")
            with st.expander(t["glossary_pitch"] if lang == "EN" else "空振率・チェイス率とは？"):
                st.markdown(t["glossary_pitch"])
            pt_tbl = pitch_type_table(pdf, t)
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
                    ax_pt.set_title(t["whiff_pct"], color="white", fontsize=16, fontweight="bold")
                    x_max = chart_data["whiff_val"].max()
                    ax_pt.set_xlim(0, x_max * 1.25 if x_max > 0 else 10)
                    for spine in ax_pt.spines.values():
                        spine.set_color("white")
                    fig_pt.tight_layout()
                    st.pyplot(fig_pt, use_container_width=True)
                    plt.close(fig_pt)

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
                    m1.metric("AVG", f"{ss['AVG']:.3f}")
                    m2.metric("OBP", f"{ss['OBP']:.3f}")
                    m3.metric("SLG", f"{ss['SLG']:.3f}")
                    m4.metric("OPS", f"{ss['OPS']:.3f}")

                    fig_z_pl, ax_z_pl = _dark_fig(figsize=(5, 4))
                    draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_z_pl, lang=lang)
                    fig_z_pl.tight_layout()
                    st.pyplot(fig_z_pl, use_container_width=True)
                    plt.close(fig_z_pl)

            # --- Count-by-count performance ---
            st.markdown(f"**{t['count_perf']}**")
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
                    ("Count" if lang == "EN" else "カウント"): f"{b}-{s}",
                    ("Type" if lang == "EN" else "分類"): tag,
                    "PA": cs["PA"], "AVG": cs["AVG"], "OBP": cs["OBP"],
                    "SLG": cs["SLG"], "OPS": cs["OPS"], "K%": cs["K%"], "BB%": cs["BB%"],
                })

            if count_rows:
                count_table = pd.DataFrame(count_rows)
                st.dataframe(
                    count_table.style.format({
                        "AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}",
                        "OPS": "{:.3f}", "K%": "{:.1f}", "BB%": "{:.1f}",
                    }).background_gradient(subset=["OPS"], cmap="RdYlGn"),
                    use_container_width=True, hide_index=True,
                )

    # ===================================================================
    # TAB 3: Ranger Suarez Analysis
    # ===================================================================
    with tab3:
        season_label = f"{season} MLB Season (Statcast)" if lang == "EN" else f"{season}年 MLBシーズン（Statcast）"
        st.header(f"\U0001F3B1 {t['tab3']} — {season_label}")

        sp_info = PITCHER_BY_NAME.get(PREDICTED_SP, {})
        sp_data = df_pit[df_pit["pitcher"] == sp_info.get("mlbam_id", -1)]

        # Profile card
        st.subheader(_name_display(PREDICTED_SP, lang))
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.metric(t["team"], sp_info.get("team", "—"))
        pc2.metric(t["throws"], sp_info.get("throws", "—"))
        pc3.metric(t["role"], t["sp_label"])
        pc4.metric("MLB ID" if lang == "EN" else "選手ID", sp_info.get("mlbam_id", "—"))

        if sp_data.empty:
            st.warning(t["no_data"])
        else:
            sp_stats = pitching_stats(sp_data)

            # Key metrics with MLB comparison
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric(t["opp_avg"], f"{sp_stats['Opp AVG']:.3f}",
                       delta=f"{sp_stats['Opp AVG'] - _MLB_AVG_PIT['Opp AVG']:+.3f} vs MLB avg",
                       delta_color="inverse")
            sc2.metric(t["k_pct"], f"{sp_stats['K%']:.1f}%",
                       delta=f"{sp_stats['K%'] - _MLB_AVG_PIT['K%']:+.1f}% vs MLB avg")
            sc3.metric(t["bb_pct"], f"{sp_stats['BB%']:.1f}%",
                       delta=f"{sp_stats['BB%'] - _MLB_AVG_PIT['BB%']:+.1f}% vs MLB avg",
                       delta_color="inverse")
            sc4, sc5 = st.columns(2)
            sc4.metric(t["whiff_pct"], f"{sp_stats['Whiff%']:.1f}%")
            if sp_stats["xwOBA"]:
                sc5.metric(t["xwoba"], f"{sp_stats['xwOBA']:.3f}",
                           delta=f"{sp_stats['xwOBA'] - _MLB_AVG_PIT['xwOBA']:+.3f} vs MLB avg",
                           delta_color="inverse")

            # Scouting summary
            st.subheader(t["scouting_summary"])
            sp_summary = generate_pitcher_summary(sp_stats, sp_data, sp_info, lang)
            st.info(sp_summary)

            # === Hitting Plan (How to hit this pitcher) ===
            st.markdown(f"### {t['hitting_plan_title']}")
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

            st.divider()

            # Arsenal table
            st.subheader(t["arsenal"])
            at = arsenal_table(sp_data, t)
            if not at.empty:
                st.dataframe(at, use_container_width=True, hide_index=True)
            with st.expander("Stats glossary" if lang == "EN" else "指標の説明"):
                st.markdown(t["arsenal_explain"])

            st.divider()

            # Movement chart
            st.subheader(t["movement_chart"])
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

            st.divider()

            # Zone heatmap (pitcher location — usage + opp BA)
            st.subheader(t["zone_heatmap_pitch"])
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
            st.subheader(t["platoon"])
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
                    m1.metric(t["opp_avg"], f"{ss['Opp AVG']:.3f}")
                    m2.metric(t["opp_slg"], f"{ss['Opp SLG']:.3f}")
                    m3.metric(t["k_pct"], f"{ss['K%']:.1f}%")
                    m4.metric(t["bb_pct"], f"{ss['BB%']:.1f}%")

                    # Zone heatmap per platoon side
                    fig_z, ax_z = _dark_fig(figsize=(5, 4))
                    draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_z, lang=lang)
                    fig_z.tight_layout()
                    st.pyplot(fig_z, use_container_width=True)
                    plt.close(fig_z)

            st.divider()

            # Pitch Selection by Count
            st.subheader(t["pitch_selection_by_count"])
            st.caption(t["pitch_selection_explain"])
            ps_table = pitch_selection_by_count(sp_data, t, lang)
            if not ps_table.empty:
                st.dataframe(ps_table, use_container_width=True, hide_index=True)

            # Count-by-count pitcher performance
            st.markdown(f"**{t['count_perf']}**")
            st.caption(t["count_explain"])

            pit_count_df = sp_data.dropna(subset=["balls", "strikes"]).copy()
            pit_count_df["balls"] = pit_count_df["balls"].astype(int)
            pit_count_df["strikes"] = pit_count_df["strikes"].astype(int)

            all_counts_pit = [
                (0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
                (2, 1), (1, 2), (3, 0), (2, 2), (3, 1), (3, 2),
            ]

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
                st.dataframe(
                    pit_count_table.style.format({
                        t["opp_avg"]: "{:.3f}",
                        t["k_pct"]: "{:.1f}",
                        t["bb_pct"]: "{:.1f}",
                        t["whiff_pct"]: "{:.1f}",
                    }).background_gradient(subset=[t["opp_avg"]], cmap="RdYlGn_r"),
                    use_container_width=True,
                    hide_index=True,
                )

            st.divider()

            # Where to attack
            st.subheader(t["where_to_attack"])
            st.success(t["attack_text_suarez"])

    # ===================================================================
    # TAB 4: Bullpen Scouting
    # ===================================================================
    with tab4:
        season_label = f"{season} MLB Season (Statcast)" if lang == "EN" else f"{season}年 MLBシーズン（Statcast）"
        st.header(f"\U0001F525 {t['tab4']} — {season_label}")

        # Bullpen usage overview
        st.subheader(t["bullpen_overview"])
        st.info(t["bullpen_text"])

        # Stats glossary (once, before reliever profiles)
        with st.expander("Stats glossary" if lang == "EN" else "指標の説明"):
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

        st.subheader("🇻🇪 " + ("投手一覧（先発除く）" if lang == "JA" else "All Pitchers (excl. Starter)"))
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
                                      t["bb_pct"]: "{:.1f}", t["whiff_pct"]: "{:.1f}"}),
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

        st.markdown("---")
        st.subheader(f"{t['reliever_profile']}: {_name_display(reliever_name, lang)}")

        rpc1, rpc2, rpc3 = st.columns(3)
        rpc1.metric(t["team"], pitcher_info.get("team", "—"))
        rpc2.metric(t["throws"], pitcher_info.get("throws", "—"))
        rpc3.metric(t["role"], pitcher_info.get("role", "RP"))

        if rp_data.empty:
            st.warning(t["no_data"])
        else:
            rp_stats = pitching_stats(rp_data)

            rm1, rm2, rm3, rm4 = st.columns(4)
            rm1.metric(t["opp_avg"], f"{rp_stats['Opp AVG']:.3f}")
            rm2.metric(t["k_pct"], f"{rp_stats['K%']:.1f}%")
            rm3.metric(t["bb_pct"], f"{rp_stats['BB%']:.1f}%")
            rm4.metric(t["whiff_pct"], f"{rp_stats['Whiff%']:.1f}%")
            if rp_stats["Avg Velo"]:
                velo_label = "平均球速" if lang == "JA" else "Avg Velo"
                st.caption(f"{velo_label}: {rp_stats['Avg Velo']:.1f} mph ({rp_stats['Avg Velo'] * 1.609:.0f} km/h)")

            rp_summary = generate_pitcher_summary(rp_stats, rp_data, pitcher_info, lang)
            st.info(rp_summary)

            # === Hitting Plan ===
            st.markdown(f"### {t['hitting_plan_title']}")
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

            # Arsenal
            rp_arsenal = arsenal_table(rp_data, t)
            if not rp_arsenal.empty:
                st.markdown(f"**{t['arsenal']}**")
                st.caption(t["arsenal_explain"])
                st.dataframe(rp_arsenal, use_container_width=True, hide_index=True)

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

            # Zone heatmaps
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

            # Pitch Selection by Count
            st.markdown(f"**{t['pitch_selection_by_count']}**")
            st.caption(t["pitch_selection_explain"])
            rp_ps_table = pitch_selection_by_count(rp_data, t, lang)
            if not rp_ps_table.empty:
                st.dataframe(rp_ps_table, use_container_width=True, hide_index=True)

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
                    sm1.metric(t["opp_avg"], f"{ss['Opp AVG']:.3f}")
                    sm2.metric(t["opp_slg"], f"{ss['Opp SLG']:.3f}")
                    sm3.metric(t["k_pct"], f"{ss['K%']:.1f}%")
                    sm4.metric(t["bb_pct"], f"{ss['BB%']:.1f}%")

                    fig_rp_z, ax_rp_z = _dark_fig(figsize=(5, 4))
                    draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_rp_z, lang=lang)
                    fig_rp_z.tight_layout()
                    st.pyplot(fig_rp_z, use_container_width=True)
                    plt.close(fig_rp_z)


if __name__ == "__main__":
    main()
