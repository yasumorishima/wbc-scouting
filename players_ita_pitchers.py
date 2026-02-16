"""WBC 2026 Italy roster — MLB pitchers."""

ITA_PITCHERS = [
    {"name": "Sam Aldegheri",               "mlbam_id": 691951, "team": "", "throws": "L", "role": "RP"},
    {"name": "Dan Altavilla",               "mlbam_id": 656186, "team": "", "throws": "R", "role": "RP"},
    {"name": "Dylan DeLucia",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Alessandro Ercolani",         "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Matt Festa",                  "mlbam_id": 670036, "team": "", "throws": "R", "role": "RP"},
    {"name": "Gordon Graceffo",             "mlbam_id": 700669, "team": "", "throws": "R", "role": "RP"},
    {"name": "Alek Jacob",                  "mlbam_id": 689690, "team": "", "throws": "R", "role": "RP"},
    {"name": "Joe La Sorsa",                "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Michael Lorenzen",            "mlbam_id": 547179, "team": "", "throws": "R", "role": "RP"},
    {"name": "Ron Marinaccio",              "mlbam_id": 676760, "team": "", "throws": "R", "role": "RP"},
    {"name": "Kyle Nicolas",                "mlbam_id": 693312, "team": "", "throws": "R", "role": "RP"},
    {"name": "Aaron Nola",                  "mlbam_id": 605400, "team": "", "throws": "R", "role": "RP"},
    {"name": "Greg Weissert",               "mlbam_id": 669711, "team": "", "throws": "R", "role": "RP"},
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in ITA_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in ITA_PITCHERS}
