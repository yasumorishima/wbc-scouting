# CLAUDE.md — wbc-scouting

Working rules for Claude Code (cloud or local). This file is the source of truth for this project; the owner's local notes are not visible to cloud sessions.

## Session protocol (cloud)
This project is worked on in Claude Code cloud. The owner starts a session with just 「続き」/「つづきから」, in the environment 「クラウド許可1」 (full network access).
1. Read this file first, then continue from the first unfinished item in **Next tasks**. If there is none, say so plainly; do not invent work.
2. Before ending, record what you did and what comes next **in this file** (update "Next tasks" and add a dated line to "Progress log"). This file is the only memory that survives between cloud sessions.
3. Cloud can push only its session branch: open a PR to `master` and merge it yourself (own repo) so the next session sees the update. Report the merged commit. No `gh` CLI in cloud — use the GitHub MCP tools. `workflow_dispatch` returns 403 from cloud, so the fetch/generate workflows (dispatch-only) cannot be started from cloud; `app-smoke.yml` runs by itself on every PR and push to `master`.
4. Write replies to the owner in Japanese (です/ます). Do not claim anything you did not run in this session, and say where every number was measured (cloud / GitHub Actions run id). The Raspberry Pi and the owner's PC are not reachable from cloud.
5. **The 37 WBC apps are pre-rendered static pages on GitHub Pages** (every state a visitor can choose is built in advance from the unchanged Streamlit app, so a page opens at once; no server, nothing sleeps): https://yasumorishima.github.io/wbc-scouting/ . A merge that touches an app, a module, `data/**` or the Pages scripts redeploys them by itself (`pages.yml`, also after the data workflows finish), and its `check` job opens every page and every state and fails on any difference — read its result (`pages-check` branch: `summary.md`, `result.json`, screenshots) before saying a change works. There is nothing to reboot for the pages.
6. **Streamlit Community Cloud now matters only for the 4 non-WBC apps** in `streamlit_apps.txt` (other repos). Cloud can reach `*.streamlit.app` (measured 2026-11-01, see "Cloud reachability") but cannot press Reboot (share.streamlit.io in a browser). The 37 WBC deployments on Streamlit Cloud are kept (owner, 2026-11-01: do not delete them) but are no longer kept awake or watched; do not report them asleep and do not add them back to keepalive.

## Progress log
- 2026-03 (WBC 2026): batter/pitcher dashboards per country deployed; quarterfinal app `app_qf_jpn_ven.py`.
- 2026-06-11: `keepalive.yml` re-enables itself after each run (survives the 60-day auto-disable of scheduled workflows).
- 2026-10-08: keepalive counts an app OK only when `<app>/~/+/_stcore/health` answers 200 (PR #1); dropped a dead non-linked deployment from `streamlit_apps.txt`; deployed `wbc-aus-pitchers`, fixed two apps that crashed in-script (None in number formats; Brazil had no CSV → now shows a notice and stops), added `app-smoke.yml` (PR #2); README updated (PR #3, `efe23f7`). Smoke run `37776267370`: `39 OK, 0 NG`.
- 2026-11-01: CLAUDE.md added for cloud work. Latest keepalive run `41266729676` (2026-11-01, GitHub Actions): `Visiting 41 Streamlit apps... Done: 41 OK, 0 NG`.
- 2026-11-01 (cloud, ~10:07 UTC): reachability measured (section below). Health of all 41 URLs in `streamlit_apps.txt`: 40 × 200, **wbc-japan-batters 400 = asleep** ("This app has gone to sleep due to inactivity"); not woken (measure-only run). The next keepalive run should wake it or report NG.
- 2026-11-01 (local): keepalive gives every failed app a second look after 120 s and fails only if it is still down (a woken app can take longer than the 90 s wait); workflow_dispatch takes an optional memo input. Sleeping between keepalive runs is normal and self-healing (runs woke 1-3 apps on 2026-10-31); do not report it.

- 2026-11-01 (local, via GitHub Actions): all 37 WBC apps moved to GitHub Pages (stlite 1.12.0). `scripts/build_pages.py` builds one page per `app_*.py` (same names as the Streamlit subdomains) plus an index; `scripts/pages_check.py` opens every page and picks the first player with data. First run 41303255017: 28 OK, 9 NG — the 9 were apps whose first roster player has no Statcast rows (the app's own "no data" notice), fixed in the checker, not in the apps. Then run 41310262764 (with --cloud): 37 OK, 0 NG and the same headings, figure counts and chosen player as Streamlit Cloud on all 37; first render 18-30 s (qf-jpn-ven 78.6 s) with 3 pages loading at once. Then the 37 WBC URLs were removed from `streamlit_apps.txt` (keepalive keeps the 4 non-WBC apps), `detect-new-apps.yml` was removed (it mapped `app_qf_jpn_ven.py` to a wrong URL and its issue creation had been failing silently on a missing label), README re-pointed to the pages.
- 2026-11-02 (local, Raspberry Pi 5 + GitHub Actions): the Pages site moved from stlite to pre-rendered static pages (PR #7). Every state a visitor can choose is built in advance, so a page opens at once (first screen on the published site: median 0.39 s, max 1.4 s over the 37 dashboards, check job of run 41407789248; stlite took 18-30 s and 78.6 s for qf-jpn-ven). The dry run 41395020868 (publish=false, on the branch) gave:
  - 7,063 states on 1,308 pages, with 4,651 control options tried;
  - sampled states equal the real Streamlit run (AppTest) in all 45 render jobs;
  - 665 MB site, 21,068 figures.
  Its one failure was the new heading gate on player pages that show only a notice ("このフィルターではデータがありません。"); the gate was fixed. The same review found closed tab panels displayed (CSS) and bold headings run into the list above in the summaries (missing blank lines; same on Streamlit); both were fixed.
  The slowest jobs were qf-jpn-ven, 8 shards of 91 states at about 2,550 s each, and dr-pitchers, 584 states in 1,489 s. Production run 41407789248 (PR #7 merge `f1f5200`): verify 37/37 OK before publishing and check 37/37 OK on the published site (7,252 states on 1,308 pages, 4,798 control options, 21,068/21,068 figures, 665 MB); about 85 min end to end.
- 2026-11-02 (local, Raspberry Pi 5 + GitHub Actions): PR #9 (docs for the pre-rendered site), PR #10 (pillow 13, streamlit 1.66.1; open Dependabot alerts 0 on 2026-11-03), PR #11 (alert icons left of the text). The post-publish check then failed twice on GitHub Pages refusals (429/503) although every file was there, so `scripts/pages_check.py` now asks again: a page is opened again on 429/5xx or a failed load (PR #12), and refused figure files are asked again in rounds, the pause doubling up to 4 min, until none is refused or the 30-min limit is reached (PR #13). A 404 is final and a file still refused at the limit still fails. `scripts/pages_check_test.py` tests this in the verify job. Run 41494150308 (PR #13 merge `0b46928`): verify, deploy and check all success. The check gave 37/37 dashboards OK, 7,252 states on 1,308 pages, 4,798 control options, 21,068/21,068 figure files (2,321 refused in the sweep, 8 after round 1, none after round 2), first screen median 0.41 s and max 0.81 s.

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
WBC 2026 scouting dashboards: one Streamlit app per country and role (batters / pitchers), built on MLB Statcast data for each roster's players (players without MLB Statcast data are not shown), plus one quarterfinal matchup app. Served as static pages on GitHub Pages since 2026-11-01 (stlite at first, pre-rendered since 2026-11-02; the tournament-time Streamlit Cloud deployments still exist but sleep). The repo also hosts the **keepalive for the owner's other Streamlit apps** (4 apps in other repos, see "Apps").
- The Pages site (see protocol 5):
  - `scripts/st_record.py`: a recording stand-in for `streamlit`.
  - `scripts/prerender.py`: runs each app once per state and writes HTML and AVIF figures. Sidebar states are pages; main-area states are `<template>` segments swapped by `scripts/prerender_page.js`.
  - `scripts/render_html.py`, `scripts/prerender_page.css`: the page markup and styles.
  - `scripts/prerender_check.py`: compares sampled states with the real Streamlit runtime (AppTest).
  - `scripts/build_pages.py`: the job list (`SHARDS`) and the index.
  - `scripts/pages_check.py`: the browser check.
  - `.github/workflows/pages.yml` runs them all; the pinned versions are in `scripts/requirements-pages.txt`.
- `scouting_lib.py` — shared analysis/plot/CSS functions used by the country apps.
- `app_dr.py` / `app_dr_pitchers.py` are the templates; `scripts/generate_apps.py` writes the other `app_<country>[_pitchers].py` from them.
- `players_<country>_{batters,pitchers}.py` — roster → MLBAM id (written by `scripts/gen_player_files.py` from `data/wbc2026_rosters.csv`).
- `data/<country>[_pitchers]_statcast.csv` — committed Statcast extracts (2024–2025), fetched by the GitHub Actions workflows below.
- `app.py` / `app_pitchers.py` — older Venezuela batter/pitcher apps (docstrings say Venezuela; they import `players.py`). Not pages (`build_pages.py` uses `app_venezuela*.py`).

## Non-negotiable discipline
1. **`streamlit_apps.txt` is the single source of truth for keepalive** (now the 4 non-WBC apps). One URL per line. Never remove a line to make keepalive green. A URL that answers 404/503 is a deployment question for the owner.
2. **Health 200 ≠ the app works.** The health endpoint (`<app>/~/+/_stcore/health`: 200 up, 503 "application is down", 404 not deployed, 400 asleep — measured from cloud 2026-11-01 on wbc-japan-batters) says only that the server is up; an app that crashes while running its script still answers 200. In-script crashes are caught only by the AppTest smoke test.
3. **AppTest one app per process.** Apps share module names and caches; running them all in one process gives false failures (e.g. a spurious `KeyError`). Use `scripts/apptest_all.py`, which already does this.
4. Every app must survive a missing or empty CSV (show a notice and `st.stop()`), and every `.style.format` needs `na_rep` — these were the two live crashes on 2026-10-08.
5. Do not commit secrets. `.env` is git-ignored.
6. **Pages gates are never loosened to pass.** Each of these stops the build or fails the check:
   - `build_pages.py` stops on an import the build does not install, an unexpected missing CSV, or a dashboard missing from the index.
   - `prerender.py` stops on any Streamlit call or argument the recorder does not know, and on a control option that leads to no built state (or to more than one).
   - `prerender_check.py` fails when a sampled state differs from the real Streamlit run in text, tables, figure count or widgets.
   - `pages.yml` stops above 950 MB.
   - `pages_check.py` fails a page when:
     - a state's figures or text differ from the build;
     - a control option shows no built state;
     - a hidden element is displayed;
     - the first screen is slower than 3 s;
     - Back or a fresh visit shows the wrong choices.

## Next tasks (in order)
- **No open task as of 2026-11-02.** The tournament is over; the repo is in maintenance. The pages need no keepalive; keepalive runs every 6 h for the 4 non-WBC apps.
- Known gaps (owner decides; not scheduled): the render check runs only after a deploy, not on a schedule. The pages load the Source Sans 3 font from Google Fonts (text shows at once in a fallback font if it is slow or down).

## How to run (cloud)
```bash
pip install -r requirements.txt
python scripts/apptest_all.py      # expects "39 OK, 0 NG" (GitHub Actions run 37776267370, 2026-10-08)
```
- Single app locally: `streamlit run app_japan.py` (use AppTest; cloud has Playwright Chromium, which can also open the live apps).
- Data refresh / player files are **GitHub Actions only and dispatch-only** (`fetch-statcast.yml`, `fetch-all-statcast.yml`, `gen-player-files.yml`), so cloud cannot start them; running the scripts in cloud is possible (`python fetch_data_generic.py --country japan [--pitchers] [--year 2025]`, `python scripts/gen_player_files.py --country japan`) and commits go through a PR.
- Adding an app: create `app_<x>.py`, push; `pages.yml` builds and checks its page (a new country must be added to `POOLS` and `COUNTRY` in `scripts/build_pages.py`, or the build stops).
- Build one dashboard in cloud without deploying: `pip install -r scripts/requirements-pages.txt && python scripts/prerender.py _site app_japan.py --jobs 4` (japan-batters: 60 states, ~6 min on a Raspberry Pi 5 with 2 processes), then `python scripts/prerender_check.py _site --per-app 6`. The quarterfinal app has 728 states; build it only in GitHub Actions (8 shards).
- Whole-site dry run of a branch: dispatch `pages.yml` on that branch. A run on a branch never publishes, and neither does `publish=false` or a non-empty `only`. A full run takes about 80 min, most of it the 8 quarterfinal shards. Cloud cannot dispatch, so the owner or a local session starts it. A merge to `master` builds, checks and publishes by itself; nothing is published unless the `verify` job's browser check passes.

## Apps
Keepalive (`streamlit_apps.txt`, 4 URLs): `npb-prediction`, `baseball-mlops`, `yasumorishima-mlb-bat-tracking`, `mlb-wp-engine`.
WBC pages (37, `https://yasumorishima.github.io/wbc-scouting/<slug>.html`; the same `<slug>` as the old `https://wbc-<slug>.streamlit.app/`):
- Pool A: pr-batters, pr-pitchers, cuba-batters, cuba-pitchers, can-batters, can-pitchers, pan-batters, pan-pitchers, col-batters, col-pitchers
- Pool B: usa-batters, usa-pitchers, mex-batters, mex-pitchers, ita-batters, ita-pitchers, gb-batters, gb-pitchers, bra-batters, bra-pitchers
- Pool C: japan-batters, japan-pitchers, kor-batters, kor-pitchers, twn-batters, aus-batters, aus-pitchers
- Pool D: dr-batters, dr-pitchers, venezuela-batters, venezuela-pitchers, ned-batters, ned-pitchers, isr-batters, isr-pitchers, nic-batters
- Quarterfinal: qf-jpn-ven

No pitcher app for twn / nic (too little pitcher Statcast data) and no app for Czechia (no MLB-organization players). Brazil has no CSV; its two pages show the no-data notice. The repo has 39 `app*.py` files = these 37 + `app.py` + `app_pitchers.py`.

## Data access
Baseball Savant Statcast via `pybaseball` (`baseballsavant.mlb.com`), PyPI for packages. The apps themselves read only the committed CSVs in `data/`.

## Credits (keep in README)
Baseball Savant Statcast data (via pybaseball); WBC 2026 rosters (`data/wbc2026_rosters.csv`); MLB stadium coordinates (`data/mlbstadiums_wbc.csv`).
