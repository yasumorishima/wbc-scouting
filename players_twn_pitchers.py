"""WBC 2026 Chinese Taipei roster — MLB pitchers."""

TWN_PITCHERS = [
    {"name": "Po-Yu Chen",                  "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Wei-En Lin",                  "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Yu-Min Lin",                  "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Tzu-Chen Sha",                "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Chen Zhong-Ao Zhuang",        "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in TWN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in TWN_PITCHERS}
