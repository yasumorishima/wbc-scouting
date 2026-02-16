"""WBC 2026 Mexico roster — MLB batters."""

MEX_BATTERS = [
    {"name": "Jonathan Aranda",             "mlbam_id": 666018, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Randy Arozarena",             "mlbam_id": 668227, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Jarren Duran",                "mlbam_id": 680776, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Nick Gonzales",               "mlbam_id": 693304, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Alejandro Kirk",              "mlbam_id": 672386, "pos": "C", "team": "", "bats": "R"},
    {"name": "Joey Meneses",                "mlbam_id": 608841, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Joey Ortiz",                  "mlbam_id": 687401, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Alejandro Osuna",             "mlbam_id": 696030, "pos": "RF", "team": "", "bats": "R"},
    {"name": "Jared Serna",                 "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Alek Thomas",                 "mlbam_id": 677950, "pos": "CF", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in MEX_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in MEX_BATTERS}
