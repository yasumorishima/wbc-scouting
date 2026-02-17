"""WBC 2026 Mexico roster — MLB pitchers."""

MEX_PITCHERS = [
    {"name": "Javier Assad",                "name_ja": "ハビエル・アサド",         "mlbam_id": 665871, "team": "", "throws": "R", "role": "RP"},
    {"name": "Brennan Bernardino",          "name_ja": "ブレナン・ベルナルディーノ","mlbam_id": 657514, "team": "", "throws": "L", "role": "RP"},
    {"name": "Taj Bradley",                 "name_ja": "タジ・ブラッドリー",       "mlbam_id": 671737, "team": "", "throws": "R", "role": "RP"},
    {"name": "Alex Carrillo",               "name_ja": "アレックス・カリージョ",   "mlbam_id": 692024, "team": "", "throws": "R", "role": "RP"},
    {"name": "Daniel Duarte",               "name_ja": "ダニエル・ドゥアルテ",     "mlbam_id": 650960, "team": "", "throws": "R", "role": "RP"},
    {"name": "Robert Garcia",               "name_ja": "ロバート・ガルシア",       "mlbam_id": 676395, "team": "", "throws": "L", "role": "RP"},
    {"name": "Luis Gastelum",               "name_ja": "ルイス・ガステルム",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Andrés Muñoz",                "name_ja": "アンドレス・ムニョス",     "mlbam_id": 662253, "team": "", "throws": "R", "role": "RP"},
    {"name": "Samy Natera Jr.",             "name_ja": "サミー・ナテラJr.",        "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Victor Vodnik",               "name_ja": "ビクター・ボドニック",     "mlbam_id": 680767, "team": "", "throws": "R", "role": "RP"},
    {"name": "Taijuan Walker",              "name_ja": "タイフアン・ウォーカー",   "mlbam_id": 592836, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in MEX_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in MEX_PITCHERS}
