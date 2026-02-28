"""WBC 2026 Japan roster — MLB pitchers."""

JAPAN_PITCHERS = [
    {"name": "Yoshinobu Yamamoto", "name_ja": "山本由伸",   "mlbam_id": 808967, "team": "Dodgers", "throws": "R", "role": "SP"},
    {"name": "Yusei Kikuchi",      "name_ja": "菊池雄星",   "mlbam_id": 579328, "team": "Angels",  "throws": "L", "role": "SP"},
    # ★辞退（左内転筋負傷・2/26公式発表）→ 代替: 金丸夢斗（中日・NPB）
    {"name": "Yuki Matsui",        "name_ja": "松井裕樹",   "mlbam_id": 673513, "team": "Padres",  "throws": "L", "role": "RP"},
    {"name": "Tomoyuki Sugano",    "name_ja": "菅野智之",   "mlbam_id": 608372, "team": "Rockies", "throws": "R", "role": "SP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in JAPAN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in JAPAN_PITCHERS}
