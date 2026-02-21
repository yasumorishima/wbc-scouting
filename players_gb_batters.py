"""WBC 2026 Great Britain roster — MLB batters."""

GB_BATTERS = [
    {"name": "Jazz Chisholm Jr.",           "name_ja": "ジャズ・チザムJr.",        "mlbam_id": 665862, "pos": "2B", "team": "NYY", "bats": "L"},
    {"name": "Willis Cresswell",            "name_ja": "ウィリス・クレスウェル",   "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Nate Eaton",                  "name_ja": "ネイト・イートン",         "mlbam_id": 681987, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Harry Ford",                  "name_ja": "ハリー・フォード",         "mlbam_id": 695670, "pos": "C", "team": "", "bats": "R"},
    {"name": "Ivan Johnson",                "name_ja": "アイバン・ジョンソン",     "mlbam_id": 0, "pos": "2B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Matt Koperniak",              "name_ja": "マット・コパーニアック",   "mlbam_id": 0, "pos": "RF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Ian Lewis Jr.",               "name_ja": "イアン・ルイスJr.",        "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "BJ Murray",                   "name_ja": "BJ・マレー",              "mlbam_id": 0, "pos": "1B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Kristian Robinson",           "name_ja": "クリスチャン・ロビンソン", "mlbam_id": 0, "pos": "CF", "team": "", "bats": "R"},  # TODO: ID not found
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in GB_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in GB_BATTERS}
