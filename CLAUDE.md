# CLAUDE.md — wbc-scouting

Working rules for Claude Code (cloud or local). This file is the source of truth for this project; the owner's local notes are not visible to cloud sessions.

## Session protocol (cloud)
This project is worked on in Claude Code cloud. The owner starts a session with just 「続き」/「つづきから」, in the environment 「クラウド許可1」 (full network access).
1. Read this file first, then continue from the first unfinished item in **Next tasks**. If there is none, say so plainly; do not invent work.
2. Before ending, record what you did and what comes next **in this file** (update "Next tasks" and add a dated line to "Progress log"). This file is the only memory that survives between cloud sessions.
3. Cloud can push only its session branch: open a PR to `master` and merge it yourself (own repo) so the next session sees the update. Report the merged commit. No `gh` CLI in cloud — use the GitHub MCP tools. `workflow_dispatch` returns 403 from cloud, so the fetch/generate workflows (dispatch-only) cannot be started from cloud; `app-smoke.yml` runs by itself on every PR and push to `master`.
4. Write replies to the owner in Japanese (です/ます). Do not claim anything you did not run in this session, and say where every number was measured (cloud / GitHub Actions run id). The Raspberry Pi and the owner's PC are not reachable from cloud.
5. **What cloud can and cannot verify about the live apps.** Cloud **can** reach `*.streamlit.app` (measured 2026-11-01, see "Cloud reachability": health with curl, rendered page with Playwright) but cannot press Reboot (that needs share.streamlit.io in the owner's browser). Cloud *can* also: run every app with AppTest (`python scripts/apptest_all.py`), and read the results of the `Streamlit Keepalive` and `App smoke test` runs on GitHub Actions. So after a merge, the live apps are **not verified** until the next keepalive run reports `Done: N OK, 0 NG` — and even then only "the server is up" is verified (see discipline 2).
6. **If a merge changes a module the apps import** (`scouting_lib.py`, any `players*.py`), tell the owner in the final reply: 「share.streamlit.io で影響するアプリを Reboot してください」 and name the apps. Streamlit Community Cloud's automatic update re-runs only the main script and keeps already-imported modules, so a new name added to `scouting_lib.py` can leave the live app on an `ImportError` screen; tests do not show this (they start a fresh process). Almost every app imports `scouting_lib`, so a change there may mean rebooting all of them.

## Progress log
- 2026-03 (WBC 2026): batter/pitcher dashboards per country deployed; quarterfinal app `app_qf_jpn_ven.py`.
- 2026-06-11: `keepalive.yml` re-enables itself after each run (survives the 60-day auto-disable of scheduled workflows).
- 2026-10-08: keepalive counts an app OK only when `<app>/~/+/_stcore/health` answers 200 (PR #1); dropped a dead non-linked deployment from `streamlit_apps.txt`; deployed `wbc-aus-pitchers`, fixed two apps that crashed in-script (None in number formats; Brazil had no CSV → now shows a notice and stops), added `app-smoke.yml` (PR #2); README updated (PR #3, `efe23f7`). Smoke run `37776267370`: `39 OK, 0 NG`.
- 2026-11-01: CLAUDE.md added for cloud work. Latest keepalive run `41266729676` (2026-11-01, GitHub Actions): `Visiting 41 Streamlit apps... Done: 41 OK, 0 NG`.
- 2026-11-01 (cloud, ~10:07 UTC): reachability measured (section below). Health of all 41 URLs in `streamlit_apps.txt`: 40 × 200, **wbc-japan-batters 400 = asleep** ("This app has gone to sleep due to inactivity"); not woken (measure-only run). The next keepalive run should wake it or report NG.
- 2026-11-01 (local): keepalive gives every failed app a second look after 120 s and fails only if it is still down (a woken app can take longer than the 90 s wait);  takes an optional . Sleeping between keepalive runs is normal and self-healing (runs woke 1-3 apps on 2026-10-31); do not report it.

## Cloud reachability (measured 2026-11-01, cloud session)
| Check (curl --max-time 60 unless noted) | Result | Proof |
|---|---|---|
| `https://mlb-wp-engine.streamlit.app/~/+/_stcore/health` | 200, 0.49 s | body `ok` |
| `https://yasumorishima-mlb-bat-tracking.streamlit.app/~/+/_stcore/health` | 200, 0.25 s | body `ok` |
| `https://wbc-japan-batters.streamlit.app/~/+/_stcore/health` | **400** (3 tries, also with cookies) | empty body; Playwright page text: "This app has gone to sleep due to inactivity" |
| Health of all 41 URLs in `streamlit_apps.txt` | 40 × 200, 1 × 400 | 400 = wbc-japan-batters (asleep) |
| Main page with curl (`-L`, cookie jar) | 303 → `share.streamlit.io/-/auth/app` → 200 | 9,782 B shell identical to share.streamlit.io (JS loader, not app content) |
| Main page with Playwright Chromium (25 s wait) | 200, app renders | mlb-wp-engine: "MLB Win Probability Engine", modes "WP Calculator / Replay Mode / Bench"; bat-tracking: "Bat Tracking Powered by savant-extras … Load Data"; wbc-japan-pitchers: "日本 投手スカウティングレポート WBC 2026" |
| `https://share.streamlit.io` | 200, 0.22 s | 9,782 B (no login attempted) |

A curl 200 on the main page proves nothing (it is the platform shell); use health + Playwright.

## What this is
WBC 2026 scouting dashboards: one Streamlit app per country and role (batters / pitchers), built on MLB Statcast data for each roster's players (players without MLB Statcast data are not shown), plus one quarterfinal matchup app. All apps are deployed on Streamlit Community Cloud. The repo also hosts the **keepalive for every Streamlit app the owner runs**, including 4 apps that live in other repos (see "Apps").
- `scouting_lib.py` — shared analysis/plot/CSS functions used by the country apps.
- `app_dr.py` / `app_dr_pitchers.py` are the templates; `scripts/generate_apps.py` writes the other `app_<country>[_pitchers].py` from them.
- `players_<country>_{batters,pitchers}.py` — roster → MLBAM id (written by `scripts/gen_player_files.py` from `data/wbc2026_rosters.csv`).
- `data/<country>[_pitchers]_statcast.csv` — committed Statcast extracts (2024–2025), fetched by the GitHub Actions workflows below.
- `app.py` / `app_pitchers.py` — older Venezuela batter/pitcher apps (docstrings say Venezuela; they import `players.py`). Not in `streamlit_apps.txt` and skipped by `detect-new-apps.yml`; which file each live Venezuela URL actually runs is set in the Streamlit dashboard, not in the repo.

## Non-negotiable discipline
1. **`streamlit_apps.txt` is the single source of truth for keepalive.** One URL per line. Never remove a line to make keepalive green; removing a line also stops keepalive for that app (including the 4 non-WBC apps from other repos). A URL that answers 404/503 is a deployment question for the owner.
2. **Health 200 ≠ the app works.** The health endpoint (`<app>/~/+/_stcore/health`: 200 up, 503 "application is down", 404 not deployed, 400 asleep — measured from cloud 2026-11-01 on wbc-japan-batters) says only that the server is up; an app that crashes while running its script still answers 200. In-script crashes are caught only by the AppTest smoke test.
3. **AppTest one app per process.** Apps share module names and caches; running them all in one process gives false failures (e.g. a spurious `KeyError`). Use `scripts/apptest_all.py`, which already does this.
4. Every app must survive a missing or empty CSV (show a notice and `st.stop()`), and every `.style.format` needs `na_rep` — these were the two live crashes on 2026-10-08.
5. Do not commit secrets. `.env` is git-ignored.

## Next tasks (in order)
- **No open task as of 2026-11-01.** The tournament is over; the repo is in maintenance. Keepalive runs every 6 h (all green from 2026-10-29 to 2026-11-01).
- Known gaps (owner decides; not scheduled): `app-smoke.yml` runs only on PR/push, so a crash caused by a newer Streamlit/pandas on Streamlit Cloud (requirements are unpinned `>=`) would show up only after the owner reboots an app, not in CI.

## How to run (cloud)
```bash
pip install -r requirements.txt
python scripts/apptest_all.py      # expects "39 OK, 0 NG" (GitHub Actions run 37776267370, 2026-10-08)
```
- Single app locally: `streamlit run app_japan.py` (use AppTest; cloud has Playwright Chromium, which can also open the live apps).
- Data refresh / player files are **GitHub Actions only and dispatch-only** (`fetch-statcast.yml`, `fetch-all-statcast.yml`, `gen-player-files.yml`), so cloud cannot start them; running the scripts in cloud is possible (`python fetch_data_generic.py --country japan [--pitchers] [--year 2025]`, `python scripts/gen_player_files.py --country japan`) and commits go through a PR.
- Adding an app: create `app_<x>.py`, push; `detect-new-apps.yml` opens an issue (label `keepalive`) if its URL is missing from `streamlit_apps.txt`; add the URL. Deploying the app itself on Streamlit Cloud is done by the owner.

## Apps (from `streamlit_apps.txt`, 41 URLs; counted 2026-11-01)
Non-WBC (other repos): `npb-prediction`, `baseball-mlops`, `yasumorishima-mlb-bat-tracking`, `mlb-wp-engine`.
WBC (37, `https://wbc-<slug>.streamlit.app/`):
- Pool A: pr-batters, pr-pitchers, cuba-batters, cuba-pitchers, can-batters, can-pitchers, pan-batters, pan-pitchers, col-batters, col-pitchers
- Pool B: usa-batters, usa-pitchers, mex-batters, mex-pitchers, ita-batters, ita-pitchers, gb-batters, gb-pitchers, bra-batters, bra-pitchers
- Pool C: japan-batters, japan-pitchers, kor-batters, kor-pitchers, twn-batters, aus-batters, aus-pitchers
- Pool D: dr-batters, dr-pitchers, venezuela-batters, venezuela-pitchers, ned-batters, ned-pitchers, isr-batters, isr-pitchers, nic-batters
- Quarterfinal: qf-jpn-ven

No pitcher app for twn / nic (too little pitcher Statcast data) and no app for Czechia (no MLB-organization players). The repo has 39 `app*.py` files = these 37 + `app.py` + `app_pitchers.py`.

## Data access
Baseball Savant Statcast via `pybaseball` (`baseballsavant.mlb.com`), PyPI for packages. The apps themselves read only the committed CSVs in `data/`.

## Credits (keep in README)
Baseball Savant Statcast data (via pybaseball); WBC 2026 rosters (`data/wbc2026_rosters.csv`); MLB stadium coordinates (`data/mlbstadiums_wbc.csv`).
