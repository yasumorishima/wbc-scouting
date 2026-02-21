# WBC 2026 Scouting Dashboard

WBC 2026（World Baseball Classic）参加チームの Statcast データを可視化するスカウティングダッシュボード。

Streamlit Community Cloud にデプロイ済み。MLB で実績のある選手（`mlbam_id` あり）のデータを表示。

## 🌐 ランディングページ

**[https://wbc-2026-scouting-dashboard-zvg.caffeine.xyz/](https://wbc-2026-scouting-dashboard-zvg.caffeine.xyz/)**

全チームのダッシュボードリンクをプール別にまとめたランディングページ（ICP / Caffeine 上でホスト、英語・日本語対応）。

> **アプリが開くまで少々お待ちください ⏳**
>
> Streamlit Community Cloud は一定時間使われないとアプリがスリープします。
> リンクを開いた際に以下のメッセージが表示された場合は正常な動作です。
>
> - **「Zzzz — This app has gone to sleep. Would you like to wake it back up?」**
>   → 「Yes, get this app back up!」ボタンをクリックしてください。
> - **「Your app is in the oven」**
>   → アプリ起動中です。そのまま 30〜60 秒ほどお待ちください。
>
> バグではありません。ボタンを押すかしばらく待つだけで、通常通り使えます。

---

## 📸 スクリーンショット

### 打者ダッシュボード
![Spray Chart](https://raw.githubusercontent.com/yasumorishima/zenn-content/master/images/wbc-batter-spray-chart.png)
![Zone Heatmap](https://raw.githubusercontent.com/yasumorishima/zenn-content/master/images/wbc-batter-zone-heatmap.png)

### 投手ダッシュボード
![Pitch Location](https://raw.githubusercontent.com/yasumorishima/zenn-content/master/images/wbc-pitcher-location.png)
![Pitch Movement](https://raw.githubusercontent.com/yasumorishima/zenn-content/master/images/wbc-pitcher-movement.png)

---

## 🌐 デプロイ済みアプリ一覧

### Pool A — San Juan
| チーム | 打者 | 投手 |
|---|---|---|
| 🇵🇷 Puerto Rico | [Batters](https://wbc-pr-batters.streamlit.app/) | [Pitchers](https://wbc-pr-pitchers.streamlit.app/) |
| 🇨🇺 Cuba | [Batters](https://wbc-cuba-batters.streamlit.app/) | — |
| 🇨🇦 Canada | [Batters](https://wbc-can-batters.streamlit.app/) | [Pitchers](https://wbc-can-pitchers.streamlit.app/) |
| 🇵🇦 Panama | [Batters](https://wbc-pan-batters.streamlit.app/) | [Pitchers](https://wbc-pan-pitchers.streamlit.app/) |
| 🇨🇴 Colombia | [Batters](https://wbc-col-batters.streamlit.app/) | [Pitchers](https://wbc-col-pitchers.streamlit.app/) |

### Pool B — Houston
| チーム | 打者 | 投手 |
|---|---|---|
| 🇺🇸 USA | [Batters](https://wbc-usa-batters.streamlit.app/) | [Pitchers](https://wbc-usa-pitchers.streamlit.app/) |
| 🇲🇽 Mexico | [Batters](https://wbc-mex-batters.streamlit.app/) | [Pitchers](https://wbc-mex-pitchers.streamlit.app/) |
| 🇮🇹 Italy | [Batters](https://wbc-ita-batters.streamlit.app/) | [Pitchers](https://wbc-ita-pitchers.streamlit.app/) |
| 🇬🇧 Great Britain | [Batters](https://wbc-gb-batters.streamlit.app/) | [Pitchers](https://wbc-gb-pitchers.streamlit.app/) |
| 🇧🇷 Brazil | — | — |

### Pool C — Tokyo Dome
| チーム | 打者 | 投手 |
|---|---|---|
| 🇯🇵 Japan | [Batters](https://wbc-japan-batters.streamlit.app/) | [Pitchers](https://wbc-japan-pitchers.streamlit.app/) |
| 🇰🇷 Korea | [Batters](https://wbc-kor-batters.streamlit.app/) | [Pitchers](https://wbc-kor-pitchers.streamlit.app/) |
| 🇹🇼 Chinese Taipei | [Batters](https://wbc-twn-batters.streamlit.app/) | — |
| 🇦🇺 Australia | [Batters](https://wbc-aus-batters.streamlit.app/) | — |
| 🇨🇿 Czechia | — | — |

### Pool D — Miami
| チーム | 打者 | 投手 |
|---|---|---|
| 🇩🇴 Dominican Republic | [Batters](https://wbc-dr-batters.streamlit.app/) | [Pitchers](https://wbc-dr-pitchers.streamlit.app/) |
| 🇻🇪 Venezuela | [Batters](https://wbc-venezuela-batters.streamlit.app/) | [Pitchers](https://wbc-venezuela-pitchers.streamlit.app/) |
| 🇳🇱 Netherlands | [Batters](https://wbc-ned-batters.streamlit.app/) | [Pitchers](https://wbc-ned-pitchers.streamlit.app/) |
| 🇮🇱 Israel | [Batters](https://wbc-isr-batters.streamlit.app/) | [Pitchers](https://wbc-isr-pitchers.streamlit.app/) |
| 🇳🇮 Nicaragua | [Batters](https://wbc-nic-batters.streamlit.app/) | — |

> **備考**
> - Brazil / Czechia: MLB 実績選手なし（全員マイナーリーグ）のためダッシュボードなし
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
