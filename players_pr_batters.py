"""Puerto Rico WBC 2026 roster — MLB batters."""

# Note: Edwin Arroyo (Reds SS) and Bryan Torres (Cardinals OF) are minor-league
# prospects without confirmed MLBAM IDs and are excluded from this list.

PR_BATTERS = [
    {"name": "Nolan Arenado",    "name_ja": "ノーラン・アレナド",     "mlbam_id": 571448, "pos": "3B",  "team": "Diamondbacks", "bats": "R"},
    {"name": "Willi Castro",     "name_ja": "ウィリー・カストロ",     "mlbam_id": 650489, "pos": "LF",  "team": "Rockies",      "bats": "S"},
    {"name": "Carlos Cortes",    "name_ja": "カルロス・コルテス",     "mlbam_id": 666126, "pos": "LF",  "team": "Athletics",    "bats": "L"},
    {"name": "Darrell Hernáiz",  "name_ja": "ダレル・エルナイス",     "mlbam_id": 687231, "pos": "3B",  "team": "Athletics",    "bats": "R"},
    {"name": "Matthew Lugo",     "name_ja": "マシュー・ルーゴ",       "mlbam_id": 683090, "pos": "CF",  "team": "Angels",       "bats": "R"},
    {"name": "Heliot Ramos",     "name_ja": "ヘリオット・ラモス",     "mlbam_id": 671218, "pos": "RF",  "team": "Giants",       "bats": "R"},
    {"name": "Luis Vázquez",     "name_ja": "ルイス・バスケス",       "mlbam_id": 676679, "pos": "SS",  "team": "Orioles",      "bats": "R"},
]

# Lookup helpers
PLAYER_BY_ID = {p["mlbam_id"]: p for p in PR_BATTERS}
PLAYER_BY_NAME = {p["name"]: p for p in PR_BATTERS}
