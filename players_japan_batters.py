"""WBC 2026 Japan roster — MLB batters."""

JAPAN_BATTERS = [
    {"name": "Shohei Ohtani",    "name_ja": "大谷翔平",   "mlbam_id": 660271, "pos": "DH", "team": "Dodgers",   "bats": "L"},
    {"name": "Seiya Suzuki",     "name_ja": "鈴木誠也",   "mlbam_id": 673548, "pos": "RF", "team": "Cubs",       "bats": "R"},
    {"name": "Masataka Yoshida", "name_ja": "吉田正尚",   "mlbam_id": 807799, "pos": "LF", "team": "Red Sox",    "bats": "L"},
    {"name": "Munetaka Murakami","name_ja": "村上宗隆",   "mlbam_id": 0,      "pos": "1B", "team": "White Sox",  "bats": "R"},  # No MLB Statcast data
    {"name": "Kazuma Okamoto",   "name_ja": "岡本和真",   "mlbam_id": 0,      "pos": "3B", "team": "Blue Jays",  "bats": "R"},  # No MLB Statcast data
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in JAPAN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in JAPAN_BATTERS}
