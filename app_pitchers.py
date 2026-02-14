"""WBC 2026 Venezuela Pitching Scouting Dashboard."""

import pathlib

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib_fontja  # noqa: F401 — enables Japanese font
import numpy as np
import pandas as pd
import streamlit as st

from players import VENEZUELA_PITCHERS, PITCHER_BY_NAME

# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------
TEXTS = {
    "EN": {
        "title": "Venezuela Pitching Scouting Report",
        "subtitle": "WBC 2026 — Quarterfinal Opponent Pitching Analysis",
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
        "avg_velo": "Avg Velo",
        "max_velo": "Max Velo",
        "avg_spin": "Avg Spin",
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
        "avg_ev": "Avg EV Against",
        "avg_la": "Avg LA Against",
        "platoon": "Platoon Splits",
        "vs_lhb": "vs LHB",
        "vs_rhb": "vs RHB",
        "count_perf": "Performance by Count",
        "ahead": "Pitcher Ahead",
        "behind": "Pitcher Behind",
        "even": "Even",
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
        "team_strengths": "Staff Strengths & Weaknesses",
    },
    "JA": {
        "title": "ベネズエラ 投手スカウティングレポート",
        "subtitle": "WBC 2026 — 準々決勝 対戦相手投手分析",
        "select_pitcher": "投手を選択",
        "team_overview": "投手陣概要",
        "season": "シーズン",
        "all_seasons": "全シーズン",
        "profile": "投手プロフィール",
        "team": "チーム",
        "throws": "投げ手",
        "role": "役割",
        "arsenal": "球種構成",
        "pitch_type": "球種",
        "count": "球数",
        "usage_pct": "使用率",
        "avg_velo": "平均球速",
        "max_velo": "最高球速",
        "avg_spin": "平均回転数",
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
        "avg_ev": "被平均打球速度",
        "avg_la": "被平均打球角度",
        "platoon": "左右別スプリット",
        "vs_lhb": "vs 左打者",
        "vs_rhb": "vs 右打者",
        "count_perf": "カウント別パフォーマンス",
        "ahead": "投手有利",
        "behind": "投手不利",
        "even": "イーブン",
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
        "team_strengths": "投手陣の強み・弱み",
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


# ---------------------------------------------------------------------------
# Visualisation helpers
# ---------------------------------------------------------------------------
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
        cmap = plt.cm.RdYlBu_r

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


def draw_movement_chart(df: pd.DataFrame, title: str, ax):
    """Plot pitch movement (pfx_x vs pfx_z) colored by pitch type."""
    valid = df.dropna(subset=["pfx_x", "pfx_z", "pitch_type"]).copy()
    top_types = valid["pitch_type"].value_counts().head(8).index

    for pt in top_types:
        sub = valid[valid["pitch_type"] == pt]
        color = PITCH_COLORS.get(pt, "#AAAAAA")
        label = PITCH_LABELS.get(pt, pt)
        ax.scatter(
            sub["pfx_x"] * 12, sub["pfx_z"] * 12,  # convert ft to inches
            c=color, s=15, alpha=0.5, label=label, edgecolors="none",
        )

    ax.axhline(0, color="white", linewidth=0.5, alpha=0.3)
    ax.axvline(0, color="white", linewidth=0.5, alpha=0.3)
    ax.set_xlabel("Horizontal Break (in)", color="white")
    ax.set_ylabel("Induced Vertical Break (in)", color="white")
    ax.set_title(title, fontsize=13, fontweight="bold", color="white")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.6)
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
            t["avg_velo"]: f"{avg_velo:.1f}" if avg_velo and not pd.isna(avg_velo) else "—",
            t["max_velo"]: f"{max_velo:.1f}" if max_velo and not pd.isna(max_velo) else "—",
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
    )

    # Sidebar
    lang = st.sidebar.radio("Language / 言語", ["EN", "JA"], horizontal=True)
    t = TEXTS[lang]

    st.sidebar.markdown(f"# 🇻🇪 {t['title']}")
    st.sidebar.caption(t["subtitle"])

    pitcher_names = [t["team_overview"]] + [p["name"] for p in VENEZUELA_PITCHERS]
    selected = st.sidebar.selectbox(t["select_pitcher"], pitcher_names)

    df_all = load_data()

    seasons = ["All"] + sorted(df_all["season"].unique().tolist())
    season = st.sidebar.selectbox(t["season"], seasons, format_func=lambda x: t["all_seasons"] if x == "All" else str(x))
    df_all = filter_season(df_all, season)

    # -----------------------------------------------------------------------
    # Staff Overview
    # -----------------------------------------------------------------------
    if selected == t["team_overview"]:
        st.header(f"🇻🇪 {t['team_overview']}")

        rows = []
        for p in VENEZUELA_PITCHERS:
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

    # Row 1: Profile
    st.header(f"🇻🇪 {pitcher['name']}")
    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
    c1.metric(t["team"], pitcher["team"])
    c2.metric(t["throws"], pitcher["throws"])
    c3.metric(t["role"], role_label)
    c4.metric(t["opp_avg"], f"{stats['Opp AVG']:.3f}")
    c5.metric(t["opp_slg"], f"{stats['Opp SLG']:.3f}")
    c6.metric(t["k_pct"], f"{stats['K%']:.1f}%")
    c7.metric(t["bb_pct"], f"{stats['BB%']:.1f}%")
    c8.metric(t["xwoba_against"], f"{stats['xwOBA']:.3f}" if stats["xwOBA"] else "—")

    st.divider()

    # Row 2: Arsenal Table
    st.subheader(t["arsenal"])
    at = arsenal_table(pdf, t)
    if not at.empty:
        st.dataframe(at, use_container_width=True, hide_index=True)

    st.divider()

    # Row 3: Movement Chart + Velo/Spin
    col_mov, col_velo = st.columns([3, 2])

    with col_mov:
        st.subheader(t["movement_chart"])
        fig_m, ax_m = plt.subplots(figsize=(6, 6), facecolor="#0e1117")
        ax_m.set_facecolor("#0e1117")
        for spine in ax_m.spines.values():
            spine.set_color("white")
        draw_movement_chart(pdf, pitcher["name"], ax_m)
        fig_m.tight_layout()
        st.pyplot(fig_m)
        plt.close(fig_m)

    with col_velo:
        st.subheader(t["batted_ball"])
        bb_profile = batted_ball_against(pdf, t)
        if bb_profile:
            for k, v in bb_profile.items():
                st.metric(k, v)
        else:
            st.write(t["no_data"])

    st.divider()

    # Row 4: Zone Heatmaps
    st.subheader(t["zone_heatmap"])
    st.caption(t["danger_zone"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor="#0e1117")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0e1117")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
    draw_zone_heatmap(pdf, "usage", t["usage_heatmap"], ax1)
    im = draw_zone_heatmap(pdf, "ba", t["ba_heatmap"], ax2)
    fig.colorbar(im, ax=[ax1, ax2], shrink=0.7, pad=0.02)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.divider()

    # Row 5: Platoon Splits
    st.subheader(t["platoon"])
    col_l, col_r = st.columns(2)

    for col, stand, label in [(col_l, "L", t["vs_lhb"]), (col_r, "R", t["vs_rhb"])]:
        with col:
            st.markdown(f"**{label}**")
            split_df = pdf[pdf["stand"] == stand]
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
        cs = pitching_stats(cdf)
        count_rows.append({
            "Situation": label,
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
            }),
            use_container_width=True,
            hide_index=True,
        )


if __name__ == "__main__":
    main()
