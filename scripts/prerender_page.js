// Pre-rendered Streamlit page: the widgets switch between states that were all built in advance.
// Sidebar widgets (language, player, season) open another page; main-area widgets swap segments.
(() => {
  const data = JSON.parse(document.getElementById("st-data").textContent);
  const nav = data.nav;
  const main = document.querySelector(".block-container");
  const sidebar = document.getElementById("sidebar");
  const toggle = document.querySelector(".st-sb-toggle");

  // ---- sidebar open/closed (kept while moving between pages of this dashboard)
  const SB_KEY = "wbc-sidebar-open";
  const setSidebar = open => {
    sidebar.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    try { sessionStorage.setItem(SB_KEY, open ? "1" : "0"); } catch (e) { /* storage off: fine */ }
  };
  let wasOpen = false;
  try { wasOpen = sessionStorage.getItem(SB_KEY) === "1"; } catch (e) { /* storage off */ }
  setSidebar(wasOpen);
  toggle.addEventListener("click", () => setSidebar(sidebar.hidden));
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !sidebar.hidden) setSidebar(false); });

  const valueOf = el => (el.type === "checkbox" ? (el.checked ? 1 : 0) : Number(el.value));
  const setValue = (el, v) => {
    if (el.type === "checkbox") el.checked = v === 1;
    else if (el.type === "radio") el.checked = Number(el.value) === v;
    else el.value = String(v);
  };
  const MOVED = `wbc-moved-${nav.slug}`;
  // the sidebar always shows this page's own state (a Back without the back/forward cache can
  // bring the page back with the browser's remembered choice, the one that left it)
  const resetSidebar = () => sidebar.querySelectorAll("[data-w]").forEach(el => {
    const v = data.outer[el.dataset.w];
    if (v !== undefined) setValue(el, v);
  });
  resetSidebar();

  // ---- sidebar widgets: go to the page of the new state
  sidebar.addEventListener("change", e => {
    const el = e.target.closest("[data-w]");
    if (!el) return;
    const id = el.dataset.w;
    const i = nav.sidebar.indexOf(id);
    const cur = data.outer;
    const want = { ...cur, [id]: valueOf(el) };
    // same earlier choices and the new value; keep later choices where that page exists
    const fits = s => nav.sidebar.slice(0, i + 1).every(k => (k in s.c ? s.c[k] : null) === (k in want ? want[k] : null));
    const cands = nav.states.filter(fits);
    if (!cands.length) return;
    const score = s => nav.sidebar.slice(i + 1).filter(k => k in s.c && s.c[k] === cur[k]).length;
    const best = cands.reduce((a, b) => (score(b) > score(a) ? b : a));
    const root = data.prefix;
    // the next page keeps main-area choices only when reached this way (one Streamlit session)
    try { sessionStorage.setItem(MOVED, "1"); } catch (e2) { /* storage off */ }
    location.href = best.k === nav.default ? `${root}${nav.slug}.html` : `${root}${nav.slug}/${best.k}.html`;
  });

  // ---- main-area widgets: show the segments of the state Streamlit would show
  // A widget keeps its value while it stays the same widget (same label, same options), as in
  // Streamlit; otherwise it starts at its default. prev = {id: [option list, value]}.
  let cur = data.variants[0];
  const sameOpts = (a, b) => a.length === b.length && a.every((x, i) => x === b[i]);
  const expected = (k, v, prev) => {
    const p = prev[k];
    return p && sameOpts(p[0], data.opts[v.o[k]]) ? p[1] : data.defaults[k];
  };
  const pick = prev => data.variants.find(v => Object.keys(v.c).every(k => v.c[k] === expected(k, v, prev)));
  const prevOf = v => Object.fromEntries(Object.entries(v.c).map(([k, x]) => [k, [data.opts[v.o[k]], x]]));
  const setControls = () => {
    main.querySelectorAll("[data-w]").forEach(el => {
      const v = cur.c[el.dataset.w];
      if (v !== undefined) setValue(el, v);
    });
  };
  // v.s = [[path, template id], ...], parents before children. A segment whose template is already
  // shown is left alone (its pictures stay loaded); a replaced container brings empty placeholders
  // for its children, which are then filled in the same pass.
  const apply = v => {
    // the control in use may sit in a segment that is replaced: give its focus to the new one
    const act = document.activeElement;
    const focus = act && main.contains(act) && act.dataset && act.dataset.w
      ? { w: act.dataset.w, value: act.type === "radio" ? act.value : null } : null;
    const want = new Map(v.s);
    const roots = v.s.map(([p]) => p).filter(p => !p.includes("."));
    // top level: one placeholder per root segment, in order
    let existing = [...main.querySelectorAll(":scope > .seg")];
    existing.filter(el => !roots.includes(el.dataset.seg)).forEach(el => el.remove());
    let prev = null;
    roots.forEach(p => {
      let el = main.querySelector(`:scope > .seg[data-seg="${p}"]`);
      if (!el) {
        el = document.createElement("div");
        el.className = "seg";
        el.dataset.seg = p;
      }
      if (prev) prev.after(el); else main.prepend(el);
      prev = el;
    });
    for (const [p, tid] of v.s) {
      const el = main.querySelector(`.seg[data-seg="${p}"]`);
      if (!el) throw new Error(`segment ${p} has no place on the page`);
      if (el.dataset.tpl === tid) continue;
      el.replaceChildren(document.getElementById(tid).content.cloneNode(true));
      el.dataset.tpl = tid;
    }
    cur = v;
    setControls();
    if (focus) {
      const sel = focus.value === null ? `[data-w="${focus.w}"]` : `[data-w="${focus.w}"][value="${focus.value}"]`;
      const el = main.querySelector(sel);
      if (el && el !== document.activeElement) el.focus({ preventScroll: true });
    }
  };
  // The same rule across the pages of this dashboard (another player or season): a main-area
  // widget with the same label, options and default keeps its value (Streamlit's widget id
  // includes all three).
  const KEEP = `wbc-inner-${nav.slug}`;
  const save = () => {
    const keep = {};
    for (const [id, [o, v]] of Object.entries(prevOf(cur))) keep[id] = [data.labels[id], o, v, data.defaults[id]];
    try { sessionStorage.setItem(KEEP, JSON.stringify(keep)); } catch (e) { /* storage off */ }
  };
  main.addEventListener("change", e => {
    const el = e.target.closest("[data-w]");
    if (!el) return;
    const k = el.dataset.w;
    const v = pick({ ...prevOf(cur), [k]: [data.opts[cur.o[k]], valueOf(el)] });
    if (v) apply(v); else setControls();  // never left showing a choice the page does not show
    save();
  });
  // Kept choices apply when this page was reached from another page of the dashboard (its sidebar,
  // or Back/Forward). Opening it fresh (a link, the address bar) or reloading starts at the
  // defaults, as a new Streamlit session does.
  const restore = fromCache => {
    let keep = {};
    try { keep = JSON.parse(sessionStorage.getItem(KEEP) || "{}"); } catch (e) { keep = {}; }
    let moved = false;
    try { moved = sessionStorage.getItem(MOVED) === "1"; sessionStorage.removeItem(MOVED); } catch (e) { /* storage off */ }
    const nav0 = performance.getEntriesByType && performance.getEntriesByType("navigation")[0];
    const history = nav0 && nav0.type === "back_forward";
    if (!fromCache && !moved && !history) keep = {};
    const prev = {};
    for (const [id, k] of Object.entries(keep)) {
      if (Array.isArray(k) && k.length === 4 && data.labels[id] === k[0] && data.defaults[id] === k[3]) {
        prev[id] = [k[1], k[2]];
      }
    }
    apply(pick(prev) || data.variants[0]);
  };
  restore(false);
  window.addEventListener("pageshow", e => {
    resetSidebar();
    // back/forward cache: the page comes back as it was left; take up the choices kept since
    if (e.persisted) restore(true); else setControls();
  });

  // ---- st.tabs
  document.addEventListener("click", e => {
    const tab = e.target.closest("[role=tab][data-tab]");
    if (!tab) return;
    const box = tab.closest(".st-tabs");
    box.querySelectorAll(":scope > [role=tablist] > [role=tab]").forEach(t =>
      t.setAttribute("aria-selected", String(t === tab)));
    box.querySelectorAll(":scope > [role=tabpanel]").forEach(p => { p.hidden = p.dataset.panel !== tab.dataset.tab; });
  });
})();
