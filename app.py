"""WBC 2026 Venezuela Scouting Dashboard."""

import pathlib

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib_fontja  # noqa: F401 — enables Japanese font
import numpy as np
import pandas as pd
import streamlit as st

from players import VENEZUELA_BATTERS, PLAYER_BY_NAME

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
TEXTS = {
    "EN": {
        "title": "Venezuela Scouting Report",
        "subtitle": "WBC 2026 — Quarterfinal Opponent Analysis",
        "select_player": "Select Player",
        "team_overview": "Team Overview",
        "season": "Season",
        "all_seasons": "All",
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
        "avg_ev": "Avg EV",
        "avg_la": "Avg LA",
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
        "ahead": "Hitter Ahead",
        "behind": "Hitter Behind",
        "even": "Even",
        "team_strengths": "Team Strengths & Weaknesses",
        "strength_note": (
            "Venezuela's lineup features elite contact ability (Arráez), "
            "power threats (Acuña, S. Perez, Suárez), and speed (Acuña, Chourio, Garcia). "
            "Key vulnerabilities: several free-swinging hitters with elevated K-rates "
            "and exploitable platoon splits."
        ),
        "no_data": "No data available for this selection.",
        "danger_zone": "Red = danger zone (high BA), Blue = attack zone (low BA)",
    },
    "JA": {
        "title": "ベネズエラ スカウティングレポート",
        "subtitle": "WBC 2026 — 準々決勝 対戦相手分析",
        "select_player": "選手を選択",
        "team_overview": "チーム概要",
        "season": "シーズン",
        "all_seasons": "全シーズン",
        "profile": "選手プロフィール",
        "pos": "ポジション",
        "team": "チーム",
        "bats": "打席",
        "zone_heatmap": "ストライクゾーン ヒートマップ",
        "ba_heatmap": "ゾーン別 打率",
        "xwoba_heatmap": "ゾーン別 xwOBA",
        "spray_chart": "スプレーチャート",
        "batted_ball": "打球傾向",
        "pull_pct": "プル%",
        "cent_pct": "センター%",
        "oppo_pct": "逆方向%",
        "gb_pct": "ゴロ%",
        "ld_pct": "ライナー%",
        "fb_pct": "フライ%",
        "avg_ev": "平均打球速度",
        "avg_la": "平均打球角度",
        "pitch_type_perf": "球種別パフォーマンス",
        "pitch_type": "球種",
        "count": "球数",
        "ba": "打率",
        "slg": "長打率",
        "whiff_pct": "空振率",
        "chase_pct": "チェイス率",
        "platoon": "左右別スプリット",
        "vs_lhp": "vs 左投手",
        "vs_rhp": "vs 右投手",
        "count_perf": "カウント別パフォーマンス",
        "ahead": "有利カウント",
        "behind": "不利カウント",
        "even": "イーブン",
        "team_strengths": "チームの強み・弱み",
        "strength_note": (
            "ベネズエラ打線はアラエスの卓越したコンタクト力、アクーニャ・S.ペレス・スアレスの長打力、"
            "アクーニャ・チョリオ・ガルシアの走力が特徴。"
            "弱点: 数名の積極的な打者はK%が高く、プラトーンスプリットを突ける可能性がある。"
        ),
        "no_data": "このフィルターではデータがありません。",
        "danger_zone": "赤 = 危険ゾーン（高打率）、青 = 攻めるゾーン（低打率）",
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
# Data loading
# ---------------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent / "data" / "venezuela_statcast.csv"


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


# ---------------------------------------------------------------------------
# Visualisation helpers
# ---------------------------------------------------------------------------
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

    cmap = plt.cm.RdYlBu_r
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
                txt = f".{int(val * 1000):03d}" if metric == "ba" else f".{int(val * 1000):03d}"
                ax.text(
                    (x_bins[j] + x_bins[j + 1]) / 2,
                    (z_bins[i] + z_bins[i + 1]) / 2,
                    txt, ha="center", va="center",
                    fontsize=9, fontweight="bold", color="white",
                )

    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(0.5, 4.5)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("plate_x (ft)")
    ax.set_ylabel("plate_z (ft)")
    return im


def draw_spray_chart(df: pd.DataFrame, title: str, ax):
    """Draw spray chart on a baseball field outline."""
    # field outline
    theta = np.linspace(-np.pi / 4, np.pi / 4, 100)
    fence_r = 250
    ax.plot(fence_r * np.sin(theta) + 125.42,
            198.27 - fence_r * np.cos(theta),
            color="white", linewidth=1.5)

    # foul lines
    ax.plot([125.42, 125.42 + fence_r * np.sin(-np.pi / 4)],
            [198.27, 198.27 - fence_r * np.cos(-np.pi / 4)],
            color="white", linewidth=1, linestyle="--")
    ax.plot([125.42, 125.42 + fence_r * np.sin(np.pi / 4)],
            [198.27, 198.27 - fence_r * np.cos(np.pi / 4)],
            color="white", linewidth=1, linestyle="--")

    # diamond
    bases = np.array([[125.42, 198.27], [155, 168], [125.42, 138], [96, 168], [125.42, 198.27]])
    ax.plot(bases[:, 0], bases[:, 1], color="white", linewidth=1)

    valid = df.dropna(subset=["hc_x", "hc_y", "events"]).copy()
    color_map = {
        "home_run": "#e53935",
        "triple": "#ff9800",
        "double": "#ff9800",
        "single": "#4caf50",
    }
    valid["color"] = valid["events"].map(color_map).fillna("#888888")
    valid["zorder"] = valid["events"].apply(lambda x: 5 if x == "home_run" else (4 if x in ("double", "triple") else 3))

    for _, row in valid.iterrows():
        ax.scatter(
            row["hc_x"], row["hc_y"],
            c=row["color"], s=18, alpha=0.7,
            edgecolors="none", zorder=row["zorder"],
        )

    ax.set_xlim(0, 250)
    ax.set_ylim(220, -20)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.axis("off")

    # legend
    for label, color in [("HR", "#e53935"), ("XBH", "#ff9800"), ("1B", "#4caf50"), ("Out", "#888888")]:
        ax.scatter([], [], c=color, s=30, label=label)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.6)


def pitch_type_table(df: pd.DataFrame, t) -> pd.DataFrame:
    """Build pitch-type performance table."""
    valid = df.dropna(subset=["pitch_type"]).copy()
    # Lump rare pitch types
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

        # chase = swings outside zone
        outside = grp[(grp["zone"].notna()) & (grp["zone"] >= 11)]
        chase_swings = outside[outside["description"].isin({
            "hit_into_play", "foul", "swinging_strike",
            "swinging_strike_blocked", "foul_tip",
        })]
        chase_pct = len(chase_swings) / len(outside) * 100 if len(outside) > 0 else 0

        # batting stats on BIP
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


# ---------------------------------------------------------------------------
# Streamlit App
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Venezuela Scouting — WBC 2026",
        page_icon="🇻🇪",
        layout="wide",
    )

    # Sidebar
    lang = st.sidebar.radio("Language / 言語", ["EN", "JA"], horizontal=True)
    t = TEXTS[lang]

    st.sidebar.markdown(f"# 🇻🇪 {t['title']}")
    st.sidebar.caption(t["subtitle"])

    player_names = [t["team_overview"]] + [p["name"] for p in VENEZUELA_BATTERS]
    selected = st.sidebar.selectbox(t["select_player"], player_names)

    df_all = load_data()

    seasons = ["All"] + sorted(df_all["season"].unique().tolist())
    season = st.sidebar.selectbox(t["season"], seasons, format_func=lambda x: t["all_seasons"] if x == "All" else str(x))
    df_all = filter_season(df_all, season)

    # -----------------------------------------------------------------------
    # Team Overview
    # -----------------------------------------------------------------------
    if selected == t["team_overview"]:
        st.header(f"🇻🇪 {t['team_overview']}")

        rows = []
        for p in VENEZUELA_BATTERS:
            pdf = df_all[df_all["batter"] == p["mlbam_id"]]
            if pdf.empty:
                continue
            s = batting_stats(pdf)
            rows.append({
                "Player": p["name"],
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

        if rows:
            overview = pd.DataFrame(rows)
            st.dataframe(
                overview.style.format({
                    "AVG": "{:.3f}", "OBP": "{:.3f}", "SLG": "{:.3f}",
                    "OPS": "{:.3f}", "K%": "{:.1f}", "BB%": "{:.1f}",
                    "xwOBA": "{:.3f}",
                }).background_gradient(subset=["OPS"], cmap="RdYlGn")
                .background_gradient(subset=["K%"], cmap="RdYlGn_r"),
                use_container_width=True,
                hide_index=True,
            )

            st.subheader(t["team_strengths"])
            st.info(t["strength_note"])
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

    # Row 1: Profile Card
    st.header(f"🇻🇪 {player['name']}")
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
    c1.metric(t["pos"], player["pos"])
    c2.metric(t["team"], player["team"])
    c3.metric(t["bats"], player["bats"])
    c4.metric("AVG", f"{stats['AVG']:.3f}")
    c5.metric("OBP", f"{stats['OBP']:.3f}")
    c6.metric("SLG", f"{stats['SLG']:.3f}")
    c7.metric("OPS", f"{stats['OPS']:.3f}")
    c8.metric("xwOBA", f"{stats['xwOBA']:.3f}" if stats["xwOBA"] else "—")

    st.divider()

    # Row 2: Zone Heatmaps
    st.subheader(t["zone_heatmap"])
    st.caption(t["danger_zone"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor="#0e1117")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0e1117")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
    draw_zone_heatmap(pdf, "ba", t["ba_heatmap"], ax1)
    im = draw_zone_heatmap(pdf, "xwoba", t["xwoba_heatmap"], ax2)
    fig.colorbar(im, ax=[ax1, ax2], shrink=0.7, pad=0.02)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.divider()

    # Row 3: Spray Chart + Batted Ball
    col_spray, col_bb = st.columns([3, 2])

    with col_spray:
        st.subheader(t["spray_chart"])
        fig_sp, ax_sp = plt.subplots(figsize=(6, 6), facecolor="#0e1117")
        ax_sp.set_facecolor("#0e1117")
        draw_spray_chart(pdf, player["name"], ax_sp)
        fig_sp.tight_layout()
        st.pyplot(fig_sp)
        plt.close(fig_sp)

    with col_bb:
        st.subheader(t["batted_ball"])
        profile = batted_ball_profile(pdf, t)
        if profile:
            for k, v in profile.items():
                st.metric(k, v)
        else:
            st.write(t["no_data"])

    st.divider()

    # Row 4: Pitch Type Performance
    st.subheader(t["pitch_type_perf"])
    pt_table = pitch_type_table(pdf, t)
    if not pt_table.empty:
        st.dataframe(pt_table, use_container_width=True, hide_index=True)

        # horizontal bar chart for whiff%
        chart_data = pt_table[[t["pitch_type"], t["whiff_pct"]]].copy()
        chart_data["whiff_val"] = chart_data[t["whiff_pct"]].str.rstrip("%").astype(float)
        chart_data = chart_data.sort_values("whiff_val", ascending=True)

        fig_pt, ax_pt = plt.subplots(figsize=(8, max(3, len(chart_data) * 0.5)), facecolor="#0e1117")
        ax_pt.set_facecolor("#0e1117")
        colors = plt.cm.RdYlGn_r(chart_data["whiff_val"] / max(chart_data["whiff_val"].max(), 1))
        ax_pt.barh(chart_data[t["pitch_type"]], chart_data["whiff_val"], color=colors)
        ax_pt.set_xlabel(t["whiff_pct"], color="white")
        ax_pt.tick_params(colors="white")
        ax_pt.set_title(t["whiff_pct"], color="white", fontweight="bold")
        for spine in ax_pt.spines.values():
            spine.set_color("white")
        fig_pt.tight_layout()
        st.pyplot(fig_pt)
        plt.close(fig_pt)

    st.divider()

    # Row 5: Platoon Splits
    st.subheader(t["platoon"])
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

            # mini zone heatmap
            fig_z, ax_z = plt.subplots(figsize=(5, 4), facecolor="#0e1117")
            ax_z.set_facecolor("#0e1117")
            ax_z.tick_params(colors="white")
            ax_z.xaxis.label.set_color("white")
            ax_z.yaxis.label.set_color("white")
            ax_z.title.set_color("white")
            draw_zone_heatmap(split_df, "ba", f"{label} — {t['ba_heatmap']}", ax_z)
            fig_z.tight_layout()
            st.pyplot(fig_z)
            plt.close(fig_z)

    st.divider()

    # Row 6: Count-based Performance
    st.subheader(t["count_perf"])
    count_df = pdf.dropna(subset=["balls", "strikes"]).copy()
    count_df["count_cat"] = count_df.apply(
        lambda r: count_category(int(r["balls"]), int(r["strikes"])), axis=1
    )

    count_rows = []
    for cat, label in [("ahead", t["ahead"]), ("behind", t["behind"]), ("even", t["even"])]:
        cdf = count_df[count_df["count_cat"] == cat]
        if cdf.empty:
            continue
        cs = batting_stats(cdf)
        count_rows.append({
            "Situation": label,
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
            }),
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
