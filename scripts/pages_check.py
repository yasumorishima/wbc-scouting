"""Open every static (stlite) page in Chromium and check that it really renders.

For each app in apps.json (written by scripts/build_pages.py):
  1. overview: wait until the app is idle, then record the time, the headings, figures (<img> drawn
     with a real size) and alerts of the main column (not the sidebar), Streamlit exceptions and
     "Traceback" text; stitch a full-length screenshot by scrolling the app's own scroll container;
  2. detail: pick players in the sidebar selectbox in roster order until one draws a figure (some
     players have no Statcast rows and the app says so; they are recorded as skipped), and record
     the same again (not for qf-*, whose sidebar selectbox is the season).
With --cloud, the same steps run on https://wbc-<slug>.streamlit.app/ and the headings, figure counts
and chosen player must match. A cloud app that is asleep or does not answer is reported, not failed.

A page fails when it does not render within LIMIT_MS, shows an exception or a Traceback, has no
heading in the main column, or no player's detail (the whole page for qf-*) draws a figure; apps
whose CSV is missing must instead show their no-data notice and draw none.
Output: pages_check/result.json, pages_check/summary.md, pages_check/<slug>[_detail].jpg.
Exit 1 when any page fails.

usage: python scripts/pages_check.py <base_url> <apps.json> [--cloud] [--only slug,slug]
"""
import argparse
import asyncio
import io
import json
import sys
import time
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

LIMIT_MS = 300_000      # static pages (Pyodide start + package install)
CLOUD_LIMIT_MS = 300_000  # a sleeping cloud app is detected at once (ASLEEP), so this is only for slow runs
IDLE_S = 4              # the app counts as idle after this many quiet seconds
RUN_GRACE_S = 20        # after a widget change, wait at most this long to see the rerun start
PARALLEL = 3
MAX_PLAYERS = 8         # players tried for the detail view
SHOT_WIDTH = 800        # stored screenshots are scaled to this width (JPEG)
MAX_STEPS = 40          # at most 40 viewport heights per stitched screenshot
NO_DATA = "Statcast"    # the no-data notice of apps without a CSV mentions Statcast
ASLEEP = ("get this app back up", "gone to sleep")
EXPAND = ['[data-testid="stExpandSidebarButton"]', '[data-testid="stSidebarCollapsedControl"] button',
          '[data-testid="collapsedControl"] button']

STATE_JS = """() => {
  // The main column only (not the sidebar, whose title is a heading on every page).
  const root = document.querySelector('[data-testid="stMain"]') || document.querySelector('section.main');
  if (!root) return null;
  const scrollers = [...document.querySelectorAll('*')].filter(e => {
    const s = getComputedStyle(e);
    return (s.overflowY === 'auto' || s.overflowY === 'scroll') && e.scrollHeight > e.clientHeight + 20;
  });
  const imgs = [...root.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth > 0 && i.getBoundingClientRect().width > 100);
  const heads = [...root.querySelectorAll('h1, h2, h3')].map(h => h.innerText.trim()).filter(Boolean);
  const status = document.querySelector('[data-testid="stStatusWidget"]');
  const app = document.querySelector('[data-testid="stApp"]');
  // Streamlit marks the app element with the script state (its own e2e tests wait on 'notRunning').
  const scriptState = app ? app.getAttribute('data-test-script-state') : null;
  const text = document.body.innerText;
  return {
    script_state: scriptState,
    images: imgs.length,
    headings: heads,
    exceptions: document.querySelectorAll('[data-testid="stException"]').length,
    traceback: text.includes('Traceback'),
    running: (scriptState !== null && scriptState !== 'notRunning') ||
             !!(status && /Running/i.test(status.innerText)) || document.querySelectorAll('[data-stale="true"]').length > 0,
    alerts: [...root.querySelectorAll('[data-testid="stAlert"]')].map(a => a.innerText.slice(0, 200)),
    sidebar_select: document.querySelectorAll('[data-testid="stSidebar"] [data-testid="stSelectbox"]').length,
    textlen: root.innerText.length,
  };
}"""

SCROLL_JS = """(y) => {
  const scrollers = [...document.querySelectorAll('*')].filter(e => {
    const s = getComputedStyle(e);
    return (s.overflowY === 'auto' || s.overflowY === 'scroll') && e.scrollHeight > e.clientHeight + 20;
  });
  const el = scrollers.sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
  if (!el) { window.scrollTo(0, y); return [window.scrollY, document.body.scrollHeight, window.innerHeight]; }
  el.scrollTop = y;
  return [el.scrollTop, el.scrollHeight, el.clientHeight];
}"""


async def app_frame(page):
    """The frame that holds the Streamlit app (Streamlit Cloud wraps it in an iframe)."""
    for fr in page.frames:
        try:
            if await fr.locator('[data-testid="stApp"]').count():
                return fr
        except Exception:
            pass
    return None


async def asleep(page):
    for fr in page.frames:
        try:
            body = (await fr.inner_text("body", timeout=2000)).lower()
            if any(a in body for a in ASLEEP):
                return True
        except Exception:
            pass
    return False


async def wait_idle(page, t0, ready, limit_ms, seen, need_run=False):
    """Wait until ready(state) holds, the script is not running and nothing has changed for IDLE_S seconds.

    need_run: after a widget change, accept only once this wait has seen the rerun start (or after
    RUN_GRACE_S, for a rerun too quick to observe), so the previous view is never taken for the new one.
    seen["running"] records whether a run in progress was ever observed (proves the busy test can fire).
    """
    last, quiet, state, fr, ran = None, 0, None, None, False
    while (time.monotonic() - t0) * 1000 < limit_ms:
        fr = await app_frame(page)
        state = None
        if fr is not None:
            try:
                state = await fr.evaluate(STATE_JS)
            except Exception:
                state = None
        if state:
            seen["running"] = seen.get("running", False) or state["running"]
            ran = ran or state["running"]
            seen.setdefault("states", set()).add(str(state["script_state"]))
            if state["exceptions"] or state["traceback"]:
                return fr, state, True
            key = (state["images"], tuple(state["headings"]), state["textlen"], tuple(state["alerts"]))
            started = ran or not need_run or time.monotonic() - t0 > RUN_GRACE_S
            if started and ready(state) and not state["running"] and key == last:
                quiet += 1
                if quiet >= IDLE_S:
                    return fr, state, True
            else:
                quiet = 0
            last = key
        elif await asleep(page):
            return fr, {"asleep": True}, False
        await page.wait_for_timeout(1000)
    return fr, state or {}, False


async def stitched_shot(page, fr, path):
    parts, y = [], 0
    for _ in range(MAX_STEPS):
        top, total, view = await fr.evaluate(SCROLL_JS, y)
        await page.wait_for_timeout(400)
        img = Image.open(io.BytesIO(await page.screenshot()))
        parts.append((top, img))
        if top + view >= total - 2:
            break
        y = top + view - 80
    width = parts[0][1].width
    height = parts[-1][0] + parts[-1][1].height
    sheet = Image.new("RGB", (width, height))
    for top, img in parts:
        sheet.paste(img.convert("RGB"), (0, top))
    sheet = sheet.resize((SHOT_WIDTH, max(1, round(height * SHOT_WIDTH / width))))
    sheet.save(path, "JPEG", quality=60)
    await fr.evaluate(SCROLL_JS, 0)


async def pick_option(page, fr, index):
    for sel in EXPAND:
        loc = fr.locator(sel)
        if await loc.count() and await loc.first.is_visible():
            await loc.first.click()
            await page.wait_for_timeout(1000)
            break
    await fr.locator('[data-testid="stSidebar"] [data-testid="stSelectbox"]').first.click()
    options = fr.get_by_role("option")
    await options.first.wait_for(timeout=10_000)
    n = await options.count()
    if index >= n:
        await page.keyboard.press("Escape")
        return None, n
    name = (await options.nth(index).inner_text()).strip()
    await options.nth(index).click()
    return name, n


async def run_one(ctx, url, slug, expect_no_data, detail, out, shots, limit_ms):
    page = await ctx.new_page()
    res, seen = {"url": url}, {}
    try:
        t0 = time.monotonic()
        await page.goto(url, wait_until="domcontentloaded", timeout=limit_ms)
        if expect_no_data:
            ready = lambda s: any(NO_DATA in a for a in s["alerts"])  # noqa: E731
        else:
            ready = lambda s: len(s["headings"]) > 0  # noqa: E731
        fr, st, ok = await wait_idle(page, t0, ready, limit_ms, seen)
        res["overview"] = {"seconds": round(time.monotonic() - t0, 1), "ready": ok, **st}
        if fr is not None and ok and shots:
            await stitched_shot(page, fr, out / f"{slug}.jpg")
        if detail and ok and fr is not None and st.get("sidebar_select"):
            skipped = []
            for index in range(1, MAX_PLAYERS + 1):
                t1 = time.monotonic()
                name, n = await pick_option(page, fr, index)
                if name is None:
                    break
                # resolved = the rerun for this player has finished and drawn something (figures, or the
                # app's own notice); need_run keeps the previous player's view from being taken for this one.
                resolved = lambda s: s["images"] > 0 or len(s["alerts"]) > 0  # noqa: E731
                fr, st, ok2 = await wait_idle(page, t1, resolved if not expect_no_data else ready, limit_ms, seen,
                                              need_run=True)
                res["detail_player"] = name
                res["detail"] = {"seconds": round(time.monotonic() - t1, 1), "ready": ok2, **st}
                if expect_no_data or not ok2 or st.get("images") or st.get("exceptions") or st.get("traceback"):
                    break
                skipped.append({"player": name, "alerts": st.get("alerts", [])})
            res["skipped_players"] = skipped
            if fr is not None and shots and res.get("detail", {}).get("ready"):
                await stitched_shot(page, fr, out / f"{slug}_detail.jpg")
    except Exception as e:  # reported in the result, never hidden
        res["error"] = f"{type(e).__name__}: {e}"[:300]
    finally:
        res["saw_running"] = seen.get("running", False)
        res["script_states"] = sorted(seen.get("states", set()))
        await page.close()
    return res


def verdict(app, static, cloud):
    problems = []
    for step in ("overview", "detail"):
        s = static.get(step)
        if s is None:
            continue
        if not s.get("ready"):
            problems.append(f"{step}: not ready")
        if s.get("exceptions") or s.get("traceback"):
            problems.append(f"{step}: exception/Traceback")
        if app["missing_csv"]:
            if s.get("images"):
                problems.append(f"{step}: figures drawn although the CSV is missing")
            if not any(NO_DATA in a for a in s.get("alerts", [])):
                problems.append(f"{step}: no-data notice not shown")
        elif not s.get("images") and (step == "detail" or app["slug"].startswith("qf-")):
            problems.append(f"{step}: no figure" + (" (no player among the first tried had one)"
                                                    if step == "detail" else ""))
    if "error" in static:
        problems.append("error: " + static["error"])
    if "overview" not in static:
        problems.append("overview missing")
    if not app["slug"].startswith("qf-") and not app["missing_csv"] and "detail" not in static:
        problems.append("detail step did not run")
    if cloud is None:
        return problems, "cloud: not compared"
    if cloud.get("overview", {}).get("asleep"):
        return problems, "cloud: asleep"
    if "error" in cloud or not cloud.get("overview", {}).get("ready"):
        return problems, "cloud: no answer"
    diffs = []
    for step in ("overview", "detail"):
        a, b = static.get(step) or {}, cloud.get(step) or {}
        if a.get("images") != b.get("images"):
            diffs.append(f"{step}: figures {a.get('images')} here vs {b.get('images')} on Streamlit Cloud")
        if a.get("headings") != b.get("headings"):
            diffs.append(f"{step}: headings differ from Streamlit Cloud")
    if static.get("detail_player") != cloud.get("detail_player"):
        diffs.append("detail: a different player than on Streamlit Cloud")
    return problems + diffs, "cloud: differs" if diffs else "cloud: same"


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base_url")
    ap.add_argument("apps_json")
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    apps = json.loads(Path(args.apps_json).read_text(encoding="utf-8"))
    if args.only:
        keep = {s.strip() for s in args.only.split(",") if s.strip()}
        unknown = keep - {a["slug"] for a in apps}
        if unknown:
            sys.exit(f"--only: unknown page(s): {', '.join(sorted(unknown))}")
        apps = [a for a in apps if a["slug"] in keep]
    if not apps:
        sys.exit("no page to check")
    out = Path("pages_check")
    out.mkdir(exist_ok=True)
    base = args.base_url.rstrip("/")
    sem = asyncio.Semaphore(PARALLEL)
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1400, "height": 1000})

        async def task(app):
            slug, detail = app["slug"], not app["slug"].startswith("qf-")
            static, cloud = {}, None
            try:
                async with sem:
                    static = await run_one(ctx, f"{base}/{slug}.html", slug, bool(app["missing_csv"]), detail,
                                           out, True, LIMIT_MS)
                    if args.cloud:
                        cctx = await browser.new_context(viewport={"width": 1400, "height": 1000})
                        cloud = await run_one(cctx, f"https://wbc-{slug}.streamlit.app/", slug,
                                              bool(app["missing_csv"]), detail, out, False, CLOUD_LIMIT_MS)
                        await cctx.close()
                problems, cloud_note = verdict(app, static, cloud)
            except Exception as e:  # one app's crash must not hide the others' results
                problems, cloud_note = [f"checker error: {type(e).__name__}: {e}"[:300]], "cloud: -"
            results[slug] = {"ok": not problems, "problems": problems, "cloud_note": cloud_note,
                             "static": static, "cloud": cloud}
            print(f"{'OK ' if not problems else 'NG '} {slug:<20} {cloud_note:<20} {'; '.join(problems)}", flush=True)

        await asyncio.gather(*(task(a) for a in apps))
        await browser.close()

    order = [a["slug"] for a in apps]
    (out / "result.json").write_text(json.dumps({s: results[s] for s in order}, ensure_ascii=False, indent=1))
    lines = ["| app | ok | first render s | figures | detail player (skipped) | detail s | figures | busy seen | Streamlit Cloud | problems |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for s in order:
        r = results[s]
        st = r["static"]
        o, d = st.get("overview", {}), st.get("detail", {})
        skipped = len(st.get("skipped_players", []))
        lines.append(f"| {s} | {'OK' if r['ok'] else 'NG'} | {o.get('seconds', '')} | {o.get('images', '')} | "
                     f"{st.get('detail_player', '')}{f' ({skipped})' if skipped else ''} | {d.get('seconds', '')} | "
                     f"{d.get('images', '')} | {st.get('saw_running', '')} | {r['cloud_note']} | {'; '.join(r['problems'])} |")
    bad = [s for s in order if not results[s]["ok"]]
    lines.append(f"\n{len(order) - len(bad)} OK, {len(bad)} NG. Timings after the first page use a warm browser cache; "
                 f"3 pages load at once. 'detail s' is the time per player tried and includes up to {RUN_GRACE_S} s of "
                 "waiting to see the rerun start: stlite never reports data-test-script-state 'running' (run "
                 "41309172214), so it is not a render time.")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print(lines[-1].strip())
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    asyncio.run(main())
