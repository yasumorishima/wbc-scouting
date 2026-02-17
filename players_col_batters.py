"""WBC 2026 Colombia roster — MLB batters."""

COL_BATTERS = [
    {"name": "Jorge Alfaro",                "name_ja": "ホルヘ・アルファロ",       "mlbam_id": 595751, "pos": "C", "team": "", "bats": "R"},
    {"name": "Michael Arroyo",              "name_ja": "マイケル・アロヨ",         "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Brayan Buelvas",              "name_ja": "ブラヤン・ブエルバス",     "mlbam_id": 0, "pos": "CF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Gustavo Campero",             "name_ja": "グスタボ・カンペロ",       "mlbam_id": 672569, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Dayan Frias",                 "name_ja": "ダヤン・フリアス",         "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in COL_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in COL_BATTERS}
