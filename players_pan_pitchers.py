"""WBC 2026 Panama roster — MLB pitchers."""

PAN_PITCHERS = [
    {"name": "Logan Allen",                 "name_ja": "ローガン・アレン",         "mlbam_id": 671106, "team": "", "throws": "L", "role": "RP"},
    {"name": "Miguel Cienfuegos",           "name_ja": "ミゲル・シエンフエゴス",   "mlbam_id": 800550, "team": "", "throws": "L", "role": "RP"},
    {"name": "James González",              "name_ja": "ジェームズ・ゴンサレス",   "mlbam_id": 686857, "team": "", "throws": "L", "role": "RP"},
    {"name": "Javy Guerra",                 "name_ja": "ハビー・ゲーラ",           "mlbam_id": 642770, "team": "", "throws": "R", "role": "RP"},
    {"name": "Abdiel Mendoza",              "name_ja": "アブディエル・メンドーサ", "mlbam_id": 665959, "team": "", "throws": "R", "role": "RP"},
    {"name": "Erian Rodríguez",             "name_ja": "エリアン・ロドリゲス",     "mlbam_id": 701477, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in PAN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in PAN_PITCHERS}
