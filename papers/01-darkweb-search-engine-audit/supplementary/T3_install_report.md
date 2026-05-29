# T3 — Isolated Install Report

**Date:** 2026-05-28
**Verdict:** ✅ Ready for T4

## Installed in

`C:\tmp\darkweb-audit\venv\` — fresh CPython venv, no global site-packages bleed.

Repo: `C:\tmp\darkweb-audit\repos\OnionClaw-genuine\` (the SAFE upstream from T1b).

`setup.py` was NOT executed (per T1b recommendation — it's a runtime configuration wizard that would touch system Tor).

## Dependencies actually installed

Source: `pip freeze` after `pip install -r requirements.txt`. Saved to `C:\tmp\darkweb-audit\T3_pip_freeze.txt`.

```
beautifulsoup4==4.14.3
certifi==2026.5.20
charset-normalizer==3.4.7
idna==3.16
PySocks==1.7.1
python-dotenv==1.2.2
requests==2.34.2
soupsieve==2.8.4
stem==1.8.2
typing_extensions==4.15.0
urllib3==2.7.0
```

11 packages total. All mainstream, all current. Transitive deps (`certifi`, `charset-normalizer`, `idna`, `urllib3`, `soupsieve`, `typing_extensions`, `PySocks`) are exactly the expected transitive closure for `requests[socks] + beautifulsoup4 + stem`. **No surprises vs T1b audit.**

Optional `mcp>=1.0.0` was **not** installed — only needed for "MCP server mode" via `python sicry.py serve`. T4 will invoke OnionClaw's Python API directly, which doesn't need it.

## Smoke tests

### Module import (no CLI side-effects)
```
=== IMPORT sicry ===
  OK  sicry from C:\tmp\darkweb-audit\repos\OnionClaw-genuine\sicry.py
  callables: ['BeautifulSoup', 'CrawlResult', 'HTTPAdapter', 'Iterator', 'Optional', 'Retry',
              'ThreadPoolExecutor', 'TorPool', 'analyze_nollm', 'as_completed', 'ask',
              'check_search_engines', 'check_tor', 'check_update', 'clear_cache', 'crawl',
              'crawl_export', 'deduplicate_results', 'dispatch', 'engine_health_history']
```

Key callables for T4: `crawl`, `dispatch` (search), `check_search_engines`, `analyze_nollm`, `TorPool`.

Note: `search.py` has module-level `argparse` parsing — importing it directly fails unless `--query` is supplied via `sys.argv`. This is sloppy packaging (CLI code at module scope) but not malicious; we'll call functions via `sicry` instead, which exposes the same operations as a library API.

### Tor connectivity from the venv
```
status=200  body={"IsTor":true,"IP":"45.84.107.76"}
```

Different exit-node IP than T2's `45.84.107.182` → circuit rotation is working.

### Stem control port
```
OK  tor version: 0.4.9.8 (git-e170cdcfebd45f6d), circuits: 20
```

OnionClaw can use stem to request `NEWNYM` (new circuit) between requests — the "identity rotation" feature the auditor flagged as legitimate.

## Environment file

Not created — env vars are passed inline per query in T4 to keep config explicit. If T4 grows to need a `.env`, it'll be at `C:\tmp\darkweb-audit\OnionClaw.env` (NOT inside the cloned repo).

## Deviations from T1b audit

**None.** Pip resolved exactly the dep tree T1b predicted. No new deps appeared.

## Hard rules upheld

- ✅ venv lives at `C:\tmp\darkweb-audit\venv` only
- ✅ No `pip install --user`
- ✅ No `setup.py` execution
- ✅ Not wired into Claude Desktop / Claude Code MCP config
- ✅ Reused the T2 Tor instance (no second tor.exe spawned)

**Status: DONE. Ready for T4.**
