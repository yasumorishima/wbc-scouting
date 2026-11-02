"""Pre-render WBC apps into static pages: every widget state is run once at build time, so a page
shows at once (no Python in the browser, nothing to wait for).

The unchanged app is executed with a recording stand-in for `streamlit` (st_record.py). Its figures
come from the app's own matplotlib code; the HTML carries Streamlit's data-testid attributes, so the
app's own CSS applies.

States:
  outer = every combination of the sidebar widgets (language, player, season) -> one HTML page each;
  inner = every combination of the main-area widgets (stadium, density, pitch type, ...), found by
          depth-first search, so a widget whose options depend on an earlier one is handled.
The main body of each inner state is cut into segments before each block that holds a widget;
segments are deduplicated by content, and a small script swaps them when a widget changes.

usage: python scripts/prerender.py OUT_DIR APP.py [APP.py ...] [--jobs N] [--only-default]
       python scripts/prerender.py OUT_DIR APP.py --shard i/n   (one build job of a split app)
       python scripts/prerender.py OUT_DIR --assemble           (once every shard's part is in OUT_DIR)
writes OUT_DIR/<slug>.html, OUT_DIR/<slug>/<state>.html, OUT_DIR/img/<hash>.<ext>,
       OUT_DIR/manifest/<slug>.json (states, figures, text digests; read by the checks);
       with --shard only OUT_DIR/img and OUT_DIR/parts/<slug>.<i>.json
"""
import argparse
import hashlib
import html
import io
import json
import os
import re
import runpy
import sys
import time
import types
from concurrent.futures import ProcessPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import render_html  # noqa: E402
import st_record  # noqa: E402

# AVIF with full colour resolution: the default 4:2:0 smeared small red/blue heatmap labels (worst
# 16px tile error 18 vs 5.3 at 4:4:4 q75, ~25KB per figure; lossless WebP was 42KB). Measured
# 2026-11-02 on 28 pitcher figures.
IMG_EXT = "avif"
AVIF = {"quality": 75, "subsampling": "4:4:4"}

_state = types.SimpleNamespace(run=None, app=None, out=None, written={})


# ----------------------------------------------------------------------------- one run
def _init_worker(out):
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    _state.st = st_record.make_module(_state)
    sys.modules["streamlit"] = _state.st
    _state.out = Path(out)
    import matplotlib
    matplotlib.use("Agg")


def image_info(sha, png):
    """Encode and write img/<sha>.avif once per process (another process may write the same file:
    same content, written to a temporary name and renamed)."""
    if sha not in _state.written:
        from PIL import Image
        im = Image.open(io.BytesIO(png))
        name = f"{sha}.{IMG_EXT}"
        path = _state.out / "img" / name
        if not path.exists():
            buf = io.BytesIO()
            im.convert("RGB").save(buf, "AVIF", **AVIF)
            tmp = path.with_name(f".{name}.{os.getpid()}")
            tmp.write_bytes(buf.getvalue())
            os.replace(tmp, path)
        _state.written[sha] = (name, im.width, im.height)
    return _state.written[sha]


def table_html(data, kw):
    """st.dataframe -> an HTML table. Styler keeps its formats; the uuid is made from the content so
    the same table hashes the same in every run."""
    hide_index = kw.get("hide_index")
    if hasattr(data, "to_html") and hasattr(data, "set_uuid"):  # pandas Styler
        styler = data
        if hide_index:
            styler = styler.hide(axis="index")
        styler.set_uuid("t")
        first = styler.to_html()
        styler.set_uuid("t" + hashlib.sha1(first.encode()).hexdigest()[:8])
        return styler.to_html()
    import pandas as pd
    if isinstance(data, pd.Series):
        data = data.to_frame()
    if isinstance(data, pd.DataFrame):
        return data.to_html(index=not hide_index, border=0, na_rep="None")
    return html.escape(str(data))


def run_app(app, choices):
    import matplotlib.pyplot as plt
    if _state.app != app:  # a new app: nothing cached for the previous one may carry over
        _state.st._clear_cache()
        _state.app = app
    _state.run = st_record.Run(dict(choices), table_html)
    try:
        runpy.run_path(str(ROOT / app), run_name="__main__")
    except st_record.Stop:
        _state.run.stopped = True
    finally:
        plt.close("all")
    return _state.run


def default_first(widget):
    return [widget["default"]] + [i for i in range(len(widget["options"])) if i != widget["default"]]


def explore(app, prefix):
    """All leaves below `prefix` (dict widget id -> option index), depth-first over the widgets in
    the order the script creates them. The run with the next widget at its default is reused as that
    branch, so every leaf costs exactly one run. Each leaf is rendered (and its pictures written)
    as soon as it is reached; only html and hashes go back to the parent."""
    out = []

    def leaf(run):
        page = render_html.render_leaf(run, render_html.Renderer(image_info, "@P@"))
        out.append({"choices": {w["id"]: w["choice"] for w in run.widgets}, "widgets": run.widgets,
                    "page": run.page, "stopped": run.stopped, "sidebar": page["sidebar"],
                    "root": page["root"], "segments": page["segments"],
                    "images": list(_iter_images(run.main.items))})

    def dfs(choices, run):
        nxt = next((w for w in run.widgets if w["id"] not in choices), None)
        if nxt is None:
            leaf(run)
            return
        for i in default_first(nxt):  # so the first leaf of every group is its default state
            c = {**choices, nxt["id"]: i}
            dfs(c, run if i == nxt["default"] else run_app(app, c))

    dfs(dict(prefix), run_app(app, prefix))
    return out


def _iter_images(items):
    for it in items:
        if it[0] == "image":
            yield it[1]
        for x in it:
            if isinstance(x, st_record.Box):
                yield from _iter_images(x.items)
            elif isinstance(x, list):
                for y in x:
                    if isinstance(y, st_record.Box):
                        yield from _iter_images(y.items)


def explore_task(args):
    return explore(*args)


# ----------------------------------------------------------------------------- page assembly
CSS = (HERE / "prerender_page.css").read_text(encoding="utf-8")
JS = (HERE / "prerender_page.js").read_text(encoding="utf-8")
# Streamlit's own typeface (OFL); display=swap, so text shows at once in the fallback font.
FONT = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap">')


PLACEHOLDER = re.compile(r'<div class="seg" data-seg="([0-9c.]+)"></div>')


def outer_key(choices):
    return "-".join(str(choices[k]) for k in sorted(choices, key=lambda k: int(k[1:])) if k.startswith("s"))


def split_prefixes(app, pool, target):
    """Split the search on the first widgets (language, player, ...) until there are `target`
    subtrees (or 4 levels); each is then searched by one task. Depth-first order, so the first
    prefix holds the all-defaults state. Deterministic: every shard of an app computes the same list."""
    prefixes = [{}]
    for _ in range(4):
        if len(prefixes) >= target:
            break
        grown = []
        for p, widgets in zip(prefixes, pool.map(widgets_task, [(app, p) for p in prefixes])):
            nxt = next((w for w in widgets if w["id"] not in p), None)
            grown += [p] if nxt is None else [{**p, nxt["id"]: i} for i in default_first(nxt)]
        if grown == prefixes:
            break
        prefixes = grown
    return prefixes


def render_shard(app, slug, out, pool, jobs, shard=0, of=1, only_default=False):
    """Run every state below this shard's prefixes (every of-th prefix) and write the figures to
    out/img and the states to out/parts/<slug>.<shard>.json (segments deduplicated)."""
    t0 = time.time()
    prefixes = split_prefixes(app, pool, 3 * jobs * of)
    if only_default:  # the default page only, but all of its main-area states
        side = {k: v for k, v in prefixes[0].items() if k.startswith("s")}
        prefixes = [p for p in prefixes if {k: v for k, v in p.items() if k.startswith("s")} == side]
    mine = [i for i in range(len(prefixes)) if i % of == shard]
    templates, leaves = {}, []
    for i, found in zip(mine, pool.map(explore_task, [(app, prefixes[i]) for i in mine])):
        for leaf in found:
            ids = []
            for path, seg in leaf["segments"]:
                tid = "t" + hashlib.sha1(seg.encode()).hexdigest()[:12]
                if templates.setdefault(tid, seg) != seg:
                    raise RuntimeError(f"{slug}: template id collision {tid}")
                ids.append([path, tid])
            leaves.append({**leaf, "segments": ids, "pi": i})
    part = {"app": app, "slug": slug, "shard": shard, "of": of, "only_default": only_default,
            "prefixes": prefixes, "mine": mine, "templates": templates, "leaves": leaves}
    (out / "parts").mkdir(parents=True, exist_ok=True)
    (out / "parts" / f"{slug}.{shard}.json").write_text(json.dumps(part, ensure_ascii=False), encoding="utf-8")
    print(f"{slug} shard {shard}/{of}: {len(mine)} of {len(prefixes)} subtrees, {len(leaves)} states, "
          f"{len(templates)} segments, {time.time() - t0:.0f}s", flush=True)


def assemble(out):
    """Every app whose parts are all in out/parts -> its pages and manifest; the parts are removed.
    Stops when a shard is missing or the shards disagree."""
    parts = {}
    for f in sorted((out / "parts").glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        parts.setdefault(p["slug"], []).append(p)
    if not parts:
        raise RuntimeError(f"no parts in {out / 'parts'}")
    for slug, ps in parts.items():
        of = ps[0]["of"]
        if sorted(p["shard"] for p in ps) != list(range(of)):
            raise RuntimeError(f"{slug}: shards {sorted(p['shard'] for p in ps)} of {of}")
        if any(p["prefixes"] != ps[0]["prefixes"] or p["app"] != ps[0]["app"] or p["of"] != of
               or p["only_default"] != ps[0]["only_default"] for p in ps):
            raise RuntimeError(f"{slug}: the shards split the search differently")
        if sorted(i for p in ps for i in p["mine"]) != list(range(len(ps[0]["prefixes"]))):
            raise RuntimeError(f"{slug}: the shards do not cover every subtree exactly once")
        templates = {}
        for p in ps:
            for tid, seg in p["templates"].items():
                if templates.setdefault(tid, seg) != seg:
                    raise RuntimeError(f"{slug}: template id collision {tid}")
        # depth-first order again: by subtree, and within a subtree as found
        leaves = [leaf for p in ps for leaf in p["leaves"]]
        leaves.sort(key=lambda leaf: leaf["pi"])
        assemble_app(ps[0]["app"], slug, out, leaves, templates, ps[0]["only_default"])
    for f in (out / "parts").glob("*.json"):
        f.unlink()
    (out / "parts").rmdir()


def assemble_app(app, slug, out, all_leaves, all_templates, only_default=False):
    groups = {}
    for leaf in all_leaves:
        o = {k: v for k, v in leaf["choices"].items() if k.startswith("s")}
        groups.setdefault(outer_key(o), (o, []))[1].append(leaf)
    if only_default:
        first_key = next(iter(groups))
        groups = {first_key: groups[first_key]}

    default_key = next(iter(groups))  # depth-first: every widget at its default
    pages, manifest = {}, {"app": app, "slug": slug, "default": default_key, "states": []}
    for key, (o, leaves) in groups.items():
        variants, opts = [], []
        ids_used = {t for leaf in leaves for _, t in leaf["segments"]}
        templates = {t: all_templates[t] for t in ids_used}
        for leaf in leaves:
            ids = leaf["segments"]
            inner = {k: v for k, v in leaf["choices"].items() if k.startswith("m")}
            # each widget's option list: with its label, what makes it "the same widget" as before
            # (Streamlit keeps a widget's value only while label and options stay the same)
            o_idx = {}
            for w in leaf["widgets"]:
                if w["id"].startswith("m"):
                    if w["options"] not in opts:
                        opts.append(w["options"])
                    o_idx[w["id"]] = opts.index(w["options"])
            variants.append({"c": inner, "s": ids, "o": o_idx})
            manifest["states"].append({"outer": key, "choices": leaf["choices"], "inner": inner,
                                       "images": leaf["images"], "stopped": leaf["stopped"], "segments": ids,
                                       "text": text_digest(fill_main(leaf["root"], templates, dict(ids)))})
        first = leaves[0]  # depth-first: the first leaf has every main widget at its default
        mains = [w for leaf in leaves for w in leaf["widgets"] if w["id"].startswith("m")]
        defaults = {w["id"]: w["default"] for w in mains}
        labels = {w["id"]: w["label"] for w in mains}
        if any(labels[w["id"]] != w["label"] or defaults[w["id"]] != w["default"] for w in mains):
            raise RuntimeError(f"{slug} {key}: a main-area widget changes label or default between states")
        check_reachable(slug, key, variants, opts, defaults)
        pages[key] = (o, first, templates, variants, defaults, labels, opts)
        manifest.setdefault("sidebar_text", {})[key] = text_digest(first["sidebar"])

    sidebar_ids = sorted({k for o, _ in groups.values() for k in o}, key=lambda k: int(k[1:]))
    nav = {"states": [{"k": k, "c": v[0]} for k, v in pages.items()], "default": default_key,
           "slug": slug, "sidebar": sidebar_ids}
    (out / slug).mkdir(parents=True, exist_ok=True)
    for key, (o, first, templates, variants, defaults, labels, opts) in pages.items():
        targets = [(out / slug / f"{key}.html", "../")]
        if key == default_key:
            targets.append((out / f"{slug}.html", ""))
        for target, prefix in targets:
            target.write_text(page_html(o, first, templates, variants, defaults, labels, opts, nav, key, prefix),
                              encoding="utf-8")
    (out / "manifest").mkdir(exist_ok=True)
    (out / "manifest" / f"{slug}.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    n_leaves = sum(len(v[1]) for v in groups.values())
    print(f"{slug}: {len(pages)} pages, {n_leaves} states", flush=True)
    return manifest


def widgets_task(args):
    app, prefix = args
    return run_app(app, prefix).widgets


def fill_main(root, templates, ids):
    """The main body of a state as the page shows it: placeholders filled with that state's
    segments, recursively (the same as the page script does)."""
    return PLACEHOLDER.sub(
        lambda m: render_html.seg_div(m.group(1), fill_main(templates[ids[m.group(1)]], templates, ids),
                                      ids[m.group(1)]),
        root)


class _Text(HTMLParser):
    """Text of an html fragment as the DOM's textContent sees it (style contents included,
    <template> contents not)."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        self.skip += tag == "template"

    def handle_endtag(self, tag):
        self.skip -= tag == "template" and self.skip > 0

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def text_digest(fragment):
    """sha1 of the text with ASCII whitespace removed; pages_check.py computes the same in the
    browser from what the page actually shows."""
    p = _Text()
    p.feed(fragment.replace("@P@", ""))
    p.close()
    text = re.sub(r"[ \t\n\r\f]+", "", "".join(p.parts))
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def expected_value(wid, v, prev, opts, defaults):
    """The value Streamlit gives main-area widget `wid` in candidate state v, coming from `prev`
    ({id: (options index, value)}): kept while it is the same widget (same option list; the label
    is the same for an id on a page), otherwise its default."""
    p = prev.get(wid)
    return p[1] if p is not None and opts[p[0]] == opts[v["o"][wid]] else defaults[wid]


def pick(variants, prev, opts, defaults):
    return [v for v in variants
            if all(v["c"][k] == expected_value(k, v, prev, opts, defaults) for k in v["c"])]


def check_reachable(slug, key, variants, opts, defaults):
    """Every option of every control on the page leads to exactly one built state, the way the page
    script chooses it; and the page with no history opens at the first (default) state."""
    if pick(variants, {}, opts, defaults) != [variants[0]]:
        raise RuntimeError(f"{slug} {key}: the default state is not the one the page opens at")
    for v in variants:
        prev = {k: (v["o"][k], x) for k, x in v["c"].items()}
        for k in v["c"]:
            for i in range(len(opts[v["o"][k]])):
                got = pick(variants, {**prev, k: (v["o"][k], i)}, opts, defaults)
                if len(got) != 1:
                    raise RuntimeError(f"{slug} {key}: from {v['c']}, {k}={i} leads to {len(got)} states")


def page_html(outer, first, templates, variants, defaults, labels, opts, nav, key, prefix):
    cfg = first["page"]
    title = html.escape(str(cfg.get("page_title", nav["slug"])))
    icon = str(cfg.get("page_icon", ""))
    favicon = ("<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' "
               f"viewBox='0 0 100 100'><text y='.9em' font-size='90'>{html.escape(icon)}</text></svg>\">"
               if icon else "")
    # the default state is written out in full (no script needed to see it); the other states'
    # segments are <template>s the page script swaps in
    main = render_html.select_controls(fill_main(first["root"], templates, dict(variants[0]["s"])),
                                       variants[0]["c"])
    used = set(t for v in variants for _, t in v["s"])
    tpls = "".join(f'<template id="{tid}">{templates[tid]}</template>' for tid in sorted(used))
    data = {"nav": nav, "key": key, "outer": outer, "prefix": prefix, "variants": variants,
            "defaults": defaults, "labels": labels, "opts": opts}
    body = (f'<div class="st-app stApp" data-testid="stApp">'
            f'<header class="st-header"><button type="button" class="st-sb-toggle" aria-expanded="false" '
            f'aria-controls="sidebar" title="Sidebar / サイドバー">&raquo;</button></header>'
            f'<section id="sidebar" data-testid="stSidebar" class="st-sidebar" hidden>'
            f'<div class="st-sb-inner">{first["sidebar"]}</div></section>'
            f'<main class="st-main" data-testid="stMain"><div class="block-container" data-testid="stMainBlockContainer">'
            f'{main}</div></main></div>{tpls}')
    body = body.replace("@P@", prefix)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return ("<!doctype html>\n<html lang=\"ja\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{title}</title>{favicon}{FONT}<style>{CSS}</style></head><body>{body}"
            f"<script id=\"st-data\" type=\"application/json\">{payload}</script>"
            f"<script>{JS}</script></body></html>\n")


def slug_of(app):
    stem = Path(app).stem[len("app_"):]
    if stem.startswith("qf_"):
        return stem.replace("_", "-")
    if stem.endswith("_pitchers"):
        return stem[: -len("_pitchers")] + "-pitchers"
    return stem + "-batters"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("apps", nargs="*")
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--only-default", action="store_true")
    ap.add_argument("--shard", default="", help="i/n: run only this shard and keep its part (assemble later)")
    ap.add_argument("--assemble", action="store_true", help="build pages from the parts in OUT_DIR/parts")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    if a.assemble:
        assemble(out)
        return
    if not a.apps:
        ap.error("no apps")
    shard, of = (int(x) for x in a.shard.split("/")) if a.shard else (0, 1)
    if not 0 <= shard < of:
        ap.error("--shard i/n needs 0 <= i < n")
    (out / "img").mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(a.jobs, initializer=_init_worker, initargs=(str(out),)) as pool:
        for app in a.apps:
            render_shard(app, slug_of(app), out, pool, a.jobs, shard, of, a.only_default)
    if not a.shard:  # the whole app was run here: make its pages now
        assemble(out)


if __name__ == "__main__":
    main()
