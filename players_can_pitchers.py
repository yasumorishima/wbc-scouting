"""WBC 2026 Canada roster — MLB pitchers."""

CAN_PITCHERS = [
    {"name": "Micah Ashman",                "name_ja": "マイカ・アッシュマン",     "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Eric Cerantola",              "name_ja": "エリック・セランターラ",   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Indigo Diaz",                 "name_ja": "インディゴ・ディアス",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Antoine Jean",                "name_ja": "アントワーヌ・ジャン",     "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Carter Loewen",               "name_ja": "カーター・ローウェン",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Adam Macko",                  "name_ja": "アダム・マッコ",           "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Cal Quantrill",               "name_ja": "キャル・クアントリル",     "mlbam_id": 615698, "team": "", "throws": "R", "role": "RP"},
    {"name": "Michael Soroka",              "name_ja": "マイケル・ソローカ",       "mlbam_id": 647336, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jameson Taillon",             "name_ja": "ジェイムソン・タイヨン",   "mlbam_id": 592791, "team": "", "throws": "R", "role": "RP"},
    {"name": "Matt Wilkinson",              "name_ja": "マット・ウィルキンソン",   "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Rob Zastryzny",               "name_ja": "ロブ・ザストリズニー",     "mlbam_id": 642239, "team": "", "throws": "L", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in CAN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in CAN_PITCHERS}
