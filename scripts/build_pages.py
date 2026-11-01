"""Build the static site: every WBC app in streamlit_apps.txt as a stlite page, plus an index.

stlite (https://github.com/whitphx/stlite, Apache-2.0) runs the unchanged Streamlit app in the
browser with Pyodide, so the pages need no server and never sleep.

For each app the files it needs are found from the code, not listed by hand:
  - local modules: `import x` / `from x import ...` where x.py is in the repo root (followed transitively);
  - data: string literals "<name>.csv" in the app and its local modules, looked up in data/.
The build stops (exit 1) when
  - an app imports a third-party package the page does not install (only ALLOWED_THIRD_PARTY);
  - a referenced CSV is missing, unless it is in EXPECTED_MISSING (the app then shows its no-data notice);
  - an app's country is not placed on the index page (POOLS).
Pages are named after the Streamlit Cloud subdomains (app_japan.py -> japan-batters.html, like
wbc-japan-batters.streamlit.app), so the old URL maps to the new one by name.

usage: python scripts/build_pages.py [out_dir=_site]
"""
import ast
import html
import json
import re
import shutil
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STLITE = "@stlite/browser@1.12.0"
# Packages given to every page (Pyodide / micropip installs them).
# matplotlib/scipy come from the Pyodide release stlite pins; the PyPI wheel is pinned here so a new
# release cannot change all pages without a rebuild and check.
REQUIREMENTS = ["matplotlib", "scipy", "matplotlib-fontja==1.1.0"]
ALLOWED_THIRD_PARTY = {"streamlit", "pandas", "numpy", "matplotlib", "matplotlib_fontja", "scipy"}
# Brazil's rosters have no MLB Statcast data; those apps show a notice and stop (fixed 2026-10-08).
EXPECTED_MISSING = {"bra_statcast.csv", "bra_pitchers_statcast.csv"}
OLD_APPS = {"app_pitchers.py"}

POOLS = [
    ("Pool A", ["pr", "cuba", "can", "pan", "col"]),
    ("Pool B", ["usa", "mex", "ita", "gb", "bra"]),
    ("Pool C", ["japan", "kor", "twn", "aus"]),
    ("Pool D", ["dr", "venezuela", "ned", "isr", "nic"]),
]
COUNTRY = {
    "pr": ("プエルトリコ", "Puerto Rico"), "cuba": ("キューバ", "Cuba"), "can": ("カナダ", "Canada"),
    "pan": ("パナマ", "Panama"), "col": ("コロンビア", "Colombia"), "usa": ("アメリカ", "USA"),
    "mex": ("メキシコ", "Mexico"), "ita": ("イタリア", "Italy"), "gb": ("イギリス", "Great Britain"),
    "bra": ("ブラジル", "Brazil"), "japan": ("日本", "Japan"), "kor": ("韓国", "Korea"),
    "twn": ("チャイニーズ・タイペイ", "Chinese Taipei"), "aus": ("オーストラリア", "Australia"),
    "dr": ("ドミニカ共和国", "Dominican Republic"), "venezuela": ("ベネズエラ", "Venezuela"),
    "ned": ("オランダ", "Netherlands"), "isr": ("イスラエル", "Israel"), "nic": ("ニカラグア", "Nicaragua"),
}
CSV_RE = re.compile(r"""["']([A-Za-z0-9_.-]+\.csv)["']""")
STDLIB = set(sys.stdlib_module_names)


def wbc_apps():
    """(slug, file) for every app_*.py; slug = the Streamlit Cloud subdomain wbc-<slug>.

    app.py / app_pitchers.py are the older Venezuela apps (superseded by app_venezuela*.py); not pages.
    """
    out = []
    for path in sorted(ROOT.glob("app_*.py")):
        if path.name in OLD_APPS:
            continue
        stem = path.stem[len("app_"):]
        if stem.startswith("qf_"):
            slug = stem.replace("_", "-")
        elif stem.endswith("_pitchers"):
            slug = stem[: -len("_pitchers")] + "-pitchers"
        else:
            slug = stem + "-batters"
        out.append((slug, path.name))
    return out


def top_imports(path):
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def dependencies(entry, errors):
    py, csv, seen, todo = [], set(), set(), [entry]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        path = ROOT / name
        py.append(name)
        csv |= set(CSV_RE.findall(path.read_text(encoding="utf-8")))
        for mod in sorted(top_imports(path)):
            if (ROOT / f"{mod}.py").exists():
                todo.append(f"{mod}.py")
            elif mod not in STDLIB and mod not in ALLOWED_THIRD_PARTY:
                errors.append(f"{entry}: imports '{mod}' (not a repo module, not stdlib, not in ALLOWED_THIRD_PARTY)")
    return py, sorted(csv)


def streamlit_config():
    theme = tomllib.loads((ROOT / ".streamlit" / "config.toml").read_text())["theme"]
    # The file has no `base`; without base=dark stlite drew dark headings on the dark background
    # (pilot, 2026-11-01), while Streamlit Cloud showed them light.
    theme.setdefault("base", "dark")
    return {f"theme.{k}": v for k, v in theme.items()}


def page_title(entry):
    tree = ast.parse((ROOT / entry).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "page_title" and isinstance(node.value, ast.Constant):
            return node.value.value
    return entry


PAGE = """<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/{stlite}/build/stlite.css" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module">
      // Generated by scripts/build_pages.py from {entry}. The Streamlit app runs unchanged in the
      // browser with stlite (Pyodide): no server, nothing to sleep, nothing to keep alive.
      import {{ mount }} from "https://cdn.jsdelivr.net/npm/{stlite}/build/stlite.js";
      mount({config}, document.getElementById("root"));
    </script>
  </body>
</html>
"""

INDEX = """<!doctype html>
<html lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>WBC 2026 Scouting</title>
<style>
  :root {{ --bg:#0e1117; --card:#1a1a2e; --text:#fafafa; --muted:#a0a4b0; --accent:#d32f2f; --line:#2c2f3f; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text); font:16px/1.6 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif; }}
  main {{ max-width:960px; margin:0 auto; padding:24px 16px 48px; }}
  h1 {{ font-size:1.6rem; margin:0 0 4px; }}
  p.lead {{ color:var(--muted); margin:0 0 24px; }}
  h2 {{ font-size:1.1rem; margin:28px 0 10px; border-left:4px solid var(--accent); padding-left:8px; }}
  ul.grid {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); }}
  li {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 14px; }}
  .name {{ font-weight:600; margin-bottom:8px; }}
  .name small {{ display:block; color:var(--muted); font-weight:400; font-size:.85rem; }}
  .links {{ display:flex; gap:8px; }}
  .links a, .links .none {{ flex:1; text-align:center; padding:8px 6px; border-radius:8px; text-decoration:none; }}
  .links a {{ background:var(--accent); color:#fff; }}
  .links a:focus-visible {{ outline:3px solid #fff; outline-offset:2px; }}
  .links .none {{ border:1px dashed var(--line); color:var(--muted); }}
  .links small {{ font-size:.8rem; opacity:.85; }}
  footer {{ margin-top:36px; color:var(--muted); font-size:.85rem; }}
  footer a {{ color:var(--muted); }}
</style>
</head>
<body>
<main>
  <h1>WBC 2026 スカウティング</h1>
  <p class="lead">国と打者・投手を選ぶと、MLB Statcast（2024〜2025）から作った分析が開きます。最初の表示は 15〜35 秒ほどかかります（ブラウザの中で Python を起動するため）。<br>
  Pick a country and batters or pitchers. Each dashboard is built from MLB Statcast 2024–2025; the first load takes 15–35 s because Python starts inside your browser.</p>
{body}
  <footer>{n} dashboards. Data: Baseball Savant Statcast (via pybaseball). Runs in the browser with <a href="https://github.com/whitphx/stlite">stlite</a>.
  Source: <a href="https://github.com/yasumorishima/wbc-scouting">github.com/yasumorishima/wbc-scouting</a>. Not affiliated with MLB or WBC.</footer>
</main>
</body>
</html>
"""


def index_html(apps):
    by_slug = {a["slug"]: a for a in apps}
    rows = []
    for pool, countries in POOLS:
        rows.append(f'  <h2>{pool}</h2>\n  <ul class="grid">')
        for c in countries:
            links = []
            for role, ja, en in (("batters", "打者", "Batters"), ("pitchers", "投手", "Pitchers")):
                a = by_slug.get(f"{c}-{role}")
                if a:
                    links.append(f'<a href="{a["slug"]}.html">{ja} <small>{en}</small></a>')
                else:
                    links.append(f'<span class="none">{ja} <small>なし / none</small></span>')
            ja, en = COUNTRY[c]
            rows.append(f'    <li><div class="name">{html.escape(ja)}<small>{html.escape(en)}</small></div>'
                        f'<div class="links">{"".join(links)}</div></li>')
        rows.append("  </ul>")
    extra = [a for a in apps if a["slug"].startswith("qf-")]
    if extra:
        rows.append('  <h2>準々決勝 Quarterfinal</h2>\n  <ul class="grid">')
        for a in extra:
            rows.append('    <li><div class="name">日本 対 ベネズエラ<small>Japan vs Venezuela</small></div>'
                        f'<div class="links"><a href="{a["slug"]}.html">開く <small>Open</small></a></div></li>')
        rows.append("  </ul>")
    listed = {f"{c}-{r}" for _, cs in POOLS for c in cs for r in ("batters", "pitchers")}
    unlisted = [a["slug"] for a in apps if a["slug"] not in listed and not a["slug"].startswith("qf-")]
    return INDEX.format(body="\n".join(rows), n=len(apps)), unlisted


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    errors, apps = [], []
    found = wbc_apps()
    if not found:
        errors.append("no app_*.py found")
    theme = streamlit_config()
    for slug, entry in found:
        py, csv = dependencies(entry, errors)
        present = [c for c in csv if (ROOT / "data" / c).exists()]
        missing = [c for c in csv if c not in present]
        for c in missing:
            if c not in EXPECTED_MISSING:
                errors.append(f"{slug}: data/{c} is referenced but missing")
        apps.append({"slug": slug, "entry": entry, "title": page_title(entry), "py": sorted(py),
                     "csv": present, "missing_csv": missing})
    index, unlisted = index_html(apps) if apps else ("", [])
    for s in unlisted:
        errors.append(f"{s}: not placed on the index page (add its country to POOLS)")
    if errors:
        print("BUILD STOPPED:\n  " + "\n  ".join(errors))
        sys.exit(1)

    if out.exists():
        shutil.rmtree(out)
    (out / "app" / "data").mkdir(parents=True)
    for name in sorted({p for a in apps for p in a["py"]}):
        shutil.copy2(ROOT / name, out / "app" / name)
    for name in sorted({c for a in apps for c in a["csv"]}):
        shutil.copy2(ROOT / "data" / name, out / "app" / "data" / name)
    for a in apps:
        files = {p: {"url": f"./app/{p}"} for p in a["py"]}
        files.update({f"data/{c}": {"url": f"./app/data/{c}"} for c in a["csv"]})
        config = {"requirements": REQUIREMENTS, "entrypoint": a["entry"], "streamlitConfig": theme, "files": files}
        (out / f"{a['slug']}.html").write_text(PAGE.format(
            title=html.escape(a["title"]), stlite=STLITE, entry=a["entry"],
            config=json.dumps(config, ensure_ascii=False, indent=2)), encoding="utf-8")
    (out / "index.html").write_text(index, encoding="utf-8")
    (out / "apps.json").write_text(json.dumps(apps, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / ".nojekyll").touch()
    print(f"built {len(apps)} pages into {out}")
    for a in apps:
        note = f"  (missing, no-data notice expected: {', '.join(a['missing_csv'])})" if a["missing_csv"] else ""
        print(f"  {a['slug']:<20} {a['entry']:<26} py={len(a['py'])} csv={len(a['csv'])}{note}")


if __name__ == "__main__":
    main()
