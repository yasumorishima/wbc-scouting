"""Open every static (stlite) page in Chromium and check that it really renders.

For each app in apps.json (written by scripts/build_pages.py):
  1. overview: wait until the app is idle, then record the time, headings, figures (<img> drawn
     with a real size), Streamlit exceptions and "Traceback" text; stitch a full-length screenshot
     by scrolling the app's own scroll container (the page itself does not scroll);
  2. detail: pick the first player in the sidebar selectbox and record the same again
     (not for qf-*, whose sidebar selectbox is the season).
With --cloud, the same steps run on https://wbc-<slug>.streamlit.app/ and the headings and figure
counts of the two must match (a cloud app that does not answer is reported, not failed).

A page fails when it does not render within LIMIT_MS, shows an exception or a Traceback, or its
player detail (the whole page for qf-*) draws no figure; apps whose CSV is missing must instead show
their no-data notice and draw none.
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

LIMIT_MS = 300_000
IDLE_S = 4              # the app counts as idle after this many quiet seconds
PARALLEL = 3
SHOT_WIDTH = 800        # stored screenshots are scaled to this width (JPEG)
MAX_STEPS = 40          # at most 40 viewport heights per stitched screenshot
NO_DATA = "Statcast"    # the no-data notice of apps without a CSV mentions Statcast
EXPAND = ['[data-testid="stExpandSidebarButton"]', '[data-testid="stSidebarCollapsedControl"] button',
          '[data-testid="collapsedControl"] button']

STATE_JS = """() => {
  const scrollers = [...document.querySelectorAll('*')].filter(e => {
    const s = getComputedStyle(e);
    return (s.overflowY === 'auto' || s.overflowY === 'scroll') && e.scrollHeight > e.clientHeight + 20;
  });
  const main = document.querySelector('[data-testid="stMain"], section.main, [data-testid="stAppViewContainer"]');
  const root = main || document.body;
  const imgs = [...root.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth > 0 && i.getBoundingClientRect().width > 100);
  const heads = [...root.querySelectorAll('h1, h2, h3')].map(h => h.innerText.trim()).filter(Boolean);
  const status = document.querySelector('[data-testid="stStatusWidget"]');
  const text = document.body.innerText;
  return {
    images: imgs.length,
    headings: heads,
    exceptions: document.querySelectorAll('[data-testid="stException"]').length,
    traceback: text.includes('Traceback'),
    running: !!(status && /Running/i.test(status.innerText)) || document.querySelectorAll('[data-stale="true"]').length > 0,
    alerts: [...document.querySelectorAll('[data-testid="stAlert"]')].map(a => a.innerText.slice(0, 200)),
    sidebar_select: document.querySelectorAll('[data-testid="stSidebar"] [data-testid="stSelectbox"]').length,
    scroll_h: scrollers.length ? Math.max(...scrollers.map(e => e.scrollHeight)) : document.body.scrollHeight,
    textlen: text.length,
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


async def wait_idle(page, t0, ready):
    """Wait until ready(state) holds and nothing has changed for IDLE_S seconds."""
    last, quiet, state = None, 0, {}
    while (time.monotonic() - t0) * 1000 < LIMIT_MS:
        fr = await app_frame(page)
        if fr is not None:
            try:
                state = await fr.evaluate(STATE_JS)
            except Exception:
                state = {}
        if state and (state["exceptions"] or state["traceback"]):
            return fr, state, True
        key = (state.get("images"), tuple(state.get("headings", [])), state.get("textlen"))
        if state and ready(state) and not state["running"] and key == last:
            quiet += 1
            if quiet >= IDLE_S:
                return fr, state, True
        else:
            quiet = 0
        last = key
        await page.wait_for_timeout(1000)
    return await app_frame(page), state, False


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


async def run_one(ctx, url, slug, expect_no_data, detail, out, shots):
    page = await ctx.new_page()
    res = {"url": url}
    try:
        t0 = time.monotonic()
        await page.goto(url, wait_until="domcontentloaded", timeout=LIMIT_MS)
        if expect_no_data:
            ready = lambda s: any(NO_DATA in a for a in s["alerts"])  # noqa: E731
        else:
            ready = lambda s: len(s["headings"]) > 0  # noqa: E731
        fr, st, ok = await wait_idle(page, t0, ready)
        res["overview"] = {"seconds": round(time.monotonic() - t0, 1), "ready": ok, **st}
        if fr is not None and shots:
            await stitched_shot(page, fr, out / f"{slug}.jpg")
        if detail and ok and fr is not None and st.get("sidebar_select"):
            for sel in EXPAND:
                loc = fr.locator(sel)
                if await loc.count():
                    await loc.first.click()
                    break
            await page.wait_for_timeout(1500)
            await fr.locator('[data-testid="stSidebar"] [data-testid="stSelectbox"]').first.click()
            option = fr.get_by_role("option").nth(1)
            res["detail_player"] = (await option.inner_text()).strip()
            t1 = time.monotonic()
            await option.click()
            before = tuple(st["headings"])
            if expect_no_data:
                ready2 = ready
            else:
                ready2 = lambda s: s["images"] > 0 and tuple(s["headings"]) != before  # noqa: E731
            await page.wait_for_timeout(1500)
            fr, st2, ok2 = await wait_idle(page, t1, ready2)
            res["detail"] = {"seconds": round(time.monotonic() - t1, 1), "ready": ok2, **st2}
            if fr is not None and shots:
                await stitched_shot(page, fr, out / f"{slug}_detail.jpg")
    except Exception as e:  # reported in the result, never hidden
        res["error"] = f"{type(e).__name__}: {e}"[:300]
    finally:
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
            problems.append(f"{step}: no figure")
    if "error" in static:
        problems.append("error: " + static["error"])
    if "overview" not in static:
        problems.append("overview missing")
    if not app["slug"].startswith("qf-") and not app["missing_csv"] and "detail" not in static:
        problems.append("detail step did not run")
    if cloud is not None:
        if "error" in cloud or not cloud.get("overview", {}).get("ready"):
            cloud_note = "cloud: no answer"
        else:
            cloud_note = "cloud: same"
            for step in ("overview", "detail"):
                a, b = static.get(step), cloud.get(step)
                if a and b:
                    if a["images"] != b["images"]:
                        problems.append(f"{step}: figures {a['images']} here vs {b['images']} on Streamlit Cloud")
                    if a["headings"] != b["headings"]:
                        problems.append(f"{step}: headings differ from Streamlit Cloud")
            if static.get("detail_player") != cloud.get("detail_player"):
                problems.append("detail: different first player than Streamlit Cloud")
            if problems:
                cloud_note = "cloud: differs"
    else:
        cloud_note = "cloud: not compared"
    return problems, cloud_note


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base_url")
    ap.add_argument("apps_json")
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    apps = json.loads(Path(args.apps_json).read_text(encoding="utf-8"))
    if args.only:
        keep = set(args.only.split(","))
        apps = [a for a in apps if a["slug"] in keep]
    out = Path("pages_check")
    out.mkdir(exist_ok=True)
    base = args.base_url.rstrip("/")
    sem = asyncio.Semaphore(PARALLEL)
    results = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(viewport={"width": 1400, "height": 1000})

        async def task(app):
            async with sem:
                slug, detail = app["slug"], not app["slug"].startswith("qf-")
                static = await run_one(ctx, f"{base}/{slug}.html", slug, bool(app["missing_csv"]), detail, out, True)
                cloud = None
                if args.cloud:
                    cctx = await browser.new_context(viewport={"width": 1400, "height": 1000})
                    cloud = await run_one(cctx, f"https://wbc-{slug}.streamlit.app/", slug,
                                          bool(app["missing_csv"]), detail, out, False)
                    await cctx.close()
                problems, cloud_note = verdict(app, static, cloud)
                results[slug] = {"ok": not problems, "problems": problems, "cloud_note": cloud_note,
                                 "static": static, "cloud": cloud}
                print(f"{'OK ' if not problems else 'NG '} {slug:<20} {cloud_note:<20} {'; '.join(problems)}", flush=True)

        await asyncio.gather(*(task(a) for a in apps))
        await browser.close()

    order = [a["slug"] for a in apps]
    (out / "result.json").write_text(json.dumps({s: results[s] for s in order}, ensure_ascii=False, indent=1))
    lines = ["| app | ok | first render s | figures | detail player | detail s | figures | Streamlit Cloud | problems |",
             "|---|---|---|---|---|---|---|---|---|"]
    for s in order:
        r = results[s]
        o, d = r["static"].get("overview", {}), r["static"].get("detail", {})
        lines.append(f"| {s} | {'OK' if r['ok'] else 'NG'} | {o.get('seconds', '')} | {o.get('images', '')} | "
                     f"{r['static'].get('detail_player', '')} | {d.get('seconds', '')} | {d.get('images', '')} | "
                     f"{r['cloud_note']} | {'; '.join(r['problems'])} |")
    bad = [s for s in order if not results[s]["ok"]]
    lines.append(f"\n{len(order) - len(bad)} OK, {len(bad)} NG. Timings after the first page use a warm browser cache.")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print(lines[-1].strip())
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    asyncio.run(main())
