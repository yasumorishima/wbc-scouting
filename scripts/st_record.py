"""A recording stand-in for the `streamlit` module, so an app can be run once per widget state
and its output written out as static HTML (no Python in the browser, nothing to wait for).

Only the calls and keyword arguments the WBC apps use are provided. Anything else raises, so a
new call or option cannot silently go missing from the pages; extend ALLOWED (and the renderer)
when an app starts using one.
"""
import functools
import hashlib
import io
import numbers
import pickle
import types

import matplotlib
# imported before the stand-in replaces `streamlit` in sys.modules (scripts/requirements-pages.txt
# pins the version whose behaviour the pages copy)
from streamlit.string_util import clean_text as _clean_text, extract_leading_icon as _leading_icon
import streamlit.emojis  # noqa: F401,E402 - extract_leading_icon imports it lazily; have it in sys.modules

matplotlib.use("Agg")

SAVEFIG = {"bbox_inches": "tight", "dpi": 200, "format": "png"}  # what st.pyplot does
FIG_CACHE = {}  # pickled figure + settings -> (sha, png); emptied with the data cache per app
# the repository's own modules (app_*.py, scouting_lib, players_*): see _KeyPickler
_REPO_MODULES = {p.stem for p in __import__("pathlib").Path(__file__).resolve().parent.parent.glob("*.py")}


class _KeyPickler(pickle.Pickler):
    """Pickles a figure for use as a key only (never loaded). matplotlib transforms keep their
    parents in a dict keyed by id(), a memory address that differs in every run; the parents are
    kept (in their order), the addresses dropped."""
    def reducer_override(self, obj):
        from matplotlib.transforms import TransformNode
        # functions and classes pickle by name only: one of the app's own (a tick formatter that
        # reads the language, say) could draw differently with the same name, so such a figure
        # gets no key and is drawn every time
        if isinstance(obj, (types.FunctionType, types.MethodType, type, functools.partial)):
            mod = getattr(getattr(obj, "func", obj), "__module__", None) or ""
            if mod == "__main__" or mod.split(".")[0] in _REPO_MODULES:
                raise pickle.PicklingError(f"{mod} object in a figure: not used as a key")
        if not isinstance(obj, TransformNode):
            return NotImplemented
        r = list(obj.__reduce_ex__(5))
        if len(r) > 2 and isinstance(r[2], dict) and isinstance(r[2].get("_parents"), dict):
            r[2] = {**r[2], "_parents": list(r[2]["_parents"].values())}
        return tuple(r)


def fig_alt(fig):
    """A text alternative for a chart, for screen readers: the figure's titles (its own and each
    plot's), else each plot's axis labels, else its category labels. Empty only for a figure with
    none of these."""
    parts = []
    sup = getattr(fig, "_suptitle", None)
    if sup is not None:
        parts.append(sup.get_text())
    for ax in fig.axes:
        parts += [ax.get_title(loc=loc) for loc in ("left", "center", "right")]
    if not any(p.strip() for p in parts):
        parts = [" / ".join(x for x in (ax.get_ylabel(), ax.get_xlabel()) if x.strip()) for ax in fig.axes]
    if not any(p.strip() for p in parts):  # e.g. a radar chart: its categories
        parts = [", ".join(t.get_text() for t in ax.get_xticklabels() if t.get_text().strip()) for ax in fig.axes]
    seen, out = set(), []
    for p in (" ".join(p.split()) for p in parts):
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    alt = " · ".join(out)
    return alt if len(alt) <= 300 else alt[:299] + "…"


def fig_key(fig, rc):
    buf = io.BytesIO()
    _KeyPickler(buf, protocol=5).dump(fig)
    return hashlib.sha256(buf.getvalue() + repr(sorted(rc.items())).encode()).digest()

# keyword arguments each call accepts (found with an AST scan of the apps, 2026-11-02)
ALLOWED = {
    "markdown": {"unsafe_allow_html"}, "caption": {"unsafe_allow_html"}, "write": set(),
    "header": set(), "subheader": set(), "divider": set(),
    "info": set(), "warning": set(), "success": set(),
    "metric": {"delta", "delta_color", "help"},
    "dataframe": {"hide_index", "use_container_width", "height"},
    "pyplot": {"use_container_width"},
    "columns": set(), "expander": {"expanded"}, "tabs": set(),
    "selectbox": {"index", "format_func", "key", "label_visibility"},
    "radio": {"index", "format_func", "key", "horizontal", "label_visibility"},
    "checkbox": {"value", "key"},
    "set_page_config": {"page_title", "page_icon", "layout", "initial_sidebar_state"},
}


class Stop(Exception):
    pass


def _check(name, kw):
    extra = set(kw) - ALLOWED[name]
    if extra:
        raise TypeError(f"st.{name}: keyword(s) {sorted(extra)} are not handled by the static renderer")


class Box:
    """A container: the page body, the sidebar, a column, an expander or a tab."""

    def __init__(self, run, kind, label=None, parent=None):
        self.run, self.kind, self.label, self.items = run, kind, label, []
        self.in_sidebar = kind == "sidebar" or bool(parent and parent.in_sidebar)

    # -- context manager: `with col:` sends module-level calls here
    def __enter__(self):
        self.run.stack.append(self)
        return self

    def __exit__(self, *exc):
        self.run.stack.pop()
        return False

    def _add(self, item):
        self.items.append(item)

    # -- text
    def markdown(self, body, unsafe_allow_html=False, **kw):
        _check("markdown", kw)
        self._add(("markdown", str(body), bool(unsafe_allow_html)))

    def write(self, *args, **kw):
        _check("write", kw)
        for a in args:
            if isinstance(a, str):
                self._add(("markdown", a, False))
            elif isinstance(a, numbers.Number):
                self._add(("markdown", str(a), False))
            elif hasattr(a, "to_html"):  # DataFrame / Series / Styler
                self.dataframe(a)
            else:
                raise TypeError(f"st.write of {type(a).__name__} is not handled by the static renderer")

    def caption(self, body, unsafe_allow_html=False, **kw):
        _check("caption", kw)
        self._add(("caption", str(body), bool(unsafe_allow_html)))

    def header(self, body, **kw):
        _check("header", kw)
        self._add(("heading", 2, str(body)))

    def subheader(self, body, **kw):
        _check("subheader", kw)
        self._add(("heading", 3, str(body)))

    def divider(self, **kw):
        _check("divider", kw)
        self._add(("divider",))

    def _callout(self, kind, body, kw):
        _check(kind, kw)
        # Streamlit (1.66) takes a leading emoji of an alert's body as its icon, shown left of the
        # text; the real Streamlit's own rule decides what counts as one
        icon, rest = _leading_icon(_clean_text(body))
        self._add(("callout", kind, rest, icon) if icon else ("callout", kind, str(body)))

    def info(self, body, **kw):
        self._callout("info", body, kw)

    def warning(self, body, **kw):
        self._callout("warning", body, kw)

    def success(self, body, **kw):
        self._callout("success", body, kw)

    def metric(self, label, value, delta=None, **kw):
        _check("metric", kw)
        self._add(("metric", str(label), "" if value is None else str(value),
                   None if delta is None else str(delta), kw.get("delta_color", "normal"),
                   kw.get("help")))

    # -- data and pictures
    def dataframe(self, data, **kw):
        _check("dataframe", kw)
        self._add(("dataframe", self.run.table_html(data, kw), kw.get("height")))

    def pyplot(self, fig=None, **kw):
        _check("pyplot", kw)
        import matplotlib.pyplot as plt
        fig = fig or plt.gcf()
        # Most figures repeat across states (the same chart in every pitch-type state): a figure
        # whose pickled state and matplotlib settings equal an earlier one's draws the same picture,
        # so the drawing is reused. The key is taken before drawing; a figure that cannot be pickled
        # is drawn every time.
        alt = fig_alt(fig)  # before drawing: the same figure state whether or not the cache hits
        try:
            key = fig_key(fig, plt.rcParams)
        except Exception:  # noqa: BLE001 - not picklable: no reuse
            key = None
        hit = FIG_CACHE.get(key) if key is not None else None
        if hit is None:
            buf = io.BytesIO()
            fig.savefig(buf, **SAVEFIG)
            data = buf.getvalue()
            hit = (hashlib.sha256(data).hexdigest()[:20], data)
            if key is not None:
                FIG_CACHE[key] = hit
        sha, data = hit
        self.run.png.setdefault(sha, data)
        self._add(("image", sha, alt))

    # -- layout
    def columns(self, spec, **kw):
        _check("columns", kw)
        n = spec if isinstance(spec, int) else len(spec)
        weights = [1] * n if isinstance(spec, int) else list(spec)
        cols = [Box(self.run, "column", parent=self) for _ in range(n)]
        self._add(("columns", weights, cols))
        return cols

    def expander(self, label, expanded=False, **kw):
        _check("expander", kw)
        box = Box(self.run, "expander", str(label), parent=self)
        self._add(("expander", str(label), bool(expanded), box))
        return box

    def tabs(self, labels, **kw):
        _check("tabs", kw)
        boxes = [Box(self.run, "tab", str(l), parent=self) for l in labels]
        self._add(("tabs", [str(l) for l in labels], boxes))
        return boxes

    # -- widgets: the value comes from the run's choices; the default is Streamlit's
    def _widget(self, kind, label, options, default, fmt, kw):
        """A widget's identity is (sidebar|main, its order there): labels change with the language."""
        _check(kind, kw)
        run = self.run
        where = "s" if self.in_sidebar else "m"
        wid = f"{where}{run.widget_count[where]}"
        run.widget_count[where] += 1
        if not options:
            raise ValueError(f"widget {wid} '{label}' has no options")
        choice = run.choices.get(wid, default)
        if not 0 <= choice < len(options):
            raise ValueError(f"widget {wid} '{label}': choice {choice} outside {len(options)} options")
        run.widgets.append({"id": wid, "kind": kind, "label": str(label),
                            "options": [str(fmt(o)) for o in options],
                            "raw": [o.item() if hasattr(o, "item") else o for o in options],
                            "default": default, "choice": choice,
                            "label_visibility": kw.get("label_visibility", "visible"),
                            "horizontal": bool(kw.get("horizontal", False)), "key": kw.get("key")})
        self._add(("widget", wid))
        return options[choice]

    def selectbox(self, label, options, index=0, format_func=str, **kw):
        if index is None:
            raise ValueError("selectbox with index=None is not supported by the static renderer")
        return self._widget("selectbox", label, list(options), index, format_func, kw)

    def radio(self, label, options, index=0, format_func=str, **kw):
        if index is None:
            raise ValueError("radio with index=None is not supported by the static renderer")
        return self._widget("radio", label, list(options), index, format_func, kw)

    def checkbox(self, label, value=False, **kw):
        return self._widget("checkbox", label, [False, True], 1 if value else 0, str, kw)


class Run:
    def __init__(self, choices, table_html):
        self.choices, self.table_html = choices, table_html
        self.widgets, self.widget_count = [], {"s": 0, "m": 0}
        self.png = {}
        self.page = {}
        self.stopped = False
        self.main = Box(self, "main")
        self.sidebar = Box(self, "sidebar")
        self.stack = [self.main]


def make_module(state):
    """state.run is swapped per run; the module forwards every call to the current container."""
    st = types.ModuleType("streamlit")

    def here():
        return state.run.stack[-1]

    for name in ("markdown", "write", "caption", "header", "subheader", "divider", "info",
                 "warning", "success", "metric", "dataframe", "pyplot", "columns", "expander",
                 "tabs", "selectbox", "radio", "checkbox"):
        setattr(st, name, (lambda n: lambda *a, **k: getattr(here(), n)(*a, **k))(name))

    class _Sidebar:
        def __getattr__(self, name):
            return getattr(state.run.sidebar, name)

        def __enter__(self):
            return state.run.sidebar.__enter__()

        def __exit__(self, *exc):
            return state.run.sidebar.__exit__(*exc)

    st.sidebar = _Sidebar()

    def set_page_config(**kw):
        _check("set_page_config", kw)
        state.run.page = kw

    def stop():
        raise Stop()

    # Like st.cache_data: keyed by the function's file and name (every app runs as __main__, so the
    # module name alone would hand one app's data to the next) and the arguments; every call gets
    # its own copy, so an app that changes the returned frame cannot change the cached one.
    cache = {}

    def cache_data(func=None, **kw):
        def wrap(f):
            @functools.wraps(f)
            def inner(*a, **k):
                try:
                    key = (f.__code__.co_filename, f.__qualname__, a, tuple(sorted(k.items())))
                    hash(key)
                except TypeError:
                    return f(*a, **k)
                if key not in cache:
                    cache[key] = pickle.dumps(f(*a, **k), protocol=pickle.HIGHEST_PROTOCOL)
                return pickle.loads(cache[key])
            return inner
        return wrap(func) if callable(func) else wrap

    st.set_page_config, st.stop, st.cache_data = set_page_config, stop, cache_data
    def _clear_cache():
        cache.clear()
        FIG_CACHE.clear()
    st._clear_cache = _clear_cache
    st.__getattr__ = lambda name: (_ for _ in ()).throw(
        AttributeError(f"st.{name} is not provided by the static renderer"))
    return st
