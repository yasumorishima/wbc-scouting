"""WBC 2026 Australia roster — MLB batters."""

AUS_BATTERS = [
    {"name": "Travis Bazzana",              "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Max Durrington",              "mlbam_id": 0, "pos": "UTL", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Curtis Mead",                 "mlbam_id": 678554, "pos": "IF", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in AUS_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in AUS_BATTERS}
