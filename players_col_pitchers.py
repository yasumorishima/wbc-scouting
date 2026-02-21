"""WBC 2026 Colombia roster — MLB pitchers."""

COL_PITCHERS = [
    {"name": "Austin Bergner",              "name_ja": "オースティン・バーグナー", "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Nabil Crismatt",              "name_ja": "ナビル・クリスマット",     "mlbam_id": 622503, "team": "", "throws": "R", "role": "RP"},
    {"name": "Tayron Guerrero",             "name_ja": "タイロン・ゲレーロ",       "mlbam_id": 594027, "team": "", "throws": "R", "role": "RP"},
    {"name": "David Lorduy",                "name_ja": "ダビド・ロルドゥイ",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Reiver Sanmartín",            "name_ja": "レイバー・サンマルティン", "mlbam_id": 665665, "team": "CIN", "throws": "L", "role": "RP"},
    {"name": "Guillo Zuñiga",               "name_ja": "ギジョ・スニガ",           "mlbam_id": 670871, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in COL_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in COL_PITCHERS}
