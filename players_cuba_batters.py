"""WBC 2026 Cuba roster — MLB batters."""

CUBA_BATTERS = [
    {"name": "Yiddi Cappe",                 "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Omar Hernandez",              "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Yoán Moncada",                "mlbam_id": 660162, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Alexander Vargas",            "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in CUBA_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in CUBA_BATTERS}
