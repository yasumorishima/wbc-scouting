"""The list of WBC apps for the static site, and the site's index page.

The dashboards themselves are pre-rendered by scripts/prerender.py (every widget state run once
at build time, so a page shows at once). This script
  list            prints the build matrix as JSON after the gates below: one entry per app and
                  shard (SHARDS splits a heavy app over several jobs);
  index OUT_DIR   writes OUT_DIR/index.html, apps.json and manifest/index.json, once every app's
                  pages are in OUT_DIR (stops if a dashboard's manifest is missing).

For each app the files it needs are found from the code, not listed by hand:
  - local modules: `import x` / `from x import ...` where x.py is in the repo root (followed transitively);
  - data: string literals "<name>.csv" in the app and its local modules, looked up in data/.
The build stops (exit 1) when
  - an app imports a third-party package the build does not install (only ALLOWED_THIRD_PARTY,
    see scripts/requirements-pages.txt);
  - a referenced CSV is missing, unless it is in EXPECTED_MISSING (the app then shows its no-data notice);
  - an app's country is not placed on the index page (scripts/index_data.json);
  - index_data.json says a country has batter or pitcher dashboards and the apps disagree (a
    dashboard counts only when its app exists and has its data).
The index (pools, venues, schedule, notes, in Japanese and English) comes from
scripts/index_data.json: moved on 2026-11-03 from the WBC page of the ICP site, which had copied
the table of the Caffeine index page used during the tournament.
Pages are named after the Streamlit Cloud subdomains (app_japan.py -> japan-batters.html, like
wbc-japan-batters.streamlit.app), so the old URL maps to the new one by name.

usage: python scripts/build_pages.py list | index OUT_DIR
"""
import ast
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWED_THIRD_PARTY = {"streamlit", "pandas", "numpy", "matplotlib", "matplotlib_fontja", "scipy"}
# Brazil's rosters have no MLB Statcast data; those apps show a notice and stop (fixed 2026-10-08).
EXPECTED_MISSING = {"bra_statcast.csv", "bra_pitchers_statcast.csv"}
OLD_APPS = {"app_pitchers.py"}
# Build jobs per dashboard (default 1). The quarterfinal app has two independent player selects
# (13 batters x 14 pitchers on each of 4 pages = 728 runs) and runs ~60 s per state on RPi5 even with
# every figure reused (its own plotting and tables: measured 2026-11-02), so it is split.
SHARDS = {"qf-jpn-ven": 8}

INDEX_DATA = json.loads((ROOT / "scripts" / "index_data.json").read_text(encoding="utf-8"))
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


def page_title(entry):
    tree = ast.parse((ROOT / entry).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "page_title" and isinstance(node.value, ast.Constant):
            return node.value.value
    return entry


INDEX = """<!doctype html>
<html lang="ja" data-lang="ja">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>WBC 2026 Scouting</title>
<script>
  // Language: the last choice on this device, else the browser's. Set before the first paint.
  (function () {{
    var l = null;
    try {{ l = localStorage.getItem("wbc-lang"); }} catch (e) {{}}
    if (l !== "ja" && l !== "en") l = /^ja\\b/i.test(navigator.language || "") ? "ja" : "en";
    document.documentElement.setAttribute("data-lang", l);
    document.documentElement.lang = l;
  }})();
</script>
<style>
  :root {{ --bg:#0e1117; --card:#1a1a2e; --text:#fafafa; --muted:#a0a4b0; --accent:#d32f2f; --line:#2c2f3f; }}
  * {{ box-sizing:border-box; }}
  html, body {{ background:var(--bg); }}
  body {{ margin:0; color:var(--text); font:16px/1.6 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif; }}
  [data-lang="ja"] .en, [data-lang="en"] .ja {{ display:none !important; }}
  main {{ max-width:960px; margin:0 auto; padding:24px 16px 48px; }}
  .top {{ display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap; }}
  h1 {{ font-size:1.6rem; margin:0 0 4px; }}
  .langs {{ display:flex; gap:4px; }}
  .langs button {{ min-height:44px; padding:0 14px; border:1px solid var(--line); border-radius:8px; background:transparent; color:var(--muted); font:inherit; cursor:pointer; }}
  .langs button[aria-pressed="true"] {{ background:var(--card); color:var(--text); border-color:var(--muted); }}
  p.lead {{ margin:0 0 6px; }}
  p.sub, p.small {{ color:var(--muted); font-size:.9rem; margin:0 0 12px; }}
  h2 {{ font-size:1.1rem; margin:28px 0 10px; border-left:4px solid var(--accent); padding-left:8px; }}
  h2 small {{ color:var(--muted); font-weight:400; margin-left:8px; font-size:.9rem; }}
  h3 {{ font-size:1rem; margin:18px 0 6px; }}
  details.sched {{ margin-top:20px; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:4px 14px; }}
  details.sched summary {{ cursor:pointer; font-weight:600; min-height:44px; display:flex; align-items:center; }}
  .scroll {{ overflow-x:auto; margin-bottom:12px; }}
  table {{ border-collapse:collapse; font-size:.85rem; }}
  th, td {{ border:1px solid var(--line); padding:6px 8px; text-align:left; vertical-align:top; white-space:nowrap; }}
  thead th {{ background:#12141f; }}
  td small, th small {{ display:block; color:var(--muted); font-size:.75rem; }}
  ul.grid {{ list-style:none; padding:0; margin:0; display:grid; gap:10px; grid-template-columns:repeat(auto-fill,minmax(260px,1fr)); }}
  ul.grid > li {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 14px; }}
  .name {{ font-weight:600; margin-bottom:8px; display:flex; align-items:center; gap:8px; }}
  .code {{ font-size:.75rem; font-weight:700; letter-spacing:.05em; padding:2px 6px; border-radius:4px; border:1px solid var(--line); color:var(--muted); }}
  .links {{ display:flex; gap:8px; }}
  .links a, .links .none {{ flex:1; text-align:center; padding:8px 6px; border-radius:8px; text-decoration:none; }}
  .links a {{ background:var(--accent); color:#fff; }}
  a:focus-visible, button:focus-visible, summary:focus-visible, .scroll:focus-visible {{ outline:3px solid #fff; outline-offset:2px; }}
  .links .none {{ border:1px dashed var(--line); color:var(--muted); font-size:.9rem; }}
  ul.notes {{ color:var(--muted); font-size:.9rem; padding-left:1.2em; }}
  footer {{ margin-top:24px; color:var(--muted); font-size:.85rem; }}
  footer a {{ color:var(--muted); }}
</style>
</head>
<body>
<main>
  <div class="top">
    <h1>{title}</h1>
    <div class="langs" role="group" aria-label="Language / 言語">
      <button type="button" data-l="ja" lang="ja">日本語</button><button type="button" data-l="en" lang="en">English</button>
    </div>
  </div>
  <p class="lead">{lede}</p>
  <p class="sub">{sub}</p>
{body}
  <footer>{count} {credit} {made}
  <a href="https://github.com/yasumorishima/wbc-scouting">{source}</a></footer>
</main>
<script>
  (function () {{
    var root = document.documentElement, buttons = document.querySelectorAll(".langs button");
    function show() {{
      buttons.forEach(function (b) {{ b.setAttribute("aria-pressed", String(b.dataset.l === root.dataset.lang)); }});
    }}
    buttons.forEach(function (b) {{
      b.addEventListener("click", function () {{
        root.dataset.lang = b.dataset.l; root.lang = b.dataset.l;
        try {{ localStorage.setItem("wbc-lang", b.dataset.l); }} catch (e) {{}}
        show();
      }});
    }});
    show();
  }})();
</script>
</body>
</html>
"""

LOCAL_TIME = re.compile(r"^(.+?)(\(\d{1,2}/\d{1,2} [^)]*\b(?:AST|CT|ET)\))$")


def esc(text):
    return html.escape(str(text))


def bi(key_or_pair, tag="span"):
    """The same text in both languages; CSS shows the chosen one."""
    if isinstance(key_or_pair, str):
        ja, en = INDEX_DATA["text"]["ja"][key_or_pair], INDEX_DATA["text"]["en"][key_or_pair]
    else:
        ja, en = key_or_pair
    return f'<{tag} class="ja" lang="ja">{esc(ja)}</{tag}><{tag} class="en" lang="en">{esc(en)}</{tag}>'


def cell(tag, text, extra=""):
    """A schedule cell; a game's local time in parentheses goes on its own small line."""
    m = LOCAL_TIME.match(text)
    inner = f"{esc(m.group(1))}<small>{esc(m.group(2))}</small>" if m else esc(text)
    return f"<{tag}{extra}>{inner}</{tag}>"


def schedule_table(rows, label_key, lang):
    head = "".join(cell("th", t, ' scope="col"') for t in rows[0])
    games, body = rows[1:], []
    for i, row in enumerate(games):
        tds = []
        if row[0]:
            # one heading cell per day, spanning that day's games
            span = 1
            while i + span < len(games) and not games[i + span][0]:
                span += 1
            tds.append(cell("th", row[0], f' scope="rowgroup" rowspan="{span}"'))
        tds += [cell("td", t) for t in row[1:]]
        body.append(f"<tr>{''.join(tds)}</tr>")
    label = esc(INDEX_DATA["text"][lang][label_key])
    return (f'<div class="scroll {lang}" lang="{lang}" tabindex="0" role="region" aria-label="{label}">'
            f'<table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')


def has_dashboard(by_slug, slug):
    """Listed only when the app exists and has its data (Brazil's apps only show a no-data notice)."""
    a = by_slug.get(slug)
    return bool(a) and not a["missing_csv"]


def index_html(apps):
    by_slug = {a["slug"]: a for a in apps}
    sched = INDEX_DATA["schedule"]
    rows = ['  <details class="sched">', f"    <summary>{bi('wb_schedule')}</summary>",
            f"    <h3>{bi('wb_round1')}</h3>", f'    <p class="small">{bi("wb_tz")}</p>']
    rows += ["    " + schedule_table(sched[lang][0], "wb_round1", lang) for lang in ("ja", "en")]
    rows.append(f"    <h3>{bi('wb_knockout')}</h3>")
    rows += ["    " + schedule_table(sched[lang][1], "wb_knockout", lang) for lang in ("ja", "en")]
    rows.append("  </details>")
    mismatched, placed = [], set()
    for pool in INDEX_DATA["pools"]:
        rows.append(f'  <h2>Pool {esc(pool["id"])}<small>{bi((pool["venueJa"], pool["venueEn"]))}</small></h2>')
        rows.append('  <ul class="grid">')
        for team in pool["teams"]:
            c = team["slug"]
            have = {r: has_dashboard(by_slug, f"{c}-{r}") for r in ("batters", "pitchers")}
            placed.update(f"{c}-{r}" for r in ("batters", "pitchers"))
            for r in have:
                if have[r] != bool(team[r]):
                    mismatched.append(f"{c}-{r}: index_data.json says {team[r]}, the apps say {have[r]}")
            if not any(have.values()):
                links = f'<span class="none">{bi("wb_noData", "b")}<br>{bi("wb_noMlb")}</span>'
            else:
                links = "".join(
                    f'<a href="{c}-{r}.html">{bi("wb_" + r)}</a>' if have[r]
                    else f'<span class="none">{bi("wb_no" + r.capitalize())}</span>'
                    for r in ("batters", "pitchers"))
            rows.append(f'    <li><div class="name"><span class="code">{esc(team["code"])}</span>'
                        f'{bi((team["ja"], team["en"]))}</div><div class="links">{links}</div></li>')
        rows.append("  </ul>")
    extra = [a for a in apps if a["slug"].startswith("qf-")]
    if extra:
        rows.append(f'  <h2>{bi("wb_qfTitle")}</h2>\n  <ul class="grid">')
        for a in extra:
            rows.append(f'    <li><div class="name"><span class="code">QF</span>{bi("wb_qfName")}</div>'
                        f'<div class="links"><a href="{a["slug"]}.html">{bi("wb_qfOpen")}</a></div></li>')
        rows.append("  </ul>")
    rows.append(f'  <h2>{bi("wb_notes")}</h2>\n  <ul class="notes">')
    rows += [f"    <li>{bi(k)}</li>" for k in ("wb_note1", "wb_note2", "wb_note3", "wb_note4")]
    rows.append("  </ul>")
    unlisted = [a["slug"] for a in apps if a["slug"] not in placed and not a["slug"].startswith("qf-")]
    n = sum(1 for a in apps if not a["missing_csv"])
    page = INDEX.format(title=bi("wb_title"), lede=bi("wb_lede"), sub=bi("wb_sub"), body="\n".join(rows),
                        count=bi((f"ダッシュボード {n} 本。", f"{n} dashboards.")), credit=bi("wb_credit"),
                        made=bi(("どの画面も Streamlit アプリから作り置きしたものです。", "Every view is pre-rendered from the Streamlit apps.")), source=bi("wb_source"))
    return page, unlisted, mismatched


def checked_apps():
    errors, apps = [], []
    found = wbc_apps()
    if not found:
        errors.append("no app_*.py found")
    for slug, entry in found:
        py, csv = dependencies(entry, errors)
        present = [c for c in csv if (ROOT / "data" / c).exists()]
        missing = [c for c in csv if c not in present]
        for c in missing:
            if c not in EXPECTED_MISSING:
                errors.append(f"{slug}: data/{c} is referenced but missing")
        apps.append({"slug": slug, "entry": entry, "title": page_title(entry), "py": sorted(py),
                     "csv": present, "missing_csv": missing})
    index, unlisted, mismatched = index_html(apps) if apps else ("", [], [])
    for s in unlisted:
        errors.append(f"{s}: not placed on the index page (add its country to scripts/index_data.json)")
    errors += mismatched
    if errors:
        print("BUILD STOPPED:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)
    return apps, index


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "index"):
        sys.exit(__doc__)
    apps, index = checked_apps()
    if sys.argv[1] == "list":
        print(json.dumps([{"slug": a["slug"], "entry": a["entry"], "shard": i, "of": SHARDS.get(a["slug"], 1)}
                          for a in apps for i in range(SHARDS.get(a["slug"], 1))]))
        return
    out = Path(sys.argv[2]).resolve()
    missing = [a["slug"] for a in apps
               if not (out / "manifest" / f"{a['slug']}.json").exists() or not (out / f"{a['slug']}.html").exists()]
    if missing:
        sys.exit(f"BUILD STOPPED: no pre-rendered pages for {', '.join(missing)}")
    (out / "index.html").write_text(index, encoding="utf-8")
    (out / "apps.json").write_text(json.dumps(apps, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "manifest" / "index.json").write_text(
        json.dumps({"slugs": [a["slug"] for a in apps], "ext": "avif"}), encoding="utf-8")
    (out / ".nojekyll").touch()
    print(f"index for {len(apps)} dashboards in {out}")
    for a in apps:
        note = f"  (missing, no-data notice expected: {', '.join(a['missing_csv'])})" if a["missing_csv"] else ""
        print(f"  {a['slug']:<20} {a['entry']:<26} py={len(a['py'])} csv={len(a['csv'])}{note}")


if __name__ == "__main__":
    main()
