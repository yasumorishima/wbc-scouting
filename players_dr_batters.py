"""Dominican Republic WBC 2026 roster — MLB batters."""

DR_BATTERS = [
    {"name": "Junior Caminero",       "mlbam_id": 691406, "pos": "3B",  "team": "Rays",          "bats": "R"},
    {"name": "Oneil Cruz",            "mlbam_id": 665833, "pos": "CF",  "team": "Pirates",       "bats": "L"},
    {"name": "Vladimir Guerrero Jr.", "mlbam_id": 665489, "pos": "1B",  "team": "Blue Jays",     "bats": "R"},
    {"name": "Manny Machado",         "mlbam_id": 592518, "pos": "3B",  "team": "Padres",        "bats": "R"},
    {"name": "Ketel Marte",           "mlbam_id": 606466, "pos": "2B",  "team": "Diamondbacks",  "bats": "S"},
    {"name": "Jeremy Peña",           "mlbam_id": 665161, "pos": "SS",  "team": "Astros",        "bats": "R"},
    {"name": "Geraldo Perdomo",       "mlbam_id": 672695, "pos": "SS",  "team": "Diamondbacks",  "bats": "S"},
    {"name": "Agustín Ramírez",       "mlbam_id": 682663, "pos": "C",   "team": "Marlins",       "bats": "R"},
    {"name": "Julio Rodríguez",       "mlbam_id": 677594, "pos": "CF",  "team": "Mariners",      "bats": "R"},
    {"name": "Johan Rojas",           "mlbam_id": 679032, "pos": "CF",  "team": "Phillies",      "bats": "R"},
    {"name": "Amed Rosario",          "mlbam_id": 642708, "pos": "UTL", "team": "Yankees",       "bats": "R"},
    {"name": "Carlos Santana",        "mlbam_id": 467793, "pos": "1B",  "team": "Diamondbacks",  "bats": "S"},
    {"name": "Juan Soto",             "mlbam_id": 665742, "pos": "RF",  "team": "Mets",          "bats": "L"},
    {"name": "Fernando Tatís Jr.",    "mlbam_id": 665487, "pos": "RF",  "team": "Padres",        "bats": "R"},
    {"name": "Austin Wells",          "mlbam_id": 669224, "pos": "C",   "team": "Yankees",       "bats": "L"},
]

# Lookup helpers
PLAYER_BY_ID = {p["mlbam_id"]: p for p in DR_BATTERS}
PLAYER_BY_NAME = {p["name"]: p for p in DR_BATTERS}
