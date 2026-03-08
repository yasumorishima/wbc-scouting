"""WBC 2026 Chinese Taipei roster — MLB batters."""

TWN_BATTERS = [
    {"name": "Tsung-Che Cheng",             "name_ja": "鄭宗哲",                   "mlbam_id": 691907, "pos": "SS", "team": "", "bats": "R"},
    {"name": "Stuart Fairchild",            "name_ja": "スチュアート・フェアチャイルド","mlbam_id": 656413, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Hao-Yu Lee",                  "name_ja": "李灝宇",                   "mlbam_id": 701678, "pos": "IF", "team": "", "bats": "R"},
    {"name": "Jonathon Long",               "name_ja": "ジョナサン・ロング",       "mlbam_id": 675085, "pos": "1B", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in TWN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in TWN_BATTERS}
