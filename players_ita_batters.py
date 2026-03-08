"""WBC 2026 Italy roster — MLB batters."""

ITA_BATTERS = [
    {"name": "Sam Antonacci",               "name_ja": "サム・アントナッチ",       "mlbam_id": 803011, "pos": "IF", "team": "", "bats": "R"},
    {"name": "Jac Caglianone",              "name_ja": "ジャック・カリアノーネ",   "mlbam_id": 695506, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Dominic Canzone",             "name_ja": "ドミニク・カンゾーネ",     "mlbam_id": 686527, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Zach Dezenzo",                "name_ja": "ザック・デゼンゾ",         "mlbam_id": 701305, "pos": "IF", "team": "", "bats": "R"},
    {"name": "Andrew Fischer",              "name_ja": "アンドリュー・フィッシャー","mlbam_id": 702652, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Jakob Marsee",                "name_ja": "ジェイコブ・マーシー",     "mlbam_id": 805300, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Miles Mastrobuoni",           "name_ja": "マイルズ・マストロブオーニ","mlbam_id": 670156, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Nick Morabito",               "name_ja": "ニック・モラビト",         "mlbam_id": 703492, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Dante Nori",                  "name_ja": "ダンテ・ノリ",             "mlbam_id": 807276, "pos": "OF", "team": "", "bats": "R"},
    {"name": "Vinnie Pasquantino",          "name_ja": "ビニー・パスクアンティーノ","mlbam_id": 686469, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Thomas Saggese",              "name_ja": "トーマス・サジェーゼ",     "mlbam_id": 695336, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Kyle Teel",                   "name_ja": "カイル・ティール",         "mlbam_id": 691019, "pos": "C", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in ITA_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in ITA_BATTERS}
