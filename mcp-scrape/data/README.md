# MCP registry snapshots

This directory holds the canonical JSONL snapshots used by the daily-refresh
workflow. Each new run appends to these files; nothing is ever overwritten.

## Files

| File | Records | Schema |
|---|---|---|
| `mcpservers_listings.jsonl` | one per mcpservers.org server slug | `{slug, name, description, ...}` |
| `mcpservers_details.jsonl` | one per server detail page | `{slug, title, short_description, readme_md, readme_len}` |
| `mcpmarket_listings.jsonl` | one per mcpmarket.com server slug | `{slug, url}` |
| `mcpmarket_details.jsonl` | one per detail page | `{slug, url, name, tagline, categories, ...}` |

## Detail files

`mcpservers_details.jsonl` and `mcpmarket_details.jsonl` are deliberately
**not** seeded into the repo because the combined size is ~70 MB. They are
created on the first GitHub Actions run: every slug present in the listings
JSONL but absent from the details JSONL is treated as "new" and fetched.
After the first run the file exists and subsequent runs append only the
genuinely new slugs.

If you want a faster local bootstrap, run the bulk scrapers locally:

```bash
cd mcp-scrape
python scrape_details.py        # ~10 min, 8K detail pages from mcpservers.org
python scrape_mcpmarket.py      # ~15 min, 34K detail pages from mcpmarket.com
```

## Daily diff reports

`changes/YYYY-MM-DD.md` files record per-day new and removed slugs across
both registries. They are also exposed as GitHub Actions workflow artefacts
for thirty days.
