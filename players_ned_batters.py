"""WBC 2026 Netherlands roster — MLB batters."""

NED_BATTERS = [
    {"name": "Ozzie Albies",                "mlbam_id": 645277, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Xander Bogaerts",             "mlbam_id": 593428, "pos": "SS", "team": "", "bats": "R"},
    {"name": "Dayson Croes",                "mlbam_id": 0, "pos": "OF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Druw Jones",                  "mlbam_id": 0, "pos": "OF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Jurickson Profar",            "mlbam_id": 595777, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Ceddanne Rafaela",            "mlbam_id": 678882, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Chadwick Tromp",              "mlbam_id": 644433, "pos": "C", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in NED_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in NED_BATTERS}
