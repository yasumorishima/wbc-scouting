"""WBC 2026 Mexico roster — MLB pitchers."""

MEX_PITCHERS = [
    {"name": "Javier Assad",                "mlbam_id": 665871, "team": "", "throws": "R", "role": "RP"},
    {"name": "Brennan Bernardino",          "mlbam_id": 657514, "team": "", "throws": "L", "role": "RP"},
    {"name": "Taj Bradley",                 "mlbam_id": 671737, "team": "", "throws": "R", "role": "RP"},
    {"name": "Alex Carrillo",               "mlbam_id": 692024, "team": "", "throws": "R", "role": "RP"},
    {"name": "Daniel Duarte",               "mlbam_id": 650960, "team": "", "throws": "R", "role": "RP"},
    {"name": "Robert Garcia",               "mlbam_id": 676395, "team": "", "throws": "L", "role": "RP"},
    {"name": "Luis Gastelum",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Andrés Muñoz",                "mlbam_id": 662253, "team": "", "throws": "R", "role": "RP"},
    {"name": "Samy Natera Jr.",             "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Victor Vodnik",               "mlbam_id": 680767, "team": "", "throws": "R", "role": "RP"},
    {"name": "Taijuan Walker",              "mlbam_id": 592836, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in MEX_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in MEX_PITCHERS}
