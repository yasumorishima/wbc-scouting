"""WBC 2026 Nicaragua roster — MLB batters."""

NIC_BATTERS = [
    {"name": "Ismael Munguia",              "name_ja": "イスマエル・ムンギア",     "mlbam_id": 0, "pos": "CF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Mark Vientos",                "name_ja": "マーク・ビエントス",       "mlbam_id": 668901, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Freddy Zamora",               "name_ja": "フレディ・サモラ",         "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in NIC_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in NIC_BATTERS}
