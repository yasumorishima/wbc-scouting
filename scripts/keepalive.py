#!/usr/bin/env python3
"""Visit all Streamlit Cloud apps with a real browser to prevent Zzz sleep.

Streamlit Cloud requires a browser (JavaScript + WebSocket) to count as
"viewer activity". A plain HTTP GET only returns the static HTML shell
and does NOT wake or keep alive the Python app process.

This script uses Playwright (Chromium) to actually load each page.
If the app shows the "Zzzz" sleep page, it clicks the wake-up button.
"""

from __future__ import annotations

import asyncio
import sys
from playwright.async_api import async_playwright

URLS = [
    # NPB / MLB
    "https://npb-prediction.streamlit.app/",
    "https://yasumorishima-mlb-bat-tracking.streamlit.app/",
    "https://mlb-wp-engine.streamlit.app/",
    # WBC — Pool A (San Juan)
    "https://wbc-pr-batters.streamlit.app/",
    "https://wbc-pr-pitchers.streamlit.app/",
    "https://wbc-cuba-batters.streamlit.app/",
    "https://wbc-can-batters.streamlit.app/",
    "https://wbc-can-pitchers.streamlit.app/",
    "https://wbc-pan-batters.streamlit.app/",
    "https://wbc-pan-pitchers.streamlit.app/",
    "https://wbc-col-batters.streamlit.app/",
    "https://wbc-col-pitchers.streamlit.app/",
    # WBC — Pool B (Houston)
    "https://wbc-usa-batters.streamlit.app/",
    "https://wbc-usa-pitchers.streamlit.app/",
    "https://wbc-mex-batters.streamlit.app/",
    "https://wbc-mex-pitchers.streamlit.app/",
    "https://wbc-ita-batters.streamlit.app/",
    "https://wbc-ita-pitchers.streamlit.app/",
    "https://wbc-gb-batters.streamlit.app/",
    "https://wbc-gb-pitchers.streamlit.app/",
    # WBC — Pool C (Tokyo)
    "https://wbc-japan-batters.streamlit.app/",
    "https://wbc-japan-pitchers.streamlit.app/",
    "https://wbc-kor-batters.streamlit.app/",
    "https://wbc-kor-pitchers.streamlit.app/",
    "https://wbc-twn-batters.streamlit.app/",
    "https://wbc-aus-batters.streamlit.app/",
    # WBC — Pool D (Miami)
    "https://wbc-dr-batters.streamlit.app/",
    "https://wbc-dr-pitchers.streamlit.app/",
    "https://wbc-venezuela-batters.streamlit.app/",
    "https://wbc-venezuela-pitchers.streamlit.app/",
    "https://wbc-ned-batters.streamlit.app/",
    "https://wbc-ned-pitchers.streamlit.app/",
    "https://wbc-isr-batters.streamlit.app/",
    "https://wbc-isr-pitchers.streamlit.app/",
    "https://wbc-nic-batters.streamlit.app/",
]

TIMEOUT_MS = 120_000  # 2 min per page (sleep → wake can be slow)


async def visit(page, url: str) -> bool:
    """Load a Streamlit app page. Click wake-up button if sleeping."""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)

        # Wait briefly for JS to render sleep/wake UI or app content
        await page.wait_for_timeout(5000)

        # Check for the "wake up" button (Streamlit sleep page)
        wake_btn = page.get_by_role("button", name="Yes, get this app back up!")
        if await wake_btn.count() > 0:
            print(f"  WAKE  {url}")
            await wake_btn.click()
            # Wait for the app to actually start (up to 90s)
            await page.wait_for_timeout(90_000)
        else:
            print(f"  OK    {url}")

        return True
    except Exception as e:
        print(f"  NG    {url} — {e}")
        return False


async def main() -> int:
    print(f"Visiting {len(URLS)} Streamlit apps...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        ok = 0
        for url in URLS:
            if await visit(page, url):
                ok += 1

        await browser.close()

    ng = len(URLS) - ok
    print(f"Done: {ok} OK, {ng} NG")
    return 1 if ng > 0 else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
