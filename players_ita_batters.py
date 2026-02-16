"""WBC 2026 Italy roster — MLB batters."""

ITA_BATTERS = [
    {"name": "Sam Antonacci",               "mlbam_id": 0, "pos": "IF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Jac Caglianone",              "mlbam_id": 695506, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Dominic Canzone",             "mlbam_id": 686527, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Zach Dezenzo",                "mlbam_id": 701305, "pos": "IF", "team": "", "bats": "R"},
    {"name": "Andrew Fischer",              "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Jakob Marsee",                "mlbam_id": 805300, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Miles Mastrobuoni",           "mlbam_id": 670156, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Nick Morabito",               "mlbam_id": 0, "pos": "OF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Dante Nori",                  "mlbam_id": 0, "pos": "OF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Vinnie Pasquantino",          "mlbam_id": 686469, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Thomas Saggese",              "mlbam_id": 695336, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Kyle Teel",                   "mlbam_id": 691019, "pos": "C", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in ITA_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in ITA_BATTERS}
