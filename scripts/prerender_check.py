"""Check the pre-rendered pages against the real Streamlit runtime.

For sampled states of every app (the default state, and states that change each main-area widget),
the unchanged app is run with Streamlit's own test runner (streamlit.testing.v1.AppTest) with the
same widget values, and its output is compared with what the static renderer recorded:
headings, markdown/caption/callout text, metric label/value/delta, table columns and cells, the
number of figures, the sidebar's text, and every widget's label, options and selected value. It checks what the script produced in each state; how the
page looks is checked separately in the browser.

usage: python scripts/prerender_check.py SITE_DIR [--per-app N] [--only slug,slug]
(SITE_DIR/manifest/*.json, or a build job's SITE_DIR/parts/*.json: N states per part)
exit 1 when any state differs.
"""
import argparse
import json
import os
import random
import runpy
import sys
import textwrap
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def norm(text):
    return textwrap.dedent(str(text)).strip()


def table_sig(data):
    """A table's columns and cell values (formats left aside: AppTest returns the raw data)."""
    import math
    import pandas as pd
    if hasattr(data, "data") and hasattr(data, "set_uuid"):  # Styler
        data = data.data
    if isinstance(data, pd.Series):
        data = data.to_frame()
    if not isinstance(data, pd.DataFrame):
        return json.dumps(["other", str(data)], ensure_ascii=False)

    def cell(x):
        if x is None or (isinstance(x, float) and math.isnan(x)) or x is pd.NA or x is pd.NaT:
            return None
        if hasattr(x, "item"):
            x = x.item()
        if isinstance(x, float):
            return round(x, 9)
        return x if isinstance(x, (int, bool)) else str(x)
    rows = [[cell(x) for x in r] for r in data.astype(object).itertuples(index=False, name=None)]
    return json.dumps([[str(c) for c in data.columns], rows], ensure_ascii=False)


def sort_key(t):
    return tuple((x is None, "" if x is None else x) for x in t)


# ---------------------------------------------------------------- the recorder's view of a state
def forget_app_modules():
    """Repo modules (scouting_lib, players_*) bind `streamlit` at import; drop them between the
    stand-in and the real runtime so each side imports its own."""
    for name in list(sys.modules):
        if (ROOT / f"{name}.py").exists():
            del sys.modules[name]


def recorded(app, choices):
    import st_record
    forget_app_modules()
    state = types.SimpleNamespace(run=None)
    mod = st_record.make_module(state)
    saved = sys.modules.get("streamlit")
    sys.modules["streamlit"] = mod
    try:
        state.run = st_record.Run(dict(choices), lambda d, k: table_sig(d))
        try:
            runpy.run_path(str(ROOT / app), run_name="__main__")
        except st_record.Stop:
            pass
        import matplotlib.pyplot as plt
        plt.close("all")
    finally:
        if saved is not None:
            sys.modules["streamlit"] = saved
        else:
            del sys.modules["streamlit"]
        forget_app_modules()
    out = {"heading": [], "text": [], "metric": [], "tables": [], "figures": 0, "sidebar": []}

    def walk(items, out):
        for it in items:
            k = it[0]
            if k == "heading":
                out["heading"].append(norm(it[2]))
            elif k in ("markdown", "caption"):
                out["text"].append(norm(it[1]))
            elif k == "callout":
                out["text"].append(norm(it[2]))
            elif k == "metric":
                out["metric"].append((norm(it[1]), norm(it[2]), None if it[3] in (None, "") else norm(it[3])))
            elif k == "dataframe":
                out["tables"].append(it[1])
            elif k == "image":
                out["figures"] += 1
            for x in it:
                if isinstance(x, st_record.Box):
                    walk(x.items, out)
                elif isinstance(x, list):
                    for y in x:
                        if isinstance(y, st_record.Box):
                            walk(y.items, out)
    walk(state.run.main.items, out)
    side = {"heading": [], "text": [], "metric": [], "tables": [], "figures": 0}
    walk(state.run.sidebar.items, side)
    out["sidebar"] = sorted(side["heading"] + side["text"])
    for k in ("text", "tables"):
        out[k] = sorted(out[k])  # order across containers is not comparable; content is
    widgets = [(w["id"], w["kind"], norm(w["label"]), w["options"], w["raw"], w["default"])
               for w in state.run.widgets]
    return out, widgets


# ---------------------------------------------------------------- the real runtime's view
_LAST_APP = [None]


def real(app, choices, widgets):
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    forget_app_modules()
    # Streamlit keys st.cache_data by module, name and source, and every app runs as __main__:
    # two apps with the same `load_data` would share one entry in this process (on Streamlit
    # Cloud each app has its own process). Empty the caches whenever the app changes.
    if _LAST_APP[0] != app:
        st.cache_data.clear()
        st.cache_resource.clear()
        _LAST_APP[0] = app
    at = AppTest.from_file(str(ROOT / app), default_timeout=600)
    at.run()
    # set the widgets in the order the script creates them, rerunning so later ones appear
    for wid, kind, label, _, raw, default in widgets:
        # a widget the recorder took at its default is left alone, so the real app uses its own
        # default: a wrong default in the recorder then shows as a difference
        if wid not in choices or choices[wid] == default:
            continue
        block = at.sidebar if wid.startswith("s") else at.main
        group = {"selectbox": block.selectbox, "radio": block.radio, "checkbox": block.checkbox}[kind]
        match = [w for w in group if norm(w.label) == label]
        if len(match) != 1:
            raise RuntimeError(f"{app}: widget {wid} '{label}' found {len(match)} times in the real app")
        w, idx = match[0], choices[wid]
        # set the option's real value: AppTest's select_index passes the displayed text instead,
        # which breaks selectboxes over range() with a format_func
        w.set_value(bool(idx) if kind == "checkbox" else raw[idx])
        at.run()
    if at.exception:
        raise RuntimeError(f"{app}: the real app raised: {at.exception}")
    out = {"heading": [], "text": [], "metric": [], "tables": [], "figures": 0, "sidebar": []}
    main = at.main
    for e in main.header:
        out["heading"].append(norm(e.value))
    for e in main.subheader:
        out["heading"].append(norm(e.value))
    for kind in ("markdown", "caption", "info", "warning", "success"):
        for e in getattr(main, kind):
            out["text"].append(norm(e.value))
    for e in main.metric:
        delta = e.delta if e.delta not in (None, "") else None
        out["metric"].append((norm(e.label), norm(e.value), None if delta is None else norm(delta)))
    out["tables"] = sorted(table_sig(e.value) for e in main.dataframe)
    # st.pyplot is "imgs" in AppTest up to streamlit 1.5x and "image" in 1.66
    out["figures"] = len(main.get("imgs")) + len(main.get("image"))
    out["text"] = sorted(out["text"])
    side = at.sidebar
    out["sidebar"] = sorted([norm(e.value) for kind in ("title", "header", "subheader") for e in getattr(side, kind)]
                            + [norm(e.value) for kind in ("markdown", "caption", "info", "warning", "success")
                               for e in getattr(side, kind)])
    rwidgets, sel = [], {}
    for block, prefix in ((at.sidebar, "s"), (at.main, "m")):
        for kind in ("selectbox", "radio", "checkbox"):
            for w in getattr(block, kind):
                opts = [] if kind == "checkbox" else [str(o) for o in w.options]
                rwidgets.append((prefix, kind, norm(w.label), opts))
                sel[(prefix, kind, norm(w.label))] = bool(w.value) if kind == "checkbox" else opts[w.index]
    return out, rwidgets, sel


def compare(a, b):
    diffs = []
    # headings: real AppTest lists headers then subheaders; compare as sets of the same multiset
    if sorted(a["heading"]) != sorted(b["heading"]):
        diffs.append(f"headings differ: only recorder {sorted(set(a['heading']) - set(b['heading']))[:3]} "
                     f"only real {sorted(set(b['heading']) - set(a['heading']))[:3]}")
    if a["text"] != b["text"]:
        ra, rb = set(a["text"]), set(b["text"])
        diffs.append(f"text differs ({len(a['text'])} vs {len(b['text'])}): only recorder "
                     f"{[t[:60] for t in sorted(ra - rb)][:2]} only real {[t[:60] for t in sorted(rb - ra)][:2]}")
    if sorted(a["metric"], key=sort_key) != sorted(b["metric"], key=sort_key):
        diffs.append(f"metrics differ: only recorder {sorted(set(a['metric']) - set(b['metric']), key=sort_key)[:3]} "
                     f"only real {sorted(set(b['metric']) - set(a['metric']), key=sort_key)[:3]}")
    if a["tables"] != b["tables"]:
        ta, tb = set(a["tables"]), set(b["tables"])
        diffs.append(f"tables differ ({len(a['tables'])} vs {len(b['tables'])}): only recorder "
                     f"{[t[:80] for t in sorted(ta - tb)][:1]} only real {[t[:80] for t in sorted(tb - ta)][:1]}")
    if a["figures"] != b["figures"]:
        diffs.append(f"figures: recorder {a['figures']} real {b['figures']}")
    if a["sidebar"] != b["sidebar"]:
        sa, sb = set(a["sidebar"]), set(b["sidebar"])
        diffs.append(f"sidebar text differs: only recorder {[t[:60] for t in sorted(sa - sb)][:2]} "
                     f"only real {[t[:60] for t in sorted(sb - sa)][:2]}")
    return diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--per-app", type=int, default=4)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    os.chdir(ROOT)
    sys.path.insert(0, str(ROOT))
    only = {s for s in a.only.split(",") if s}
    failed, checked = [], 0
    # finished dashboards (manifest/) and the parts of a split build job (parts/, before assembly)
    sources = []
    for mf in sorted((Path(a.site) / "manifest").glob("*.json")):
        if mf.name != "index.json":
            sources.append(json.loads(mf.read_text(encoding="utf-8")))
    for pf in sorted((Path(a.site) / "parts").glob("*.json")):
        p = json.loads(pf.read_text(encoding="utf-8"))
        sources.append({"slug": f"{p['slug']}.{p['shard']}", "app": p["app"],
                        "states": [{"choices": leaf["choices"], "images": leaf["images"],
                                    "inner": {k: v for k, v in leaf["choices"].items() if k.startswith("m")}}
                                   for leaf in p["leaves"]]})
    for m in sources:
        if only and m["slug"].split(".")[0] not in only:
            continue
        states = m["states"]
        if not states:
            continue
        rnd = random.Random(m["slug"])
        # the default state, one state for each non-default main-area value seen, then random ones
        picked = [states[0]]
        seen = set(states[0]["inner"].items())
        for s in states:
            new = set(s["inner"].items()) - seen
            if new and len(picked) < a.per_app and s not in picked:
                seen |= new
                picked.append(s)
        while len(picked) < a.per_app and len(picked) < len(states):
            s = rnd.choice(states)
            if s not in picked:
                picked.append(s)
        for s in picked:
            checked += 1
            rec, widgets = recorded(m["app"], s["choices"])
            try:
                got, rwidgets, real_sel = real(m["app"], s["choices"], widgets)
            except Exception as e:  # noqa: BLE001 - reported as a failure, not a crash
                import traceback
                traceback.print_exc()
                failed.append(f"{m['slug']} {s['choices']}: {e}")
                print("FAIL", failed[-1], flush=True)
                continue
            diffs = compare(rec, got)
            mine = sorted((w[0][0], w[1], w[2], [] if w[1] == "checkbox" else w[3]) for w in widgets)
            # and the controls must show the same selection as the real widgets do
            diffs += [f"widget {w[0]} '{w[2]}': recorder {w[3][s['choices'][w[0]]] if w[1] != 'checkbox' else s['choices'][w[0]]}"
                      f" real {real_sel.get((w[0][0], w[1], w[2]))}"
                      for w in widgets if w[0] in s["choices"]
                      and real_sel.get((w[0][0], w[1], w[2])) != (w[3][s["choices"][w[0]]] if w[1] != "checkbox"
                                                                  else bool(s["choices"][w[0]]))]
            theirs = sorted(rwidgets)
            if mine != theirs:
                diffs.append(f"widgets differ: recorder {mine[:4]} real {theirs[:4]}")
            if len(s["images"]) != rec["figures"]:
                diffs.append(f"manifest has {len(s['images'])} figures, recorder now {rec['figures']}")
            status = "OK  " if not diffs else "FAIL"
            print(status, m["slug"], s["choices"], f"figures={rec['figures']}", "; ".join(diffs), flush=True)
            if diffs:
                failed.append(f"{m['slug']} {s['choices']}: " + "; ".join(diffs))
    print(f"\n{checked - len(failed)}/{checked} states match the real Streamlit run")
    sys.exit(1 if failed or not checked else 0)


if __name__ == "__main__":
    main()
