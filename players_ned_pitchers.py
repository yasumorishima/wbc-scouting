"""WBC 2026 Netherlands roster — MLB pitchers."""

NED_PITCHERS = [
    {"name": "Jamdrick Cornelia",           "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Jaydenn Estanista",           "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Kenley Jansen",               "mlbam_id": 445276, "team": "", "throws": "R", "role": "RP"},
    {"name": "Antwone Kelly",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Jaitoine Kelly",              "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Ryjeteri Merite",             "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Shawndrick Oduber",           "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Dylan Wilson",                "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in NED_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in NED_PITCHERS}
