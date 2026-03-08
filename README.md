# WBC 2026 Scouting Dashboard

WBC 2026（World Baseball Classic）参加チームの Statcast データを可視化するスカウティングダッシュボード。

Streamlit Community Cloud にデプロイ済み。Baseball Savant の Statcast データ（`mlbam_id` で紐付け）がある選手のみ表示。MLB 出場経験のない選手は Statcast データが存在しないため対象外。20か国 306選手中、97選手の MLBAM ID を 2026-03-08 に一括追加。

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

## 📅 スケジュール

<details>
<summary>1次ラウンド + 決勝トーナメント日程（クリックで展開）</summary>

> ※ 時刻は日本時間（JST）。US会場の（）内は現地日時
> ※ San Juan: AST / Houston: CT / Miami: ET
### 1次ラウンド

| 日付 | JST | Pool A (San Juan) | Pool B (Houston) | Pool C (Tokyo) | Pool D (Miami) |
|---|---|---|---|---|---|
| 3/5 (木) | 12:00 | | | 台湾 vs オーストラリア | |
| | 19:00 | | | チェコ vs 韓国 | |
| 3/6 (金) | 12:00 | | | オーストラリア vs チェコ | |
| | 19:00 | | | 日本 vs 台湾 | |
| 3/7 (土) | 1:00 | キューバ vs パナマ (3/6 12pm) | | | |
| | 2:00 | | | | オランダ vs ベネズエラ (3/6 12pm) |
| | 3:00 | | メキシコ vs イギリス (3/6 12pm) | | |
| | 8:00 | プエルトリコ vs コロンビア (3/6 7pm) | | | |
| | 9:00 | | | | ニカラグア vs ドミニカ (3/6 7pm) |
| | 10:00 | | アメリカ vs ブラジル (3/6 7pm) | | |
| | 12:00 | | | 台湾 vs チェコ | |
| | 19:00 | | | 韓国 vs 日本 | |
| 3/8 (日) | 1:00 | コロンビア vs カナダ (3/7 12pm) | | | |
| | 2:00 | | | | ニカラグア vs オランダ (3/7 12pm) |
| | 3:00 | | ブラジル vs イタリア (3/7 12pm) | | |
| | 8:00 | パナマ vs プエルトリコ (3/7 7pm) | | | |
| | 9:00 | | | | イスラエル vs ベネズエラ (3/7 7pm) |
| | 10:00 | | イギリス vs アメリカ (3/7 7pm) | | |
| | 12:00 | | | 台湾 vs 韓国 | |
| | 19:00 | | | オーストラリア vs 日本 | |
| 3/9 (月) | 1:00 | コロンビア vs キューバ (3/8 12pm) | | | オランダ vs ドミニカ (3/8 12pm) |
| | 2:00 | | イギリス vs イタリア (3/8 12pm) | | |
| | 8:00 | パナマ vs カナダ (3/8 7pm) | | | ニカラグア vs イスラエル (3/8 7pm) |
| | 9:00 | | ブラジル vs メキシコ (3/8 7pm) | | |
| | 19:00 | | | 韓国 vs オーストラリア | |
| 3/10 (火) | 1:00 | コロンビア vs パナマ (3/9 12pm) | | | ドミニカ vs イスラエル (3/9 12pm) |
| | 2:00 | | ブラジル vs イギリス (3/9 12pm) | | |
| | 8:00 | キューバ vs プエルトリコ (3/9 7pm) | | | ベネズエラ vs ニカラグア (3/9 7pm) |
| | 9:00 | | メキシコ vs アメリカ (3/9 7pm) | | |
| | 19:00 | | | チェコ vs 日本 | |
| 3/11 (水) | 8:00 | カナダ vs プエルトリコ (3/10 7pm) | | | イスラエル vs オランダ (3/10 7pm) |
| | 10:00 | | イタリア vs アメリカ (3/10 8pm) | | |
| 3/12 (木) | 4:00 | カナダ vs キューバ (3/11 3pm) | | | |
| | 8:00 | | イタリア vs メキシコ (3/11 6pm) | | |
| | 9:00 | | | | ドミニカ vs ベネズエラ (3/11 8pm) |

### 決勝トーナメント

| 日付 (JST) | JST | ラウンド | 会場 | US現地 |
|---|---|---|---|---|
| 3/14 (土) | 7:30 | 準々決勝 | Houston | 3/13 5:30pm CT |
| | 9:00 | 準々決勝 | Miami | 3/13 8:00pm ET |
| 3/15 (日) | 4:00 | 準々決勝 | Houston | 3/14 2:00pm CT |
| | 10:00 | 準々決勝 | Miami | 3/14 9:00pm ET |
| 3/16 (月) | 9:00 | 準決勝 | Miami | 3/15 8:00pm ET |
| 3/17 (火) | 9:00 | 準決勝 | Miami | 3/16 8:00pm ET |
| 3/18 (水) | 9:00 | 決勝 | Miami | 3/17 8:00pm ET |

</details>

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
> - Czechia: MLB/MiLB 組織所属選手なしのためダッシュボードなし
> - Brazil: アプリは作成済み（`app_bra.py` / `app_bra_pitchers.py`）だが Streamlit Cloud 未デプロイ
> - Cuba / Nicaragua / Chinese Taipei / Australia: 投手アプリ未作成（投手の Statcast データは取得済み）

---

## 📊 機能

### 打者ダッシュボード
- **注目打者 TOP3** — OPS上位3選手のカードに**ミニレーダーチャート**（MLB平均ラインつき）を表示。選手選択不要で一目で比較できる
- **チーム打線レーダーチャート** — AVG・OBP・SLG・K%・BB%の5軸、MLB平均ライン（灰色破線）重ね表示
- チーム Overview（主要打撃指標一覧、折りたたみ式）
- **選手別詳細レーダーチャート** — 個人成績をMLB平均と視覚比較（Scouting Summary直後に表示）
- 主要指標にMLB平均値を並記（例: `+.015 (MLB avg: .243)`）
- ゾーンヒートマップ（5×5・3×3、縦並び表示でモバイル対応）
- スプレーチャート（全打球 / vs LHP / vs RHP）
- カウント別パフォーマンス（0-0〜3-2 全カウント）
- 各セクションに用語キャプション付き（野球に詳しくなくても読める）

### 投手ダッシュボード
- **注目投手 TOP3** — K%上位3選手のカードに**ミニレーダーチャート**（MLB平均ラインつき）を表示
- **チーム投手陣レーダーチャート** — K%（奪三振率）・Whiff%（空振り率）・BB%（四球率）・被打率・xwOBA（被打球の期待出塁率）・球速の6軸、MLB平均ライン重ね表示
- チーム Overview（主要投球指標一覧、折りたたみ式）
- **選手別詳細レーダーチャート** — 6軸でMLB平均と視覚比較（Scouting Summary直後）
- 主要指標にMLB平均値を並記（Opp AVG / Opp SLG / K% / BB% / xwOBA）
- 球種別成績テーブル（球速 mph + km/h）、変化量チャート
- 配球ヒートマップ（縦並び表示、球種フィルター連動）
- 左右打者別成績、カウント別パフォーマンス・球種配分チャート
- 球種フィルター（全セクション連動）
- 各セクションに用語キャプション付き

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
