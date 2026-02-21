"""WBC 2026 Canada roster — MLB batters."""

CAN_BATTERS = [
    {"name": "Tyler Black",                 "name_ja": "タイラー・ブラック",       "mlbam_id": 672012, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Owen Caissie",                "name_ja": "オーウェン・ケイシー",     "mlbam_id": 683357, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Denzel Clarke",               "name_ja": "デンゼル・クラーク",       "mlbam_id": 672016, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Liam Hicks",                  "name_ja": "リアム・ヒックス",         "mlbam_id": 689414, "pos": "C", "team": "", "bats": "R"},
    {"name": "Edouard Julien",              "name_ja": "エドゥアール・ジュリアン", "mlbam_id": 666397, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Otto López",                  "name_ja": "オットー・ロペス",         "mlbam_id": 672640, "pos": "SS", "team": "TOR", "bats": "R"},
    {"name": "Josh Naylor",                 "name_ja": "ジョシュ・ネイラー",       "mlbam_id": 647304, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Bo Naylor",                   "name_ja": "ボー・ネイラー",           "mlbam_id": 666310, "pos": "C", "team": "", "bats": "R"},
    {"name": "Tyler O'Neill",               "name_ja": "タイラー・オニール",       "mlbam_id": 641933, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Abraham Toro",                "name_ja": "エイブラハム・トロ",       "mlbam_id": 647351, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Jared Young",                 "name_ja": "ジャレッド・ヤング",       "mlbam_id": 676724, "pos": "UTL", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in CAN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in CAN_BATTERS}
