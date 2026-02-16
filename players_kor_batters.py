"""WBC 2026 Korea roster — MLB batters."""

KOR_BATTERS = [
    {"name": "Jahmai Jones",                "mlbam_id": 663330, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Hyeseong Kim",                "mlbam_id": 808975, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Jung-Hoo Lee",                "mlbam_id": 0, "pos": "CF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Shay Whitcomb",               "mlbam_id": 694376, "pos": "2B", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in KOR_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in KOR_BATTERS}
