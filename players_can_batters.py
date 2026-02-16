"""WBC 2026 Canada roster — MLB batters."""

CAN_BATTERS = [
    {"name": "Tyler Black",                 "mlbam_id": 672012, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Owen Caissie",                "mlbam_id": 683357, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Denzel Clarke",               "mlbam_id": 672016, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Liam Hicks",                  "mlbam_id": 689414, "pos": "C", "team": "", "bats": "R"},
    {"name": "Edouard Julien",              "mlbam_id": 666397, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Otto López",                  "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Josh Naylor",                 "mlbam_id": 647304, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Bo Naylor",                   "mlbam_id": 666310, "pos": "C", "team": "", "bats": "R"},
    {"name": "Tyler O'Neill",               "mlbam_id": 641933, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Abraham Toro",                "mlbam_id": 647351, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Jared Young",                 "mlbam_id": 676724, "pos": "UTL", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in CAN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in CAN_BATTERS}
