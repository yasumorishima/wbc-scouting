"""WBC 2026 Nicaragua roster — MLB pitchers."""

NIC_PITCHERS = [
    {"name": "Stiven Cruz",                 "mlbam_id": 691602, "team": "", "throws": "R", "role": "RP"},
    {"name": "Duque Hebbert",               "mlbam_id": 808986, "team": "", "throws": "R", "role": "RP"},
    {"name": "Oscar Rayo",                  "mlbam_id": 699325, "team": "", "throws": "L", "role": "RP"},
    {"name": "Carlos Rodríguez",            "mlbam_id": 121349, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in NIC_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in NIC_PITCHERS}
