"""WBC 2026 Israel roster — MLB pitchers."""

ISR_PITCHERS = [
    {"name": "Charlie Beilenson",           "name_ja": "チャーリー・ベイレンソン", "mlbam_id": 810897, "team": "", "throws": "R", "role": "RP"},
    {"name": "Josh Blum",                   "name_ja": "ジョシュ・ブラム",         "mlbam_id": 810840, "team": "", "throws": "R", "role": "RP"},
    {"name": "Matt Bowman",                 "name_ja": "マット・ボウマン",         "mlbam_id": 621199, "team": "", "throws": "R", "role": "RP"},
    {"name": "Harrison Cohen",              "name_ja": "ハリソン・コーエン",       "mlbam_id": 694660, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jordan Geber",                "name_ja": "ジョーダン・ゲバー",       "mlbam_id": 802363, "team": "", "throws": "R", "role": "RP"},
    {"name": "Dean Kremer",                 "name_ja": "ディーン・クレーマー",     "mlbam_id": 665152, "team": "", "throws": "R", "role": "RP"},
    {"name": "Max Lazar",                   "name_ja": "マックス・レイザー",       "mlbam_id": 676661, "team": "", "throws": "R", "role": "RP"},
    {"name": "Carlos Lequerica",            "name_ja": "カルロス・レケリカ",       "mlbam_id": 701557, "team": "", "throws": "R", "role": "RP"},
    {"name": "Josh Mallitz",                "name_ja": "ジョシュ・マリッツ",       "mlbam_id": 695256, "team": "", "throws": "R", "role": "RP"},
    {"name": "Eli Morgan",                  "name_ja": "イーライ・モーガン",       "mlbam_id": 669212, "team": "", "throws": "R", "role": "RP"},
    {"name": "Ryan Prager",                 "name_ja": "ライアン・プレイガー",     "mlbam_id": 696492, "team": "", "throws": "L", "role": "RP"},
    {"name": "Ben Simon",                   "name_ja": "ベン・サイモン",           "mlbam_id": 815084, "team": "", "throws": "R", "role": "RP"},
    {"name": "Robert Stock",                "name_ja": "ロバート・ストック",       "mlbam_id": 476594, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in ISR_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in ISR_PITCHERS}
