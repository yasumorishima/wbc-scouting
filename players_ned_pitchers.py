"""WBC 2026 Netherlands roster — MLB pitchers."""

NED_PITCHERS = [
    {"name": "Jamdrick Cornelia",           "name_ja": "ジャムドリック・コルネリア","mlbam_id": 808378, "team": "", "throws": "L", "role": "RP"},
    {"name": "Jaydenn Estanista",           "name_ja": "ジェイデン・エスタニスタ", "mlbam_id": 692838, "team": "", "throws": "R", "role": "RP"},
    {"name": "Kenley Jansen",               "name_ja": "ケンリー・ジャンセン",     "mlbam_id": 445276, "team": "", "throws": "R", "role": "RP"},
    {"name": "Antwone Kelly",               "name_ja": "アントワン・ケリー",       "mlbam_id": 699008, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jaitoine Kelly",              "name_ja": "ジェイトワン・ケリー",     "mlbam_id": 823858, "team": "", "throws": "R", "role": "RP"},
    {"name": "Ryjeteri Merite",             "name_ja": "ライジェテリ・メリテ",     "mlbam_id": 820853, "team": "", "throws": "L", "role": "RP"},
    {"name": "Shawndrick Oduber",           "name_ja": "ショーンドリック・オドゥバー","mlbam_id": 806779, "team": "", "throws": "R", "role": "RP"},
    {"name": "Dylan Wilson",                "name_ja": "ディラン・ウィルソン",     "mlbam_id": 808511, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in NED_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in NED_PITCHERS}
