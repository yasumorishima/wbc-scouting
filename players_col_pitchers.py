"""WBC 2026 Colombia roster — MLB pitchers."""

COL_PITCHERS = [
    {"name": "Austin Bergner",              "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Nabil Crismatt",              "mlbam_id": 622503, "team": "", "throws": "R", "role": "RP"},
    {"name": "Tayron Guerrero",             "mlbam_id": 594027, "team": "", "throws": "R", "role": "RP"},
    {"name": "David Lorduy",                "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Reiver Sanmartín",            "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Guillo Zuñiga",               "mlbam_id": 670871, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in COL_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in COL_PITCHERS}
