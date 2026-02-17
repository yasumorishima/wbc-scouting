"""USA WBC 2026 roster — MLB pitchers."""

USA_PITCHERS = [
    {"name": "David Bednar",          "name_ja": "デイビッド・ベドナー",         "mlbam_id": 670280, "team": "Yankees",     "throws": "R", "role": "RP"},
    {"name": "Matt Boyd",             "name_ja": "マット・ボイド",               "mlbam_id": 571510, "team": "Cubs",        "throws": "L", "role": "SP"},
    {"name": "Garrett Cleavinger",    "name_ja": "ギャレット・クレビンジャー",   "mlbam_id": 664076, "team": "Rays",        "throws": "L", "role": "RP"},
    {"name": "Clay Holmes",           "name_ja": "クレイ・ホームズ",             "mlbam_id": 605280, "team": "Mets",        "throws": "R", "role": "RP"},
    {"name": "Griffin Jax",           "name_ja": "グリフィン・ジャックス",       "mlbam_id": 643377, "team": "Rays",        "throws": "R", "role": "RP"},
    {"name": "Brad Keller",           "name_ja": "ブラッド・ケラー",             "mlbam_id": 641745, "team": "Phillies",    "throws": "R", "role": "SP"},
    {"name": "Clayton Kershaw",       "name_ja": "クレイトン・カーショウ",       "mlbam_id": 477132, "team": "Free Agent",  "throws": "L", "role": "SP"},
    {"name": "Nolan McLean",          "name_ja": "ノーラン・マクリーン",         "mlbam_id": 690997, "team": "Mets",        "throws": "R", "role": "RP"},
    {"name": "Mason Miller",          "name_ja": "メイソン・ミラー",             "mlbam_id": 680911, "team": "Padres",      "throws": "R", "role": "RP"},
    {"name": "Joe Ryan",              "name_ja": "ジョー・ライアン",             "mlbam_id": 657746, "team": "Twins",       "throws": "R", "role": "SP"},
    {"name": "Paul Skenes",           "name_ja": "ポール・スキーンズ",           "mlbam_id": 694973, "team": "Pirates",     "throws": "R", "role": "SP"},
    {"name": "Tarik Skubal",          "name_ja": "タリック・スクーバル",         "mlbam_id": 669373, "team": "Tigers",      "throws": "L", "role": "SP"},
    {"name": "Gabe Speier",           "name_ja": "ゲイブ・スパイアー",           "mlbam_id": 642100, "team": "Mariners",    "throws": "L", "role": "RP"},
    {"name": "Michael Wacha",         "name_ja": "マイケル・ワカ",               "mlbam_id": 608379, "team": "Royals",      "throws": "R", "role": "SP"},
    {"name": "Logan Webb",            "name_ja": "ローガン・ウェッブ",           "mlbam_id": 657277, "team": "Giants",      "throws": "R", "role": "SP"},
    {"name": "Garrett Whitlock",      "name_ja": "ギャレット・ウィットロック",   "mlbam_id": 676477, "team": "Red Sox",     "throws": "R", "role": "RP"},
]

# Lookup helpers
PITCHER_BY_ID = {p["mlbam_id"]: p for p in USA_PITCHERS}
PITCHER_BY_NAME = {p["name"]: p for p in USA_PITCHERS}
