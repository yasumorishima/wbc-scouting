"""Puerto Rico WBC 2026 roster — MLB pitchers."""

# Note: Luis Quinones (Twins), Eduardo Rivera (Red Sox), Elmer Rodriguez (Yankees),
# and Ricardo Velez (Rangers) are minor-league prospects without confirmed MLBAM IDs
# and are excluded from this list.

PR_PITCHERS = [
    {"name": "Fernando Cruz",  "name_ja": "フェルナンド・クルーズ",   "mlbam_id": 518585, "team": "Yankees",  "throws": "R", "role": "RP"},
    {"name": "Edwin Díaz",     "name_ja": "エドウィン・ディアス",     "mlbam_id": 621242, "team": "Dodgers",  "throws": "R", "role": "RP"},
    {"name": "José Espada",    "name_ja": "ホセ・エスパダ",           "mlbam_id": 664744, "team": "Orioles",  "throws": "R", "role": "RP"},
    {"name": "Rico Garcia",    "name_ja": "リコ・ガルシア",           "mlbam_id": 670329, "team": "Orioles",  "throws": "R", "role": "RP"},
    {"name": "Seth Lugo",      "name_ja": "セス・ルーゴ",             "mlbam_id": 607625, "team": "Royals",   "throws": "R", "role": "SP"},
    {"name": "Jovani Morán",   "name_ja": "ホバニ・モラン",           "mlbam_id": 663558, "team": "Red Sox",  "throws": "L", "role": "RP"},
    {"name": "Yacksel Ríos",   "name_ja": "ヤクセル・リオス",         "mlbam_id": 605441, "team": "Cubs",     "throws": "R", "role": "RP"},
]

# Lookup helpers
PITCHER_BY_ID = {p["mlbam_id"]: p for p in PR_PITCHERS}
PITCHER_BY_NAME = {p["name"]: p for p in PR_PITCHERS}
