"""WBC 2026 Cuba roster — MLB pitchers."""

CUBA_PITCHERS = [
    {"name": "Emmanuel Chapman",            "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Naykel Cruz",                 "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Daviel Hurtado",              "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Yariel Rodriguez",            "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in CUBA_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in CUBA_PITCHERS}
