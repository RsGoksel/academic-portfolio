"""Scrape mcpmarket.com via sitemap.

Two indexes:
  - tools-*.xml: MCP servers (URL pattern /server/<slug>)
  - skills-*.xml: Agent skills (URL pattern /skills/<slug>)

We only want the servers for parity with the mcpservers.org dataset.
Each /server/<slug> page is scraped for: name, tagline, README, categories, author, related MCPs.

Outputs:
  C:/tmp/mcp-scrape/mcpmarket_listings.jsonl  (slug, url, lastmod)
  C:/tmp/mcp-scrape/mcpmarket_details.jsonl   (parsed per-server data)
  C:/tmp/mcp-scrape/mcpmarket_errors.jsonl    (failures)
"""
import asyncio
import json
import re
import sys
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

BASE = Path(r"C:\tmp\mcp-scrape")
LISTINGS = BASE / "mcpmarket_listings.jsonl"
DETAILS = BASE / "mcpmarket_details.jsonl"
ERRORS = BASE / "mcpmarket_errors.jsonl"

SITEMAP_INDEX = "https://mcpmarket.com/sitemap.xml"
CONCURRENCY = 12
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


async def fetch_text(session, url, sem):
    async with sem:
        for attempt in range(4):
            try:
                async with session.get(url, headers=HEADERS, timeout=30) as r:
                    return await r.text()
            except Exception as e:
                if attempt == 3:
                    print(f"FAIL {url}: {e}", file=sys.stderr)
                    return ""
                await asyncio.sleep(1.5 * (attempt + 1))


async def discover_listings(session, sem):
    """Pull all /server/<slug> URLs from tools-*.xml sitemaps."""
    index_xml = await fetch_text(session, SITEMAP_INDEX, sem)
    tool_sitemaps = sorted(set(
        re.findall(r"https://mcpmarket\.com/sitemap/tools-\d+\.xml", index_xml)
    ))
    print(f"Tool sitemaps: {len(tool_sitemaps)}", flush=True)

    all_urls = []
    for sm in tool_sitemaps:
        xml = await fetch_text(session, sm, sem)
        urls = re.findall(r"<loc>(https://mcpmarket\.com/server/[^<]+)</loc>", xml)
        # capture lastmod if present
        entries = re.findall(
            r"<url>\s*<loc>(https://mcpmarket\.com/server/[^<]+)</loc>\s*(?:<lastmod>([^<]+)</lastmod>)?",
            xml,
        )
        for url, lm in entries:
            all_urls.append({"url": url, "lastmod": lm or ""})
        if not entries:
            for u in urls:
                all_urls.append({"url": u, "lastmod": ""})

    # dedup
    seen = set()
    uniq = []
    for e in all_urls:
        if e["url"] in seen:
            continue
        seen.add(e["url"])
        e["slug"] = e["url"].removeprefix("https://mcpmarket.com/server/")
        uniq.append(e)
    return uniq


def parse_detail(html, slug, url):
    soup = BeautifulSoup(html, "lxml")

    # Title
    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else ""

    # H1 / name
    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else ""

    # Strip noise then pull readable text
    for tag in soup(["script", "style", "svg", "noscript"]):
        tag.decompose()

    # Tagline / description: usually a short paragraph near header
    tagline = ""
    if h1:
        nxt = h1.find_next(["p", "div"])
        if nxt:
            t = nxt.get_text(" ", strip=True)
            if 10 < len(t) < 400:
                tagline = t

    # Categories: look for category links
    categories = []
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("/categories/"):
            txt = a.get_text(strip=True)
            if txt and len(txt) < 60:
                categories.append(txt)
    categories = list(dict.fromkeys(categories))

    # Author
    author = ""
    m = re.search(r'href="/(?:user|profile|by)/([^"]+)"', html)
    if m:
        author = m.group(1)
    else:
        # Fallback: pattern "by <name>" in visible text
        text = soup.get_text(" ", strip=True)
        ma = re.search(r"\bby\s+([A-Za-z0-9_-]{2,40})\b", text)
        if ma:
            author = ma.group(1)

    # README section: many pages show a README header
    readme_md = ""
    readme_marker = soup.find(string=re.compile(r"^README$", re.I))
    if readme_marker:
        # Take all text after the README marker, in its container
        parent = readme_marker.find_parent()
        if parent:
            sib_text = []
            for sib in parent.find_all_next():
                if sib.name in ("footer", "nav"):
                    break
                if sib.name in ("p", "li", "h1", "h2", "h3", "h4", "pre", "code"):
                    t = sib.get_text(" ", strip=True)
                    if t:
                        sib_text.append(t)
                if len("\n".join(sib_text)) > 20000:
                    break
            readme_md = "\n".join(sib_text)

    # Related MCPs
    related = []
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("/server/") and a["href"] != f"/server/{slug}":
            n = a.get_text(strip=True)
            if n:
                related.append({"slug": a["href"].removeprefix("/server/"), "name": n})
    # Dedup, cap
    rseen = set()
    related_uniq = []
    for r in related:
        if r["slug"] in rseen:
            continue
        rseen.add(r["slug"])
        related_uniq.append(r)
    related_uniq = related_uniq[:10]

    return {
        "slug": slug,
        "url": url,
        "name": name or page_title.split(" | ")[0].strip(),
        "page_title": page_title,
        "tagline": tagline,
        "categories": categories,
        "author": author,
        "readme_md": readme_md,
        "readme_len": len(readme_md),
        "related_slugs": [r["slug"] for r in related_uniq],
    }


async def scrape_detail(session, entry, sem, out_f, err_f, counter):
    html = await fetch_text(session, entry["url"], sem)
    counter[0] += 1
    if not html:
        err_f.write(json.dumps({"slug": entry["slug"], "url": entry["url"], "error": "fetch_failed"}) + "\n")
        err_f.flush()
        return
    try:
        parsed = parse_detail(html, entry["slug"], entry["url"])
        parsed["lastmod"] = entry.get("lastmod", "")
        out_f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
        out_f.flush()
    except Exception as e:
        err_f.write(json.dumps({"slug": entry["slug"], "error": f"parse: {e}"}) + "\n")
        err_f.flush()
    if counter[0] % 100 == 0:
        print(f"  detail {counter[0]}", flush=True)


async def main():
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Phase 1: Discover all server URLs
        if LISTINGS.exists():
            print(f"Reusing existing listings: {LISTINGS}")
            entries = [json.loads(l) for l in LISTINGS.open(encoding="utf-8")]
        else:
            print("Discovering listings from sitemap...")
            entries = await discover_listings(session, sem)
            with LISTINGS.open("w", encoding="utf-8") as f:
                for e in entries:
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"Total servers: {len(entries)}")

        # Phase 2: Fetch each detail. Resume by skipping already-scraped slugs.
        done = set()
        if DETAILS.exists():
            for line in DETAILS.open(encoding="utf-8"):
                try:
                    done.add(json.loads(line)["slug"])
                except Exception:
                    pass
        todo = [e for e in entries if e["slug"] not in done]
        print(f"Done: {len(done)} | Todo: {len(todo)}", flush=True)
        if not todo:
            print("Detail phase: nothing to do.")
            return

        out_f = DETAILS.open("a", encoding="utf-8")
        err_f = ERRORS.open("a", encoding="utf-8")
        counter = [0]
        try:
            tasks = [scrape_detail(session, e, sem, out_f, err_f, counter) for e in todo]
            await asyncio.gather(*tasks)
        finally:
            out_f.close()
            err_f.close()
        print(f"DONE: processed {counter[0]} detail pages")


if __name__ == "__main__":
    asyncio.run(main())
