"""Open the static (stlite) page and the Streamlit Cloud app in Chromium, time how long until the
app's own content is visible, and save a screenshot of each to pages_check/.

usage: python scripts/pages_check.py <static_url> <streamlit_url>
"Visible" = the app's own text MARK is rendered (not the platform shell or a loading spinner).
"""
import asyncio
import json
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

MARK = "選手"  # appears in the app's own widgets once the script has run
LIMIT_MS = 300_000


async def page_text(page):
    texts = []
    for fr in page.frames:
        try:
            texts.append(await fr.inner_text("body", timeout=2000))
        except Exception:
            pass
    return "\n".join(texts)


async def measure(browser, url, name, out):
    page = await browser.new_page(viewport={"width": 1400, "height": 1000})
    t0 = time.monotonic()
    await page.goto(url, wait_until="domcontentloaded", timeout=LIMIT_MS)
    text = ""
    while (time.monotonic() - t0) * 1000 < LIMIT_MS:
        text = await page_text(page)
        if MARK in text or "Traceback" in text:
            break
        await page.wait_for_timeout(1000)
    result = {"url": url, "seconds": round(time.monotonic() - t0, 1),
              "rendered": MARK in text, "traceback": "Traceback" in text}
    await page.wait_for_timeout(8000)  # let charts finish drawing
    await page.screenshot(path=str(out / f"{name}.png"), full_page=True)
    result["text_head"] = (await page_text(page))[:600]
    await page.close()
    return result


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
    print(json.dumps({k: {x: v[x] for x in ("seconds", "rendered", "traceback")} for k, v in res.items()}))


if __name__ == "__main__":
    asyncio.run(main())
