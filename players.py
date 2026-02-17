"""Venezuela WBC 2026 roster — MLB batters & pitchers."""

VENEZUELA_BATTERS = [
    {"name": "Ronald Acuña Jr.",   "name_ja": "ロナルド・アクーニャJr.",  "mlbam_id": 660670, "pos": "RF",     "team": "Braves",   "bats": "R"},
    {"name": "Wilyer Abreu",       "name_ja": "ウィルヤー・アブレウ",     "mlbam_id": 677800, "pos": "RF",     "team": "Red Sox",   "bats": "L"},
    {"name": "Luis Arráez",        "name_ja": "ルイス・アラエス",         "mlbam_id": 650333, "pos": "1B",     "team": "Giants",    "bats": "L"},
    {"name": "Jackson Chourio",    "name_ja": "ジャクソン・チュリオ",     "mlbam_id": 694192, "pos": "CF",     "team": "Brewers",   "bats": "R"},
    {"name": "Willson Contreras",  "name_ja": "ウィルソン・コントレラス", "mlbam_id": 575929, "pos": "1B",     "team": "Red Sox",   "bats": "R"},
    {"name": "William Contreras",  "name_ja": "ウィリアム・コントレラス", "mlbam_id": 661388, "pos": "C",      "team": "Brewers",   "bats": "S"},
    {"name": "Maikel Garcia",      "name_ja": "マイケル・ガルシア",       "mlbam_id": 672580, "pos": "3B",     "team": "Royals",    "bats": "R"},
    {"name": "Andrés Giménez",     "name_ja": "アンドレス・ヒメネス",     "mlbam_id": 665926, "pos": "2B/SS",  "team": "Blue Jays", "bats": "L"},
    {"name": "Salvador Perez",     "name_ja": "サルバドール・ペレス",     "mlbam_id": 521692, "pos": "C",      "team": "Royals",    "bats": "R"},
    {"name": "Javier Sanoja",      "name_ja": "ハビエル・サノハ",         "mlbam_id": 691594, "pos": "UTL",    "team": "Marlins",   "bats": "R"},
    {"name": "Eugenio Suárez",     "name_ja": "エウヘニオ・スアレス",     "mlbam_id": 553993, "pos": "3B",     "team": "Reds",      "bats": "R"},
    {"name": "Gleyber Torres",     "name_ja": "グレイバー・トーレス",     "mlbam_id": 650402, "pos": "2B",     "team": "Tigers",    "bats": "R"},
    {"name": "Ezequiel Tovar",     "name_ja": "エゼキエル・トバー",       "mlbam_id": 678662, "pos": "SS",     "team": "Rockies",   "bats": "R"},
]

VENEZUELA_PITCHERS = [
    {"name": "Jose Alvarado",       "name_ja": "ホセ・アルバラード",       "mlbam_id": 621237, "team": "Phillies",       "throws": "L", "role": "RP"},
    {"name": "Eduard Bazardo",      "name_ja": "エドゥアルド・バサルド",   "mlbam_id": 660825, "team": "Mariners",       "throws": "R", "role": "RP"},
    {"name": "José Buttó",          "name_ja": "ホセ・ブット",             "mlbam_id": 676130, "team": "Giants",         "throws": "R", "role": "RP"},
    {"name": "Enmanuel De Jesus",   "name_ja": "エンマヌエル・デ・ヘスス", "mlbam_id": 646241, "team": "Tigers",         "throws": "L", "role": "RP"},
    {"name": "Yoendrys Gómez",      "name_ja": "ヨエンドリス・ゴメス",     "mlbam_id": 672782, "team": "Rays",           "throws": "R", "role": "RP"},
    {"name": "Carlos Guzman",       "name_ja": "カルロス・グスマン",       "mlbam_id": 664346, "team": "Mets",           "throws": "R", "role": "RP"},
    {"name": "Pablo López",         "name_ja": "パブロ・ロペス",           "mlbam_id": 641154, "team": "Twins",          "throws": "R", "role": "SP"},
    {"name": "Keider Montero",      "name_ja": "ケイダー・モンテロ",       "mlbam_id": 672456, "team": "Tigers",         "throws": "R", "role": "SP"},
    {"name": "Daniel Palencia",     "name_ja": "ダニエル・パレンシア",     "mlbam_id": 694037, "team": "Cubs",           "throws": "R", "role": "RP"},
    {"name": "Eduardo Rodríguez",   "name_ja": "エドゥアルド・ロドリゲス", "mlbam_id": 593958, "team": "Diamondbacks",   "throws": "L", "role": "SP"},
    {"name": "Antonio Senzatela",   "name_ja": "アントニオ・センサテーラ", "mlbam_id": 622608, "team": "Rockies",        "throws": "R", "role": "SP"},
    {"name": "Ranger Suárez",       "name_ja": "レンジャー・スアレス",     "mlbam_id": 624133, "team": "Red Sox",        "throws": "L", "role": "SP"},
    {"name": "Angel Zerpa",         "name_ja": "アンヘル・セルパ",         "mlbam_id": 672582, "team": "Brewers",        "throws": "L", "role": "RP"},
]
# Note: Oddanier Mosqueda (LHP, Pirates) excluded — no Statcast data (minor league)

# Lookup helpers — batters
PLAYER_BY_ID = {p["mlbam_id"]: p for p in VENEZUELA_BATTERS}
PLAYER_BY_NAME = {p["name"]: p for p in VENEZUELA_BATTERS}

# Lookup helpers — pitchers
PITCHER_BY_ID = {p["mlbam_id"]: p for p in VENEZUELA_PITCHERS}
PITCHER_BY_NAME = {p["name"]: p for p in VENEZUELA_PITCHERS}
