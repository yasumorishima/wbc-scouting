"""WBC 2026 Australia roster — MLB pitchers."""

AUS_PITCHERS = [
    {"name": "Mitch Neunborn",              "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Blake Townsend",              "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in AUS_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in AUS_PITCHERS}
