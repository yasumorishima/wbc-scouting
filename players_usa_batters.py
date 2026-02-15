"""USA WBC 2026 roster — MLB batters."""

USA_BATTERS = [
    {"name": "Alex Bregman",          "mlbam_id": 608324, "pos": "3B",  "team": "Cubs",          "bats": "R"},
    {"name": "Byron Buxton",          "mlbam_id": 621439, "pos": "CF",  "team": "Twins",         "bats": "R"},
    {"name": "Corbin Carroll",        "mlbam_id": 682998, "pos": "LF",  "team": "Diamondbacks",  "bats": "L"},
    {"name": "Ernie Clement",         "mlbam_id": 676391, "pos": "UTL", "team": "Blue Jays",     "bats": "R"},
    {"name": "Pete Crow-Armstrong",   "mlbam_id": 691718, "pos": "CF",  "team": "Cubs",          "bats": "L"},
    {"name": "Paul Goldschmidt",      "mlbam_id": 502671, "pos": "1B",  "team": "Free Agent",    "bats": "R"},
    {"name": "Bryce Harper",          "mlbam_id": 547180, "pos": "1B",  "team": "Phillies",      "bats": "L"},
    {"name": "Gunnar Henderson",      "mlbam_id": 683002, "pos": "SS",  "team": "Orioles",       "bats": "L"},
    {"name": "Aaron Judge",           "mlbam_id": 592450, "pos": "RF",  "team": "Yankees",       "bats": "R"},
    {"name": "Cal Raleigh",           "mlbam_id": 663728, "pos": "C",   "team": "Mariners",      "bats": "S"},
    {"name": "Kyle Schwarber",        "mlbam_id": 656941, "pos": "DH",  "team": "Phillies",      "bats": "L"},
    {"name": "Will Smith",            "mlbam_id": 669257, "pos": "C",   "team": "Dodgers",       "bats": "R"},
    {"name": "Brice Turang",          "mlbam_id": 668930, "pos": "2B",  "team": "Brewers",       "bats": "L"},
    {"name": "Bobby Witt Jr.",        "mlbam_id": 677951, "pos": "SS",  "team": "Royals",        "bats": "R"},
]

# Lookup helpers
PLAYER_BY_ID = {p["mlbam_id"]: p for p in USA_BATTERS}
PLAYER_BY_NAME = {p["name"]: p for p in USA_BATTERS}
