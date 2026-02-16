"""WBC 2026 Colombia roster — MLB batters."""

COL_BATTERS = [
    {"name": "Jorge Alfaro",                "mlbam_id": 595751, "pos": "C", "team": "", "bats": "R"},
    {"name": "Michael Arroyo",              "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Brayan Buelvas",              "mlbam_id": 0, "pos": "CF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Gustavo Campero",             "mlbam_id": 672569, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Dayan Frias",                 "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in COL_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in COL_BATTERS}
