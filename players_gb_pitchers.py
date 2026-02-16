"""WBC 2026 Great Britain roster — MLB pitchers."""

GB_PITCHERS = [
    {"name": "Jack Anderson",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Brendan Beck",                "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Tristan Beck",                "mlbam_id": 663941, "team": "", "throws": "R", "role": "RP"},
    {"name": "Gary Gill Hill",              "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Antonio Knowles",             "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Miles Langhorne",             "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Ryan Long",                   "mlbam_id": 117899, "team": "", "throws": "R", "role": "RP"},
    {"name": "Michael Petersen",            "mlbam_id": 656848, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jack Seppings",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Najer Victor",                "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Owen Wild",                   "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in GB_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in GB_PITCHERS}
