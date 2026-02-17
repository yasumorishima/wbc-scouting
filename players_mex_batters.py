"""WBC 2026 Mexico roster — MLB batters."""

MEX_BATTERS = [
    {"name": "Jonathan Aranda",             "name_ja": "ジョナサン・アランダ",     "mlbam_id": 666018, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Randy Arozarena",             "name_ja": "ランディ・アロサレーナ",   "mlbam_id": 668227, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Jarren Duran",                "name_ja": "ジャレン・デュラン",       "mlbam_id": 680776, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Nick Gonzales",               "name_ja": "ニック・ゴンザレス",       "mlbam_id": 693304, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Alejandro Kirk",              "name_ja": "アレハンドロ・カーク",     "mlbam_id": 672386, "pos": "C", "team": "", "bats": "R"},
    {"name": "Joey Meneses",                "name_ja": "ジョーイ・メネセス",       "mlbam_id": 608841, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Joey Ortiz",                  "name_ja": "ジョーイ・オルティス",     "mlbam_id": 687401, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Alejandro Osuna",             "name_ja": "アレハンドロ・オスーナ",   "mlbam_id": 696030, "pos": "RF", "team": "", "bats": "R"},
    {"name": "Jared Serna",                 "name_ja": "ハレド・セルナ",           "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Alek Thomas",                 "name_ja": "アレク・トーマス",         "mlbam_id": 677950, "pos": "CF", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in MEX_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in MEX_BATTERS}
