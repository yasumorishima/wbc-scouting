# WBC 2026 Scouting Dashboard

WBC 2026（World Baseball Classic）参加チームの Statcast データを可視化するスカウティングダッシュボード。

Streamlit Community Cloud にデプロイ済み。MLB で実績のある選手（`mlbam_id` あり）のデータを表示。

---

## 🌐 デプロイ済みアプリ一覧

### Group A
| チーム | 打者 | 投手 |
|---|---|---|
| 🇩🇴 Dominican Republic | [Batters](https://wbc-dr-batters.streamlit.app/) | [Pitchers](https://wbc-dr-pitchers.streamlit.app/) |
| 🇻🇪 Venezuela | [Batters](https://wbc-venezuela-batters.streamlit.app/) | [Pitchers](https://wbc-venezuela-pitchers.streamlit.app/) |
| 🇨🇺 Cuba | [Batters](https://wbc-cuba-batters.streamlit.app/) | — |
| 🇳🇮 Nicaragua | [Batters](https://wbc-nic-batters.streamlit.app/) | — |
| 🇵🇦 Panama | [Batters](https://wbc-pan-batters.streamlit.app/) | [Pitchers](https://wbc-pan-pitchers.streamlit.app/) |
| 🇨🇴 Colombia | [Batters](https://wbc-col-batters.streamlit.app/) | [Pitchers](https://wbc-col-pitchers.streamlit.app/) |

### Group B
| チーム | 打者 | 投手 |
|---|---|---|
| 🇺🇸 USA | [Batters](https://wbc-usa-batters.streamlit.app/) | [Pitchers](https://wbc-usa-pitchers.streamlit.app/) |
| 🇵🇷 Puerto Rico | [Batters](https://wbc-pr-batters.streamlit.app/) | [Pitchers](https://wbc-pr-pitchers.streamlit.app/) |
| 🇲🇽 Mexico | [Batters](https://wbc-mex-batters.streamlit.app/) | [Pitchers](https://wbc-mex-pitchers.streamlit.app/) |
| 🇨🇦 Canada | [Batters](https://wbc-can-batters.streamlit.app/) | [Pitchers](https://wbc-can-pitchers.streamlit.app/) |
| 🇧🇷 Brazil | — | — |

### Group C
| チーム | 打者 | 投手 |
|---|---|---|
| 🇯🇵 Japan | [Batters](https://wbc-japan-batters.streamlit.app/) | [Pitchers](https://wbc-japan-pitchers.streamlit.app/) |
| 🇰🇷 Korea | [Batters](https://wbc-kor-batters.streamlit.app/) | [Pitchers](https://wbc-kor-pitchers.streamlit.app/) |
| 🇹🇼 Chinese Taipei | [Batters](https://wbc-twn-batters.streamlit.app/) | — |
| 🇦🇺 Australia | [Batters](https://wbc-aus-batters.streamlit.app/) | — |

### Group D
| チーム | 打者 | 投手 |
|---|---|---|
| 🇳🇱 Netherlands | [Batters](https://wbc-ned-batters.streamlit.app/) | [Pitchers](https://wbc-ned-pitchers.streamlit.app/) |
| 🇮🇹 Italy | [Batters](https://wbc-ita-batters.streamlit.app/) | [Pitchers](https://wbc-ita-pitchers.streamlit.app/) |
| 🇮🇱 Israel | [Batters](https://wbc-isr-batters.streamlit.app/) | [Pitchers](https://wbc-isr-pitchers.streamlit.app/) |
| 🇬🇧 Great Britain | [Batters](https://wbc-gb-batters.streamlit.app/) | [Pitchers](https://wbc-gb-pitchers.streamlit.app/) |

> **備考**
> - Brazil: MLB 実績選手なし（全員マイナーリーグ）のためダッシュボードなし
> - Cuba / Nicaragua / Chinese Taipei / Australia: 投手の MLB Statcast データなしのため投手ダッシュボードなし

---

## 📊 機能

### 打者ダッシュボード
- チーム Overview（主要打撃指標一覧）
- 選手別詳細: プロフィール、球種別打撃成績、ゾーンヒートマップ（3×3）、スプレーチャート
- vs LHP / vs RHP スプレーチャート
- カウント別パフォーマンス（0-0〜3-2 全カウント）
- 密度ヒートマップ（ガウシアン KDE）

### 投手ダッシュボード
- チーム Overview（主要投球指標一覧）
- 選手別詳細: プロフィール、球種別成績、変化量チャート、配球ヒートマップ
- 左右打者別成績、カウント別パフォーマンス・球種配分
- 球種フィルター（全セクション連動）

---

## 🗂️ データソース

- [Baseball Savant](https://baseballsavant.mlb.com/) Statcast データ（[pybaseball](https://github.com/jldbc/pybaseball) 経由）
- WBC 2026 公式ロスター（`data/wbc2026_rosters.csv`、20チーム 306人）
- MLB 球場座標（`data/mlbstadiums_wbc.csv`）

---

## 🛠️ Tech Stack

- Python 3.11
- [Streamlit](https://streamlit.io/)
- [pybaseball](https://github.com/jldbc/pybaseball)
- pandas / matplotlib / scipy
- GitHub Actions（Statcast CSV 自動取得 → push）
