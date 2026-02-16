"""WBC 2026 Japan roster — MLB pitchers."""

JAPAN_PITCHERS = [
    {"name": "Yoshinobu Yamamoto", "mlbam_id": 808967, "team": "Dodgers", "throws": "R", "role": "SP"},
    {"name": "Yusei Kikuchi",      "mlbam_id": 579328, "team": "Angels",  "throws": "L", "role": "SP"},
    {"name": "Yuki Matsui",        "mlbam_id": 673513, "team": "Padres",  "throws": "L", "role": "RP"},
    {"name": "Tomoyuki Sugano",    "mlbam_id": 608372, "team": "FA",      "throws": "R", "role": "SP"},  # Former Orioles
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in JAPAN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in JAPAN_PITCHERS}
