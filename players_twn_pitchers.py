"""WBC 2026 Chinese Taipei roster — MLB pitchers."""

TWN_PITCHERS = [
    {"name": "Po-Yu Chen",                  "mlbam_id": 696040, "team": "", "throws": "R", "role": "RP"},
    {"name": "Wei-En Lin",                  "mlbam_id": 827734, "team": "", "throws": "L", "role": "RP"},
    {"name": "Yu-Min Lin",                  "mlbam_id": 801179, "team": "", "throws": "L", "role": "RP"},
    {"name": "Tzu-Chen Sha",                "mlbam_id": 809223, "team": "", "throws": "R", "role": "RP"},
    {"name": "Chen Zhong-Ao Zhuang",        "mlbam_id": 800018, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in TWN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in TWN_PITCHERS}
