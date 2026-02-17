"""USA WBC 2026 roster — MLB batters."""

USA_BATTERS = [
    {"name": "Alex Bregman",          "name_ja": "アレックス・ブレグマン",       "mlbam_id": 608324, "pos": "3B",  "team": "Cubs",          "bats": "R"},
    {"name": "Byron Buxton",          "name_ja": "バイロン・バクストン",         "mlbam_id": 621439, "pos": "CF",  "team": "Twins",         "bats": "R"},
    {"name": "Corbin Carroll",        "name_ja": "コービン・キャロル",           "mlbam_id": 682998, "pos": "LF",  "team": "Diamondbacks",  "bats": "L"},
    {"name": "Ernie Clement",         "name_ja": "アーニー・クレメント",         "mlbam_id": 676391, "pos": "UTL", "team": "Blue Jays",     "bats": "R"},
    {"name": "Pete Crow-Armstrong",   "name_ja": "ピート・クロウ＝アームストロング","mlbam_id": 691718, "pos": "CF",  "team": "Cubs",          "bats": "L"},
    {"name": "Paul Goldschmidt",      "name_ja": "ポール・ゴールドシュミット",   "mlbam_id": 502671, "pos": "1B",  "team": "Free Agent",    "bats": "R"},
    {"name": "Bryce Harper",          "name_ja": "ブライス・ハーパー",           "mlbam_id": 547180, "pos": "1B",  "team": "Phillies",      "bats": "L"},
    {"name": "Gunnar Henderson",      "name_ja": "ガナー・ヘンダーソン",         "mlbam_id": 683002, "pos": "SS",  "team": "Orioles",       "bats": "L"},
    {"name": "Aaron Judge",           "name_ja": "アーロン・ジャッジ",           "mlbam_id": 592450, "pos": "RF",  "team": "Yankees",       "bats": "R"},
    {"name": "Cal Raleigh",           "name_ja": "キャル・ローリー",             "mlbam_id": 663728, "pos": "C",   "team": "Mariners",      "bats": "S"},
    {"name": "Kyle Schwarber",        "name_ja": "カイル・シュワーバー",         "mlbam_id": 656941, "pos": "DH",  "team": "Phillies",      "bats": "L"},
    {"name": "Will Smith",            "name_ja": "ウィル・スミス",               "mlbam_id": 669257, "pos": "C",   "team": "Dodgers",       "bats": "R"},
    {"name": "Brice Turang",          "name_ja": "ブライス・トゥラング",         "mlbam_id": 668930, "pos": "2B",  "team": "Brewers",       "bats": "L"},
    {"name": "Bobby Witt Jr.",        "name_ja": "ボビー・ウィットJr.",          "mlbam_id": 677951, "pos": "SS",  "team": "Royals",        "bats": "R"},
]

# Lookup helpers
PLAYER_BY_ID = {p["mlbam_id"]: p for p in USA_BATTERS}
PLAYER_BY_NAME = {p["name"]: p for p in USA_BATTERS}
