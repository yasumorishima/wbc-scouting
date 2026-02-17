"""WBC 2026 Italy roster — MLB pitchers."""

ITA_PITCHERS = [
    {"name": "Sam Aldegheri",               "name_ja": "サム・アルデゲリ",         "mlbam_id": 691951, "team": "", "throws": "L", "role": "RP"},
    {"name": "Dan Altavilla",               "name_ja": "ダン・アルタビラ",         "mlbam_id": 656186, "team": "", "throws": "R", "role": "RP"},
    {"name": "Dylan DeLucia",               "name_ja": "ディラン・デルシア",       "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Alessandro Ercolani",         "name_ja": "アレッサンドロ・エルコラーニ","mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Matt Festa",                  "name_ja": "マット・フェスタ",         "mlbam_id": 670036, "team": "", "throws": "R", "role": "RP"},
    {"name": "Gordon Graceffo",             "name_ja": "ゴードン・グレイスフォ",   "mlbam_id": 700669, "team": "", "throws": "R", "role": "RP"},
    {"name": "Alek Jacob",                  "name_ja": "アレク・ジェイコブ",       "mlbam_id": 689690, "team": "", "throws": "R", "role": "RP"},
    {"name": "Joe La Sorsa",                "name_ja": "ジョー・ラ・ソーサ",       "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Michael Lorenzen",            "name_ja": "マイケル・ローレンゼン",   "mlbam_id": 547179, "team": "", "throws": "R", "role": "RP"},
    {"name": "Ron Marinaccio",              "name_ja": "ロン・マリナッチオ",       "mlbam_id": 676760, "team": "", "throws": "R", "role": "RP"},
    {"name": "Kyle Nicolas",                "name_ja": "カイル・ニコラス",         "mlbam_id": 693312, "team": "", "throws": "R", "role": "RP"},
    {"name": "Aaron Nola",                  "name_ja": "アーロン・ノラ",           "mlbam_id": 605400, "team": "", "throws": "R", "role": "RP"},
    {"name": "Greg Weissert",               "name_ja": "グレッグ・ワイサート",     "mlbam_id": 669711, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in ITA_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in ITA_PITCHERS}
