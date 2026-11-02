# Weekly check 2026-11-02

Status: NEEDS ATTENTION (3 items)

Measured from a Claude Code cloud session, 2026-11-02 00:00–00:10 UTC (GitHub data via the GitHub MCP tools; HTTP checks with `curl --max-time 60` from cloud). This is the first weekly check (no earlier LATEST.md to compare with).

## Needs attention
| # | item | evidence | owner action |
|---|---|---|---|
| 1 | mlb-data-pipeline `Weekly Data Refresh` latest run failed; `dbt Marts` skipped | run 40275703412 (schedule, 2026-10-26) failure, prev 39205581128 success; dbt Marts 40277350449 skipped. The 2026-11-02 run (cron Mon 01:00 UTC) had not started at check time. Known item (mlb-data-pipeline CLAUDE.md task 0: exit 134 after "Every expected table was produced.") | Look at the 2026-11-02 run; if it fails the same way, fix by PR per that CLAUDE.md |
| 2 | baseball-scorebook-ocr `Dependabot Updates` failing | run 41186202664 (2026-10-31, zod) failure, prev 34522067192 (2026-09-10, vitest) failure. Log: `misconfigured_tooling` — repo has `bun.lock` but no npm/yarn/pnpm lock; Dependabot asks for `package-ecosystem: "bun"` in dependabot.yml | Change the ecosystem in Dependabot config to `bun` (or turn off version updates for that directory) |
| 3 | baseball-mlops `CodeQL` (scheduled) disabled for inactivity | workflow state `disabled_inactivity`, last run 27895915491 (2026-06-21, success). Already noted in baseball-mlops CLAUDE.md task 3 | Re-enable in the Actions web UI if wanted (cloud cannot); or leave as is |

## 1a. WBC Pages
| item | result | evidence |
|---|---|---|
| Latest `Pages (stlite)` run | success | run 41312353694 (push, 2026-11-01T13:39Z, `b3e1b77`); `pages-check/RUN.txt`: "check outcome: success"; `summary.md` all rows OK. Later master commit `d9b01ec` (README only) did not trigger a run |

## 1b. Streamlit keepalive (4 non-WBC apps)
| item | result | evidence |
|---|---|---|
| Latest run time | 2026-11-01T21:24Z (2.6 h before check) | run 41351851654 (schedule), workflow state active |
| Conclusion / STILL DOWN | success, no STILL DOWN | log: "Visiting 4 Streamlit apps... Done: 4 OK, 0 NG"; previous run 41305014557 success |

## 2. mlb-pitch-forecast API
| item | result | evidence |
|---|---|---|
| GET /api/predict | 200, 2.9 s, 1,268 B | `data_through` 2026-09-27, `model` "2026 before 2026-09-21", `serve_season` 2027 |
| POST example_request | 200, 0.43 s | 9 probabilities, sum 1.000000 (FF 0.369, CH 0.377, SL 0.145 …), most_likely CH |

## 3. GitHub Actions (17 repos)
| item | result | evidence |
|---|---|---|
| Failed latest runs in the last 8 days | 2 | items 1 and 2 above |
| Disabled scheduled workflows | 1 inactivity + 1 manual | baseball-mlops CodeQL `disabled_inactivity` (item 3); baseball-mlops `spring_update.yml` `disabled_manually` (owner's choice, per its CLAUDE.md — not a finding) |
| Older failures (latest run before 2026-10-25, info only) | 4 | npb-prediction `hf_restricted_cleanup.yml` 39987719328 (one-off, 2026-10-23; follow-up recreate 40032482140 success); npb-prediction `research_marcel_weights.yml` 37744242090 and `research_stan.yml` 37744243411 (push to branch consolidate-research, 2026-10-08); kaggle-datasets `update-metadata.yml` 36434751768 (2026-09-28, dispatch) |
| Everything else | latest run success / skipped / no runs | Dependency Graph workflow runs were not listed |

## 4. Open PRs (17 repos)
| item | result | evidence |
|---|---|---|
| Open PRs | none | `list_pull_requests` state=open, all 17 repos |
| Merged by this check | none (other than this record's own PR) | |

## 5. Cloud reachability
| item | result | evidence |
|---|---|---|
| Kaggle `www.kaggle.com/api/v1/datasets/list?user=yasunorim` | 200 | 11 datasets |
| Savant sprint_speed 2025 CSV | 200 | 579 lines |
| Stats API teams sportId=1 | 200 | 30 teams |
