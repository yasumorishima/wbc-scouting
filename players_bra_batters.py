"""WBC 2026 Brazil roster — MLB batters."""

BRA_BATTERS = [
    {"name": "Lucas Ramirez",               "mlbam_id": 0, "pos": "OF", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in BRA_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in BRA_BATTERS}
