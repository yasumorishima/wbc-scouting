"""Dominican Republic WBC 2026 roster — MLB pitchers."""

DR_PITCHERS = [
    {"name": "Sandy Alcántara",        "name_ja": "サンディ・アルカンタラ",       "mlbam_id": 645261, "team": "Marlins",      "throws": "R", "role": "SP"},
    {"name": "Elvis Alvarado",         "name_ja": "エルビス・アルバラード",       "mlbam_id": 665660, "team": "Athletics",    "throws": "R", "role": "RP"},
    {"name": "Brayan Bello",           "name_ja": "ブライアン・ベイヨ",           "mlbam_id": 678394, "team": "Red Sox",      "throws": "R", "role": "SP"},
    {"name": "Huascar Brazobán",       "name_ja": "ワスカー・ブラソバン",         "mlbam_id": 623211, "team": "Mets",         "throws": "R", "role": "RP"},
    {"name": "Seranthony Domínguez",   "name_ja": "セランソニー・ドミンゲス",     "mlbam_id": 622554, "team": "White Sox",    "throws": "R", "role": "RP"},
    {"name": "Camilo Doval",           "name_ja": "カミロ・ドバル",               "mlbam_id": 666808, "team": "Yankees",      "throws": "R", "role": "RP"},
    {"name": "Carlos Estévez",         "name_ja": "カルロス・エステベス",         "mlbam_id": 608032, "team": "Royals",       "throws": "R", "role": "RP"},
    {"name": "Wandy Peralta",          "name_ja": "ワンディ・ペラルタ",           "mlbam_id": 593974, "team": "Padres",       "throws": "L", "role": "RP"},
    {"name": "Cristopher Sánchez",     "name_ja": "クリストファー・サンチェス",   "mlbam_id": 650911, "team": "Phillies",     "throws": "L", "role": "SP"},
    {"name": "Dennis Santana",         "name_ja": "デニス・サンタナ",             "mlbam_id": 642701, "team": "Pirates",      "throws": "R", "role": "RP"},
    {"name": "Luis Severino",          "name_ja": "ルイス・セベリーノ",           "mlbam_id": 622663, "team": "Athletics",    "throws": "R", "role": "SP"},
    {"name": "Gregory Soto",           "name_ja": "グレゴリー・ソト",             "mlbam_id": 642397, "team": "Pirates",      "throws": "L", "role": "RP"},
    {"name": "Abner Uribe",            "name_ja": "アブナー・ウリベ",             "mlbam_id": 682842, "team": "Brewers",      "throws": "R", "role": "RP"},
    {"name": "Edwin Uceta",            "name_ja": "エドウィン・ウセタ",           "mlbam_id": 670955, "team": "Rays",         "throws": "R", "role": "RP"},
]

# Lookup helpers
PITCHER_BY_ID = {p["mlbam_id"]: p for p in DR_PITCHERS}
PITCHER_BY_NAME = {p["name"]: p for p in DR_PITCHERS}
