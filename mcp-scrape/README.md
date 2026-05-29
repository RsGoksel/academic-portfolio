# mcp-scrape

Reproducible scrapers for two community registries of Model Context Protocol
(MCP) servers, with an incremental update script that runs daily via GitHub
Actions.

## Layout

```
mcp-scrape/
├── scrape_listings.py        # mcpservers.org bulk first-time scrape (paginated)
├── scrape_details.py         # mcpservers.org per-server detail pages
├── scrape_mcpmarket.py       # mcpmarket.com sitemap-based bulk first-time scrape
├── build_report.py           # build RAG-ready report from the JSONL snapshots
├── incremental_update.py     # daily diff-and-append refresh (used by GH Actions)
├── requirements.txt
└── data/
    ├── mcpservers_listings.jsonl   # {slug, name, description, ...} per server
    ├── mcpservers_details.jsonl    # {slug, title, short_description, readme_md, ...}
    ├── mcpmarket_listings.jsonl    # {slug, url}
    ├── mcpmarket_details.jsonl     # {slug, url, name, tagline, categories, ...}
    └── changes/
        └── YYYY-MM-DD.md           # one daily diff report per refresh
```

## First-time bulk scrape

```bash
cd mcp-scrape
pip install -r requirements.txt

# mcpservers.org -- ~8,200 entries, paginated. ~5 minutes at default concurrency.
python scrape_listings.py
python scrape_details.py

# mcpmarket.com -- ~34,000 entries via sitemap. ~10-15 minutes.
python scrape_mcpmarket.py
```

The bulk scripts are idempotent: they detect existing JSONL files and resume.

## Daily incremental refresh

`incremental_update.py` is the workflow primitive used by
`.github/workflows/daily-mcp-refresh.yml`:

1. Read the canonical listings JSONL for each registry.
2. Re-discover the current slug set (page walk for mcpservers, sitemap for
   mcpmarket).
3. Diff: identify slugs not seen in the prior snapshot ("new") and slugs no
   longer listed ("removed").
4. For each new slug, fetch the detail page and append a record to
   `*_details.jsonl`.
5. Write a daily report at `data/changes/YYYY-MM-DD.md`.

The GitHub Actions workflow runs the script at 04:00 UTC, commits any
appended records, and uploads the daily report as a workflow artifact.

## Querying the RAG index

`build_report.py` is the recommended path from the raw JSONL into a
RAG-ingestion shape (consolidated index + per-category breakdowns). It treats
the two registries as separate corpora (different metadata shapes, different
populations) rather than merging them.

## Notes

- The two registries materially overlap on famous entries (Filesystem, GitHub,
  Slack), and materially diverge on the long tail. Querying both is
  recommended for completeness.
- "Removed" slugs are recorded but never deleted from the local JSONL; the
  detail records remain available for retrospective analysis of disappeared
  servers.
- The scrapers respect a single User-Agent header that identifies them as the
  rg-bildiri refresh bot. If either registry adds a robots.txt deny rule for
  this UA, the scripts should be disabled and the registry contacted before
  any further refresh.
