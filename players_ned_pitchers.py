"""WBC 2026 Netherlands roster — MLB pitchers."""

NED_PITCHERS = [
    {"name": "Jamdrick Cornelia",           "name_ja": "ジャムドリック・コルネリア","mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Jaydenn Estanista",           "name_ja": "ジェイデン・エスタニスタ", "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Kenley Jansen",               "name_ja": "ケンリー・ジャンセン",     "mlbam_id": 445276, "team": "", "throws": "R", "role": "RP"},
    {"name": "Antwone Kelly",               "name_ja": "アントワン・ケリー",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Jaitoine Kelly",              "name_ja": "ジェイトワン・ケリー",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Ryjeteri Merite",             "name_ja": "ライジェテリ・メリテ",     "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Shawndrick Oduber",           "name_ja": "ショーンドリック・オドゥバー","mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Dylan Wilson",                "name_ja": "ディラン・ウィルソン",     "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in NED_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in NED_PITCHERS}
