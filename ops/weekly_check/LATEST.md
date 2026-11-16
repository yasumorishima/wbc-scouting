# Weekly check 2026-11-16

Status: NEEDS ATTENTION (2 items)

Measured from a Claude Code cloud session, 2026-11-16 00:05–00:20 UTC (GitHub data via the GitHub MCP tools; HTTP checks with `curl --max-time 60` from cloud). Compared with `2026-11-09.md`. Both items are carried over (issue #6); nothing new.

## Needs attention
| # | item | evidence | owner action |
|---|---|---|---|
| 1 | baseball-scorebook-ocr `Dependabot Updates` still failing (issue #6 item 2) | latest run 41186202664 (2026-10-31, zod) failure, prev 34522067192 (2026-09-10) failure, no newer run. Cause recorded earlier: `misconfigured_tooling` (`bun.lock`, no npm/yarn/pnpm lock) | Set `package-ecosystem: "bun"` in dependabot.yml, or stop version updates for that directory |
| 2 | baseball-mlops `CodeQL` (`codeql.yml`) still `disabled_inactivity` (issue #6 item 3) | last run 27895915491 (2026-06-21, success). CodeQL default setup is active and green (latest 43711977001, 2026-11-15, success) | Re-enable in the web UI, or decide `codeql.yml` is no longer needed |

## 1a. WBC Pages
| item | result | evidence |
|---|---|---|
| Latest `Pages (pre-rendered)` run on master | success | run 41579235464 (push, 2026-11-03, `a4b379e`); no newer run (no master change touched the watched paths). `pages-check/RUN.txt`: "run 41579235464 … check outcome: success"; `summary.md`: 37/37 dashboards OK, 7252 states / 1308 pages, 21068/21068 figure files |

## 1b. Streamlit keepalive (4 non-WBC apps)
| item | result | evidence |
|---|---|---|
| Latest run time | 2026-11-15T22:09Z (2.0 h before check), workflow active | run 43767692560 (schedule) |
| Conclusion / STILL DOWN | success, no STILL DOWN | log: "Visiting 4 Streamlit apps... Done: 4 OK, 0 NG"; every keepalive run since 2026-11-04 success |

## 2. mlb-pitch-forecast API
| item | result | evidence |
|---|---|---|
| GET /api/predict | 200, 3.0 s, 1,268 B | `data_through` 2026-09-27, `model` "2026 before 2026-09-21", `serve_season` 2027 |
| POST example_request | 200, 0.48 s, 292 B | 9 probabilities, sum 1.0 (FF 0.369, CH 0.377, SL 0.145 …), most_likely CH |

## 3. GitHub Actions (17 repos)
| item | result | evidence |
|---|---|---|
| Failed latest runs in the last 8 days | 0 | all 17 repos. mlb-data-pipeline `dbt Marts` 42581472508 (2026-11-09, parser download 504) was superseded by 42584023254 (2026-11-09, success, PR #61 pin) |
| Disabled scheduled workflows | 1 inactivity + 1 manual | baseball-mlops `codeql.yml` `disabled_inactivity` (item 2); `spring_update.yml` `disabled_manually` (owner's choice) |
| Older failures still latest (info) | 5 | baseball-scorebook-ocr Dependabot 41186202664 (item 1); npb-prediction `hf_restricted_cleanup` 39987719328 (one-off, follow-up 40032482140 success), `research_marcel_weights` 37744242090 and `research_stan` 37744243411 (branch consolidate-research, 2026-10-08); kaggle-datasets `update-metadata` 36434751768 (2026-09-28) |
| Notable successes | — | mlb-data-pipeline `Weekly Data Refresh` 42580182035 (2026-11-09) success, 11-16 run not started at check time; mlb-pitch-forecast `build-model` daily success to 43743265044 (2026-11-15); savant-extras `Live Savant` 42609537792 (2026-11-09) success, 11-16 run not started yet; npb-foreign-statcast `Frozen files` 42624617539 (2026-11-09) success |

## 4. Open PRs (17 repos)
| item | result | evidence |
|---|---|---|
| Open PRs | none | `list_pull_requests` state=open, all 17 repos |
| Merged by this check | none (other than this record's own PR) | |

## 5. Cloud reachability (unchanged from 2026-11-09)
| item | result | evidence |
|---|---|---|
| Kaggle `www.kaggle.com/api/v1/datasets/list?user=yasunorim` | 200, 0.30 s | 11 datasets |
| Savant sprint_speed 2025 CSV | 200, 0.34 s, 36,204 B | 579 lines |
| Stats API teams sportId=1 | 200, 0.15 s | 30 teams |
