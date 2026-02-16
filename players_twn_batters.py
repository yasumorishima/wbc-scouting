"""WBC 2026 Chinese Taipei roster — MLB batters."""

TWN_BATTERS = [
    {"name": "Tsung-Che Cheng",             "mlbam_id": 691907, "pos": "SS", "team": "", "bats": "R"},
    {"name": "Stuart Fairchild",            "mlbam_id": 656413, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Hao-Yu Lee",                  "mlbam_id": 0, "pos": "IF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Jonathon Long",               "mlbam_id": 0, "pos": "1B", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in TWN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in TWN_BATTERS}
