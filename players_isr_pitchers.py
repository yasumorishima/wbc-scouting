"""WBC 2026 Israel roster — MLB pitchers."""

ISR_PITCHERS = [
    {"name": "Charlie Beilenson",           "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Josh Blum",                   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Matt Bowman",                 "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Harrison Cohen",              "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Jordan Geber",                "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Dean Kremer",                 "mlbam_id": 665152, "team": "", "throws": "R", "role": "RP"},
    {"name": "Max Lazar",                   "mlbam_id": 676661, "team": "", "throws": "R", "role": "RP"},
    {"name": "Carlos Lequerica",            "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Josh Mallitz",                "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Eli Morgan",                  "mlbam_id": 669212, "team": "", "throws": "R", "role": "RP"},
    {"name": "Ryan Prager",                 "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Ben Simon",                   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Robert Stock",                "mlbam_id": 476594, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in ISR_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in ISR_PITCHERS}
