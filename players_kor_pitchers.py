"""WBC 2026 Korea roster — MLB pitchers."""

KOR_PITCHERS = [
    {"name": "Dane Dunning",                "name_ja": "デイン・ダニング",         "mlbam_id": 641540, "team": "", "throws": "R", "role": "RP"},
    {"name": "Woo Suk Go",                  "name_ja": "コ・ウソク",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Riley O'Brien",               "name_ja": "ライリー・オブライエン",   "mlbam_id": 676617, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in KOR_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in KOR_PITCHERS}
