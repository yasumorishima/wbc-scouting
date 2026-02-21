"""WBC 2026 Korea roster — MLB batters."""

KOR_BATTERS = [
    {"name": "Jahmai Jones",                "name_ja": "ジャーマイ・ジョーンズ",   "mlbam_id": 663330, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Hyeseong Kim",                "name_ja": "キム・ヘソン",             "mlbam_id": 808975, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Jung-Hoo Lee",                "name_ja": "イ・ジョンフ",             "mlbam_id": 808982, "pos": "CF", "team": "SF", "bats": "L"},
    {"name": "Shay Whitcomb",               "name_ja": "シェイ・ウィットコム",     "mlbam_id": 694376, "pos": "2B", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in KOR_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in KOR_BATTERS}
