"""WBC 2026 Australia roster — MLB batters."""

AUS_BATTERS = [
    {"name": "Travis Bazzana",              "name_ja": "トラビス・バザーナ",       "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Max Durrington",              "name_ja": "マックス・ダリントン",     "mlbam_id": 0, "pos": "UTL", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Curtis Mead",                 "name_ja": "カーティス・ミード",       "mlbam_id": 678554, "pos": "IF", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in AUS_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in AUS_BATTERS}
