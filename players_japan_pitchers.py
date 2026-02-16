"""WBC 2026 Japan roster — MLB pitchers."""

JAPAN_PITCHERS = [
    {"name": "Yoshinobu Yamamoto",          "mlbam_id": 808967, "team": "", "throws": "R", "role": "RP"},
    {"name": "Yusei Kikuchi",               "mlbam_id": 579328, "team": "", "throws": "L", "role": "RP"},
    {"name": "Yuki Matsui",                 "mlbam_id": 673513, "team": "", "throws": "L", "role": "RP"},
    {"name": "Tomoyuki Sugano",             "mlbam_id": 608372, "team": "", "throws": "R", "role": "RP"},
    {"name": "Sandy Alcántara",             "mlbam_id": 645261, "team": "", "throws": "R", "role": "RP"},
    {"name": "Elvis Alvarado",              "mlbam_id": 665660, "team": "", "throws": "R", "role": "RP"},
    {"name": "Huascar Brazobán",            "mlbam_id": 623211, "team": "", "throws": "R", "role": "RP"},
    {"name": "Brayan Bello",                "mlbam_id": 678394, "team": "", "throws": "R", "role": "RP"},
    {"name": "Seranthony Domínguez",        "mlbam_id": 622554, "team": "", "throws": "R", "role": "RP"},
    {"name": "Camilo Doval",                "mlbam_id": 666808, "team": "", "throws": "R", "role": "RP"},
    {"name": "Carlos Estévez",              "mlbam_id": 608032, "team": "", "throws": "R", "role": "RP"},
    {"name": "Wandy Peralta",               "mlbam_id": 593974, "team": "", "throws": "L", "role": "RP"},
    {"name": "Cristopher Sanchez",          "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Dennis Santana",              "mlbam_id": 642701, "team": "", "throws": "R", "role": "RP"},
    {"name": "Luis Severino",               "mlbam_id": 622663, "team": "", "throws": "R", "role": "RP"},
    {"name": "Gregory Soto",                "mlbam_id": 642397, "team": "", "throws": "L", "role": "RP"},
    {"name": "Abner Uribe",                 "mlbam_id": 682842, "team": "", "throws": "R", "role": "RP"},
    {"name": "Edwin Uceta",                 "mlbam_id": 670955, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jose Alvarado",               "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Eduard Bazardo",              "mlbam_id": 660825, "team": "", "throws": "R", "role": "RP"},
    {"name": "José Buttó",                  "mlbam_id": 676130, "team": "", "throws": "R", "role": "RP"},
    {"name": "Enmanuel De Jesus",           "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Yoendrys Gómez",              "mlbam_id": 672782, "team": "", "throws": "R", "role": "RP"},
    {"name": "Carlos Guzman",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Pablo López",                 "mlbam_id": 641154, "team": "", "throws": "R", "role": "RP"},
    {"name": "Keider Montero",              "mlbam_id": 672456, "team": "", "throws": "R", "role": "RP"},
    {"name": "Oddanier Mosqueda",           "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Daniel Palencia",             "mlbam_id": 694037, "team": "", "throws": "R", "role": "RP"},
    {"name": "Eduardo Rodríguez",           "mlbam_id": 593958, "team": "", "throws": "L", "role": "RP"},
    {"name": "Antonio Senzatela",           "mlbam_id": 622608, "team": "", "throws": "R", "role": "RP"},
    {"name": "Ranger Suárez",               "mlbam_id": 624133, "team": "", "throws": "L", "role": "RP"},
    {"name": "Angel Zerpa",                 "mlbam_id": 672582, "team": "", "throws": "L", "role": "RP"},
    {"name": "Fernando Cruz",               "mlbam_id": 518585, "team": "", "throws": "R", "role": "RP"},
    {"name": "Edwin Diaz",                  "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "José Espada",                 "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Rico Garcia",                 "mlbam_id": 670329, "team": "", "throws": "R", "role": "RP"},
    {"name": "Seth Lugo",                   "mlbam_id": 607625, "team": "", "throws": "R", "role": "RP"},
    {"name": "Jovani Morán",                "mlbam_id": 663558, "team": "", "throws": "L", "role": "RP"},
    {"name": "Luis Quinones",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Yacksel Ríos",                "mlbam_id": 605441, "team": "", "throws": "R", "role": "RP"},
    {"name": "Eduardo Rivera",              "mlbam_id": 0, "team": "", "throws": "L", "role": "RP"},  # TODO: ID not found
    {"name": "Elmer Rodríguez",             "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
    {"name": "Ricardo Velez",               "mlbam_id": 0, "team": "", "throws": "R", "role": "RP"},  # TODO: ID not found
]

PITCHER_BY_ID   = {p['mlbam_id']: p for p in JAPAN_PITCHERS}
PITCHER_BY_NAME = {p['name']: p for p in JAPAN_PITCHERS}
