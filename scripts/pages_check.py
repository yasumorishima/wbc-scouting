"""Open the static (stlite) page and the Streamlit Cloud app in Chromium and time two things:
  1. first render: until the app's own text MARK is visible (not the platform shell or a spinner);
  2. player detail: open the sidebar, pick PLAYER in the player selectbox, until DETAIL_MARK is visible.
Screenshots of both states go to pages_check/<name>.png and <name>_player.png; numbers to result.json.

usage: python scripts/pages_check.py <static_url> <streamlit_url>
"""
import asyncio
import json
import re
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

MARK = "選手"
PLAYER = "大谷翔平"
DETAIL_MARK = "ストライクゾーン ヒートマップ"
LIMIT_MS = 300_000
EXPAND = ['[data-testid="stExpandSidebarButton"]', '[data-testid="stSidebarCollapsedControl"] button',
          '[data-testid="collapsedControl"] button']


async def frame_with(page, text):
    for fr in page.frames:
        try:
            if text in await fr.inner_text("body", timeout=2000):
                return fr
        except Exception:
            pass
    return None


async def all_text(page):
    out = []
    for fr in page.frames:
        try:
            out.append(await fr.inner_text("body", timeout=2000))
        except Exception:
            pass
    return "\n".join(out)


async def wait_for(page, text, t0):
    while (time.monotonic() - t0) * 1000 < LIMIT_MS:
        body = await all_text(page)
        if text in body or "Traceback" in body:
            return body
        await page.wait_for_timeout(1000)
    return await all_text(page)


async def measure(browser, url, name, out):
    page = await browser.new_page(viewport={"width": 1400, "height": 1000})
    res = {"url": url}
    t0 = time.monotonic()
    await page.goto(url, wait_until="domcontentloaded", timeout=LIMIT_MS)
    body = await wait_for(page, MARK, t0)
    res.update(seconds=round(time.monotonic() - t0, 1), rendered=MARK in body, traceback="Traceback" in body)
    await page.wait_for_timeout(8000)
    await page.screenshot(path=str(out / f"{name}.png"), full_page=True)

    fr = await frame_with(page, MARK)
    try:
        for sel in EXPAND:
            loc = fr.locator(sel)
            if await loc.count():
                await loc.first.click()
                break
        await page.wait_for_timeout(1500)
        await fr.locator('[data-testid="stSidebar"] [data-testid="stSelectbox"]').first.click()
        t1 = time.monotonic()
        await fr.get_by_role("option", name=re.compile(PLAYER)).first.click()
        body = await wait_for(page, DETAIL_MARK, t1)
        res.update(player_seconds=round(time.monotonic() - t1, 1), player_rendered=DETAIL_MARK in body,
                   player_traceback="Traceback" in body)
        await page.wait_for_timeout(10000)
        await page.screenshot(path=str(out / f"{name}_player.png"), full_page=True)
    except Exception as e:  # report, do not hide
        res["player_error"] = f"{type(e).__name__}: {e}"[:300]
    await page.close()
    return res


async def main():
    static_url, cloud_url = sys.argv[1], sys.argv[2]
    out = Path("pages_check")
    out.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        res = {"static": await measure(browser, static_url, "static", out),
               "streamlit_cloud": await measure(browser, cloud_url, "streamlit_cloud", out)}
        await browser.close()
    (out / "result.json").write_text(json.dumps(res, ensure_ascii=False, indent=2))
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
