"""Venezuela WBC 2026 roster — MLB batters & pitchers."""

VENEZUELA_BATTERS = [
    {"name": "Ronald Acuña Jr.",   "mlbam_id": 660670, "pos": "RF",     "team": "Braves",   "bats": "R"},
    {"name": "Wilyer Abreu",       "mlbam_id": 677800, "pos": "RF",     "team": "Red Sox",   "bats": "L"},
    {"name": "Luis Arráez",        "mlbam_id": 650333, "pos": "1B",     "team": "Giants",    "bats": "L"},
    {"name": "Jackson Chourio",    "mlbam_id": 694192, "pos": "CF",     "team": "Brewers",   "bats": "R"},
    {"name": "Willson Contreras",  "mlbam_id": 575929, "pos": "1B",     "team": "Red Sox",   "bats": "R"},
    {"name": "William Contreras",  "mlbam_id": 661388, "pos": "C",      "team": "Brewers",   "bats": "S"},
    {"name": "Maikel Garcia",      "mlbam_id": 672580, "pos": "3B",     "team": "Royals",    "bats": "R"},
    {"name": "Andrés Giménez",     "mlbam_id": 665926, "pos": "2B/SS",  "team": "Blue Jays", "bats": "L"},
    {"name": "Salvador Perez",     "mlbam_id": 521692, "pos": "C",      "team": "Royals",    "bats": "R"},
    {"name": "Javier Sanoja",      "mlbam_id": 691594, "pos": "UTL",    "team": "Marlins",   "bats": "R"},
    {"name": "Eugenio Suárez",     "mlbam_id": 553993, "pos": "3B",     "team": "Reds",      "bats": "R"},
    {"name": "Gleyber Torres",     "mlbam_id": 650402, "pos": "2B",     "team": "Tigers",    "bats": "R"},
    {"name": "Ezequiel Tovar",     "mlbam_id": 678662, "pos": "SS",     "team": "Rockies",   "bats": "R"},
]

VENEZUELA_PITCHERS = [
    {"name": "Jose Alvarado",       "mlbam_id": 621237, "team": "Phillies",       "throws": "L", "role": "RP"},
    {"name": "Eduard Bazardo",      "mlbam_id": 660825, "team": "Mariners",       "throws": "R", "role": "RP"},
    {"name": "José Buttó",          "mlbam_id": 676130, "team": "Giants",         "throws": "R", "role": "RP"},
    {"name": "Enmanuel De Jesus",   "mlbam_id": 646241, "team": "Tigers",         "throws": "L", "role": "RP"},
    {"name": "Yoendrys Gómez",      "mlbam_id": 672782, "team": "Rays",           "throws": "R", "role": "RP"},
    {"name": "Carlos Guzman",       "mlbam_id": 664346, "team": "Mets",           "throws": "R", "role": "RP"},
    {"name": "Pablo López",         "mlbam_id": 641154, "team": "Twins",          "throws": "R", "role": "SP"},
    {"name": "Keider Montero",      "mlbam_id": 672456, "team": "Tigers",         "throws": "R", "role": "SP"},
    {"name": "Daniel Palencia",     "mlbam_id": 694037, "team": "Cubs",           "throws": "R", "role": "RP"},
    {"name": "Eduardo Rodríguez",   "mlbam_id": 593958, "team": "Diamondbacks",   "throws": "L", "role": "SP"},
    {"name": "Antonio Senzatela",   "mlbam_id": 622608, "team": "Rockies",        "throws": "R", "role": "SP"},
    {"name": "Ranger Suárez",       "mlbam_id": 624133, "team": "Red Sox",        "throws": "L", "role": "SP"},
    {"name": "Angel Zerpa",         "mlbam_id": 672582, "team": "Brewers",        "throws": "L", "role": "RP"},
]
# Note: Oddanier Mosqueda (LHP, Pirates) excluded — no Statcast data (minor league)

# Lookup helpers — batters
PLAYER_BY_ID = {p["mlbam_id"]: p for p in VENEZUELA_BATTERS}
PLAYER_BY_NAME = {p["name"]: p for p in VENEZUELA_BATTERS}

# Lookup helpers — pitchers
PITCHER_BY_ID = {p["mlbam_id"]: p for p in VENEZUELA_PITCHERS}
PITCHER_BY_NAME = {p["name"]: p for p in VENEZUELA_PITCHERS}
