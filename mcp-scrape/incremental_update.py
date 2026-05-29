"""Incremental refresh for the two MCP-server registries.

Behaviour:
  * Reads existing data/{mcpservers_listings.jsonl, mcpmarket_listings.jsonl}.
  * Re-scans each registry's listing/sitemap to discover today's slug set.
  * Diffs against yesterday's snapshot to compute the new-slug delta.
  * Fetches detail pages for new slugs only.
  * Appends (slug, name, description, ...) records to the canonical JSONL files.
  * Writes a daily diff report to data/changes/YYYY-MM-DD.md.

Designed for GitHub Actions: idempotent, resumable, never destructive. If the
remote site is temporarily unavailable, the script exits zero with a NOTE in
the changes/ report so the workflow does not fail noisily.
"""
import asyncio
import datetime as dt
import json
import re
import sys
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CHANGES = DATA / "changes"
DATA.mkdir(parents=True, exist_ok=True)
CHANGES.mkdir(parents=True, exist_ok=True)

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
CONCURRENCY = 6  # slower, more polite -- avoid tripping CDN rate limits on shared CI IPs

# Sanity gate: if the rediscovery returns less than this fraction of the prior
# snapshot, treat the run as a transient failure rather than a real listing change.
# Prevents false "removed: 8233" reports when a CDN denies the runner's request.
SANITY_FRACTION = 0.50


# -----------------------------------------------------------------------------
# Common helpers
# -----------------------------------------------------------------------------

async def fetch_text(session, url, sem, retries=3):
    for attempt in range(retries):
        try:
            async with sem, session.get(url, headers=UA, timeout=30) as r:
                return await r.text()
        except Exception as e:
            if attempt == retries - 1:
                print(f"  fetch failed: {url}: {e}", file=sys.stderr)
                return ""
            await asyncio.sleep(2 * (attempt + 1))


def load_jsonl(path: Path):
    if not path.exists():
        return []
    out = []
    for line in path.open(encoding="utf-8"):
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def append_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# -----------------------------------------------------------------------------
# mcpservers.org (paginated)
# -----------------------------------------------------------------------------

MCPSERVERS_LISTING_URL = "https://mcpservers.org/all?page={}&sort=newest"
MCPSERVERS_DETAIL_URL = "https://mcpservers.org/servers/{}"

CARD_RE = re.compile(
    r'<a href="(/servers/[^"]+)" class="block">'
    r'.*?'
    r'<div class="tracking-tight text-lg font-semibold">([^<]+)</div>'
    r'.*?'
    r'<div class="text-sm text-gray-600 leading-relaxed line-clamp-3">([^<]*)</div>',
    re.S,
)


async def discover_mcpservers(session, sem):
    page1_html = await fetch_text(session, MCPSERVERS_LISTING_URL.format(1), sem)
    m = re.search(r"Showing\s+[0-9-]+\s+of\s+([0-9,]+)", page1_html)
    total = int(m.group(1).replace(",", "")) if m else 0
    pages = max(1, (total + 29) // 30)
    print(f"  mcpservers.org reports {total} servers across {pages} pages")
    discovered = []
    seen = set()
    for p in range(1, pages + 1):
        html = await fetch_text(session, MCPSERVERS_LISTING_URL.format(p), sem)
        for mm in CARD_RE.finditer(html):
            slug = mm.group(1).removeprefix("/servers/")
            if slug in seen:
                continue
            seen.add(slug)
            discovered.append({
                "slug": slug,
                "name": mm.group(2).strip(),
                "description": mm.group(3).strip(),
                "first_seen_page": p,
            })
        if p % 25 == 0 or p == pages:
            print(f"    page {p}/{pages} -- {len(discovered)} unique slugs so far")
    return discovered


# -----------------------------------------------------------------------------
# mcpmarket.com (sitemap-based)
# -----------------------------------------------------------------------------

MCPMARKET_SITEMAP = "https://mcpmarket.com/sitemap.xml"

async def discover_mcpmarket(session, sem):
    index_xml = await fetch_text(session, MCPMARKET_SITEMAP, sem)
    tool_sitemaps = sorted(set(
        re.findall(r"https://mcpmarket\.com/sitemap/tools-\d+\.xml", index_xml)
    ))
    print(f"  mcpmarket.com tool sitemaps: {len(tool_sitemaps)}")
    discovered = []
    seen = set()
    for sm in tool_sitemaps:
        xml = await fetch_text(session, sm, sem)
        for url in re.findall(r"<loc>(https://mcpmarket\.com/server/[^<]+)</loc>", xml):
            slug = url.removeprefix("https://mcpmarket.com/server/")
            if slug in seen:
                continue
            seen.add(slug)
            discovered.append({"slug": slug, "url": url})
    print(f"  mcpmarket.com discovered {len(discovered)} slugs")
    return discovered


def parse_mcpmarket_detail(html, slug, url):
    soup = BeautifulSoup(html, "lxml")
    title_tag = soup.find("title")
    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else (title_tag.get_text(strip=True) if title_tag else slug)
    for t in soup(["script", "style", "svg", "noscript"]):
        t.decompose()
    tagline = ""
    if h1:
        nxt = h1.find_next(["p", "div"])
        if nxt:
            tt = nxt.get_text(" ", strip=True)
            if 10 < len(tt) < 400:
                tagline = tt
    cats = []
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("/categories/"):
            txt = a.get_text(strip=True)
            if txt:
                cats.append(txt)
    cats = list(dict.fromkeys(cats))
    return {
        "slug": slug,
        "url": url,
        "name": name,
        "tagline": tagline,
        "categories": cats,
    }


# -----------------------------------------------------------------------------
# mcpservers.org detail
# -----------------------------------------------------------------------------

def parse_mcpservers_detail(html, slug):
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else ""
    short = ""
    if h1:
        p = h1.find_next("p")
        if p:
            short = p.get_text(strip=True)
    body = soup.select_one(".markdown-body")
    md = body.get_text("\n", strip=True)[:50000] if body else ""
    return {
        "slug": slug,
        "title": title,
        "short_description": short,
        "readme_md": md,
        "readme_len": len(md),
    }


# -----------------------------------------------------------------------------
# Orchestration
# -----------------------------------------------------------------------------

async def refresh_one(name, listings_path, details_path, discover_fn, parse_detail_fn,
                       detail_url_template, session, sem):
    """Generic incremental refresh for one registry.

    `discover_fn(session, sem) -> list[dict]`            (each dict has 'slug', optional metadata)
    `parse_detail_fn(html, slug, *args) -> dict`         (parsed detail record)
    `detail_url_template` is a str.format-able URL with one slug placeholder.
    """
    prior = load_jsonl(listings_path)
    prior_slugs = {r["slug"] for r in prior}
    discovered = await discover_fn(session, sem)
    discovered_slugs = {r["slug"] for r in discovered}

    # Sanity gate -- a sub-threshold discovery is almost certainly a transient
    # CDN denial against the runner IP, not a real ecosystem collapse. Bail out
    # without recording a misleading "removed" diff.
    if prior_slugs and len(discovered_slugs) < int(len(prior_slugs) * SANITY_FRACTION):
        msg = (f"  {name}: discovered={len(discovered_slugs)} is below the sanity "
               f"floor of {int(len(prior_slugs) * SANITY_FRACTION)} "
               f"(prior={len(prior_slugs)}). Treating as a transient fetch failure; "
               f"skipping diff and detail fetch for this run.")
        print(msg, file=sys.stderr)
        return {
            "registry": name,
            "discovered_total": len(discovered_slugs),
            "prior_total": len(prior_slugs),
            "new_slugs": [],
            "removed_slugs": [],
            "new_detail_count": 0,
            "sanity_aborted": True,
            "note": msg.strip(),
        }

    new_slugs = discovered_slugs - prior_slugs
    removed_slugs = prior_slugs - discovered_slugs
    print(f"  {name}: discovered={len(discovered_slugs)}  prior={len(prior_slugs)}  "
          f"new={len(new_slugs)}  removed={len(removed_slugs)}")

    # Append new listings
    new_listing_records = [r for r in discovered if r["slug"] in new_slugs]
    if new_listing_records:
        append_jsonl(listings_path, new_listing_records)

    # Fetch detail pages for new slugs only
    new_detail_records = []
    for r in new_listing_records:
        slug = r["slug"]
        url = detail_url_template.format(slug)
        html = await fetch_text(session, url, sem)
        if not html:
            continue
        try:
            if name == "mcpmarket":
                detail = parse_detail_fn(html, slug, url)
            else:
                detail = parse_detail_fn(html, slug)
            new_detail_records.append(detail)
        except Exception as e:
            print(f"    parse failed {slug}: {e}", file=sys.stderr)
    if new_detail_records:
        append_jsonl(details_path, new_detail_records)

    return {
        "registry": name,
        "discovered_total": len(discovered_slugs),
        "prior_total": len(prior_slugs),
        "new_slugs": sorted(new_slugs),
        "removed_slugs": sorted(removed_slugs),
        "new_detail_count": len(new_detail_records),
    }


async def main():
    today = dt.date.today().isoformat()
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        reports = await asyncio.gather(
            refresh_one(
                "mcpservers",
                DATA / "mcpservers_listings.jsonl",
                DATA / "mcpservers_details.jsonl",
                discover_mcpservers,
                parse_mcpservers_detail,
                "https://mcpservers.org/servers/{}",
                session, sem,
            ),
            refresh_one(
                "mcpmarket",
                DATA / "mcpmarket_listings.jsonl",
                DATA / "mcpmarket_details.jsonl",
                discover_mcpmarket,
                parse_mcpmarket_detail,
                "https://mcpmarket.com/server/{}",
                session, sem,
            ),
        )

    # If every registry tripped the sanity gate, write a single short note and
    # skip the per-registry section so a transient CI failure does not pollute
    # the daily-change record.
    all_aborted = all(r.get("sanity_aborted") for r in reports)

    out = CHANGES / f"{today}.md"
    lines = [f"# MCP registry refresh {today}\n"]
    if all_aborted:
        lines.append("Every registry tripped the rediscovery sanity gate; this "
                     "run is treated as a transient fetch failure (most likely "
                     "a CDN denial against the runner IP). No diff is recorded "
                     "and no data files were modified.\n")
        for rep in reports:
            lines.append(f"- **{rep['registry']}**: discovered "
                         f"{rep['discovered_total']} / prior {rep['prior_total']}")
        out.write_text("\n".join(lines), encoding="utf-8")
        print(f"\nDaily report (all aborted): {out}")
        return reports

    for rep in reports:
        lines.append(f"## {rep['registry']}\n")
        if rep.get("sanity_aborted"):
            lines.append(f"_skipped: discovery returned only {rep['discovered_total']} "
                         f"of {rep['prior_total']} prior slugs; treated as transient fetch failure._\n")
            continue
        lines.append(f"- discovered today: {rep['discovered_total']}")
        lines.append(f"- prior snapshot: {rep['prior_total']}")
        lines.append(f"- new this run: {len(rep['new_slugs'])}")
        lines.append(f"- removed (disappeared from listing): {len(rep['removed_slugs'])}")
        lines.append(f"- new detail records appended: {rep['new_detail_count']}\n")
        if rep["new_slugs"]:
            lines.append("### New slugs\n")
            for s in rep["new_slugs"]:
                lines.append(f"- {s}")
            lines.append("")
        if rep["removed_slugs"]:
            lines.append("### Removed slugs (no longer listed)\n")
            for s in rep["removed_slugs"]:
                lines.append(f"- {s}")
            lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nDaily report: {out}")
    return reports


if __name__ == "__main__":
    asyncio.run(main())
