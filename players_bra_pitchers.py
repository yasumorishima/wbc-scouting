"""WBC 2026 Brazil roster — MLB pitchers."""

BRA_PITCHERS = [
    {"name": "Pietro Albanez",              "name_ja": "ピエトロ・アルバネス",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Gabriel Barbosa",             "name_ja": "ガブリエル・バルボーザ",   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Pedro Lemos",                 "name_ja": "ペドロ・レモス",           "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Daniel Missaki",              "name_ja": "ダニエル・ミッサキ",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in BRA_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in BRA_PITCHERS}
