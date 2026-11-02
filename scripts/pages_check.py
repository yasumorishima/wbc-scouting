"""Open the published static pages in Chromium and check every state against the build manifest.

For each dashboard (manifest/index.json on the site, written by scripts/prerender.py):
  1. its address <slug>.html opens, shows its first screen (every figure visible there loaded)
     within FIRST_MS, and raises no script error; a full-length screenshot is kept (desktop and
     phone width);
  2. every page of the dashboard (one per language/player/season) opens; on each, every
     main-area state (stadium, density, pitch type, ...) is selected through the page's own
     controls, and the figures shown must be exactly the manifest's figures for that state, in
     order, and the text shown must be the text the build made for it (sidebar text too); then
     every option of every control is chosen once from the first state, and the controls must
     name a built state that the page then shows;
  3. every figure file the site references answers 200;
  4. choosing another player in the sidebar opens that player's page, and Back shows the first
     page with its own sidebar choices and the main-area choice made before leaving; opening the
     address again starts at the defaults.
On every page, nothing marked hidden (closed tab panels, ...) may be displayed, and the main column
has a heading or a notice (on the dashboard's own address: a heading, or the no-data notice of an
app without data). A dashboard must draw a figure in some state of some page, unless every page
shows the no-data notice.
Output: pages_check/result.json, pages_check/summary.md, pages_check/<slug>.jpg / <slug>_phone.jpg.
Exit 1 when anything fails.

usage: python scripts/pages_check.py <base_url> [--only slug,slug]
"""
import argparse
import asyncio
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

FIRST_MS = 3_000      # the first screen of a dashboard (with its figures) must show within this
PARALLEL = 6
FILES_LIMIT_S = 1800  # at most this long asking for figure files (the check job has 120 min)
NO_DATA = "Statcast"  # the no-data notice of apps without data mentions Statcast
SHOT_WIDTH = 800

# every figure of the state in document order (figures in a closed tab or expander count too:
# they are part of the state, as in the manifest)
SHOWN_JS = """() => [...document.querySelectorAll('.block-container img')]
  .map(i => i.getAttribute('src').split('/').pop().split('.')[0])"""

SET_JS = """(inner) => {
  // select a main-area state with the page's own controls, the way a person would
  for (const [id, v] of Object.entries(inner)) {
    const el = document.querySelector(`.block-container select[data-w="${id}"]`)
      || document.querySelector(`.block-container input[type=checkbox][data-w="${id}"]`)
      || document.querySelector(`.block-container input[type=radio][data-w="${id}"][value="${v}"]`);
    if (!el) return `no control ${id}`;
    if (el.tagName === 'SELECT') { if (el.value === String(v)) continue; el.value = String(v); }
    else if (el.type === 'checkbox') { if (el.checked === (v === 1)) continue; el.checked = v === 1; }
    else { if (el.checked) continue; el.checked = true; }
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }
  return null;
}"""


# sha1 of the shown text without ASCII whitespace; prerender.py's text_digest() makes the same
# from the html it built, so a wrong, stale or missing segment shows as a difference
TEXT_JS = """async (sel) => {
  const t = document.querySelector(sel).textContent.replace(/[ \\t\\n\\r\\f]+/g, '');
  const b = await crypto.subtle.digest('SHA-1', new TextEncoder().encode(t));
  return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, '0')).join('');
}"""

# the first screen is shown: the document is parsed and every figure that is visible in the first
# viewport (not in a closed expander or another tab) has loaded; a page with none there counts
# as shown once parsed
FIRST_JS = """() => {
  if (document.readyState === 'loading') return false;
  const c = document.querySelector('.block-container');
  if (!c) return false;
  return [...c.querySelectorAll('img')]
    .filter(i => i.checkVisibility() && i.getBoundingClientRect().top < innerHeight)
    .every(i => i.complete && i.naturalWidth > 0);
}"""
FIRST_COUNT_JS = """() => [...document.querySelectorAll('.block-container img')]
  .filter(i => i.checkVisibility() && i.getBoundingClientRect().top < innerHeight).length"""

# elements marked hidden that a style still displays (a closed tab panel shown below the open one)
HIDDEN_SHOWN_JS = """() => [...document.querySelectorAll('[hidden]')]
  .filter(e => getComputedStyle(e).display !== 'none')
  .map(e => e.tagName + (e.getAttribute('role') ? '[' + e.getAttribute('role') + ']' : '')).slice(0, 5)"""

# every main-area control on the page and its options (radio: one entry per group)
CONTROLS_JS = """() => {
  const out = {};
  document.querySelectorAll('.block-container [data-w]').forEach(el => {
    const id = el.dataset.w;
    if (el.tagName === 'SELECT') out[id] = [...el.options].map(o => Number(o.value));
    else if (el.type === 'checkbox') out[id] = [0, 1];
    else (out[id] = out[id] || []).push(Number(el.value));
  });
  return out;
}"""

# what the controls say now
VALUES_JS = """() => {
  const out = {};
  document.querySelectorAll('.block-container [data-w]').forEach(el => {
    if (el.tagName === 'SELECT') out[el.dataset.w] = Number(el.value);
    else if (el.type === 'checkbox') out[el.dataset.w] = el.checked ? 1 : 0;
    else if (el.checked) out[el.dataset.w] = Number(el.value);
  });
  return out;
}"""


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def answers(url, tries=4, base_wait=2.0, stop_at=float("inf")):
    """None when url answers 200 to HEAD, else why it did not (the last status or error).
    A 404 is final; anything else (429, 5xx, a dropped connection) is waited out and retried,
    and still counts if it never answers. No waiting past stop_at."""
    if time.time() >= stop_at:
        return "time limit"
    req = urllib.request.Request(url, method="HEAD")
    why = "no answer"
    for i in range(tries):
        wait = base_wait * 2 ** i
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                if r.status == 200:
                    return None
                why = str(r.status)
        except urllib.error.HTTPError as e:
            why = str(e.code)
            if e.code == 404:
                return why
            retry_after = (e.headers or {}).get("Retry-After", "")
            if retry_after.isdigit():
                wait = max(wait, min(int(retry_after), 60))
        except Exception as e:  # noqa: BLE001 - retried, then counted as missing
            why = type(e).__name__
        if i + 1 < tries:
            if time.time() + wait >= stop_at:
                return f"{why}, then time limit"
            time.sleep(wait)
    return why


def check_files(base, names, pause=30.0, base_wait=2.0, limit_s=FILES_LIMIT_S):
    """Ask base/<name> for every name: a 32-way sweep, then the ones refused for any reason but
    404 (a host limiting the sweep) again, 4 at a time, in rounds after a pause that doubles up to
    4 minutes, until none is refused. Stops waiting after limit_s in all; files not answered by
    then count as missing ("time limit"), so a host that keeps refusing cannot use up the job's
    time before the pages are checked.
    Returns (missing names in order, {last answer: count})."""
    from concurrent.futures import ThreadPoolExecutor
    stop_at = time.time() + limit_s
    with ThreadPoolExecutor(32) as ex:
        why = dict(zip(names, ex.map(
            lambda n: answers(f"{base}/{n}", base_wait=base_wait, stop_at=stop_at), names)))
    rnd = 0
    while True:
        again = [n for n in names if why[n] is not None and why[n] != "404"]
        left = stop_at - time.time()
        if not again or left < 5:
            break
        rnd += 1
        wait = min(pause, left - 4)  # the last round still gets the time that is left
        print(f"{len(again)} files not answered yet; round {rnd} after {wait:.0f} s", flush=True)
        time.sleep(wait)
        with ThreadPoolExecutor(4) as ex:
            why.update(zip(again, ex.map(
                lambda n: answers(f"{base}/{n}", tries=6, base_wait=base_wait, stop_at=stop_at), again)))
        pause = min(pause * 2, 240.0)
    missing = [n for n in names if why[n] is not None]
    reasons = {}
    for n in missing:
        reasons[why[n]] = reasons.get(why[n], 0) + 1
    return missing, reasons


async def shot(page, path, width):
    await page.set_viewport_size({"width": width, "height": 900})
    await page.evaluate("() => document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
    await page.wait_for_load_state("networkidle")
    png = await page.screenshot(full_page=True)
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if im.width > SHOT_WIDTH:
        im = im.resize((SHOT_WIDTH, round(im.height * SHOT_WIDTH / im.width)))
    im = im.crop((0, 0, im.width, min(im.height, 12000)))
    im.save(path, quality=70)


class NotLoaded(Exception):
    pass


def first_line(e, n):
    return f"{type(e).__name__}: {(str(e).splitlines() or [''])[0][:n]}"


def answered(resp, err):
    return f"{resp.status}" if resp is not None else (err or "nothing")


async def goto(page, url, wait_until="domcontentloaded", tries=4):
    """page.goto, opened again (after 2, 4, 8 s) while the host answers 429 or 5xx or the load
    fails (a dropped connection, a timeout). Returns (response or None, the time the last attempt
    started, the last load error) so the first screen is timed from the attempt that answered."""
    resp, started, err = None, time.time(), None
    for i in range(max(tries, 1)):
        started = time.time()
        try:
            resp, err = await page.goto(url, wait_until=wait_until), None
        except Exception as e:  # noqa: BLE001 - Playwright raises on net::ERR_* and timeouts
            resp, err = None, f"{first_line(e, 120)}"
        if resp is not None and resp.status != 429 and resp.status < 500:
            break
        if i + 1 < tries:
            await asyncio.sleep(2 * 2 ** i)
    return resp, started, err


async def must_goto(page, url):
    """goto, raising NotLoaded unless the page answered 200."""
    resp, _, err = await goto(page, url)
    if resp is None or resp.status != 200:
        raise NotLoaded(f"{url} answered {answered(resp, err)}")


async def check_app(ctx, res, base, m, out):
    """Fills res (errors, pages, states, ...); the caller owns ctx and records anything raised."""
    slug = m["slug"]
    page = await ctx.new_page()
    page.on("pageerror", lambda e: res["errors"].append(f"script error: {e}"))

    # 1. the address everyone links to
    resp, t0, err = await goto(page, f"{base}/{slug}.html", wait_until="commit")
    if not resp or resp.status != 200:
        res["errors"].append(f"{slug}.html answered {answered(resp, err)}")
        return res
    try:
        await page.wait_for_function(FIRST_JS, timeout=FIRST_MS * 5)
        res["first_ms"] = round((time.time() - t0) * 1000)
        res["first_figures"] = await page.evaluate(FIRST_COUNT_JS)
        if res["first_ms"] > FIRST_MS:
            res["errors"].append(f"first screen after {res['first_ms']} ms (limit {FIRST_MS})")
    except Exception as e:  # noqa: BLE001
        res["errors"].append(f"first screen not shown: {e}")
    await shot(page, out / f"{slug}.jpg", 1280)
    await shot(page, out / f"{slug}_phone.jpg", 390)
    await page.set_viewport_size({"width": 1280, "height": 900})

    # 2. every page, every main-area state
    by_outer = {}
    for s in m["states"]:
        by_outer.setdefault(s["outer"], []).append(s)
    for outer, states in by_outer.items():
        url = f"{base}/{slug}/{outer}.html"
        r, _, err = await goto(page, url)
        if not r or r.status != 200:
            res["errors"].append(f"{slug}/{outer}.html answered {answered(r, err)}")
            continue
        res["pages"] += 1
        shown_hidden = await page.evaluate(HIDDEN_SHOWN_JS)
        if shown_hidden:
            res["errors"].append(f"{outer}: hidden elements are displayed: {shown_hidden}")
        # the dashboard's own address shows a heading in its main column (an app without data: its
        # no-data notice); another page shows a heading or the app's notice (a player without data
        # for the chosen season gets "このフィルターではデータがありません。" and nothing else)
        head = await page.evaluate("""([nd, first]) => document.querySelectorAll('.block-container :is(h1, h2, h3)').length > 0
            || [...document.querySelectorAll('.block-container [data-testid=stAlert]')].some(a => !first || a.textContent.includes(nd))""",
                                   [NO_DATA, outer == m["default"]])
        if not head:
            res["errors"].append(f"{outer}: no heading and no notice in the main column")
        if any(s["images"] for s in states):
            res["pages_with_figures"] = res.get("pages_with_figures", 0) + 1
        elif await page.evaluate("""(nd) => [...document.querySelectorAll('.block-container [data-testid=stAlert]')]
            .some(a => a.textContent.includes(nd))""", NO_DATA):
            res["no_data_pages"] = res.get("no_data_pages", 0) + 1
        side = m.get("sidebar_text", {}).get(outer)
        if side and await page.evaluate(TEXT_JS, "#sidebar .st-sb-inner") != side:
            res["errors"].append(f"{outer}: sidebar text differs from the build")
        by_inner = {json.dumps(s["inner"], sort_keys=True): s for s in states}

        async def same(s, what, outer=outer):
            shown = await page.evaluate(SHOWN_JS)
            text = await page.evaluate(TEXT_JS, ".block-container")
            if shown != s["images"] or text != s["text"]:
                res["errors"].append(f"{outer} {what}: " + ("figures differ" if shown != s["images"] else "text differs")
                                     + f" (shown {len(shown)} figures, expected {len(s['images'])})")

        for s in states:
            err = await page.evaluate(SET_JS, s["inner"])
            res["states"] += 1
            if err:
                res["errors"].append(f"{outer} {s['inner']}: {err}")
            else:
                await same(s, s["inner"])
            if len(res["errors"]) > 20:
                break
        # every option of every control does something: from the page's first state, choose it;
        # the controls must then name a built state, and the page must show exactly that state
        await must_goto(page, url)
        for wid, values in (await page.evaluate(CONTROLS_JS)).items():
            for val in values:
                if len(res["errors"]) > 20:
                    break
                await page.evaluate(SET_JS, states[0]["inner"])
                if await page.evaluate(f"() => !!document.querySelector('.block-container [data-w=\"{wid}\"]')"):
                    await page.evaluate(SET_JS, {wid: val})
                now = await page.evaluate(VALUES_JS)
                s = by_inner.get(json.dumps(now, sort_keys=True))
                res["options"] = res.get("options", 0) + 1
                if s is None:
                    res["errors"].append(f"{outer} {wid}={val}: the controls show {now}, which is no built state")
                else:
                    await same(s, f"{wid}={val}")

    # a dashboard draws figures somewhere (a player without Statcast rows draws none and says so);
    # only an app without data may have none, and then every page shows its no-data notice
    if not res.get("pages_with_figures") and res.get("no_data_pages", 0) != res["pages"]:
        res["errors"].append(f"no state of any page has a figure ({res.get('no_data_pages', 0)} of "
                             f"{res['pages']} pages show the no-data notice)")

    # 4. the sidebar opens another player's page. Start from a page with main-area choices (when
    # the dashboard has one) and a neighbour page that differs in one sidebar choice.
    pages = {}
    for s in m["states"]:
        pages.setdefault(s["outer"], []).append(s)
    url_of = lambda o: f"{base}/{slug}.html" if o == m["default"] else f"{base}/{slug}/{o}.html"  # noqa: E731
    plan = None
    for a in sorted(pages, key=lambda o: (all(s["inner"] == pages[o][0]["inner"] for s in pages[o]), o != m["default"])):
        av = a.split("-")
        b = next((b for b in pages if len(b.split("-")) == len(av)
                  and sum(x != y for x, y in zip(av, b.split("-"))) == 1), None)
        if b:
            plan = (a, b)
            break
    if plan:
        start, target_outer = plan
        home = pages[start]
        # a main-area choice other than the default, made before leaving (kept on the way Back)
        other = next((s for s in home if s["inner"] != home[0]["inner"]), None)
        await must_goto(page, url_of(start))
        if other:
            await page.evaluate(SET_JS, other["inner"])
        await page.click(".st-sb-toggle")
        target = {"outer": target_outer}
        key_vals = target_outer.split("-")
        diff = next((i for i, (x, y) in enumerate(zip(key_vals, start.split("-"))) if x != y), None)
        if diff is not None:
            ids = await page.evaluate("() => JSON.parse(document.getElementById('st-data').textContent).nav.sidebar")
            wid = ids[diff]
            sel = page.locator(f'#sidebar select[data-w="{wid}"]')
            if await sel.count():
                async with page.expect_navigation():
                    await sel.select_option(key_vals[diff])
                if page.url.split("?")[0] != url_of(target["outer"]):
                    res["errors"].append(f"sidebar choice opened {page.url}, expected {url_of(target['outer'])}")
                # Back: the first page's sidebar must show its own choices again
                await page.go_back(wait_until="domcontentloaded")
                await page.wait_for_timeout(300)
                wrong = await page.evaluate("""() => {
                  const d = JSON.parse(document.getElementById('st-data').textContent);
                  return [...document.querySelectorAll('#sidebar select[data-w]')]
                    .filter(el => String(d.outer[el.dataset.w]) !== el.value).map(el => el.dataset.w);
                }""")
                if wrong:
                    res["errors"].append(f"after Back the sidebar shows other choices in {wrong}")
                if other:
                    now = await page.evaluate(VALUES_JS)
                    res["back_kept"] = now
                    if now != other["inner"]:
                        res["errors"].append(f"after Back the page shows {now}, not the choice made before leaving {other['inner']}")
                    elif (await page.evaluate(SHOWN_JS) != other["images"]
                          or await page.evaluate(TEXT_JS, ".block-container") != other["text"]):
                        res["errors"].append(f"after Back the controls show {now} but the page shows another state")
                    # opening the address again is a new session: the defaults
                    await must_goto(page, url_of(start))
                    now = await page.evaluate(VALUES_JS)
                    if now != home[0]["inner"]:
                        res["errors"].append(f"opened again, the page shows {now}, not the defaults {home[0]['inner']}")
    return res


async def run(base, only):
    index = fetch_json(f"{base}/manifest/index.json")
    unknown = sorted(set(only) - set(index["slugs"]))
    if unknown:
        sys.exit(f"--only names dashboards the site does not have: {', '.join(unknown)}")
    slugs = [s for s in index["slugs"] if not only or s in only]
    if not slugs:
        sys.exit("no dashboard to check")
    out = Path("pages_check")
    out.mkdir(exist_ok=True)
    manifests = {s: fetch_json(f"{base}/manifest/{s}.json") for s in slugs}

    # 3. every figure file answers
    names = sorted({f"{sha}.{index['ext']}" for m in manifests.values() for s in m["states"] for sha in s["images"]})

    missing, reasons = check_files(f"{base}/img", names)

    sem = asyncio.Semaphore(PARALLEL)
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        async def one(s):
            async with sem:
                r = {"slug": s, "errors": [], "states": 0, "pages": 0}
                ctx = await browser.new_context(viewport={"width": 1280, "height": 900})
                try:
                    await check_app(ctx, r, base, manifests[s], out)
                except NotLoaded as e:
                    r["errors"].append(f"check stopped: {e}")
                except Exception as e:  # noqa: BLE001 - this dashboard fails; the others are still checked
                    r["errors"].append(f"check stopped: {first_line(e, 200)}")
                finally:
                    await ctx.close()
                print(("OK  " if not r["errors"] else "FAIL"), s,
                      f"pages={r['pages']} states={r['states']} options={r.get('options', 0)}",
                      f"first={r.get('first_ms')}ms ({r.get('first_figures')} figures on the first screen)",
                      f"back_kept={r.get('back_kept')}",
                      "; ".join(r["errors"][:3]), flush=True)
                return r
        results = await asyncio.gather(*(one(s) for s in slugs))
        await browser.close()

    bad = [r for r in results if r["errors"]]
    lines = ["# Pages check", "", f"{len(results) - len(bad)}/{len(results)} dashboards OK; "
             f"{sum(r['states'] for r in results)} states on {sum(r['pages'] for r in results)} pages checked, "
             f"{sum(r.get('options', 0) for r in results)} control options tried; "
             f"{len(names) - len(missing)}/{len(names)} figure files answer.", "",
             "| dashboard | pages | states | first figure | problems |", "|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['slug']} | {r['pages']} | {r['states']} | {r.get('first_ms', '-')} ms | "
                     f"{'; '.join(r['errors'][:2]) or 'none'} |")
    if missing:
        lines += ["", f"Missing figure files ({len(missing)}; by last answer: "
                  + ", ".join(f"{k} {v}" for k, v in sorted(reasons.items())) + "): " + ", ".join(missing[:20])]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "result.json").write_text(json.dumps({"results": results, "missing": missing,
                                                 "missing_by_answer": reasons}, indent=1), encoding="utf-8")
    print("\n".join(lines[:3]))
    return 1 if bad or missing else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base_url")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    only = {s for s in a.only.split(",") if s}
    sys.exit(asyncio.run(run(a.base_url.rstrip("/"), only)))


if __name__ == "__main__":
    main()
