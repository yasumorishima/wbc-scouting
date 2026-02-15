# WBC Venezuela Scouting Dashboard — 開発メモ

## 実装状況（2/15更新）

### 完了
- [x] `players.py`: ベネズエラ打者13人 + 投手13人の定義（MLBAM ID確認済み）
- [x] `fetch_data.py`: Statcastデータ取得（打者/投手両対応、`--pitchers`フラグ）
- [x] `app.py`: 打者スカウティングアプリ（Streamlit）
  - Team Overview（全13打者サマリー + OPS/K%カラーグラデーション）
  - 個別レポート: プロフィール / ゾーンヒートマップ / スプレーチャート / 球種別 / プラトーン / カウント別
  - サイドバー: 選手セレクター + シーズンフィルター + EN/JA言語切替
- [x] `app_pitchers.py`: 投手スカウティングアプリ（Streamlit、打者とは別アプリ）
  - Staff Overview（全13投手サマリー + K%/被打率カラーグラデーション）
  - 個別レポート: プロフィール / 球種構成テーブル / 変化量チャート / 配球ヒートマップ / プラトーン / カウント別
- [x] `.streamlit/config.toml`: ダークテーマ設定
- [x] `requirements.txt`
- [x] `.gitignore`
- [x] `data/wbc2026_rosters.csv`: 全20チームMLB選手一覧（Baseball America 2/5発表）

### 完了（2/21）
1. ✅ **打者データ取得**: 56,114行 → `data/venezuela_statcast.csv`
2. ✅ **投手データ取得**: 29,301行 → `data/venezuela_pitchers_statcast.csv`
3. ✅ **GitHub リポジトリ作成・push**: https://github.com/yasumorishima/wbc-scouting（public）
   - cp932エンコードエラー → `PYTHONUTF8=1`で解決
   - CSV大容量push → `git config http.postBuffer 157286400`

### 未完了（次回やること）
1. **Streamlit Community Cloud デプロイ**（ブラウザ操作必要）
   - 打者: `app.py`、投手: `app_pitchers.py`（別アプリとしてデプロイ）
2. **デプロイ後URL追記**（README、Profile README等）
3. **ブログ記事**（任意）

## MLBAM ID一覧

### 打者（13人）
| 選手 | MLBAM ID | Bats | Pos | Team |
|------|----------|------|-----|------|
| Ronald Acuña Jr. | 660670 | R | RF | Braves |
| Wilyer Abreu | 677800 | L | RF | Red Sox |
| Luis Arráez | 650333 | L | 1B | Giants |
| Jackson Chourio | 694192 | R | CF | Brewers |
| Willson Contreras | 575929 | R | 1B | Red Sox |
| William Contreras | 661388 | S | C | Brewers |
| Maikel Garcia | 672580 | R | 3B | Royals |
| Andrés Giménez | 665926 | L | 2B/SS | Blue Jays |
| Salvador Perez | 521692 | R | C | Royals |
| Javier Sanoja | 691594 | R | UTL | Marlins |
| Eugenio Suárez | 553993 | R | 3B | Reds |
| Gleyber Torres | 650402 | R | 2B | Tigers |
| Ezequiel Tovar | 678662 | R | SS | Rockies |

### 投手（13人）
| 選手 | MLBAM ID | Throws | Role | Team |
|------|----------|--------|------|------|
| Jose Alvarado | 621237 | L | RP | Phillies |
| Eduard Bazardo | 660825 | R | RP | Mariners |
| José Buttó | 676130 | R | RP | Giants |
| Enmanuel De Jesus | 646241 | L | RP | Tigers |
| Yoendrys Gómez | 672782 | R | RP | Rays |
| Carlos Guzman | 664346 | R | RP | Mets |
| Pablo López | 641154 | R | SP | Twins |
| Keider Montero | 672456 | R | SP | Tigers |
| Daniel Palencia | 694037 | R | RP | Cubs |
| Eduardo Rodríguez | 593958 | L | SP | Diamondbacks |
| Antonio Senzatela | 622608 | R | SP | Rockies |
| Ranger Suárez | 624133 | L | SP | Red Sox |
| Angel Zerpa | 672582 | L | RP | Brewers |

※ Oddanier Mosqueda (LHP, Pirates) — Statcastデータなし（マイナー）のため除外

## ファイル構造
```
C:\Users\fw_ya\Desktop\Claude_code\wbc-scouting\
├── app.py                     # 打者スカウティングアプリ（約450行）
├── app_pitchers.py            # 投手スカウティングアプリ（約400行）
├── fetch_data.py              # データ取得（打者/投手両対応）
├── players.py                 # 選手定義（打者13人 + 投手13人）
├── DEV_NOTE.md                # この開発メモ
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── .gitignore
└── data/
    ├── wbc2026_rosters.csv              # 全20チームロスター
    ├── (venezuela_statcast.csv)         ← fetch_data.py実行後
    └── (venezuela_pitchers_statcast.csv) ← fetch_data.py --pitchers実行後
```

## 設計方針
- **国ごと・打者/投手ごとに完全に別ファイル構成にする**
- 既存ファイルに他国の選手を追加しない（情報過多を避ける）
- 選手定義ファイルも打者・投手で分離する
- 例: ドミニカ → `players_dr_batters.py` / `players_dr_pitchers.py` / `app_dr.py` / `app_dr_pitchers.py`
- **データ取得はGitHub Actionsで実行**（ローカルPCはRAM 4GBで重いため）
  - ベネズエラ・ドミニカはローカルで取得済み（そのまま使用）
  - アメリカ以降はGitHub Actionsワークフローで取得 → 自動commit/push

## 技術メモ
- ゾーンヒートマップ: plate_x(-1.5~1.5), plate_z(1.0~4.0)を5×5グリッド分割、セルのサンプル数5以上で表示
- スプレーチャート: Statcast座標系（ホームプレート=125.42, 198.27）、フェンスは半径250で描画
- 球種分類: 上位8種を表示、それ以外はOther
- チェイス率: zone >= 11（ゾーン外）でのスイング率
- カウント分類（打者版）: balls > strikes = ahead, strikes > balls = behind, 同じ = even
- カウント分類（投手版）: strikes > balls = ahead（投手有利）, balls > strikes = behind
- 変化量チャート: pfx_x/pfx_z（ft→in変換 ×12）、球種別色分け
- 投手版は打者版と別アプリ（情報過多を避けるため）
