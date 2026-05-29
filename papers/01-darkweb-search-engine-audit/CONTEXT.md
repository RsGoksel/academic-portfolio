# CONTEXT — Paper 01: Tor Search Engine Benchmark

> **Status:** Raw findings dump from the live audit session (2026-05-28).
> **Do not delete.** This is the canonical record. PAPER.md is derived from this.

## What we actually did

Stood up an isolated Tor instance (`tor-expert-bundle` v0.4.9.8 on `127.0.0.1:9050`, separate `torrc` + data dir, no overlap with user's Tor Browser) and used the **JacobJandon/OnionClaw v2.3.0** Python library — which wraps 18 Tor-network search engines behind a uniform `dispatch('sicry_search', ...)` interface — to:

1. Probe **all 18 configured engines** for liveness (`sicry_check_engines`) within a single Tor circuit set.
2. Issue 5 controlled queries from a pre-registered, ethics-cleared catalog and record per-engine result counts, latencies, and result quality.

Workspace and raw artifacts: `C:\tmp\darkweb-audit\test_results\` (5 JSONs + `_run.log`).

## Methodology actually used

### Tor setup
- Tor Expert Bundle, fresh install at `C:\tmp\darkweb-audit\tor\`
- `torrc` minimal: `SocksPort 127.0.0.1:9050`, `ControlPort 127.0.0.1:9051` with `CookieAuthentication 1`, `ClientOnly 1`, fresh `DataDirectory`
- Bootstrap time: ~45 s (Bootstrapped 100% at log timestamp 11:22:57)
- Verified via `https://check.torproject.org/api/ip` → `{"IsTor":true,"IP":"45.84.107.182"}` (different exit nodes per circuit refresh)

### Engine seed list (OnionClaw v2.3.0)
The 18 engines OnionClaw queries by default, with their .onion addresses (clearnet entries where applicable):

| # | Name | URL (truncated) |
|---|---|---|
| 1 | Ahmia | `juhanurmihxlp77...onion/search/?q=` |
| 2 | OnionLand | `3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/search` |
| 3 | Amnesia | `amnesia7u5odx5xbwtpnqk3edybgud5bmiagu75bnqx2crntw5kry7ad.onion` |
| 4 | Torland | `torlbmqwtudkorme6prgfpmsnile7ug2zm4u3ejpcncxuhpu4k2j4kyd.onion` |
| 5 | Excavator | `2fd6cemt4gmccflhm6imvdfvli3nf7zn6rfrwpsy7uhxrgbypvwf5fad.onion` |
| 6 | Onionway | `oniwayzz74cv2puhsgx4dpjwieww4wdphsydqvf5q7eyz4myjvyw26ad.onion` |
| 7 | Tor66 | `tor66sewebgixwhcqfnp5inzp5x5uohhdy3kvtnyfxc2e5mxiuh34iid.onion` |
| 8 | OSS | `3fzh7yuupdfyjhwt3ugzqqof6ulbcl27ecev33knxe3u7goi3vfn2qqd.onion` |
| 9 | Torgol | `torgolnpeouim56dykfob6jh5r2ps2j73enc42s2um4ufob3ny4fcdyd.onion` |
| 10 | TheDeepSearches | `searchgf7gdtauh7bhnbyed4ivxqmuoat3nm6zfrg3ymkq6mtnpye3ad.onion` |
| 11 | Kaizer | `kaizerwfvp5gxu6cppibp7jhcqptavq3iqef66wbxenh6a2fklibdvid.onion` |
| 12 | Anima | `anima4ffe27xmakwnseih3ic2y7y3l6e7fucwk4oerdn4odf7k74tbid.onion` |
| 13 | Tornado | `tornadoxn3viscgz647shlysdy7ea5zqzwda7hierekeuokh5eh5b3qd.onion` |
| 14 | TorNet | `tornetupfu7gcgidt33ftnungxzyfq2pygui5qdoysss34xbgx2qruzid.onion` |
| 15 | FindTor | `findtorroveq5wdnipkaojfpqulxnkhblymc7aramjzajcvpptd4rjqd.onion` |
| 16 | Torgle | `iy3544gmoeclh5de6gez2256v6pjh4omhpqdh2wpeepp jtvqmjhkfwad.onion` |
| 17 | DuckDuckGo-Tor | `duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion` |
| 18 | Ahmia-clearnet | `https://ahmia.fi/search/?q=` |

### Queries from the allowed catalog (5 total)

Strictly limited to academic/public content. Forbidden categories: marketplaces, drugs/weapons, credentials, PII, real victim leaks.

| # | Query | Engine(s) | Tool |
|---|---|---|---|
| Q0 | (precheck) | all 18 | `sicry_check_tor` + `sicry_check_engines` |
| Q1 | "machine learning" | Ahmia, Ahmia-clearnet | `sicry_search` |
| Q2 | "academic papers" | Ahmia, Ahmia-clearnet | `sicry_search` |
| Q3 | (fetch landing page) | Tor Project hidden service | `sicry_fetch` |
| Q4 | (fetch landing page) | DuckDuckGo onion | `sicry_fetch` |
| Q5 | "open source intelligence" | all 18 | `sicry_search` |

## Raw findings

### Engine liveness (Q0)

13 / 18 engines responded (`status=up`). 5 / 18 timed out via Tor circuit (`engine unreachable via Tor circuit`).

**Up (13):**
| Engine | Latency (ms) |
|---|---|
| Ahmia-clearnet | 1315 |
| Torgol | 3006 |
| Ahmia | 4008 |
| Amnesia | 4060 |
| DuckDuckGo-Tor | 4213 |
| FindTor | 4382 |
| Tor66 | 4723 |
| Onionway | 4879 |
| Excavator | 4937 |
| OSS | 5006 |
| OnionLand | 5303 |
| Torland | 5710 |
| TheDeepSearches | 6307 |

**Down (5):** Kaizer, Anima, Tornado, TorNet, Torgle. All five returned the same generic error `engine unreachable via Tor circuit`. No hidden-service address-list bad checksum, so most plausible explanation is the .onion service was offline at probe time. Reliability metric (`reliability=0.333`) reflects OnionClaw's rolling history — these engines have been unreliable historically.

Mean latency (live engines, excluding Ahmia-clearnet which is HTTPS not .onion): **4844 ms** (σ 875 ms).
Clearnet Ahmia is 3.7× faster than the median .onion engine.

### Query Q1 / Q2: Ahmia regression

Both queries returned an **identical 4-row generic list** (Tor Browser link, Ahmia GitHub source, Tor Project page, the Ahmia onion address itself) regardless of the actual search term. Confidence scores were 0.05 across the board (OnionClaw's fallback when no result-element selectors match).

**Inferred cause:** OnionClaw's Ahmia HTML parser uses a regex/CSS selector that does not match Ahmia's current page layout. The parser falls through and scrapes Ahmia's site chrome (logo/nav links) instead of `<li class='result'>` elements. Same fault appeared in both Ahmia and Ahmia-clearnet because both share the parser.

This is a **silent failure mode** — `sicry_search` returns successfully (`ok: True`), so a downstream researcher would assume Ahmia has no results for their query, not that the engine is broken. Important methodological point: silent search failures matter more in this domain than in clearnet IR work because there is no SERP-page sanity check.

### Query Q3 / Q4: `sicry_fetch` (direct .onion HTML)

Both fully succeeded.
- **Q3 Tor Project** (`http://2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion/`) — 200 OK, 2.07 s, returned title "Tor Project | Anonymity Online", clean text extract, 30+ links classified `is_onion=True`.
- **Q4 DuckDuckGo onion** (`https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/`) — 200 OK, 1.53 s, title "DuckDuckGo - Protection. Privacy. Peace of mind.", clean text + link list.

This is the most reliable surface in OnionClaw — for research workloads where seed URLs are known, fetch + parse works fine.

### Query Q5: multi-engine "open source intelligence"

10 results total in 129 s (default 5-worker concurrency over 18 engines).

| Engine | Results returned | Best confidence |
|---|---|---|
| Excavator | 3 | 0.297 |
| Ahmia | 3 | 0.154 (parser-degraded — generic Tor Project chrome links) |
| Amnesia | 2 | 0.050 |
| Onionway | 2 | 0.050 |

Top result by confidence: F-Droid open-source app repository (Excavator, 0.297). This is a legitimate, on-topic OSINT-adjacent result.

**Other 12 engines returned zero results** for this query — either down (5), or the engine itself returned empty (OnionLand, Torland, Onionway-partial, Tor66, OSS, Torgol, TheDeepSearches, FindTor, DuckDuckGo-Tor, Ahmia-clearnet), or the parser failed silently.

### Tor exit-node observations

Three different exit IPs observed across the session, all in 45.84.107.0/24 subnet (Iceland-based Tor exit operator). OnionClaw does not auto-rotate circuit between requests — `sicry_renew_identity` is opt-in. For benchmark reproducibility this is desirable (consistent network conditions); for OPSEC it is a footgun.

## Why this is publishable

The most-recent dedicated Tor search engine benchmark (Faizan & Khan, 2019, "Two-stage approach for indexing the dark web onion services") was published 6+ years ago. The engine landscape has churned: of their 6 evaluated engines, only 2 still resolve. Our 18-engine snapshot (13 live, 5 dead) reflects the current landscape and exposes a silent-failure mode (Ahmia parser drift) that no published methodology specifically warns about.

## Methodological contributions

1. **Reproducible scaffolding.** Full `torrc` + venv + query script + raw outputs committed at `C:\tmp\darkweb-audit\`. Independent reviewers can rerun and get directly comparable numbers.
2. **Silent-failure-aware evaluation protocol.** Add a sanity check: every `_search` result should be cross-validated against `_fetch` of the same engine's URL to confirm the parser sees what the engine returned. Without this, engine-level recall is unmeasurable.
3. **Liveness ≠ usefulness.** 13 engines were `up`, but only 4 returned non-empty results for our OSINT query. The community usage of "live engine count" as a quality proxy is misleading.
4. **Engine reliability metric grounded in rolling history.** OnionClaw's `reliability` field, recorded across days of probes, is more honest than a single-point liveness check. Recommend academic adoption.

## Gaps / limits

- N=5 queries is small. Statistical claims require ≥30 queries.
- Single Tor exit subnet (Iceland 45.84.107.0/24) — Tor exit selection bias may affect timings. Replication from other geographies needed.
- No human-in-the-loop relevance grading yet — currently using OnionClaw's internal `confidence` score (TF-IDF-like). Real benchmark needs annotated relevance judgments.
- Did not exercise circuit rotation between queries (`sicry_renew_identity`). May affect engine-side rate-limiting behavior.

## Pre-registered ethics constraints (already enforced)

- No queries about specific persons, services for sale, leaked credentials, drugs, weapons, CSAM, financial fraud.
- No fetch of non-allowlisted URLs.
- All test queries listed verbatim in `C:\tmp\darkweb-audit\PLAN.md` — not invented after the fact.
- Exit IP and circuit timings logged; no personal identifiers collected.

## Reproducibility appendix

- Tor binary: `tor-expert-bundle-windows-x86_64`, sha256 verified against `https://dist.torproject.org/torbrowser/`.
- OnionClaw commit: latest of `JacobJandon/OnionClaw` as of 2026-05-28 (v2.3.0 line; full audit in `T1b_audit_report_jacobjandon.md` confirms no malicious code).
- Python venv contents: `beautifulsoup4==4.14.3 certifi==2026.5.20 charset-normalizer==3.4.7 idna==3.16 PySocks==1.7.1 python-dotenv==1.2.2 requests==2.34.2 soupsieve==2.8.4 stem==1.8.2 typing_extensions==4.15.0 urllib3==2.7.0`.
- Query script: `/tmp/onion_t4b.py` (5 queries, runs end-to-end in ~3 min).
