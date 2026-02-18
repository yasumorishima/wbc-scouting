"""Generate app_XX.py and app_XX_pitchers.py for each WBC country.

Usage:
    python scripts/generate_apps.py              # all countries
    python scripts/generate_apps.py --country japan
"""

import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Country metadata
# ---------------------------------------------------------------------------
COUNTRIES = {
    "japan": {
        "name_en": "Japan",
        "name_ja": "日本",
        "flag": "\U0001F1EF\U0001F1F5",
        "var": "JAPAN",
        "batter_en": (
            "Japan is widely regarded as one of the strongest teams in the tournament, "
            "featuring a balanced lineup with elite contact hitters and disciplined plate approach. "
            "Key batters include Shohei Ohtani and Munetaka Murakami, both capable of elite power. "
            "The lineup's depth and high on-base skills may pose significant challenges for opposing pitchers."
        ),
        "batter_ja": (
            "日本はトーナメント屈指の強豪チームと考えられており、"
            "バランスの取れた打線と高い選球眼が特徴とされている。\n\n"
            "大谷翔平・村上宗隆らを中心に長打力と出塁率を兼ね備えた打者が多く、"
            "打線全体の得点力は高い可能性がある。"
        ),
        "pitcher_en": (
            "Japan is expected to feature a deep and high-quality pitching staff, "
            "with starters capable of elite strikeout rates and strong command. "
            "The combination of power pitching and pitch-type variety may make Japan's rotation "
            "one of the most difficult to face in the tournament."
        ),
        "pitcher_ja": (
            "日本の投手陣はトーナメントでも屈指の質と深さを誇ると考えられている。\n\n"
            "高い奪三振能力と制球力を持つ先発投手を複数擁し、"
            "球種の多彩さと組み立ての巧みさが特徴とされている。"
        ),
    },
    "mex": {
        "name_en": "Mexico",
        "name_ja": "メキシコ",
        "flag": "\U0001F1F2\U0001F1FD",
        "var": "MEX",
        "batter_en": (
            "Mexico fields a lineup with a mix of MLB veterans and emerging talent. "
            "The team is known for aggressive hitting and solid middle-of-the-order power. "
            "Key batters such as Randy Arozarena bring elite athleticism and clutch hitting ability, "
            "making Mexico a dangerous offensive opponent."
        ),
        "batter_ja": (
            "メキシコは積極的な打撃スタイルと中軸の長打力が特徴とされている。\n\n"
            "ランディ・アロサレーナらMLB経験豊富な選手を擁し、"
            "クラッチヒッターとしての能力が高い可能性がある。"
        ),
        "pitcher_en": (
            "Mexico's pitching staff includes several MLB-level arms with the ability "
            "to generate swings and misses across multiple pitch types. "
            "The rotation and bullpen depth may provide strong coverage throughout the tournament."
        ),
        "pitcher_ja": (
            "メキシコの投手陣は複数のMLBレベルの投手を擁し、"
            "多彩な球種で空振りを奪う能力が高い可能性がある。\n\n"
            "先発・中継ぎの層の厚さが特徴と考えられる。"
        ),
    },
    "kor": {
        "name_en": "South Korea",
        "name_ja": "韓国",
        "flag": "\U0001F1F0\U0001F1F7",
        "var": "KOR",
        "batter_en": (
            "South Korea traditionally fields a disciplined, contact-oriented lineup "
            "with strong fundamentals. The team tends to emphasize high on-base percentage "
            "and situational hitting. MLB-experienced players may anchor the lineup "
            "and provide additional power threat."
        ),
        "batter_ja": (
            "韓国は規律ある打撃スタイルと高い出塁率を重視するチームとして知られている。\n\n"
            "コンタクトヒッターを中心に状況判断に優れた打者が多く、"
            "MLB経験者が中軸を担うケースもある。"
        ),
        "pitcher_en": (
            "South Korea's pitching staff is known for strong command and efficient pitch usage. "
            "The rotation may feature arms with diverse pitch mixes and the ability "
            "to limit walks and induce weak contact."
        ),
        "pitcher_ja": (
            "韓国の投手陣は高い制球力と効率的な投球が特徴とされている。\n\n"
            "多彩な球種と四球の少なさが強みと考えられ、"
            "打ち損じを誘う投球スタイルが持ち味の可能性がある。"
        ),
    },
    "ned": {
        "name_en": "Netherlands",
        "name_ja": "オランダ",
        "flag": "\U0001F1F3\U0001F1F1",
        "var": "NED",
        "batter_en": (
            "The Netherlands features several MLB-caliber players, notably Xander Bogaerts "
            "and Didi Gregorius, providing a solid middle-of-the-order core. "
            "The lineup blends experience with emerging talent, "
            "and can be dangerous when players make consistent contact."
        ),
        "batter_ja": (
            "オランダはザンダー・ボガーツやディディ・グレゴリアスらMLBレベルの選手を擁し、"
            "中軸に安定感がある。\n\n"
            "経験豊富な選手と若手の融合が特徴で、"
            "コンタクト率が高まると得点力が増す可能性がある。"
        ),
        "pitcher_en": (
            "The Netherlands has developed a solid pitching tradition with players competing "
            "at the MLB and Triple-A level. The staff may feature diverse arm types "
            "with the ability to keep opposing lineups off balance."
        ),
        "pitcher_ja": (
            "オランダの投手陣はMLBやトリプルAレベルの投手を含む充実した顔ぶれが期待される。\n\n"
            "多様な球種と投球スタイルで打線を抑える能力が高い可能性がある。"
        ),
    },
    "can": {
        "name_en": "Canada",
        "name_ja": "カナダ",
        "flag": "\U0001F1E8\U0001F1E6",
        "var": "CAN",
        "batter_en": (
            "Canada has grown significantly as a baseball nation, producing MLB-level talent in recent years. "
            "The lineup is expected to feature a mix of power hitters and table-setters, "
            "capable of providing dangerous run-producing ability throughout the order."
        ),
        "batter_ja": (
            "カナダは近年MLB選手を多く輩出する野球大国として台頭しており、"
            "長打力と出塁力を兼ね備えた選手が中軸を形成すると考えられる。\n\n"
            "攻撃的なラインナップで、得点力の高いチームになる可能性がある。"
        ),
        "pitcher_en": (
            "Canada's pitching staff includes several active MLB arms, "
            "capable of high strikeout rates and power pitching. "
            "The bullpen depth may be a key factor in Canada's tournament performance."
        ),
        "pitcher_ja": (
            "カナダの投手陣は複数の現役MLB投手を擁し、"
            "高い奪三振能力が期待される。\n\n"
            "ブルペンの層の厚さがトーナメントでの重要な武器になる可能性がある。"
        ),
    },
    "ita": {
        "name_en": "Italy",
        "name_ja": "イタリア",
        "flag": "\U0001F1EE\U0001F1F9",
        "var": "ITA",
        "batter_en": (
            "Italy has steadily improved its talent pool by drawing on players of Italian descent "
            "competing in MLB and MiLB. The lineup features versatile hitters "
            "with solid contact skills, and key contributors may include "
            "players with notable MLB experience."
        ),
        "batter_ja": (
            "イタリアはイタリア系MLB・マイナー選手を積極的に招集し、"
            "打線の質を年々高めていると考えられている。\n\n"
            "コンタクト能力の高い選手を中心に、"
            "MLB経験者が打線を牽引する可能性がある。"
        ),
        "pitcher_en": (
            "Italy's pitching staff draws on Italian-heritage players from the MLB pipeline. "
            "The rotation may feature arms with solid command and varied pitch types, "
            "capable of limiting damage against strong lineups."
        ),
        "pitcher_ja": (
            "イタリアの投手陣はMLBパイプラインのイタリア系選手で構成される見込みで、"
            "制球力と球種の多彩さが特徴とされている。\n\n"
            "強力打線に対してダメージを最小化する投球が期待される。"
        ),
    },
    "isr": {
        "name_en": "Israel",
        "name_ja": "イスラエル",
        "flag": "\U0001F1EE\U0001F1F1",
        "var": "ISR",
        "batter_en": (
            "Israel fields a roster composed largely of Jewish-heritage players from MLB and MiLB. "
            "The lineup may feature solid contact hitters with plate discipline, "
            "and certain batters have demonstrated the ability to reach base consistently "
            "against international competition."
        ),
        "batter_ja": (
            "イスラエルはユダヤ系のMLB・マイナー選手で構成されており、"
            "選球眼の良さとコンタクト能力が特徴とされている。\n\n"
            "国際大会での経験を持つ選手も含まれており、"
            "出塁率を高める打撃スタイルが持ち味の可能性がある。"
        ),
        "pitcher_en": (
            "Israel's pitching staff includes MLB-level arms with experience in professional baseball. "
            "The rotation and bullpen may surprise opponents with diverse pitch mixes "
            "and competitive command."
        ),
        "pitcher_ja": (
            "イスラエルの投手陣はMLBレベルの経験を持つ投手を含んでいる。\n\n"
            "多彩な球種と安定した制球力で対戦相手を苦しめる可能性がある。"
        ),
    },
    "gb": {
        "name_en": "Great Britain",
        "name_ja": "イギリス",
        "flag": "\U0001F1EC\U0001F1E7",
        "var": "GB",
        "batter_en": (
            "Great Britain has developed a growing baseball program, "
            "drawing on British-heritage MLB and MiLB players. "
            "The lineup may feature underrated contact hitters and players "
            "with strong fundamental skills developed through professional organizations."
        ),
        "batter_ja": (
            "イギリスは成長著しいベースボールプログラムを持ち、"
            "英国系のMLB・マイナー選手を中心に構成される見込みである。\n\n"
            "コンタクト能力と基礎技術を重視した打線が特徴の可能性がある。"
        ),
        "pitcher_en": (
            "Great Britain's pitching staff may feature arms developed through MLB organizations. "
            "The key strength may lie in command and pitch sequencing "
            "rather than raw velocity."
        ),
        "pitcher_ja": (
            "イギリスの投手陣はMLB傘下で育成された投手を含む構成が見込まれる。\n\n"
            "球速よりも制球力と球種の組み立てが強みとなる可能性がある。"
        ),
    },
    "pan": {
        "name_en": "Panama",
        "name_ja": "パナマ",
        "flag": "\U0001F1F5\U0001F1E6",
        "var": "PAN",
        "batter_en": (
            "Panama has a rich baseball history and features a lineup built around "
            "MLB-experienced players with power and speed. "
            "The team's offensive profile may center on run production through "
            "extra-base hits and aggressive baserunning."
        ),
        "batter_ja": (
            "パナマは野球の伝統国であり、MLB経験者を中心とした長打力と機動力のある打線が特徴とされている。\n\n"
            "長打と積極的な走塁を組み合わせた攻撃的なスタイルが持ち味の可能性がある。"
        ),
        "pitcher_en": (
            "Panama's pitching staff includes arms with MLB and MiLB experience, "
            "capable of generating swings and misses with power stuff. "
            "The bullpen may be a key strength for Panama's tournament run."
        ),
        "pitcher_ja": (
            "パナマの投手陣はMLB・マイナー経験者を含み、"
            "力強い球種で空振りを奪う能力が高い可能性がある。\n\n"
            "ブルペンの充実がトーナメントでの鍵になると考えられる。"
        ),
    },
    "col": {
        "name_en": "Colombia",
        "name_ja": "コロンビア",
        "flag": "\U0001F1E8\U0001F1F4",
        "var": "COL",
        "batter_en": (
            "Colombia continues to develop as a baseball nation, "
            "with a growing pipeline of MLB-caliber talent. "
            "The lineup may feature athletic hitters with speed and gap power, "
            "capable of manufacturing runs through contact and baserunning."
        ),
        "batter_ja": (
            "コロンビアはMLBへの選手輩出が増えており、"
            "身体能力の高い打者が揃う可能性がある。\n\n"
            "スピードとギャップを突く打撃でランを製造するスタイルが特徴と考えられる。"
        ),
        "pitcher_en": (
            "Colombia's pitching staff may include several active MLB arms "
            "with the ability to miss bats and generate weak contact. "
            "The overall depth of the pitching staff is a potential strength."
        ),
        "pitcher_ja": (
            "コロンビアの投手陣は現役MLB投手を複数含む可能性があり、"
            "空振りの奪取と弱い打球の誘発が得意な投手が揃うと考えられる。\n\n"
            "投手陣全体の層の厚さが強みとなる可能性がある。"
        ),
    },
    "pr": {
        "name_en": "Puerto Rico",
        "name_ja": "プエルトリコ",
        "flag": "\U0001F1F5\U0001F1F7",
        "var": "PR",
        "batter_en": (
            "Puerto Rico has a storied WBC history, featuring elite MLB talent "
            "throughout the lineup. Key contributors may include players with "
            "elite power and on-base skills, making Puerto Rico one of the "
            "most dangerous offensive teams in the field."
        ),
        "batter_ja": (
            "プエルトリコはWBCで輝かしい実績を持つ強豪で、"
            "打線にエリートMLB選手が揃うと考えられている。\n\n"
            "長打力と出塁率を兼ね備えた打者が中心となり、"
            "最も得点力の高いチームの一つになる可能性がある。"
        ),
        "pitcher_en": (
            "Puerto Rico's pitching staff has historically featured elite-level arms "
            "at every level of the roster. The rotation and bullpen combination "
            "may provide dominant coverage, with high strikeout potential "
            "and strong command throughout."
        ),
        "pitcher_ja": (
            "プエルトリコの投手陣は歴史的にエリートレベルの投手を多数擁してきた。\n\n"
            "高い奪三振能力と安定した制球力を持つ投手陣が"
            "トーナメントを通じて支配的な投球を見せる可能性がある。"
        ),
    },
    "twn": {
        "name_en": "Chinese Taipei",
        "name_ja": "チャイニーズタイペイ",
        "flag": "\U0001F1F9\U0001F1FC",
        "var": "TWN",
        "batter_en": (
            "Chinese Taipei features a lineup with strong contact-oriented hitters, "
            "drawing on players from NPB, CPBL, and MLB organizations. "
            "The team emphasizes plate discipline and situational hitting, "
            "and may pose a significant challenge through consistent contact and run manufacturing."
        ),
        "batter_ja": (
            "チャイニーズタイペイはNPB・CPBL・MLB組織の選手を擁するコンタクト重視の打線が特徴とされている。\n\n"
            "選球眼と状況に応じた打撃が持ち味で、"
            "コンスタントなコンタクトからの得点製造能力が高い可能性がある。"
        ),
        "pitcher_en": (
            "Chinese Taipei's pitching staff may feature arms from NPB and MLB organizations "
            "with strong command and diverse pitch mixes. "
            "The team has historically produced competitive pitching in international competition."
        ),
        "pitcher_ja": (
            "チャイニーズタイペイの投手陣はNPB・MLB組織出身の投手を含み、"
            "制球力と多彩な球種が特徴と考えられる。\n\n"
            "国際大会での実績もあり、安定した投球が期待される。"
        ),
    },
    "nic": {
        "name_en": "Nicaragua",
        "name_ja": "ニカラグア",
        "flag": "\U0001F1F3\U0001F1EE",
        "var": "NIC",
        "batter_en": (
            "Nicaragua is a developing baseball nation with a growing presence in international play. "
            "The lineup features players from the domestic league and professional organizations, "
            "with an emphasis on contact hitting and aggressive baserunning."
        ),
        "batter_ja": (
            "ニカラグアは成長著しい野球新興国であり、"
            "国内リーグとプロ組織の選手で構成されている。\n\n"
            "コンタクト打撃と積極的な走塁を重視するスタイルが特徴の可能性がある。"
        ),
        "pitcher_en": (
            "Nicaragua's pitching staff draws on domestic and professional-level arms. "
            "The key strength may lie in pitching efficiency and competitive spirit "
            "against stronger international opponents."
        ),
        "pitcher_ja": (
            "ニカラグアの投手陣は国内・プロレベルの投手で構成されており、"
            "効率的な投球と強豪への挑戦的な姿勢が特徴と考えられる。"
        ),
    },
    "aus": {
        "name_en": "Australia",
        "name_ja": "オーストラリア",
        "flag": "\U0001F1E6\U0001F1FA",
        "var": "AUS",
        "batter_en": (
            "Australia's baseball program continues to grow, featuring players "
            "from MLB organizations and professional leagues. "
            "The lineup may emphasize athletic hitters with the ability "
            "to make contact and take walks, backed by solid fundamental skills."
        ),
        "batter_ja": (
            "オーストラリアのベースボールプログラムは着実に成長しており、"
            "MLB組織やプロリーグ出身の選手で構成される見込みである。\n\n"
            "コンタクト能力と四球を組み合わせた攻撃的な打線が特徴の可能性がある。"
        ),
        "pitcher_en": (
            "Australia's pitching staff may include arms developed in MLB organizations, "
            "with competitive stuff and solid command. "
            "The team has shown improvement in pitching depth at recent international tournaments."
        ),
        "pitcher_ja": (
            "オーストラリアの投手陣はMLB組織で育成された投手を含む可能性があり、"
            "安定した制球力が特徴と考えられる。\n\n"
            "近年の国際大会では投手陣の層の厚さが増していると考えられる。"
        ),
    },
    "cuba": {
        "name_en": "Cuba",
        "name_ja": "キューバ",
        "flag": "\U0001F1E8\U0001F1FA",
        "var": "CUBA",
        "batter_en": (
            "Cuba has a legendary baseball tradition and fields a physically imposing lineup. "
            "The team historically emphasizes power hitting and aggressive approach at the plate. "
            "MLB-experienced Cuban players may bring elite-level talent to anchor the lineup."
        ),
        "batter_ja": (
            "キューバは野球の伝統国として長い歴史を誇り、"
            "身体的に強靭な打者が揃う打線が特徴とされている。\n\n"
            "積極的な打撃スタイルと長打力が持ち味で、"
            "MLB経験を持つキューバ系選手が打線の中心となる可能性がある。"
        ),
        "pitcher_en": (
            "Cuba's pitching tradition has produced numerous world-class arms. "
            "The staff may feature pitchers with elite velocity and power stuff, "
            "capable of dominating international competition when at their best."
        ),
        "pitcher_ja": (
            "キューバは数多くの世界クラスの投手を輩出してきた野球大国である。\n\n"
            "高い球速と力強い球種を持つ投手陣が国際舞台で"
            "支配的な投球を見せる可能性がある。"
        ),
    },
    "bra": {
        "name_en": "Brazil",
        "name_ja": "ブラジル",
        "flag": "\U0001F1E7\U0001F1F7",
        "var": "BRA",
        "batter_en": (
            "Brazil is an emerging baseball nation with a growing presence on the international stage. "
            "The lineup features players from the domestic league and professional organizations, "
            "with improving talent depth as the Brazilian baseball program continues to develop."
        ),
        "batter_ja": (
            "ブラジルは国際舞台での存在感を高めつつある新興野球国である。\n\n"
            "国内リーグとプロ組織の選手で構成されており、"
            "ブラジルの野球プログラムの成長とともに選手の質も向上していると考えられる。"
        ),
        "pitcher_en": (
            "Brazil's pitching staff reflects the nation's developing baseball infrastructure. "
            "The staff may feature competitive arms with solid fundamentals, "
            "aimed at keeping games close against more established baseball nations."
        ),
        "pitcher_ja": (
            "ブラジルの投手陣は同国の発展する野球インフラを反映している。\n\n"
            "基礎的な技術を持つ競争力ある投手が揃い、"
            "強豪国相手に接戦に持ち込む投球が期待される。"
        ),
    },
}

# Countries that have pitchers CSV (others only have batters)
HAS_PITCHERS_CSV = {
    "japan", "mex", "kor", "ned", "can", "ita", "isr", "gb", "pan", "col", "pr", "bra",
    "dr", "usa", "venezuela",
}


def _replace_strength_notes(result: str, en_text: str, ja_text: str) -> str:
    """Replace both EN and JA strength_note blocks (1st=EN, 2nd=JA)."""
    pat = re.compile(r'        "strength_note": \(\n.*?        \),', re.DOTALL)
    matches = list(pat.finditer(result))
    if len(matches) >= 2:
        # Replace in reverse order to preserve positions
        # Escape newlines so they stay as \n in the output Python file
        en_escaped = en_text.replace("\n", "\\n")
        ja_escaped = ja_text.replace("\n", "\\n")
        ja_new = f'        "strength_note": (\n            "{ja_escaped}"\n        ),'
        en_new = f'        "strength_note": (\n            "{en_escaped}"\n        ),'
        result = result[:matches[1].start()] + ja_new + result[matches[1].end():]
        result = result[:matches[0].start()] + en_new + result[matches[0].end():]
    return result


DR_FLAG_LITERAL = r"\U0001F1E9\U0001F1F4"


def _flag_escape(emoji: str) -> str:
    """Convert flag emoji to \\U escape form for Python source files."""
    return "".join(f"\\U{ord(c):08X}" for c in emoji)


def generate_batter_app(code: str, data: dict, template: str) -> str:
    c = data
    name_en = c["name_en"]
    name_ja = c["name_ja"]
    flag = c["flag"]
    var = c["var"]

    result = template

    # 1. Docstring
    result = result.replace(
        '"""WBC 2026 Dominican Republic Batter Scouting Dashboard."""',
        f'"""WBC 2026 {name_en} Batter Scouting Dashboard."""',
    )
    # 2. Import
    result = result.replace(
        "from players_dr_batters import DR_BATTERS, PLAYER_BY_NAME",
        f"from players_{code}_batters import {var}_BATTERS, PLAYER_BY_NAME",
    )
    # 3. EN title
    result = result.replace(
        '"title": "Dominican Republic Batter Scouting Report",',
        f'"title": "{name_en} Batter Scouting Report",',
    )
    # 4+6. EN & JA strength_note (both at once)
    result = _replace_strength_notes(result, c["batter_en"], c["batter_ja"])

    # 5. JA title
    result = result.replace(
        '"title": "ドミニカ共和国 打者スカウティングレポート",',
        f'"title": "{name_ja} 打者スカウティングレポート",',
    )

    # 7. DATA_PATH
    result = result.replace(
        '"data" / "dr_statcast.csv"',
        f'"data" / "{code}_statcast.csv"',
    )
    # 8. page_title
    result = result.replace(
        'page_title="Dominican Republic Scouting \u2014 WBC 2026",',
        f'page_title="{name_en} Scouting \u2014 WBC 2026",',
    )
    # 9. Flag emoji (literal \U escape in template → target country's \U escape)
    result = result.replace(DR_FLAG_LITERAL, _flag_escape(flag))
    # 10. Variable references
    result = result.replace("DR_BATTERS", f"{var}_BATTERS")

    return result


def generate_pitcher_app(code: str, data: dict, template: str) -> str:
    c = data
    name_en = c["name_en"]
    name_ja = c["name_ja"]
    flag = c["flag"]
    var = c["var"]

    result = template

    # 1. Docstring
    result = result.replace(
        '"""WBC 2026 Dominican Republic Pitching Scouting Dashboard."""',
        f'"""WBC 2026 {name_en} Pitching Scouting Dashboard."""',
    )
    # 2. Import
    result = result.replace(
        "from players_dr_pitchers import DR_PITCHERS, PITCHER_BY_NAME",
        f"from players_{code}_pitchers import {var}_PITCHERS, PITCHER_BY_NAME",
    )
    # 3. EN title
    result = result.replace(
        '"title": "Dominican Republic Pitching Scouting Report",',
        f'"title": "{name_en} Pitching Scouting Report",',
    )
    # 4+6. EN & JA strength_note (both at once)
    result = _replace_strength_notes(result, c["pitcher_en"], c["pitcher_ja"])

    # 5. JA title
    result = result.replace(
        '"title": "ドミニカ共和国 投手スカウティングレポート",',
        f'"title": "{name_ja} 投手スカウティングレポート",',
    )

    # 7. DATA_PATH
    result = result.replace(
        '"data" / "dr_pitchers_statcast.csv"',
        f'"data" / "{code}_pitchers_statcast.csv"',
    )
    # 8. page_title (template has literal \u2014 and also actual — em dash)
    result = result.replace(
        'page_title="Dominican Republic Pitching \\u2014 WBC 2026",',
        f'page_title="{name_en} Pitching \\u2014 WBC 2026",',
    )
    result = result.replace(
        'page_title="Dominican Republic Pitching \u2014 WBC 2026",',
        f'page_title="{name_en} Pitching \u2014 WBC 2026",',
    )
    # 9. Flag emoji (literal \U escape in template → target country's \U escape)
    result = result.replace(DR_FLAG_LITERAL, _flag_escape(flag))
    # 10. Variable references
    result = result.replace("DR_PITCHERS", f"{var}_PITCHERS")

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--country", default=None, help="Single country code to generate")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    batter_template = (ROOT / "app_dr.py").read_text(encoding="utf-8")
    pitcher_template = (ROOT / "app_dr_pitchers.py").read_text(encoding="utf-8")

    targets = [args.country] if args.country else list(COUNTRIES.keys())

    for code in targets:
        if code not in COUNTRIES:
            print(f"Unknown country: {code}")
            continue

        data = COUNTRIES[code]

        # Batter app
        out_batter = ROOT / f"app_{code}.py"
        if out_batter.exists() and not args.force:
            print(f"  SKIP (exists): app_{code}.py  (use --force to overwrite)")
        else:
            content = generate_batter_app(code, data, batter_template)
            out_batter.write_text(content, encoding="utf-8")
            print(f"  {'UPDATED' if out_batter.exists() else 'CREATED'}: app_{code}.py")

        # Pitcher app
        if code in HAS_PITCHERS_CSV:
            out_pitcher = ROOT / f"app_{code}_pitchers.py"
            if out_pitcher.exists() and not args.force:
                print(f"  SKIP (exists): app_{code}_pitchers.py  (use --force to overwrite)")
            else:
                content = generate_pitcher_app(code, data, pitcher_template)
                out_pitcher.write_text(content, encoding="utf-8")
                print(f"  {'UPDATED' if out_pitcher.exists() else 'CREATED'}: app_{code}_pitchers.py")
        else:
            print(f"  SKIP pitchers (no CSV): app_{code}_pitchers.py")


if __name__ == "__main__":
    main()
