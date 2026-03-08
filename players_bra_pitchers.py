"""WBC 2026 Brazil roster — MLB pitchers."""

BRA_PITCHERS = [
    {"name": "Pietro Albanez",              "name_ja": "ピエトロ・アルバネス",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # No MLBAM ID yet (signed Jan 2026)
    {"name": "Gabriel Barbosa",             "name_ja": "ガブリエル・バルボーザ",   "mlbam_id": 682858, "team": "", "throws": "R", "role": "RP"},
    {"name": "Pedro Lemos",                 "name_ja": "ペドロ・レモス",           "mlbam_id": 692038, "team": "", "throws": "R", "role": "RP"},
    {"name": "Daniel Missaki",              "name_ja": "ダニエル・ミッサキ",       "mlbam_id": 627392, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in BRA_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in BRA_PITCHERS}
