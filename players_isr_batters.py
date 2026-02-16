"""WBC 2026 Israel roster — MLB batters."""

ISR_BATTERS = [
    {"name": "Harrison Bader",              "mlbam_id": 664056, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Cole Carrigg",                "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Jake Gelof",                  "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Spencer Horwitz",             "mlbam_id": 687462, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Troy Johnston",               "mlbam_id": 687859, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Zach Levenson",               "mlbam_id": 0, "pos": "RF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Noah Mendlinger",             "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Matt Mervis",                 "mlbam_id": 670223, "pos": "1B", "team": "", "bats": "R"},
    {"name": "RJ Schreck",                  "mlbam_id": 0, "pos": "LF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Garrett Stubbs",              "mlbam_id": 596117, "pos": "C", "team": "", "bats": "R"},
    {"name": "CJ Stubbs",                   "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in ISR_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in ISR_BATTERS}
