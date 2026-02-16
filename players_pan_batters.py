"""WBC 2026 Panama roster — MLB batters."""

PAN_BATTERS = [
    {"name": "Miguel Amaya",                "mlbam_id": 665804, "pos": "C", "team": "", "bats": "R"},
    {"name": "Leo Bernal",                  "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Christian Bethancourt",       "mlbam_id": 542194, "pos": "C/1B", "team": "", "bats": "R"},
    {"name": "Enrique Bradfield",           "mlbam_id": 0, "pos": "CF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "José Caballero",              "mlbam_id": 676609, "pos": "IF", "team": "", "bats": "R"},
    {"name": "Ivan Herrera",                "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Leo Jiménez",                 "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Jose Ramos",                  "mlbam_id": 0, "pos": "OF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Edmundo Sosa",                "mlbam_id": 624641, "pos": "2B", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in PAN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in PAN_BATTERS}
