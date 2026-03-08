"""WBC 2026 Cuba roster — MLB batters."""

CUBA_BATTERS = [
    {"name": "Yiddi Cappe",                 "name_ja": "イディ・カッペ",           "mlbam_id": 691268, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Omar Hernandez",              "name_ja": "オマール・エルナンデス",   "mlbam_id": 683427, "pos": "C", "team": "", "bats": "R"},
    {"name": "Yoán Moncada",                "name_ja": "ヨアン・モンカダ",         "mlbam_id": 660162, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Alexander Vargas",            "name_ja": "アレクサンダー・バルガス", "mlbam_id": 683061, "pos": "SS", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in CUBA_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in CUBA_BATTERS}
