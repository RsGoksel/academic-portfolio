"""Scrape each server detail page: extract title, description, external URL, README markdown.

Resumable: skips slugs already in details.jsonl.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup

LISTINGS = Path(r"C:\tmp\mcp-scrape\listings.jsonl")
OUT = Path(r"C:\tmp\mcp-scrape\details.jsonl")
ERR = Path(r"C:\tmp\mcp-scrape\details_errors.jsonl")
CONCURRENCY = 16
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# matches the "View on X" external link
EXT_LINK_RE = re.compile(
    r'<a href="(https?://[^"]+)"[^>]*target="_blank"[^>]*>[^<]*View on',
)


def html_to_markdown(soup_node):
    """Crude HTML→Markdown for README body."""
    out = []

    def walk(node, depth=0):
        if isinstance(node, str):
            text = node
            if text.strip():
                out.append(text)
            return
        name = node.name
        if name is None:
            return
        if name in ("script", "style"):
            return
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            out.append("\n\n" + "#" * level + " ")
            for c in node.children:
                walk(c, depth + 1)
            out.append("\n")
        elif name == "p":
            out.append("\n\n")
            for c in node.children:
                walk(c, depth + 1)
        elif name == "br":
            out.append("\n")
        elif name in ("ul", "ol"):
            out.append("\n")
            for li in node.find_all("li", recursive=False):
                out.append("\n- ")
                for c in li.children:
                    walk(c, depth + 1)
        elif name == "li":
            for c in node.children:
                walk(c, depth + 1)
        elif name == "code" and node.parent and node.parent.name != "pre":
            out.append("`" + node.get_text() + "`")
        elif name == "pre":
            code = node.get_text()
            out.append("\n\n```\n" + code + "\n```\n\n")
        elif name == "a":
            text = node.get_text().strip()
            href = node.get("href", "")
            if text and href:
                out.append(f"[{text}]({href})")
            elif text:
                out.append(text)
        elif name in ("strong", "b"):
            out.append("**" + node.get_text() + "**")
        elif name in ("em", "i"):
            out.append("*" + node.get_text() + "*")
        else:
            for c in node.children:
                walk(c, depth + 1)

    walk(soup_node)
    md = "".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


def parse_detail(html, slug):
    soup = BeautifulSoup(html, "lxml")

    # Title
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else ""

    # Short description: first <p> after <h1>
    short_desc = ""
    if h1:
        nxt = h1.find_next("p")
        if nxt:
            short_desc = nxt.get_text(strip=True)

    # External link ("View on X")
    ext_url = ""
    m = EXT_LINK_RE.search(html)
    if m:
        ext_url = m.group(1)

    # README body — inside .markdown-body
    readme_md = ""
    body_node = soup.select_one(".markdown-body")
    if body_node:
        readme_md = html_to_markdown(body_node)

    # Categories / tags from breadcrumb or sidebar — try to grab any badge-like spans
    tags = []
    for span in soup.find_all("span"):
        cls = " ".join(span.get("class", []))
        if "rounded-full" in cls or "badge" in cls.lower():
            txt = span.get_text(strip=True)
            if txt and len(txt) < 40 and txt.lower() not in ("sponsor",):
                tags.append(txt)
    tags = list(dict.fromkeys(tags))[:10]

    return {
        "slug": slug,
        "title": title,
        "short_description": short_desc,
        "external_url": ext_url,
        "tags": tags,
        "readme_md": readme_md,
        "readme_len": len(readme_md),
    }


async def fetch_detail(session, slug, sem):
    async with sem:
        url = f"https://mcpservers.org/servers/{slug}"
        for attempt in range(4):
            try:
                async with session.get(url, headers=HEADERS, timeout=30) as r:
                    if r.status == 404:
                        return slug, None, "404"
                    if r.status >= 500:
                        raise aiohttp.ClientError(f"status {r.status}")
                    html = await r.text()
                    return slug, html, None
            except Exception as e:
                if attempt == 3:
                    return slug, None, str(e)
                await asyncio.sleep(1.5 * (attempt + 1))


async def main():
    listings = [json.loads(l) for l in LISTINGS.open(encoding="utf-8")]
    all_slugs = [l["slug"] for l in listings]

    # Resume: skip already-done
    done = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                done.add(json.loads(line)["slug"])
            except Exception:
                pass

    todo = [s for s in all_slugs if s not in done]
    print(f"Total: {len(all_slugs)} | Done: {len(done)} | Todo: {len(todo)}", flush=True)
    if not todo:
        print("Nothing to do.")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY * 2, ttl_dns_cache=300)

    progress = 0
    errors = 0
    async with aiohttp.ClientSession(connector=connector) as session:
        out_f = OUT.open("a", encoding="utf-8")
        err_f = ERR.open("a", encoding="utf-8")
        try:
            tasks = [fetch_detail(session, s, sem) for s in todo]
            for coro in asyncio.as_completed(tasks):
                slug, html, err = await coro
                progress += 1
                if html is None:
                    errors += 1
                    err_f.write(json.dumps({"slug": slug, "error": err}) + "\n")
                    err_f.flush()
                else:
                    try:
                        parsed = parse_detail(html, slug)
                        out_f.write(json.dumps(parsed, ensure_ascii=False) + "\n")
                        out_f.flush()
                    except Exception as e:
                        errors += 1
                        err_f.write(json.dumps({"slug": slug, "error": f"parse: {e}"}) + "\n")
                        err_f.flush()

                if progress % 100 == 0:
                    print(f"  {progress}/{len(todo)} (errors={errors})", flush=True)
        finally:
            out_f.close()
            err_f.close()

    print(f"DONE. Processed {progress}, errors {errors}")


if __name__ == "__main__":
    asyncio.run(main())
