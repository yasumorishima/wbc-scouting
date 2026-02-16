"""WBC 2026 Great Britain roster — MLB batters."""

GB_BATTERS = [
    {"name": "Jazz Chisholm Jr.",           "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Willis Cresswell",            "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Nate Eaton",                  "mlbam_id": 681987, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Harry Ford",                  "mlbam_id": 695670, "pos": "C", "team": "", "bats": "R"},
    {"name": "Ivan Johnson",                "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Matt Koperniak",              "mlbam_id": 0, "pos": "RF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Ian Lewis Jr.",               "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "BJ Murray",                   "mlbam_id": 0, "pos": "1B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Kristian Robinson",           "mlbam_id": 0, "pos": "CF", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in GB_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in GB_BATTERS}
