"""Build the RAG-ready report from listings.jsonl + details.jsonl.

Outputs:
  - MCP_INDEX.md           : compact list of all servers (name, desc, url) -- RAG primary doc
  - MCP_REPORT.md          : summary stats + curated categories
  - mcp_full.jsonl         : merged record per server (RAG-embedding source)
  - categories/<name>.md   : per-keyword groupings for browsing
"""
import json
import re
from collections import defaultdict
from pathlib import Path

BASE = Path(r"C:\tmp\mcp-scrape")
LISTINGS = BASE / "listings.jsonl"
DETAILS = BASE / "details.jsonl"
OUT_DIR = BASE / "report"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Topic keywords -> regex patterns. A server can belong to multiple categories.
CATEGORIES = {
    "Database & SQL": r"\b(postgres|postgresql|mysql|sqlite|mongodb|redis|database|sql|duckdb|clickhouse|cassandra|dynamodb|supabase|neon|planetscale|firestore)\b",
    "Web Search & Scraping": r"\b(search|scrap|crawl|browser|playwright|selenium|fetch|exa|tavily|brave|duckduckgo|serpapi|firecrawl|jina|web)\b",
    "GitHub & Git": r"\b(github|gitlab|bitbucket|git\b|repository|pull request|issue)\b",
    "Cloud (AWS/GCP/Azure)": r"\b(aws|s3|ec2|lambda|gcp|google cloud|azure|cloudflare|vercel|netlify)\b",
    "Communication (Slack/Discord/Email)": r"\b(slack|discord|telegram|teams|email|gmail|outlook|smtp|imap|whatsapp|signal|sms|twilio)\b",
    "Files & Filesystem": r"\b(filesystem|file system|files?\b|dropbox|google drive|onedrive|sharepoint|nextcloud|ftp|sftp)\b",
    "Productivity (Notion/Linear/Jira)": r"\b(notion|linear|jira|asana|trello|monday|clickup|todoist|airtable|coda|confluence)\b",
    "Calendar & Scheduling": r"\b(calendar|google calendar|outlook calendar|caldav|schedul|cron|appointment)\b",
    "Crypto & Blockchain": r"\b(crypto|bitcoin|ethereum|solana|blockchain|web3|defi|nft|wallet|trading|binance|coinbase|coingecko|polygon|chainlink|x402|alpaca)\b",
    "AI / LLM / Embeddings": r"\b(llm|openai|anthropic|claude|gpt|gemini|llama|embedding|vector|rag|chroma|pinecone|weaviate|qdrant|huggingface)\b",
    "Browser Automation": r"\b(playwright|puppeteer|selenium|browser\b|chrome|firefox|headless|stealth)\b",
    "Documentation & Knowledge": r"\b(docs?\b|documentation|wiki|knowledge|context7|readme|api docs|swagger|openapi)\b",
    "Image / Video / Media": r"\b(image|video|audio|media|youtube|spotify|vimeo|figma|canva|imagemagick|ffmpeg|chatgpt-image|dall|midjourney)\b",
    "Finance & Markets": r"\b(stock|finance|trading|market|polygon|alpaca|yfinance|yahoo|tradingview|portfolio|invest)\b",
    "Maps & Geo": r"\b(map|maps|geo|location|gps|google maps|openstreetmap|nominatim)\b",
    "DevOps & Infrastructure": r"\b(docker|kubernetes|k8s|terraform|ansible|ci/cd|jenkins|prometheus|grafana|sentry|datadog)\b",
    "E-commerce & Payments": r"\b(stripe|shopify|woocommerce|paypal|payment|checkout|invoice|billing|ecommerce|amazon)\b",
    "Social Media": r"\b(twitter|x\.com|reddit|linkedin|instagram|facebook|tiktok|youtube|mastodon|bluesky)\b",
    "Security & Auth": r"\b(security|auth|oauth|jwt|secret|vault|1password|bitwarden|nmap|burp|metasploit)\b",
    "Memory & Notes": r"\b(memory|notes?\b|obsidian|logseq|roam|joplin|evernote|notebooklm)\b",
    "Time & Date": r"\b(time|date|timezone|chrono|sleep|wait|delay)\b",
    "Translation & Language": r"\b(translat|language|i18n|deepl|locale)\b",
    "PDF & Documents": r"\b(pdf|word|docx|excel|spreadsheet|csv|markdown|latex|pandoc)\b",
}


def slugify_filename(s):
    return re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")


def truncate(s, n):
    s = s.replace("\n", " ").replace("\r", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def load():
    listings = {}
    for line in LISTINGS.open(encoding="utf-8"):
        d = json.loads(line)
        listings[d["slug"]] = d
    details = {}
    if DETAILS.exists():
        for line in DETAILS.open(encoding="utf-8"):
            try:
                d = json.loads(line)
                details[d["slug"]] = d
            except Exception:
                pass
    return listings, details


def merge_record(slug, listing, detail):
    name = (detail or {}).get("title") or listing["name"]
    desc = (detail or {}).get("short_description") or listing.get("description") or ""
    return {
        "slug": slug,
        "name": name,
        "description": desc.strip(),
        "external_url": (detail or {}).get("external_url", ""),
        "mcpservers_url": f"https://mcpservers.org/servers/{slug}",
        "tags": (detail or {}).get("tags", []),
        "readme_md": (detail or {}).get("readme_md", ""),
        "readme_len": (detail or {}).get("readme_len", 0),
    }


def main():
    listings, details = load()
    print(f"Listings: {len(listings)} | Details: {len(details)}")

    merged = []
    for slug, listing in listings.items():
        merged.append(merge_record(slug, listing, details.get(slug)))
    merged.sort(key=lambda r: r["name"].lower())

    # 1) mcp_full.jsonl
    full_jsonl = OUT_DIR / "mcp_full.jsonl"
    with full_jsonl.open("w", encoding="utf-8") as f:
        for r in merged:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  wrote {full_jsonl} ({full_jsonl.stat().st_size/1024/1024:.1f} MB)")

    # 2) MCP_INDEX.md (compact, RAG-friendly)
    idx = OUT_DIR / "MCP_INDEX.md"
    with idx.open("w", encoding="utf-8") as f:
        f.write("# MCP Servers Master Index\n\n")
        f.write(f"Scraped from https://mcpservers.org/all -- **{len(merged)} servers**.\n\n")
        f.write("Format per entry: `name -- description (mcpservers slug | external link)`\n\n")
        f.write("---\n\n")
        for r in merged:
            line = f"- **{r['name']}** -- {truncate(r['description'], 280)}"
            line += f"  \n  [{r['slug']}](https://mcpservers.org/servers/{r['slug']})"
            if r["external_url"]:
                line += f" | [external]({r['external_url']})"
            f.write(line + "\n\n")
    print(f"  wrote {idx} ({idx.stat().st_size/1024:.0f} KB)")

    # 3) Per-category MD files
    cat_dir = OUT_DIR / "categories"
    cat_dir.mkdir(exist_ok=True)
    cat_counts = defaultdict(int)
    cat_files = {}
    for cat in CATEGORIES:
        f = (cat_dir / f"{slugify_filename(cat)}.md").open("w", encoding="utf-8")
        f.write(f"# {cat}\n\n")
        cat_files[cat] = f

    uncategorized = []
    for r in merged:
        haystack = (r["name"] + " " + r["description"]).lower()
        matched_any = False
        for cat, pattern in CATEGORIES.items():
            if re.search(pattern, haystack, re.I):
                cat_files[cat].write(
                    f"- **{r['name']}** -- {truncate(r['description'], 220)}  \n"
                    f"  [{r['slug']}](https://mcpservers.org/servers/{r['slug']})"
                    + (f" | [external]({r['external_url']})" if r["external_url"] else "")
                    + "\n\n"
                )
                cat_counts[cat] += 1
                matched_any = True
        if not matched_any:
            uncategorized.append(r)

    for f in cat_files.values():
        f.close()

    unc = cat_dir / "uncategorized.md"
    with unc.open("w", encoding="utf-8") as f:
        f.write("# Uncategorized\n\n")
        for r in uncategorized:
            f.write(
                f"- **{r['name']}** -- {truncate(r['description'], 220)}  \n"
                f"  [{r['slug']}](https://mcpservers.org/servers/{r['slug']})\n\n"
            )

    # 4) MCP_REPORT.md (summary + how to use)
    report = OUT_DIR / "MCP_REPORT.md"
    with report.open("w", encoding="utf-8") as f:
        f.write("# MCP Servers Report -- mcpservers.org snapshot\n\n")
        f.write(f"- **Total servers scraped:** {len(merged)}\n")
        f.write(f"- **With full README content:** {sum(1 for r in merged if r['readme_len']>0)}\n")
        f.write(f"- **Source:** https://mcpservers.org/all\n")
        f.write(f"- **Files in this report directory:**\n")
        f.write(f"  - `MCP_INDEX.md` -- compact list of all {len(merged)} servers (use for quick scan / Ctrl-F)\n")
        f.write(f"  - `mcp_full.jsonl` -- one JSON record per server (RAG embedding source)\n")
        f.write(f"  - `categories/*.md` -- servers grouped by keyword theme\n")
        f.write("\n## How to use as a RAG knowledge base\n\n")
        f.write("1. Embed `mcp_full.jsonl` using the field `name + description + readme_md` per record.\n")
        f.write("2. Query: 'I need an MCP for X' -> top-k retrieval returns relevant servers with slugs + install URLs.\n")
        f.write("3. Or just `grep` / `Ctrl-F` in `MCP_INDEX.md` for fast lookups.\n\n")
        f.write("## Category overview\n\n")
        f.write("| Category | # servers | File |\n|---|---|---|\n")
        for cat in sorted(CATEGORIES, key=lambda c: -cat_counts[c]):
            f.write(f"| {cat} | {cat_counts[cat]} | `categories/{slugify_filename(cat)}.md` |\n")
        f.write(f"| _Uncategorized_ | {len(uncategorized)} | `categories/uncategorized.md` |\n")
    print(f"  wrote {report}")

    print("\nCategory counts (servers can match multiple):")
    for cat in sorted(CATEGORIES, key=lambda c: -cat_counts[c]):
        print(f"  {cat_counts[cat]:5d}  {cat}")
    print(f"  {len(uncategorized):5d}  (Uncategorized)")


if __name__ == "__main__":
    main()
