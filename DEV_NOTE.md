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

### 未完了（次回やること）
1. **打者データ取得**: `python fetch_data.py` → `data/venezuela_statcast.csv`
2. **打者アプリ動作確認**: `streamlit run app.py`
3. **投手データ取得**: `python fetch_data.py --pitchers` → `data/venezuela_pitchers_statcast.csv`
4. **投手アプリ動作確認**: `streamlit run app_pitchers.py`
5. **GitHub リポジトリ作成**: `yasumorishima/wbc-scouting`（public）→ CSVごとpush
6. **Streamlit Community Cloud デプロイ**（打者・投手それぞれ or マルチページ化）
7. **ブログ記事**（任意）

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

## 技術メモ
- ゾーンヒートマップ: plate_x(-1.5~1.5), plate_z(1.0~4.0)を5×5グリッド分割、セルのサンプル数5以上で表示
- スプレーチャート: Statcast座標系（ホームプレート=125.42, 198.27）、フェンスは半径250で描画
- 球種分類: 上位8種を表示、それ以外はOther
- チェイス率: zone >= 11（ゾーン外）でのスイング率
- カウント分類（打者版）: balls > strikes = ahead, strikes > balls = behind, 同じ = even
- カウント分類（投手版）: strikes > balls = ahead（投手有利）, balls > strikes = behind
- 変化量チャート: pfx_x/pfx_z（ft→in変換 ×12）、球種別色分け
- 投手版は打者版と別アプリ（情報過多を避けるため）
