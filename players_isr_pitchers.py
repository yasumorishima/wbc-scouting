"""WBC 2026 Israel roster — MLB pitchers."""

ISR_PITCHERS = [
    {"name": "Charlie Beilenson",           "name_ja": "チャーリー・ベイレンソン", "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Josh Blum",                   "name_ja": "ジョシュ・ブラム",         "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Matt Bowman",                 "name_ja": "マット・ボウマン",         "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Harrison Cohen",              "name_ja": "ハリソン・コーエン",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Jordan Geber",                "name_ja": "ジョーダン・ゲバー",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Dean Kremer",                 "name_ja": "ディーン・クレーマー",     "mlbam_id": 665152, "team": "", "throws": "R", "role": "RP"},
    {"name": "Max Lazar",                   "name_ja": "マックス・レイザー",       "mlbam_id": 676661, "team": "", "throws": "R", "role": "RP"},
    {"name": "Carlos Lequerica",            "name_ja": "カルロス・レケリカ",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Josh Mallitz",                "name_ja": "ジョシュ・マリッツ",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Eli Morgan",                  "name_ja": "イーライ・モーガン",       "mlbam_id": 669212, "team": "", "throws": "R", "role": "RP"},
    {"name": "Ryan Prager",                 "name_ja": "ライアン・プレイガー",     "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Ben Simon",                   "name_ja": "ベン・サイモン",           "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Robert Stock",                "name_ja": "ロバート・ストック",       "mlbam_id": 476594, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in ISR_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in ISR_PITCHERS}
