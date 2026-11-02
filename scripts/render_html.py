"""Turn one recorded run (st_record.Run) into HTML that looks like the Streamlit page.

The markup carries the same data-testid attributes Streamlit uses, so the app's own PREMIUM_CSS
(which targets [data-testid="stMetric"], stExpander, stTabs, stSidebar, .stDataFrame, ...) applies.
"""
import hashlib
import html
import re
import textwrap

from markdown_it import MarkdownIt

from st_record import Box

# Streamlit renders markdown as CommonMark + GFM tables/strikethrough (react-markdown, remark-gfm):
# a list right after a "**Strengths:**" line is a list, not part of the paragraph.
_MD_SAFE = MarkdownIt("commonmark", {"html": False}).enable(["table", "strikethrough"])
_MD_HTML = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])


def esc(text):
    return html.escape(str(text), quote=True)


def markdown_html(body, unsafe=False, inline=False):
    # st.markdown dedents the body (streamlit's clean_text) before rendering it
    text = textwrap.dedent(str(body)).strip("\n")
    out = (_MD_HTML if unsafe else _MD_SAFE).render(text).strip()
    if inline and out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return out


class Renderer:
    """Renders items. image_info(sha, png) -> (file name, width, height) writes the picture once."""

    def __init__(self, image_info, prefix):
        self.image_info, self.prefix = image_info, prefix

    def image(self, sha, png):
        name, w, h = self.image_info(sha, png)
        return (f'<div data-testid="stImage" class="st-img"><img src="{self.prefix}img/{name}" '
                f'width="{w}" height="{h}" loading="lazy" decoding="async" alt=""></div>')

    def items(self, items, run, widget_html):
        return "".join(self.item(it, run, widget_html) for it in items)

    def item(self, it, run, widget_html, box_html=None):
        """box_html(box, k) renders the k-th child box of a container (default: its items)."""
        kind = it[0]
        if box_html is None:
            box_html = lambda box, k: self.items(box.items, run, widget_html)  # noqa: E731
        if kind == "markdown":
            body = markdown_html(it[1], it[2])
            return f'<div data-testid="stMarkdown" class="st-md">{body}</div>'
        if kind == "caption":
            return f'<div data-testid="stCaptionContainer" class="st-caption">{markdown_html(it[1], it[2])}</div>'
        if kind == "heading":
            level, text = it[1], it[2]
            tag = "h2" if level == 2 else "h3"
            testid = "stHeading"
            return f'<div data-testid="{testid}" class="st-h"><{tag}>{markdown_html(text, inline=True)}</{tag}></div>'
        if kind == "divider":
            return '<hr data-testid="stDivider">'
        if kind == "callout":
            return (f'<div data-testid="stAlert" class="st-alert st-{it[1]}" role="alert">'
                    f'{markdown_html(it[2])}</div>')
        if kind == "metric":
            label, value, delta, color, help_text = it[1], it[2], it[3], it[4], it[5]
            d = ""
            if delta not in (None, ""):
                neg = str(delta).strip().startswith("-")
                cls = {"normal": "down" if neg else "up", "inverse": "up-bad" if not neg else "down-good",
                       "off": "off"}.get(color)
                if cls is None:
                    raise ValueError(f"metric delta_color {color!r} not handled")
                arrow = "&#8595;" if neg else "&#8593;"
                d = (f'<div data-testid="stMetricDelta" class="st-delta {cls}">{arrow} '
                     f'{markdown_html(delta, inline=True)}</div>')
            tip = ""
            if help_text:
                # Streamlit shows a (?) that reveals the help text; a native tooltip, also on tap
                tip = (f'<span class="st-help" tabindex="0" role="img" aria-label="{esc(help_text)}" '
                       f'title="{esc(help_text)}">?</span>')
            return (f'<div data-testid="stMetric" class="st-metric">'
                    f'<div data-testid="stMetricLabel"><p>{markdown_html(label, inline=True)}</p>{tip}</div>'
                    f'<div data-testid="stMetricValue"><p>{markdown_html(value, inline=True)}</p></div>{d}</div>')
        if kind == "dataframe":
            # Not class "stDataFrame": the apps' CSS restyles `.stDataFrame thead th`, which never
            # showed on Streamlit's canvas grid. Streamlit shows about ten rows and scrolls the rest.
            height = it[2] or 38 + 35 * 10
            return (f'<div class="st-df" data-testid="stDataFrame"><div class="df-scroll" '
                    f'style="max-height:{int(height)}px">{it[1]}</div></div>')
        if kind == "image":
            return self.image(it[1], run.png[it[1]])
        if kind == "columns":
            weights, cols = it[1], it[2]
            inner = "".join(
                f'<div data-testid="stColumn" class="st-col" style="flex:{w} 1 0%">'
                f'{box_html(c, k)}</div>'
                for k, (w, c) in enumerate(zip(weights, cols)))
            return f'<div data-testid="stHorizontalBlock" class="st-cols">{inner}</div>'
        if kind == "expander":
            label, expanded, box = it[1], it[2], it[3]
            return (f'<details data-testid="stExpander" class="st-exp"{" open" if expanded else ""}>'
                    f'<summary>{markdown_html(label, inline=True)}</summary>'
                    f'<div class="st-exp-body">{box_html(box, 0)}</div></details>')
        if kind == "tabs":
            labels, boxes = it[1], it[2]
            tid = hashlib.sha1("|".join(labels).encode()).hexdigest()[:6]
            heads = "".join(
                f'<button role="tab" type="button" aria-selected="{"true" if i == 0 else "false"}" '
                f'data-tab="{tid}-{i}">{markdown_html(l, inline=True)}</button>' for i, l in enumerate(labels))
            panels = "".join(
                f'<div role="tabpanel" data-panel="{tid}-{i}"{"" if i == 0 else " hidden"}>'
                f'{box_html(b, i)}</div>' for i, b in enumerate(boxes))
            return f'<div data-testid="stTabs" class="st-tabs"><div role="tablist">{heads}</div>{panels}</div>'
        if kind == "widget":
            return widget_html(it[1])
        raise ValueError(f"unknown item {kind}")


def widget_control(w, selected=None):
    """A widget as a form control. selected=None leaves it neutral (the page script sets it)."""
    wid, kind, label, opts = w["id"], w["kind"], w["label"], w["options"]
    lcls = "st-wlabel sr-only" if w.get("label_visibility") == "collapsed" else "st-wlabel"
    lab = markdown_html(label, inline=True)
    # autocomplete=off: browsers must not restore an old choice over the state the page shows
    if kind == "checkbox":
        checked = " checked" if selected == 1 else ""
        return (f'<div data-testid="stCheckbox" class="st-check"><label><input type="checkbox" '
                f'autocomplete="off" data-w="{wid}"{checked}> <span>{lab}</span></label></div>')
    if kind == "radio":
        boxes = "".join(
            f'<label><input type="radio" name="r-{wid}" value="{i}" autocomplete="off" data-w="{wid}"'
            f'{" checked" if selected == i else ""}> <span>{esc(o)}</span></label>' for i, o in enumerate(opts))
        horiz = " horizontal" if w.get("horizontal") else ""
        return (f'<div data-testid="stRadio" class="st-radio{horiz}" role="radiogroup" aria-labelledby="l-{wid}">'
                f'<div id="l-{wid}" class="{lcls}">{lab}</div><div class="st-radio-opts">{boxes}</div></div>')
    options = "".join(f'<option value="{i}"{" selected" if selected == i else ""}>{esc(o)}</option>'
                      for i, o in enumerate(opts))
    return (f'<div data-testid="stSelectbox" class="st-select"><label for="w-{wid}" class="{lcls}">{lab}</label>'
            f'<div><div><select id="w-{wid}" autocomplete="off" data-w="{wid}">{options}</select></div></div></div>')


_SELECT = re.compile(r'(<select id="w-(m\d+)" autocomplete="off" data-w="m\d+">)(.*?)(</select>)', re.S)
_CHECK = re.compile(r'<input type="checkbox" autocomplete="off" data-w="(m\d+)">')
_RADIO = re.compile(r'<input type="radio" name="r-(m\d+)" value="(\d+)" autocomplete="off" data-w="m\d+">')


def select_controls(fragment, choices):
    """Mark the main-area controls in already-rendered (neutral) html with `choices`, so the page
    shows the right state before any script runs."""
    def sel(m):
        v = choices.get(m.group(2))
        opts = m.group(3) if v is None else m.group(3).replace(f'<option value="{v}">', f'<option value="{v}" selected>', 1)
        return m.group(1) + opts + m.group(4)
    fragment = _SELECT.sub(sel, fragment)
    fragment = _CHECK.sub(lambda m: m.group(0)[:-1] + (" checked>" if choices.get(m.group(1)) == 1 else ">"), fragment)
    return _RADIO.sub(lambda m: m.group(0)[:-1] + (" checked>" if str(choices.get(m.group(1))) == m.group(2) else ">"),
                      fragment)


def walk_widgets(items, out):
    for it in items:
        if it[0] == "widget":
            out.append(it[1])
        for x in it:
            if isinstance(x, Box):
                walk_widgets(x.items, out)
            elif isinstance(x, list):
                for y in x:
                    if isinstance(y, Box):
                        walk_widgets(y.items, out)
    return out


CONTAINERS = ("columns", "tabs", "expander")


def seg_div(path, content="", tpl=None):
    t = f' data-tpl="{tpl}"' if tpl else ""
    return f'<div class="seg" data-seg="{path}"{t}>{content}</div>'


def render_leaf(run, renderer):
    """-> the sidebar html (its widgets selected) and the main body as segments.

    Every box (the page, a column, a tab, an expander) is cut before each item that holds a
    main-area widget: that item and what follows may depend on the widget, what is before it
    cannot (the script runs top to bottom). A container that holds a widget is kept as a shell with
    an empty placeholder per child box, and the child boxes are cut the same way, so choosing a
    batter in one tab swaps only the rest of that tab. Segments are returned parents first, as
    (path, html) with empty placeholders `<div class="seg" data-seg="child path"></div>`.
    Controls in the main body are rendered neutral, so equal content gives equal segments.
    """
    by_id = {w["id"]: w for w in run.widgets}

    def neutral(wid):
        return widget_control(by_id[wid])

    def chosen(wid):
        return widget_control(by_id[wid], by_id[wid]["choice"])

    segs = []

    def cut(items, path):
        groups, cur = [], []
        for it in items:
            if walk_widgets([it], []) and cur:
                groups.append(cur)
                cur = []
            cur.append(it)
        if cur:
            groups.append(cur)
        placeholders = []
        for gi, group in enumerate(groups):
            p = f"{path}.{gi}" if path else str(gi)
            placeholders.append(seg_div(p))
            slot = len(segs)
            segs.append(None)  # keep parents before children
            parts = []
            for it in group:
                if it[0] in CONTAINERS and walk_widgets([it], []):
                    parts.append(renderer.item(it, run, neutral,
                                               box_html=lambda box, k, p=p: cut(box.items, f"{p}.c{k}")))
                else:
                    parts.append(renderer.item(it, run, neutral))
            segs[slot] = (p, "".join(parts))
        return "".join(placeholders)

    root = cut(run.main.items, "")
    sidebar = renderer.items(run.sidebar.items, run, chosen)
    return {"sidebar": sidebar, "root": root, "segments": segs}
