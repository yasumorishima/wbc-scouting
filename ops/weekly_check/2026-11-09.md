# Weekly check 2026-11-09

Status: NEEDS ATTENTION (2 items)

Measured from a Claude Code cloud session, 2026-11-09 00:05–00:25 UTC (GitHub data via the GitHub MCP tools; HTTP checks with `curl --max-time 60` from cloud). Compared with `2026-11-02.md`. Both items are carried over from last week (issue #6); last week's item 1 (mlb-data-pipeline refresh) is resolved.

## Needs attention
| # | item | evidence | owner action |
|---|---|---|---|
| 1 | baseball-scorebook-ocr `Dependabot Updates` still failing (carried over, issue #6 item 2) | latest run 41186202664 (2026-10-31, zod) failure, prev 34522067192 (2026-09-10) failure, no newer run. Log: `misconfigured_tooling` — `bun.lock` but no npm/yarn/pnpm lock; set `package-ecosystem: "bun"` | Change the Dependabot ecosystem to `bun` (or turn off version updates for that directory) |
| 2 | baseball-mlops `CodeQL` (`codeql.yml`, scheduled) still `disabled_inactivity` (carried over, issue #6 item 3) | last run 27895915491 (2026-06-21, success). New since last week: GitHub CodeQL default setup is active there (setup run 42133727988, 2026-11-06, success) | Re-enable in the web UI, or delete/leave `codeql.yml` since default setup now covers code scanning |

## Resolved since last week
| item | evidence |
|---|---|
| mlb-data-pipeline `Weekly Data Refresh` | run 41404288278 (schedule, 2026-11-02) success; `dbt Marts` 41405895920 (2026-11-02) success. The 2026-11-09 run had not started at check time |

## 1a. WBC Pages
| item | result | evidence |
|---|---|---|
| Latest `Pages (pre-rendered)` run on master | success | run 41579235464 (push, 2026-11-03T04:37Z, `a4b379e`); before it 41562415321 failure (attempt 2), superseded. `pages-check/RUN.txt`: "run 41579235464 … check outcome: success"; `summary.md`: 37/37 OK, 7252 states / 1308 pages, 21068/21068 figure files. Later master commit `2c6c703` (README) did not trigger a run |

## 1b. Streamlit keepalive (4 non-WBC apps)
| item | result | evidence |
|---|---|---|
| Latest run time | 2026-11-08T21:24Z (2.8 h before check), workflow active | run 42525034575 (schedule) |
| Conclusion / STILL DOWN | success, no STILL DOWN | log: "Visiting 4 Streamlit apps... Done: 4 OK, 0 NG"; all runs since 2026-11-03 success |

## 2. mlb-pitch-forecast API
| item | result | evidence |
|---|---|---|
| GET /api/predict | 200, 3.0 s, 1,268 B | `data_through` 2026-09-27, `model` "2026 before 2026-09-21", `serve_season` 2027 |
| POST example_request | 200, 0.24 s | 9 probabilities, sum 1.0 (FF 0.369, CH 0.377, SL 0.145 …), most_likely CH |

## 3. GitHub Actions (17 repos)
| item | result | evidence |
|---|---|---|
| Failed latest runs in the last 8 days | 0 | all 17 repos |
| Disabled scheduled workflows | 1 inactivity + 1 manual | baseball-mlops `codeql.yml` `disabled_inactivity` (item 2); baseball-mlops `spring_update.yml` `disabled_manually` (owner's choice) |
| Older failures still latest (info) | 5 | baseball-scorebook-ocr Dependabot 41186202664 (item 1); npb-prediction `hf_restricted_cleanup` 39987719328 (one-off, follow-up 40032482140 success), `research_marcel_weights` 37744242090 and `research_stan` 37744243411 (branch consolidate-research, 2026-10-08); kaggle-datasets `update-metadata` 36434751768 (2026-09-28) |
| Notable successes | — | mlb-pitch-forecast `build-model` daily success to 42503350008 (2026-11-08); savant-extras `Live Savant` 41434037691 (2026-11-02) success, 11-09 run not started yet; npb-foreign-statcast `Frozen files` 41448087651 (11-02) success; CodeQL default setup enabled 2026-11-06 in 16 repos, all setup runs success |

## 4. Open PRs (17 repos)
| item | result | evidence |
|---|---|---|
| Open PRs | none | `list_pull_requests` state=open, all 17 repos |
| Merged by this check | none (other than this record's own PR) | |

## 5. Cloud reachability (unchanged from 2026-11-02)
| item | result | evidence |
|---|---|---|
| Kaggle `www.kaggle.com/api/v1/datasets/list?user=yasunorim` | 200 | 11 datasets |
| Savant sprint_speed 2025 CSV | 200 | 579 lines |
| Stats API teams sportId=1 | 200 | 30 teams |
