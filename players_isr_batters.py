"""WBC 2026 Israel roster — MLB batters."""

ISR_BATTERS = [
    {"name": "Harrison Bader",              "name_ja": "ハリソン・ベイダー",       "mlbam_id": 664056, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Cole Carrigg",                "name_ja": "コール・キャリグ",         "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Jake Gelof",                  "name_ja": "ジェイク・ジェロフ",       "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Spencer Horwitz",             "name_ja": "スペンサー・ホーウィッツ", "mlbam_id": 687462, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Troy Johnston",               "name_ja": "トロイ・ジョンストン",     "mlbam_id": 687859, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Zach Levenson",               "name_ja": "ザック・レベンソン",       "mlbam_id": 0, "pos": "RF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Noah Mendlinger",             "name_ja": "ノア・メンドリンガー",     "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Matt Mervis",                 "name_ja": "マット・マービス",         "mlbam_id": 670223, "pos": "1B", "team": "", "bats": "R"},
    {"name": "RJ Schreck",                  "name_ja": "RJ・シュレック",           "mlbam_id": 0, "pos": "LF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Garrett Stubbs",              "name_ja": "ギャレット・スタッブス",   "mlbam_id": 596117, "pos": "C", "team": "", "bats": "R"},
    {"name": "CJ Stubbs",                   "name_ja": "CJ・スタッブス",           "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in ISR_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in ISR_BATTERS}
