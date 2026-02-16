"""WBC 2026 Japan roster — MLB batters."""

JAPAN_BATTERS = [
    {"name": "Shohei Ohtani",               "mlbam_id": 660271, "pos": "DH", "team": "", "bats": "R"},
    {"name": "Seiya Suzuki",                "mlbam_id": 673548, "pos": "RF", "team": "", "bats": "R"},
    {"name": "Masataka Yoshida",            "mlbam_id": 807799, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Munetaka Murakami",           "mlbam_id": 0, "pos": "1B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Kazuma Okamoto",              "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Junior Caminero",             "mlbam_id": 691406, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Oneil Cruz",                  "mlbam_id": 665833, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Vladimir Guerrero Jr.",       "mlbam_id": 0, "pos": "1B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Manny Machado",               "mlbam_id": 592518, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Ketel Marte",                 "mlbam_id": 606466, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Jeremy Peña",                 "mlbam_id": 665161, "pos": "SS", "team": "", "bats": "R"},
    {"name": "Geraldo Perdomo",             "mlbam_id": 672695, "pos": "SS", "team": "", "bats": "R"},
    {"name": "Agustín Ramírez",             "mlbam_id": 682663, "pos": "C", "team": "", "bats": "R"},
    {"name": "Julio Rodríguez",             "mlbam_id": 677594, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Johan Rojas",                 "mlbam_id": 679032, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Amed Rosario",                "mlbam_id": 642708, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Carlos Santana",              "mlbam_id": 467793, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Juan Soto",                   "mlbam_id": 665742, "pos": "RF", "team": "", "bats": "R"},
    {"name": "Fernando Tatís Jr.",          "mlbam_id": 0, "pos": "RF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Austin Wells",                "mlbam_id": 669224, "pos": "C", "team": "", "bats": "R"},
    {"name": "Ronald Acuña Jr.",            "mlbam_id": 0, "pos": "RF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Wilyer Abreu",                "mlbam_id": 677800, "pos": "RF", "team": "", "bats": "R"},
    {"name": "Luis Arráez",                 "mlbam_id": 650333, "pos": "1B", "team": "", "bats": "R"},
    {"name": "Jackson Chourio",             "mlbam_id": 694192, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Willson Contreras",           "mlbam_id": 575929, "pos": "1B", "team": "", "bats": "R"},
    {"name": "William Contreras",           "mlbam_id": 661388, "pos": "C", "team": "", "bats": "R"},
    {"name": "Maikel Garcia",               "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Andrés Giménez",              "mlbam_id": 665926, "pos": "2B/SS", "team": "", "bats": "R"},
    {"name": "Salvador Perez",              "mlbam_id": 0, "pos": "C", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Javier Sanoja",               "mlbam_id": 691594, "pos": "UTL", "team": "", "bats": "R"},
    {"name": "Eugenio Suárez",              "mlbam_id": 553993, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Gleyber Torres",              "mlbam_id": 650402, "pos": "2B", "team": "", "bats": "R"},
    {"name": "Ezequiel Tovar",              "mlbam_id": 678662, "pos": "SS", "team": "", "bats": "R"},
    {"name": "Nolan Arenado",               "mlbam_id": 571448, "pos": "3B", "team": "", "bats": "R"},
    {"name": "Edwin Arroyo",                "mlbam_id": 0, "pos": "SS", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Willi Castro",                "mlbam_id": 650489, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Carlos Cortes",               "mlbam_id": 666126, "pos": "LF", "team": "", "bats": "R"},
    {"name": "Darrell Hernáiz",             "mlbam_id": 0, "pos": "3B", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Matthew Lugo",                "mlbam_id": 683090, "pos": "CF", "team": "", "bats": "R"},
    {"name": "Heliot Ramos",                "mlbam_id": 671218, "pos": "RF", "team": "", "bats": "R"},
    {"name": "Bryan Torres",                "mlbam_id": 0, "pos": "OF", "team": "", "bats": "R"},  # TODO: ID not found
    {"name": "Luis Vázquez",                "mlbam_id": 676679, "pos": "SS", "team": "", "bats": "R"},
]

PLAYER_BY_ID   = {p['mlbam_id']: p for p in JAPAN_BATTERS}
PLAYER_BY_NAME = {p['name']: p for p in JAPAN_BATTERS}
