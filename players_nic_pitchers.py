"""WBC 2026 Nicaragua roster — MLB pitchers."""

NIC_PITCHERS = [
    {"name": "Stiven Cruz",                 "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Duque Hebbert",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Oscar Rayo",                  "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Carlos Rodríguez",            "mlbam_id": 121349, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in NIC_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in NIC_PITCHERS}
