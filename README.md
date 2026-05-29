# Research-Gate-bildiri

Code, figures, supplementary materials, and reproducibility scaffolding for
academic papers submitted to ResearchGate by
**Kadir Göksel Gündüz** (Energy Institute, Istanbul Technical University).

The papers themselves — abstracts, full PDFs, citations — live on
ResearchGate. This repository contains the working artefacts that the papers
either reference, depend on, or were generated with.

ORCID: [0009-0007-9120-5659](https://orcid.org/0009-0007-9120-5659)

---

## Layout

```
.
├── papers/                        # one folder per submitted paper
│   ├── 01-darkweb-search-engine-audit/
│   ├── 02-vlm-darknet-screenshots/
│   ├── 03-leak-site-classification/
│   ├── 04-supply-chain-audit-lab/
│   └── 05-pixel-perfect-image-to-code/
├── mcp-scrape/                    # MCP-registry scraping pipeline + daily CI
│   ├── scrape_listings.py
│   ├── scrape_details.py
│   ├── scrape_mcpmarket.py
│   ├── build_report.py
│   ├── incremental_update.py
│   └── data/                      # JSONL snapshots + daily diff reports
└── tools/
    └── build_pdfs.py              # markdown -> figure-embedded PDF pipeline
```

Each `papers/NN-name/` directory contains:

- `CONTEXT.md` — raw findings, methodology notes, source-of-truth used to
  generate the paper text.
- `figures/` — Mermaid sources (`.mmd`), rendered PNGs, and any generator
  scripts.
- `scripts/` — paper-specific reproducibility code (probe scripts, ablations).
- `supplementary/` — the artefact bundle attached to the paper on ResearchGate.
- `references/` — `_style_notes.md` summarising the field's writing
  conventions used for the paper.
- `README.md` — paper-specific overview and the ResearchGate link.

The `PAPER.md` source and the typeset `PAPER.pdf` are deliberately **not**
checked in. The canonical reading copy is the ResearchGate publication; this
repository carries the things that the paper does not reproduce: figure
sources, probe scripts, raw data, build tooling.

---

## Papers

| # | Title | ResearchGate | Folder |
|---|---|---|---|
| 01 | A Single-Snapshot Audit of 18 Tor Search Engines | _(link pending upload)_ | [papers/01-darkweb-search-engine-audit/](papers/01-darkweb-search-engine-audit/) |
| 02 | Visual Classification of Tor Hidden Services with Frontier Vision-Language Models | _(link pending upload)_ | [papers/02-vlm-darknet-screenshots/](papers/02-vlm-darknet-screenshots/) |
| 03 | Structured Classification of Ransomware Leak-Site Posts with Large Language Models | _(link pending upload)_ | [papers/03-leak-site-classification/](papers/03-leak-site-classification/) |
| 04 | Detecting Typo-Squat-by-Copy Supply-Chain Attacks | _(link pending upload)_ | [papers/04-supply-chain-audit-lab/](papers/04-supply-chain-audit-lab/) |
| 05 | Iterative Visual Feedback Loops for Pixel-Faithful Image-to-Code Generation | _(link pending upload)_ | [papers/05-pixel-perfect-image-to-code/](papers/05-pixel-perfect-image-to-code/) |

ResearchGate URLs will be filled in here as each paper is published.

---

## MCP registry refresh

The `mcp-scrape/` pipeline keeps two daily snapshots of the published MCP
server ecosystem:

- **mcpservers.org** — community-curated registry, ~8,200 entries at first
  scrape.
- **mcpmarket.com** — sitemap-discoverable registry, ~34,000 entries at first
  scrape.

The two registries materially diverge on the long tail; both are scraped and
treated as separate corpora.

A GitHub Actions workflow runs `incremental_update.py` at 04:00 UTC daily,
appends any newly listed servers to the canonical JSONL files, and writes a
human-readable diff to `mcp-scrape/data/changes/YYYY-MM-DD.md`. The commit
history of `mcp-scrape/data/` therefore doubles as a longitudinal record of
the MCP ecosystem's growth.

See [mcp-scrape/README.md](mcp-scrape/README.md) for usage details.

---

## How to cite

When citing one of the papers, please cite the ResearchGate publication for
that paper directly. When citing the code or data, please link to the file
or directory at a specific commit, for example:

> Gündüz, K. G. (2026). Research-Gate-bildiri: Code and supplementary
> materials [Software]. GitHub. https://github.com/RsGoksel/Research-Gate-bildiri

---

## License

The code and data in this repository are released under the MIT License
(see [LICENSE](LICENSE)). Paper text and the typeset PDFs hosted on
ResearchGate are © Kadir Göksel Gündüz and are subject to the licence terms
of the ResearchGate platform.

Third-party material referenced in `papers/*/references/` (academic papers
downloaded as prior art) is not redistributed in this repository; the
`_style_notes.md` files contain only my own commentary on those works.

---

## Contact

Kadir Göksel Gündüz
Energy Institute, Istanbul Technical University (İTÜ)
gokssel.gunduz@gmail.com · gunduz25@itu.edu.tr
