"""WBC 2026 Panama roster — MLB batters."""

PAN_BATTERS = [
    {"name": "Miguel Amaya",                "name_ja": "ミゲル・アマヤ",           "mlbam_id": 665804, "pos": "C", "team": "", "bats": "R"},
    {"name": "Leo Bernal",                  "name_ja": "レオ・ベルナル",           "mlbam_id": 699024, "pos": "C", "team": "", "bats": "R"},
    {"name": "Christian Bethancourt",       "name_ja": "クリスチャン・ベタンコート","mlbam_id": 542194, "pos": "C/1B", "team": "", "bats": "R"},
    {"name": "Enrique Bradfield",           "name_ja": "エンリケ・ブラッドフィールド","mlbam_id": 690961, "pos": "CF", "team": "", "bats": "R"},
    {"name": "José Caballero",              "name_ja": "ホセ・カバジェロ",         "mlbam_id": 676609, "pos": "IF", "team": "", "bats": "R"},
    {"name": "Ivan Herrera",                "name_ja": "イバン・エレーラ",         "mlbam_id": 671056, "pos": "C", "team": "STL", "bats": "R"},
    {"name": "Leo Jiménez",                 "name_ja": "レオ・ヒメネス",           "mlbam_id": 677870, "pos": "SS", "team": "", "bats": "R"},
    {"name": "Jose Ramos",                  "name_ja": "ホセ・ラモス",             "mlbam_id": 682947, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Edmundo Sosa",                "name_ja": "エドムンド・ソーサ",       "mlbam_id": 624641, "pos": "2B", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in PAN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in PAN_BATTERS}
