"""WBC 2026 Canada roster — MLB pitchers."""

CAN_PITCHERS = [
    {"name": "Micah Ashman",                "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Eric Cerantola",              "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Indigo Diaz",                 "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Antoine Jean",                "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Carter Loewen",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Adam Macko",                  "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Cal Quantrill",               "mlbam_id": 615698, "team": "", "throws": "R", "role": "RP"},
    {"name": "Michael Soroka",              "mlbam_id": 647336, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jameson Taillon",             "mlbam_id": 592791, "team": "", "throws": "R", "role": "RP"},
    {"name": "Matt Wilkinson",              "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Rob Zastryzny",               "mlbam_id": 642239, "team": "", "throws": "L", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in CAN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in CAN_PITCHERS}
