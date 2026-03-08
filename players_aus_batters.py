"""WBC 2026 Australia roster — MLB batters."""

AUS_BATTERS = [
    {"name": "Travis Bazzana",              "name_ja": "トラビス・バザーナ",       "mlbam_id": 683953, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Max Durrington",              "name_ja": "マックス・ダリントン",     "mlbam_id": 828589, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Curtis Mead",                 "name_ja": "カーティス・ミード",       "mlbam_id": 678554, "pos": "IF", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in AUS_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in AUS_BATTERS}
