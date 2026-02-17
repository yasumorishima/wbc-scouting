"""WBC 2026 Great Britain roster — MLB pitchers."""

GB_PITCHERS = [
    {"name": "Jack Anderson",               "name_ja": "ジャック・アンダーソン",   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Brendan Beck",                "name_ja": "ブレンダン・ベック",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Tristan Beck",                "name_ja": "トリスタン・ベック",       "mlbam_id": 663941, "team": "", "throws": "R", "role": "RP"},
    {"name": "Gary Gill Hill",              "name_ja": "ゲイリー・ギル・ヒル",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Antonio Knowles",             "name_ja": "アントニオ・ノールズ",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Miles Langhorne",             "name_ja": "マイルズ・ラングホーン",   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Ryan Long",                   "name_ja": "ライアン・ロング",         "mlbam_id": 117899, "team": "", "throws": "R", "role": "RP"},
    {"name": "Michael Petersen",            "name_ja": "マイケル・ピーターセン",   "mlbam_id": 656848, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jack Seppings",               "name_ja": "ジャック・セッピングス",   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Najer Victor",                "name_ja": "ネイジャー・ビクター",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Owen Wild",                   "name_ja": "オーウェン・ワイルド",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in GB_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in GB_PITCHERS}
