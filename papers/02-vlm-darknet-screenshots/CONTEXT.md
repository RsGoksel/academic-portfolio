# CONTEXT — Paper 02: VLM Classification of Tor Hidden Services

> **Status:** Raw findings dump (2026-05-28). Do not delete. PAPER.md derives from this.

## Proposed contribution (no executed experiment yet — this is a methodology paper)

This paper proposes — but does NOT yet empirically validate — a frontier-VLM-based methodology for **automatic classification of Tor hidden services** from rendered screenshots of their landing pages, into a small label set that supports downstream OSINT triage.

The audit session did not run this experiment. But the upstream pieces are all proven independently in our session:
1. `sicry_fetch` reliably retrieves .onion HTML (Q3, Q4 in `T4_query_report.md`)
2. Headless browser screenshot tooling for clearnet exists at scale (Playwright MCP, mcp-screenshot-website-fast — surfaced in pixel-perfect frontend research)
3. Frontier VLMs (Claude Opus 4.7, GPT-5, Qwen2.5-VL, UI2Code^N-9B) have documented strong performance on UI screenshot classification (Design2Code benchmark)

The methodology paper proposes wiring these together for darknet triage.

## Task definition

**Input:** A list of `.onion` URLs (e.g. from `sicry_search` results, or a curated seed list).
**Step 1:** Fetch each URL through Tor and render the landing page via a headless Tor-aware browser.
**Step 2:** Save the rendered page as a PNG screenshot (e.g. 1280×800 viewport).
**Step 3:** Pass each screenshot to a frontier VLM with a structured-output prompt asking for a single label from `{Forum, Marketplace, Blog, EmptyOrError, Parked, LeakSite, ImageboardOrChan, ServiceLanding, MirrorOrIndex, Other}`.
**Step 4:** Optionally a second pass with confidence scores and freeform notes for ambiguity.
**Output:** Per-URL label + confidence + a screenshot archive for human spot-check.

## Why VLMs for this (vs. HTML parsing or fingerprinting)

- HTML parsing is brittle against the heterogeneity of .onion sites (custom themes, broken markup, anti-scraping JavaScript).
- TLS fingerprint and HTTP header banners (typical clearnet web typology tools) are largely useless on .onion because the transport is uniform Tor.
- Visual layout is the most stable signal: a forum looks like a forum, a marketplace looks like a marketplace, a leak site looks like a leak site — across themes.
- Frontier VLMs have been trained on enough clearnet web UI that the visual gestalt of these page types is in-distribution even if specific darknet sites are not.

## Candidate VLMs (from session's prior research; see `C:\tmp\mcp-scrape\report\research_web_image_to_code.md`)

| Model | UI-relevant benchmark | Access |
|---|---|---|
| Claude Opus 4.7 | 98.5% visual acuity (custom internal benchmark); 2576px input | API |
| GPT-5 | Design2Code 93.7 | API |
| Claude Sonnet 4.6 | Design2Code 85.1 | API |
| Gemini 2.5 (Glm-5V-Turbo) | Design2Code 94.8 | API |
| UI2Code^N-9B (zai-org) | Design2Code 92.5; UI-polish 95.0 | HF, self-hostable |
| Qwen2.5-VL | strong ScreenSpot performance | HF, self-hostable |
| Pixtral, InternVL, Molmo | various | HF |

Cost-sensitive replication can use UI2Code^N-9B on a single A100 or even consumer GPU with quantization.

## Why the label set above

Drawn from prior darknet typology work (Faizan & Khan 2019, Spitters et al. 2014, Christin 2013, Moore & Rid 2016):
- Forum, Marketplace, Blog → classical typology
- LeakSite → emerged post-2019 (ransomware-as-a-service economy)
- ImageboardOrChan → distinct visual signature, large fraction of historical darknet
- ServiceLanding (single-page service like an email-relay or wallet) → common in 2020+
- MirrorOrIndex (Hidden Wiki clones) → very common, deserves its own bucket
- EmptyOrError / Parked → silent failure modes that need explicit labels for OSINT pipelines

## Evaluation plan (proposed, not yet executed)

1. **Sample.** 500 .onion URLs drawn from a single multi-engine `sicry_search` pass over 30 OSINT-related queries (drawn from the SecurityOnion or MISP query catalogs). Excluded: anything matching illegal-content seed lists.
2. **Ground truth.** Two human annotators independently label each screenshot. Inter-annotator agreement reported (target: Cohen's κ ≥ 0.75).
3. **Models.** Claude Opus 4.7 (primary), GPT-5 (head-to-head), UI2Code^N-9B (open-source baseline).
4. **Metrics.** Per-class precision/recall, weighted F1, confusion matrix, per-model cost-per-1k-URLs.
5. **Ablation.** Compare VLM-on-screenshot vs LLM-on-HTML-text-only (text-only baseline on rendered HTML), to quantify visual signal contribution.
6. **Failure analysis.** Manual inspection of every confident misclassification (≥ 0.9 confidence wrong) to document failure modes.

## Why publishable now

No prior published work classifies .onion landing pages with frontier VLMs. The closest analogues:
- Spitters et al. 2014 used bag-of-words text classification — pre-deep-learning, pre-Tor v3.
- Faizan & Khan 2019 used HTML-feature engineering — brittle, low accuracy.
- All clearnet UI-classification work (web genre identification) avoids darknet because TLS fingerprinting works there.

The methodology contribution is the **pipeline architecture itself** — Tor-aware browser → screenshot → VLM → structured label. A solid methodology paper with even N=500 labeled samples is publishable in venues like USENIX Security, NDSS workshop, or ACM CSCW.

## Tor-aware browser implementation note

Playwright with SOCKS5 proxy support (built-in since v1.20) can route through our T2-configured `127.0.0.1:9050`. Cookie-jar isolation per-page is critical so that one site's tracker can't fingerprint across the corpus. Resource limits (block JavaScript by default, opt-in per site) are necessary for safety — many .onion sites serve hostile JS.

Alternative: Selenium-Wire + Tor Browser bundle, used by tbselenium-windows package (we audited but did not install — author trust profile too low; see T1 audit).

## Limits

- **VLM hallucination.** Frontier VLMs will confidently misclassify; ablation against text-only baseline is necessary to bound this.
- **Dynamic content.** Many .onion sites load content via JS after initial paint. Screenshot timing (wait_until='networkidle' with 10s ceiling) is a research variable.
- **Adversarial sites.** Some leak sites deliberately spoof "EmptyOrError" appearance to deter casual visitors. VLMs might be more confused than HTML parsers here.
- **Token cost.** At Claude Opus rates, 500 screenshots ~$15-50 depending on resolution. UI2Code^N self-hosted bypasses this but needs GPU.

## Ethics

- All fetched URLs must be from a pre-registered seed list, no walking links into uncategorized territory during screenshot capture.
- Screenshots that visually contain content suggesting CSAM, real PII, weapons trafficking, or actual leaked corporate data must be auto-flagged for immediate deletion (regex over OCR'd text + VLM second-pass for visual content).
- IRB or institutional ethics approval before any human-annotator phase.

## Pre-2022 prior art to cite (for downstream PAPER.md restyling)

- Faizan & Khan 2019, "Two-stage approach for indexing the dark web onion services"
- Spitters, Verbruggen, van Staalduinen 2014, "Towards a comprehensive insight into the thematic organization of the Tor hidden services"
- Christin 2013, "Traveling the Silk Road: A measurement analysis of a large anonymous online marketplace"
- Moore & Rid 2016, "Cryptopolitik and the Darknet"
- Web genre identification: Santini 2007 "Automatic identification of genre in web pages"
- Visual web genre: Boididou et al. 2018, Lin et al. 2014 (Layout-based classification)
- Pre-2022 VLM seed work for citation: Radford et al. 2021 (CLIP), Dosovitskiy 2020 (ViT), Lu et al. 2019 (ViLBERT)

These are pre-2022 and should be retrievable via arxiv MCP for full PDFs.
