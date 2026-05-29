"""Scrape all listing pages of mcpservers.org/all → JSONL of (slug, name, description, is_sponsor, page)."""
import asyncio
import json
import re
import sys
from pathlib import Path

import aiohttp

BASE = "https://mcpservers.org/all?page={}&sort=newest"
TOTAL_PAGES = 284
OUT = Path(r"C:\tmp\mcp-scrape\listings.jsonl")
CONCURRENCY = 12
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

CARD_RE = re.compile(
    r'<a href="(/servers/[^"]+)" class="block">'
    r'.*?'
    r'<div class="tracking-tight text-lg font-semibold">([^<]+)</div>'
    r'(?:.*?<span[^>]*>(sponsor)</span>)?'
    r'.*?'
    r'<div class="text-sm text-gray-600 leading-relaxed line-clamp-3">([^<]*)</div>',
    re.S,
)


async def fetch_page(session, page, sem):
    async with sem:
        url = BASE.format(page)
        for attempt in range(4):
            try:
                async with session.get(url, headers=HEADERS, timeout=30) as r:
                    html = await r.text()
                    return page, html
            except Exception as e:
                if attempt == 3:
                    print(f"FAIL page {page}: {e}", file=sys.stderr)
                    return page, ""
                await asyncio.sleep(2 * (attempt + 1))


def parse_cards(html, page):
    # Restrict to the cards grid: remove sponsor at top so flags align with cards properly
    out = []
    for m in CARD_RE.finditer(html):
        slug = m.group(1).removeprefix("/servers/")
        name = m.group(2).strip()
        sponsor = bool(m.group(3))
        desc = m.group(4).strip()
        out.append(
            {"slug": slug, "name": name, "description": desc, "sponsor": sponsor, "page": page}
        )
    return out


async def main():
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_page(session, p, sem) for p in range(1, TOTAL_PAGES + 1)]
        done = 0
        all_cards = []
        for coro in asyncio.as_completed(tasks):
            page, html = await coro
            cards = parse_cards(html, page) if html else []
            all_cards.extend(cards)
            done += 1
            if done % 20 == 0 or done == TOTAL_PAGES:
                print(f"  {done}/{TOTAL_PAGES} pages, {len(all_cards)} cards so far", flush=True)

    # Dedup by slug, keep first occurrence (lowest page = newest)
    seen = set()
    deduped = []
    for c in sorted(all_cards, key=lambda x: x["page"]):
        if c["slug"] in seen:
            continue
        seen.add(c["slug"])
        deduped.append(c)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for c in deduped:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"DONE: {len(deduped)} unique servers written to {OUT}")


if __name__ == "__main__":
    asyncio.run(main())
